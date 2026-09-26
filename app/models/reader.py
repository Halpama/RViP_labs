"""ORM model: the single ``readers`` table of the library domain.

The whole domain (readers, reader tickets, book issues, reports) is stored in
one table: a book issue is represented as a JSONB array element inside the
``books_on_hand`` column, so there are no joins and exactly one table.
"""

from datetime import date, datetime

from sqlalchemy import CheckConstraint, Date, DateTime, Index, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.enums import IssueStatus, TicketStatus


class Reader(Base):
    """Читатель библиотеки вместе с читательским билетом и книгами на руках."""

    __tablename__ = "readers"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(50))
    email: Mapped[str | None] = mapped_column(String(254))
    birth_date: Mapped[date | None] = mapped_column(Date)
    address: Mapped[str | None] = mapped_column(String(255))

    # --- Читательский билет -------------------------------------------------
    ticket_number: Mapped[str | None] = mapped_column(String(32), unique=True)
    ticket_status: Mapped[TicketStatus] = mapped_column(
        String(20),
        nullable=False,
        default=TicketStatus.ACTIVE,
        server_default=TicketStatus.ACTIVE.value,
    )
    ticket_issued_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )
    ticket_confiscated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
    confiscation_reason: Mapped[str | None] = mapped_column(String(255))

    # --- Книги на руках (JSONB-массив объектов выдачи) ----------------------
    # Элемент массива:
    # {"book_title": str, "author": str|None, "isbn": str|None,
    #  "issue_date": iso-date, "due_date": iso-date|None,
    #  "status": "issued"|"returned", "return_date": iso-date|None}
    books_on_hand: Mapped[list[dict]] = mapped_column(
        JSONB,
        nullable=False,
        default=list,
        server_default="[]",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    __table_args__ = (
        CheckConstraint(
            f"ticket_status IN ('{TicketStatus.ACTIVE}', "
            f"'{TicketStatus.SUSPENDED}', '{TicketStatus.REVOKED}')",
            name="ticket_status_valid",
        ),
        Index("ix_readers_full_name", "full_name"),
        # GIN-индекс по книгам на руках создаётся в миграции Alembic
        # (SQLAlchemy не умеет декларативно задавать operator classes).
    )

    # Convenience helpers -----------------------------------------------------

    def active_issues(self) -> list[dict]:
        """Выдачи со статусом ``issued`` (книги фактически на руках)."""
        return [b for b in self.books_on_hand if b.get("status") == IssueStatus.ISSUED]

    @property
    def books_count(self) -> int:
        return len(self.active_issues())
