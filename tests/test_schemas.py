"""Tests for M.A.U.R.Y.A. Pydantic API schemas."""

from types import SimpleNamespace
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.models.scan import ScanStatus
from app.schemas import ScanCreate, ScanRead, TargetCreate, TargetRead


def test_target_create_normalizes_domain() -> None:
    """Verify domain normalization."""
    target = TargetCreate(domain=" Example.COM. ")

    assert target.domain == "example.com"


@pytest.mark.parametrize(
    "domain",
    [
        "",
        "example",
        "https://example.com",
        "example.com/path",
        "invalid_domain.com",
        "-invalid.com",
    ],
)
def test_target_create_rejects_invalid_domains(domain: str) -> None:
    """Reject malformed domain values."""
    with pytest.raises(ValidationError):
        TargetCreate(domain=domain)


def test_target_create_rejects_extra_fields() -> None:
    """Reject unexpected request attributes."""
    with pytest.raises(ValidationError):
        TargetCreate(
            domain="example.com",
            unexpected="value",
        )


def test_target_read_serializes_attributes() -> None:
    """Verify ORM-style attribute serialization."""
    target_id = uuid4()

    target = SimpleNamespace(
        id=target_id,
        domain="example.com",
    )

    result = TargetRead.model_validate(target)

    assert result.id == str(target_id)
    assert result.domain == "example.com"


def test_scan_create_validates_target_uuid() -> None:
    """Verify scan target identifier validation."""
    target_id = uuid4()

    scan = ScanCreate(target_id=target_id)

    assert scan.target_id == target_id


def test_scan_create_rejects_invalid_uuid() -> None:
    """Reject malformed target identifiers."""
    with pytest.raises(ValidationError):
        ScanCreate(target_id="not-a-uuid")


def test_scan_read_serializes_attributes() -> None:
    """Verify scan response serialization."""
    scan_id = uuid4()
    target_id = uuid4()

    scan = SimpleNamespace(
        id=scan_id,
        target_id=target_id,
        status=ScanStatus.PENDING,
        started_at=None,
        completed_at=None,
    )

    result = ScanRead.model_validate(scan)

    assert result.id == scan_id
    assert result.target_id == target_id
    assert result.status == ScanStatus.PENDING
    assert result.started_at is None
    assert result.completed_at is None
