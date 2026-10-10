from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def find_env_file() -> Path | None:
    for parent in (Path(__file__).resolve(), *Path(__file__).resolve().parents):
        candidate = parent / ".env"
        if candidate.is_file():
            return candidate
    return None


class Settings(BaseSettings):
    reader_service_url: str = Field(
        default="http://reader-service:3001",
        validation_alias="READER_SERVICE_URL",
    )
    app_port: int = Field(default=3002, validation_alias="APP_PORT")
    model_config = SettingsConfigDict(env_file=find_env_file(), extra="ignore")

    @field_validator("reader_service_url")
    @classmethod
    def normalize_reader_service_url(cls, value: str) -> str:
        return value.rstrip("/")


@lru_cache
def get_settings() -> Settings:
    return Settings()
