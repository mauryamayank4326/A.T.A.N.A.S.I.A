"""Tests for unified passive reconnaissance."""

from datetime import datetime, timezone

import httpx
import pytest

from app.services.recon import passive_recon
from app.services.recon.passive_recon import (
    PassiveReconError,
    PassiveReconResult,
    run_passive_recon,
)
from app.services.recon.whois_lookup import WhoisRecord


def build_whois_record() -> WhoisRecord:
    return WhoisRecord(
        domain="example.com",
        registrar="Example Registrar",
        creation_date=datetime(2020, 1, 1, tzinfo=timezone.utc),
        expiration_date=datetime(2030, 1, 1, tzinfo=timezone.utc),
        updated_date=None,
        nameservers=("ns1.example.net",),
        emails=("admin@example.com",),
        organization="Example Organization",
        country="US",
    )


@pytest.mark.asyncio
async def test_passive_recon_success(monkeypatch) -> None:
    async def fake_crtsh(domain, client):
        return [
            "api.example.com",
            "www.example.com",
        ]

    async def fake_whois(domain, timeout_seconds):
        return build_whois_record()

    monkeypatch.setattr(
        passive_recon,
        "fetch_subdomains",
        fake_crtsh,
    )
    monkeypatch.setattr(
        passive_recon,
        "fetch_whois",
        fake_whois,
    )

    async with httpx.AsyncClient() as client:
        result = await run_passive_recon(
            "Example.COM",
            client,
        )

    assert isinstance(result, PassiveReconResult)
    assert result.domain == "example.com"
    assert result.subdomains == (
        "api.example.com",
        "www.example.com",
    )
    assert result.whois_record is not None
    assert result.successful_sources == ("crt.sh", "whois")
    assert result.failed_sources == ()


@pytest.mark.asyncio
async def test_passive_recon_survives_crtsh_failure(monkeypatch) -> None:
    async def failing_crtsh(domain, client):
        raise passive_recon.CRTShError("Simulated crt.sh failure")

    async def fake_whois(domain, timeout_seconds):
        return build_whois_record()

    monkeypatch.setattr(
        passive_recon,
        "fetch_subdomains",
        failing_crtsh,
    )
    monkeypatch.setattr(
        passive_recon,
        "fetch_whois",
        fake_whois,
    )

    async with httpx.AsyncClient() as client:
        result = await run_passive_recon(
            "example.com",
            client,
        )

    assert result.subdomains == ()
    assert result.whois_record is not None
    assert result.crtsh_error is not None
    assert result.failed_sources == ("crt.sh",)


@pytest.mark.asyncio
async def test_passive_recon_survives_whois_failure(monkeypatch) -> None:
    async def fake_crtsh(domain, client):
        return ["api.example.com"]

    async def failing_whois(domain, timeout_seconds):
        raise passive_recon.WhoisLookupError("Simulated WHOIS failure")

    monkeypatch.setattr(
        passive_recon,
        "fetch_subdomains",
        fake_crtsh,
    )
    monkeypatch.setattr(
        passive_recon,
        "fetch_whois",
        failing_whois,
    )

    async with httpx.AsyncClient() as client:
        result = await run_passive_recon(
            "example.com",
            client,
        )

    assert result.subdomains == ("api.example.com",)
    assert result.whois_record is None
    assert result.whois_error is not None
    assert result.failed_sources == ("whois",)


@pytest.mark.asyncio
async def test_passive_recon_raises_when_all_sources_fail(
    monkeypatch,
) -> None:
    async def failing_crtsh(domain, client):
        raise passive_recon.CRTShError("crt.sh unavailable")

    async def failing_whois(domain, timeout_seconds):
        raise passive_recon.WhoisLookupError("WHOIS unavailable")

    monkeypatch.setattr(
        passive_recon,
        "fetch_subdomains",
        failing_crtsh,
    )
    monkeypatch.setattr(
        passive_recon,
        "fetch_whois",
        failing_whois,
    )

    async with httpx.AsyncClient() as client:
        with pytest.raises(PassiveReconError):
            await run_passive_recon(
                "example.com",
                client,
            )


@pytest.mark.asyncio
async def test_passive_recon_rejects_invalid_domain() -> None:
    async with httpx.AsyncClient() as client:
        with pytest.raises(ValueError):
            await run_passive_recon(
                "https://example.com",
                client,
            )


@pytest.mark.asyncio
async def test_passive_recon_rejects_invalid_timeout() -> None:
    async with httpx.AsyncClient() as client:
        with pytest.raises(ValueError):
            await run_passive_recon(
                "example.com",
                client,
                whois_timeout_seconds=0,
            )
