# BQ4050 Qt Host

这是一个面向 `TI bq4050` 的上位机原型，当前优先支持 `模拟设备连接`，并已切换到 `PySide6` 桌面界面，适合先把数据页、轮询节奏和信息组织方式验证清楚。

## 当前能力

- 默认支持 `模拟设备`，无硬件即可联调
- Qt 桌面界面，包含：
  - 顶部状态概览
  - 6 个关键指标卡片
  - 按分组拆开的数据标签页
  - 实时日志区
- 预留 `USB-TTL 串口桥 / WiFi-TCP 桥 / Bluetooth 桥` 入口
- 真实链路当前会明确提示需要 `SMBus 桥接端`

## 重要说明

`bq4050` 本体是 `SMBus` 设备，不是 UART/TTL 设备。

这意味着：

- 不能把 PC 的 USB-TTL 直接接到 `bq4050` 上通信
- 如果你后面要走 USB-TTL、WiFi 或蓝牙，上位机对面必须有一个桥接端
- 桥接端负责把串口/TCP/BLE 数据转换成对 `bq4050` 的 SMBus 访问

当前这版先把上位机和模拟数据链路跑通，后续再把真实桥接协议接进来。

## Conda 环境

环境文件在 [environment.yml](/D:/bms/environment.yml)。

```powershell
cd D:\bms
conda env create -f environment.yml
conda activate bq4050-qt
```

如果环境已经创建过：

```powershell
conda activate bq4050-qt
```

## 运行

```powershell
cd D:\bms
conda run -n bq4050-qt python bq4050_host.py
```

或者先激活环境再运行：

```powershell
cd D:\bms
conda activate bq4050-qt
python bq4050_host.py
```

## 测试

```powershell
cd D:\bms
conda run -n bq4050-qt python -m pytest
```

## 文件

- [bq4050_host.py](/D:/bms/bq4050_host.py)
  - Qt 主界面
  - 模拟设备数据源
  - 真实链路占位入口
- [test_bq4050_host.py](/D:/bms/test_bq4050_host.py)
  - 模拟数据基本校验
