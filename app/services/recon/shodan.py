
"""Asynchronous Shodan intelligence collection service."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx
from pydantic import SecretStr

from app.services.recon.whois_lookup import normalize_domain

SHODAN_SEARCH_URL = "https://api.shodan.io/shodan/host/search"
MAX_RESULTS_LIMIT = 100


class ShodanError(RuntimeError):
    """Base exception for Shodan collection failures."""


class ShodanConfigurationError(ShodanError):
    """Raised when Shodan configuration is invalid."""


class ShodanAuthenticationError(ShodanError):
    """Raised when Shodan rejects the API credentials."""


class ShodanRateLimitError(ShodanError):
    """Raised when the API rate limit is reached."""


class ShodanRequestError(ShodanError):
    """Raised when the Shodan request fails."""


class ShodanResponseError(ShodanError):
    """Raised when Shodan returns an unexpected response."""


@dataclass(frozen=True, slots=True)
class ShodanHostObservation:
    """Normalized host observation returned by Shodan."""

    ip: str
    port: int
    transport: str | None
    hostnames: tuple[str, ...]
    domains: tuple[str, ...]
    organization: str | None
    product: str | None
    timestamp: str | None


@dataclass(frozen=True, slots=True)
class ShodanSearchResult:
    """Combined result of a Shodan host search."""

    domain: str
    query: str
    total: int
    observations: tuple[ShodanHostObservation, ...]

    @property
    def truncated(self) -> bool:
        """Indicate whether the result limit omitted matches."""
        return self.total > len(self.observations)


def _optional_string(value: Any) -> str | None:
    """Convert a non-empty string value into an optional string."""
    if not isinstance(value, str):
        return None

    value = value.strip()
    return value or None


def _string_tuple(value: Any) -> tuple[str, ...]:
    """Normalize a list of strings into a tuple."""
    if not isinstance(value, list):
        return ()

    return tuple(
        sorted(
            {
                item.strip().lower()
                for item in value
                if isinstance(item, str) and item.strip()
            }
        )
    )


def _normalize_match(match: Any) -> ShodanHostObservation:
    """Convert a Shodan match into a normalized observation."""
    if not isinstance(match, dict):
        raise ShodanResponseError("Shodan returned an invalid host record.")

    ip = _optional_string(match.get("ip_str"))
    port = match.get("port")

    if ip is None:
        raise ShodanResponseError("Shodan host record is missing its IP address.")

    if isinstance(port, bool) or not isinstance(port, int) or not 1 <= port <= 65535:
        raise ShodanResponseError("Shodan host record contains an invalid port.")

    return ShodanHostObservation(
        ip=ip,
        port=port,
        transport=_optional_string(match.get("transport")),
        hostnames=_string_tuple(match.get("hostnames")),
        domains=_string_tuple(match.get("domains")),
        organization=_optional_string(match.get("org")),
        product=_optional_string(match.get("product")),
        timestamp=_optional_string(match.get("timestamp")),
    )


async def search_shodan_hosts(
    domain: str,
    client: httpx.AsyncClient,
    api_key: SecretStr,
    max_results: int = 100,
) -> ShodanSearchResult:
    """Search Shodan for indexed hosts associated with a domain."""
    normalized_domain = normalize_domain(domain)

    if not isinstance(api_key, SecretStr):
        raise ShodanConfigurationError("Shodan API key must be a SecretStr.")

    secret = api_key.get_secret_value().strip()

    if not secret:
        raise ShodanConfigurationError("Shodan API key is not configured.")

    if isinstance(max_results, bool) or not isinstance(max_results, int):
        raise ValueError("max_results must be an integer.")

    if not 1 <= max_results <= MAX_RESULTS_LIMIT:
        raise ValueError(
            f"max_results must be between 1 and {MAX_RESULTS_LIMIT}."
        )

    query = f"hostname:{normalized_domain}"

    try:
        response = await client.get(
            SHODAN_SEARCH_URL,
            params={
                "key": secret,
                "query": query,
                "minify": "true",
            },
        )
        response.raise_for_status()

    except httpx.TimeoutException as exc:
        raise ShodanRequestError("Shodan request timed out.") from exc

    except httpx.HTTPStatusError as exc:
        status_code = exc.response.status_code

        if status_code in (401, 403):
            raise ShodanAuthenticationError(
                "Shodan authentication or authorization failed."
            ) from exc

        if status_code == 429:
            raise ShodanRateLimitError(
                "Shodan API rate limit reached."
            ) from exc

        raise ShodanRequestError(
            f"Shodan returned HTTP status {status_code}."
        ) from exc

    except httpx.RequestError as exc:
        raise ShodanRequestError(
            "Unable to communicate with the Shodan API."
        ) from exc

    try:
        payload = response.json()
    except ValueError as exc:
        raise ShodanResponseError(
            "Shodan returned invalid JSON."
        ) from exc

    if not isinstance(payload, dict):
        raise ShodanResponseError(
            "Shodan returned an unexpected response structure."
        )

    total = payload.get("total")
    matches = payload.get("matches")

    if isinstance(total, bool) or not isinstance(total, int) or total < 0:
        raise ShodanResponseError("Shodan returned an invalid result count.")

    if not isinstance(matches, list):
        raise ShodanResponseError("Shodan returned an invalid matches collection.")

    observations = tuple(
        _normalize_match(match)
        for match in matches[:max_results]
    )
    return ShodanSearchResult(
        domain=normalized_domain,
        query=query,
        total=total,
        observations=observations,
    )
