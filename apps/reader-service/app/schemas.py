from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ReaderCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=255)
    card_number: str = Field(min_length=1, max_length=100)


class ReaderUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    card_number: str | None = Field(default=None, min_length=1, max_length=100)

    @field_validator("full_name", "card_number")
    @classmethod
    def profile_field_must_not_be_blank(cls, value: str | None) -> str | None:
        if value is None or not value.strip():
            raise ValueError("profile fields must not be blank")
        return value

    @model_validator(mode="after")
    def must_include_profile_field(self) -> "ReaderUpdate":
        if not self.model_fields_set:
            raise ValueError("at least one profile field is required")
        return self


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
