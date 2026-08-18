# RoboMaster 2026 通信协议 V2.0.0 对照表

来源：`role/UTF-8__RoboMaster 2026 机甲大师高校系列赛通信协议 V2.0.0（20260626）.pdf_by_PaddleOCR-VL-1.6.md`

## 基础帧格式

裁判系统串口帧保持为：

| 字段 | 长度 | 当前代码 |
| --- | ---: | --- |
| frame_header | 5 bytes | `driver/referee/messages.py::RefereeGenericMessage` |
| cmd_id | 2 bytes | little endian `uint16` |
| data | n bytes | `data_length` 指定 |
| frame_tail | 2 bytes | CRC16，整包校验 |

frame_header：

| 字段 | 长度 | 说明 |
| --- | ---: | --- |
| SOF | 1 | 固定 `0xA5` |
| data_length | 2 | data 长度 |
| seq | 1 | 包序号 |
| CRC8 | 1 | 帧头 CRC8 |

## 常规链路命令码

| cmd_id | 数据长度 | 频率/触发 | 当前代码状态 |
| --- | ---: | --- | --- |
| `0x0001` | 11 | 比赛状态，1Hz | `MsgID.GAME_STATUS` 已覆盖；当前只解析比赛类型、阶段、剩余时间 |
| `0x0003` | 20 | 机器人血量，3Hz | `RobotHPData` / `RobotHPMessage` 已覆盖；`RefereeCommManager` 已绑定并保存敌方前哨站/基地血量 |
| `0x0101` | 4 | 场地事件，1Hz | `MsgID.FIELD_EVENT` 枚举存在；当前主链路未绑定 |
| `0x0104` | 3 | 裁判警告，触发/1Hz | `MsgID.REFEREE_WARNING` 枚举存在；当前主链路未绑定 |
| `0x0105` | 3 | 飞镖发射相关，1Hz | `DartStatData` / `DartStatusMessage` 已覆盖 |
| `0x0201` | 17 | 机器人性能体系，10Hz | `RobotStatusData` 已补齐 `bullet_speed_limit`，静态估算 17 字节 |
| `0x0202` | 14 | 底盘缓冲能量/射击热量，10Hz | 枚举存在；当前主链路未绑定 |
| `0x0207` | 7 | 实时射击，触发 | 枚举存在；当前主链路未绑定 |
| `0x0208` | 8 | 允许发弹量与金币，10Hz | 枚举存在；当前主链路未绑定 |
| `0x020A` | 6 | 飞镖选手端指令，3Hz | 枚举存在；当前主链路未绑定 |
| `0x020B` | 40 | 地面机器人位置，1Hz | 枚举存在；当前主链路未绑定 |
| `0x020C` | 2 | 雷达标记进度，1Hz | `RadarMarkProgressData` 已覆盖 |
| `0x020E` | 1 | 雷达自主决策信息同步，1Hz | `RadarInfoData` 已覆盖 |
| `0x0301` | 118 | 机器人交互数据，上限 30Hz | `InteractiveStructMessage` 已覆盖 |
| `0x0305` | 48 | 雷达小地图数据，上限 5Hz | `Radar2ClientData` 已覆盖；发送周期已改为 0.2s |

## 0x020E 雷达自主决策信息同步

协议定义为 1 字节 `radar_info`：

| bit | 说明 | 当前代码 |
| --- | --- | --- |
| 0-1 | 雷达拥有触发双倍易伤机会，至多 2 | `RadarInfoData.double_vulnerability_count` |
| 2 | 对方是否正在被触发双倍易伤 | `RadarInfoData.is_double_vulnerability` |
| 3-4 | 己方加密等级，即对方干扰波难度，1-3 | `RadarInfoData.encryption_level` |
| 5 | 当前是否可以修改密钥 | `RadarInfoData.can_modify_password` |
| 6-7 | 保留 | `RadarInfoData.reserve` |

当前结构体大小静态估算为 1 字节，符合协议。

## 0x0003 机器人血量数据

协议长度为 20 字节：

