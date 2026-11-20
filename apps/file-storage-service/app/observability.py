import json
import logging
import os
import socket
import time
from uuid import uuid4

from opentelemetry import trace
from prometheus_client import Counter, Histogram, generate_latest
from starlette.requests import Request
from starlette.responses import Response

request_count = Counter("http_requests_total", "HTTP requests", ["method", "path", "status"])
request_duration = Histogram("http_request_duration_seconds", "HTTP request duration", ["method", "path"])
logger = logging.getLogger("request")


async def observe_request(request: Request, call_next) -> Response:
    started = time.perf_counter()
    request_id = request.headers.get("X-Request-ID", str(uuid4()))
    status_code = 500
    span = trace.get_tracer("file-storage-service").start_span(f"{request.method} {request.url.path}")
    try:
        response = await call_next(request)
        status_code = response.status_code
        response.headers["X-Request-ID"] = request_id
        return response
    finally:
        elapsed = time.perf_counter() - started
        request_count.labels(request.method, request.url.path, str(status_code)).inc()
        request_duration.labels(request.method, request.url.path).observe(elapsed)
        span.set_attribute("http.status_code", status_code)
        span.end()
        logger.info(json.dumps({
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": status_code,
            "duration_ms": round(elapsed * 1000, 2),
            "hostname": os.environ.get("HOSTNAME") or socket.gethostname(),
            "instance_name": os.environ.get("INSTANCE_NAME", "file-storage-service"),
        }, separators=(",", ":")))


def metrics_response() -> Response:
    return Response(generate_latest(), media_type="text/plain; version=0.0.4")
