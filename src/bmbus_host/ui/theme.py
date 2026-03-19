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
            font-size: 13px;
        }
        QMainWindow {
            background: #F9FAFB;
        }
        QFrame#Sidebar {
            background: #111827;
            border-radius: 0px;
        }
        QScrollArea#SidebarScroll,
        QScrollArea#SidebarScroll > QWidget,
        QScrollArea#SidebarScroll > QWidget > QWidget {
            background: #111827;
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
            font-size: 22px;
            font-weight: 700;
        }
        QLabel#SidebarDesc, QLabel#TipsLabel {
            color: #9CA3AF;
            line-height: 1.45;
            font-size: 12px;
        }
        QLabel#ConfigHint, QLabel#SimStatus {
            color: #9CA3AF;
            font-size: 11px;
            line-height: 1.4;
        }
        QFrame#Sidebar QGroupBox {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 14px;
            margin-top: 10px;
            padding-top: 16px;
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
            border-radius: 7px;
            padding: 4px 8px;
            color: #F9FAFB;
            min-height: 30px;
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
            border-radius: 8px;
            padding: 8px 12px;
            min-height: 36px;
            background: #3B82F6;
            color: #FFFFFF;
            font-weight: 600;
        }
        QPushButton:hover {
            background: #2563EB;
        }
        QPushButton:pressed {
            background: #1D4ED8;
        }
        QPushButton:disabled {
            background: #E5E7EB;
            color: #9CA3AF;
        }
        QFrame#Sidebar QPushButton {
            min-height: 38px;
            padding: 0 12px;
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
            border-radius: 18px;
            border: 1px solid #E5E7EB;
        }
        QLabel#HeroTitle {
            font-size: 20px;
            font-weight: 700;
            color: #111827;
        }
        QLabel#HeroSummary {
            font-size: 14px;
            color: #4B5563;
        }
        QLabel#UpdatedLabel {
            color: #9CA3AF;
            font-size: 11px;
        }
        QLabel#StatusPill {
            border-radius: 10px;
            padding: 3px 10px;
            font-size: 11px;
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
            border-radius: 18px;
            border: 1px solid #E5E7EB;
        }
        QFrame#StatIconBg {
            border-radius: 10px;
        }
        QFrame#StatCard[accent="blue"] QFrame#StatIconBg {
            background: #EFF6FF;
        }
        QFrame#StatCard[accent="blue"] QLabel#StatIcon {
            color: #3B82F6;
        }
        QFrame#StatCard[accent="amber"] QFrame#StatIconBg {
            background: #FFFBEB;
        }
        QFrame#StatCard[accent="amber"] QLabel#StatIcon {
            color: #D97706;
        }
        QFrame#StatCard[accent="green"] QFrame#StatIconBg {
            background: #F0FDF4;
        }
        QFrame#StatCard[accent="green"] QLabel#StatIcon {
            color: #10B981;
        }
        QFrame#StatCard[accent="slate"] QFrame#StatIconBg {
            background: #F8FAFC;
        }
        QFrame#StatCard[accent="slate"] QLabel#StatIcon {
            color: #64748B;
        }
        QLabel#StatIcon {
            font-size: 16px;
            font-weight: 800;
        }
        QLabel#StatTitle {
            color: #111827;
            font-size: 13px;
            font-weight: 600;
        }
        QLabel#StatCaption {
            color: #6B7280;
            font-size: 11px;
        }
        QLabel#StatValue {
            color: #111827;
            font-size: 24px;
            font-weight: 700;
        }
        QTabWidget::pane {
            border: 1px solid #E5E7EB;
            border-radius: 18px;
            background: #FFFFFF;
            top: -1px;
        }
        QTabBar::tab {
            background: transparent;
            color: #6B7280;
            padding: 8px 16px;
            font-weight: 600;
            border-bottom: 2px solid transparent;
        }
        QTabBar::tab:selected {
            color: #3B82F6;
            border-bottom: 2px solid #3B82F6;
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
            padding: 9px;
            font-weight: 600;
            border-bottom: 1px solid #F3F4F6;
            text-transform: uppercase;
            font-size: 10px;
            letter-spacing: 0.5px;
        }
        QFrame#LogPanel {
            background: #FFFFFF;
            border: 1px solid #E5E7EB;
            border-radius: 18px;
        }
        QLabel#SectionTitle {
            font-size: 14px;
            font-weight: 700;
            color: #111827;
        }
        QPlainTextEdit {
            background: #0F172A;
            color: #E2E8F0;
            border-radius: 12px;
            padding: 10px;
            font-family: "Cascadia Code", "Consolas", monospace;
            font-size: 12px;
        }
        """
    )