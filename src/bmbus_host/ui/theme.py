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
            font-family: "Inter", "Segoe UI", "PingFang SC", "Microsoft YaHei";
            font-size: 14px;
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
            font-size: 11px;
            font-weight: 800;
            letter-spacing: 2px;
            text-transform: uppercase;
        }
        QLabel#SidebarTitle {
            color: #F9FAFB;
            font-size: 24px;
            font-weight: 700;
        }
        QLabel#SidebarDesc, QLabel#TipsLabel {
            color: #9CA3AF;
            line-height: 1.5;
            font-size: 13px;
        }
        QFrame#Sidebar QGroupBox {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            margin-top: 12px;
            padding-top: 20px;
            color: #F9FAFB;
            font-weight: 600;
        }
        /* 强制 QGroupBox 标题颜色，防止被全局 QWidget 样式覆盖 */
        QGroupBox::title {
            color: #F9FAFB;
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding-left: 10px;
            padding-top: 10px;
        }
        QFrame#Sidebar QLabel,
        QFrame#Sidebar QCheckBox {
            color: #E5E7EB;
        }
        QFrame#Sidebar QComboBox,
        QFrame#Sidebar QDoubleSpinBox {
            background: rgba(255, 255, 255, 0.07);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 6px 10px;
            color: #F9FAFB;
        }
        QComboBox::drop-down {
            border: none;
        }
        QPushButton {
            border: none;
            border-radius: 10px;
            padding: 10px 16px;
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
        QPushButton#GhostButton {
            background: #F3F4F6;
            color: #374151;
        }
        QPushButton#GhostButton:hover {
            background: #E5E7EB;
        }
        QFrame#Hero {
            background: #FFFFFF;
            border-radius: 24px;
            border: 1px solid #E5E7EB;
        }
        QLabel#HeroTitle {
            font-size: 22px;
            font-weight: 700;
            color: #111827;
        }
        QLabel#HeroSummary {
            font-size: 15px;
            color: #4B5563;
        }
        QLabel#UpdatedLabel {
            color: #9CA3AF;
            font-size: 12px;
        }
        QLabel#StatusPill {
            border-radius: 12px;
            padding: 4px 12px;
            font-size: 12px;
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
            border-radius: 24px;
            border: 1px solid #E5E7EB;
        }
        QFrame#StatIconBg {
            border-radius: 12px;
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
            font-size: 18px;
            font-weight: 800;
        }
        QLabel#StatTitle {
            color: #111827;
            font-size: 14px;
            font-weight: 600;
        }
        QLabel#StatCaption {
            color: #6B7280;
            font-size: 12px;
        }
        QLabel#StatValue {
            color: #111827;
            font-size: 28px;
            font-weight: 700;
        }
        QTabWidget::pane {
            border: 1px solid #E5E7EB;
            border-radius: 24px;
            background: #FFFFFF;
            top: -1px;
        }
        QTabBar::tab {
            background: transparent;
            color: #6B7280;
            padding: 10px 20px;
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
            padding: 12px;
            font-weight: 600;
            border-bottom: 1px solid #F3F4F6;
            text-transform: uppercase;
            font-size: 11px;
            letter-spacing: 0.5px;
        }
        QFrame#LogPanel {
            background: #FFFFFF;
            border: 1px solid #E5E7EB;
            border-radius: 24px;
        }
        QLabel#SectionTitle {
            font-size: 15px;
            font-weight: 700;
            color: #111827;
        }
        QPlainTextEdit {
            background: #0F172A;
            color: #E2E8F0;
            border-radius: 16px;
            padding: 12px;
            font-family: "JetBrains Mono", "Cascadia Code", "Consolas", monospace;
            font-size: 13px;
        }
        """
    )
