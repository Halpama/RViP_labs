"""Book issuing / returning endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas import BookIssueCreate, BookReturn, ReaderOut
from app.services import reader_service

router = APIRouter(prefix="/readers/{reader_id}/books", tags=["Выдача книг"])

DbSession = Annotated[AsyncSession, Depends(get_db)]


@router.post(
    "",
    response_model=ReaderOut,
    summary="Выдать книгу на руки",
    description=(
        "Добавляет активную выдачу читателю. Невозможна, если билет изят или аннулирован."
    ),
)
async def issue_book(
    payload: BookIssueCreate,
    session: DbSession,
    reader_id: Annotated[int, Path(ge=1)],
) -> ReaderOut:
    return await reader_service.issue_book(session, reader_id, payload)


@router.post(
    "/{book_index}/return",
    response_model=ReaderOut,
    summary="Принять книгу обратно в фонд",
    description=(
        "book_index — позиция выдачи в массиве books_on_hand карточки читателя "
        "(нумерация с 0). Запись остаётся в истории со статусом returned."
    ),
)
async def return_book(
    session: DbSession,
    reader_id: Annotated[int, Path(ge=1)],
    book_index: Annotated[int, Path(ge=0)],
    payload: BookReturn | None = None,
) -> ReaderOut:
    return await reader_service.return_book(
        session, reader_id, book_index, payload or BookReturn()
    )
