"""Readers CRUD endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import TicketStatus
from app.schemas import ReaderCreate, ReaderOut, ReaderPage, ReaderUpdate
from app.services import reader_service

router = APIRouter(prefix="/readers", tags=["Читатели"])

DbSession = Annotated[AsyncSession, Depends(get_db)]


@router.post(
    "",
    response_model=ReaderOut,
    status_code=status.HTTP_201_CREATED,
    summary="Добавить читателя",
    description="Создаёт читателя и автоматически оформляет читательский билет.",
)
async def create_reader(payload: ReaderCreate, session: DbSession) -> ReaderOut:
    return await reader_service.create_reader(session, payload)


@router.get(
    "",
    response_model=ReaderPage,
    summary="Список читателей",
    description="Постраничный список с фильтрами по ФИО, статусу билета и наличию книг.",
)
async def list_readers(
    session: DbSession,
    search: Annotated[str | None, Query(description="Подстрока ФИО")] = None,
    ticket_status: Annotated[TicketStatus | None, Query()] = None,
    has_books: Annotated[bool | None, Query(description="Есть книги на руках")] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> ReaderPage:
    items, total = await reader_service.list_readers(
        session,
        search=search,
        ticket_status=ticket_status,
        has_books=has_books,
        limit=limit,
        offset=offset,
    )
    return ReaderPage(items=items, total=total, limit=limit, offset=offset)


@router.get(
    "/{reader_id}",
    response_model=ReaderOut,
    summary="Карточка читателя",
)
async def get_reader(
    session: DbSession,
    reader_id: Annotated[int, Path(ge=1)],
) -> ReaderOut:
    return await reader_service.get_reader(session, reader_id)


@router.patch(
    "/{reader_id}",
    response_model=ReaderOut,
    summary="Редактировать читателя",
    description="Частичное обновление данных читателя (передайте только изменяемые поля).",
)
async def update_reader(
    payload: ReaderUpdate,
    session: DbSession,
    reader_id: Annotated[int, Path(ge=1)],
) -> ReaderOut:
    return await reader_service.update_reader(session, reader_id, payload)


@router.delete(
    "/{reader_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить читателя",
    description="Удаление невозможно, пока у читателя есть книги на руках.",
)
async def delete_reader(
    session: DbSession,
    reader_id: Annotated[int, Path(ge=1)],
) -> None:
    await reader_service.delete_reader(session, reader_id)
