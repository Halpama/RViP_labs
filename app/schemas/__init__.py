"""Pydantic schemas (request/response DTOs)."""

from app.schemas.book_issue import BookIssueCreate, BookIssueOut, BookReturn
from app.schemas.reader import (
    ReaderCreate,
    ReaderOut,
    ReaderPage,
    ReaderUpdate,
)
from app.schemas.report import ReadersReport
from app.schemas.ticket import TicketConfiscate, TicketRestore

__all__ = [
    "BookIssueCreate",
    "BookIssueOut",
    "BookReturn",
    "ReaderCreate",
    "ReaderOut",
    "ReaderPage",
    "ReaderUpdate",
    "ReadersReport",
    "TicketConfiscate",
    "TicketRestore",
]
