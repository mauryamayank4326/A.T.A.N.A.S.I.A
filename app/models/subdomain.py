"""Subdomain observations associated with reconnaissance scans."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.scan import Scan


class Subdomain(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Represent a subdomain discovered during a scan.

    A subdomain observation belongs to one scan. The same fully
    qualified domain name may appear in different scan executions.
    """

    __tablename__ = "subdomains"

    __table_args__ = (
        UniqueConstraint(
            "scan_id",
            "fqdn",
            name="uq_subdomains_scan_id_fqdn",
        ),
        Index(
            "ix_subdomains_scan_id_created_at",
            "scan_id",
            "created_at",
        ),
    )

    scan_id: Mapped[UUID] = mapped_column(
        ForeignKey("scans.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    fqdn: Mapped[str] = mapped_column(
        String(253),
        nullable=False,
    )

    source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="unknown",
    )

    scan: Mapped[Scan] = relationship(
        back_populates="subdomains",
    )
