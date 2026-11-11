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
            crtsh_error = str(crtsh_result)

    else:
        subdomains = tuple(crtsh_result)

    if isinstance(whois_result, BaseException):
        if not isinstance(whois_result, Exception):
            raise whois_result

        if not isinstance(whois_result, (WhoisLookupError, ValueError)):
            whois_error = "Unexpected source failure"
        else:
            whois_error = str(whois_result)

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
