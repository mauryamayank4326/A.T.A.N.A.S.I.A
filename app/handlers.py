"""Centralized exception handlers for the FastAPI application."""

from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.exceptions import APIError

logger = logging.getLogger(__name__)


def _validation_field(location: tuple[Any, ...]) -> str:
    """Convert a validation location into a safe dotted field path."""
    parts = [str(part) for part in location if part not in {"body", "query", "path"}]
    return ".".join(parts) if parts else "request"


async def api_error_handler(
    request: Request,
    exc: APIError,
) -> JSONResponse:
    """Return a deliberately safe application error response."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": [],
            }
        },
    )


async def validation_error_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Normalize request validation errors without exposing raw input."""
    details = [
        {
            "field": _validation_field(tuple(error.get("loc", ()))),
            "message": "Invalid or missing value.",
        }
        for error in exc.errors()
    ]

    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed.",
                "details": details,
            }
        },
    )


async def http_error_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    """Normalize HTTP errors while preserving status and safe headers."""
    safe_messages: Mapping[int, tuple[str, str]] = {
        400: ("BAD_REQUEST", "The request could not be processed."),
        401: ("UNAUTHORIZED", "Authentication is required."),
        403: ("FORBIDDEN", "You are not permitted to perform this action."),
        404: ("NOT_FOUND", "The requested resource was not found."),
        405: ("METHOD_NOT_ALLOWED", "The requested method is not allowed."),
        409: ("CONFLICT", "The request conflicts with the current resource state."),
        429: ("RATE_LIMITED", "Too many requests."),
    }

    code, message = safe_messages.get(
        exc.status_code,
        ("HTTP_ERROR", "The request could not be completed."),
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": [],
            }
        },
        headers=exc.headers,
    )


async def unexpected_error_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Log unexpected failures and return a generic response."""
    logger.exception(
        "Unhandled application exception",
        extra={"path": request.url.path},
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred.",
                "details": [],
            }
        },
    )