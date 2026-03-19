from __future__ import annotations

from bq4050_host import MockBq4050Bridge


def test_mock_bridge_returns_expected_keys() -> None:
    bridge = MockBq4050Bridge()
    bridge.open()

    snapshot = bridge.read_snapshot(full=True)

    assert snapshot["device.device_name"] == "BQ4050"
    assert snapshot["device.device_chemistry"] == "LION"
    assert snapshot["flags.security_mode"] == "SEALED"
    assert snapshot["runtime.cell_delta_mv"] >= 0
    assert "diagnostics.da_pack_voltage_mv" in snapshot
