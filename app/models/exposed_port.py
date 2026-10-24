"""Exposed-port observations associated with reconnaissance scans."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.scan import Scan


class ExposedPort(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Represent a network port observation from a reconnaissance scan.

    The model stores the host and protocol observed alongside the port
    number. It does not perform network probing itself.
    """

    __tablename__ = "exposed_ports"

    __table_args__ = (
        UniqueConstraint(
            "scan_id",
            "host",
            "port",
            "protocol",
            name="uq_exposed_ports_scan_host_port_protocol",
        ),
        CheckConstraint(
            "port >= 1 AND port <= 65535",
            name="ck_exposed_ports_valid_port",
        ),
        CheckConstraint(
            "protocol IN ('tcp', 'udp')",
            name="ck_exposed_ports_valid_protocol",
        ),
        Index(
            "ix_exposed_ports_scan_id_created_at",
            "scan_id",
            "created_at",
        ),
    )

    scan_id: Mapped[UUID] = mapped_column(
        ForeignKey("scans.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    host: Mapped[str] = mapped_column(
        String(253),
        nullable=False,
    )

    port: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    protocol: Mapped[str] = mapped_column(
        String(8),
        nullable=False,
        default="tcp",
    )

    service_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    scan: Mapped[Scan] = relationship(
        back_populates="exposed_ports",
    )
