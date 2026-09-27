"""Tests for the M.A.U.R.Y.A. FastAPI application."""

from pathlib import Path

from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_application


def test_health_endpoint(tmp_path: Path) -> None:
    """Verify the health endpoint and application lifecycle."""
    database_path = tmp_path / "health.db"

    settings = Settings(
        app_name="M.A.U.R.Y.A. Test",
        environment="test",
        debug=False,
        database_url=f"sqlite+aiosqlite:///{database_path}",
    )

    application = create_application(settings)

    with TestClient(application) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "maurya",
    }

    assert database_path.exists()


def test_application_uses_supplied_settings(tmp_path: Path) -> None:
    """Verify that application lifespan uses injected settings."""
    database_path = tmp_path / "custom.db"

    settings = Settings(
        app_name="M.A.U.R.Y.A. Custom Test",
        environment="test",
        debug=False,
        database_url=f"sqlite+aiosqlite:///{database_path}",
    )

    application = create_application(settings)

    with TestClient(application):
        assert application.state.settings is settings
        assert application.state.db_engine.url.database == str(
            database_path
        )