| 偏移 | 长度 | 字段 | 当前代码 |
| ---: | ---: | --- | --- |
| 0 | 2 | 己方英雄机器人血量 | `RobotHPData.ally_hero_hp` |
| 2 | 2 | 己方工程机器人血量 | `RobotHPData.ally_engineer_hp` |
| 4 | 2 | 己方3号步兵机器人血量 | `RobotHPData.ally_infantry_3_hp` |
| 6 | 2 | 己方4号步兵机器人血量 | `RobotHPData.ally_infantry_4_hp` |
| 8 | 2 | 己方全队总伤害与对方全队总伤害之差 | `RobotHPData.ally_total_damage_delta` |
| 10 | 2 | 己方7号哨兵机器人血量 | `RobotHPData.ally_sentry_hp` |
| 12 | 2 | 己方前哨站血量 | `RobotHPData.ally_outpost_hp` |
| 14 | 2 | 己方基地血量 | `RobotHPData.ally_base_hp` |
| 16 | 2 | 对方前哨站血量 | `RobotHPData.enemy_outpost_hp` |
| 18 | 2 | 对方基地血量 | `RobotHPData.enemy_base_hp` |

当前 `RefereeCommManager` 绑定 `MsgID.ROBOT_HP` 后保存最近一次 `RobotHPMessage`，并暴露 `enemy_outpost_hp` / `enemy_base_hp` 缓存字段。

## 0x0301 机器人交互数据

协议数据段头：

| 偏移 | 长度 | 字段 |
| ---: | ---: | --- |
| 0 | 2 | 子内容 ID |
| 2 | 2 | 发送者 ID |
| 4 | 2 | 接收者 ID |
| 6 | x | 内容数据段，最大 112 字节 |

当前项目使用的子内容 ID：

| 子内容 ID | 长度 | 用途 | 当前代码 |
| --- | ---: | --- | --- |
| `0x0121` | 8 | 雷达自主决策指令 | `RadarDecisionMessage` |
| `0x0222` | 自定义 | 哨兵到雷达 | `Sentry2RadarMessage`，已修正为 `SENTRY_2_RADAR` |
| `0x0233` | 自定义 | 雷达到机器人/哨兵 | `Radar2RobotMessage` |

静态估算：

- `RadarDecisionData`：8 字节，符合 `0x0121`。
- `Radar2RobotData`：112 字节，加 6 字节交互头后 `0x0301` data 为 118 字节，正好达到协议上限。
- `RadarStatusFrame`：108 字节，可以放入 `Radar2RobotData.msg[110]`。
- `RadarLocationFrame`：54 字节，可以放入 `Radar2RobotData.msg[110]`。

## 0x0121 雷达自主决策指令

| 偏移 | 长度 | 字段 | 当前代码 |
| ---: | ---: | --- | --- |
| 0 | 1 | `radar_cmd`，触发双倍易伤请求计数，需单调递增 | `RadarDecisionData.radar_cmd` |
| 1 | 1 | `password_cmd`，1 更新己方密钥，2 验证破解密钥 | `RadarDecisionData.password_cmd` |
| 2-7 | 6 | 密钥 ASCII 字母或数字 | `RadarDecisionData.password_1` ~ `password_6` |

当前结构体大小静态估算为 8 字节，符合协议。

## 0x0305 雷达小地图数据

协议长度为 48 字节，字段为双方英雄、工程、3号步兵、4号步兵、空中机器人、哨兵的 x/y 坐标，单位 cm。

当前代码：

- `Radar2ClientData` 静态估算为 48 字节，符合协议。
- `config/params.yaml` 的 `referee.radar2client.tx_interval` 已从 0.1s 改为 0.2s。
- `RefereeCommManager` 缺省 `radar2client_tx_interval` 已从 0.1s 改为 0.2s。

## 雷达无线链路命令码

| cmd_id | 数据长度 | 频率 | 当前代码 |
| --- | ---: | --- | --- |
| `0x0A01` | 24 | 10Hz | `Location` |
| `0x0A02` | 12 | 10Hz | `HP` |
| `0x0A03` | 10 | 10Hz | `AllowedBullets` |
| `0x0A04` | 8 | 10Hz | `EnemyStatus` |
| `0x0A05` | 41 | 10Hz | `BuffStatus`，已从旧版 36 字节更新 |
| `0x0A06` | 6 | 10Hz | `JammingKey`，ASCII 字母或数字 |

## 0x0A05 新版字段

新版 `0x0A05` 为 41 字节：

| 偏移 | 长度 | 字段 | 当前代码 |
| ---: | ---: | --- | --- |
| 0-6 | 7 | 英雄回血/冷却/防御/负防御/攻击增益 | `BuffStatus.hero` |
| 7-13 | 7 | 工程回血/冷却/防御/负防御/攻击增益 | `BuffStatus.engineer` |
| 14-20 | 7 | 3号步兵回血/冷却/防御/负防御/攻击增益 | `BuffStatus.inf3` |
| 21-27 | 7 | 4号步兵回血/冷却/防御/负防御/攻击增益 | `BuffStatus.inf4` |
| 28-34 | 7 | 哨兵回血/冷却/防御/负防御/攻击增益 | `BuffStatus.sentry` |
| 35 | 1 | 哨兵姿态，1-6 | `BuffStatus.sentry_pose` |
| 36 | 1 | 英雄主要状态 | `BuffStatus.hero_state` |
| 37 | 1 | 工程主要状态 | `BuffStatus.engineer_state` |
| 38 | 1 | 3号步兵主要状态 | `BuffStatus.inf3_state` |
| 39 | 1 | 4号步兵主要状态 | `BuffStatus.inf4_state` |
| 40 | 1 | 哨兵主要状态 | `BuffStatus.sentry_state` |

