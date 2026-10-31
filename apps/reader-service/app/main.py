import json
import logging
import os
import socket

from fastapi import FastAPI
from starlette.requests import Request

from .config import get_settings
from .routers import readers

request_logger = logging.getLogger("request")


def create_app() -> FastAPI:
    get_settings()
    application = FastAPI(title="Library Reader Service", version="1.0.0", root_path="/reader-service")
    application.include_router(readers.router)

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
                        "instance_name": os.environ.get("INSTANCE_NAME", "reader-service"),
                    },
                    separators=(",", ":"),
                )
            )
        return response

    return application


app = create_app()
