"""Manual Shodan intelligence lookup."""

import asyncio

import httpx

from app.config import get_settings
from app.services.recon.shodan import search_shodan_hosts


async def main() -> None:
    settings = get_settings()

    if (
        settings.shodan_api_key is None
        or not settings.shodan_api_key.get_secret_value().strip()
    ):
        raise RuntimeError("Configure MAURYA_SHODAN_API_KEY first.")

    timeout = httpx.Timeout(settings.http_timeout_seconds)

    async with httpx.AsyncClient(timeout=timeout) as client:
        result = await search_shodan_hosts(
            domain="example.com",
            client=client,
            api_key=settings.shodan_api_key,
        )

    print("Domain:", result.domain)
    print("Total matches:", result.total)
    print("Returned observations:", len(result.observations))
    print("Truncated:", result.truncated)

    for observation in result.observations:
        print(
            observation.ip,
            observation.port,
            observation.transport,
            observation.hostnames,
        )

    async with httpx.AsyncClient(
        timeout=settings.http_timeout_seconds,
    ) as client:
        result = await search_shodan_hosts(
            domain="example.com",
            client=client,
            api_key=settings.shodan_api_key,
        )
    print("Domain:", result.domain)
    print("Total matches:", result.total)
    print("Returned observations:", len(result.observations))
    print("Truncated:", result.truncated)


if __name__ == "__main__":
    asyncio.run(main())