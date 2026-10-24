"""Discovered email observations associated with reconnaissance scans."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.scan import Scan


class DiscoveredEmail(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Represent an email address discovered during a scan.

    Each observation belongs to one scan. The same address may be
    recorded in separate scans to preserve historical provenance.
    """

    __tablename__ = "discovered_emails"

    __table_args__ = (
        UniqueConstraint(
            "scan_id",
            "email_address",
            name="uq_discovered_emails_scan_email",
        ),
        CheckConstraint(
            "length(trim(email_address)) > 0",
            name="ck_discovered_emails_nonempty_address",
        ),
        CheckConstraint(
            "length(trim(source)) > 0",
            name="ck_discovered_emails_nonempty_source",
        ),
        Index(
            "ix_discovered_emails_scan_id_created_at",
            "scan_id",
            "created_at",
        ),
    )

    scan_id: Mapped[UUID] = mapped_column(
        ForeignKey("scans.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    email_address: Mapped[str] = mapped_column(
        String(320),
        nullable=False,
    )

    source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="unknown",
    )

    scan: Mapped[Scan] = relationship(
        back_populates="discovered_emails",
    )
