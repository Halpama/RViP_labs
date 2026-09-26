"""Schemas for book issue records stored inside the reader JSONB column."""

from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import IssueStatus


class BookIssueCreate(BaseModel):
    """Запрос на выдачу книги читателю на руки."""

    model_config = ConfigDict(str_strip_whitespace=True)

    book_title: str = Field(..., min_length=1, max_length=255, examples=["Мастер и Маргарита"])
    author: str | None = Field(None, max_length=200, examples=["Михаил Булгаков"])
    isbn: str | None = Field(None, max_length=32, examples=["978-5-389-06927-1"])
    due_date: date | None = Field(
        None, description="Плановая дата возврата (по умолчанию +30 дней)."
    )


class BookIssueOut(BookIssueCreate):
    """Выдача книги в ответе API."""

    status: IssueStatus = IssueStatus.ISSUED
    issue_date: date
    return_date: date | None = None


class BookReturn(BaseModel):
    """Возврат книги в фонд."""

    return_date: date | None = Field(None, description="По умолчанию — сегодня.")
