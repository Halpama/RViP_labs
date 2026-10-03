from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Reader(Base):
    __tablename__ = "readers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    card_number: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    card_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    book_title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    registered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
