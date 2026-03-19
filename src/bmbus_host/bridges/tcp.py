from __future__ import annotations

import socket
import threading
from typing import Any, TextIO

from bmbus_host.bridges.protocol import BRIDGE_PROTOCOL_VERSION, BridgeProtocolError, send_bridge_request
from bmbus_host.core.models import BridgeConfig


class TcpJsonBridge:
    def __init__(self, config: BridgeConfig, label: str = "WiFi/TCP 桥") -> None:
        self._config = config
        self._base_label = label
        self._socket: socket.socket | None = None
        self._reader: TextIO | None = None
        self._writer: TextIO | None = None
        self._lock = threading.Lock()
        self._server_info: dict[str, Any] = {}

    @property
    def label(self) -> str:
        host = self._config.normalized_tcp_host()
        return f"{self._base_label} {host}:{self._config.tcp_port}"

    def open(self) -> None:
        host = self._config.normalized_tcp_host()
        timeout = self._config.tcp_timeout_s
        try:
            sock = socket.create_connection((host, self._config.tcp_port), timeout=timeout)
        except OSError as exc:
            raise RuntimeError(f"无法连接到 TCP 桥 {host}:{self._config.tcp_port}: {exc}") from exc

        sock.settimeout(timeout)
        self._socket = sock
        self._reader = sock.makefile("r", encoding="utf-8", newline="\n")
        self._writer = sock.makefile("w", encoding="utf-8", newline="\n")

        info = self._request("hello")
        protocol = info.get("protocol")
        if protocol != BRIDGE_PROTOCOL_VERSION:
            self.close()
            raise RuntimeError(f"桥接协议版本不匹配: {protocol!r}")
        self._server_info = info

    def close(self) -> None:
        if self._writer is not None:
            self._writer.close()
            self._writer = None
        if self._reader is not None:
            self._reader.close()
            self._reader = None
        if self._socket is not None:
            self._socket.close()
            self._socket = None
        self._server_info = {}

    def read_snapshot(self, full: bool = True) -> dict[str, Any]:
        return self._request("read_snapshot", full=full)

    def _request(self, command: str, **params: Any) -> dict[str, Any]:
        if self._reader is None or self._writer is None:
            raise RuntimeError("TCP 桥尚未连接。")

        def write_line(line: str) -> None:
            assert self._writer is not None
            self._writer.write(line + "\n")
            self._writer.flush()

        def read_line() -> str:
            assert self._reader is not None
            try:
                line = self._reader.readline()
            except OSError as exc:
                raise BridgeProtocolError(f"读取 TCP 桥响应失败: {exc}") from exc
            if not line:
                raise BridgeProtocolError("TCP 桥已断开连接。")
            return line

        with self._lock:
            return send_bridge_request(write_line, read_line, command, **params)