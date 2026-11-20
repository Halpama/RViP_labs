import os
from collections.abc import Mapping
from contextlib import contextmanager
from typing import Any

from opentelemetry import context, trace
from opentelemetry.propagate import extract, inject
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter


def configure_tracing() -> None:
    if trace.get_tracer_provider().__class__.__name__ != "ProxyTracerProvider":
        return
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    if not endpoint:
        return
    provider = TracerProvider(
        resource=Resource.create(
            {"service.name": os.getenv("OTEL_SERVICE_NAME", "report-service")}
        )
    )
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint)))
    trace.set_tracer_provider(provider)


def inject_headers(headers: dict[str, Any]) -> None:
    inject(headers)


def extract_context(headers: Mapping[str, Any]):
    return extract({key: str(value) for key, value in headers.items()})


@contextmanager
def attach_context(carrier: Mapping[str, Any]):
    token = context.attach(extract_context(carrier))
    try:
        yield
    finally:
        context.detach(token)
