"""Centralized logging and request tracing for M.A.U.R.Y.A."""

from __future__ import annotations

import logging
from contextvars import ContextVar
from uuid import UUID, uuid4

from starlette.types import ASGIApp, Message, Receive, Scope, Send

REQUEST_ID_HEADER = b"x-request-id"
DEFAULT_REQUEST_ID = "-"

request_id_context: ContextVar[str] = ContextVar(
    "maurya_request_id",
    default=DEFAULT_REQUEST_ID,
)


class RequestIdLogFilter(logging.Filter):
    """Attach the current request ID to every log record."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Populate the request_id attribute used by log formatters."""
        record.request_id = request_id_context.get()
        return True


def configure_logging(log_level: str) -> None:
    """Configure consistent root logging using a validated log level."""
    level_name = log_level.upper()
    level = getattr(logging, level_name, None)

    if not isinstance(level, int):
        raise ValueError(f"Unsupported logging level: {log_level!r}")

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    if not root_logger.handlers:
        root_logger.addHandler(logging.StreamHandler())

    formatter = logging.Formatter(
        fmt=(
            "%(asctime)s %(levelname)s %(name)s "
            "request_id=%(request_id)s %(message)s"
        ),
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    for handler in root_logger.handlers:
        handler.setFormatter(formatter)

        if not any(
            isinstance(existing_filter, RequestIdLogFilter)
            for existing_filter in handler.filters
        ):
            handler.addFilter(RequestIdLogFilter())


def _resolve_request_id(headers: list[tuple[bytes, bytes]]) -> str:
    """Accept a valid UUID request ID or generate a fresh identifier."""
    supplied_value: bytes | None = next(
        (
            value
            for name, value in headers
            if name.lower() == REQUEST_ID_HEADER
        ),
        None,
    )

    if supplied_value is not None:
        try:
            decoded_value = supplied_value.decode("ascii")
            return str(UUID(decoded_value))
        except (UnicodeDecodeError, ValueError, AttributeError):
            pass

    return str(uuid4())


class RequestIdMiddleware:
    """Provide request-scoped correlation IDs for HTTP requests."""

    def __init__(self, app: ASGIApp) -> None:
        """Initialize the middleware around an ASGI application."""
        self.app = app

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ) -> None:
        """Set request context and attach its ID to the response."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = _resolve_request_id(scope.get("headers", []))
        token = request_id_context.set(request_id)

        scope.setdefault("state", {})["request_id"] = request_id

        async def send_with_request_id(message: Message) -> None:
            """Add the correlation header to the HTTP response."""
            if message["type"] == "http.response.start":
                original_headers = message.get("headers", [])
                filtered_headers = [
                    (name, value)
                    for name, value in original_headers
                    if name.lower() != REQUEST_ID_HEADER
                ]
                filtered_headers.append(
                    (REQUEST_ID_HEADER, request_id.encode("ascii"))
                )
                message = {
                    **message,
                    "headers": filtered_headers,
                }

            await send(message)

        try:
            await self.app(scope, receive, send_with_request_id)
        finally:
            request_id_context.reset(token)