
import httpx
import pytest

from app.config import get_settings
from app.services.recon.shodan import (
    ShodanAuthenticationError,
    ShodanRateLimitError,
    ShodanRequestError,
    ShodanResponseError,
    search_shodan_hosts,
)


@pytest.fixture(autouse=True)
def clear_settings_cache():
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def configured_settings(monkeypatch, api_key="test-api-key"):
    monkeypatch.setenv("MAURYA_SHODAN_API_KEY", api_key)
    get_settings.cache_clear()
    return get_settings()


def make_client(handler):
    transport = httpx.MockTransport(handler)
    return httpx.AsyncClient(transport=transport)


@pytest.mark.asyncio
async def test_shodan_search_success(monkeypatch):
    settings = configured_settings(monkeypatch)
    assert settings.shodan_api_key.get_secret_value() == "test-api-key"
    payload = {
        "total": 1,
        "matches": [
            {
                "ip_str": "203.0.113.10",
                "port": 443,
                "transport": "tcp",
                "hostnames": ["WWW.Example.com"],
                "domains": ["Example.com"],
                "org": "Example Hosting",
                "product": "Example Server",
                "timestamp": "2026-11-01T10:00:00.000000",
            }
        ],
    }

    def handler(request):
        assert request.url.params["query"] == "hostname:example.com"
        assert request.url.params["key"] == "test-api-key"
        return httpx.Response(200, json=payload)

    async with make_client(handler) as client:
        result = await search_shodan_hosts(
            domain="Example.com",
            client=client,
            api_key=settings.shodan_api_key,
        )

    assert result.domain == "example.com"
    assert result.total == 1
    assert result.observations[0].ip == "203.0.113.10"
    assert result.observations[0].port == 443
    assert result.observations[0].hostnames == ("www.example.com",)


@pytest.mark.asyncio
async def test_shodan_authentication_error(monkeypatch):
    settings = configured_settings(monkeypatch, "invalid-key")
    assert settings.shodan_api_key.get_secret_value() == "invalid-key"

    def handler(request):
        return httpx.Response(401, json={"error": "Invalid API key"})

    async with make_client(handler) as client:
        with pytest.raises(ShodanAuthenticationError):
            await search_shodan_hosts(
                domain="example.com",
                client=client,
                api_key=settings.shodan_api_key,
            )


@pytest.mark.asyncio
async def test_shodan_rate_limit_error(monkeypatch):
    settings = configured_settings(monkeypatch)
    assert settings.shodan_api_key.get_secret_value() == "test-api-key"

    def handler(request):
        return httpx.Response(429, json={"error": "Rate limit exceeded"})

    async with make_client(handler) as client:
        with pytest.raises(ShodanRateLimitError):
            await search_shodan_hosts(
                domain="example.com",
                client=client,
                api_key=settings.shodan_api_key,
            )


@pytest.mark.asyncio
async def test_shodan_invalid_json(monkeypatch):
    settings = configured_settings(monkeypatch)
    assert settings.shodan_api_key.get_secret_value() == "test-api-key"

    def handler(request):
        return httpx.Response(200, content=b"not-json")

    async with make_client(handler) as client:
        with pytest.raises(ShodanResponseError):
            await search_shodan_hosts(
                domain="example.com",
                client=client,
                api_key=settings.shodan_api_key,
            )


@pytest.mark.asyncio
async def test_shodan_empty_results(monkeypatch):
    settings = configured_settings(monkeypatch)
    assert settings.shodan_api_key.get_secret_value() == "test-api-key"

    def handler(request):
        return httpx.Response(
            200,
            json={"total": 0, "matches": []},
        )

    async with make_client(handler) as client:
        result = await search_shodan_hosts(
            domain="example.com",
            client=client,
            api_key=settings.shodan_api_key,
        )

    assert result.total == 0
    assert result.observations == ()
    assert result.truncated is False


@pytest.mark.asyncio
async def test_shodan_caps_observations_to_max_results(monkeypatch):
    settings = configured_settings(monkeypatch)
    assert settings.shodan_api_key.get_secret_value() == "test-api-key"

    def handler(request):
        return httpx.Response(
            200,
            json={
                "total": 3,
                "matches": [
                    {"ip_str": f"203.0.113.{index}", "port": 443}
                    for index in range(1, 4)
                ],
            },
        )

    async with make_client(handler) as client:
        result = await search_shodan_hosts(
            domain="example.com",
            client=client,
            api_key=settings.shodan_api_key,
            max_results=2,
        )

    assert result.total == 3
    assert len(result.observations) == 2
    assert result.truncated is True


@pytest.mark.asyncio
async def test_shodan_connection_error(monkeypatch):
    settings = configured_settings(monkeypatch)
    assert settings.shodan_api_key.get_secret_value() == "test-api-key"

    def handler(request):
        raise httpx.ConnectError("internal connection detail")

    async with make_client(handler) as client:
        with pytest.raises(ShodanRequestError):
            await search_shodan_hosts(
                domain="example.com",
                client=client,
                api_key=settings.shodan_api_key,
            )
