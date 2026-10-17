from datetime import datetime, timezone

import httpx
import pytest
from httpx import Request, Response


def reader(reader_id: int, book_title: str | None) -> dict:
    return {
        "id": reader_id,
        "full_name": f"Reader {reader_id}",
        "card_number": f"CARD-{reader_id}",
        "card_active": True,
        "book_title": book_title,
        "registered_at": datetime(2026, 1, reader_id, tzinfo=timezone.utc).isoformat(),
    }


@pytest.mark.asyncio
async def test_reports_return_empty_values(client, reader_transport):
    reader_transport.append(lambda request: Response(200, json=[]))

    assert (await client.get("/reports/readers")).json() == []
    assert (await client.get("/reports/summary")).json() == {
        "total_readers": 0,
        "outstanding_books": 0,
    }


@pytest.mark.asyncio
async def test_reports_return_reader_fields_and_summary(client, reader_transport):
    payload = [reader(1, "Algorithms"), reader(2, None), reader(3, "Compilers")]
    reader_transport.append(lambda request: Response(200, json=payload))

    response = await client.get("/reports/readers")

    assert response.status_code == 200
    assert set(response.json()[0]) == {
        "id",
        "full_name",
        "card_number",
        "card_active",
        "book_title",
        "registered_at",
    }

    reader_transport.append(lambda request: Response(200, json=payload))
    assert (await client.get("/reports/summary")).json() == {
        "total_readers": 3,
        "outstanding_books": 2,
    }


@pytest.mark.asyncio
async def test_reader_service_error_is_returned_as_502(client, reader_transport):
    reader_transport.append(lambda request: Response(500, json={"detail": "database error"}))

    response = await client.get("/reports/readers")

    assert response.status_code == 502
    assert response.json() == {"detail": "reader-service returned HTTP 500"}


@pytest.mark.asyncio
async def test_reader_service_timeout_is_returned_as_504(client, reader_transport):
    def timeout(request: Request) -> Response:
        raise httpx.ReadTimeout("reader-service timed out", request=request)

    reader_transport.append(timeout)

    response = await client.get("/reports/summary")

    assert response.status_code == 504
    assert response.json() == {"detail": "reader-service request timed out"}


@pytest.mark.asyncio
async def test_export_sends_csv_to_file_storage(client, reader_transport):
    payload = [reader(1, "Algorithms"), reader(2, None)]
    reader_transport.append(lambda request: Response(200, json=payload))
    reader_transport.append(
        lambda request: Response(201, json={"filename": "readers-report.csv"})
    )

    response = await client.post("/reports/export")

    assert response.status_code == 200
    assert response.json() == {
        "filename": "readers-report.csv",
        "download_url": "/file-storage/files/readers-report.csv",
    }
