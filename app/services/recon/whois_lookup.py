"""Asynchronous WHOIS-based passive domain intelligence."""

from __future__ import annotations

import asyncio
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import whois

_LABEL_PATTERN = re.compile(
    r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$",
    re.IGNORECASE,
)


class WhoisLookupError(Exception):
    """Raised when a WHOIS lookup cannot be completed."""


class WhoisLookupTimeoutError(WhoisLookupError):
    """Raised when a WHOIS lookup exceeds its configured timeout."""


@dataclass(frozen=True, slots=True)
class WhoisRecord:
    """Normalized WHOIS registration information."""

    domain: str
    registrar: str | None
    creation_date: datetime | None
    expiration_date: datetime | None
    updated_date: datetime | None
    nameservers: tuple[str, ...]
    emails: tuple[str, ...]
    organization: str | None
    country: str | None


def normalize_domain(domain: str) -> str:
    """Normalize and validate an ASCII domain name."""
    normalized = domain.strip().lower().rstrip(".")

    if not normalized or len(normalized) > 253:
        raise ValueError("A valid target domain is required.")

    labels = normalized.split(".")

    if len(labels) < 2:
        raise ValueError("A fully qualified domain name is required.")

    if not all(_LABEL_PATTERN.fullmatch(label) for label in labels):
        raise ValueError("The target domain has an invalid hostname format.")

    return normalized


def _first_value(value: Any) -> Any:
    """Return the first available value from scalar or collection data."""
    if isinstance(value, list | tuple):
        return next((item for item in value if item is not None), None)

    if isinstance(value, set):
        return next(iter(value), None)

    return value


def _as_string(value: Any) -> str | None:
    """Convert a WHOIS scalar into a normalized optional string."""
    value = _first_value(value)

    if value is None:
        return None

    normalized = str(value).strip()

    return normalized or None


def _as_datetime(value: Any) -> datetime | None:
    """Normalize a WHOIS date field."""
    value = _first_value(value)

    if isinstance(value, datetime):
        return value

    return None


def _as_string_tuple(value: Any) -> tuple[str, ...]:
    """Normalize WHOIS collection fields into sorted unique strings."""
    if value is None:
        return ()

    if isinstance(value, str):
        values = [value]
    elif isinstance(value, list | tuple | set):
        values = value
    else:
        values = [value]

    normalized = {
        str(item).strip().lower() for item in values if item is not None and str(item).strip()
    }

    return tuple(sorted(normalized))


def _build_record(domain: str, raw_data: Any) -> WhoisRecord:
    """Convert raw python-whois output into a stable result structure."""
    return WhoisRecord(
        domain=domain,
        registrar=_as_string(raw_data.get("registrar")),
        creation_date=_as_datetime(raw_data.get("creation_date")),
        expiration_date=_as_datetime(raw_data.get("expiration_date")),
        updated_date=_as_datetime(raw_data.get("updated_date")),
        nameservers=_as_string_tuple(raw_data.get("name_servers")),
        emails=_as_string_tuple(raw_data.get("emails")),
        organization=_as_string(raw_data.get("org")),
        country=_as_string(raw_data.get("country")),
    )


async def fetch_whois(
    domain: str,
    timeout_seconds: float = 10.0,
) -> WhoisRecord:
    """Perform a blocking WHOIS lookup outside the asyncio event loop."""
    normalized_domain = normalize_domain(domain)

    if timeout_seconds <= 0:
        raise ValueError("WHOIS timeout must be greater than zero.")

    try:
        raw_data = await asyncio.wait_for(
            asyncio.to_thread(whois.whois, normalized_domain),
            timeout=timeout_seconds,
        )
    except TimeoutError as exc:
        raise WhoisLookupTimeoutError(f"WHOIS lookup timed out for {normalized_domain}.") from exc
    except Exception as exc:
        raise WhoisLookupError(f"WHOIS lookup failed for {normalized_domain}.") from exc

    if raw_data is None:
        raise WhoisLookupError("WHOIS returned no response.")

    if not hasattr(raw_data, "get"):
        raise WhoisLookupError("WHOIS returned an unexpected response format.")

    return _build_record(normalized_domain, raw_data)
