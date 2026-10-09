from functools import lru_cache
from pathlib import Path
from urllib.parse import urlparse

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def find_env_file() -> Path | None:
    for parent in (Path(__file__).resolve(), *Path(__file__).resolve().parents):
        candidate = parent / ".env"
        if candidate.is_file():
            return candidate
    return None


class Settings(BaseSettings):
    database_url: str = Field(validation_alias="DATABASE_URL")
    app_port: int = Field(default=3002, validation_alias="APP_PORT")
    model_config = SettingsConfigDict(env_file=find_env_file(), extra="ignore")

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        parsed = urlparse(value)
        if parsed.scheme not in {"postgresql", "postgresql+asyncpg"} or not parsed.hostname:
            raise ValueError("DATABASE_URL must be a PostgreSQL URL with a hostname")
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
