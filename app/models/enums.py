"""Domain enums shared by ORM models and Pydantic schemas."""

from enum import StrEnum


class TicketStatus(StrEnum):
    """Состояние читательского билета."""

    ACTIVE = "active"          # билет на руках у читателя
    SUSPENDED = "suspended"    # билет изъят временно
    REVOKED = "revoked"        # билет аннулирован


class IssueStatus(StrEnum):
    """Статус выдачи книги читателю."""

    ISSUED = "issued"      # книга на руках
    RETURNED = "returned"  # книга возвращена в фонд
