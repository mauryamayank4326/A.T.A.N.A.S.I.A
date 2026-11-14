
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.recon.tcp_probe import (
    TCPPortStatus,
    TCPProbeError,
    grab_tcp_banner,
    identify_tcp_service,
    probe_tcp_port,
    scan_tcp_ports,
)


@pytest.mark.asyncio
async def test_grab_tcp_banner():
    reader = asyncio.StreamReader()
    reader.feed_data(b"SSH-2.0-OpenSSH_9.6\r\n")
    reader.feed_eof()

    writer = AsyncMock()
    writer.wait_closed = AsyncMock()

    with patch(
        "app.services.recon.tcp_probe.asyncio.open_connection",
        new=AsyncMock(return_value=(reader, writer)),
    ):
        banner = await grab_tcp_banner("127.0.0.1", 2222)

    assert banner == "SSH-2.0-OpenSSH_9.6"
    writer.close.assert_called_once()

@pytest.mark.asyncio
async def test_probe_tcp_port_open():
    writer = MagicMock()
    writer.wait_closed = AsyncMock()

    with patch(
        "app.services.recon.tcp_probe.asyncio.open_connection",
        new=AsyncMock(return_value=(None, writer)),
    ):
        result = await probe_tcp_port("127.0.0.1", 443)

    assert result.status == TCPPortStatus.OPEN
    assert result.port == 443
    writer.close.assert_called_once()
    writer.wait_closed.assert_awaited_once()


@pytest.mark.asyncio
async def test_probe_tcp_port_closed():
    with patch(
        "app.services.recon.tcp_probe.asyncio.open_connection",
        new=AsyncMock(side_effect=ConnectionRefusedError),
    ):
        result = await probe_tcp_port("127.0.0.1", 8080)

    assert result.status == TCPPortStatus.CLOSED


@pytest.mark.asyncio
async def test_probe_tcp_port_timeout():
    with patch(
        "app.services.recon.tcp_probe.asyncio.open_connection",
        new=AsyncMock(side_effect=asyncio.TimeoutError),
    ):
        result = await probe_tcp_port("127.0.0.1", 8081)

    assert result.status == TCPPortStatus.FILTERED
    assert result.error == "Connection attempt timed out."


@pytest.mark.asyncio
async def test_scan_tcp_ports_deduplicates_ports():
    writer = MagicMock()
    writer.wait_closed = AsyncMock()

    with patch(
        "app.services.recon.tcp_probe.asyncio.open_connection",
        new=AsyncMock(return_value=(None, writer)),
    ) as mock_connection:
        results = await scan_tcp_ports(
            host="127.0.0.1",
            ports=[80, 443, 80],
            max_concurrency=2,
        )

    assert len(results) == 2
    assert [result.port for result in results] == [80, 443]
    assert mock_connection.await_count == 2


@pytest.mark.asyncio
async def test_scan_tcp_ports_rejects_invalid_port():
    with pytest.raises(TCPProbeError):
        await scan_tcp_ports(
            host="127.0.0.1",
            ports=[80, 70000],
        )


@pytest.mark.asyncio
async def test_scan_tcp_ports_rejects_invalid_concurrency():
    with pytest.raises(TCPProbeError):
        await scan_tcp_ports(
            host="127.0.0.1",
            ports=[80],
            max_concurrency=0,
        )


def test_probe_rejects_empty_host():
    with pytest.raises(TCPProbeError):
        asyncio.run(probe_tcp_port("", 80))

def test_identify_ssh_from_banner():
    result = identify_tcp_service(
        2222,
        "SSH-2.0-OpenSSH_9.6",
    )

    assert result.service_name == "ssh"
    assert result.confidence == "high"


def test_identify_service_from_port_hint():
    result = identify_tcp_service(443, None)

    assert result.service_name == "https"
    assert result.confidence == "low"


def test_unknown_port_without_banner():
    result = identify_tcp_service(49152, None)

    assert result.service_name is None
    assert result.confidence == "unknown"
