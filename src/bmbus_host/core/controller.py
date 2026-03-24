from __future__ import annotations

import threading

from PySide6.QtCore import QObject, QTimer, Signal

from bmbus_host.bridges import BridgeProtocol, build_bridge
from bmbus_host.core.models import BridgeConfig, LinkKind, SnapshotResult


class HostController(QObject):
    snapshot_ready = Signal(object)
    info = Signal(str)
    error = Signal(str)
    status_changed = Signal(str, str)
    busy_changed = Signal(bool)

    def __init__(self) -> None:
        super().__init__()
        self.bridge: BridgeProtocol | None = None
        self.bridge_kind: LinkKind | None = None
        self.busy = False
        self.auto_poll = True
        self.poll_interval_s = 1.0
        self.poll_timer = QTimer(self)
        self.poll_timer.timeout.connect(self._poll_tick)

    def connect_bridge(
        self,
        kind: LinkKind,
        config: BridgeConfig,
        auto_poll: bool,
        poll_interval_s: float,
    ) -> None:
        try:
            self.disconnect_bridge(silent=True)
            bridge = build_bridge(kind, config)
            bridge.open()
            self.bridge = bridge
            self.bridge_kind = kind
            self.auto_poll = auto_poll
            self.poll_interval_s = poll_interval_s
            self.status_changed.emit("已连接", "online")
            self.info.emit(f"已连接到 {bridge.label}")
            if not getattr(self.bridge, "is_streaming", False):
                self.request_snapshot(full=True, label="连接后首次读取")
            self._sync_polling()
        except Exception as exc:
            self.bridge = None
            self.bridge_kind = None
            self.status_changed.emit("连接失败", "error")
            self.error.emit(str(exc))

    def disconnect_bridge(self, silent: bool = False) -> None:
        self.poll_timer.stop()
        if self.bridge is not None:
            try:
                self.bridge.close()
            finally:
                self.bridge = None
        self.bridge_kind = None
        self._set_busy(False)
        self.status_changed.emit("未连接", "offline")
        if not silent:
            self.info.emit("连接已断开")

    def apply_poll_settings(self, auto_poll: bool, poll_interval_s: float) -> None:
        self.auto_poll = auto_poll
        self.poll_interval_s = poll_interval_s
        self._sync_polling()

    def request_snapshot(self, full: bool, label: str) -> None:
        if self.bridge is None:
            self.status_changed.emit("连接失败", "error")
            self.error.emit("当前没有可用连接，请先连接模拟设备或桥接端。")
            return
        if self.busy:
            return

        self._set_busy(True)

        def worker() -> None:
            try:
                payload = self.bridge.read_snapshot(full=full)
                self.snapshot_ready.emit(SnapshotResult(label, payload))
                self.status_changed.emit("已连接", "online")
            except Exception as exc:
                self.status_changed.emit("读取失败", "error")
                self.error.emit(f"{label}失败: {exc}")
            finally:
                self._set_busy(False)

        threading.Thread(target=worker, daemon=True).start()

    def _poll_tick(self) -> None:
        if self.bridge is None or self.busy:
            return
        self.request_snapshot(full=False, label="自动轮询")

    def _sync_polling(self) -> None:
        if self.bridge is None:
            self.poll_timer.stop()
            return

        is_streaming = getattr(self.bridge, "is_streaming", False)
        if is_streaming:
            self.poll_timer.stop()
            self._start_stream_worker()
            return

        if not self.auto_poll:
            self.poll_timer.stop()
            return
        self.poll_timer.start(max(200, int(self.poll_interval_s * 1000)))

    def _start_stream_worker(self) -> None:
        bridge_ref = self.bridge

        def worker() -> None:
            while self.bridge is bridge_ref and bridge_ref is not None:
                try:
                    payload = bridge_ref.read_snapshot(full=False)
                    self.snapshot_ready.emit(SnapshotResult("自动更新", payload))
                    self.status_changed.emit("已连接", "online")
                except Exception as exc:
                    # In stream mode, we can just ignore timeouts and keep reading
                    if "超时" in str(exc):
                        continue
                    self.status_changed.emit("读取失败", "error")
                    self.error.emit(f"自动更新失败: {exc}")
                    break

        threading.Thread(target=worker, daemon=True).start()

    def _set_busy(self, busy: bool) -> None:
        if self.busy == busy:
            return
        self.busy = busy
        self.busy_changed.emit(busy)