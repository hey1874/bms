from __future__ import annotations

import argparse
import json
import socketserver
import threading
import time
from typing import Any

from bmbus_host.bridges.mock import MockBq4050Bridge
from bmbus_host.bridges.protocol import BRIDGE_PROTOCOL_VERSION


class _ThreadingTcpServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

    def __init__(self, server_address: tuple[str, int], bridge: MockBq4050Bridge) -> None:
        super().__init__(server_address, _MockBridgeRequestHandler)
        self.bridge = bridge


class _MockBridgeRequestHandler(socketserver.StreamRequestHandler):
    def handle(self) -> None:
        while True:
            raw = self.rfile.readline()
            if not raw:
                return

            request_id: str | None = None
            try:
                request = json.loads(raw.decode("utf-8"))
                request_id = str(request.get("request_id", "")) or None
                command = request.get("command")
                if command == "hello":
                    result: dict[str, Any] = {
                        "protocol": BRIDGE_PROTOCOL_VERSION,
                        "bridge": "mock-tcp",
                        "device": "BQ4050",
                    }
                elif command == "read_snapshot":
                    full = bool(request.get("full", True))
                    result = self.server.bridge.read_snapshot(full=full)  # type: ignore[attr-defined]
                elif command == "ping":
                    result = {"alive": True}
                else:
                    raise RuntimeError(f"不支持的命令: {command!r}")
                response = {"request_id": request_id, "ok": True, "result": result}
            except Exception as exc:
                response = {"request_id": request_id, "ok": False, "error": str(exc)}

            payload = json.dumps(response, ensure_ascii=False) + "\n"
            self.wfile.write(payload.encode("utf-8"))


class MockBridgeServer:
    def __init__(self, host: str = "127.0.0.1", port: int = 8855) -> None:
        self.host = host
        self.port = port
        self._server: _ThreadingTcpServer | None = None
        self._thread: threading.Thread | None = None
        self._bridge: MockBq4050Bridge | None = None

    @property
    def is_running(self) -> bool:
        return self._server is not None

    def start(self) -> None:
        if self._server is not None:
            return

        bridge = MockBq4050Bridge()
        bridge.open()
        server = _ThreadingTcpServer((self.host, self.port), bridge)
        address = server.server_address
        self.host = str(address[0])
        self.port = int(address[1])
        self._bridge = bridge
        self._server = server
        self._thread = threading.Thread(target=server.serve_forever, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        if self._server is None:
            return

        self._server.shutdown()
        self._server.server_close()
        if self._thread is not None:
            self._thread.join(timeout=1.0)
        if self._bridge is not None:
            self._bridge.close()

        self._server = None
        self._thread = None
        self._bridge = None


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a local mock BMBus TCP bridge.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8855)
    args = parser.parse_args()

    server = MockBridgeServer(host=args.host, port=args.port)
    server.start()
    print(f"Mock bridge listening on {server.host}:{server.port}")

    try:
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        pass
    finally:
        server.stop()