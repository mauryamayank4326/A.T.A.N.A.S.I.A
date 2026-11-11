"""Tests for standardized API error responses."""

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.testclient import TestClient

from app.exceptions import APIError
from app.handlers import (
    api_error_handler,
    unexpected_error_handler,
    validation_error_handler,
)


def create_test_application() -> FastAPI:
    """Build an isolated app for testing exception contracts."""
    application = FastAPI()

    application.add_exception_handler(APIError, api_error_handler)
    application.add_exception_handler(
        RequestValidationError,
        validation_error_handler,
    )
    application.add_exception_handler(
        Exception,
        unexpected_error_handler,
    )

    @application.get("/expected-error")
    async def expected_error() -> None:
        raise APIError(
            code="RESOURCE_NOT_FOUND",
            message="The requested resource was not found.",
            status_code=404,
        )

    @application.get("/unexpected-error")
    async def unexpected_error() -> None:
        raise RuntimeError("internal database path must not be exposed")

    @application.get("/items/{item_id}")
    async def get_item(item_id: int) -> dict[str, int]:
        return {"item_id": item_id}

    return application


def test_application_error_uses_standard_envelope() -> None:
    """Expected application errors should follow the public contract."""
    client = TestClient(create_test_application())

    response = client.get("/expected-error")

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "RESOURCE_NOT_FOUND",
            "message": "The requested resource was not found.",
            "details": [],
        }
    }


def test_validation_error_does_not_expose_input_value() -> None:
    """Validation responses should not echo untrusted input."""
    client = TestClient(create_test_application())

    response = client.get("/items/not-a-number")

    assert response.status_code == 422
    body = response.json()

    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert body["error"]["message"] == "Request validation failed."
    assert body["error"]["details"]
    assert "not-a-number" not in response.text


def test_unexpected_error_hides_internal_exception() -> None:
    """Unexpected exception details must remain server-side."""
    client = TestClient(
        create_test_application(),
        raise_server_exceptions=False,
    )

    response = client.get("/unexpected-error")

    assert response.status_code == 500
    assert response.json() == {
        "error": {
            "code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred.",
            "details": [],
        }
    }
    assert "internal database path" not in response.text
