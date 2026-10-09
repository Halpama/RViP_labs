from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ReaderReport(BaseModel):
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
