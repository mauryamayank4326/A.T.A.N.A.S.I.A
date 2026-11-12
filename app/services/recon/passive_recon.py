"""Unified passive reconnaissance service."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

import httpx

from app.services.recon.crtsh import (
    CRTShError,
    fetch_subdomains,
)
from app.services.recon.whois_lookup import (
    WhoisLookupError,
    WhoisRecord,
    fetch_whois,
    normalize_domain,
)


class PassiveReconError(Exception):
    """Raised when every passive reconnaissance source fails."""

def sanitize_source_error(source: str) -> str:
    """Return a safe, stable error message for a failed source."""
    return f"{source} collection failed."


@dataclass(frozen=True, slots=True)
class PassiveReconResult:
    """Combined passive reconnaissance results."""

    domain: str
    subdomains: tuple[str, ...]
    whois_record: WhoisRecord | None
    crtsh_error: str | None
    whois_error: str | None

    @property
    def successful_sources(self) -> tuple[str, ...]:
        """Return the names of sources that completed successfully."""
        successful = []

        if self.crtsh_error is None:
            successful.append("crt.sh")

        if self.whois_error is None:
            successful.append("whois")

        return tuple(successful)

    @property
    def failed_sources(self) -> tuple[str, ...]:
        """Return the names of sources that failed."""
        failed = []

        if self.crtsh_error is not None:
            failed.append("crt.sh")

        if self.whois_error is not None:
            failed.append("whois")

        return tuple(failed)


async def run_passive_recon(
    domain: str,
    client: httpx.AsyncClient,
    whois_timeout_seconds: float = 10.0,
) -> PassiveReconResult:
    """Execute crt.sh and WHOIS lookups concurrently."""

    normalized_domain = normalize_domain(domain)

    if whois_timeout_seconds <= 0:
        raise ValueError("WHOIS timeout must be greater than zero.")

    crtsh_result, whois_result = await asyncio.gather(
        fetch_subdomains(normalized_domain, client),
        fetch_whois(
            normalized_domain,
            timeout_seconds=whois_timeout_seconds,
        ),
        return_exceptions=True,
    )

    crtsh_error = None
    whois_error = None
    subdomains: tuple[str, ...] = ()
    whois_record = None

    if isinstance(crtsh_result, BaseException):
        if not isinstance(crtsh_result, Exception):
            raise crtsh_result

        if not isinstance(crtsh_result, (CRTShError, ValueError)):
            crtsh_error = "Unexpected source failure"
        else:
            crtsh_error = sanitize_source_error("crt.sh")

    else:
        subdomains = normalize_subdomains(
            crtsh_result,
            normalized_domain,
        )

    if isinstance(whois_result, BaseException):
        if not isinstance(whois_result, Exception):
            raise whois_result

        if not isinstance(whois_result, (WhoisLookupError, ValueError)):
            whois_error = "Unexpected source failure"
        else:
            whois_error = sanitize_source_error("WHOIS")

    else:
        whois_record = whois_result

    if crtsh_error is not None and whois_error is not None:
        raise PassiveReconError(
            f"All passive reconnaissance sources failed for {normalized_domain}."
        )

    return PassiveReconResult(
        domain=normalized_domain,
        subdomains=subdomains,
        whois_record=whois_record,
        crtsh_error=crtsh_error,
        whois_error=whois_error,
    )
def normalize_subdomains(
    subdomains: tuple[str, ...] | list[str],
    domain: str,
) -> tuple[str, ...]:
    """Return unique, normalized, in-scope subdomains."""
    normalized_domain = normalize_domain(domain)
    results: set[str] = set()

    for item in subdomains:
        if not isinstance(item, str):
            continue

        hostname = item.strip().lower().rstrip(".")

        if hostname.startswith("*."):
            hostname = hostname[2:]

        if not hostname or hostname == normalized_domain:
            continue

        if hostname.endswith(f".{normalized_domain}"):
            results.add(hostname)

    return tuple(sorted(results))