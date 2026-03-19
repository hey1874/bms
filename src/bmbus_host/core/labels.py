from __future__ import annotations

from typing import Any


FIELD_LABELS = {
    "device.manufacturer_name": "制造商",
    "device.device_name": "芯片型号",
    "device.device_chemistry": "化学体系",
    "device.serial_number": "序列号",
    "device.design_capacity_mah": "设计容量 (mAh)",
    "device.design_voltage_mv": "设计电压 (mV)",
    "device.manufacturer_date": "制造日期",
    "runtime.pack_voltage_mv": "总压 (mV)",
    "runtime.current_ma": "电流 (mA)",
    "runtime.average_current_ma": "平均电流 (mA)",
    "runtime.relative_soc_percent": "SOC (%)",
    "runtime.remaining_capacity_mah": "剩余容量 (mAh)",
    "runtime.full_charge_capacity_mah": "满充容量 (mAh)",
    "runtime.cycle_count": "循环次数",
    "runtime.state_of_health_percent": "SOH (%)",
    "runtime.cell1_mv": "Cell 1 (mV)",
    "runtime.cell2_mv": "Cell 2 (mV)",
    "runtime.cell3_mv": "Cell 3 (mV)",
    "runtime.cell4_mv": "Cell 4 (mV)",
    "runtime.cell_delta_mv": "压差 (mV)",
    "thermal.internal_temp_c": "内部温度 (C)",
    "thermal.ts1_temp_c": "TS1 (C)",
    "thermal.ts2_temp_c": "TS2 (C)",
    "thermal.ts3_temp_c": "TS3 (C)",
    "thermal.ts4_temp_c": "TS4 (C)",
    "thermal.cell_temp_c": "电芯温度 (C)",
    "thermal.fet_temp_c": "FET 温度 (C)",
    "flags.security_mode": "安全状态",
    "flags.chg_fet_on": "充电 FET",
    "flags.dsg_fet_on": "放电 FET",
    "flags.pchg_fet_on": "预充 FET",
    "flags.permanent_failure": "永久故障",
    "flags.safety_mode": "安全模式",
    "flags.sleep_mode": "休眠模式",
    "flags.charge_disabled": "禁止充电",
    "flags.discharge_disabled": "禁止放电",
    "diagnostics.da_pack_voltage_mv": "诊断总压 (mV)",
    "diagnostics.da_bat_voltage_mv": "诊断 BAT 电压 (mV)",
    "diagnostics.da_cell1_current_ma": "Cell 1 电流 (mA)",
    "diagnostics.da_cell2_current_ma": "Cell 2 电流 (mA)",
    "diagnostics.da_cell3_current_ma": "Cell 3 电流 (mA)",
    "diagnostics.da_cell4_current_ma": "Cell 4 电流 (mA)",
    "diagnostics.da_pack_power_cw": "包功率 (cW)",
    "diagnostics.da_average_power_cw": "平均功率 (cW)",
}


SECTION_FIELDS = {
    "概览": [
        "runtime.pack_voltage_mv",
        "runtime.current_ma",
        "runtime.average_current_ma",
        "runtime.relative_soc_percent",
        "runtime.remaining_capacity_mah",
        "runtime.full_charge_capacity_mah",
        "runtime.state_of_health_percent",
        "runtime.cycle_count",
        "flags.security_mode",
        "flags.chg_fet_on",
        "flags.dsg_fet_on",
    ],
    "电芯": [
        "runtime.cell1_mv",
        "runtime.cell2_mv",
        "runtime.cell3_mv",
        "runtime.cell4_mv",
        "runtime.cell_delta_mv",
        "diagnostics.da_cell1_current_ma",
        "diagnostics.da_cell2_current_ma",
        "diagnostics.da_cell3_current_ma",
        "diagnostics.da_cell4_current_ma",
    ],
    "温度": [
        "thermal.internal_temp_c",
        "thermal.ts1_temp_c",
        "thermal.ts2_temp_c",
        "thermal.ts3_temp_c",
        "thermal.ts4_temp_c",
        "thermal.cell_temp_c",
        "thermal.fet_temp_c",
    ],
    "设备": [
        "device.manufacturer_name",
        "device.device_name",
        "device.device_chemistry",
        "device.serial_number",
        "device.design_capacity_mah",
        "device.design_voltage_mv",
        "device.manufacturer_date",
    ],
    "诊断": [
        "diagnostics.da_pack_voltage_mv",
        "diagnostics.da_bat_voltage_mv",
        "diagnostics.da_pack_power_cw",
        "diagnostics.da_average_power_cw",
        "flags.pchg_fet_on",
        "flags.permanent_failure",
        "flags.safety_mode",
        "flags.sleep_mode",
        "flags.charge_disabled",
        "flags.discharge_disabled",
    ],
}


def format_value(value: Any) -> str:
    if isinstance(value, bool):
        return "开启" if value else "关闭"
    if isinstance(value, float):
        return f"{value:.1f}"
    return str(value)


def field_label(key: str) -> str:
    return FIELD_LABELS.get(key, key)
