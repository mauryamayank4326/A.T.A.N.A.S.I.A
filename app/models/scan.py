"""Scan entity and scan lifecycle definitions."""

from __future__ import annotations

from datetime import datetime
from enum import Enum as PyEnum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.exposed_port import ExposedPort
    from app.models.subdomain import Subdomain
    from app.models.target import Target

class ScanStatus(str, PyEnum):
    """Represent the lifecycle state of a reconnaissance scan."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Scan(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Represent one reconnaissance execution against a target."""

    __tablename__ = "scans"

    target_id: Mapped[UUID] = mapped_column(
        ForeignKey("targets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    status: Mapped[ScanStatus] = mapped_column(
        Enum(
            ScanStatus,
            name="scan_status",
            native_enum=False,
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
        default=ScanStatus.PENDING,
        index=True,
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    target: Mapped[Target] = relationship(
        back_populates="scans",
    )

    subdomains: Mapped[list["Subdomain"]] = relationship(
        back_populates="scan",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    exposed_ports: Mapped[list["ExposedPort"]] = relationship(
        back_populates="scan",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )