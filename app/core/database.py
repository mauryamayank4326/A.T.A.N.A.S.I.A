"""Asynchronous SQLite persistence infrastructure.

This module owns the SQLAlchemy 2.0 asynchronous engine,
session factory, declarative ORM base, and SQLite runtime
configuration used by M.A.U.R.Y.A.

SQLite is configured for:

* Write-Ahead Logging (WAL)
* NORMAL synchronous behavior
* foreign-key enforcement
* bounded busy timeout

No application-specific ORM entities are defined here.
Those belong in ``app.models``.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from pathlib import Path
from typing import Final

from sqlalchemy import event, text
from sqlalchemy.engine import Engine, make_url
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import Settings


SQLITE_BUSY_TIMEOUT_MS: Final[int] = 5_000


class Base(DeclarativeBase):
    """Declarative base for all M.A.U.R.Y.A. ORM entities."""


def _prepare_sqlite_directory(database_url: str) -> None:
    """Create the parent directory for a file-backed SQLite database.

    Args:
        database_url: SQLAlchemy database URL.

    Raises:
        ValueError: If the supplied URL is not a supported SQLite URL.
    """
    url = make_url(database_url)

    if not url.drivername.startswith("sqlite"):
        raise ValueError(
            "M.A.U.R.Y.A. persistence currently supports SQLite URLs only."
        )

    database_path = url.database

    if database_path in (None, "", ":memory:"):
        return

    path = Path(database_path).expanduser()

    if path.parent != Path("."):
        path.parent.mkdir(parents=True, exist_ok=True)


def _configure_sqlite_connection(dbapi_connection: object, _: object) -> None:
    """Configure a newly opened SQLite connection.

    The SQLAlchemy async SQLite dialect exposes the underlying synchronous
    DB-API connection to SQLAlchemy's connection event system.

    Args:
        dbapi_connection: Newly established SQLite DB-API connection.
        _: SQLAlchemy connection record, intentionally unused.
    """
    cursor = dbapi_connection.cursor()

    try:
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute(
            f"PRAGMA busy_timeout={SQLITE_BUSY_TIMEOUT_MS}"
        )
    finally:
        cursor.close()


def create_database_engine(settings: Settings) -> AsyncEngine:
    """Create the configured SQLAlchemy asynchronous engine.

    Args:
        settings: Validated application settings.

    Returns:
        Configured SQLAlchemy asynchronous engine.

    Raises:
        ValueError: If the configured database URL is not SQLite.
    """
    _prepare_sqlite_directory(settings.database_url)

    engine = create_async_engine(
        settings.database_url,
        echo=settings.debug,
        connect_args={
            "timeout": SQLITE_BUSY_TIMEOUT_MS / 1_000,
        },
    )

    if engine.url.drivername.startswith("sqlite"):
        event.listen(
            engine.sync_engine,
            "connect",
            _configure_sqlite_connection,
        )

    return engine


def create_session_factory(
    engine: AsyncEngine,
) -> async_sessionmaker[AsyncSession]:
    """Create the application's asynchronous session factory.

    Sessions do not expire ORM attributes after commit. This prevents
    unnecessary implicit database access when application code reads
    already-loaded values after a successful transaction.

    Args:
        engine: SQLAlchemy asynchronous engine.

    Returns:
        Typed asynchronous session factory.
    """
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )


async def get_db_session(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncGenerator[AsyncSession, None]:
    """Yield an asynchronous database session.

    The caller is responsible for transaction boundaries. The session
    context manager guarantees that the session is released after use.

    Args:
        session_factory: Configured SQLAlchemy async session factory.

    Yields:
        An active asynchronous SQLAlchemy session.
    """
    async with session_factory() as session:
        yield session


async def initialize_database(engine: AsyncEngine) -> None:
    """Verify that the database is reachable.

    ORM table creation is intentionally not performed here because
    application entities are introduced in later milestones.

    Args:
        engine: SQLAlchemy asynchronous engine.

    Raises:
        sqlalchemy.exc.SQLAlchemyError: If SQLite cannot be reached.
    """
    async with engine.connect() as connection:
        await connection.execute(text("SELECT 1"))


async def dispose_database(engine: AsyncEngine) -> None:
    """Dispose all resources owned by the asynchronous database engine.

    Args:
        engine: SQLAlchemy asynchronous engine.
    """
    await engine.dispose()