from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

from .config import get_settings
from .routers import reports


@asynccontextmanager
async def lifespan(application: FastAPI):
    application.state.settings = get_settings()
    application.state.http_client = httpx.AsyncClient(timeout=5.0)
    try:
        yield
    finally:
        await application.state.http_client.aclose()


def create_app() -> FastAPI:
    application = FastAPI(
        title="Library Report Service",
        version="1.0.0",
        root_path="/report-service",
        lifespan=lifespan,
    )
    application.include_router(reports.router)
    return application


app = create_app()
