from __future__ import annotations

from bmbus_host.bridges import MockBridgeServer, TcpJsonBridge
from bmbus_host.core.models import BridgeConfig


def test_tcp_bridge_reads_snapshot_from_mock_server() -> None:
    server = MockBridgeServer(host="127.0.0.1", port=0)
    server.start()

    bridge = TcpJsonBridge(
        BridgeConfig(
            tcp_host=server.host,
            tcp_port=server.port,
            tcp_timeout_s=1.0,
        )
    )
    bridge.open()

    try:
        snapshot = bridge.read_snapshot(full=True)
    finally:
        bridge.close()
        server.stop()

    assert snapshot["device.device_name"] == "BQ4050"
    assert snapshot["flags.security_mode"] == "SEALED"
    assert "diagnostics.da_pack_voltage_mv" in snapshot