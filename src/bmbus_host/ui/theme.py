from __future__ import annotations

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QMainWindow


def apply_theme(window: QMainWindow) -> None:
    palette = window.palette()
    palette.setColor(window.backgroundRole(), QColor("#F9FAFB"))
    window.setPalette(palette)

    window.setStyleSheet(
        """
        QWidget {
            background: #F9FAFB;
            color: #111827;
            font-size: 12px;
        }
        QLabel,
        QCheckBox {
            background: transparent;
        }
        QMainWindow {
            background: #F9FAFB;
        }
        QFrame#Sidebar {
            background: #0F172A;
            border-radius: 0px;
        }
        QScrollArea#SidebarScroll,
        QScrollArea#SidebarScroll > QWidget,
        QScrollArea#SidebarScroll > QWidget > QWidget {
            background: #0F172A;
            border: none;
        }
        QWidget#MainContent {
            background: #F9FAFB;
        }
        QLabel#Eyebrow {
            color: #6B7280;
            font-size: 10px;
            font-weight: 800;
            letter-spacing: 1.5px;
            text-transform: uppercase;
        }
        QLabel#SidebarTitle {
            color: #F9FAFB;
            font-size: 20px;
            font-weight: 700;
        }
        QLabel#SidebarDesc, QLabel#TipsLabel {
            color: #94A3B8;
            line-height: 1.4;
            font-size: 11px;
        }
        QLabel#ConfigHint, QLabel#SimStatus {
            color: #94A3B8;
            font-size: 10px;
            line-height: 1.4;
        }
        QFrame#Sidebar QGroupBox {
            background: rgba(255, 255, 255, 0.025);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            margin-top: 8px;
            padding-top: 14px;
            color: #F9FAFB;
            font-weight: 600;
        }
        QGroupBox::title {
            color: #F9FAFB;
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding-left: 8px;
            padding-top: 8px;
        }
        QFrame#Sidebar QLabel,
        QFrame#Sidebar QCheckBox {
            color: #E5E7EB;
        }
        QFrame#Sidebar QLineEdit,
        QFrame#Sidebar QSpinBox,
        QFrame#Sidebar QComboBox,
        QFrame#Sidebar QDoubleSpinBox {
            background: rgba(255, 255, 255, 0.07);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 5px;
            padding: 3px 8px;
            color: #F9FAFB;
            min-height: 28px;
        }
        QFrame#Sidebar QStackedWidget,
        QFrame#Sidebar QStackedWidget QWidget,
        QFrame#Sidebar QFrame {
            background: transparent;
        }
        QComboBox::drop-down,
        QSpinBox::up-button,
        QSpinBox::down-button,
        QDoubleSpinBox::up-button,
        QDoubleSpinBox::down-button {
            border: none;
        }
        QPushButton {
            border: none;
            border-radius: 6px;
            padding: 6px 10px;
            min-height: 34px;
            background: #2563EB;
            color: #FFFFFF;
            font-weight: 600;
        }
        QPushButton:hover {
            background: #1D4ED8;
        }
        QPushButton:pressed {
            background: #1E40AF;
        }
        QPushButton:disabled {
            background: #E5E7EB;
            color: #9CA3AF;
        }
        QFrame#Sidebar QPushButton {
            min-height: 34px;
            padding: 0 10px;
        }
        QFrame#Sidebar QPushButton:disabled {
            background: rgba(255, 255, 255, 0.06);
            color: rgba(229, 231, 235, 0.45);
        }
        QPushButton#GhostButton {
            background: #F3F4F6;
            color: #374151;
        }
        QPushButton#GhostButton:hover {
            background: #E5E7EB;
        }
        QFrame#Sidebar QPushButton#GhostButton {
            background: rgba(255, 255, 255, 0.08);
            color: #E5E7EB;
            border: 1px solid rgba(255, 255, 255, 0.08);
        }
        QFrame#Sidebar QPushButton#GhostButton:hover {
            background: rgba(255, 255, 255, 0.14);
        }
        QFrame#Hero {
            background: #FFFFFF;
            border-radius: 12px;
            border: 1px solid #E5E7EB;
        }
        QLabel#HeroTitle {
            font-size: 18px;
            font-weight: 700;
            color: #111827;
        }
        QLabel#HeroSummary {
            font-size: 13px;
            color: #4B5563;
        }
        QLabel#UpdatedLabel {
            color: #9CA3AF;
            font-size: 10px;
        }
        QLabel#StatusPill {
            border-radius: 8px;
            padding: 2px 8px;
            font-size: 10px;
            font-weight: 600;
        }
        QLabel#StatusPill[state="offline"] {
            background: #F3F4F6;
            color: #6B7280;
        }
        QLabel#StatusPill[state="online"] {
            background: #DCFCE7;
            color: #166534;
        }
        QLabel#StatusPill[state="error"] {
            background: #FEE2E2;
            color: #991B1B;
        }
        QFrame#StatCard {
            background: #FFFFFF;
            border-radius: 12px;
            border: 1px solid #E5E7EB;
        }
        QFrame#StatIconBg {
            border-radius: 8px;
        }
        QFrame#StatCard[accent="blue"] QFrame#StatIconBg {
            background: #EFF6FF;
        }
        QFrame#StatCard[accent="blue"] QLabel#StatIcon {
            color: #2563EB;
        }
        QFrame#StatCard[accent="amber"] QFrame#StatIconBg {
            background: #FFFBEB;
        }
        QFrame#StatCard[accent="amber"] QLabel#StatIcon {
            color: #B45309;
        }
        QFrame#StatCard[accent="green"] QFrame#StatIconBg {
            background: #F0FDF4;
        }
        QFrame#StatCard[accent="green"] QLabel#StatIcon {
            color: #059669;
        }
        QFrame#StatCard[accent="slate"] QFrame#StatIconBg {
            background: #F8FAFC;
        }
        QFrame#StatCard[accent="slate"] QLabel#StatIcon {
            color: #475569;
        }
        QLabel#StatIcon {
            font-size: 15px;
            font-weight: 800;
        }
        QLabel#StatTitle {
            color: #111827;
            font-size: 12px;
            font-weight: 600;
        }
        QLabel#StatCaption {
            color: #6B7280;
            font-size: 10px;
        }
        QLabel#StatValue {
            color: #111827;
            font-size: 22px;
            font-weight: 700;
        }
        QTabWidget::pane {
            border: 1px solid #E5E7EB;
            border-radius: 12px;
            background: #FFFFFF;
            top: -1px;
        }
        QTabBar::tab {
            background: transparent;
            color: #6B7280;
            padding: 7px 14px;
            font-weight: 600;
            border-bottom: 2px solid transparent;
        }
        QTabBar::tab:selected {
            color: #2563EB;
            border-bottom: 2px solid #2563EB;
        }
        QTableWidget {
            background: #FFFFFF;
            border: none;
            alternate-background-color: #F9FAFB;
            gridline-color: transparent;
        }
        QHeaderView::section {
            background: #FFFFFF;
            color: #6B7280;
            border: none;
            padding: 8px;
            font-weight: 600;
            border-bottom: 1px solid #F3F4F6;
            text-transform: uppercase;
            font-size: 9px;
            letter-spacing: 0.5px;
        }
        QFrame#LogPanel {
            background: #FFFFFF;
            border: 1px solid #E5E7EB;
            border-radius: 12px;
        }
        QLabel#SectionTitle {
            font-size: 13px;
            font-weight: 700;
            color: #111827;
        }
        QPlainTextEdit {
            background: #0F172A;
            color: #E2E8F0;
            border-radius: 8px;
            padding: 8px;
            font-family: "Cascadia Code", "Consolas", monospace;
            font-size: 11px;
        }
        """
    )