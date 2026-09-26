"""Report schema: total readers and how many of them hold books."""

from pydantic import BaseModel, Field


class ReadersReport(BaseModel):
    """Отчёт о читателях библиотеки."""

    total_readers: int = Field(..., description="Всего читателей в базе.")
    readers_with_books: int = Field(
        ..., description="Читатели, у которых есть хотя бы одна книга на руках."
    )
    readers_without_books: int = Field(
        ..., description="Читатели без книг на руках."
    )
    total_books_on_hand: int = Field(
        ..., description="Суммарное количество книг на руках у всех читателей."
    )
    readers_with_active_ticket: int = Field(
        ..., description="Читатели с активным (не изъятых) билетом."
    )
    tickets_confiscated: int = Field(
        ..., description="Число читателей с изъятым/аннулированным билетом."
    )
    share_with_books_percent: float = Field(
        ..., description="Доля читателей с книгами на руках, %."
    )
