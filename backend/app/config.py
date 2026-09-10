"""Environment-backed application settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings loaded from environment variables or a local .env file."""

    app_name: str = "Hardware Distributed URL Shortener"
    environment: str = "development"
    log_level: str = "INFO"
    api_prefix: str = "/api/v1"
    allowed_origins: str = "http://localhost:5173"
    public_base_url: str = "http://localhost:8000"
    database_url: str = (
        "postgresql+asyncpg://url_shortener:url_shortener@localhost:5432/"
        "url_shortener"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return a cached settings instance for dependency injection."""

    return Settings()