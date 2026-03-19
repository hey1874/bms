from __future__ import annotations

from typing import Protocol

from bmbus_host.core.models import LinkKind

from .mock import MockBq4050Bridge
from .placeholder import PlaceholderBridge


class BridgeProtocol(Protocol):
    @property
    def label(self) -> str: ...

    def open(self) -> None: ...

    def close(self) -> None: ...

    def read_snapshot(self, full: bool = True) -> dict[str, object]: ...


def build_bridge(kind: LinkKind) -> BridgeProtocol:
    if kind == LinkKind.MOCK:
        return MockBq4050Bridge()
    if kind == LinkKind.SERIAL:
        return PlaceholderBridge("USB-TTL 串口桥")
    if kind == LinkKind.TCP:
        return PlaceholderBridge("WiFi/TCP 桥")
    return PlaceholderBridge("Bluetooth 桥")


__all__ = [
    "BridgeProtocol",
    "MockBq4050Bridge",
    "PlaceholderBridge",
    "build_bridge",
]
