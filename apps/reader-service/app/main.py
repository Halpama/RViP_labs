import json
import logging
import os
import socket

from fastapi import Depends, FastAPI, Form, HTTPException, status
from fastapi.responses import Response
from starlette.requests import Request

from .auth import create_access_token
from .config import get_settings
from .auth import require_auth
from .observability import metrics_response, observe_request
from .routers import readers
from .tracing import configure_tracing

request_logger = logging.getLogger("request")


def create_app() -> FastAPI:
    configure_tracing()
    get_settings()
    application = FastAPI(title="Library Reader Service", version="1.0.0", root_path="/reader-service")
    application.include_router(readers.router)

    application.middleware("http")(observe_request)

    return application


app = create_app()


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/metrics")
async def metrics() -> Response:
    return metrics_response()


@app.post("/auth/token")
async def token(username: str = Form(...), password: str = Form(...)) -> dict[str, str]:
    settings = get_settings()
    if username != settings.auth_username or password != settings.auth_password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid credentials")
    return {"access_token": create_access_token(username), "token_type": "bearer"}
