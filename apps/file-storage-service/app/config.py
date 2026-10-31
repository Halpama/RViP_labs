from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    rabbitmq_url: str = Field(
        default="amqp://guest:guest@rabbitmq:5672/",
        validation_alias="RABBITMQ_URL",
    )
    app_port: int = Field(default=3003, validation_alias="APP_PORT")
    model_config = SettingsConfigDict(extra="ignore")
