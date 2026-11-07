"""Application entry point for M.A.U.R.Y.A."""

from __future__ import annotations

from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1.router import api_router
from app.config import Settings, get_settings
from app.core.database import (
    create_database_engine,
    create_session_factory,
    dispose_database,
    initialize_database,
)
from app.core.observability import (
    RequestIdMiddleware,
    configure_logging,
)
from app.exceptions import APIError
from app.handlers import (
    api_error_handler,
    http_error_handler,
    unexpected_error_handler,
    validation_error_handler,
)


def create_lifespan(
    settings: Settings,
) -> Callable[[FastAPI], AsyncGenerator[None, None]]:
    """Build a lifespan handler using the supplied settings."""

    @asynccontextmanager
    async def lifespan(application: FastAPI) -> AsyncGenerator[None, None]:
        """Initialize and release application database resources."""
        engine = create_database_engine(settings)

        try:
            await initialize_database(engine)

            session_factory = create_session_factory(engine)

            application.state.settings = settings
            application.state.db_engine = engine
            application.state.db_session_factory = session_factory

            yield
        finally:
            await dispose_database(engine)

    return lifespan


def create_application(
    settings: Settings | None = None,
) -> FastAPI:
    """Construct the FastAPI application with validated settings."""
    runtime_settings = settings or get_settings()

    configure_logging(runtime_settings.log_level)

    application = FastAPI(
        title=runtime_settings.app_name,
        debug=runtime_settings.debug,
        lifespan=create_lifespan(runtime_settings),
    )

    application.add_exception_handler(APIError, api_error_handler)
    application.add_exception_handler(
        RequestValidationError,
        validation_error_handler,
    )
    application.add_exception_handler(
        StarletteHTTPException,
        http_error_handler,
    )
    application.add_exception_handler(
        Exception,
        unexpected_error_handler,
    )

    application.add_middleware(RequestIdMiddleware)

    application.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ],
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", "X-Request-ID"],
        expose_headers=["X-Request-ID"],
    )

    application.include_router(
        api_router,
        prefix=runtime_settings.api_prefix,
    )

    if runtime_settings.api_prefix == "/api/v1":
        application.include_router(api_router)

    return application


create_app = create_application
app = create_application()
