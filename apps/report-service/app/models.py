from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Reader(Base):
    __tablename__ = "readers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(255))
    card_number: Mapped[str] = mapped_column(String(100))
    card_active: Mapped[bool] = mapped_column(Boolean)
    book_title: Mapped[str | None] = mapped_column(String(500))
    registered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
