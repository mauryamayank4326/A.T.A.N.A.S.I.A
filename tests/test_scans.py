"""Tests for scan creation endpoints."""

from uuid import uuid4

from fastapi.testclient import TestClient


def test_create_scan_success(client: TestClient, target) -> None:
    """An existing target should produce a pending scan."""

    response = client.post(
        "/api/v1/scans",
        json={"target_id": str(target.id)},
    )

    assert response.status_code == 201

    body = response.json()

    assert body["target_id"] == str(target.id)
    assert body["status"] == "pending"
    assert body["id"]


def test_create_scan_for_missing_target(client: TestClient) -> None:
    """A nonexistent target should return a standardized 404."""

    response = client.post(
        "/api/v1/scans",
        json={"target_id": str(uuid4())},
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "TARGET_NOT_FOUND"


def test_create_scan_rejects_invalid_uuid(client: TestClient) -> None:
    """Malformed target identifiers should fail validation."""

    response = client.post(
        "/api/v1/scans",
        json={"target_id": "not-a-valid-uuid"},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_create_scan_rejects_extra_fields(
    client: TestClient,
    target,
) -> None:
    """Unexpected request fields must be rejected."""

    response = client.post(
        "/api/v1/scans",
        json={
            "target_id": str(target.id),
            "status": "completed",
        },
    )

    assert response.status_code == 422