`BuffStatus.enemy_is_invincible` 由各机器人主要状态派生：状态 0 为可攻击，状态 1/2/3 均视为无法被攻击，并通过 `RadarStatusFrame.enemy_is_invincible` 转发给哨兵。当前 0x0A05 不包含空中机器人主要状态，空中机器人无敌标志置 0。

机器人主要状态：

- 0：存活
- 1：战亡
- 2：无敌但不虚弱
- 3：无敌且虚弱

## 当前验证状态

- 已新增 `scripts/verify_protocol_update_20260626.py`，用于离线复核本页记录的核心协议映射。
- 当前验证脚本已覆盖：
  - RX `0x0A01~0x0A06` payload 解码与长度检查。
  - `0x0A05` 41 字节新版字段。
  - `0x0A06` 密钥进入 `DemodState.jamming_key`。
  - `0x0301 / 0x0121` 密钥验证帧生成，`password_cmd=2`，`password_1~6` 等于解调密钥。
  - `0x020E` 雷达信息同步对 `encryption_level`、`can_modify_password`、`break_key_correct` 的更新。
  - `0x0305` data length 为 48 字节。
  - 直接解析六份 `RX/RX_new/*/*.py` 生成 flowgraph 文件，并确认其中的频点、gain mode、gain、xlating decimation、前级低通、后级低通、quadrature gain、sps、max data length 与项目侧 `FlowgraphSpec` 一致。
  - 检查每个 `FlowgraphSpec.source_path` 是否指向对应 `RX_new` 生成文件，保证参数同步有明确来源。
  - 检查六份 `RX_new` 生成 top_block 的运行约束：均依赖 `Qt.QWidget` / `Qt.QApplication`，`red-base` 无 `uri` 构造参数且固定 `ip:192.168.2.1`，`red-base` / `red-level2` 存在固定 file sink。
  - 扫描 `RX/RX_new/*/*epy_block*.py`，确认 epy block 的 `OTA_PAYLOAD_LEN=15`、`CMD_0A05` payload 长度为 41，并且仍通过 `message_port_pub(self.out_port, pmt.intern(text))` 发布文本结果；当前未通过 `pmt.to_pmt`、`pmt.make_dict` 或 `pmt.init_u8vector` 发布结构化对象或原始字节。
- 当前默认 `python` 环境缺少 `numpy`、`loguru`、`pyserial`：
  - `driver/referee/messages.py` 已内置轻量数值类型兼容层，因此裁判系统结构体和消息打包不再依赖真实 `numpy` 才能导入验证。
  - `scripts/verify_protocol_update_20260626.py` 仍会为 `RX.runtime` 参数/控制链路检查提供最小 fake `numpy`，并为 `RefereeCommManager` 纯逻辑检查提供最小 `loguru` / `serial` 替身。
  - 完整运行环境下应使用真实依赖重新跑同一脚本。

## 当前未完成项

- 尚未在真实 SDR / GNU Radio 环境下启动六组 flowgraph。
- 尚未接入真实裁判系统串口做 `0x0301 / 0x0305` 实发验证。
- 尚未在完整依赖环境下用真实 `numpy`、`loguru`、`pyserial` 跑 `scripts/verify_protocol_update_20260626.py`。
- `RX_new` 目前已同步参数和解析规则，但尚未把 `_HeadlessFlowgraph` 改成直接加载生成代码的 adapter；原因是生成 epy block 输出文本消息，当前项目链路需要结构化 `ProtocolMessage` callback。
- 当前验证脚本已固化该限制：`RX_new` 的 `decoded_out` 消息端口输出仍是文本日志，不是可直接进入 `DemodController / DemodProcessManager` 的结构化消息。
- 直接加载生成 top_block 还存在运行形态差异：生成代码当前是 Qt GUI top_block，不是 headless 后端；并且部分文件固定 URI 或固定 file sink。项目侧因此继续用 `_HeadlessFlowgraph` 承载同一组 `RX_new` 参数，直到设计出明确的 headless adapter。
