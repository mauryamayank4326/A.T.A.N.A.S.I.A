"""Application configuration for M.A.U.R.Y.A.

Configuration is loaded from environment variables and .env files. Secrets are
intentionally excluded from source-controlled configuration.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    """Strongly typed runtime configuration.

    Environment variables use the ``MAURYA_`` prefix. For example,
    ``MAURYA_DEBUG=true`` maps to the ``debug`` field.

    Attributes:
        app_name: Human-readable application name.
        environment: Deployment environment identifier.
        debug: Enables development-oriented debugging behavior.
        log_level: Application logging level.
        api_prefix: Root prefix for versioned REST APIs.
        database_url: SQLAlchemy asynchronous database URL.
        shodan_api_key: Optional Shodan API credential.
        http_timeout_seconds: Default outbound HTTP timeout.
        max_concurrency: Maximum future collector concurrency budget.
    """

    model_config = SettingsConfigDict(
        env_prefix="MAURYA_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = Field(
        default="M.A.U.R.Y.A.",
        min_length=1,
        max_length=100,
    )    

    environment: str = Field(
        default="development",
        min_length=1,
        max_length=32,
    )

    debug: bool = False

    log_level: str = Field(
        default="INFO",
        min_length=1,
        max_length=20,
    )

    api_prefix: str = Field(
        default="/api/v1",
        pattern=r"^/api/v[0-9]+$",
    )

    database_url: str = Field(
        default="sqlite+aiosqlite:///./maurya.db",
        min_length=1,
    )

    shodan_api_key: SecretStr | None = None

    http_timeout_seconds: float = Field(
        default=10.0,
        ge=0.0,
        le=300.0,
    )

    max_concurrency: int = Field(
        default=10,
        ge=1,
        le=1000,
    )

@lru_cache
def get_settings() -> Settings:
    """Return the process-wide immutable-by-convention settings instance.

    returns:
        Validated application settings.

    Raises:
        pydantic.ValidationError: if an environment value violates the
            declared configuration constraints.
    """

    return Settings()