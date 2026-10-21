"""Target entity for reconnaissance operations."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from app.models.scan import Scan


class Target(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Represent a reconnaissance target.

    A target represents the logical asset being investigated.
    Multiple scan executions may be associated with one target.
    """

    __tablename__ = "targets"

    domain: Mapped[str] = mapped_column(
        String(253),
        nullable=False,
        unique=True,
        index=True,
    )

    scans: Mapped[list[Scan]] = relationship(
        back_populates="target",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
