from datetime import datetime

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.models import Reader


@pytest.mark.asyncio
async def test_migrated_reader_defaults_and_unique_card(session):
    first = Reader(full_name="Grace Hopper", card_number="CARD-DB")
    session.add(first)
    await session.commit()
    await session.refresh(first)
    first_id = first.id

    assert first.card_active is True
    assert first.book_title is None
    assert isinstance(first.registered_at, datetime)

    session.add(Reader(full_name="Another Reader", card_number="CARD-DB"))
    with pytest.raises(IntegrityError):
        await session.commit()
    await session.rollback()
    assert (await session.scalar(select(Reader).where(Reader.id == first_id))).full_name == "Grace Hopper"
