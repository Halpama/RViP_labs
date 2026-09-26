"""Reader request/response schemas."""

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.enums import TicketStatus
from app.schemas.book_issue import BookIssueOut


class ReaderBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    full_name: str = Field(..., min_length=2, max_length=200, examples=["Иванов Иван Иванович"])
    phone: str | None = Field(None, max_length=50, examples=["+7 900 123-45-67"])
    email: EmailStr | None = Field(None, max_length=254, examples=["ivanov@example.com"])
    birth_date: date | None = Field(None, examples=["1990-05-15"])
    address: str | None = Field(None, max_length=255, examples=["г. Москва, ул. Ленина, д. 1"])
    ticket_number: str | None = Field(
        None,
        max_length=32,
        description="Номер читательского билета; если не указан — генерируется автоматически.",
        examples=["Б-000001"],
    )


class ReaderCreate(ReaderBase):
    """Добавление нового читателя."""


class ReaderUpdate(BaseModel):
    """Редактирование читателя (частичное обновление, PATCH-семантика)."""

    model_config = ConfigDict(str_strip_whitespace=True)

    full_name: str | None = Field(None, min_length=2, max_length=200)
    phone: str | None = Field(None, max_length=50)
    email: EmailStr | None = Field(None, max_length=254)
    birth_date: date | None = None
    address: str | None = Field(None, max_length=255)
    ticket_number: str | None = Field(None, max_length=32)


class ReaderOut(ReaderBase):
    """Читатель в ответе API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    ticket_status: TicketStatus
    ticket_issued_at: datetime | None = None
    ticket_confiscated_at: datetime | None = None
    confiscation_reason: str | None = None
    books_on_hand: list[BookIssueOut] = []
    created_at: datetime
    updated_at: datetime

    books_count: int = Field(0, description="Количество книг, фактически находящихся на руках.")


class ReaderPage(BaseModel):
    """Страница постраничного списка читателей."""

    items: list[ReaderOut]
    total: int = Field(..., description="Общее число читателей, удовлетворяющих фильтру.")
    limit: int
    offset: int
