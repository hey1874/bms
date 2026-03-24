from __future__ import annotations

import time
from typing import Any

from bmbus_host.core.models import BridgeConfig


class Ft4232Bridge:
    def __init__(self, url: str) -> None:
        self._url = url
        self._i2c_ctrl = None
        self._bq_slave = None
        self._opened = False

    @property
    def label(self) -> str:
        return f"FT4232H I2C ({self._url})"

    def open(self) -> None:
        try:
            import pyftdi.i2c
        except ImportError as exc:
            raise RuntimeError("需要安装 pyftdi 支持，运行 `pip install pyftdi`") from exc

        self._i2c_ctrl = pyftdi.i2c.I2cController()
        # FTDI FT4232H has 4 channels, I2C is usually on interface 1 (A) or 2 (B)
        try:
            self._i2c_ctrl.configure(self._url, frequency=100000)
            # BQ4050 SBS address is typically 0x0B (7-bit)
            self._bq_slave = self._i2c_ctrl.get_port(0x0B)
        except Exception as exc:
            self.close()
            raise RuntimeError(f"FTDI 配置失败或未找到匹配的 FT4232 设备 ({self._url}): {exc}") from exc
        
        self._opened = True

    def close(self) -> None:
        self._opened = False
        if self._i2c_ctrl is not None:
            self._i2c_ctrl.terminate()
            self._i2c_ctrl = None
        self._bq_slave = None

    def _read_word(self, cmd: int) -> int | None:
        if self._bq_slave is None:
            return None
        # SBS uses Little Endian. We read 2 bytes, ignoring optional PEC here.
        # exchange([cmd], 2) performs a Write [cmd], then repeated Start, then Read 2 bytes
        try:
            data = self._bq_slave.exchange([cmd], 2, relaxed=True)
            if len(data) >= 2:
                return data[0] | (data[1] << 8)
        except Exception:
            pass
        return None

    def read_snapshot(self, full: bool = True) -> dict[str, Any]:
        if not self._opened or self._bq_slave is None:
            raise RuntimeError("硬件尚未连接")

        res: dict[str, Any] = {}
        
        v = self._read_word(0x09)
        if v is not None: res["runtime.pack_voltage_mv"] = v

        c = self._read_word(0x0A)
        if c is not None:
            # 16-bit signed integer
            if c > 32767: c -= 65536
            res["runtime.current_ma"] = c

        soc = self._read_word(0x0D)
        if soc is not None: res["runtime.relative_soc_percent"] = soc

        temp_k = self._read_word(0x08)
        if temp_k is not None:
            # temp is in 0.1K, convert to Celsius
            res["thermal.cell_temp_c"] = round((temp_k / 10.0) - 273.15, 1)

        cap = self._read_word(0x0F)
        if cap is not None: res["runtime.remaining_capacity_mah"] = cap

        cyc = self._read_word(0x17)
        if cyc is not None: res["runtime.cycle_count"] = cyc

        # BQ4050 Cell voltages: 0x3C, 0x3D, 0x3E, 0x3F
        c1 = self._read_word(0x3C)
        c2 = self._read_word(0x3D)
        c3 = self._read_word(0x3E)
        c4 = self._read_word(0x3F)
        cells = []
        if c1 is not None and c1 > 0:
            res["runtime.cell1_mv"] = c1
            cells.append(c1)
        if c2 is not None and c2 > 0:
            res["runtime.cell2_mv"] = c2
            cells.append(c2)
        if c3 is not None and c3 > 0:
            res["runtime.cell3_mv"] = c3
            cells.append(c3)
        if c4 is not None and c4 > 0:
            res["runtime.cell4_mv"] = c4
            cells.append(c4)

        if cells:
            res["runtime.cell_delta_mv"] = max(cells) - min(cells)

        status = self._read_word(0x16)
        if status is not None:
            # simple parse
            res["flags.security_mode"] = f"0x{status:04X}"
            res["flags.chg_fet_on"] = bool(status & (1 << 10) or status & (1 << 11)) # Approximation
            res["flags.dsg_fet_on"] = bool(status & (1 << 14) or status & (1 << 15))

        return res
