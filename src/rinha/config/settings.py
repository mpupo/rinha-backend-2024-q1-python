import pytz
from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class PostgresSettings(BaseSettings):
    DB_NAME: str = "rinha"
    DB_USER: str = "rinha"
    DB_PASSWORD: str = "rinha"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30

    @computed_field
    @property
    def db_url(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__", env_prefix="rinha_")

    PROJECT_NAME: str = "rinha-backend-2024-q1-mpupo"
    ECHO_SQL: bool = True
    DB: PostgresSettings = PostgresSettings()
    DEBUG: bool = True
    PROFILING: bool = False
    TIMEZONE: str = "America/Sao_Paulo"


settings = Settings()

UTC_TIMEZONE = pytz.timezone("UTC")
TIMEZONE = pytz.timezone(settings.TIMEZONE)
