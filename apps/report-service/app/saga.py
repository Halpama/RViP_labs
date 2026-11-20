from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

import csv
import io
from opentelemetry import trace
from aio_pika.exceptions import AMQPException

from .queue import ReportPublisher
from .schemas import ReaderReport


@dataclass(frozen=True)
class ExportResult:
    job_id: UUID
    filename: str


def readers_csv(reader_list: list[ReaderReport]) -> bytes:
    output = io.StringIO(newline="")
    fields = (
        "id",
        "full_name",
        "card_number",
        "card_active",
        "book_title",
        "registered_at",
    )
    writer = csv.DictWriter(output, fieldnames=fields)
    writer.writeheader()
    for reader in reader_list:
        row = reader.model_dump()
        row["registered_at"] = reader.registered_at.isoformat()
        writer.writerow(row)
    return output.getvalue().encode("utf-8")


class ReportExportSaga:
    """Orchestrates report creation and its asynchronous storage step."""

    def __init__(self, publisher: ReportPublisher) -> None:
        self.publisher = publisher
        self.tracer = trace.get_tracer("library.report-export")

    async def execute(self, reader_list: list[ReaderReport]) -> ExportResult:
        with self.tracer.start_as_current_span("saga.report-export") as span:
            span.set_attribute("saga.name", "report-export")
            span.set_attribute("saga.step", "publish-export")
            filename = f"readers-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.csv"
            try:
                job_id = await self.publisher.publish(filename, readers_csv(reader_list))
            except (AMQPException, OSError, RuntimeError):
                span.set_attribute("saga.status", "compensated")
                span.add_event("saga.compensation", {"action": "export-not-enqueued"})
                raise
            span.set_attribute("saga.status", "completed")
            return ExportResult(job_id=job_id, filename=filename)
