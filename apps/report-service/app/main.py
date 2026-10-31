from contextlib import asynccontextmanager
import json
import logging
import os
import socket

import httpx
from aio_pika.exceptions import AMQPException
from fastapi import FastAPI
from starlette.requests import Request

from .config import get_settings
from .queue import ReportPublisher
from .routers import reports

request_logger = logging.getLogger("request")
queue_logger = logging.getLogger("queue")


@asynccontextmanager
async def lifespan(application: FastAPI):
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

    @application.middleware("http")
    async def log_requests(request: Request, call_next):
        try:
            response = await call_next(request)
        except Exception:
            status_code = 500
            raise
        else:
            status_code = response.status_code
        finally:
            request_logger.info(
                json.dumps(
                    {
                        "method": request.method,
                        "path": request.url.path,
                        "status_code": status_code,
                        "hostname": os.environ.get("HOSTNAME") or socket.gethostname(),
                        "instance_name": os.environ.get("INSTANCE_NAME", "report-service"),
                    },
                    separators=(",", ":"),
                )
            )
        return response

    return application


app = create_app()
