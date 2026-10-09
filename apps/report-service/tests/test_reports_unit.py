import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.db import get_session
from app.main import app


@pytest.fixture
def session():
    session = AsyncMock()
    return session


@pytest.fixture
async def client(session):
    app.dependency_overrides[get_session] = lambda: session
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_report_endpoints_return_empty_values_without_database(client, session):
    empty_rows = SimpleNamespace(scalars=lambda: iter(()))
    session.execute.side_effect = [
        empty_rows,
        SimpleNamespace(one=lambda: (0, 0)),
    ]

    assert (await client.get("/reports/readers")).json() == []
    assert (await client.get("/reports/summary")).json() == {
        "total_readers": 0,
        "outstanding_books": 0,
    }


@pytest.mark.asyncio
async def test_report_endpoints_serialize_rows_and_counts_without_database(client, session):
    reader = SimpleNamespace(
        id=7,
        full_name="Ada Lovelace",
        card_number="CARD-7",
        card_active=True,
        book_title="Algorithms",
        registered_at="2026-01-01T00:00:00Z",
    )
    session.execute.side_effect = [
        SimpleNamespace(scalars=lambda: iter((reader,))),
        SimpleNamespace(one=lambda: (2, 1)),
    ]

    response = await client.get("/reports/readers")
    assert response.status_code == 200
    assert response.json()[0]["card_number"] == "CARD-7"
    assert (await client.get("/reports/summary")).json() == {
        "total_readers": 2,
        "outstanding_books": 1,
    }


def test_postman_collection_contains_gateway_scenario_and_assertions():
    collection_path = Path(__file__).parents[3] / "postman" / "library.postman_collection.json"
    collection = json.loads(collection_path.read_text(encoding="utf-8"))
    scenario = next(item for item in collection["item"] if item["name"] == "Сквозной сценарий")
    assert len(scenario["item"]) == 7
    assert all(item.get("event") for item in scenario["item"])
    assert collection["variable"][0] == {
        "key": "base_url",
        "value": "http://127.0.0.1:8080",
    }
