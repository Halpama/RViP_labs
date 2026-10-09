from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_session
from ..models import Reader
from ..schemas import ReaderReport, SummaryResponse

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/readers", response_model=list[ReaderReport])
async def readers(session: AsyncSession = Depends(get_session)) -> list[Reader]:
    return list((await session.execute(select(Reader).order_by(Reader.id))).scalars())


@router.get("/summary", response_model=SummaryResponse)
async def summary(session: AsyncSession = Depends(get_session)) -> SummaryResponse:
    total, outstanding = (
        await session.execute(select(func.count(Reader.id), func.count(Reader.book_title)))
    ).one()
    return SummaryResponse(total_readers=total, outstanding_books=outstanding)
