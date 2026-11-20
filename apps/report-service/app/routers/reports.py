import asyncio
import re

import httpx
from aio_pika.exceptions import AMQPException
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import Response

from ..schemas import ReaderReport, SummaryResponse
from ..saga import ReportExportSaga

router = APIRouter(prefix="/reports", tags=["reports"])
SAFE_FILENAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")


async def request_file(
    client: httpx.AsyncClient,
    file_storage_service_url: str,
    filename: str,
) -> httpx.Response:
    future: asyncio.Future[httpx.Response] = asyncio.ensure_future(
        client.get(f"{file_storage_service_url}/files/{filename}")
    )
    return await future


async def fetch_export(request: Request, filename: str) -> httpx.Response:
    if not SAFE_FILENAME.fullmatch(filename):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="file not found")

    client: httpx.AsyncClient = request.app.state.http_client
    settings = request.app.state.settings
    try:
        response = await request_file(
            client,
            settings.file_storage_service_url,
            filename,
        )
        response.raise_for_status()
    except httpx.TimeoutException as error:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="file-storage-service request timed out",
        ) from error
    except httpx.HTTPStatusError as error:
        if error.response.status_code == status.HTTP_404_NOT_FOUND:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="file not found",
            ) from error
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"file-storage-service returned HTTP {error.response.status_code}",
        ) from error
    except httpx.RequestError as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="file-storage-service is unavailable",
        ) from error
    return response


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


@router.post("/export", status_code=status.HTTP_202_ACCEPTED)
async def export_report(request: Request) -> dict[str, str]:
    reader_list = await fetch_readers(request)
    try:
        result = await ReportExportSaga(request.app.state.report_publisher).execute(
            reader_list
        )
    except (AMQPException, OSError, RuntimeError) as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="report queue is unavailable",
        ) from error

    return {
        "job_id": str(result.job_id),
        "filename": result.filename,
        "status": "queued",
        "download_url": f"/file-storage/files/{result.filename}",
    }


@router.get("/export/{filename}")
async def download_export(request: Request, filename: str) -> Response:
    response = await fetch_export(request, filename)
    return Response(
        content=response.content,
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )
