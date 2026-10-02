"""Validated environment-backed settings for M.A.U.R.Y.A."""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


EnvironmentName = Literal[
    "development",
    "test",
    "staging",
    "production",
]

LogLevel = Literal[
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
]


class Settings(BaseSettings):
    """Application configuration validated at initialization."""

    model_config = SettingsConfigDict(
        env_prefix="MAURYA_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        validate_default=True,
    )

    app_name: str = Field(
        default="M.A.U.R.Y.A.",
        min_length=1,
        max_length=120,
    )

    environment: EnvironmentName = "development"

    debug: bool = False

    log_level: LogLevel = "INFO"

    api_prefix: str = Field(
        default="/api/v1",
        pattern=r"^/api/v[0-9]+$",
    )

    database_url: str = (
        "sqlite+aiosqlite:///./data/osint.db"
    )

    shodan_api_key: SecretStr | None = None

    http_timeout_seconds: float = Field(
        default=10.0,
        gt=0,
        le=300,
    )

    max_concurrency: int = Field(
        default=20,
        ge=1,
        le=1000,
    )

    @field_validator("environment", mode="before")
    @classmethod
    def normalize_environment(cls, value: object) -> object:
        """Normalize environment names before validating them."""
        if isinstance(value, str):
            return value.strip().lower()
        return value

    @field_validator("log_level", mode="before")
    @classmethod
    def normalize_log_level(cls, value: object) -> object:
        """Normalize logging levels to uppercase."""
        if isinstance(value, str):
            return value.strip().upper()
        return value

    @field_validator("app_name")
    @classmethod
    def validate_app_name(cls, value: str) -> str:
        """Reject application names containing only whitespace."""
        normalized = value.strip()

        if not normalized:
            raise ValueError("app_name must not be blank")

        return normalized

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        """Require the project's supported async SQLite driver."""
        from sqlalchemy.engine import make_url
        from sqlalchemy.exc import ArgumentError

        try:
            parsed_url = make_url(value)
        except (ArgumentError, ValueError, TypeError) as exc:
            raise ValueError(
                "database_url must be a valid SQLAlchemy URL"
            ) from exc

        if parsed_url.drivername != "sqlite+aiosqlite":
            raise ValueError(
                "database_url must use sqlite+aiosqlite"
            )

        if parsed_url.database == "":
            raise ValueError(
                "database_url must specify a database or :memory:"
            )

        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings for the default application instance."""
    return Settings()