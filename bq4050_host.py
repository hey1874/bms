from __future__ import annotations

import sys
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Any

try:
    from PySide6.QtCore import QObject, Qt, QTimer, Signal
    from PySide6.QtGui import QColor, QFont
    from PySide6.QtWidgets import (
        QApplication,
        QCheckBox,
        QComboBox,
        QDoubleSpinBox,
        QFrame,
        QGridLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QMainWindow,
        QMessageBox,
        QPlainTextEdit,
        QPushButton,
        QSizePolicy,
        QSpacerItem,
        QSplitter,
        QTabWidget,
        QTableWidget,
        QTableWidgetItem,
        QVBoxLayout,
        QWidget,
    )
except ImportError:
    PYSIDE_AVAILABLE = False
else:
    PYSIDE_AVAILABLE = True


class LinkKind(StrEnum):
    MOCK = "mock"
    SERIAL = "serial"
    TCP = "tcp"
    BLUETOOTH = "bluetooth"


@dataclass(slots=True)
class SnapshotResult:
    label: str
    payload: dict[str, Any]


class MockBq4050Bridge:
    def __init__(self) -> None:
        self._opened = False
        self._started_at = time.monotonic()

    @property
    def label(self) -> str:
        return "模拟设备"

    def open(self) -> None:
        self._opened = True

    def close(self) -> None:
        self._opened = False

    def read_snapshot(self, full: bool = True) -> dict[str, Any]:
        if not self._opened:
            raise RuntimeError("模拟设备未连接")

        elapsed = int(time.monotonic() - self._started_at)
        soc = max(45, 82 - (elapsed % 20))
        current_ma = -1250 + (elapsed % 10) * 20
        cells = [3741, 3744, 3742, 3750]
        pack_voltage = sum(cells)
        avg_temp = 25.3 + ((elapsed % 5) * 0.2)

        snapshot = {
            "device.manufacturer_name": "Texas Instruments",
            "device.device_name": "BQ4050",
            "device.device_chemistry": "LION",
            "device.serial_number": "0x1234",
            "device.design_capacity_mah": 4400,
            "device.design_voltage_mv": 14800,
            "device.manufacturer_date": "2024-03-19",
            "runtime.pack_voltage_mv": pack_voltage,
            "runtime.current_ma": current_ma,
            "runtime.average_current_ma": current_ma + 35,
            "runtime.relative_soc_percent": soc,
            "runtime.remaining_capacity_mah": int(4400 * soc / 100),
            "runtime.full_charge_capacity_mah": 4380,
            "runtime.cycle_count": 128,
            "runtime.state_of_health_percent": 98,
            "runtime.cell1_mv": cells[0],
            "runtime.cell2_mv": cells[1],
            "runtime.cell3_mv": cells[2],
            "runtime.cell4_mv": cells[3],
            "runtime.cell_delta_mv": max(cells) - min(cells),
            "thermal.internal_temp_c": round(avg_temp - 0.2, 1),
            "thermal.ts1_temp_c": round(avg_temp + 0.5, 1),
            "thermal.ts2_temp_c": round(avg_temp + 0.3, 1),
            "thermal.ts3_temp_c": round(avg_temp + 0.2, 1),
            "thermal.ts4_temp_c": round(avg_temp + 0.1, 1),
            "thermal.cell_temp_c": round(avg_temp, 1),
            "thermal.fet_temp_c": round(avg_temp + 1.6, 1),
            "flags.security_mode": "SEALED",
            "flags.chg_fet_on": True,
            "flags.dsg_fet_on": True,
            "flags.pchg_fet_on": False,
            "flags.permanent_failure": False,
            "flags.safety_mode": False,
            "flags.sleep_mode": False,
            "flags.charge_disabled": False,
            "flags.discharge_disabled": False,
        }

        if full:
            snapshot.update(
                {
                    "diagnostics.da_pack_voltage_mv": pack_voltage,
                    "diagnostics.da_bat_voltage_mv": pack_voltage - 80,
                    "diagnostics.da_cell1_current_ma": current_ma,
                    "diagnostics.da_cell2_current_ma": current_ma - 10,
                    "diagnostics.da_cell3_current_ma": current_ma + 5,
                    "diagnostics.da_cell4_current_ma": current_ma - 15,
                    "diagnostics.da_pack_power_cw": int(pack_voltage * current_ma / 1000),
                    "diagnostics.da_average_power_cw": int(pack_voltage * (current_ma + 35) / 1000),
                }
            )

        return snapshot


