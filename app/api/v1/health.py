"""Health endpoints for API version 1."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db_session

router = APIRouter(tags=["health"])


@router.get("/health", summary="Check application and database health")
async def health_check(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, str]:
    """Report application and database availability."""

    try:
        await session.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=503,
            detail="Database service is unavailable.",
        ) from exc

    return {
        "status": "ok",
        "service": "maurya",
        "database": "connected",
    }
