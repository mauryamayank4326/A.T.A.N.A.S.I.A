"""Application-level exceptions exposed through stable API contracts."""

from __future__ import annotations


class APIError(Exception):
    """An expected application error safe to expose to API clients."""

    def __init__(
        self,
        *,
        code: str,
        message: str,
        status_code: int,
    ) -> None:
        if not code.strip():
            raise ValueError("API error code cannot be blank.")
        if not message.strip():
            raise ValueError("API error message cannot be blank.")
        if not 400 <= status_code <= 599:
            raise ValueError("API error status code must be between 400 and 599.")

        self.code = code
        self.message = message
        self.status_code = status_code
        super().__init__(message)