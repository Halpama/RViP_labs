"""Business logic for the library readers domain.

The service layer works with an injected ``AsyncSession`` and raises domain
exceptions; HTTP concerns stay in the router layer.

Concurrency note: mutations of a reader row use ``SELECT ... FOR UPDATE``
(row lock) so that concurrent book-issue/return operations on the same
reader cannot lose JSONB updates.
"""

from datetime import date, datetime, timedelta, timezone
from typing import Any

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import IssueStatus, Reader, TicketStatus
from app.schemas.book_issue import BookIssueCreate, BookReturn
from app.schemas.reader import ReaderCreate, ReaderOut, ReaderUpdate
from app.schemas.report import ReadersReport
from app.schemas.ticket import TicketConfiscate, TicketRestore
from app.services.exceptions import (
    BookNotOnHandError,
    DuplicateTicketNumberError,
    EmptyUpdateError,
    ReaderNotFoundError,
    TicketAlreadyConfiscatedError,
    TicketNotIssuedError,
)

DEFAULT_LOAN_DAYS = 30

# SQL predicate "reader has at least one issued book" over the JSONB column.
_HAS_ISSUED_SQL = 'jsonb_path_exists(books_on_hand, \'$[*] ? (@.status == "issued")\')'
_ISSUED_ARRAY_SQL = '\'$[*] ? (@.status == "issued")\''


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


async def _get_reader_for_update(session: AsyncSession, reader_id: int) -> Reader:
    """Load a reader with a row-level lock (FOR UPDATE)."""
    stmt = select(Reader).where(Reader.id == reader_id).with_for_update()
    reader = await session.scalar(stmt)
    if reader is None:
        raise ReaderNotFoundError(f"Читатель с id={reader_id} не найден.")
    return reader


async def _ticket_number_exists(
    session: AsyncSession, ticket_number: str, exclude_id: int | None = None
) -> bool:
    stmt = select(func.count()).select_from(Reader).where(
        Reader.ticket_number == ticket_number
    )
    if exclude_id is not None:
        stmt = stmt.where(Reader.id != exclude_id)
    return (await session.scalar(stmt)) > 0


async def _generate_ticket_number(session: AsyncSession) -> str:
    """Generate a sequential ticket number like ``Б-000001``."""
    seq = await session.scalar(select(func.coalesce(func.max(Reader.id), 0)))
    next_value = int(seq or 0) + 1
    candidate = f"Б-{next_value:06d}"
    while await _ticket_number_exists(session, candidate):
        next_value += 1
        candidate = f"Б-{next_value:06d}"
    return candidate


def _to_out(reader: Reader) -> dict[str, Any]:
    """ORM -> response DTO (adds computed books_count)."""
    result = ReaderOut.model_validate(reader).model_dump()
    result["books_count"] = len(reader.active_issues())
    return result


# --------------------------------------------------------------------- CRUD


async def create_reader(session: AsyncSession, payload: ReaderCreate) -> dict[str, Any]:
    """Добавить читателя (билет выдаётся автоматически, если номер не задан)."""
    if payload.ticket_number and await _ticket_number_exists(
        session, payload.ticket_number
    ):
        raise DuplicateTicketNumberError(
            f"Читательский билет {payload.ticket_number!r} уже зарегистрирован."
        )

    reader = Reader(
        **payload.model_dump(exclude={"ticket_number"}, exclude_none=True),
        ticket_number=payload.ticket_number or await _generate_ticket_number(session),
        ticket_status=TicketStatus.ACTIVE,
        ticket_issued_at=_utcnow(),
        books_on_hand=[],
    )
    session.add(reader)
    await session.flush()
    await session.refresh(reader)
    return _to_out(reader)


async def get_reader(session: AsyncSession, reader_id: int) -> dict[str, Any]:
    reader = await session.get(Reader, reader_id)
    if reader is None:
        raise ReaderNotFoundError(f"Читатель с id={reader_id} не найден.")
    return _to_out(reader)


async def list_readers(
    session: AsyncSession,
    *,
    search: str | None = None,
    ticket_status: TicketStatus | None = None,
    has_books: bool | None = None,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[dict[str, Any]], int]:
    """Постраничный список читателей с фильтрами."""
    conditions = []
    if search:
        conditions.append(Reader.full_name.ilike(f"%{search}%"))
    if ticket_status:
        conditions.append(Reader.ticket_status == ticket_status.value)
    if has_books is True:
        conditions.append(text(_HAS_ISSUED_SQL))
    elif has_books is False:
        conditions.append(text(f"NOT {_HAS_ISSUED_SQL}"))

    total = await session.scalar(
        select(func.count()).select_from(Reader).where(*conditions)
    )
    rows = await session.scalars(
        select(Reader)
        .where(*conditions)
        .order_by(Reader.id)
        .limit(limit)
        .offset(offset)
    )
    return [_to_out(r) for r in rows], int(total or 0)


async def update_reader(
    session: AsyncSession, reader_id: int, payload: ReaderUpdate
) -> dict[str, Any]:
    """Отредактировать данные читателя (частичное обновление)."""
    reader = await _get_reader_for_update(session, reader_id)

    changes = payload.model_dump(exclude_unset=True)
    if not changes:
        raise EmptyUpdateError("Не передано ни одного поля для обновления.")

    new_ticket = changes.get("ticket_number")
    if new_ticket and await _ticket_number_exists(
        session, new_ticket, exclude_id=reader_id
    ):
        raise DuplicateTicketNumberError(
            f"Читательский билет {new_ticket!r} уже зарегистрирован."
        )

    for field, value in changes.items():
        setattr(reader, field, value)
    await session.flush()
    await session.refresh(reader)
    return _to_out(reader)


