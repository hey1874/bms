from __future__ import annotations

import json
import threading
import time
from typing import Any

from bmbus_host.bridges.protocol import BridgeProtocolError
from bmbus_host.core.models import BridgeConfig


class SerialJsonBridge:
    def __init__(self, port: str, baudrate: int, timeout_s: float, label: str) -> None:
        self._port = port
        self._baudrate = baudrate
        self._timeout_s = timeout_s
        self._label = label
        self._serial = None
        self._lock = threading.Lock()
        self.is_streaming = True

    @property
    def label(self) -> str:
        return f"{self._label} {self._port}"

    def open(self) -> None:
        if not self._port:
            raise RuntimeError("串口号不能为空。")

        try:
            import serial  # type: ignore[import-not-found]
        except ImportError as exc:
            raise RuntimeError("串口链路需要 pyserial，请先安装 pyserial。") from exc

        try:
            self._serial = serial.Serial(
                port=self._port,
                baudrate=self._baudrate,
                timeout=self._timeout_s,
                write_timeout=self._timeout_s,
            )
            self._serial.reset_input_buffer()
        except Exception as exc:
            raise RuntimeError(f"无法打开串口 {self._port}: {exc}") from exc

    def close(self) -> None:
        if self._serial is not None:
            self._serial.close()
            self._serial = None

    def read_snapshot(self, full: bool = True) -> dict[str, Any]:
        if self._serial is None:
            raise RuntimeError("串口桥尚未连接。")

        deadline = time.time() + self._timeout_s
        while time.time() < deadline:
            try:
                raw = self._serial.readline()
                if not raw:
                    continue
                line = raw.decode("utf-8", errors="ignore").strip()
                if not line or not line.startswith("{") or not line.endswith("}"):
                    continue
                try:
                    data = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise BridgeProtocolError(f"JSON 解析失败: {line} -> {exc}") from exc
                return self._map_to_fields(data)
            except BridgeProtocolError:
                raise
            except Exception:
                continue

        raise BridgeProtocolError("读取下位机数据超时，或未收到有效 JSON 行。")

    def _map_to_fields(self, data: dict[str, Any]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        mapping = {
            "mfg": "device.manufacturer_name",
            "model": "device.device_name",
            "temp_c": "thermal.internal_temp_c",
            "vol_mv": "runtime.pack_voltage_mv",
            "cur_ma": "runtime.current_ma",
            "avg_cur_ma": "runtime.average_current_ma",
            "soc": "runtime.relative_soc_percent",
            "asoc": "runtime.absolute_soc_percent",
            "rem_cap_mah": "runtime.remaining_capacity_mah",
            "full_cap_mah": "runtime.full_charge_capacity_mah",
            "design_cap_mah": "device.design_capacity_mah",
            "design_mv": "device.design_voltage_mv",
            "chg_vol_mv": "runtime.charging_voltage_mv",
            "chg_cur_ma": "runtime.charging_current_ma",
            "cell1_mv": "runtime.cell1_mv",
            "cell2_mv": "runtime.cell2_mv",
            "cell3_mv": "runtime.cell3_mv",
            "cell4_mv": "runtime.cell4_mv",
            "cycle": "runtime.cycle_count",
            "soh": "runtime.state_of_health_percent",
            "status": "flags.battery_status_hex",
        }
        for key, value in data.items():
            result[mapping.get(key, key)] = value

        cell_values = [
            value
            for key, value in result.items()
            if key.startswith("runtime.cell") and key.endswith("_mv") and isinstance(value, (int, float))
        ]
        if cell_values and "runtime.cell_delta_mv" not in result:
            result["runtime.cell_delta_mv"] = max(cell_values) - min(cell_values)

        return result


class BluetoothSerialBridge(SerialJsonBridge):
    def __init__(self, config: BridgeConfig) -> None:
        super().__init__(
            port=config.normalized_bluetooth_port(),
            baudrate=config.bluetooth_baudrate,
            timeout_s=config.bluetooth_timeout_s,
            label="Bluetooth 串口桥",
        )