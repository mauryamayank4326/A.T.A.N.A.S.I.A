"""Tests for M.A.U.R.Y.A. asynchronous SQLite persistence."""

from collections.abc import AsyncGenerator
from pathlib import Path

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncEngine

from app.config import Settings
from app.core.database import (
    create_database_engine,
    create_session_factory,
    initialize_database,
)


@pytest.fixture
def database_settings(tmp_path: Path) -> Settings:
    """Create isolated test database settings."""
    database_path = tmp_path / "test.db"

    return Settings(
        app_name="M.A.U.R.Y.A. Test",
        environment="test",
        debug=False,
        database_url=f"sqlite+aiosqlite:///{database_path}",
    )


@pytest.fixture
async def database_engine(
    database_settings: Settings,
) -> AsyncGenerator[AsyncEngine, None]:
    """Create and dispose an isolated test database engine."""
    engine = create_database_engine(database_settings)

    yield engine

    await engine.dispose()


@pytest.mark.asyncio
async def test_database_connectivity(
    database_engine: AsyncEngine,
) -> None:
    """Verify initialization creates all registered model tables."""
    await initialize_database(database_engine)

    async with database_engine.connect() as connection:
        tables = await connection.execute(
            text("SELECT name FROM sqlite_master WHERE type = 'table'")
        )
        result = await connection.execute(text("SELECT 1"))

        assert {
            "targets",
            "scans",
            "subdomains",
            "exposed_ports",
            "discovered_emails",
        }.issubset(set(tables.scalars()))
        assert result.scalar_one() == 1


@pytest.mark.asyncio
async def test_initialized_database_has_history_indexes(
    database_engine: AsyncEngine,
) -> None:
    """Verify history indexes exist in SQLite with their expected columns."""
    await initialize_database(database_engine)

    expected_indexes = {
        "scans": ("ix_scans_target_id_created_at", ("target_id", "created_at")),
        "subdomains": ("ix_subdomains_scan_id_created_at", ("scan_id", "created_at")),
        "exposed_ports": (
            "ix_exposed_ports_scan_id_created_at",
            ("scan_id", "created_at"),
        ),
        "discovered_emails": (
            "ix_discovered_emails_scan_id_created_at",
            ("scan_id", "created_at"),
        ),
    }

    async with database_engine.connect() as connection:
        for table, (expected_index, expected_columns) in expected_indexes.items():
            indexes = await connection.exec_driver_sql(f"PRAGMA index_list('{table}')")
            assert expected_index in {row[1] for row in indexes}

            index_columns = await connection.exec_driver_sql(
                f"PRAGMA index_info('{expected_index}')"
            )
            assert tuple(row[2] for row in index_columns) == expected_columns


@pytest.mark.asyncio
async def test_sqlite_wal_configuration(
    database_engine: AsyncEngine,
) -> None:
    """Verify that SQLite runtime configuration is correct."""
    async with database_engine.connect() as connection:
        journal_mode = await connection.execute(text("PRAGMA journal_mode"))
        synchronous = await connection.execute(text("PRAGMA synchronous"))
        foreign_keys = await connection.execute(text("PRAGMA foreign_keys"))

        assert journal_mode.scalar_one().lower() == "wal"
        assert synchronous.scalar_one() == 1
        assert foreign_keys.scalar_one() == 1


@pytest.mark.asyncio
async def test_sqlite_foreign_keys_are_enforced(
    database_engine: AsyncEngine,
) -> None:
    """Verify an observation cannot reference a nonexistent scan."""
    await initialize_database(database_engine)

    with pytest.raises(IntegrityError):
        async with database_engine.begin() as connection:
            await connection.execute(
                text(
                    """
                    INSERT INTO exposed_ports (
                        id, scan_id, host, port, protocol, created_at, updated_at
                    ) VALUES (
                        '00000000-0000-0000-0000-000000000001',
                        '00000000-0000-0000-0000-000000000002',
                        'example.com',
                        443,
                        'tcp',
                        '2026-01-01T00:00:00',
                        '2026-01-01T00:00:00'
                    )
                    """
                )
            )


@pytest.mark.asyncio
async def test_session_factory(
    database_engine: AsyncEngine,
) -> None:
    """Verify that the async session factory creates usable sessions."""
    session_factory = create_session_factory(database_engine)

    async with session_factory() as session:
        result = await session.execute(text("SELECT 1"))

        assert result.scalar_one() == 1
