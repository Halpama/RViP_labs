import httpx
from fastapi import APIRouter, HTTPException, Request, status

from ..schemas import ReaderReport, SummaryResponse

router = APIRouter(prefix="/reports", tags=["reports"])


async def fetch_readers(request: Request) -> list[ReaderReport]:
    client: httpx.AsyncClient = request.app.state.reader_client
    try:
        response = await client.get("/readers")
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
