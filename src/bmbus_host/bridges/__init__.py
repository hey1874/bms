from __future__ import annotations

from typing import Protocol

from bmbus_host.core.models import BridgeConfig, LinkKind

from .mock import MockBq4050Bridge
from .serial import BluetoothSerialBridge, SerialJsonBridge
from .server import MockBridgeServer
from .tcp import TcpJsonBridge


class BridgeProtocol(Protocol):
    @property
    def label(self) -> str: ...

    def open(self) -> None: ...

    def close(self) -> None: ...

    def read_snapshot(self, full: bool = True) -> dict[str, object]: ...


def build_bridge(kind: LinkKind, config: BridgeConfig) -> BridgeProtocol:
    if kind == LinkKind.MOCK:
        return MockBq4050Bridge()
    if kind == LinkKind.SERIAL:
        return SerialJsonBridge(
            port=config.normalized_serial_port(),
            baudrate=config.serial_baudrate,
            timeout_s=config.serial_timeout_s,
            label="USB-TTL 串口桥",
        )
    if kind == LinkKind.TCP:
        return TcpJsonBridge(config)
    return BluetoothSerialBridge(config)


__all__ = [
    "BluetoothSerialBridge",
    "BridgeProtocol",
    "MockBq4050Bridge",
    "MockBridgeServer",
    "SerialJsonBridge",
    "TcpJsonBridge",
    "build_bridge",
]