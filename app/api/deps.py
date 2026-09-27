"""FastAPI dependency providers for M.A.U.R.Y.A."""

from __future__ import annotations

from collections.abc import AsyncGenerator

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


async def get_db_session(
    request: Request,
) -> AsyncGenerator[AsyncSession, None]:
    """Provide an asynchronous database session to an API request.

    The session factory is created once during application startup
    and stored in FastAPI application state.

    Args:
        request: Current FastAPI request.

    Yields:
        An active asynchronous SQLAlchemy session.

    Raises:
        RuntimeError: If the database session factory has not been
            initialized by the application lifespan.
    """
    session_factory = getattr(
        request.app.state,
        "db_session_factory",
        None,
    )

    if not isinstance(session_factory, async_sessionmaker):
        raise RuntimeError(
            "Database session factory is not initialized."
        )

    async with session_factory() as session:
        yield session