class PlaceholderBridge:
    def __init__(self, name: str) -> None:
        self._name = name

    @property
    def label(self) -> str:
        return self._name

    def open(self) -> None:
        raise NotImplementedError(
            "bq4050 是 SMBus 设备，不是 UART。当前先用模拟设备验证界面；真实链路需要 SMBus 桥接端。"
        )

    def close(self) -> None:
        return None


def build_bridge(kind: LinkKind) -> MockBq4050Bridge | PlaceholderBridge:
    if kind == LinkKind.MOCK:
        return MockBq4050Bridge()
    if kind == LinkKind.SERIAL:
        return PlaceholderBridge("USB-TTL 串口桥")
    if kind == LinkKind.TCP:
        return PlaceholderBridge("WiFi/TCP 桥")
    return PlaceholderBridge("Bluetooth 桥")


FIELD_LABELS = {
    "device.manufacturer_name": "制造商",
    "device.device_name": "芯片型号",
    "device.device_chemistry": "化学体系",
    "device.serial_number": "序列号",
    "device.design_capacity_mah": "设计容量 (mAh)",
    "device.design_voltage_mv": "设计电压 (mV)",
    "device.manufacturer_date": "制造日期",
    "runtime.pack_voltage_mv": "总压 (mV)",
    "runtime.current_ma": "电流 (mA)",
    "runtime.average_current_ma": "平均电流 (mA)",
    "runtime.relative_soc_percent": "SOC (%)",
    "runtime.remaining_capacity_mah": "剩余容量 (mAh)",
    "runtime.full_charge_capacity_mah": "满充容量 (mAh)",
    "runtime.cycle_count": "循环次数",
    "runtime.state_of_health_percent": "SOH (%)",
    "runtime.cell1_mv": "Cell 1 (mV)",
    "runtime.cell2_mv": "Cell 2 (mV)",
    "runtime.cell3_mv": "Cell 3 (mV)",
    "runtime.cell4_mv": "Cell 4 (mV)",
    "runtime.cell_delta_mv": "压差 (mV)",
    "thermal.internal_temp_c": "内部温度 (C)",
    "thermal.ts1_temp_c": "TS1 (C)",
    "thermal.ts2_temp_c": "TS2 (C)",
    "thermal.ts3_temp_c": "TS3 (C)",
    "thermal.ts4_temp_c": "TS4 (C)",
    "thermal.cell_temp_c": "电芯温度 (C)",
    "thermal.fet_temp_c": "FET 温度 (C)",
    "flags.security_mode": "安全状态",
    "flags.chg_fet_on": "充电 FET",
    "flags.dsg_fet_on": "放电 FET",
    "flags.pchg_fet_on": "预充 FET",
    "flags.permanent_failure": "永久故障",
    "flags.safety_mode": "安全模式",
    "flags.sleep_mode": "休眠模式",
    "flags.charge_disabled": "禁止充电",
    "flags.discharge_disabled": "禁止放电",
    "diagnostics.da_pack_voltage_mv": "诊断总压 (mV)",
    "diagnostics.da_bat_voltage_mv": "诊断 BAT 电压 (mV)",
    "diagnostics.da_cell1_current_ma": "Cell 1 电流 (mA)",
    "diagnostics.da_cell2_current_ma": "Cell 2 电流 (mA)",
    "diagnostics.da_cell3_current_ma": "Cell 3 电流 (mA)",
    "diagnostics.da_cell4_current_ma": "Cell 4 电流 (mA)",
    "diagnostics.da_pack_power_cw": "包功率 (cW)",
    "diagnostics.da_average_power_cw": "平均功率 (cW)",
}


