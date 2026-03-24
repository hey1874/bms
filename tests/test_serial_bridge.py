from __future__ import annotations

import json

from bmbus_host.bridges.serial import SerialJsonBridge


class _FakeSerial:
    def __init__(self, lines: list[bytes]) -> None:
        self._lines = list(lines)

    def readline(self) -> bytes:
        if not self._lines:
            return b""
        return self._lines.pop(0)



def test_serial_bridge_ignores_logs_and_does_not_invent_missing_flags() -> None:
    payload = {
        "mfg": "RN",
        "model": "BQ4050-1S",
        "temp_c": 25.5,
        "vol_mv": 3970,
        "cur_ma": 0,
        "avg_cur_ma": 0,
        "soc": 99,
        "asoc": 99,
        "rem_cap_mah": 5741,
        "full_cap_mah": 5800,
        "design_cap_mah": 5800,
        "cell1_mv": 3970,
        "cycle": 0,
        "soh": 100,
        "status": "0x00C7",
    }
    bridge = SerialJsonBridge(port="COM11", baudrate=115200, timeout_s=0.1, label="USB-TTL")
    bridge._serial = _FakeSerial(
        [
            b"scan i2c bus...\r\n",
            b"found device: 0x0B BQ4050\r\n",
            b"\r\n",
            json.dumps(payload).encode("utf-8") + b"\r\n",
        ]
    )

    snapshot = bridge.read_snapshot(full=True)

    assert snapshot["device.manufacturer_name"] == "RN"
    assert snapshot["device.device_name"] == "BQ4050-1S"
    assert snapshot["runtime.pack_voltage_mv"] == 3970
    assert snapshot["runtime.cell1_mv"] == 3970
    assert snapshot["runtime.cell_delta_mv"] == 0
    assert snapshot["flags.battery_status_hex"] == "0x00C7"
    assert "flags.security_mode" not in snapshot
    assert "flags.chg_fet_on" not in snapshot
    assert "flags.dsg_fet_on" not in snapshot