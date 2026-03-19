from __future__ import annotations

import sys


def main() -> None:
    try:
        from PySide6.QtGui import QFont
        from PySide6.QtWidgets import QApplication
    except ImportError as exc:
        raise SystemExit(
            "PySide6 未安装。请先运行 `conda activate bq4050-qt`，再执行 `python -m bq4050_host`。"
        ) from exc

    from bmbus_host.ui import BQ4050MainWindow

    app = QApplication(sys.argv)
    app.setApplicationName("BQ4050 Qt Host")
    app.setFont(QFont("Segoe UI", 10))
    window = BQ4050MainWindow()
    window.show()
    sys.exit(app.exec())