async def delete_reader(session: AsyncSession, reader_id: int) -> None:
    """Удалить читателя (нельзя удалить, пока книги на руках)."""
    reader = await _get_reader_for_update(session, reader_id)
    if reader.active_issues():
        raise TicketNotIssuedError(
            "Нельзя удалить читателя: у него есть незавершённые выдачи книг."
        )
    await session.delete(reader)
    await session.flush()


# -------------------------------------------------------------- Ticket rules


async def confiscate_ticket(
    session: AsyncSession, reader_id: int, payload: TicketConfiscate
) -> dict[str, Any]:
    """Изъять читательский билет (временно — suspended, либо аннулировать)."""
    reader = await _get_reader_for_update(session, reader_id)
    if reader.ticket_status != TicketStatus.ACTIVE:
        raise TicketAlreadyConfiscatedError(
            f"Билет {reader.ticket_number!r} уже изят (статус: {reader.ticket_status})."
        )

    reader.ticket_status = (
        TicketStatus.SUSPENDED if payload.suspend else TicketStatus.REVOKED
    )
    reader.ticket_confiscated_at = _utcnow()
    reader.confiscation_reason = payload.reason
    await session.flush()
    await session.refresh(reader)
    return _to_out(reader)


async def restore_ticket(
    session: AsyncSession, reader_id: int, payload: TicketRestore
) -> dict[str, Any]:
    """Вернуть ранее изъятый (suspended) билет читателю."""
    reader = await _get_reader_for_update(session, reader_id)
    if reader.ticket_status == TicketStatus.ACTIVE:
        raise TicketNotIssuedError("Билет и так активен — возвращать нечего.")
    if reader.ticket_status == TicketStatus.REVOKED:
        raise TicketAlreadyConfiscatedError(
            "Аннулированный билет нельзя вернуть — оформите читателю новый билет."
        )

    reader.ticket_status = TicketStatus.ACTIVE
    reader.ticket_confiscated_at = None
    reader.confiscation_reason = payload.comment
    await session.flush()
    await session.refresh(reader)
    return _to_out(reader)


# --------------------------------------------------------------- Book issuing


async def issue_book(
    session: AsyncSession, reader_id: int, payload: BookIssueCreate
) -> dict[str, Any]:
    """Выдать книгу на руки. Билет читателя должен быть активен."""
    reader = await _get_reader_for_update(session, reader_id)
    if reader.ticket_status != TicketStatus.ACTIVE:
        raise TicketAlreadyConfiscatedError(
            "Выдача невозможна: читательский билет изят или аннулирован."
        )

    today = date.today()
    record = {
        **payload.model_dump(),
        "due_date": (
            payload.due_date or (today + timedelta(days=DEFAULT_LOAN_DAYS))
        ).isoformat(),
        "status": IssueStatus.ISSUED.value,
        "issue_date": today.isoformat(),
        "return_date": None,
    }
    # JSONB mutation: re-assign a new object so SQLAlchemy tracks the change.
    reader.books_on_hand = [*reader.books_on_hand, record]
    await session.flush()
    await session.refresh(reader)
    return _to_out(reader)


async def return_book(
    session: AsyncSession, reader_id: int, book_index: int, payload: BookReturn
) -> dict[str, Any]:
    """Принять книгу обратно в фонд.

    Запись остаётся в истории читателя со статусом ``returned``.
    """
    reader = await _get_reader_for_update(session, reader_id)

    issues = list(reader.books_on_hand)
    if book_index < 0 or book_index >= len(issues):
        raise BookNotOnHandError(f"Выдача с индексом {book_index} не найдена.")
    if issues[book_index].get("status") != IssueStatus.ISSUED.value:
        raise BookNotOnHandError("Эта книга уже возвращена в фонд.")

    issues[book_index] = {
        **issues[book_index],
        "status": IssueStatus.RETURNED.value,
        "return_date": (payload.return_date or date.today()).isoformat(),
    }
    reader.books_on_hand = issues
    await session.flush()
    await session.refresh(reader)
    return _to_out(reader)


# --------------------------------------------------------------------- Report


async def build_report(session: AsyncSession) -> ReadersReport:
    """Отчёт: всего читателей и сколько из них имеет книги на руках.

    Один агрегирующий запрос к PostgreSQL над JSONB-колонкой ``books_on_hand``.
    """
    issued_len = func.jsonb_array_length(
        func.jsonb_path_query_array(Reader.books_on_hand, text(_ISSUED_ARRAY_SQL))
    )
    stmt = select(
        func.count(),
        func.count().filter(text(_HAS_ISSUED_SQL)),
        func.coalesce(func.sum(issued_len), 0),
        func.count().filter(Reader.ticket_status == TicketStatus.ACTIVE.value),
    )
    total, with_books, books_total, active_tickets = (await session.execute(stmt)).one()
    share = round(with_books / total * 100, 2) if total else 0.0

    return ReadersReport(
        total_readers=total,
        readers_with_books=with_books,
        readers_without_books=total - with_books,
        total_books_on_hand=int(books_total),
        readers_with_active_ticket=active_tickets,
        tickets_confiscated=total - active_tickets,
        share_with_books_percent=share,
    )
