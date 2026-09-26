"""FastAPI application factory and entrypoint.

Run locally::

    uvicorn app.main:app --reload

Swagger UI is served at ``/docs`` (OpenAPI JSON at ``/openapi.json``).
"""

import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.database import engine
from app.services.exceptions import (
    BookNotOnHandError,
    DomainError,
    DuplicateTicketNumberError,
    EmptyUpdateError,
    ReaderNotFoundError,
    TicketAlreadyConfiscatedError,
    TicketNotIssuedError,
)
from app.settings import get_settings

logger = logging.getLogger("app")

# Domain exception -> HTTP status code mapping.
_STATUS_MAP: dict[type[DomainError], int] = {
    ReaderNotFoundError: status.HTTP_404_NOT_FOUND,
    DuplicateTicketNumberError: status.HTTP_409_CONFLICT,
    TicketAlreadyConfiscatedError: status.HTTP_409_CONFLICT,
    TicketNotIssuedError: status.HTTP_409_CONFLICT,
    BookNotOnHandError: status.HTTP_404_NOT_FOUND,
    EmptyUpdateError: status.HTTP_400_BAD_REQUEST,
}


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Manage engine lifecycle (dispose connections on shutdown)."""
    logger.info("Starting up, DB URL: %s", get_settings().database_url)
    yield
    await engine.dispose()
    logger.info("Shutdown complete")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        description=settings.app_description,
        version=settings.app_version,
        lifespan=lifespan,
        docs_url="/docs",       # Swagger UI
        redoc_url="/redoc",     # ReDoc
        openapi_url="/openapi.json",
    )
    app.include_router(api_router, prefix=settings.api_prefix)

    @app.exception_handler(DomainError)
    async def domain_error_handler(_: Request, exc: DomainError) -> JSONResponse:
        code = _STATUS_MAP.get(type(exc), status.HTTP_400_BAD_REQUEST)
        return JSONResponse(status_code=code, content={"detail": exc.message})

    @app.get("/healthcheck", tags=["Service"], summary="Проверка работоспособности")
    async def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
