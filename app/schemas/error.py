"""Consistent API error response schemas."""

from pydantic import BaseModel, ConfigDict, Field


class ErrorDetail(BaseModel):
    """A safe, field-specific explanation of a request error."""

    model_config = ConfigDict(extra="forbid")

    field: str
    message: str


class ErrorBody(BaseModel):
    """The structured error payload."""

    model_config = ConfigDict(extra="forbid")

    code: str
    message: str
    details: list[ErrorDetail] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    """Top-level API error envelope."""

    model_config = ConfigDict(extra="forbid")

    error: ErrorBody