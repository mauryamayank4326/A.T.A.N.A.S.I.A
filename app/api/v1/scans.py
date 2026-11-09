"""Scan management endpoints for API version 1."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db_session
from app.exceptions import APIError
from app.models.scan import Scan, ScanStatus
from app.models.target import Target
from app.schemas.scan import ScanCreate, ScanRead

router = APIRouter(prefix="/scans", tags=["scans"])


@router.post(
    "",
    response_model=ScanRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a reconnaissance scan",
)
async def create_scan(
    payload: ScanCreate,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> Scan:
    """Create a pending scan for an existing target."""

    target_result = await session.execute(
        select(Target).where(Target.id == payload.target_id)
    )
    target = target_result.scalar_one_or_none()

    if target is None:
        raise APIError(
            code="TARGET_NOT_FOUND",
            message="The requested target was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    scan = Scan(
        target_id=target.id,
        status=ScanStatus.PENDING,
    )

    try:
        session.add(scan)
        await session.commit()
        await session.refresh(scan)

    except IntegrityError as exc:
        await session.rollback()
        raise APIError(
            code="SCAN_CREATION_CONFLICT",
            message="The scan could not be created because of a data conflict.",
            status_code=status.HTTP_409_CONFLICT,
        ) from exc

    except SQLAlchemyError as exc:
        await session.rollback()
        raise APIError(
            code="SCAN_CREATION_FAILED",
            message="The scan could not be created.",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        ) from exc

    return scan