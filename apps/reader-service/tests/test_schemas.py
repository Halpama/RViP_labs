import pytest
from pydantic import ValidationError

from app.schemas import IssueBookRequest, ReaderCreate


def test_reader_create_requires_non_empty_fields():
    with pytest.raises(ValidationError):
        ReaderCreate(full_name="", card_number="card-1")


def test_issue_book_rejects_blank_title():
    with pytest.raises(ValidationError):
        IssueBookRequest(book_title="  ")
