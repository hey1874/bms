from __future__ import annotations

import sys
from pathlib import Path


def main() -> None:
    try:
        from PySide6.QtGui import QFont, QGuiApplication
        from PySide6.QtQml import QQmlApplicationEngine
    except ImportError as exc:
        raise SystemExit(
            "PySide6 未安装。请先运行 `conda activate bq4050-qt`，再执行 `python -m bmbus_host`。"
        ) from exc

    from bmbus_host.ui.bridge import AppModel

    import os
    os.environ["QT_QUICK_CONTROLS_STYLE"] = "Material"

    # We use QGuiApplication instead of QApplication for QML
    app = QGuiApplication(sys.argv)
    app.setApplicationName("BQ4050 Qt Host")
    font = QFont(app.font())
    font.setPointSize(10)
    app.setFont(font)

    engine = QQmlApplicationEngine()
    
    app_model = AppModel()
    engine.rootContext().setContextProperty("AppModel", app_model)

    qml_file = Path(__file__).parent / "ui" / "qml" / "main.qml"
    engine.load(qml_file.as_posix())

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())