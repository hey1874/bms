from __future__ import annotations

from datetime import datetime
from typing import Any

from PySide6.QtCore import QObject, Property, Slot, Signal

from bmbus_host.bridges import MockBridgeServer
from bmbus_host.core.controller import HostController
from bmbus_host.core.labels import SECTION_FIELDS, field_label, format_value
from bmbus_host.core.models import BridgeConfig, LinkKind, SnapshotResult


class AppModel(QObject):
    logAppended = Signal(str)
    dataChanged = Signal()
    statusChangedSignal = Signal()
    simStatusChanged = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.latest: dict[str, Any] = {}
        
        self.controller = HostController()
        self.controller.snapshot_ready.connect(self._on_snapshot_ready)
        self.controller.info.connect(self._on_info)
        self.controller.error.connect(self._on_error)
        self.controller.status_changed.connect(self._on_status_changed)
        self.controller.busy_changed.connect(self._on_busy_changed)

        self._local_mock_server: MockBridgeServer | None = None

        self._statusPillText = "未连接"
        self._statusPillState = "offline"
        self._summaryText = "等待设备连接，准备接收 BMBus 遥测数据..."
        self._updatedText = "最后同步: N/A"
        self._simStatusText = "本地模拟桥未启动"
        self._simRunning = False

        self._append_log("界面已启动，当前默认使用模拟设备进行联调。")

    @Property("QVariantMap", notify=dataChanged)
    def latestData(self) -> dict[str, Any]:
        return dict(self.latest)

    @Property(str, notify=dataChanged)
    def latestDataJson(self) -> str:
        import json
        return json.dumps(self.latest)

    @Property(bool, notify=statusChangedSignal)
    def isConnected(self) -> bool:
        return self.controller.bridge is not None

    @Property(bool, notify=statusChangedSignal)
    def isBusy(self) -> bool:
        return self.controller.busy

    @Property(str, notify=statusChangedSignal)
    def statusPillText(self) -> str:
        return self._statusPillText

    @Property(str, notify=statusChangedSignal)
    def statusPillState(self) -> str:
        return self._statusPillState

    @Property(str, notify=dataChanged)
    def summaryText(self) -> str:
        return self._summaryText

    @Property(str, notify=dataChanged)
    def updatedText(self) -> str:
        return self._updatedText

    @Property(str, notify=simStatusChanged)
    def simStatusText(self) -> str:
        return self._simStatusText

    @Property(bool, notify=simStatusChanged)
    def isSimRunning(self) -> bool:
        return self._simRunning

    @Property(str, constant=True)
    def sectionNamesJson(self) -> str:
        import json
        return json.dumps(list(SECTION_FIELDS.keys()))

    @Property(str, constant=True)
    def sectionFieldsJson(self) -> str:
        import json
        return json.dumps(SECTION_FIELDS)

    @Slot(str, result=str)
    def fieldLabel(self, key: str) -> str:
        return field_label(key)

    @Slot(str, result=str)
    def fieldValue(self, key: str) -> str:
        if key not in self.latest:
            return ""
        return format_value(self.latest[key])

    @Slot(result="QStringList")
    def getSerialPorts(self) -> list[str]:
        try:
            import serial.tools.list_ports
            return [port.device for port in serial.tools.list_ports.comports()]
        except Exception:
            return []

    @Slot(str, dict, bool, float)
    def connectBridge(self, kindStr: str, configDict: dict[str, Any], autoPoll: bool, interval: float) -> None:
        try:
            kind = LinkKind(kindStr)
        except ValueError:
            kind = LinkKind.MOCK

        config = BridgeConfig(
            serial_port=configDict.get("serialPort", "COM3"),
            serial_baudrate=configDict.get("serialBaudrate", 115200),
            serial_timeout_s=configDict.get("serialTimeout", 2.0),
            tcp_host=configDict.get("tcpHost", "127.0.0.1"),
            tcp_port=configDict.get("tcpPort", 8855),
            tcp_timeout_s=configDict.get("tcpTimeout", 2.0),
            bluetooth_port=configDict.get("bluetoothPort", "COM8"),
            bluetooth_baudrate=configDict.get("bluetoothBaudrate", 115200),
            bluetooth_timeout_s=configDict.get("bluetoothTimeout", 2.0),
            ftdi_url=configDict.get("ftdiUrl", "ftdi://ftdi:4232/1"),
        )

        self.controller.connect_bridge(kind, config, autoPoll, interval)

    @Slot()
    def disconnectBridge(self) -> None:
        self.controller.disconnect_bridge()

    @Slot(bool, float)
    def applyPollSettings(self, autoPoll: bool, interval: float) -> None:
        self.controller.apply_poll_settings(autoPoll, interval)

    @Slot(bool, str)
    def requestSnapshot(self, full: bool, label: str) -> None:
        self.controller.request_snapshot(full, label)

    @Slot(str, int)
    def startSimulator(self, host: str, port: int) -> None:
        if self._local_mock_server is not None and self._local_mock_server.is_running:
            self._append_log("本地 TCP 模拟桥已经在运行。")
            return

        server = MockBridgeServer(host=host or "0.0.0.0", port=port)
        try:
            server.start()
        except Exception as exc:
            self.logAppended.emit(f"启动本地 TCP 模拟桥失败: {exc}")
            return

        self._local_mock_server = server
        self._simRunning = True
        self._append_log(f"本地 TCP 模拟桥已启动: {server.host}:{server.port}")
        self._updateSimStatus()

    @Slot()
    def stopSimulator(self) -> None:
        if self._local_mock_server is None:
            return

        if self.controller.bridge_kind == LinkKind.TCP and self.controller.bridge is not None:
            self.controller.disconnect_bridge(silent=True)

        self._local_mock_server.stop()
        self._local_mock_server = None
        self._simRunning = False
        self._append_log("本地 TCP 模拟桥已停止。")
        self._updateSimStatus()

    @Slot()
    def cleanupOnClose(self) -> None:
        self.controller.disconnect_bridge(silent=True)
        if self._local_mock_server is not None:
            self._local_mock_server.stop()
            self._local_mock_server = None

    def _updateSimStatus(self) -> None:
        if self._local_mock_server is not None and self._local_mock_server.is_running:
            self._simStatusText = f"本地模拟桥运行中: {self._local_mock_server.host}:{self._local_mock_server.port}"
        else:
            self._simStatusText = "本地模拟桥未启动"
        self.simStatusChanged.emit()

    def _on_snapshot_ready(self, result: SnapshotResult) -> None:
        self.latest.update(result.payload)
        self._updatedText = f"最近更新: {datetime.now():%Y-%m-%d %H:%M:%S}"
        self._summaryText = self._build_summary()
        self._append_log(f"{result.label}，共收到 {len(result.payload)} 个字段")
        self.dataChanged.emit()

    def _on_info(self, message: str) -> None:
        self._append_log(message)

    def _on_error(self, message: str) -> None:
        self._updatedText = "最近更新: 读取失败"
        self.dataChanged.emit()
        self._append_log(f"错误: {message}")

    def _on_status_changed(self, text: str, state: str) -> None:
        self._statusPillText = text
        self._statusPillState = state
        self.statusChangedSignal.emit()

    def _on_busy_changed(self, busy: bool) -> None:
        self.statusChangedSignal.emit()
        if busy:
            self._append_log("正在读取数据...")

    def _append_log(self, message: str) -> None:
        self.logAppended.emit(f"[{datetime.now():%H:%M:%S}] {message}")

    def _build_summary(self) -> str:
        voltage_mv = self.latest.get("runtime.pack_voltage_mv")
        current_ma = self.latest.get("runtime.current_ma")
        soc = self.latest.get("runtime.relative_soc_percent")
        delta_mv = self.latest.get("runtime.cell_delta_mv", 0)
        mode = self.latest.get("flags.battery_status_hex", "--")
        if voltage_mv is None or current_ma is None or soc is None:
            return "连接后将显示总压、电流、SOC、压差和安全状态等关键摘要。"

        if current_ma > 0:
            direction = "充电"
        elif current_ma < 0:
            direction = "放电"
        else:
            direction = "静置"

        return (
            f"当前总压 {float(voltage_mv) / 1000:.3f} V，"
            f"电流 {float(current_ma) / 1000:.2f} A（{direction}），"
            f"SOC {soc}%，压差 {delta_mv} mV，安全状态 {mode}。"
        )