SECTION_FIELDS = {
    "概览": [
        "runtime.pack_voltage_mv",
        "runtime.current_ma",
        "runtime.average_current_ma",
        "runtime.relative_soc_percent",
        "runtime.remaining_capacity_mah",
        "runtime.full_charge_capacity_mah",
        "runtime.state_of_health_percent",
        "runtime.cycle_count",
        "flags.security_mode",
        "flags.chg_fet_on",
        "flags.dsg_fet_on",
    ],
    "电芯": [
        "runtime.cell1_mv",
        "runtime.cell2_mv",
        "runtime.cell3_mv",
        "runtime.cell4_mv",
        "runtime.cell_delta_mv",
        "diagnostics.da_cell1_current_ma",
        "diagnostics.da_cell2_current_ma",
        "diagnostics.da_cell3_current_ma",
        "diagnostics.da_cell4_current_ma",
    ],
    "温度": [
        "thermal.internal_temp_c",
        "thermal.ts1_temp_c",
        "thermal.ts2_temp_c",
        "thermal.ts3_temp_c",
        "thermal.ts4_temp_c",
        "thermal.cell_temp_c",
        "thermal.fet_temp_c",
    ],
    "设备": [
        "device.manufacturer_name",
        "device.device_name",
        "device.device_chemistry",
        "device.serial_number",
        "device.design_capacity_mah",
        "device.design_voltage_mv",
        "device.manufacturer_date",
    ],
    "诊断": [
        "diagnostics.da_pack_voltage_mv",
        "diagnostics.da_bat_voltage_mv",
        "diagnostics.da_pack_power_cw",
        "diagnostics.da_average_power_cw",
        "flags.pchg_fet_on",
        "flags.permanent_failure",
        "flags.safety_mode",
        "flags.sleep_mode",
        "flags.charge_disabled",
        "flags.discharge_disabled",
    ],
}


def format_value(value: Any) -> str:
    if isinstance(value, bool):
        return "开启" if value else "关闭"
    if isinstance(value, float):
        return f"{value:.1f}"
    return str(value)


def field_label(key: str) -> str:
    return FIELD_LABELS.get(key, key)


