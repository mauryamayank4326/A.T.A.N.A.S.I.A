"""Tests for M.A.U.R.Y.A. request tracing and logging."""

from __future__ import annotations

import logging
from uuid import UUID

from fastapi.testclient import TestClient

from app.config import Settings
from app.core.observability import (
    DEFAULT_REQUEST_ID,
    RequestIdLogFilter,
    request_id_context,
)
from app.main import create_application


def make_test_settings(database_path: str) -> Settings:
    """Create isolated settings for an application test."""
    return Settings(
        _env_file=None,
        environment="test",
        log_level="WARNING",
        database_url=f"sqlite+aiosqlite:///{database_path}",
    )


def test_response_contains_generated_request_id(
    tmp_path: object,
) -> None:
    """Requests without an incoming ID receive a valid UUID."""
    database_path = str(tmp_path / "request-id.db")  # type: ignore[operator]
    application = create_application(make_test_settings(database_path))

    with TestClient(application) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "maurya",
    }
    UUID(response.headers["x-request-id"])


def test_valid_incoming_request_id_is_preserved(
    tmp_path: object,
) -> None:
    """A valid UUID supplied by an upstream client is preserved."""
    database_path = str(tmp_path / "valid-id.db")  # type: ignore[operator]
    application = create_application(make_test_settings(database_path))
    request_id = "c3c7f6d8-4e3c-4d3a-9f15-8dcd7c3c0c71"

    with TestClient(application) as client:
        response = client.get(
            "/health",
            headers={"X-Request-ID": request_id},
        )

    assert response.status_code == 200
    assert response.headers["x-request-id"] == request_id


def test_invalid_incoming_request_id_is_replaced(
    tmp_path: object,
) -> None:
    """Malformed IDs are not propagated to response headers."""
    database_path = str(tmp_path / "invalid-id.db")  # type: ignore[operator]
    application = create_application(make_test_settings(database_path))

    with TestClient(application) as client:
        response = client.get(
            "/health",
            headers={"X-Request-ID": "untrusted value\nfor-logs"},
        )

    assert response.status_code == 200
    generated_id = response.headers["x-request-id"]
    UUID(generated_id)
    assert generated_id != "untrusted value\nfor-logs"


def test_request_context_is_reset_after_request(
    tmp_path: object,
) -> None:
    """Request context does not leak into the caller context."""
    database_path = str(tmp_path / "context.db")  # type: ignore[operator]
    application = create_application(make_test_settings(database_path))

    assert request_id_context.get() == DEFAULT_REQUEST_ID

    with TestClient(application) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert request_id_context.get() == DEFAULT_REQUEST_ID


def test_logging_filter_adds_request_id(
) -> None:
    """The logging filter adds the context value to each record."""
    log_filter = RequestIdLogFilter()
    record = logging.LogRecord(
        name="maurya.test",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="test event",
        args=(),
        exc_info=None,
    )

    token = request_id_context.set(
        "c3c7f6d8-4e3c-4d3a-9f15-8dcd7c3c0c71"
    )
    try:
        assert log_filter.filter(record) is True
        assert record.request_id == (
            "c3c7f6d8-4e3c-4d3a-9f15-8dcd7c3c0c71"
        )
    finally:
        request_id_context.reset(token)