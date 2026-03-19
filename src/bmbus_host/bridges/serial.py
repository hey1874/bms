from __future__ import annotations

import threading
from typing import Any

from bmbus_host.bridges.protocol import BRIDGE_PROTOCOL_VERSION, BridgeProtocolError, send_bridge_request
from bmbus_host.core.models import BridgeConfig


class SerialJsonBridge:
    def __init__(self, port: str, baudrate: int, timeout_s: float, label: str) -> None:
        self._port = port
        self._baudrate = baudrate
        self._timeout_s = timeout_s
        self._label = label
        self._serial = None
        self._lock = threading.Lock()

    @property
    def label(self) -> str:
        return f"{self._label} {self._port}"

    def open(self) -> None:
        if not self._port:
            raise RuntimeError("串口号不能为空。")

        try:
            import serial  # type: ignore[import-not-found]
        except ImportError as exc:
            raise RuntimeError("串口链路需要 pyserial，请先在环境中安装 pyserial。") from exc

        try:
            self._serial = serial.Serial(
                port=self._port,
                baudrate=self._baudrate,
                timeout=self._timeout_s,
                write_timeout=self._timeout_s,
            )
        except Exception as exc:
            raise RuntimeError(f"无法打开串口 {self._port}: {exc}") from exc

        info = self._request("hello")
        protocol = info.get("protocol")
        if protocol != BRIDGE_PROTOCOL_VERSION:
            self.close()
            raise RuntimeError(f"桥接协议版本不匹配: {protocol!r}")

    def close(self) -> None:
        if self._serial is not None:
            self._serial.close()
            self._serial = None

    def read_snapshot(self, full: bool = True) -> dict[str, Any]:
        return self._request("read_snapshot", full=full)

    def _request(self, command: str, **params: Any) -> dict[str, Any]:
        if self._serial is None:
            raise RuntimeError("串口桥尚未连接。")

        def write_line(line: str) -> None:
            assert self._serial is not None
            self._serial.write((line + "\n").encode("utf-8"))
            self._serial.flush()

        def read_line() -> str:
            assert self._serial is not None
            raw = self._serial.readline()
            if not raw:
                raise BridgeProtocolError("串口桥未返回数据，可能超时或设备已断开。")
            return raw.decode("utf-8", errors="strict")

        with self._lock:
            return send_bridge_request(write_line, read_line, command, **params)


class BluetoothSerialBridge(SerialJsonBridge):
    def __init__(self, config: BridgeConfig) -> None:
        super().__init__(
            port=config.normalized_bluetooth_port(),
            baudrate=config.bluetooth_baudrate,
            timeout_s=config.bluetooth_timeout_s,
            label="Bluetooth 串口桥",
        )