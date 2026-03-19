from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout


class StatCard(QFrame):
    def __init__(self, title: str, icon: str, accent: str) -> None:
        super().__init__()
        self.setObjectName("StatCard")
        self.setProperty("accent", accent)
        self.setMinimumWidth(220)
        self.setMinimumHeight(120)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(10)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)

        self.icon_bg = QFrame()
        self.icon_bg.setObjectName("StatIconBg")
        self.icon_bg.setFixedSize(40, 40)
        icon_inner_layout = QVBoxLayout(self.icon_bg)
        icon_inner_layout.setContentsMargins(0, 0, 0, 0)
        icon_inner_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.icon_label = QLabel(icon)
        self.icon_label.setObjectName("StatIcon")
        icon_inner_layout.addWidget(self.icon_label)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(1)
        self.title_label = QLabel(title)
        self.title_label.setObjectName("StatTitle")
        self.caption_label = QLabel("等待数据")
        self.caption_label.setObjectName("StatCaption")
        title_layout.addWidget(self.title_label)
        title_layout.addWidget(self.caption_label)

        header_layout.addWidget(self.icon_bg)
        header_layout.addLayout(title_layout)
        header_layout.addStretch(1)

        self.value_label = QLabel("--")
        self.value_label.setObjectName("StatValue")

        layout.addLayout(header_layout)
        layout.addWidget(self.value_label)

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
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setShowGrid(False)
        self.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.horizontalHeader().setObjectName("DataTableHeader")

    def set_rows(self, rows: list[tuple[str, str]]) -> None:
        self.setRowCount(len(rows))
        for row_index, (label, value) in enumerate(rows):
            self.setItem(row_index, 0, QTableWidgetItem(label))
            self.setItem(row_index, 1, QTableWidgetItem(value))
        self.resizeColumnsToContents()