"""FastAPI dependencies for database access."""

from collections.abc import AsyncGenerator

from fastapi import HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession


async def get_db_session(
    request: Request,
) -> AsyncGenerator[AsyncSession, None]:
    """Provide an application-managed async database session."""

    session_factory = getattr(
        request.app.state,
        "db_session_factory",
        None,
    )

    if session_factory is None:
        raise HTTPException(
            status_code=503,
            detail="Database service is unavailable.",
        )

    async with session_factory() as session:
        yield session
