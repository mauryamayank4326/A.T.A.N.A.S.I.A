"""Shared Pydantic schema configuration."""

from pydantic import BaseModel, ConfigDict


class RequestSchema(BaseModel):
    """Base class for API request schemas."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )


class ORMReadSchema(BaseModel):
    """Base class for schemas serialized from ORM objects."""

    model_config = ConfigDict(
        from_attributes=True,
    )
