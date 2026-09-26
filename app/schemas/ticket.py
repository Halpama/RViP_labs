"""Ticket confiscation / restoration schemas."""

from pydantic import BaseModel, Field


class TicketConfiscate(BaseModel):
    """Изъятие читательского билета."""

    reason: str = Field(
        ...,
        min_length=3,
        max_length=255,
        description="Причина изъятия билета (например, просрочка возврата книг).",
        examples=["Просрочка возврата книг более 60 дней"],
    )
    suspend: bool = Field(
        True,
        description=(
            "True — временное изъятие (статус suspended, билет можно вернуть); "
            "False — аннулирование (статус revoked)."
        ),
    )


class TicketRestore(BaseModel):
    """Возврат ранее изъятого читательского билета."""

    comment: str | None = Field(None, max_length=255, examples=["Задолженность погашена"])
