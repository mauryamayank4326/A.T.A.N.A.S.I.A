
"""Manual WHOIS lookup runner."""

import asyncio

from app.services.recon.whois_lookup import fetch_whois


async def main() -> None:
    result = await fetch_whois(
        "example.com",
        timeout_seconds=10.0,
    )

    print("Domain:", result.domain)
    print("Registrar:", result.registrar)
    print("Created:", result.creation_date)
    print("Expires:", result.expiration_date)
    print("Nameservers:", result.nameservers)


if __name__ == "__main__":
    asyncio.run(main())
