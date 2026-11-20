from functools import lru_cache
from pathlib import Path
from urllib.parse import urlparse

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def find_env_file() -> Path | None:
    for parent in Path(__file__).resolve().parents:
        env_file = parent / ".env"
        if env_file.is_file():
            return env_file
    return None


class Settings(BaseSettings):
    database_url: str = Field(validation_alias="DATABASE_URL")
    app_port: int = Field(default=3001, validation_alias="APP_PORT")
    auth_enabled: bool = Field(default=False, validation_alias="AUTH_ENABLED")
    jwt_secret: str = Field(default="local-development-secret", validation_alias="JWT_SECRET")
    jwt_expire_minutes: int = Field(default=30, validation_alias="JWT_EXPIRE_MINUTES")
    auth_username: str = Field(default="admin", validation_alias="AUTH_USERNAME")
    auth_password: str = Field(default="admin", validation_alias="AUTH_PASSWORD")

    model_config = SettingsConfigDict(
        env_file=find_env_file(),
        extra="ignore",
    )

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        parsed = urlparse(value)
        if parsed.scheme not in {"postgresql", "postgresql+asyncpg"} or not parsed.hostname:
            raise ValueError(
                "DATABASE_URL must be a PostgreSQL URL with a hostname "
                "(for example postgresql+asyncpg://user:password@host:5432/db)"
            )
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
