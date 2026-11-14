import asyncio

from app.services.recon.tcp_probe import scan_tcp_ports


async def main():
    results = await scan_tcp_ports(
        host="127.0.0.1",
        ports=[8000, 8080, 443],
        timeout_seconds=1.5,
        max_concurrency=5,
    )

    for result in results:
        print(
            result.host,
            result.port,
            result.status.value,
            round(result.latency_ms, 2),
        )


if __name__ == "__main__":
    asyncio.run(main())