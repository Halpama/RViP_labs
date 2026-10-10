from collections.abc import Callable

import httpx
import pytest_asyncio
from httpx import ASGITransport, AsyncClient, MockTransport, Request, Response

from app.main import app


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as test_client:
        yield test_client


@pytest_asyncio.fixture
async def reader_transport():
    handlers: list[Callable[[Request], Response]] = []

    def handler(request: Request) -> Response:
        if not handlers:
            return Response(200, json=[])
        return handlers.pop(0)(request)

    reader_client = httpx.AsyncClient(
        transport=MockTransport(handler),
        base_url="http://reader-service:3001",
        timeout=5.0,
    )
    app.state.reader_client = reader_client
    try:
        yield handlers
    finally:
        await reader_client.aclose()
