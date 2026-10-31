from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

from .config import get_settings
from .queue import ReportPublisher
from .routers import reports


@asynccontextmanager
async def lifespan(application: FastAPI):
    application.state.settings = get_settings()
    application.state.http_client = httpx.AsyncClient(timeout=5.0)
    application.state.report_publisher = ReportPublisher(
        application.state.settings.rabbitmq_url
    )
    try:
        await application.state.report_publisher.connect()
        yield
    finally:
        await application.state.http_client.aclose()
        await application.state.report_publisher.close()


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
