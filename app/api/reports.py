"""Reporting endpoint."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import ReadersReport
from app.services import reader_service

router = APIRouter(prefix="/reports", tags=["Отчёты"])

DbSession = Annotated[AsyncSession, Depends(get_db)]


@router.get(
    "/readers",
    response_model=ReadersReport,
    summary="Отчёт по читателям",
    description=(
        "Сколько всего читателей в библиотеке и сколько из них имеют книги на руках "
        "(плюс производные показатели)."
    ),
)
async def readers_report(session: DbSession) -> ReadersReport:
    return await reader_service.build_report(session)
