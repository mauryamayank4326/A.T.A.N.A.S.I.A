"""Tests for WHOIS passive intelligence service."""

from datetime import datetime, timezone

import pytest

from app.services.recon import whois_lookup
from app.services.recon.whois_lookup import (
    WhoisLookupError,
    WhoisLookupTimeoutError,
    fetch_whois,
    normalize_domain,
)


def test_normalize_domain() -> None:
    assert normalize_domain(" Example.COM. ") == "example.com"


@pytest.mark.parametrize(
    "domain",
    [
        "",
        "example",
        "https://example.com",
        "example.com/path",
        "-invalid.com",
        "example..com",
    ],
)
def test_normalize_domain_rejects_invalid_input(domain: str) -> None:
    with pytest.raises(ValueError):
        normalize_domain(domain)


@pytest.mark.asyncio
async def test_fetch_whois_normalizes_response(monkeypatch) -> None:
    creation_date = datetime(2020, 1, 1, tzinfo=timezone.utc)
    expiration_date = datetime(2030, 1, 1, tzinfo=timezone.utc)

    raw_data = {
        "registrar": "Example Registrar",
        "creation_date": creation_date,
        "expiration_date": expiration_date,
        "updated_date": None,
        "name_servers": [
            "NS2.EXAMPLE.NET",
            "ns1.example.net",
            "ns1.example.net",
        ],
        "emails": ["ADMIN@EXAMPLE.COM"],
        "org": "Example Organization",
        "country": "US",
    }

    def fake_whois(domain: str):
        assert domain == "example.com"
        return raw_data

    monkeypatch.setattr(whois_lookup.whois, "whois", fake_whois)

    result = await fetch_whois("example.com")

    assert result.domain == "example.com"
    assert result.registrar == "Example Registrar"
    assert result.creation_date == creation_date
    assert result.expiration_date == expiration_date
    assert result.nameservers == (
        "ns1.example.net",
        "ns2.example.net",
    )
    assert result.emails == ("admin@example.com",)
    assert result.organization == "Example Organization"
    assert result.country == "US"


@pytest.mark.asyncio
async def test_fetch_whois_handles_missing_fields(monkeypatch) -> None:
    monkeypatch.setattr(
        whois_lookup.whois,
        "whois",
        lambda domain: {},
    )

    result = await fetch_whois("example.com")

    assert result.registrar is None
    assert result.creation_date is None
    assert result.expiration_date is None
    assert result.nameservers == ()
    assert result.emails == ()


@pytest.mark.asyncio
async def test_fetch_whois_wraps_lookup_failure(monkeypatch) -> None:
    def failing_lookup(domain: str):
        raise OSError("Simulated network failure")

    monkeypatch.setattr(
        whois_lookup.whois,
        "whois",
        failing_lookup,
    )

    with pytest.raises(WhoisLookupError):
        await fetch_whois("example.com")


@pytest.mark.asyncio
async def test_fetch_whois_timeout(monkeypatch) -> None:
    def slow_lookup(domain: str):
        import time

        time.sleep(0.1)
        return {}

    monkeypatch.setattr(
        whois_lookup.whois,
        "whois",
        slow_lookup,
    )

    with pytest.raises(WhoisLookupTimeoutError):
        await fetch_whois(
            "example.com",
            timeout_seconds=0.01,
        )


@pytest.mark.asyncio
async def test_fetch_whois_rejects_invalid_timeout() -> None:
    with pytest.raises(ValueError):
        await fetch_whois(
            "example.com",
            timeout_seconds=0,
        )
