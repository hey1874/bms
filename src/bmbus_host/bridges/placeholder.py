from __future__ import annotations


class PlaceholderBridge:
    def __init__(self, name: str) -> None:
        self._name = name

    @property
    def label(self) -> str:
        return self._name

    def open(self) -> None:
        raise NotImplementedError(
            "bq4050 使用 SMBus 通信，不能直接通过 TTL/UART 访问。"
            "如果后续需要 USB-TTL、WiFi 或蓝牙接入，需要先加一个 SMBus 桥接端。"
        )

    def close(self) -> None:
        return None

    def read_snapshot(self, full: bool = True) -> dict[str, object]:
        raise NotImplementedError("占位桥接端不支持读取。")
