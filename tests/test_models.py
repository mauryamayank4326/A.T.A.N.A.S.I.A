"""Tests for the M.A.U.R.Y.A. relational model foundation."""

from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Scan, ScanStatus, Target


"""Tests for the M.A.U.R.Y.A. relational model foundation."""

from app.models import Base, ExposedPort, Scan, Subdomain


def test_all_reconnaissance_tables_are_registered() -> None:
    """Verify the core reconnaissance tables exist in ORM metadata."""

    assert {
        "targets",
        "scans",
        "subdomains",
        "exposed_ports",
    }.issubset(Base.metadata.tables)


def test_subdomain_references_scan() -> None:
    """Verify subdomain observations have a scan foreign key."""

    table = Subdomain.__table__
    foreign_keys = {
        foreign_key.target_fullname
        for foreign_key in table.foreign_keys
    }

    assert "scans.id" in foreign_keys


def test_subdomain_scan_and_fqdn_are_unique() -> None:
    """Prevent duplicate subdomain observations within one scan."""

    constraints = [
        constraint
        for constraint in Subdomain.__table__.constraints
        if getattr(constraint, "name", None)
        == "uq_subdomains_scan_id_fqdn"
    ]

    assert len(constraints) == 1
    assert tuple(column.name for column in constraints[0].columns) == (
        "scan_id",
        "fqdn",
    )


def test_exposed_port_references_scan() -> None:
    """Verify port observations have a scan foreign key."""

    table = ExposedPort.__table__
    foreign_keys = {
        foreign_key.target_fullname
        for foreign_key in table.foreign_keys
    }

    assert "scans.id" in foreign_keys


def test_exposed_port_has_integrity_constraints() -> None:
    """Verify port range, protocol, and uniqueness constraints."""

    constraints = {
        constraint.name
        for constraint in ExposedPort.__table__.constraints
    }

    assert "ck_exposed_ports_valid_port" in constraints
    assert "ck_exposed_ports_valid_protocol" in constraints
    assert "uq_exposed_ports_scan_host_port_protocol" in constraints


def test_scan_relationships_include_new_entities() -> None:
    """Verify Scan exposes both new observation relationships."""

    relationships = set(Scan.__mapper__.relationships.keys())

    assert "target" in relationships
    assert "subdomains" in relationships
    assert "exposed_ports" in relationships

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
