"""Passive subdomain discovery through Certificate Transparency."""

from __future__ import annotations

import logging
import re
from typing import Any

import httpx

logger = logging.getLogger(__name__)

CRTSH_URL = "https://crt.sh/"

# DNS hostname validation: labels are 1–63 characters.
_LABEL_PATTERN = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$")


class CRTShError(Exception):
    """Raised when Certificate Transparency retrieval fails."""


def _is_valid_hostname(hostname: str) -> bool:
    """Validate a normalized DNS hostname."""
    if not hostname or len(hostname) > 253:
        return False

    labels = hostname.split(".")

    if len(labels) < 2:
        return False

    return all(_LABEL_PATTERN.fullmatch(label) for label in labels)


def _normalize_hostname(value: str) -> str:
    """Normalize a certificate hostname entry."""
    hostname = value.strip().lower().rstrip(".")

    if hostname.startswith("*."):
        hostname = hostname[2:]

    return hostname


def _is_in_scope(hostname: str, domain: str) -> bool:
    """Ensure a hostname belongs to the requested domain."""
    return hostname.endswith(f".{domain}") and hostname != domain


def _extract_hostnames(
    records: list[dict[str, Any]],
    domain: str,
) -> list[str]:
    """Extract, normalize, validate, and deduplicate hostnames."""
    discovered: set[str] = set()

    for record in records:
        if not isinstance(record, dict):
            continue

        names: list[str] = []

        for field in ("name_value", "common_name"):
            value = record.get(field)

            if isinstance(value, str):
                names.extend(value.splitlines())

        for raw_name in names:
            hostname = _normalize_hostname(raw_name)

            if not _is_valid_hostname(hostname):
                continue

            if not _is_in_scope(hostname, domain):
                continue

            discovered.add(hostname)

    return sorted(discovered)


async def fetch_subdomains(
    domain: str,
    client: httpx.AsyncClient,
) -> list[str]:
    """
    Retrieve passive subdomain observations from crt.sh.

    The supplied client is managed by the caller so connection
    pooling and application-level timeout policies can be reused.
    """
    normalized_domain = domain.strip().lower().rstrip(".")

    if not _is_valid_hostname(normalized_domain):
        raise ValueError("A valid fully qualified domain is required.")

    try:
        response = await client.get(
            CRTSH_URL,
            params={
                "q": f"%.{normalized_domain}",
                "output": "json",
            },
        )
        response.raise_for_status()

    except httpx.TimeoutException as exc:
        logger.warning(
            "crt.sh request timed out for domain %s",
            normalized_domain,
        )
        raise CRTShError("Certificate Transparency request timed out.") from exc

    except httpx.HTTPStatusError as exc:
        logger.warning(
            "crt.sh returned HTTP %s for domain %s",
            exc.response.status_code,
            normalized_domain,
        )
        raise CRTShError("Certificate Transparency service returned an error.") from exc

    except httpx.RequestError as exc:
        logger.warning(
            "crt.sh connection failed for domain %s",
            normalized_domain,
        )
        raise CRTShError("Certificate Transparency service is unavailable.") from exc

    try:
        records = response.json()

    except ValueError as exc:
        raise CRTShError("Certificate Transparency service returned invalid JSON.") from exc

    if not isinstance(records, list):
        raise CRTShError("Certificate Transparency service returned an unexpected response.")

    return _extract_hostnames(records, normalized_domain)