if PYSIDE_AVAILABLE:
    class HostSignals(QObject):
        snapshot_ready = Signal(object)
        info = Signal(str)
        error = Signal(str)


    class StatCard(QFrame):
        def __init__(self, title: str) -> None:
            super().__init__()
            self.setObjectName("StatCard")
            layout = QVBoxLayout(self)
            layout.setContentsMargins(18, 16, 18, 16)
            layout.setSpacing(4)

            self.title_label = QLabel(title)
            self.title_label.setObjectName("StatTitle")
            self.value_label = QLabel("--")
            self.value_label.setObjectName("StatValue")
            self.caption_label = QLabel("等待数据")
            self.caption_label.setObjectName("StatCaption")

            layout.addWidget(self.title_label)
            layout.addWidget(self.value_label)
            layout.addWidget(self.caption_label)

        def update_card(self, value: str, caption: str) -> None:
            self.value_label.setText(value)
            self.caption_label.setText(caption)


    class DataTable(QTableWidget):
        def __init__(self) -> None:
            super().__init__(0, 2)
            self.setHorizontalHeaderLabels(["字段", "值"])
            self.horizontalHeader().setStretchLastSection(True)
            self.verticalHeader().setVisible(False)
            self.setAlternatingRowColors(True)
            self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            self.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
            self.setShowGrid(False)
            self.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        def set_rows(self, rows: list[tuple[str, str]]) -> None:
            self.setRowCount(len(rows))
            for row_index, (label, value) in enumerate(rows):
                self.setItem(row_index, 0, QTableWidgetItem(label))
                self.setItem(row_index, 1, QTableWidgetItem(value))
            self.resizeColumnsToContents()


    class BQ4050MainWindow(QMainWindow):
        def __init__(self) -> None:
            super().__init__()
            self.setWindowTitle("BQ4050 Qt Host")
            self.resize(1360, 860)

            self.bridge: MockBq4050Bridge | PlaceholderBridge | None = None
            self.latest: dict[str, Any] = {}
            self.busy = False
            self.signals = HostSignals()
            self.signals.snapshot_ready.connect(self._on_snapshot_ready)
            self.signals.info.connect(self._on_info)
            self.signals.error.connect(self._on_error)

            self.transport_labels = {
                LinkKind.MOCK: "模拟设备",
                LinkKind.SERIAL: "USB-TTL 串口桥",
                LinkKind.TCP: "WiFi/TCP 桥",
                LinkKind.BLUETOOTH: "Bluetooth 桥",
            }

            self.poll_timer = QTimer(self)
            self.poll_timer.timeout.connect(self._poll_tick)

            self._build_ui()
            self._apply_style()
            self._append_log("界面已就绪，默认建议先连接模拟设备。")

        def _build_ui(self) -> None:
            central = QWidget()
            self.setCentralWidget(central)

            root_layout = QHBoxLayout(central)
            root_layout.setContentsMargins(18, 18, 18, 18)

            splitter = QSplitter(Qt.Orientation.Horizontal)
            root_layout.addWidget(splitter)

            sidebar = self._build_sidebar()
            content = self._build_content()
            splitter.addWidget(sidebar)
            splitter.addWidget(content)
            splitter.setSizes([320, 980])

        def _build_sidebar(self) -> QWidget:
            panel = QFrame()
            panel.setObjectName("Sidebar")
            panel.setMinimumWidth(300)
            layout = QVBoxLayout(panel)
            layout.setContentsMargins(20, 22, 20, 22)
            layout.setSpacing(16)

            eyebrow = QLabel("BQ4050 DESKTOP HOST")
            eyebrow.setObjectName("Eyebrow")
            title = QLabel("模拟数据联调台")
            title.setObjectName("SidebarTitle")
            desc = QLabel("先验证数据组织和页面结构，再接 SMBus 桥接端。")
            desc.setWordWrap(True)
            desc.setObjectName("SidebarDesc")

            layout.addWidget(eyebrow)
            layout.addWidget(title)
            layout.addWidget(desc)

            connection_box = QGroupBox("连接")
            connection_layout = QVBoxLayout(connection_box)
            connection_layout.setSpacing(10)

            self.transport_combo = QComboBox()
            self.transport_combo.addItems(list(self.transport_labels.values()))
            self.transport_combo.setCurrentText(self.transport_labels[LinkKind.MOCK])

            self.auto_poll_checkbox = QCheckBox("自动轮询")
            self.auto_poll_checkbox.setChecked(True)
            self.poll_interval_spin = QDoubleSpinBox()
            self.poll_interval_spin.setRange(0.2, 60.0)
            self.poll_interval_spin.setSingleStep(0.2)
            self.poll_interval_spin.setValue(1.0)
            self.poll_interval_spin.setSuffix(" s")

            interval_row = QHBoxLayout()
            interval_row.addWidget(QLabel("轮询周期"))
            interval_row.addStretch(1)
            interval_row.addWidget(self.poll_interval_spin)

            button_row = QHBoxLayout()
            self.connect_button = QPushButton("连接")
            self.connect_button.clicked.connect(self.connect_bridge)
            self.disconnect_button = QPushButton("断开")
            self.disconnect_button.clicked.connect(self.disconnect_bridge)
            self.disconnect_button.setObjectName("GhostButton")
            button_row.addWidget(self.connect_button)
            button_row.addWidget(self.disconnect_button)

            connection_layout.addWidget(QLabel("链路类型"))
            connection_layout.addWidget(self.transport_combo)
            connection_layout.addWidget(self.auto_poll_checkbox)
            connection_layout.addLayout(interval_row)
            connection_layout.addLayout(button_row)

            actions_box = QGroupBox("采集")
            actions_layout = QVBoxLayout(actions_box)
            self.full_button = QPushButton("读取全量快照")
            self.full_button.clicked.connect(lambda: self.request_snapshot(True, "读取全量快照"))
            self.fast_button = QPushButton("读取实时状态")
            self.fast_button.setObjectName("GhostButton")
            self.fast_button.clicked.connect(lambda: self.request_snapshot(False, "读取实时状态"))
            actions_layout.addWidget(self.full_button)
            actions_layout.addWidget(self.fast_button)

            tips_box = QGroupBox("链路说明")
            tips_layout = QVBoxLayout(tips_box)
            tips = QLabel(
                "bq4050 是 SMBus 芯片。后续若接 USB-TTL、WiFi 或蓝牙，另一端必须有桥接固件把这些链路转换成 SMBus 访问。"
            )
            tips.setWordWrap(True)
            tips.setObjectName("TipsLabel")
            tips_layout.addWidget(tips)

            layout.addWidget(connection_box)
            layout.addWidget(actions_box)
            layout.addWidget(tips_box)
            layout.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
            return panel

        def _build_content(self) -> QWidget:
            panel = QWidget()
            layout = QVBoxLayout(panel)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(14)

            hero = QFrame()
            hero.setObjectName("Hero")
            hero_layout = QVBoxLayout(hero)
            hero_layout.setContentsMargins(22, 20, 22, 20)
            hero_layout.setSpacing(6)

            top_row = QHBoxLayout()
            title = QLabel("数据总览")
            title.setObjectName("HeroTitle")
            self.status_pill = QLabel("未连接")
            self.status_pill.setObjectName("StatusPill")
            top_row.addWidget(title)
            top_row.addStretch(1)
            top_row.addWidget(self.status_pill)

            self.summary_label = QLabel("选择“模拟设备”后连接，即可看到动态数据和页面布局效果。")
            self.summary_label.setWordWrap(True)
            self.summary_label.setObjectName("HeroSummary")
            self.updated_label = QLabel("尚未刷新")
            self.updated_label.setObjectName("UpdatedLabel")

            hero_layout.addLayout(top_row)
            hero_layout.addWidget(self.summary_label)
            hero_layout.addWidget(self.updated_label)
            layout.addWidget(hero)

            cards_layout = QGridLayout()
            cards_layout.setHorizontalSpacing(12)
            cards_layout.setVerticalSpacing(12)

            self.card_voltage = StatCard("总压")
            self.card_current = StatCard("电流")
            self.card_soc = StatCard("SOC")
            self.card_delta = StatCard("压差")
            self.card_temp = StatCard("电芯温度")
            self.card_mode = StatCard("安全状态")

            cards = [
                self.card_voltage,
                self.card_current,
                self.card_soc,
                self.card_delta,
                self.card_temp,
                self.card_mode,
            ]
            for index, card in enumerate(cards):
                cards_layout.addWidget(card, index // 3, index % 3)
            layout.addLayout(cards_layout)

            lower_split = QSplitter(Qt.Orientation.Vertical)
            lower_split.addWidget(self._build_tabs())
            lower_split.addWidget(self._build_log())
            lower_split.setSizes([500, 220])
            layout.addWidget(lower_split, 1)
            return panel

        def _build_tabs(self) -> QWidget:
            self.tabs = QTabWidget()
            self.tables: dict[str, DataTable] = {}
            for section_name in SECTION_FIELDS:
                table = DataTable()
                self.tables[section_name] = table
                self.tabs.addTab(table, section_name)
            return self.tabs

        def _build_log(self) -> QWidget:
            wrapper = QFrame()
            wrapper.setObjectName("LogPanel")
            layout = QVBoxLayout(wrapper)
            layout.setContentsMargins(14, 14, 14, 14)
            layout.setSpacing(8)

            header = QHBoxLayout()
            title = QLabel("事件日志")
            title.setObjectName("SectionTitle")
            clear_button = QPushButton("清空")
            clear_button.setObjectName("GhostButton")
            header.addWidget(title)
            header.addStretch(1)
            header.addWidget(clear_button)

            self.log_edit = QPlainTextEdit()
            self.log_edit.setReadOnly(True)
            clear_button.clicked.connect(self.log_edit.clear)

            layout.addLayout(header)
            layout.addWidget(self.log_edit)
            return wrapper

        def _apply_style(self) -> None:
            palette = self.palette()
            palette.setColor(self.backgroundRole(), QColor("#F3EFE7"))
            self.setPalette(palette)

            self.setStyleSheet(
                """
                QWidget {
                    background: #F3EFE7;
                    color: #17313B;
                    font-family: "Segoe UI", "Microsoft YaHei";
                    font-size: 13px;
                }
                QMainWindow {
                    background: #F3EFE7;
                }
                QFrame#Sidebar {
                    background: #18343F;
                    border-radius: 18px;
                }
                QLabel#Eyebrow {
                    color: #8ECFC9;
                    font-size: 11px;
                    font-weight: 700;
                    letter-spacing: 2px;
                }
                QLabel#SidebarTitle {
                    color: #F6F1E8;
                    font-size: 28px;
                    font-weight: 700;
                }
                QLabel#SidebarDesc, QLabel#TipsLabel {
                    color: #CFE1DF;
                    line-height: 1.4;
                }
                QGroupBox {
                    border: 1px solid rgba(24, 52, 63, 0.12);
                    border-radius: 16px;
                    margin-top: 12px;
                    padding-top: 14px;
                    background: rgba(255, 255, 255, 0.7);
                    font-weight: 600;
                }
                QFrame#Sidebar QGroupBox {
                    background: rgba(255, 255, 255, 0.06);
                    border: 1px solid rgba(255, 255, 255, 0.08);
                    color: #F6F1E8;
                }
                QFrame#Sidebar QComboBox,
                QFrame#Sidebar QDoubleSpinBox {
                    background: rgba(255, 255, 255, 0.12);
                    border: 1px solid rgba(255, 255, 255, 0.12);
                    border-radius: 10px;
                    padding: 8px 10px;
                    color: #F6F1E8;
                }
                QCheckBox {
                    spacing: 8px;
                }
                QPushButton {
                    border: none;
                    border-radius: 12px;
                    padding: 10px 14px;
                    background: #1C8C85;
                    color: #FFFFFF;
                    font-weight: 700;
                }
                QPushButton:hover {
                    background: #15766F;
                }
                QPushButton#GhostButton {
                    background: #F0E5D6;
                    color: #18343F;
                }
                QPushButton#GhostButton:hover {
                    background: #E6D7C1;
                }
                QFrame#Hero {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #FFF7E8, stop:1 #E9F6F3);
                    border-radius: 20px;
                    border: 1px solid rgba(23, 49, 59, 0.08);
                }
                QLabel#HeroTitle {
                    font-size: 26px;
                    font-weight: 700;
                    color: #18343F;
                }
                QLabel#HeroSummary {
                    font-size: 14px;
                    color: #34535E;
                }
                QLabel#UpdatedLabel {
                    color: #6E7F84;
                    font-size: 12px;
                }
                QLabel#StatusPill {
                    background: #18343F;
                    color: #FFFFFF;
                    border-radius: 12px;
                    padding: 6px 12px;
                    font-weight: 700;
                }
                QFrame#StatCard {
                    background: #FFFDFC;
                    border-radius: 18px;
                    border: 1px solid rgba(23, 49, 59, 0.08);
                }
                QLabel#StatTitle {
                    color: #6C8088;
                    font-size: 12px;
                    font-weight: 700;
                }
                QLabel#StatValue {
                    color: #17313B;
                    font-size: 28px;
                    font-weight: 700;
                }
                QLabel#StatCaption {
                    color: #73878D;
                    font-size: 12px;
                }
                QTabWidget::pane {
                    border: 1px solid rgba(23, 49, 59, 0.08);
                    border-radius: 16px;
                    background: #FFFDFC;
                    top: -1px;
                }
                QTabBar::tab {
                    background: #EAE2D5;
                    color: #34535E;
                    padding: 10px 16px;
                    border-top-left-radius: 12px;
                    border-top-right-radius: 12px;
                    margin-right: 4px;
                    font-weight: 600;
                }
                QTabBar::tab:selected {
                    background: #FFFDFC;
                    color: #17313B;
                }
                QTableWidget {
                    background: #FFFDFC;
                    border: none;
                    gridline-color: transparent;
                    alternate-background-color: #F7F2EA;
                }
                QHeaderView::section {
                    background: #F0E5D6;
                    color: #17313B;
                    border: none;
                    padding: 10px 8px;
                    font-weight: 700;
                }
                QFrame#LogPanel {
                    background: #FFFDFC;
                    border: 1px solid rgba(23, 49, 59, 0.08);
                    border-radius: 16px;
                }
                QLabel#SectionTitle {
                    font-size: 15px;
                    font-weight: 700;
                }
                QPlainTextEdit {
                    background: #152E38;
                    color: #D9F3EE;
                    border-radius: 12px;
                    border: none;
                    padding: 10px;
                    font-family: Consolas, "Cascadia Mono";
                }
                """
            )

        def connect_bridge(self) -> None:
            try:
                self.disconnect_bridge(silent=True)
                self.bridge = build_bridge(self._selected_kind())
                self.bridge.open()
                self.status_pill.setText("在线")
                self.summary_label.setText("链路已建立。可以读取全量快照或保持自动轮询观察数据变化。")
                self._append_log(f"已连接 {self.bridge.label}")
                self.request_snapshot(True, "连接后读取全量快照")
                self._sync_polling()
            except Exception as exc:
                self._show_error(str(exc))

        def disconnect_bridge(self, silent: bool = False) -> None:
            self.poll_timer.stop()
            if self.bridge is not None:
                try:
                    self.bridge.close()
                finally:
                    self.bridge = None
            self.busy = False
            self.status_pill.setText("未连接")
            if not silent:
                self._append_log("连接已关闭")

        def request_snapshot(self, full: bool, label: str) -> None:
            if self.bridge is None:
                self._show_error("尚未建立连接。")
                return
            if self.busy:
                return

            self.busy = True
            self.updated_label.setText("正在读取...")

            def worker() -> None:
                try:
                    payload = self.bridge.read_snapshot(full=full)  # type: ignore[union-attr]
                    self.signals.snapshot_ready.emit(SnapshotResult(label, payload))
                except Exception as exc:
                    self.signals.error.emit(f"{label}失败: {exc}")

            threading.Thread(target=worker, daemon=True).start()

        def _on_snapshot_ready(self, result: SnapshotResult) -> None:
            self.busy = False
            self.latest.update(result.payload)
            self._render_snapshot(result)
            self._sync_polling()

        def _on_info(self, message: str) -> None:
            self._append_log(message)

        def _on_error(self, message: str) -> None:
            self.busy = False
            self.updated_label.setText("读取失败")
            self._show_error(message)

        def _render_snapshot(self, result: SnapshotResult) -> None:
            self.updated_label.setText(f"最近更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            self.summary_label.setText(self._build_summary())
            self._append_log(f"{result.label}完成，共 {len(result.payload)} 项")
            self._render_cards()
            self._render_tables()

        def _render_cards(self) -> None:
            voltage_mv = self.latest.get("runtime.pack_voltage_mv")
            current_ma = self.latest.get("runtime.current_ma")
            soc = self.latest.get("runtime.relative_soc_percent")
            delta_mv = self.latest.get("runtime.cell_delta_mv")
            cell_temp = self.latest.get("thermal.cell_temp_c")
            mode = self.latest.get("flags.security_mode")

            self.card_voltage.update_card("--" if voltage_mv is None else f"{float(voltage_mv) / 1000:.3f} V", "电池包总压")
            self.card_current.update_card("--" if current_ma is None else f"{float(current_ma) / 1000:.2f} A", "负值代表放电")
            self.card_soc.update_card("--" if soc is None else f"{soc}%", "剩余电量估算")
            self.card_delta.update_card("--" if delta_mv is None else f"{delta_mv} mV", "单体一致性")
            self.card_temp.update_card("--" if cell_temp is None else f"{cell_temp:.1f} C", "电芯平均温度")
            self.card_mode.update_card("--" if mode is None else str(mode), "来自标志位信息")

        def _render_tables(self) -> None:
            for section_name, keys in SECTION_FIELDS.items():
                rows: list[tuple[str, str]] = []
                for key in keys:
                    if key in self.latest:
                        rows.append((field_label(key), format_value(self.latest[key])))
                self.tables[section_name].set_rows(rows)

        def _build_summary(self) -> str:
            voltage_mv = self.latest.get("runtime.pack_voltage_mv")
            current_ma = self.latest.get("runtime.current_ma")
            soc = self.latest.get("runtime.relative_soc_percent")
            delta_mv = self.latest.get("runtime.cell_delta_mv")
            mode = self.latest.get("flags.security_mode", "--")
            if voltage_mv is None or current_ma is None or soc is None or delta_mv is None:
                return "模拟设备已连接，等待首帧数据。"
            return (
                f"当前总压 {float(voltage_mv) / 1000:.3f} V，电流 {float(current_ma) / 1000:.2f} A，"
                f"SOC {soc}% ，压差 {delta_mv} mV，安全状态 {mode}。"
            )

        def _sync_polling(self) -> None:
            if self.bridge is None or not self.auto_poll_checkbox.isChecked():
                self.poll_timer.stop()
                return
            self.poll_timer.start(int(self.poll_interval_spin.value() * 1000))

        def _poll_tick(self) -> None:
            if self.bridge is None or self.busy:
                return
            self.request_snapshot(False, "自动轮询刷新")

        def _selected_kind(self) -> LinkKind:
            text = self.transport_combo.currentText()
            for kind, label in self.transport_labels.items():
                if label == text:
                    return kind
            return LinkKind.MOCK

        def _append_log(self, message: str) -> None:
            self.log_edit.appendPlainText(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

        def _show_error(self, message: str) -> None:
            self._append_log(f"错误: {message}")
            QMessageBox.critical(self, "操作失败", message)

        def closeEvent(self, event) -> None:  # type: ignore[override]
            self.disconnect_bridge(silent=True)
            super().closeEvent(event)


def main() -> None:
    if not PYSIDE_AVAILABLE:
        raise SystemExit(
            "PySide6 未安装。请先运行 `conda activate bq4050-qt`，再执行 `python bq4050_host.py`。"
        )

    app = QApplication(sys.argv)
    app.setApplicationName("BQ4050 Qt Host")
    app.setFont(QFont("Segoe UI", 10))
    window = BQ4050MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
