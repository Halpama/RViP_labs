"""Reader-ticket operations: confiscation and restoration."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import ReaderOut, TicketConfiscate, TicketRestore
from app.services import reader_service

router = APIRouter(prefix="/readers/{reader_id}/ticket", tags=["Читательские билеты"])

DbSession = Annotated[AsyncSession, Depends(get_db)]


@router.post(
    "/confiscate",
    response_model=ReaderOut,
    summary="Изъять читательский билет",
    description=(
        "Временное изъятие (suspend=true) или аннулирование (suspend=false). "
        "Пока билет изят, выдача книг невозможна."
    ),
)
async def confiscate_ticket(
    payload: TicketConfiscate,
    session: DbSession,
    reader_id: Annotated[int, Path(ge=1)],
) -> ReaderOut:
    return await reader_service.confiscate_ticket(session, reader_id, payload)


@router.post(
    "/restore",
    response_model=ReaderOut,
    summary="Вернуть изъятый билет",
    description="Возвращает временно изятый (suspended) билет. Аннулированный не возвращается.",
)
async def restore_ticket(
    payload: TicketRestore,
    session: DbSession,
    reader_id: Annotated[int, Path(ge=1)],
) -> ReaderOut:
    return await reader_service.restore_ticket(session, reader_id, payload)
