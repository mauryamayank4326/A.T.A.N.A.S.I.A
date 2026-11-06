"""Pydantic schemas for reconnaissance targets."""

import re
from typing import Annotated
from uuid import UUID

from pydantic import Field, field_validator

from app.schemas.common import ORMReadSchema, RequestSchema

DOMAIN_PATTERN = re.compile(
    r"^(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+"
    r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$",
    re.IGNORECASE,
)


class TargetCreate(RequestSchema):
    """Validate a new reconnaissance target."""

    domain: Annotated[
        str,
        Field(
            min_length=3,
            max_length=253,
            description="DNS domain to investigate.",
            examples=["example.com"],
        ),
    ]

    @field_validator("domain")
    @classmethod
    def validate_domain(cls, value: str) -> str:
        """Normalize and validate a DNS domain."""

        domain = value.lower().rstrip(".")

        if not DOMAIN_PATTERN.fullmatch(domain):
            raise ValueError("A valid DNS domain is required.")

        return domain


class TargetRead(ORMReadSchema):
    """Serialize a persisted reconnaissance target."""

    id: str
    domain: str

    @field_validator("id", mode="before")
    @classmethod
    def serialize_id(cls, value: UUID | str) -> str:
        """Convert the ORM UUID identifier to its API string form."""
        return str(value)
