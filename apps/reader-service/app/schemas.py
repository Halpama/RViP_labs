from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ReaderCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=255)
    card_number: str = Field(min_length=1, max_length=100)


class ReaderUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    card_number: str | None = Field(default=None, min_length=1, max_length=100)
    card_active: bool | None = None


class IssueBookRequest(BaseModel):
    book_title: str = Field(min_length=1, max_length=500)

    @field_validator("book_title")
    @classmethod
    def title_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("book_title must not be blank")
        return value


class ReaderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    card_number: str
    card_active: bool
    book_title: str | None
    registered_at: datetime


class SummaryResponse(BaseModel):
    total_readers: int
    outstanding_books: int
