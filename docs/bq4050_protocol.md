# bq4050 协议说明

本文档说明 `TI bq4050` 的原生通信协议，以及它和本项目桥接层之间的关系。

结论先说：

- `bq4050` 原生不是 UART/TTL 设备，而是 `SMBus v1.1` 电池管理器。
- PC 侧的 `USB-TTL / WiFi / Bluetooth` 只能作为“桥接链路”；真正贴近芯片的一侧必须实现 `SMBus master`。
- 本项目上位机当前使用的是自定义 `JSON 行协议`；桥接端负责把该协议转换成 `bq4050 SBS/MAC` 访问。

## 官方资料

- [bq4050 产品页](https://www.ti.com/product/BQ4050)
- [bq4050 Datasheet, Rev. B](https://www.ti.com/lit/ds/symlink/bq4050.pdf)
- [bq4050 Technical Reference Manual, Rev. A](https://www.ti.com/lit/pdf/sluuaq3)

本文档的命令、访问方式和注意事项均以 TI 官方资料为准；如果后续发现你的固件版本或 Data Flash 配置与默认值不同，应以实物配置为准。

## 1. 通信基础

### 1.1 物理和总线层

根据 TI datasheet，`bq4050` 使用：

- `SMBus v1.1`
- 标准 `100 kHz` 通信
- 可选 `400 kHz` 模式
- 可选 `PEC`（Packet Error Checking）

另外，datasheet 还说明：

- 正常模式下，量测/计算/保护决策按 `250 ms` 周期更新
- 单体电压更新周期也是 `0.25 s`
- 当 `SMBC` 和 `SMBD` 同时被拉低超过 `2 s` 时，芯片会进入 SMBus off state；任一线恢复高电平后，约 `1 ms` 内恢复通信

这对桥接端有两个直接约束：

1. 轮询周期没必要小于 `250 ms`
2. SMBus 线不能被 MCU 或桥芯片长期错误拉低

### 1.2 设备地址

TI 将设备地址放在可配置的 SMBus/Data Flash 设置里管理，因此桥接端不应该把地址写死。工程上建议：

- 地址作为配置项保留
- 如果你采用 TI 默认 pack 配置，常见地址通常是 `0x16`
- 实际部署时始终以当前 pack 的 Data Flash 配置为准

上面关于 `0x16` 的说法属于基于 TI 默认工程配置的工程经验，不应当把它当成不可变的协议常量。

### 1.3 安全模式

TRM Chapter 10 定义了三种安全模式：

- `SEALED`
- `UNSEALED`
- `FULL ACCESS`

其中：

- `SEALED` 下仍然允许标准 SBS 读操作，但大多数扩展命令和 Data Flash 写访问会受限
- `UNSEALED` / `FULL ACCESS` 才能做更多配置、密钥、校准和制造相关操作

本项目当前上位机建议默认走“只读监控”路径，优先使用 `SEALED` 也能访问的命令集。

## 2. bq4050 命令模型

`bq4050` 的访问可以分成两层：

- 标准 `SBS` 命令
- 扩展 `MAC` 命令（Manufacturer Access）

### 2.1 标准 SBS 命令

这类命令直接通过 SMBus command code 访问，最适合实时轮询。

常用命令如下：

| 命令 | 地址 | 类型 | 说明 |
| --- | --- | --- | --- |
| `Temperature()` | `0x08` | Read Word | 包温度，单位 `0.1 K` |
| `Voltage()` | `0x09` | Read Word | 总压，单位 `mV` |
| `Current()` | `0x0A` | Read Word | 瞬时电流，单位 `mA`，有符号 |
| `AverageCurrent()` | `0x0B` | Read Word | 平均电流，单位 `mA`，有符号 |
| `RelativeStateOfCharge()` | `0x0D` | Read Word | 相对 SOC，单位 `%` |
| `RemainingCapacity()` | `0x0F` | Read Word | 剩余容量，`mAh` 或 `10 mWh` |
| `FullChargeCapacity()` | `0x10` | Read Word | 满充容量，`mAh` 或 `10 mWh` |
| `CycleCount()` | `0x17` | Read Word | 循环次数 |
| `DesignCapacity()` | `0x18` | Read Word | 设计容量，默认单位 `mAh` |
| `DesignVoltage()` | `0x19` | Read Word | 设计电压，单位 `mV` |
| `ManufacturerDate()` | `0x1B` | Read Word | 制造日期 |
| `SerialNumber()` | `0x1C` | Read Word | 序列号 |
| `ManufacturerName()` | `0x20` | Read Block | 制造商字符串 |
| `DeviceName()` | `0x21` | Read Block | 设备名字符串 |
| `DeviceChemistry()` | `0x22` | Read Block | 化学体系字符串 |
| `CellVoltage4()` | `0x3C` | Read Word | Cell 4 电压 |
| `CellVoltage3()` | `0x3D` | Read Word | Cell 3 电压 |
| `CellVoltage2()` | `0x3E` | Read Word | Cell 2 电压 |
| `CellVoltage1()` | `0x3F` | Read Word | Cell 1 电压 |
| `StateOfHealth()` | `0x4F` | Read Word | SOH 信息 |
| `SafetyAlert()` | `0x50` | Read Block | 安全告警位 |
| `SafetyStatus()` | `0x51` | Read Block | 安全状态位 |
| `PFAlert()` | `0x52` | Read Block | 永久故障告警位 |
| `PFStatus()` | `0x53` | Read Block | 永久故障状态位 |
| `OperationStatus()` | `0x54` | Read Block | 运行状态位 |
| `ChargingStatus()` | `0x55` | Read Block | 充电状态位 |
| `GaugingStatus()` | `0x56` | Read Block | 计量状态位 |
| `ManufacturingStatus()` | `0x57` | Read Block | 制造状态位 |
| `LifetimeDataBlock1..5()` | `0x60..0x64` | Read Block | 寿命统计 |
| `ManufacturerInfo()` | `0x70` | Read Block | 制造信息 |
| `DAStatus1()` | `0x71` | Read Block | 电压/电流/功率诊断 |
| `DAStatus2()` | `0x72` | Read Block | 温度诊断 |

### 2.2 扩展 MAC 命令

TI 把扩展访问放在：

- `0x00 ManufacturerAccess()`
- `0x44 ManufacturerBlockAccess()`

TRM 说明这两种入口是可互通的；你可以把子命令发到其中任一入口，然后从 `ManufacturerData()` 或 `ManufacturerBlockAccess()` 读取返回结果。

本项目后续如果要做：

- 固件/硬件版本读取
- FET 控制
- Seal / Unseal
- 校准
- Authentication / Key
- 寿命数据、AFE 寄存器等扩展数据

都应该走 MAC 路径。

常见 MAC 子命令包括：

| 子命令 | 含义 |
| --- | --- |
| `0x0001` | `DeviceType` |
| `0x0002` | `FirmwareVersion` |
| `0x0003` | `HardwareVersion` |
| `0x0030` | `SealDevice` |
| `0x0035` | `SecurityKeys` |
| `0x0037` | `AuthenticationKey` |
| `0x0041` | `DeviceReset` |
| `0x0050` | `SafetyAlert` |
| `0x0051` | `SafetyStatus` |
| `0x0052` | `PFAlert` |
| `0x0053` | `PFStatus` |
| `0x0054` | `OperationStatus` |
| `0x0055` | `ChargingStatus` |
| `0x0056` | `GaugingStatus` |
| `0x0057` | `ManufacturingStatus` |
| `0x0058` | `AFERegister` |
| `0x0060..0x0062` | `LifetimeDataBlock1..3` |
| `0x0070` | `ManufacturerInfo` |
| `0x0071` | `DAStatus1` |
| `0x0072` | `DAStatus2` |

## 3. 数据格式和换算

TRM Chapter 14 说明扩展返回数据采用小端格式：

- 无符号整数：Little Endian
- 有符号整数：Little Endian，2's complement
- 浮点：Little Endian IEEE754

实现桥接端时建议按下面规则处理：

### 3.1 温度

`Temperature()` 的原始单位是 `0.1 K`，换算成摄氏度：

```text
temp_c = raw / 10 - 273.15
```

`DAStatus2()` 中的内部温度、TS1..TS4、Cell Temp、FET Temp 也应按 TI 文档中的温度格式解析后再转摄氏度。

### 3.2 电流

`Current()` / `AverageCurrent()` 是 `I2`，即 16 位有符号数：

- 充电和放电方向要按 TI 定义解释
- 桥接端不要把有符号值错当成无符号值

### 3.3 容量

`RemainingCapacity()` 和 `FullChargeCapacity()` 的单位受 `BatteryMode()[CAPM]` 影响：

- `CAPM = 0` 时，单位是 `mAh`
- `CAPM = 1` 时，单位是 `10 mWh`

本项目 UI 当前字段名使用 `*_mah`，所以真实桥接端最好：

- 要么保证 pack 工作在 `CAPM = 0`
- 要么在桥接端完成单位统一，转换后再回给上位机

### 3.4 制造日期

`ManufacturerDate()` 的编码公式由 TRM 给出：

```text
day + month * 32 + (year - 1980) * 256
```

桥接端应把原始值解码成标准日期字符串，例如 `2026-03-19`。

## 4. 与本项目字段的推荐映射

当前上位机字段定义在 [labels.py](/D:/bms/src/bmbus_host/core/labels.py)。推荐桥接端按下表组织：

### 4.1 设备信息

| 上位机字段 | 推荐来源 |
| --- | --- |
| `device.manufacturer_name` | `0x20 ManufacturerName()` |
| `device.device_name` | `0x21 DeviceName()` |
| `device.device_chemistry` | `0x22 DeviceChemistry()` |
| `device.serial_number` | `0x1C SerialNumber()` |
| `device.design_capacity_mah` | `0x18 DesignCapacity()` |
| `device.design_voltage_mv` | `0x19 DesignVoltage()` |
| `device.manufacturer_date` | `0x1B ManufacturerDate()` 解码后输出 |

### 4.2 运行数据

| 上位机字段 | 推荐来源 |
| --- | --- |
| `runtime.pack_voltage_mv` | `0x09 Voltage()` |
| `runtime.current_ma` | `0x0A Current()` |
| `runtime.average_current_ma` | `0x0B AverageCurrent()` |
| `runtime.relative_soc_percent` | `0x0D RelativeStateOfCharge()` |
| `runtime.remaining_capacity_mah` | `0x0F RemainingCapacity()` |
| `runtime.full_charge_capacity_mah` | `0x10 FullChargeCapacity()` |
| `runtime.cycle_count` | `0x17 CycleCount()` |
| `runtime.state_of_health_percent` | `0x4F StateOfHealth()` |
| `runtime.cell1_mv` | `0x3F CellVoltage1()` |
| `runtime.cell2_mv` | `0x3E CellVoltage2()` |
| `runtime.cell3_mv` | `0x3D CellVoltage3()` |
| `runtime.cell4_mv` | `0x3C CellVoltage4()` |
| `runtime.cell_delta_mv` | `max(cell1..cell4) - min(cell1..cell4)` |

### 4.3 温度和诊断

| 上位机字段 | 推荐来源 |
| --- | --- |
| `thermal.internal_temp_c` | `0x72 DAStatus2()` |
| `thermal.ts1_temp_c` | `0x72 DAStatus2()` |
| `thermal.ts2_temp_c` | `0x72 DAStatus2()` |
| `thermal.ts3_temp_c` | `0x72 DAStatus2()` |
| `thermal.ts4_temp_c` | `0x72 DAStatus2()` |
| `thermal.cell_temp_c` | `0x72 DAStatus2()` |
| `thermal.fet_temp_c` | `0x72 DAStatus2()` |
| `diagnostics.da_pack_voltage_mv` | `0x71 DAStatus1()` |
| `diagnostics.da_bat_voltage_mv` | `0x71 DAStatus1()` |
| `diagnostics.da_cell1_current_ma` | `0x71 DAStatus1()` |
| `diagnostics.da_cell2_current_ma` | `0x71 DAStatus1()` |
| `diagnostics.da_cell3_current_ma` | `0x71 DAStatus1()` |
| `diagnostics.da_cell4_current_ma` | `0x71 DAStatus1()` |
| `diagnostics.da_pack_power_cw` | `0x71 DAStatus1()` |
| `diagnostics.da_average_power_cw` | `0x71 DAStatus1()` |

### 4.4 标志位

本项目 `flags.*` 字段建议由下列状态块组合解码：

- `0x50 SafetyAlert()`
- `0x51 SafetyStatus()`
- `0x52 PFAlert()`
- `0x53 PFStatus()`
- `0x54 OperationStatus()`
- `0x55 ChargingStatus()`
- `0x56 GaugingStatus()`
- `0x57 ManufacturingStatus()`

需要注意：

- `flags.security_mode` 建议从安全模式状态派生，输出 `SEALED / UNSEALED / FULL ACCESS`
- `flags.chg_fet_on / dsg_fet_on / pchg_fet_on` 建议从运行状态/FET 状态位派生
- `flags.permanent_failure` 可由 `PFStatus` 或等效 PF 位派生
- `flags.safety_mode` 可由 `SafetyStatus` 非零或等效安全位派生
- `flags.sleep_mode` 建议从 `OperationStatus()` 的休眠相关位派生
- `flags.charge_disabled / discharge_disabled` 应优先根据真实禁止状态位推导，而不是单纯根据电流方向猜测

这里之所以写“建议来源”，是因为 TI 在多个状态块里会提供相近语义；最终桥接端应以你选定的固件配置和验证结果为准。

## 5. 建议的桥接端读取策略

为了适配当前上位机的“自动轮询 / 完整读取”两种模式，建议桥接端这样分层：

### 5.1 快速轮询

建议每 `0.5 s ~ 1.0 s` 读取一次：

- `0x09 Voltage()`
- `0x0A Current()`
- `0x0B AverageCurrent()`
- `0x0D RelativeStateOfCharge()`
- `0x0F RemainingCapacity()`
- `0x10 FullChargeCapacity()`
- `0x3C..0x3F CellVoltage1..4()`
- 必要时加 `0x54 OperationStatus()`

### 5.2 完整快照

在首次连接、手动刷新或诊断页面中读取：

- 设备信息：`0x18 0x19 0x1B 0x1C 0x20 0x21 0x22`
- 运行信息：快速轮询全套
- 状态块：`0x50..0x57`
- 诊断块：`0x71 0x72`
- 可选寿命块：`0x60..0x64`

## 6. 与本项目桥接协议的关系

本项目上位机并不直接说 SMBus，而是说一层统一 JSON 协议，定义在：

- [protocol.py](/D:/bms/src/bmbus_host/bridges/protocol.py)
- [server.py](/D:/bms/src/bmbus_host/bridges/server.py)

当前命令只有：

- `hello`
- `read_snapshot`
- `ping`

因此真实桥接端的职责可以概括为：

1. 接收上位机 `read_snapshot(full=...)`
2. 按本文件定义去访问 `bq4050 SBS/MAC`
3. 做单位换算和字段组装
4. 回传本项目定义的字段名，例如 `runtime.pack_voltage_mv`

也就是说：

- 上位机协议是项目自定义的
- 芯片协议是 TI 的 `SMBus/SBS/MAC`
- 中间桥接端负责翻译这两层

## 7. 开发建议

- 如果是 MCU 桥接，优先选带硬件 I2C/SMBus 主机的芯片，不要真用 TTL 直连 `bq4050`
- 初版先只做只读链路，不要一开始就开放 `Seal / Unseal / FET 控制 / Data Flash 写入`
- 先验证 `0x09/0x0A/0x0D/0x3C..0x3F/0x20..0x22/0x71/0x72`，再扩展状态块和寿命块
- 如果后续改成 BLE，不建议在上位机里直接实现 BLE GATT 解析；更稳的做法仍然是做一个“BLE 侧桥接端”，对上位机继续暴露同一套 JSON 协议

## 8. 当前文档边界

本文档重点是“上位机监控和桥接实现需要的协议骨架”，没有展开以下内容：

- 全部状态位的逐 bit 解释
- 全部 Lifetime Data 块字段定义
- Data Flash 子类表和写入流程
- Authentication 详细交互和密钥管理

如果后面你要接真板，我建议下一步继续补一份：

- `docs/bq4050_bridge_implementation.md`

专门写 MCU/TCP/串口桥的报文流程、状态位映射和异常处理。
