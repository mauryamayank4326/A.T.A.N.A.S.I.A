"""Tests for the FastAPI health endpoint."""

from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


def test_health_endpoint_returns_database_status(tmp_path):
    settings = Settings(
        app_name="M.A.U.R.Y.A. Test",
        environment="test",
        debug=False,
        database_url=(f"sqlite+aiosqlite:///{tmp_path / 'health_test.db'}"),
    )

    app = create_app(settings)

    with TestClient(app) as client:
        response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "database": "connected",
    }


def test_application_has_expected_api_prefix(tmp_path):
    settings = Settings(
        app_name="M.A.U.R.Y.A. Test",
        environment="test",
        debug=False,
        database_url=(f"sqlite+aiosqlite:///{tmp_path / 'prefix_test.db'}"),
    )

    app = create_app(settings)

    assert any(route.path == "/api/v1/health" for route in app.routes)
