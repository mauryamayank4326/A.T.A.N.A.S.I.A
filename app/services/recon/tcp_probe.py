
"""Asynchronous TCP connect probing service."""

from __future__ import annotations

import asyncio
import inspect
from collections.abc import Sequence
from dataclasses import dataclass, replace
from enum import Enum
from time import perf_counter
from typing import ClassVar


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
    banner: str | None = None
    service_name: str | None = None
    service_confidence: str = "unknown"

@dataclass(frozen=True, slots=True)
class TCPServiceIdentification:
    """Represent a probable service identification."""

    service_name: str | None
    banner: str | None
    confidence: str

    SERVICE_PORT_HINTS: ClassVar[dict[int, str]] = {
        21: "ftp",
        22: "ssh",
        25: "smtp",
        53: "dns",
        80: "http",
        110: "pop3",
        143: "imap",
        443: "https",
        3306: "mysql",
        5432: "postgresql",
        6379: "redis",
        8080: "http-proxy",
        8443: "https-alt",
    }


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


async def grab_tcp_banner(
    host: str,
    port: int,
    timeout_seconds: float = 2.0,
    max_banner_bytes: int = 1024,
) -> str | None:
    """Read an initial banner from an authorized TCP service."""
    normalized_host = _validate_host(host)
    _validate_port(port)

    if (
        isinstance(timeout_seconds, bool)
        or not isinstance(timeout_seconds, int | float)
        or timeout_seconds <= 0
    ):
        raise TCPProbeError("Timeout must be a positive number.")

    if (
        isinstance(max_banner_bytes, bool)
        or not isinstance(max_banner_bytes, int)
        or not 1 <= max_banner_bytes <= 8192
    ):
        raise TCPProbeError(
            "max_banner_bytes must be between 1 and 8192."
        )

    writer = None

    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(normalized_host, port),
            timeout=float(timeout_seconds),
        )

        data = await asyncio.wait_for(
            reader.read(max_banner_bytes),
            timeout=float(timeout_seconds),
        )

        if not data:
            return None

        return data.decode("utf-8", errors="replace").strip() or None

    except (asyncio.TimeoutError, OSError):
        return None

    finally:
        if writer is not None:
            close_result = writer.close()
            if inspect.isawaitable(close_result):
                await close_result
            try:
                await writer.wait_closed()
            except OSError:
                pass


def identify_tcp_service(
    port: int,
    banner: str | None,
) -> TCPServiceIdentification:
    """Identify a probable service using banner and port hints."""
    _validate_port(port)

    normalized_banner = banner.strip() if banner else None

    if normalized_banner:
        lowered = normalized_banner.lower()

        if lowered.startswith("ssh-"):
            return TCPServiceIdentification(
                service_name="ssh",
                banner=normalized_banner,
                confidence="high",
            )

        if lowered.startswith("220"):
            return TCPServiceIdentification(
                service_name="ftp-or-mail",
                banner=normalized_banner,
                confidence="low",
            )

        if "smtp" in lowered:
            return TCPServiceIdentification(
                service_name="smtp",
                banner=normalized_banner,
                confidence="medium",
            )

    service_hint = TCPServiceIdentification.SERVICE_PORT_HINTS.get(port)

    return TCPServiceIdentification(
        service_name=service_hint,
        banner=normalized_banner,
        confidence="low" if service_hint else "unknown",
    )


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
        close_result = writer.close()
        if inspect.isawaitable(close_result):
            await close_result

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

async def enrich_tcp_observation(
    observation: TCPPortObservation,
    timeout_seconds: float = 2.0,
) -> TCPPortObservation:
    """Collect an initial banner and enrich an open-port observation."""
    if observation.status != TCPPortStatus.OPEN:
        return observation

    banner = await grab_tcp_banner(
        host=observation.host,
        port=observation.port,
        timeout_seconds=timeout_seconds,
    )

    identification = identify_tcp_service(
        port=observation.port,
        banner=banner,
    )

    return replace(
        observation,
        banner=identification.banner,
        service_name=identification.service_name,
        service_confidence=identification.confidence,
    )
