"""Tests for the M.A.U.R.Y.A. relational model foundation."""

from uuid import uuid4

import pytest
from sqlalchemy import CheckConstraint, Uuid, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Base,
    DiscoveredEmail,
    ExposedPort,
    Scan,
    ScanStatus,
    Subdomain,
    Target,
)


def test_all_reconnaissance_tables_are_registered() -> None:
    """Verify the core reconnaissance tables exist in ORM metadata."""

    assert {
        "targets",
        "scans",
        "subdomains",
        "exposed_ports",
        "discovered_emails",
    }.issubset(Base.metadata.tables)


def test_subdomain_references_scan() -> None:
    """Verify subdomain observations have a scan foreign key."""

    table = Subdomain.__table__
    foreign_keys = {foreign_key.target_fullname for foreign_key in table.foreign_keys}

    assert "scans.id" in foreign_keys


def test_subdomain_scan_and_fqdn_are_unique() -> None:
    """Prevent duplicate subdomain observations within one scan."""

    constraints = [
        constraint
        for constraint in Subdomain.__table__.constraints
        if getattr(constraint, "name", None) == "uq_subdomains_scan_id_fqdn"
    ]

    assert len(constraints) == 1
    assert tuple(column.name for column in constraints[0].columns) == (
        "scan_id",
        "fqdn",
    )


def test_exposed_port_references_scan() -> None:
    """Verify port observations have a scan foreign key."""

    table = ExposedPort.__table__
    foreign_keys = {foreign_key.target_fullname for foreign_key in table.foreign_keys}

    assert "scans.id" in foreign_keys


def test_exposed_port_has_integrity_constraints() -> None:
    """Verify port range, protocol, and uniqueness constraints."""

    constraints = {constraint.name for constraint in ExposedPort.__table__.constraints}

    assert "ck_exposed_ports_valid_port" in constraints
    assert "ck_exposed_ports_valid_protocol" in constraints
    assert "uq_exposed_ports_scan_host_port_protocol" in constraints


def test_scan_relationships_include_new_entities() -> None:
    """Verify Scan exposes both new observation relationships."""

    relationships = set(Scan.__mapper__.relationships.keys())

    assert "target" in relationships
    assert "subdomains" in relationships
    assert "exposed_ports" in relationships


def test_discovered_email_references_scan() -> None:
    """Verify the email observation has a scan foreign key."""

    foreign_keys = {
        foreign_key.target_fullname for foreign_key in DiscoveredEmail.__table__.foreign_keys
    }

    assert "scans.id" in foreign_keys


def test_discovered_email_has_uuid_primary_key() -> None:
    """Verify discovered emails use a UUID primary key."""

    id_column = DiscoveredEmail.__table__.c.id

    assert isinstance(id_column.type, Uuid)
    assert id_column.primary_key


def test_discovered_email_required_columns_are_non_nullable() -> None:
    """Verify email address and source are required fields."""

    table = DiscoveredEmail.__table__

    assert table.c.email_address.nullable is False
    assert table.c.source.nullable is False


def test_discovered_email_constraints_are_registered() -> None:
    """Verify email uniqueness and non-empty-value constraints."""

    constraints = {constraint.name for constraint in DiscoveredEmail.__table__.constraints}

    assert "uq_discovered_emails_scan_email" in constraints
    assert "ck_discovered_emails_nonempty_address" in constraints
    assert "ck_discovered_emails_nonempty_source" in constraints

    checks = {
        constraint.name: str(constraint.sqltext)
        for constraint in DiscoveredEmail.__table__.constraints
        if isinstance(constraint, CheckConstraint)
    }

    assert checks["ck_discovered_emails_nonempty_address"] == ("length(trim(email_address)) > 0")
    assert checks["ck_discovered_emails_nonempty_source"] == "length(trim(source)) > 0"


def test_discovered_email_uniqueness_columns() -> None:
    """Verify uniqueness is scoped to a scan and email address."""

    constraint = next(
        constraint
        for constraint in DiscoveredEmail.__table__.constraints
        if constraint.name == "uq_discovered_emails_scan_email"
    )

    assert tuple(column.name for column in constraint.columns) == (
        "scan_id",
        "email_address",
    )


def test_discovered_email_relationship_is_bidirectional() -> None:
    """Verify Scan and DiscoveredEmail point back to each other."""

    email_to_scan = DiscoveredEmail.__mapper__.relationships["scan"]
    scan_to_emails = Scan.__mapper__.relationships["discovered_emails"]

    assert email_to_scan.back_populates == "discovered_emails"
    assert scan_to_emails.back_populates == "scan"


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
