# BQ4050 Qt Host

这是一个面向 `TI bq4050` 的上位机原型。当前已经补齐三类链路的上位机侧接入能力：

- `模拟设备`：内置数据源，无硬件可联调
- `WiFi/TCP 桥`：可直接连接外部 TCP 桥接端
- `USB-TTL / Bluetooth 串口桥`：走统一的 JSON 行协议，串口侧依赖 `pyserial`

同时提供 `本地 TCP 模拟桥`，可以在没有硬件时验证“真实 TCP 链路 + 桥接协议 + 上位机界面”的整条路径。

## 重要说明

`bq4050` 本体是 `SMBus` 设备，不是 UART/TTL 设备。

这意味着：

- 不能把 PC 的 USB-TTL 直接接到 `bq4050` 上通信
- 如果后面要走 USB-TTL、WiFi 或蓝牙，上位机对面必须有一个桥接端
- 桥接端负责把串口/TCP/BLE 数据转换成对 `bq4050` 的 SMBus 访问

## 当前能力

- Qt 桌面界面，支持链路参数配置
- 内置模拟设备
- 本地 TCP 模拟桥，可从界面一键启动/停止
- TCP 桥接读取
- 串口 / 蓝牙串口桥协议接入层
- 自动轮询、完整读取、快速刷新、日志输出

## 统一桥接协议

上位机和桥接端之间使用一行一个 JSON 的请求/响应协议。

请求示例：

```json
{"request_id":"abc123","command":"hello"}
{"request_id":"abc124","command":"read_snapshot","full":true}
```

响应示例：

```json
{"request_id":"abc123","ok":true,"result":{"protocol":"bmbus-bridge/1","bridge":"mock-tcp","device":"BQ4050"}}
{"request_id":"abc124","ok":true,"result":{"runtime.pack_voltage_mv":14977}}
```

当前实现的命令：

- `hello`
- `read_snapshot`
- `ping`

后续 MCU / WiFi / Bluetooth 桥接端只要遵守这套协议，就能直接接入当前上位机。

## Conda 环境

环境文件在 [environment.yml](/D:/bms/environment.yml)。

```powershell
cd D:\bms
conda env update -f environment.yml --prune
conda activate bq4050-qt
```

## 运行上位机

```powershell
cd D:\bms
python -m bq4050_host
```

## 运行独立模拟桥

```powershell
cd D:\bms
python -m bmbus_host.bridge_server --host 127.0.0.1 --port 8855
```

或者安装脚本入口后：

```powershell
pip install -e .
bmbus-bridge-sim --host 127.0.0.1 --port 8855
```

## 无硬件测试方式

1. 直接选择 `模拟设备`
2. 或选择 `WiFi/TCP 桥`
3. 点击界面左侧的 `启动本地模拟桥`
4. 保持 `127.0.0.1:8855`
5. 点击 `连接链路`

这样可以验证 TCP 桥接协议和界面更新逻辑。

## 测试

```powershell
cd D:\bms
python -m pytest
```

当前测试覆盖：

- 内置模拟设备快照
- TCP 桥接从本地模拟桥读取快照