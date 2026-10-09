from fastapi import FastAPI

from .config import get_settings
from .routers import reports


def create_app() -> FastAPI:
    get_settings()
    application = FastAPI(title="Library Report Service", version="1.0.0", root_path="/report-service")
    application.include_router(reports.router)
    return application


app = create_app()
