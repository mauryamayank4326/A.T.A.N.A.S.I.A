
"""Asynchronous TCP connect probing service."""

from __future__ import annotations

import asyncio
from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum
from time import perf_counter


class TCPProbeError(ValueError):
    """Raised when TCP probe configuration is invalid."""


class TCPPortStatus(str, Enum):
    """Possible outcomes of a TCP connection attempt."""

    OPEN = "open"
    CLOSED = "closed"
    FILTERED = "filtered"
    ERROR = "error"


@dataclass(frozen=True, slots=True)
class TCPPortObservation:
    """Normalized result of a TCP port probe."""

    host: str
    port: int
    status: TCPPortStatus
    latency_ms: float
    error: str | None = None


def _validate_host(host: str) -> str:
    """Validate and normalize a target hostname or IP string."""
    if not isinstance(host, str) or not host.strip():
        raise TCPProbeError("Target host must be a non-empty string.")

    return host.strip()


def _validate_port(port: int) -> None:
    """Validate a TCP port number."""
    if isinstance(port, bool) or not isinstance(port, int):
        raise TCPProbeError("Port must be an integer.")

    if not 1 <= port <= 65535:
        raise TCPProbeError("Port must be between 1 and 65535.")


async def probe_tcp_port(
    host: str,
    port: int,
    timeout_seconds: float = 2.0,
) -> TCPPortObservation:
    """Probe one TCP port using a normal TCP connection."""
    normalized_host = _validate_host(host)
    _validate_port(port)

    if (
        isinstance(timeout_seconds, bool)
        or not isinstance(timeout_seconds, int | float)
        or timeout_seconds <= 0
    ):
        raise TCPProbeError("Timeout must be a positive number.")

    started_at = perf_counter()

    try:
        _, writer = await asyncio.wait_for(
            asyncio.open_connection(normalized_host, port),
            timeout=float(timeout_seconds),
        )

    except asyncio.TimeoutError:
        return TCPPortObservation(
            host=normalized_host,
            port=port,
            status=TCPPortStatus.FILTERED,
            latency_ms=(perf_counter() - started_at) * 1000,
            error="Connection attempt timed out.",
        )

    except ConnectionRefusedError:
        return TCPPortObservation(
            host=normalized_host,
            port=port,
            status=TCPPortStatus.CLOSED,
            latency_ms=(perf_counter() - started_at) * 1000,
        )

    except OSError as exc:
        return TCPPortObservation(
            host=normalized_host,
            port=port,
            status=TCPPortStatus.ERROR,
            latency_ms=(perf_counter() - started_at) * 1000,
            error=type(exc).__name__,
        )

    else:
        writer.close()

        try:
            await writer.wait_closed()
        except OSError:
            pass

        return TCPPortObservation(
            host=normalized_host,
            port=port,
            status=TCPPortStatus.OPEN,
            latency_ms=(perf_counter() - started_at) * 1000,
        )


async def scan_tcp_ports(
    host: str,
    ports: Sequence[int],
    timeout_seconds: float = 2.0,
    max_concurrency: int = 20,
) -> tuple[TCPPortObservation, ...]:
    """Probe multiple TCP ports with bounded concurrency."""
    normalized_host = _validate_host(host)

    if (
        isinstance(max_concurrency, bool)
        or not isinstance(max_concurrency, int)
        or max_concurrency < 1
    ):
        raise TCPProbeError("max_concurrency must be a positive integer.")

    if not isinstance(ports, list | tuple):
        raise TCPProbeError("Ports must be provided as a list or tuple.")

    normalized_ports = tuple(dict.fromkeys(ports))

    for port in normalized_ports:
        _validate_port(port)

    if (
        isinstance(timeout_seconds, bool)
        or not isinstance(timeout_seconds, int | float)
        or timeout_seconds <= 0
    ):
        raise TCPProbeError("Timeout must be a positive number.")

    semaphore = asyncio.Semaphore(max_concurrency)

    async def bounded_probe(port: int) -> TCPPortObservation:
        async with semaphore:
            return await probe_tcp_port(
                host=normalized_host,
                port=port,
                timeout_seconds=float(timeout_seconds),
            )

    results = await asyncio.gather(
        *(bounded_probe(port) for port in normalized_ports)
    )

    return tuple(results)
