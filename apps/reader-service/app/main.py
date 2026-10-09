from fastapi import FastAPI

from .config import get_settings
from .routers import readers


def create_app() -> FastAPI:
    get_settings()
    application = FastAPI(title="Library Reader Service", version="1.0.0", root_path="/reader-service")
    application.include_router(readers.router)
    return application


app = create_app()
