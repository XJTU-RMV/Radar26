# Radar26

西安交通大学笃行战队 RoboMaster 2026 雷达站代码。

本项目面向 RoboMaster 2026 赛季雷达站，覆盖赛场目标定位、信息波/干扰波解调、裁判系统通信、激光反制控制和雷达站可视化界面。代码以实车/实场地部署为目标，默认运行环境为 Linux + conda `lidar` 环境，核心配置集中在 `config/params.yaml`。

> 本仓库为战队技术交流与复现用途代码，不代表 DJI 或 RoboMaster 官方实现。

## 功能概览

- 视觉定位：主相机识别地面机器人装甲板/车辆目标，通过相机外参和场地模型完成像素到赛场坐标的映射。
- 信息波解调：`RX/` 封装 GNU Radio 生成的信息波、干扰波解调链路，解析坐标、状态、密钥等雷达无线链路消息。
- 裁判系统通信：`driver/referee/` 处理裁判系统串口协议、雷达小地图坐标发送、雷达自主决策和机器人交互数据。
- 激光反制：`lisar/` 负责副相机激光检测模块识别、云台控制、阶段化搜索与第三阶段模型检测。
- 可视化界面：`ui/` 提供雷达站运行状态、地图目标、解调状态、反制状态和标定入口的 PyQt 界面。
- 离线验证与调试：`scripts/`、`callibrate/` 提供协议复核、热区可视化、相机标定和地图标定辅助脚本。

## 系统架构

运行时主入口由 `main.py` 和 `main_event_loop.py` 组织，典型数据流如下：

1. 主相机图像进入 `tracker/`，得到机器人类别和图像位置。
2. `transform/` 根据相机内外参、场地模型和关键点配置，将像素位置投影到赛场坐标。
3. `RX/` 从 SDR 解调信息波/干扰波，输出敌方状态、坐标和密钥信息。
4. `main_event_loop.py` 融合视觉、解调和裁判系统状态，维护雷达站运行状态。
5. `driver/referee/` 将小地图坐标、雷达状态、密钥验证和双倍易伤指令发送给裁判系统或己方机器人。
6. `lisar/` 根据比赛阶段、裁判系统状态和副相机检测结果控制激光云台执行反制。
7. `ui/` 读取运行状态并提供可视化监控和交互控制。

## 项目结构

```text
.
├── main.py                 # 命令行运行入口
├── main_event_loop.py      # 雷达站主事件循环与多线程状态聚合
├── config/                 # 比赛参数、模型路径、相机参数、地图关键点
├── RX/                     # GNU Radio 信息波/干扰波解调封装
├── driver/
│   ├── hik_camera/         # 海康工业相机封装
│   ├── motor/              # 激光云台底层控制工程
│   └── referee/            # 裁判系统串口协议与消息定义
├── tracker/                # 主相机目标检测、跟踪和卡尔曼滤波
├── transform/              # 像素坐标到赛场坐标的几何映射
├── lisar/                  # 激光检测模块识别、搜索策略和反制控制
│   ├── common/             # 反制通用组件
│   ├── easy/               # 基于传统视觉的检测方案
│   └── difficulty/         # 基于 YOLO26 的第三阶段检测方案
├── ui/                     # PyQt 雷达站监控界面
├── callibrate/             # 相机外参和地图点标定工具
├── model/                  # 模型封装与本地 YOLO26 代码
├── weights/                # TensorRT / PyTorch 模型权重
├── docs/                   # 协议映射与技术说明
└── scripts/                # 离线验证和可视化脚本
```

## 运行环境

建议在已配置硬件驱动的 Linux 主机上运行：

- conda 环境：`lidar`
- Python：建议 3.10 系列
- CUDA / TensorRT：用于 `.engine` 模型推理
- PyQt5：用于雷达站界面
- GNU Radio / PlutoSDR：用于信息波和干扰波解调
- 海康工业相机 SDK：用于主相机和副相机取流
- 串口设备：用于裁判系统和激光云台通信

安装 Python 依赖：

```bash
conda activate lidar
pip install -r requirements.txt
```

不同工控机的 CUDA、TensorRT、相机 SDK、GNU Radio 和 SDR 驱动版本可能不同，部署时应先确认这些系统级依赖已经可用。

## 快速启动

启动图形界面：

```bash
conda activate lidar
python -m ui.radar_monitor_window
```

或使用仓库脚本：

```bash
bash start.sh
```

直接启动主流程示例：

```bash
python main.py \
  --faction red \
  --enable_vision_localization \
  --enable_laser_tracking \
  --enable_referee \
  --enable_demod
```

单独启动解调调试：

```bash
python -m RX.run_demod --side red --level base
```

常用运行开关也可以在 `config/params.yaml` 中配置，包括阵营、相机启用状态、裁判系统串口、解调监听端口、模型路径、相机内外参和反制策略。

## 关键配置

- `faction`：己方阵营，支持 `red` / `blue`。
- `enable_vision_localization`：是否启用主相机视觉定位。
- `enable_laser_tracking`：是否启用副相机激光反制链路。
- `enable_referee`：是否启用裁判系统串口通信。
- `enable_demod`：是否启用信息波/干扰波解调。
- `main_camera` / `sub_camera`：相机采集参数、内参、畸变和录制配置。
- `transform`：场地模型、地图图片和关键点配置。
- `car_detector` / `armor_detector` / `stage3_detector`：检测模型路径和推理阈值。
- `referee`：裁判系统串口、雷达小地图发送周期、机器人交互数据发送策略。

实场地部署前，应重新核对相机外参、场地关键点、模型权重路径、SDR 序列号、串口设备名和云台方向。

## 技术模块

### 视觉定位

`tracker/` 负责目标检测、跟踪和短时滤波，`transform/` 负责把图像坐标转换为赛场坐标。标定相关工具位于 `callibrate/`，地图、关键点和场地图像位于 `config/`。

### 信息波与干扰波

`RX/` 保留 GNU Radio 生成代码来源，并在项目侧封装 headless 运行逻辑。`RX/protocol.py`、`RX/runtime.py`、`RX/receiver.py` 和 `RX/sender.py` 负责解析、运行、接收和转发解调结果。

### 裁判系统协议

`driver/referee/messages.py` 定义裁判系统消息结构，`referee_comm.py` 负责串口通信和业务状态维护。`docs/protocol_update_20260626.md` 记录了当前代码与 RoboMaster 2026 通信协议的主要映射关系。

### 激光反制

`lisar/common/` 放置相机取流、云台控制、搜索状态和行为编排等共性组件；`lisar/easy/` 使用传统视觉方案；`lisar/difficulty/` 使用 YOLO26 模型方案处理更复杂阶段。

## 开发与验证

离线协议验证：

```bash
python scripts/verify_protocol_update_20260626.py
```

第三阶段反制验证脚本：

```bash
python scripts/test_referee_countermeasure_difficulty.py
```

热区效果可视化：

```bash
python scripts/visualize_hot_region_effect.py
```

实机验证建议按链路逐步进行：先相机取流和标定，再视觉定位，再 SDR 解调，再裁判系统串口，最后启用激光反制闭环。

## 开源说明

本仓库当前未附带独立 LICENSE 文件。若需要正式二次分发、商业使用或作为其他项目依赖，请先补充明确的开源许可证。

外部贡献建议优先围绕以下方向：

- 完善部署文档和硬件连接说明。
- 将硬件相关路径、串口名和设备序列号配置化。
- 增强离线协议测试和无硬件模拟测试。
- 补充不同场地和不同相机组合下的标定流程。
