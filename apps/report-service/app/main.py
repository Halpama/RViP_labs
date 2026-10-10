from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

from .config import get_settings
from .routers import reports


@asynccontextmanager
async def lifespan(application: FastAPI):
    application.state.reader_client = httpx.AsyncClient(
        base_url=get_settings().reader_service_url,
        timeout=5.0,
    )
    try:
        yield
    finally:
        await application.state.reader_client.aclose()


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
