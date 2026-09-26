"""FastAPI application entry point for M.A.U.R.Y.A."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.config import Settings, get_settings
from app.core.database import (
    create_database_engine,
    create_session_factory,
    dispose_database,
    initialize_database,
)


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application startup and shutdown resources.

    Database resources are created during startup and disposed during
    application shutdown.

    Args:
        application: Active FastAPI application instance.

    Yields:
        Control to the running ASGI application.

    Raises:
        Exception: Propagates database initialization failures so that
            the application does not start in a partially initialized state.
    """
    settings: Settings = get_settings()

    engine = create_database_engine(settings)
    session_factory = create_session_factory(engine)

    application.state.settings = settings
    application.state.db_engine = engine
    application.state.db_session_factory = session_factory

    try:
        await initialize_database(engine)
        yield
    finally:
        await dispose_database(engine)


def create_application(settings: Settings | None = None) -> FastAPI:
    """Create and configure the M.A.U.R.Y.A. FastAPI application.

    Args:
        settings: Optional validated settings instance.

    Returns:
        Configured FastAPI application.
    """
    runtime_settings = settings or get_settings()

    application = FastAPI(
        title=runtime_settings.app_name,
        version="0.1.0",
        description=(
            "Modern OSINT & Threat Recon Dashboard for "
            "External Attack Surface Management and threat intelligence."
        ),
        debug=runtime_settings.debug,
        lifespan=lifespan,
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost",
            "http://127.0.0.1",
        ],
        allow_credentials=False,
        allow_methods=[
            "GET",
            "POST",
            "PUT",
            "PATCH",
            "DELETE",
            "OPTIONS",
        ],
        allow_headers=["*"],
    )

    @application.get("/health", tags=["system"])
    async def health() -> dict[str, str]:
        """Return a lightweight process health response."""
        return {
            "status": "ok",
            "service": "maurya",
        }

    return application


app = create_application()