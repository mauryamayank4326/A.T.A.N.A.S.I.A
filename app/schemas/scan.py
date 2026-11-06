"""Pydantic schemas for reconnaissance scans."""

from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.models.scan import ScanStatus
from app.schemas.common import ORMReadSchema, RequestSchema


class ScanCreate(RequestSchema):
    """Validate a request to create a scan."""

    target_id: UUID = Field(
        description="UUID of the target associated with the scan.",
    )


class ScanRead(ORMReadSchema):
    """Serialize a persisted reconnaissance scan."""

    id: UUID
    target_id: UUID
    status: ScanStatus
    started_at: datetime | None = None
    completed_at: datetime | None = None
