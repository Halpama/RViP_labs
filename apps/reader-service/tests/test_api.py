import pytest
from httpx import ASGITransport, AsyncClient

from app.db import get_session
from app.main import app


@pytest.mark.asyncio
async def test_reader_lifecycle(session):
    async def override_session():
        yield session

    app.dependency_overrides[get_session] = override_session
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            created = await client.post(
                "/readers",
                json={"full_name": "Ada Lovelace", "card_number": "CARD-1"},
            )
            assert created.status_code == 201
            reader_id = created.json()["id"]

            issued = await client.post(f"/readers/{reader_id}/issue-book", json={"book_title": "Algorithms"})
            assert issued.status_code == 200
            assert issued.json()["book_title"] == "Algorithms"

            blocked = await client.delete(f"/readers/{reader_id}")
            assert blocked.status_code == 409

            returned = await client.post(f"/readers/{reader_id}/return-book")
            assert returned.status_code == 200
            assert returned.json()["book_title"] is None

            deleted = await client.delete(f"/readers/{reader_id}")
            assert deleted.status_code == 204
    finally:
        app.dependency_overrides.clear()
