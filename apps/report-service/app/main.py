from contextlib import asynccontextmanager
import json
import logging
import os
import socket

import httpx
from aio_pika.exceptions import AMQPException
from fastapi import FastAPI, Form, HTTPException, status
from fastapi.responses import Response
from starlette.requests import Request

from .config import get_settings
from .auth import create_access_token
from .observability import metrics_response, observe_request
from .queue import ReportPublisher
from .routers import reports
from .tracing import configure_tracing

request_logger = logging.getLogger("request")
queue_logger = logging.getLogger("queue")


@asynccontextmanager
async def lifespan(application: FastAPI):
    configure_tracing()
    application.state.settings = get_settings()
    application.state.http_client = httpx.AsyncClient(timeout=5.0)
    application.state.report_publisher = ReportPublisher(
        application.state.settings.rabbitmq_url
    )
    try:
        try:
            await application.state.report_publisher.connect()
        except (AMQPException, OSError) as error:
            queue_logger.warning("RabbitMQ is unavailable at startup: %s", error)
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
