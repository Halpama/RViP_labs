from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_session
from ..models import Reader
from ..schemas import SummaryResponse

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/summary", response_model=SummaryResponse)
async def summary(session: AsyncSession = Depends(get_session)) -> SummaryResponse:
    total, outstanding = (
        await session.execute(
            select(
                func.count(Reader.id),
                func.count(Reader.book_title),
            )
        )
    ).one()
    return SummaryResponse(total_readers=total, outstanding_books=outstanding)
