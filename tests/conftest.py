from collections.abc import AsyncGenerator
from pathlib import Path

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings
from app.core.database import create_database_engine, create_session_factory
from app.models import Base


@pytest.fixture
async def session(tmp_path: Path) -> AsyncGenerator[AsyncSession, None]:
    database_path = tmp_path / "models.db"
    settings = Settings(
        environment="test",
        debug=False,
        database_url=f"sqlite+aiosqlite:///{database_path}",
    )
    engine = create_database_engine(settings)

    try:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

        session_factory = create_session_factory(engine)

        async with session_factory() as database_session:
            yield database_session
    finally:
        await engine.dispose()
