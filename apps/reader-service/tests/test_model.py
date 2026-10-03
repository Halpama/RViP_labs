from sqlalchemy import inspect

from app.models import Base, Reader


def test_metadata_contains_only_readers_table():
    assert set(Base.metadata.tables) == {"readers"}
    assert inspect(Reader).columns["card_number"].unique is True
    assert inspect(Reader).columns["book_title"].nullable is True
