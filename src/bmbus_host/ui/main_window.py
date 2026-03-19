from __future__ import annotations

from datetime import datetime
from typing import Any

from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (
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
    QVBoxLayout,
    QWidget,
    QScrollArea,
)

from bmbus_host.core.controller import HostController
from bmbus_host.core.labels import SECTION_FIELDS, field_label, format_value
from bmbus_host.core.models import LinkKind, SnapshotResult
from bmbus_host.ui.theme import apply_theme
from bmbus_host.ui.widgets import DataTable, StatCard


class BQ4050MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("BQ4050 上位机 - BMBus 监控")
        self.setMinimumSize(1100, 720)
        self.resize(1360, 860)

        self.latest: dict[str, Any] = {}
        self.controller = HostController()
        self.controller.snapshot_ready.connect(self._on_snapshot_ready)
        self.controller.info.connect(self._on_info)
        self.controller.error.connect(self._on_error)
        self.controller.status_changed.connect(self._on_status_changed)
        self.controller.busy_changed.connect(self._on_busy_changed)

        self.transport_labels = {
            LinkKind.MOCK: "模拟设备",
            LinkKind.SERIAL: "USB-TTL 串口桥",
            LinkKind.TCP: "WiFi/TCP 桥",
            LinkKind.BLUETOOTH: "Bluetooth 桥",
        }

        self._build_ui()
        apply_theme(self)
        self._set_status_pill("未连接", "offline")
        self._sync_button_state()
        self._append_log("界面已启动，当前默认使用模拟设备进行联调。")

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setHandleWidth(1)
        splitter.setChildrenCollapsible(False)
        splitter.setStyleSheet("QSplitter::handle { background: transparent; }")

        # Sidebar Scroll Area
        sidebar_scroll = QScrollArea()
        sidebar_scroll.setObjectName("SidebarScroll")
        sidebar_scroll.setWidgetResizable(True)
        sidebar_scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        sidebar_scroll.setMinimumWidth(320)
        sidebar_scroll.setMaximumWidth(450)
        
        sidebar_widget = self._build_sidebar()
        sidebar_scroll.setWidget(sidebar_widget)

        # Content Scroll Area
        content_scroll = QScrollArea()
        content_scroll.setWidgetResizable(True)
        content_scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        content_scroll.setWidget(self._build_content())

        splitter.addWidget(sidebar_scroll)
        splitter.addWidget(content_scroll)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([340, 1020])

        root_layout.addWidget(splitter)

    def _build_sidebar(self) -> QWidget:
        panel = QFrame()
        panel.setObjectName("Sidebar")

        # Inner layout for scrolling content
        outer_layout = QVBoxLayout(panel)
        outer_layout.setContentsMargins(12, 12, 12, 12)

        container = QFrame()
        container.setStyleSheet("background: transparent;")
        layout = QVBoxLayout(container)
        layout.setContentsMargins(12, 16, 12, 16)
        layout.setSpacing(24)

        header_layout = QVBoxLayout()
        header_layout.setSpacing(8)
        eyebrow = QLabel("BQ4050 DESKTOP HOST")
        eyebrow.setObjectName("Eyebrow")

        title = QLabel("BMBus 监控系统")
        title.setObjectName("SidebarTitle")

        desc = QLabel("高性能电池管理系统桌面端")
        desc.setObjectName("SidebarDesc")
        
        header_layout.addWidget(eyebrow)
        header_layout.addWidget(title)
        header_layout.addWidget(desc)
        layout.addLayout(header_layout)

        connection_box = QGroupBox("连接配置")
        connection_layout = QVBoxLayout(connection_box)
        connection_layout.setSpacing(12)

        self.transport_combo = QComboBox()
        self.transport_combo.addItems(list(self.transport_labels.values()))
        self.transport_combo.setCurrentText(self.transport_labels[LinkKind.MOCK])

        poll_row = QHBoxLayout()
        self.auto_poll_checkbox = QCheckBox("自动轮询")
        self.auto_poll_checkbox.setChecked(True)
        self.auto_poll_checkbox.toggled.connect(self._push_poll_settings)
        poll_row.addWidget(self.auto_poll_checkbox)
        poll_row.addStretch(1)

        self.poll_interval_spin = QDoubleSpinBox()
        self.poll_interval_spin.setRange(0.2, 60.0)
        self.poll_interval_spin.setSingleStep(0.2)
        self.poll_interval_spin.setValue(1.0)
        self.poll_interval_spin.setSuffix(" s")
        self.poll_interval_spin.valueChanged.connect(self._push_poll_settings)

        interval_row = QHBoxLayout()
        interval_label = QLabel("间隔")
        interval_label.setStyleSheet("color: #9CA3AF; font-size: 13px;")
        interval_row.addWidget(interval_label)
        interval_row.addStretch(1)
        interval_row.addWidget(self.poll_interval_spin)

        button_row = QHBoxLayout()
        button_row.setSpacing(10)
        self.connect_button = QPushButton("连接设备")
        self.connect_button.clicked.connect(self.connect_bridge)

        self.disconnect_button = QPushButton("断开")
        self.disconnect_button.setObjectName("GhostButton")
        self.disconnect_button.clicked.connect(self.disconnect_bridge)
        self.disconnect_button.setFixedWidth(80)

        button_row.addWidget(self.connect_button, 1)
        button_row.addWidget(self.disconnect_button)

        connection_layout.addWidget(QLabel("链路类型"))
        connection_layout.addWidget(self.transport_combo)
        connection_layout.addLayout(poll_row)
        connection_layout.addLayout(interval_row)
        connection_layout.addSpacing(4)
        connection_layout.addLayout(button_row)

        actions_box = QGroupBox("快操作")
        actions_layout = QVBoxLayout(actions_box)
        actions_layout.setSpacing(10)

        self.full_button = QPushButton("同步完整寄存器")
        self.full_button.clicked.connect(lambda: self.controller.request_snapshot(True, "手动完整读取"))

        self.fast_button = QPushButton("刷新核心状态")
        self.fast_button.setObjectName("GhostButton")
        self.fast_button.clicked.connect(lambda: self.controller.request_snapshot(False, "手动快速刷新"))

        actions_layout.addWidget(self.full_button)
        actions_layout.addWidget(self.fast_button)

        tips_label = QLabel(
            "提示: SMBus 协议对时序敏感，在高负载读取时请适当增加轮询间隔以保证链路稳定。"
        )
        tips_label.setWordWrap(True)
        tips_label.setObjectName("TipsLabel")

        layout.addWidget(connection_box)
        layout.addWidget(actions_box)
        layout.addWidget(tips_label)
        layout.addStretch(1)
        
        outer_layout.addWidget(container)
        return panel

    def _build_content(self) -> QWidget:
        panel = QWidget()
        panel.setObjectName("MainContent")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(24)

        hero = QFrame()
        hero.setObjectName("Hero")
        hero_layout = QVBoxLayout(hero)
        hero_layout.setContentsMargins(28, 24, 28, 24)
        hero_layout.setSpacing(12)

        top_row = QHBoxLayout()
        title = QLabel("电池实时摘要")
        title.setObjectName("HeroTitle")

        self.status_pill = QLabel("未连接")
        self.status_pill.setObjectName("StatusPill")

        top_row.addWidget(title)
        top_row.addStretch(1)
        top_row.addWidget(self.status_pill)

        self.summary_label = QLabel("等待设备连接，准备接收 BMBus 遥测数据...")
        self.summary_label.setWordWrap(True)
        self.summary_label.setObjectName("HeroSummary")

        self.updated_label = QLabel("最后同步: N/A")
        self.updated_label.setObjectName("UpdatedLabel")

        hero_layout.addLayout(top_row)
        hero_layout.addWidget(self.summary_label)
        hero_layout.addWidget(self.updated_label)
        layout.addWidget(hero)

        cards_layout = QGridLayout()
        cards_layout.setHorizontalSpacing(16)
        cards_layout.setVerticalSpacing(16)

        self.card_voltage = StatCard("总压", "VOLT", "blue")
        self.card_current = StatCard("电流", "CURR", "amber")
        self.card_soc = StatCard("SOC", "CAP", "green")
        self.card_delta = StatCard("压差", "DIFF", "blue")
        self.card_temp = StatCard("温度", "TEMP", "amber")
        self.card_mode = StatCard("安全", "SAFE", "slate")

        cards = [
            self.card_voltage,
            self.card_current,
            self.card_soc,
            self.card_delta,
            self.card_temp,
            self.card_mode,
        ]
        
        # Grid items will not squeeze beyond their minimum size
        for index, card in enumerate(cards):
            card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            cards_layout.addWidget(card, index // 3, index % 3)
        layout.addLayout(cards_layout)

        # Tab + Log split area
        lower_split = QSplitter(Qt.Orientation.Vertical)
        lower_split.setHandleWidth(12)
        lower_split.setChildrenCollapsible(False)
        lower_split.addWidget(self._build_tabs())
        lower_split.addWidget(self._build_log())
        lower_split.setStretchFactor(0, 3)
        lower_split.setStretchFactor(1, 1)
        lower_split.setSizes([460, 200])
        
        layout.addWidget(lower_split, 1)
        return panel

    def _build_tabs(self) -> QWidget:
        tabs = QTabWidget()
        self.tables: dict[str, DataTable] = {}
        for section_name in SECTION_FIELDS:
            table = DataTable()
            self.tables[section_name] = table
            tabs.addTab(table, section_name)
        return tabs

    def _build_log(self) -> QWidget:
        wrapper = QFrame()
        wrapper.setObjectName("LogPanel")

        layout = QVBoxLayout(wrapper)
        layout.setContentsMargins(20, 18, 20, 20)
        layout.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel("运行日志")
        title.setObjectName("SectionTitle")

        clear_button = QPushButton("清空日志")
        clear_button.setObjectName("GhostButton")
        clear_button.setFixedWidth(80)
        clear_button.setFixedHeight(32)
        clear_button.setStyleSheet("font-size: 12px; padding: 0;")

        header.addWidget(title)
        header.addStretch(1)
        header.addWidget(clear_button)

        self.log_edit = QPlainTextEdit()
        self.log_edit.setReadOnly(True)
        clear_button.clicked.connect(self.log_edit.clear)

        layout.addLayout(header)
        layout.addWidget(self.log_edit)
        return wrapper

    def connect_bridge(self) -> None:
        self.controller.connect_bridge(
            self._selected_kind(),
            self.auto_poll_checkbox.isChecked(),
            self.poll_interval_spin.value(),
        )
        self._sync_button_state()

    def disconnect_bridge(self) -> None:
        self.controller.disconnect_bridge()
        self._sync_button_state()

    def _push_poll_settings(self) -> None:
        self.controller.apply_poll_settings(
            self.auto_poll_checkbox.isChecked(),
            self.poll_interval_spin.value(),
        )

    def _on_snapshot_ready(self, result: SnapshotResult) -> None:
        self.latest.update(result.payload)
        self.updated_label.setText(f"最近更新: {datetime.now():%Y-%m-%d %H:%M:%S}")
        self.summary_label.setText(self._build_summary())
        self._append_log(f"{result.label}，共收到 {len(result.payload)} 个字段")
        self._render_cards()
        self._render_tables()

    def _on_info(self, message: str) -> None:
        self._append_log(message)

    def _on_error(self, message: str) -> None:
        self.updated_label.setText("最近更新: 读取失败")
        self._append_log(f"错误: {message}")
        QMessageBox.critical(self, "连接或读取失败", message)

    def _on_status_changed(self, text: str, state: str) -> None:
        self._set_status_pill(text, state)
        self._sync_button_state()

    def _on_busy_changed(self, busy: bool) -> None:
        self._sync_button_state()
        if busy:
            self._append_log("正在读取数据...")

    def _sync_button_state(self) -> None:
        connected = self.controller.bridge is not None
        busy = self.controller.busy

        self.connect_button.setEnabled((not connected) and (not busy))
        self.disconnect_button.setEnabled(connected)
        self.full_button.setEnabled(connected and (not busy))
        self.fast_button.setEnabled(connected and (not busy))
        self.transport_combo.setEnabled((not connected) and (not busy))

    def _render_cards(self) -> None:
        voltage_mv = self.latest.get("runtime.pack_voltage_mv")
        current_ma = self.latest.get("runtime.current_ma")
        soc = self.latest.get("runtime.relative_soc_percent")
        delta_mv = self.latest.get("runtime.cell_delta_mv")
        cell_temp = self.latest.get("thermal.cell_temp_c")
        mode = self.latest.get("flags.security_mode")

        self.card_voltage.update_card(
            "--" if voltage_mv is None else f"{float(voltage_mv) / 1000:.3f} V",
            "电池包总电压",
        )
        self.card_current.update_card(
            "--" if current_ma is None else f"{float(current_ma) / 1000:.2f} A",
            "负值表示放电",
        )
        self.card_soc.update_card(
            "--" if soc is None else f"{soc}%",
            "剩余电量估算",
        )
        self.card_delta.update_card(
            "--" if delta_mv is None else f"{delta_mv} mV",
            "单体最大压差",
        )
        self.card_temp.update_card(
            "--" if cell_temp is None else f"{cell_temp:.1f} C",
            "电芯温度",
        )
        self.card_mode.update_card(
            "--" if mode is None else str(mode),
            "当前安全状态",
        )

    def _render_tables(self) -> None:
        for section_name, keys in SECTION_FIELDS.items():
            rows = [(field_label(key), format_value(self.latest[key])) for key in keys if key in self.latest]
            self.tables[section_name].set_rows(rows)

    def _build_summary(self) -> str:
        voltage_mv = self.latest.get("runtime.pack_voltage_mv")
        current_ma = self.latest.get("runtime.current_ma")
        soc = self.latest.get("runtime.relative_soc_percent")
        delta_mv = self.latest.get("runtime.cell_delta_mv")
        mode = self.latest.get("flags.security_mode", "--")
        if voltage_mv is None or current_ma is None or soc is None or delta_mv is None:
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

    def _selected_kind(self) -> LinkKind:
        text = self.transport_combo.currentText()
        for kind, label in self.transport_labels.items():
            if label == text:
                return kind
        return LinkKind.MOCK

    def _append_log(self, message: str) -> None:
        self.log_edit.appendPlainText(f"[{datetime.now():%H:%M:%S}] {message}")

    def _set_status_pill(self, text: str, state: str) -> None:
        self.status_pill.setText(text)
        self.status_pill.setProperty("state", state)
        self.style().unpolish(self.status_pill)
        self.style().polish(self.status_pill)

    def closeEvent(self, event: QCloseEvent) -> None:
        self.controller.disconnect_bridge(silent=True)
        super().closeEvent(event)