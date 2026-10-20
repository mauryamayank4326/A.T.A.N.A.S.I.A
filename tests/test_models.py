"""Tests for the M.A.U.R.Y.A. relational model foundation."""

from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Scan, ScanStatus, Target


@pytest.mark.asyncio
async def test_target_can_be_persisted(session: AsyncSession) -> None:
    """Verify that a target can be persisted and retrieved."""

    target = Target(domain="example.com")

    session.add(target)
    await session.commit()

    result = await session.execute(select(Target).where(Target.domain == "example.com"))
    stored_target = result.scalar_one()

    assert stored_target.id is not None
    assert stored_target.domain == "example.com"


@pytest.mark.asyncio
async def test_scan_defaults_to_pending(
    session: AsyncSession,
) -> None:
    """Verify that new scans use the pending lifecycle state."""

    target = Target(domain="example.com")
    session.add(target)
    await session.flush()

    scan = Scan(target_id=target.id)
    session.add(scan)
    await session.commit()

    result = await session.execute(select(Scan).where(Scan.id == scan.id))
    stored_scan = result.scalar_one()

    assert stored_scan.status is ScanStatus.PENDING
    assert stored_scan.target_id == target.id


@pytest.mark.asyncio
async def test_scan_target_relationship(
    session: AsyncSession,
) -> None:
    """Verify that a scan references its owning target."""

    target = Target(domain="example.org")
    session.add(target)
    await session.flush()

    scan = Scan(
        target_id=target.id,
        status=ScanStatus.RUNNING,
    )
    session.add(scan)
    await session.commit()

    result = await session.execute(select(Scan).where(Scan.id == scan.id))
    stored_scan = result.scalar_one()

    assert stored_scan.target_id == target.id
    assert stored_scan.status is ScanStatus.RUNNING


@pytest.mark.asyncio
async def test_scan_accepts_explicit_uuid(
    session: AsyncSession,
) -> None:
    """Verify that scan identity can be explicitly assigned."""

    target = Target(domain="example.net")
    session.add(target)
    await session.flush()

    scan_id = uuid4()
    scan = Scan(
        id=scan_id,
        target_id=target.id,
    )

    session.add(scan)
    await session.commit()

    result = await session.execute(select(Scan).where(Scan.id == scan_id))

    stored_scan = result.scalar_one()

    assert stored_scan.id == scan_id
