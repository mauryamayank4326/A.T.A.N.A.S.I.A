
"""Tests for M.A.U.R.Y.A. configuration validation."""

import pytest
from pydantic import SecretStr, ValidationError

from app.config import Settings


def test_default_settings_are_valid() -> None:
    """Verify the default configuration is valid."""
    settings = Settings(_env_file=None)

    assert settings.environment == "development"
    assert settings.log_level == "INFO"
    assert settings.api_prefix == "/api/v1"
    assert settings.max_concurrency == 20
    assert settings.database_url == (
        "sqlite+aiosqlite:///./data/osint.db"
    )


def test_environment_and_log_level_are_normalized() -> None:
    """Verify case and surrounding whitespace are normalized."""
    settings = Settings(
        _env_file=None,
        environment="  TEST ",
        log_level=" warning ",
    )

    assert settings.environment == "test"
    assert settings.log_level == "WARNING"


@pytest.mark.parametrize(
    "environment",
    ["", "local", "prod", "invalid"],
)
def test_invalid_environment_is_rejected(
    environment: str,
) -> None:
    """Reject environment names outside the supported set."""
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            environment=environment,
        )


@pytest.mark.parametrize(
    "log_level",
    ["TRACE", "VERBOSE", "INVALID", ""],
)
def test_invalid_log_level_is_rejected(
    log_level: str,
) -> None:
    """Reject unsupported logging levels."""
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            log_level=log_level,
        )


@pytest.mark.parametrize(
    "database_url",
    [
        "postgresql://localhost/example",
        "sqlite:///./data/osint.db",
        "not-a-database-url",
    ],
)
def test_unsupported_database_urls_are_rejected(
    database_url: str,
) -> None:
    """Require a valid URL using the async SQLite driver."""
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            database_url=database_url,
        )


@pytest.mark.parametrize(
    "api_prefix",
    [
        "api/v1",
        "/api",
        "/api/v1/",
        "/api/vx",
    ],
)
def test_invalid_api_prefix_is_rejected(
    api_prefix: str,
) -> None:
    """Reject API prefixes that do not match the versioned format."""
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            api_prefix=api_prefix,
        )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("http_timeout_seconds", 0),
        ("http_timeout_seconds", 301),
        ("max_concurrency", 0),
        ("max_concurrency", 1001),
    ],
)
def test_numeric_boundaries_are_enforced(
    field: str,
    value: int,
) -> None:
    """Reject values outside configured operational boundaries."""
    with pytest.raises(ValidationError):
        Settings(
            _env_file=None,
            **{field: value},
        )


def test_api_key_is_stored_as_secret() -> None:
    """Ensure API credentials use SecretStr."""
    settings = Settings(
        _env_file=None,
        shodan_api_key="example-test-key",
    )

    assert isinstance(settings.shodan_api_key, SecretStr)
    assert settings.shodan_api_key.get_secret_value() == (
        "example-test-key"
    )
    assert "example-test-key" not in str(settings.shodan_api_key)