from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class LinkKind(StrEnum):
    MOCK = "mock"
    SERIAL = "serial"
    TCP = "tcp"
    BLUETOOTH = "bluetooth"


@dataclass(slots=True)
class SnapshotResult:
    label: str
    payload: dict[str, Any]


@dataclass(slots=True)
class BridgeConfig:
    serial_port: str = "COM3"
    serial_baudrate: int = 115200
    serial_timeout_s: float = 2.0
    tcp_host: str = "127.0.0.1"
    tcp_port: int = 8855
    tcp_timeout_s: float = 2.0
    bluetooth_port: str = "COM8"
    bluetooth_baudrate: int = 115200
    bluetooth_timeout_s: float = 2.0

    def normalized_tcp_host(self) -> str:
        host = self.tcp_host.strip()
        return host or "127.0.0.1"

    def normalized_serial_port(self) -> str:
        return self.serial_port.strip()

    def normalized_bluetooth_port(self) -> str:
        return self.bluetooth_port.strip()