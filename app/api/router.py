"""API v1 router aggregation."""

from fastapi import APIRouter

from app.api import books, readers, reports, tickets

api_router = APIRouter()
api_router.include_router(readers.router)
api_router.include_router(tickets.router)
api_router.include_router(books.router)
api_router.include_router(reports.router)
