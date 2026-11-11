"""Manual runner for unified passive reconnaissance."""

import asyncio

import httpx

from app.services.recon.passive_recon import run_passive_recon


async def main() -> None:
    timeout = httpx.Timeout(10.0)

    async with httpx.AsyncClient(timeout=timeout) as client:
        result = await run_passive_recon(
            "example.com",
            client,
            whois_timeout_seconds=10.0,
        )

    print(f"\nTarget: {result.domain}")

    print("\nDiscovered subdomains:")
    for subdomain in result.subdomains:
        print(f"  {subdomain}")

    print("\nWHOIS information:")
    if result.whois_record is not None:
        print("  Registrar:", result.whois_record.registrar)
        print("  Created:", result.whois_record.creation_date)
        print("  Expires:", result.whois_record.expiration_date)
        print("  Nameservers:", result.whois_record.nameservers)
    else:
        print("  WHOIS information unavailable")

    print("\nSource status:")
    print("  Successful:", result.successful_sources)
    print("  Failed:", result.failed_sources)

    if result.crtsh_error:
        print("  crt.sh error:", result.crtsh_error)

    if result.whois_error:
        print("  WHOIS error:", result.whois_error)


if __name__ == "__main__":
    asyncio.run(main())
