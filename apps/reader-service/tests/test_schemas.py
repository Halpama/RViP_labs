import pytest
from pydantic import ValidationError

from app.schemas import IssueBookRequest, ReaderCreate, ReaderUpdate


def test_reader_create_requires_non_empty_fields():
    with pytest.raises(ValidationError):
        ReaderCreate(full_name="", card_number="card-1")


def test_issue_book_rejects_blank_title():
    with pytest.raises(ValidationError):
        IssueBookRequest(book_title="  ")


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"full_name": None},
        {"full_name": ""},
        {"full_name": "  "},
        {"card_number": None},
        {"card_number": ""},
        {"card_number": "  "},
        {"card_active": False},
        {"book_title": "A book"},
        {"nickname": "Unknown"},
    ],
)
def test_reader_update_rejects_invalid_payloads(payload):
    with pytest.raises(ValidationError):
        ReaderUpdate.model_validate(payload)
