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
    file_storage_service_url: str = Field(
        default="http://file-storage-service:3003",
        validation_alias="FILE_STORAGE_SERVICE_URL",
    )
    rabbitmq_url: str = Field(
        default="amqp://guest:guest@rabbitmq:5672/",
        validation_alias="RABBITMQ_URL",
    )
    app_port: int = Field(default=3002, validation_alias="APP_PORT")
    auth_enabled: bool = Field(default=False, validation_alias="AUTH_ENABLED")
    jwt_secret: str = Field(default="local-development-secret", validation_alias="JWT_SECRET")
    jwt_expire_minutes: int = Field(default=30, validation_alias="JWT_EXPIRE_MINUTES")
    auth_username: str = Field(default="admin", validation_alias="AUTH_USERNAME")
    auth_password: str = Field(default="admin", validation_alias="AUTH_PASSWORD")
    model_config = SettingsConfigDict(env_file=find_env_file(), extra="ignore")

    @field_validator("reader_service_url")
    @classmethod
    def normalize_reader_service_url(cls, value: str) -> str:
        return value.rstrip("/")

    @field_validator("file_storage_service_url")
    @classmethod
    def normalize_file_storage_service_url(cls, value: str) -> str:
        return value.rstrip("/")



@lru_cache
def get_settings() -> Settings:
    return Settings()
