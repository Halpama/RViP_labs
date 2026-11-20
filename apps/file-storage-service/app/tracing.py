import os
from collections.abc import Mapping
from typing import Any

from opentelemetry import propagate
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter


def extract_context(headers: Mapping[str, Any]):
    return propagate.extract({key: str(value) for key, value in headers.items()})


def configure_tracing() -> None:
    if trace.get_tracer_provider().__class__.__name__ != "ProxyTracerProvider":
        return
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    if not endpoint:
        return
    provider = TracerProvider(
        resource=Resource.create(
            {"service.name": os.getenv("OTEL_SERVICE_NAME", "file-storage-service")}
        )
    )
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=endpoint)))
    trace.set_tracer_provider(provider)
