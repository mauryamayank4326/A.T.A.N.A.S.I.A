"""Tests for the Day 01 FastAPI application foundation."""

from fastapi.testclient import TestClient
from app.config import Settings
from app.main import create_application


def test_health_endpoint() -> None:
    """Verify the application starts and exposes its health endpoint."""
    settings = Settings(
        app_name="M.A.U.R.Y.A. Test",
        environment="test",
        debug=False,
        database_url="sqlite+aiosqlite:///:memory:",
    )

    application = create_application(settings)

    with TestClient(application) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "maurya",
    }


def test_settings_validation() -> None:
    """Verify configuration values are parsed into their declared types."""
    settings = Settings(
        environment="test",
        debug=True,
        http_timeout_seconds="15",
        max_concurrency="50",
    )

    assert settings.environment == "test"
    assert settings.debug is True
    assert settings.http_timeout_seconds == 15.0
    assert settings.max_concurrency == 50