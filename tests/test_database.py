"""Tests for M.A.U.R.Y.A. asynchronous SQLite persistence."""

from pathlib import Path
from collections.abc import AsyncGenerator

import pytest
from sqlalchemy import text
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
    """Verify that the async SQLite engine can execute SQL."""
    await initialize_database(database_engine)

    async with database_engine.connect() as connection:
        result = await connection.execute(text("SELECT 1"))
        assert result.scalar_one() == 1


@pytest.mark.asyncio
async def test_sqlite_wal_configuration(
    database_engine: AsyncEngine,
) -> None:
    """Verify that SQLite is operating with WAL enabled."""
    async with database_engine.connect() as connection:
        journal_mode = await connection.execute(
            text("PRAGMA journal_mode")
        )
        synchronous = await connection.execute(
            text("PRAGMA synchronous")
        )
        foreign_keys = await connection.execute(
            text("PRAGMA foreign_keys")
        )

        assert journal_mode.scalar_one().lower() == "wal"
        assert synchronous.scalar_one() == 1
        assert foreign_keys.scalar_one() == 1


@pytest.mark.asyncio
async def test_session_factory(
    database_engine: AsyncEngine,
) -> None:
    """Verify that the async session factory creates usable sessions."""
    session_factory = create_session_factory(database_engine)

    async with session_factory() as session:
        result = await session.execute(text("SELECT 1"))
        assert result.scalar_one() == 1