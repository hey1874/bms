from __future__ import annotations

import time
from typing import Any


class MockBq4050Bridge:
    def __init__(self) -> None:
        self._opened = False
        self._started_at = time.monotonic()

    @property
    def label(self) -> str:
        return "模拟设备"

    def open(self) -> None:
        self._opened = True

    def close(self) -> None:
        self._opened = False

    def read_snapshot(self, full: bool = True) -> dict[str, Any]:
        if not self._opened:
            raise RuntimeError("模拟设备尚未连接。")

        elapsed = int(time.monotonic() - self._started_at)
        soc = max(45, 82 - (elapsed % 20))
        current_ma = -1250 + (elapsed % 10) * 20
        cells = [3741, 3744, 3742, 3750]
        pack_voltage = sum(cells)
        average_temp_c = 25.3 + ((elapsed % 5) * 0.2)

        snapshot: dict[str, Any] = {
            "device.manufacturer_name": "Texas Instruments",
            "device.device_name": "BQ4050",
            "device.device_chemistry": "LION",
            "device.serial_number": "0x1234",
            "device.design_capacity_mah": 4400,
            "device.design_voltage_mv": 14800,
            "device.manufacturer_date": "2024-03-19",
            "runtime.pack_voltage_mv": pack_voltage,
            "runtime.current_ma": current_ma,
            "runtime.average_current_ma": current_ma + 35,
            "runtime.relative_soc_percent": soc,
            "runtime.remaining_capacity_mah": int(4400 * soc / 100),
            "runtime.full_charge_capacity_mah": 4380,
            "runtime.cycle_count": 128,
            "runtime.state_of_health_percent": 98,
            "runtime.cell1_mv": cells[0],
            "runtime.cell2_mv": cells[1],
            "runtime.cell3_mv": cells[2],
            "runtime.cell4_mv": cells[3],
            "runtime.cell_delta_mv": max(cells) - min(cells),
            "thermal.internal_temp_c": round(average_temp_c - 0.2, 1),
            "thermal.ts1_temp_c": round(average_temp_c + 0.5, 1),
            "thermal.ts2_temp_c": round(average_temp_c + 0.3, 1),
            "thermal.ts3_temp_c": round(average_temp_c + 0.2, 1),
            "thermal.ts4_temp_c": round(average_temp_c + 0.1, 1),
            "thermal.cell_temp_c": round(average_temp_c, 1),
            "thermal.fet_temp_c": round(average_temp_c + 1.6, 1),
            "flags.security_mode": "SEALED",
            "flags.chg_fet_on": True,
            "flags.dsg_fet_on": True,
            "flags.pchg_fet_on": False,
            "flags.permanent_failure": False,
            "flags.safety_mode": False,
            "flags.sleep_mode": False,
            "flags.charge_disabled": False,
            "flags.discharge_disabled": False,
        }

        if full:
            snapshot.update(
                {
                    "diagnostics.da_pack_voltage_mv": pack_voltage,
                    "diagnostics.da_bat_voltage_mv": pack_voltage - 80,
                    "diagnostics.da_cell1_current_ma": current_ma,
                    "diagnostics.da_cell2_current_ma": current_ma - 10,
                    "diagnostics.da_cell3_current_ma": current_ma + 5,
                    "diagnostics.da_cell4_current_ma": current_ma - 15,
                    "diagnostics.da_pack_power_cw": int(pack_voltage * current_ma / 1000),
                    "diagnostics.da_average_power_cw": int(pack_voltage * (current_ma + 35) / 1000),
                }
            )

        return snapshot
