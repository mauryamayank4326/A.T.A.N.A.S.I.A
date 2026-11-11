"""Tests for crt.sh passive reconnaissance integration."""

import httpx
import pytest

from app.services.recon.crtsh import (
    CRTShError,
    _extract_hostnames,
    fetch_subdomains,
)


def test_extract_hostnames_normalizes_and_deduplicates() -> None:
    """Normalize wildcard and multiline certificate names."""

    records = [
        {"name_value": ("WWW.EXAMPLE.COM\n*.example.com\napi.example.com")},
        {"common_name": "api.example.com"},
    ]

    result = _extract_hostnames(records, "example.com")

    assert result == [
        "api.example.com",
        "example.com",
        "www.example.com",
    ] or result == [
        "api.example.com",
        "www.example.com",
    ]


@pytest.mark.asyncio
async def test_fetch_subdomains_success() -> None:
    """Retrieve and normalize a successful crt.sh response."""

    records = [
        {"name_value": "www.example.com\napi.example.com"},
        {"name_value": "api.example.com"},
    ]

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=records)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        result = await fetch_subdomains("example.com", client)

    assert result == [
        "api.example.com",
        "www.example.com",
    ]


@pytest.mark.asyncio
async def test_fetch_subdomains_rejects_out_of_scope_names() -> None:
    """Never return hostnames belonging to unrelated domains."""

    records = [{"name_value": ("api.example.com\nexample.com.attacker.net\nattacker.net")}]

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=records)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        result = await fetch_subdomains("example.com", client)

    assert result == ["api.example.com"]


@pytest.mark.asyncio
async def test_fetch_subdomains_handles_http_failure() -> None:
    """Translate HTTP failures into the connector exception."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503)

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(CRTShError):
            await fetch_subdomains("example.com", client)


@pytest.mark.asyncio
async def test_fetch_subdomains_handles_invalid_json() -> None:
    """Reject malformed JSON responses."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            content=b"not-json",
            headers={"Content-Type": "application/json"},
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(CRTShError):
            await fetch_subdomains("example.com", client)


@pytest.mark.asyncio
async def test_fetch_subdomains_rejects_invalid_domain() -> None:
    """Reject malformed domain input before making a request."""

    async with httpx.AsyncClient() as client:
        with pytest.raises(ValueError):
            await fetch_subdomains("https://example.com", client)
