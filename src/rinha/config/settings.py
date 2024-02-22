from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class PostgresSettings(BaseSettings):
    DB_NAME: str = "test"
    DB_USER: str = "test"
    DB_PASSWORD: str = "test"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432

    @computed_field
    @property
    def db_url(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__")

    project_name: str = "rinha-backend-2024-q1-mpupo"
    echo_sql: bool | str = "debug"
    db: PostgresSettings = PostgresSettings()
    debug_logs: bool = True


settings = Settings()
