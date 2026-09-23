"""FastAPI application entry point for M.A.U.R.Y.A."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import Settings, get_settings


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncGenerator[None, None]:
    """Manage application startup and shutdown lifecycle.

    The lifecycle hook intentionally contains no database initialization yet.
    Database engine construction belongs to the persistence milestone.

    Args:
        application: Active FastAPI application instance.

    Yields:
        Control to the running ASGI application.
    """
    application.state.settings = get_settings()
    yield


def create_application(settings: Settings | None = None) -> FastAPI:
    """Create and configure a M.A.U.R.Y.A. FastAPI application.

    Using an application factory keeps the runtime independently testable
    and allows tests to construct isolated application instances.

    Args:
        settings: Optional validated settings instance. When omitted,
            process configuration is loaded through ``get_settings()``.

    Returns:
        Fully configured FastAPI application.
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
        allow_origins=["http://localhost", "http://127.0.0.1"],
        allow_credentials=False,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
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