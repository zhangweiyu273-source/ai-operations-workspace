from functools import lru_cache
from uuid import UUID

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    app_env: str = "development"
    app_name: str = "AI运营工作台"
    app_version: str = "1.0.0"
    log_level: str = "INFO"
    database_url: str = "postgresql+psycopg://ai_ops@localhost:5432/ai_ops"
    cors_origins: str = "http://localhost:3000"
    upload_dir: str = "storage/uploads"
    max_upload_size_mb: int = Field(default=20, ge=1, le=100)
    default_organization_id: UUID = UUID("00000000-0000-4000-8000-000000000001")
    ai_provider: str = "deepseek"
    deepseek_api_key: str | None = None
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"
    ai_timeout: float = Field(default=30, ge=1, le=120)
    ai_max_retries: int = Field(default=2, ge=0, le=5)

    @field_validator("database_url")
    @classmethod
    def normalize_postgres_url(cls, value: str) -> str:
        """Accept managed PostgreSQL URLs while consistently using psycopg."""
        if value.startswith("postgres://"):
            return "postgresql+psycopg://" + value.removeprefix("postgres://")
        if value.startswith("postgresql://"):
            return "postgresql+psycopg://" + value.removeprefix("postgresql://")
        return value

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
