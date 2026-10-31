import csv
import io
from datetime import datetime, timezone

import httpx
from aio_pika.exceptions import AMQPException
from fastapi import APIRouter, HTTPException, Request, status

from ..schemas import ReaderReport, SummaryResponse

router = APIRouter(prefix="/reports", tags=["reports"])


async def fetch_readers(request: Request) -> list[ReaderReport]:
    client: httpx.AsyncClient = request.app.state.http_client
    settings = request.app.state.settings
    try:
        response = await client.get(f"{settings.reader_service_url}/readers")
        response.raise_for_status()
    except httpx.TimeoutException as error:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="reader-service request timed out",
        ) from error
    except httpx.HTTPStatusError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"reader-service returned HTTP {error.response.status_code}",
        ) from error
    except httpx.RequestError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="reader-service is unavailable",
        ) from error

    try:
        return [ReaderReport.model_validate(item) for item in response.json()]
    except (TypeError, ValueError) as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="reader-service returned an invalid reader list",
        ) from error


@router.get("/readers", response_model=list[ReaderReport])
async def readers(request: Request) -> list[ReaderReport]:
    return await fetch_readers(request)


@router.get("/summary", response_model=SummaryResponse)
async def summary(request: Request) -> SummaryResponse:
    reader_list = await fetch_readers(request)
    return SummaryResponse(
        total_readers=len(reader_list),
        outstanding_books=sum(reader.book_title is not None for reader in reader_list),
    )


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


@router.post("/export", status_code=status.HTTP_202_ACCEPTED)
async def export_report(request: Request) -> dict[str, str]:
    reader_list = await fetch_readers(request)
    filename = f"readers-{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}.csv"
    try:
        job_id = await request.app.state.report_publisher.publish(
            filename,
            readers_csv(reader_list),
        )
    except (AMQPException, OSError, RuntimeError) as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="report queue is unavailable",
        ) from error

    return {
        "job_id": str(job_id),
        "filename": filename,
        "status": "queued",
        "download_url": f"/file-storage/files/{filename}",
    }
