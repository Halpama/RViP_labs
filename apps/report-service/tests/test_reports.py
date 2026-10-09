import pytest


@pytest.mark.asyncio
async def test_empty_reports(client):
    assert (await client.get("/reports/readers")).json() == []
    assert (await client.get("/reports/summary")).json() == {
        "total_readers": 0, "outstanding_books": 0
    }


@pytest.mark.asyncio
async def test_report_routes_are_read_only(client, session):
    from app.models import Reader
    from sqlalchemy import insert, select

    await session.execute(insert(Reader).values(full_name="Ada", card_number="R-1", card_active=True))
    await session.commit()
    before = (await session.execute(select(Reader))).scalars().all()
    assert (await client.get("/reports/readers")).status_code == 200
    assert (await client.get("/reports/summary")).status_code == 200
    after = (await session.execute(select(Reader))).scalars().all()
    assert [(r.id, r.card_number) for r in before] == [(r.id, r.card_number) for r in after]


@pytest.mark.asyncio
async def test_populated_reports_include_reader_fields_and_counts(client, session):
    from app.models import Reader
    from sqlalchemy import insert

    await session.execute(insert(Reader), [
        {"full_name": "Ada", "card_number": "R-1", "card_active": True, "book_title": "Algorithms"},
        {"full_name": "Grace", "card_number": "R-2", "card_active": False, "book_title": None},
    ])
    await session.commit()
    readers = (await client.get("/reports/readers")).json()
    assert set(readers[0]) == {
        "id", "full_name", "card_number", "card_active", "book_title", "registered_at"
    }
    assert (await client.get("/reports/summary")).json() == {
        "total_readers": 2, "outstanding_books": 1
    }
