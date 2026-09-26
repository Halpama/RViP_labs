"""Application settings loaded from environment variables / .env file."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration for the service.

    All values can be overridden via environment variables (case-insensitive)
    or a local ``.env`` file, e.g.::

        DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/library
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Library Readers API"
    app_description: str = (
        "Асинхронный сервис учёта читателей библиотеки: "
        "CRUD читателей, изъятие читательского билета, выдача/возврат книг "
        "и отчёт по читателям."
    )
    app_version: str = "1.0.0"
    api_prefix: str = "/api/v1"

    # Async SQLAlchemy DSN (asyncpg driver).
    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/library"
    )

    # Synchronous DSN used by Alembic (psycopg2 driver). Derived automatically
    # from database_url unless overridden explicitly.
    alembic_database_url: str | None = None

    echo_sql: bool = False

    def sync_database_url(self) -> str:
        """Return a psycopg2-based DSN for Alembic migrations."""
        if self.alembic_database_url:
            return self.alembic_database_url
        return self.database_url.replace("+asyncpg", "+psycopg2")


@lru_cache
def get_settings() -> Settings:
    """Cached settings factory (FastAPI dependency-friendly)."""
    return Settings()
