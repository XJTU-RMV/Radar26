## R 机甲大师 ROBOMASTER

第二十五届全国大学生机器人大赛

ROBOMASTER 2026

机甲大师高校系列赛

通信协议

RoboMaster 组委会 编制

2026年6月 发布

### 修改日志



<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>日期</td><td style='text-align: center; word-wrap: break-word;'>版本</td><td style='text-align: center; word-wrap: break-word;'>修订记录</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>2026.06.26</td><td style='text-align: center; word-wrap: break-word;'>V2.0.0</td><td style='text-align: center; word-wrap: break-word;'>● 修订命令：0x0003，0x0120，0x0201，0x020C，0x020D，0x0301，0x0A05\n● 修订自定义客户端协议中指令：GameStatus，SentryStatusSync，SentryCtrlCommand，AirSupportStatusSync，AirSupportCommand\n● 完善和补充多处描述</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>2026.05.19</td><td style='text-align: center; word-wrap: break-word;'>V1.3.1</td><td style='text-align: center; word-wrap: break-word;'>修订自定义客户端协议中原 MapClickInfoNotify(现拆分为 MapClickInfo与MapClickCmd)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>2026.03.26</td><td style='text-align: center; word-wrap: break-word;'>V1.3.0</td><td style='text-align: center; word-wrap: break-word;'>● 修订命令字：0x0101,0x0305\n● 修订自定义客户端协议中指令：CustomControl，RadarInfoToClient，AirSupportCommand，MapClickInfoNotify，RuneStatusSync，Event，RobotPosition，SentryCtrlCommand，SentryCtrlResult，TechCoreMotionStateSync\n● 修改了自定义客户端 IP 配置方式\n● 补充了自定义客户端 proto 版本信息\n● 明确了波特率和物理接口的对应关系\n● 修复了多处触发式协议频率\n● 完善和补充了多处描述</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>2026.02.09</td><td style='text-align: center; word-wrap: break-word;'>V1.2.0</td><td style='text-align: center; word-wrap: break-word;'>● 修订命令 0x0105,0x0204,0x0209,0x020C,0x020D,0x0309,0x0310\n● 删除命令码 0x0304\n● 修订自定义客户端协议中原 RemoteControl(现拆分为 KeyboardMouseControl与CustomControl)，TechCoreMotionStateSync，RobotModuleStatus，RadarInfoToClient，DartCommand，GlobalUnitStatus，RobotModuleStatus，AirSupportStatusSync，</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>DartSelectTargetStatusSync,\nRobotPerformanceSelectionCommand\n● 自定义客户端新增 CommonCommand 指令\n● 修复了多处描述或命名错误</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>2025.12.18</td><td style='text-align: center; word-wrap: break-word;'>V1.1.0</td><td style='text-align: center; word-wrap: break-word;'>补充雷达无线链路相关说明</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>2025.11.27</td><td style='text-align: center; word-wrap: break-word;'>V1.0.0</td><td style='text-align: center; word-wrap: break-word;'>首次发布</td></tr></table>





### 前言

本通信协议在RMUC与RMUL两项赛事中的适用范围如下：

对于在RMUC与RMUL之间共用的兵种、机制或场地道具等条目，本协议内容对两项赛事均适用；

对于仅适用于某一赛项的兵种、机制或场地道具等条目，默认不适用于另一赛项。

## 目录

修改日志.....1    
前言.....2    
1 串口协议.....4    
1.1 串口协议格式.....4    
1.2 命令码 ID 和常规链路数据说明.....6    
1.3 小地图交互数据.....32    
1.4 图传链路数据说明.....37    
1.5 非链路数据说明.....38    
1.6 雷达无线链路数据说明.....39    
2 自定义客户端协议.....44    
2.1 指令概览.....44    
2.2 详细协议定义.....48    
附录一：CRC 校验代码示例.....75    
附录二：ID 编号说明.....79    
附录三：自定义客户端示例通信代码.....81

### 1串口协议

#### 1.1 串口协议格式

通信方式为串口的部分，性质如下：8位数据位，1位停止位，无硬件流控，无校验位。详细信息见以下表格：

<div style="text-align: center;"><div style="text-align: center;">表1-1 波特率</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>物理接口</td><td style='text-align: center; word-wrap: break-word;'>波特率</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>电源管理模块←→机器人</td><td style='text-align: center; word-wrap: break-word;'>115200</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>自定义控制器←→选手端</td><td style='text-align: center; word-wrap: break-word;'>115200</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>图传发送端←→机器人</td><td style='text-align: center; word-wrap: break-word;'>921600</td></tr></table>

<div style="text-align: center;"><div style="text-align: center;">表 1-2 通信协议格式</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>frame_header</td><td style='text-align: center; word-wrap: break-word;'>cmd_id</td><td style='text-align: center; word-wrap: break-word;'>data</td><td style='text-align: center; word-wrap: break-word;'>frame_tail</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>5-byte</td><td style='text-align: center; word-wrap: break-word;'>2-byte</td><td style='text-align: center; word-wrap: break-word;'>n-byte</td><td style='text-align: center; word-wrap: break-word;'>2-byte, CRC16, 整包校验</td></tr></table>

<div style="text-align: center;"><div style="text-align: center;">表 1-3 frame_header 格式</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>SOF</td><td style='text-align: center; word-wrap: break-word;'>data_length</td><td style='text-align: center; word-wrap: break-word;'>seq</td><td style='text-align: center; word-wrap: break-word;'>CRC8</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>1-byte</td><td style='text-align: center; word-wrap: break-word;'>2-byte</td><td style='text-align: center; word-wrap: break-word;'>1-byte</td><td style='text-align: center; word-wrap: break-word;'>1-byte</td></tr></table>

<div style="text-align: center;"><div style="text-align: center;">表1-4 帧头详细定义</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>域</td><td style='text-align: center; word-wrap: break-word;'>偏移位置</td><td style='text-align: center; word-wrap: break-word;'>大小（字节）</td><td style='text-align: center; word-wrap: break-word;'>详细描述</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>SOF</td><td style='text-align: center; word-wrap: break-word;'>0</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>数据帧起始字节，固定值为 0xA5</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>data_length</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>数据帧中 data 的长度</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>seq</td><td style='text-align: center; word-wrap: break-word;'>3</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>包序号</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>CRC8</td><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>帧头 CRC8 校验</td></tr></table>

裁判系统串口数据链路有三种：常规链路、图传链路、雷达无线链路。

常规链路由裁判系统服务器和主控模块进行数据转发，从电源管理模块的 User 串口收发数据，示意图如下：

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//2bcd5f86-9bcc-48d9-b223-8f6164fbed8c/markdown_1/imgs/img_in_image_box_241_289_962_587.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A40Z%2F-1%2F%2Fc645dcdbdce1fe37a80f8393a27c8664f4b2ecf946fcbe561d0d8aff268ea4d5" alt="Image" width="60%" /></div>


图传链路由裁判系统选手端和图传模块进行数据转发，从图传模块（发送端）的串口接收数据，示意图如下：

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//2bcd5f86-9bcc-48d9-b223-8f6164fbed8c/markdown_1/imgs/img_in_image_box_114_754_1073_1014.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A40Z%2F-1%2F%2Fab49a8aae4f9ad79ebd3f1b66e36166d38be6825e55d833566d033239c3f03b9" alt="Image" width="80%" /></div>


##### 机器人

雷达无线链路由裁判系统信号发射源进行数据发送，从雷达接收电磁波并解析信息。

正常工作状态下，裁判系统数据延迟约为130ms，丢包率小于1%；

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//2bcd5f86-9bcc-48d9-b223-8f6164fbed8c/markdown_1/imgs/img_in_image_box_170_1259_214_1301.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A40Z%2F-1%2F%2F7c1cf53529b199777d1bd162d261edfdb18e7fec15799926d5afe8f335323011" alt="Image" width="3%" /></div>


在赛场网络环境较恶劣时，裁判系统数据延迟约为200ms，丢包率约为3%；

测量数据可能存在误差，数据仅供参考。

#### 1.2 命令码 ID 和常规链路数据说明

<div style="text-align: center;"><div style="text-align: center;">表1-5 命令码ID一览</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>命令码</td><td style='text-align: center; word-wrap: break-word;'>数据段长度</td><td style='text-align: center; word-wrap: break-word;'>说明</td><td style='text-align: center; word-wrap: break-word;'>发送方/接收方</td><td style='text-align: center; word-wrap: break-word;'>所属数据链路</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0x0001</td><td style='text-align: center; word-wrap: break-word;'>11</td><td style='text-align: center; word-wrap: break-word;'>比赛状态数据，固定以 1Hz 频率发送</td><td style='text-align: center; word-wrap: break-word;'>服务器→全体机器人</td><td style='text-align: center; word-wrap: break-word;'>常规链路</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0x0002</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>比赛结果数据，比赛结束触发发送</td><td style='text-align: center; word-wrap: break-word;'>服务器→全体机器人</td><td style='text-align: center; word-wrap: break-word;'>常规链路</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0x0003</td><td style='text-align: center; word-wrap: break-word;'>20</td><td style='text-align: center; word-wrap: break-word;'>机器人血量数据，固定以 3Hz 频率发送</td><td style='text-align: center; word-wrap: break-word;'>服务器→全体机器人</td><td style='text-align: center; word-wrap: break-word;'>常规链路</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0x0101</td><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>场地事件数据，固定以 1Hz 频率发送</td><td style='text-align: center; word-wrap: break-word;'>服务器→己方全体机器人</td><td style='text-align: center; word-wrap: break-word;'>常规链路</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0x0104</td><td style='text-align: center; word-wrap: break-word;'>3</td><td style='text-align: center; word-wrap: break-word;'>裁判警告数据，己方判罚/判负时触发发送，其余时间以 1Hz 频率发送</td><td style='text-align: center; word-wrap: break-word;'>服务器→被判罚方全体机器人</td><td style='text-align: center; word-wrap: break-word;'>常规链路</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0x0105</td><td style='text-align: center; word-wrap: break-word;'>3</td><td style='text-align: center; word-wrap: break-word;'>飞镖发射相关数据，固定以 1Hz 频率发送</td><td style='text-align: center; word-wrap: break-word;'>服务器→己方全体机器人</td><td style='text-align: center; word-wrap: break-word;'>常规链路</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0x0201</td><td style='text-align: center; word-wrap: break-word;'>17</td><td style='text-align: center; word-wrap: break-word;'>机器人性能体系数据，固定以 10Hz 频率发送</td><td style='text-align: center; word-wrap: break-word;'>主控模块→对应机器人</td><td style='text-align: center; word-wrap: break-word;'>常规链路</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0x0202</td><td style='text-align: center; word-wrap: break-word;'>14</td><td style='text-align: center; word-wrap: break-word;'>实时底盘缓冲能量和射击热量数据，固定以 10Hz 频率发送</td><td style='text-align: center; word-wrap: break-word;'>主控模块→对应机器人</td><td style='text-align: center; word-wrap: break-word;'>常规链路</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0x0203</td><td style='text-align: center; word-wrap: break-word;'>16</td><td style='text-align: center; word-wrap: break-word;'>机器人位置数据，固定以 1Hz 频率发送</td><td style='text-align: center; word-wrap: break-word;'>主控模块→对应机器人</td><td style='text-align: center; word-wrap: break-word;'>常规链路</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0x0204</td><td style='text-align: center; word-wrap: break-word;'>8</td><td style='text-align: center; word-wrap: break-word;'>机器人增益和底盘能量数据，固定以 3Hz 频率发送</td><td style='text-align: center; word-wrap: break-word;'>服务器→对应机器人</td><td style='text-align: center; word-wrap: break-word;'>常规链路</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0x0206</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>伤害状态数据，伤害发生后发送</td><td style='text-align: center; word-wrap: break-word;'>主控模块→对应机器人</td><td style='text-align: center; word-wrap: break-word;'>常规链路</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0x0207</td><td style='text-align: center; word-wrap: break-word;'>7</td><td style='text-align: center; word-wrap: break-word;'>实时射击数据，弹丸发射后发送</td><td style='text-align: center; word-wrap: break-word;'>主控模块→对应机器人</td><td style='text-align: center; word-wrap: break-word;'>常规链路</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0x0208</td><td style='text-align: center; word-wrap: break-word;'>8</td><td style='text-align: center; word-wrap: break-word;'>允许发弹量与剩余金币数，固定以10Hz频率发送</td><td style='text-align: center; word-wrap: break-word;'>服务器→己方英雄、步兵、哨兵、空中机器人</td><td style='text-align: center; word-wrap: break-word;'>常规链路</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0x0209</td><td style='text-align: center; word-wrap: break-word;'>5</td><td style='text-align: center; word-wrap: break-word;'>机器人RFID模块状态，固定以3Hz频率发送</td><td style='text-align: center; word-wrap: break-word;'>服务器→己方装有RFID模块的机器人</td><td style='text-align: center; word-wrap: break-word;'>常规链路</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0x020A</td><td style='text-align: center; word-wrap: break-word;'>6</td><td style='text-align: center; word-wrap: break-word;'>飞镖选手端指令数据，固定以3Hz频率发送</td><td style='text-align: center; word-wrap: break-word;'>服务器→己方飞镖机器人</td><td style='text-align: center; word-wrap: break-word;'>常规链路</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0x020B</td><td style='text-align: center; word-wrap: break-word;'>40</td><td style='text-align: center; word-wrap: break-word;'>地面机器人位置数据，固定以1Hz频率发送</td><td style='text-align: center; word-wrap: break-word;'>服务器→己方哨兵机器人</td><td style='text-align: center; word-wrap: break-word;'>常规链路</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0x020C</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>雷达标记进度数据，固定以1Hz频率发送</td><td style='text-align: center; word-wrap: break-word;'>服务器→己方雷达机器人</td><td style='text-align: center; word-wrap: break-word;'>常规链路</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0x020D</td><td style='text-align: center; word-wrap: break-word;'>14</td><td style='text-align: center; word-wrap: break-word;'>哨兵自主决策信息同步，固定以1Hz频率发送</td><td style='text-align: center; word-wrap: break-word;'>服务器→己方哨兵机器人</td><td style='text-align: center; word-wrap: break-word;'>常规链路</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0x020E</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>雷达自主决策信息同步，固定以1Hz频率发送</td><td style='text-align: center; word-wrap: break-word;'>服务器→己方雷达机器人</td><td style='text-align: center; word-wrap: break-word;'>常规链路</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0x0301</td><td style='text-align: center; word-wrap: break-word;'>118</td><td style='text-align: center; word-wrap: break-word;'>机器人交互数据，发送方触发发送，频率上限为30Hz</td><td style='text-align: center; word-wrap: break-word;'>-</td><td style='text-align: center; word-wrap: break-word;'>常规链路</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0x0302</td><td style='text-align: center; word-wrap: break-word;'>30</td><td style='text-align: center; word-wrap: break-word;'>自定义控制器与机器人交互数据，发送方触发发送，频率上限为30Hz</td><td style='text-align: center; word-wrap: break-word;'>自定义控制器→选手端图传连接的机器人</td><td style='text-align: center; word-wrap: break-word;'>图传链路</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0x0303</td><td style='text-align: center; word-wrap: break-word;'>15</td><td style='text-align: center; word-wrap: break-word;'>选手端小地图交互数据，选手端触发发送</td><td style='text-align: center; word-wrap: break-word;'>选手端点击→服务器→发送方选择的己方机器人</td><td style='text-align: center; word-wrap: break-word;'>常规链路</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0x0305</td><td style='text-align: center; word-wrap: break-word;'>48</td><td style='text-align: center; word-wrap: break-word;'>选手端小地图接收雷达数据，频率上限为5Hz</td><td style='text-align: center; word-wrap: break-word;'>雷达→服务器→己方所有选手端</td><td style='text-align: center; word-wrap: break-word;'>常规链路</td></tr></table>







<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>命令码</td><td style='text-align: center; word-wrap: break-word;'>数据段长度</td><td style='text-align: center; word-wrap: break-word;'>说明</td><td style='text-align: center; word-wrap: break-word;'>发送方/接收方</td><td style='text-align: center; word-wrap: break-word;'>所属数据链路</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0x0306</td><td style='text-align: center; word-wrap: break-word;'>8</td><td style='text-align: center; word-wrap: break-word;'>自定义控制器与选手端交互数据，发送方触发发送，频率上限为 30Hz</td><td style='text-align: center; word-wrap: break-word;'>自定义控制器→选手端</td><td style='text-align: center; word-wrap: break-word;'>-</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0x0307</td><td style='text-align: center; word-wrap: break-word;'>103</td><td style='text-align: center; word-wrap: break-word;'>选手端小地图接收路径数据，频率上限为 1Hz</td><td style='text-align: center; word-wrap: break-word;'>哨兵/半自动控制机器人\n→对应操作手选手端</td><td style='text-align: center; word-wrap: break-word;'>常规链路</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0x0308</td><td style='text-align: center; word-wrap: break-word;'>34</td><td style='text-align: center; word-wrap: break-word;'>选手端小地图接收机器人数据，频率上限为 3Hz</td><td style='text-align: center; word-wrap: break-word;'>己方机器人→己方选手端</td><td style='text-align: center; word-wrap: break-word;'>常规链路</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0x0309</td><td style='text-align: center; word-wrap: break-word;'>30</td><td style='text-align: center; word-wrap: break-word;'>自定义控制器接收机器人数据，频率上限为 10Hz</td><td style='text-align: center; word-wrap: break-word;'>选手端连接的自定义控制器</td><td style='text-align: center; word-wrap: break-word;'>图传链路</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0x0310</td><td style='text-align: center; word-wrap: break-word;'>300</td><td style='text-align: center; word-wrap: break-word;'>机器人发送给自定义客户端的数据，频率上限为 50Hz</td><td style='text-align: center; word-wrap: break-word;'>己方机器人→图传链路→对应操作手选手端连接的自定义客户端</td><td style='text-align: center; word-wrap: break-word;'>图传链路</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0x0311</td><td style='text-align: center; word-wrap: break-word;'>30</td><td style='text-align: center; word-wrap: break-word;'>自定义客户端发送给机器人的自定义指令，频率上限为 75Hz</td><td style='text-align: center; word-wrap: break-word;'>对应操作手选手端连接的自定义客户端→图传链路</td><td style='text-align: center; word-wrap: break-word;'>图传链路</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0x0A01</td><td style='text-align: center; word-wrap: break-word;'>24</td><td style='text-align: center; word-wrap: break-word;'>对方机器人的位置坐标，以 10Hz 频率持续发送</td><td style='text-align: center; word-wrap: break-word;'>信号发射源→雷达</td><td style='text-align: center; word-wrap: break-word;'>雷达无线链路</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0x0A02</td><td style='text-align: center; word-wrap: break-word;'>12</td><td style='text-align: center; word-wrap: break-word;'>对方机器人的血量信息，以 10Hz 频率持续发送</td><td style='text-align: center; word-wrap: break-word;'>信号发射源→雷达</td><td style='text-align: center; word-wrap: break-word;'>雷达无线链路</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0x0A03</td><td style='text-align: center; word-wrap: break-word;'>10</td><td style='text-align: center; word-wrap: break-word;'>对方机器人的剩余发弹量信息，以 10Hz 频率持续发送</td><td style='text-align: center; word-wrap: break-word;'>信号发射源→雷达</td><td style='text-align: center; word-wrap: break-word;'>雷达无线链路</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0x0A04</td><td style='text-align: center; word-wrap: break-word;'>8</td><td style='text-align: center; word-wrap: break-word;'>对方队伍的宏观状态信息，以 10Hz 频率持续发送</td><td style='text-align: center; word-wrap: break-word;'>信号发射源→雷达</td><td style='text-align: center; word-wrap: break-word;'>雷达无线链路</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0x0A05</td><td style='text-align: center; word-wrap: break-word;'>41</td><td style='text-align: center; word-wrap: break-word;'>对方各机器人当前增益效果，以 10Hz 频率持续发送</td><td style='text-align: center; word-wrap: break-word;'>信号发射源→雷达</td><td style='text-align: center; word-wrap: break-word;'>雷达无线链路</td></tr></table>

ROBOMASTER



<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>命令码</td><td style='text-align: center; word-wrap: break-word;'>数据段长度</td><td style='text-align: center; word-wrap: break-word;'>说明</td><td style='text-align: center; word-wrap: break-word;'>发送方/接收方</td><td style='text-align: center; word-wrap: break-word;'>所属数据链路</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0x0A06</td><td style='text-align: center; word-wrap: break-word;'>6</td><td style='text-align: center; word-wrap: break-word;'>对方干扰波密钥，以 10Hz\n频率持续发送</td><td style='text-align: center; word-wrap: break-word;'>信号发射源→雷达</td><td style='text-align: center; word-wrap: break-word;'>雷达无线链路</td></tr></table>

<div style="text-align: center;"><div style="text-align: center;">表 1-6 0x0001</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>字节偏移量</td><td style='text-align: center; word-wrap: break-word;'>大小</td><td style='text-align: center; word-wrap: break-word;'>说明</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>● bit 0-3：比赛类型\n➢ 1：RoboMaster 机甲大师超级对抗赛\n➢ 2：RoboMaster 机甲大师高校单项赛\n➢ 3：ICRA RoboMaster 高校人工智能挑战赛\n➢ 4：RoboMaster 机甲大师高校联盟赛 3V3 对抗\n➢ 5：RoboMaster 机甲大师高校联盟赛步兵对抗\n● bit 4-7：当前比赛阶段\n➢ 0：未开始比赛\n➢ 1：准备阶段\n➢ 2：十五秒裁判系统自检阶段\n➢ 3：五秒倒计时\n➢ 4：比赛中\n➢ 5：比赛结算中</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>当前阶段剩余时间，单位：秒</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>3</td><td style='text-align: center; word-wrap: break-word;'>8</td><td style='text-align: center; word-wrap: break-word;'>UNIX 时间，当机器人正确连接到裁判系统的 NTP 服务器后生效</td></tr></table>

typedef _packed struct

uint8_t game_type: 4;

uint8_t game_progress: 4;

uint16_t stage_remain_time;

uint64_t SyncTimeStamp;

{game_status_t;

<div style="text-align: center;"><div style="text-align: center;">表 1-7 0x0002</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>字节偏移量</td><td style='text-align: center; word-wrap: break-word;'>大小</td><td style='text-align: center; word-wrap: break-word;'>说明</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>0: 平局\n1: 红方胜利\n2: 蓝方胜利</td></tr><tr><td colspan="3">typedef _packed struct\n{\n    uint8_t winner;\n} game_result_t;</td></tr></table>

<div style="text-align: center;"><div style="text-align: center;">表 1-8 0x0003</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>字节偏移量</td><td style='text-align: center; word-wrap: break-word;'>大小</td><td style='text-align: center; word-wrap: break-word;'>说明</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>己方1号英雄机器人血量，若该机器人未上场或者被罚下，则血量为0，下文同理</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>己方2号工程机器人血量</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>己方3号步兵机器人血量</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>6</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>己方4号步兵机器人血量</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>8</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>己方全队总伤害与对方全队总伤害之差</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>10</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>己方7号哨兵机器人血量</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>12</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>己方前哨站血量</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>14</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>己方基地血量</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>16</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>对方前哨站血量</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>18</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>对方基地血量</td></tr></table>

##### ROBOMASTER

uint16_t ally_outpost_HP;

uint16_t ally_base_HP;

uint16_t enemy_outpost_HP;

uint16_t enemy_base_HP;

}game_robot_HP_t;

<div style="text-align: center;"><div style="text-align: center;">表 1-9 0x0101</div> </div>




<table border="1" style="margin: auto; word-wrap: break-word;"><tr><td style="text-align: center; word-wrap: break-word;">字节偏移量</td><td style="text-align: center; word-wrap: break-word;">大小</td><td style="text-align: center; word-wrap: break-word;">说明</td></tr><tr><td rowspan="16">0</td><td rowspan="16">4</td><td style="text-align: center; word-wrap: break-word;">0: 未占领/未激活</td></tr><tr><td style="text-align: center; word-wrap: break-word;">1: 已占领/已激活</td></tr><tr><td style="text-align: center; word-wrap: break-word;">● bit 0-2:</td></tr><tr><td style="text-align: center; word-wrap: break-word;">➢ bit 0: 已方补给区的占领状态, 1 为已占领</td></tr><tr><td style="text-align: center; word-wrap: break-word;">➢ bit 1: 保留位</td></tr><tr><td style="text-align: center; word-wrap: break-word;">➢ bit 2: 已方补给区的占领状态, 1 为已占领 (仅 RMUL 适用)</td></tr><tr><td style="text-align: center; word-wrap: break-word;">● bit 3-6: 已方能量机关状态</td></tr><tr><td style="text-align: center; word-wrap: break-word;">➢ bit 3-4: 已方小能量机关的激活状态, 0 为未激活, 1 为已激活, 2 为正在激活</td></tr><tr><td style="text-align: center; word-wrap: break-word;">➢ bit 5-6: 已方大能量机关的激活状态, 0 为未激活, 1 为已激活, 2 为正在激活</td></tr><tr><td style="text-align: center; word-wrap: break-word;">● bit 7-8: 已方中央高地的占领状态, 1 为被己方占领, 2 为被对方占领</td></tr><tr><td style="text-align: center; word-wrap: break-word;">● bit 9-10: 已方梯形高地的占领状态, 1 为已占领</td></tr><tr><td style="text-align: center; word-wrap: break-word;">● bit 11-19: 对方飞镖最后一次击中己方前哨站或基地的时间 (0-420, 开局默认为 0)</td></tr><tr><td style="text-align: center; word-wrap: break-word;">● bit 20-22: 对方飞镖最后一次击中己方前哨站或基地的具体目标, 开局默认为 0, 1 为击中前哨站, 2 为击中基地固定目标, 3 为击中基地随机固定目标, 4 为击中基地随机移动目标, 5 为击中基地末端移动目标</td></tr><tr><td style="text-align: center; word-wrap: break-word;">● bit 23-24: 中心增益点的占领状态, 0 为未被占领, 1 为被己方占领, 2 为被对方占领, 3 为被双方占领。(仅 RMUL 适用)</td></tr><tr><td style="text-align: center; word-wrap: break-word;">● bit 25-26: 已方堡垒增益点的占领状态, 0 为未被占领, 1 为被己方占领, 2 为被对方占领, 3 为被双方占领</td></tr><tr><td style="text-align: center; word-wrap: break-word;">● bit 27-28: 已方前哨站增益点的占领状态, 0 为未被占领, 1 为被己方</td></tr><tr><td style="text-align: center; word-wrap: break-word;"></td><td style="text-align: center; word-wrap: break-word;"></td><td style="text-align: center; word-wrap: break-word;">占领，2 为被对方占领\n● bit 29：己方基地增益点的占领状态，1 为已占领\n● bit 30-31：保留位\ntypedef _packed struct\n{\nuint32_t event_data;\n}event_data_t;</td></tr></table>




<div style="text-align: center;"><div style="text-align: center;">表 1-10 0x0104</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>字节偏移量</td><td style='text-align: center; word-wrap: break-word;'>大小</td><td style='text-align: center; word-wrap: break-word;'>说明</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>己方最后一次受到判罚的等级：\n● 1：双方黄牌\n● 2：黄牌\n● 3：红牌\n● 4：判负</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>● 己方最后一次受到判罚的违规机器人 ID（如红 1 机器人 ID 为 1，蓝 1 机器人 ID 为 101）\n● 判负和双方黄牌时，该值为 0</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>己方最后一次受到判罚的违规机器人对应判罚等级的违规次数（开局默认为 0）</td></tr><tr><td colspan="3">typedef _packed struct\n{\n    uint8_t level;\n    uint8_t offending_robot_id;\n    uint8_t count;\n}referee_warning_t;</td></tr></table>

<div style="text-align: center;"><div style="text-align: center;">表 1-11 0x0105</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>字节偏移量</td><td style='text-align: center; word-wrap: break-word;'>大小</td><td style='text-align: center; word-wrap: break-word;'>说明</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>己方飞镖发射剩余时间，单位：秒</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>● bit 0-2:\n最近一次己方飞镖击中的目标，开局默认为 0，1 为击中前哨站，2 为击中</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>基地固定目标，3为击中基地随机固定目标，4为击中基地随机移动目标，5为击中基地末端移动目标\n● bit 3-5:\n对方最近被击中的目标累计被击中计次数，开局默认为0，至多为4\n● bit 6-8:\n飞镖此时选定的击打目标，开局默认或未选定/选定前哨站时为0，选中基地固定目标为1，选中基地随机固定目标为2，选中基地随机移动目标为3，选中基地末端移动目标为4\n● bit 9-15: 保留</td></tr></table>





typedef _packed struct

uint8_t dart_remaining_time;

uint16_t dart_info;

}dart_info_t;

<div style="text-align: center;"><div style="text-align: center;">表 1-12 0x0201</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>字节偏移量</td><td style='text-align: center; word-wrap: break-word;'>大小</td><td style='text-align: center; word-wrap: break-word;'>说明</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>本机器人 ID</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>机器人等级</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>机器人当前血量</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>机器人血量上限</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>6</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>机器人射击热量每秒冷却值</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>8</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>机器人射击热量上限</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>10</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>机器人底盘功率上限</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>12</td><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>机器人射击初速度上限</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>16</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>电源管理模块的输出情况:\n● bit 0: gimbal 口输出, 0 为无输出, 1 为 24V 输出\n● bit 1: chassis 口输出, 0 为无输出, 1 为 24V 输出</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>● bit 2: shooter 口输出, 0 为无输出, 1 为 24V 输出</td></tr><tr><td colspan="3">typedef_packed struct\n{ uint8_t robot_id; uint8_t robot_level; uint16_t current_HP; uint16_t maximum_HP; uint16_t shooter_barrel_cooling_value; uint16_t shooter_barrel_heat_limit; uint16_t chassis_power_limit; float bullet_speed_limit; uint8_t power_management_gimbal_output:1; uint8_t power_management_chassis_output:1; uint8_t power_management_shooter_output:1; robot_status_t;</td></tr><tr><td colspan="3">表 1-13 0x0202</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>字节偏移量</td><td style='text-align: center; word-wrap: break-word;'>大小</td><td style='text-align: center; word-wrap: break-word;'>说明</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>保留位</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>保留位</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>保留位</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>8</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>缓冲能量 (单位: J)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>10</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>17mm 发射机构的射击热量</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>12</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>42mm 发射机构的射击热量</td></tr><tr><td colspan="3">typedef_packed struct\n{ uint16_t reserved; uint16_t reserved; float reserved; uint16_t buffer_energy; uint16_t shooter_17mm_barrel_heat; uint16_t shooter_42mm_barrel_heat; power_heat_data_t;</td></tr></table>





<div style="text-align: center;"><div style="text-align: center;">表 1-14 0x0203</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>字节偏移量</td><td style='text-align: center; word-wrap: break-word;'>大小</td><td style='text-align: center; word-wrap: break-word;'>说明</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0</td><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>本机器人位置 x 坐标，单位：m</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>本机器人位置 y 坐标，单位：m</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>8</td><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>本机器人测速模块的朝向，单位：度，正北为 0 度</td></tr><tr><td colspan="3">typedef _packed struct\n{\n    float x;\n    float y;\n    float angle;\n} robot_pos_t;</td></tr></table>

<div style="text-align: center;"><div style="text-align: center;">表 1-15 0x0204</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>字节偏移量</td><td style='text-align: center; word-wrap: break-word;'>大小</td><td style='text-align: center; word-wrap: break-word;'>说明</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>机器人回血增益（百分比，值为 10 表示每秒恢复血量上限的 10%）</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>机器人射击热量冷却增益具体值（直接值，值为 x 表示热量冷却增加 x/s）</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>3</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>机器人防御增益（百分比，值为 50 表示 50% 防御增益）</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>机器人负防御增益（百分比，值为 30 表示-30% 防御增益）</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>5</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>机器人攻击增益（百分比，值为 50 表示 50% 攻击增益）</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>7</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>bit 0-6: 机器人剩余能量值反馈，以 16 进制标识机器人剩余能量值比例。\n机器人初始能量视为 100%\n● bit 0: 在剩余能量≥125%时为 1，其余情况为 0\n● bit 1: 在剩余能量≥100%时为 1，其余情况为 0\n● bit 2: 在剩余能量≥50%时为 1，其余情况为 0\n● bit 3: 在剩余能量≥30%时为 1，其余情况为 0\n● bit 4: 在剩余能量≥15%时为 1，其余情况为 0\n● bit 5: 在剩余能量≥5%时为 1，其余情况为 0\n● bit 6: 在剩余能量≥1%时为 1，其余情况为 0</td></tr></table>

typedef _packed struct



<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>uint8_t recovery_buff;\nuint16_t cooling_buff;\nuint8_t defence_buff;\nuint8_t vulnerability_buff;\nuint16_t attack_buff;\nuint8_t remaining_energy;\nbuff_t;</td></tr></table>

<div style="text-align: center;"><div style="text-align: center;">表 1-16 0x0206</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>字节偏移量</td><td style='text-align: center; word-wrap: break-word;'>大小</td><td style='text-align: center; word-wrap: break-word;'>说明</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>bit 0-3: 当扫血原因为装甲模块被弹丸攻击、受撞击或离线时，该 4 bit 组成的数值为装甲模块或测速模块的 ID 编号；当其他原因导致扫血时，该数值为 0\nbit 4-7: 血量变化类型\n● 0: 装甲模块被弹丸攻击导致扫血\n● 1: 装甲模块或超级电容管理模块离线导致扫血\n● 5: 装甲模块受到撞击导致扫血</td></tr><tr><td colspan="3">typedef _packed struct\n{\n    uint8_t armor_id : 4;\n    uint8_t HP_deduction_reason : 4;\n}hurt_data_t;</td></tr><tr><td style='text-align: center; word-wrap: break-word;'><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//5b8ec177-8c39-4ad6-955e-eedf10e141fb/markdown_0/imgs/img_in_image_box_128_980_171_1026.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A40Z%2F-1%2F%2Fbca00655564194dc431d33d8a5259ac8934aef9d2389bb31f56038936a0a5ffa" alt="Image"" /></td><td colspan="2">0x0206 的受伤害情况为机器人裁判系统本地判定，即时发送，但实际是否受到对应伤害受规则条例影响，请以服务器最终判定为准。</td></tr></table>

<div style="text-align: center;"><div style="text-align: center;">表 1-17 0x0207</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>字节偏移量</td><td style='text-align: center; word-wrap: break-word;'>大小</td><td style='text-align: center; word-wrap: break-word;'>说明</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>弹丸类型：\n● bit 1: 17mm 弹丸\n● bit 2: 42mm 弹丸</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>发射机构 ID：\n● 1: 17mm 发射机构\n● 2: 保留位\n● 3: 42mm 发射机构</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>弹丸射速（单位：Hz）</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>3</td><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>弹丸初速度（单位：m/s）</td></tr><tr><td colspan="3">typedef _packed struct\n{    uint8_t bullet_type;    uint8_t shooter_number;    uint8_t launching_frequency;    float initial_speed;}\n}shoot_data_t;</td></tr></table>

©2026 大疆 版权所有





<div style="text-align: center;"><div style="text-align: center;">表 1-18 0x0208</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>字节偏移量</td><td style='text-align: center; word-wrap: break-word;'>大小</td><td style='text-align: center; word-wrap: break-word;'>说明</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>机器人自身拥有的 17mm 弹丸允许发弹量</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>42mm 弹丸允许发弹量</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>剩余金币数量</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>6</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>堡垒增益点提供的储备 17mm 弹丸允许发弹量；该值与机器人是否实际占领堡垒无关</td></tr></table>

{projectile_allowance_t;

<div style="text-align: center;"><div style="text-align: center;">表 1-19 0x0209</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>字节偏移量</td><td style='text-align: center; word-wrap: break-word;'>大小</td><td style='text-align: center; word-wrap: break-word;'>说明</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0</td><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>● bit 位值为 1/0 的含义：是否已检测到该增益点 RFID 卡\n● bit 0：己方基地增益点\n● bit 1：己方中央高地增益点\n● bit 2：对方中央高地增益点\n● bit 3：己方梯形高地增益点</td></tr></table>

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//5b8ec177-8c39-4ad6-955e-eedf10e141fb/markdown_2/imgs/img_in_chart_box_101_136_1071_1518.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A41Z%2F-1%2F%2F7f98c1b4e246424fd48b65065dd4259bfa8ebb4bb06e1785c1eea571e86c18c5" alt="Image" width="81%" /></div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>字节偏移量</td><td style='text-align: center; word-wrap: break-word;'>大小</td><td style='text-align: center; word-wrap: break-word;'>说明</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>bit 31: 己方地形跨越增益点（隧道）（靠近己方梯形高地较高处）</td></tr><tr><td rowspan="6">4</td><td rowspan="6">1</td><td style='text-align: center; word-wrap: break-word;'>bit 0: 对方地形跨越增益点（隧道）（靠近对方公路一侧下方）</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>bit 1: 对方地形跨越增益点（隧道）（靠近对方公路一侧中间）</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>bit 2: 对方地形跨越增益点（隧道）（靠近对方公路一侧上方）</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>bit 3: 对方地形跨越增益点（隧道）（靠近对方梯形高地较低处）</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>bit 4: 对方地形跨越增益点（隧道）（靠近对方梯形高地较中间）</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>bit 5: 对方地形跨越增益点（隧道）（靠近对方梯形高地较高处）</td></tr><tr><td colspan="3">注：所有RFID卡仅在赛内生效。在赛外，即使检测到对应的RFID卡，对应值也为0。</td></tr><tr><td colspan="3">typedef_packed struct{uint32_t rfid_status;uint8_t rfid_status_2;}rfid_status_t;</td></tr><tr><td colspan="3">表1-20 0x020A</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>字节偏移量</td><td style='text-align: center; word-wrap: break-word;'>大小</td><td style='text-align: center; word-wrap: break-word;'>说明</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>当前飞镖发射站的状态:</td></tr><tr><td rowspan="2">0</td><td style='text-align: center; word-wrap: break-word;'>1: 关闭</td><td style='text-align: center; word-wrap: break-word;'>● 1: 关闭</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>2: 正在开启或者关闭中</td><td style='text-align: center; word-wrap: break-word;'>● 0: 已经开启</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>保留位</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>切换击打目标时的比赛剩余时间，单位：秒，无/未切换动作，默认为0。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>最后一次操作手确定发射指令时的比赛剩余时间，单位：秒，初始值为0。</td></tr><tr><td colspan="3">typedef_packed struct{uint8_t dart_launch_opening_status;uint8_t reserved;uint16_t target_change_time;uint16_t latest_launch_cmd_time;}dart_client_cmd_t;</td></tr></table>

<div style="text-align: center;"><div style="text-align: center;">表 1-21 0x020B</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>字节偏移量</td><td style='text-align: center; word-wrap: break-word;'>大小</td><td style='text-align: center; word-wrap: break-word;'>说明</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0</td><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>己方英雄机器人位置 x 轴坐标，单位：m</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>己方英雄机器人位置 y 轴坐标，单位：m</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>8</td><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>己方工程机器人位置 x 轴坐标，单位：m</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>12</td><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>己方工程机器人位置 y 轴坐标，单位：m</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>16</td><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>己方 3 号步兵机器人位置 x 轴坐标，单位：m</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>20</td><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>己方 3 号步兵机器人位置 y 轴坐标，单位：m</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>24</td><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>己方 4 号步兵机器人位置 x 轴坐标，单位：m</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>28</td><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>己方 4 号步兵机器人位置 y 轴坐标，单位：m</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>32</td><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>保留位</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>36</td><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>保留位</td></tr></table>

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//1c13b0a2-5b5f-4ce5-9510-6f0bb755bb61/markdown_0/imgs/img_in_image_box_128_888_172_934.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A40Z%2F-1%2F%2F79b430bf5cea803b11ebb2eece4db4aaa1b372f26b9bf106cbc27061ed1ec50d" alt="Image" width="3%" /></div>


场地围挡在红方补给站附近的交点为坐标原点，沿场地长边向蓝方为 X 轴正方向，沿场地短边向红方停机坪为 Y 轴正方向。



<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>typedef _packed struct</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>{</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>float hero_x;</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>float hero_y;</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>float engineer_x;</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>float engineer_y;</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>float standard_3_x;</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>float standard_3_y;</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>float standard_4_x;</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>float standard_4_y;</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>float reserved;</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>float reserved;</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>}ground_robot_position_t;</td></tr></table>

<div style="text-align: center;"><div style="text-align: center;">表 1-22 0x020C</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>字节偏移量</td><td style='text-align: center; word-wrap: break-word;'>大小</td><td style='text-align: center; word-wrap: break-word;'>说明</td><td style='text-align: center; word-wrap: break-word;'>备注</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>● bit 0：对方 1 号英雄机器人易伤情况</td><td style='text-align: center; word-wrap: break-word;'>对方机器人：在对应机器</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>● bit 1：对方 2 号工程机器人易伤情况\n● bit 2：对方 3 号步兵机器人易伤情况\n● bit 3：对方 4 号步兵机器人易伤情况\n● bit 4：对方空中机器人特殊标识情况\n● bit 5：对方哨兵机器人易伤情况\n● bit 6：己方 1 号英雄机器人特殊标识情况\n● bit 7：己方 2 号工程机器人特殊标识情况\n● bit 8：己方 3 号步兵机器人特殊标识情况\n● bit 9：己方 4 号步兵机器人特殊标识情况\n● bit 10：己方空中机器人特殊标识情况\n● bit 11：己方哨兵机器人特殊标识情况\n● bit 12：对方空中机器人是否被己方雷达激光瞄准\n● bit 13：对方空中机器人当前是否处于被反制状态\n● bit 14：己方空中机器人是否被对方雷达激光瞄准\n● bit 15：己方空中机器人是否处于被反制状态</td><td style='text-align: center; word-wrap: break-word;'>人被标记进度≥100 时发送 1，被标记进度&lt;100 时发送 0。\n己方机器人：在对应机器人被标记进度≥50 时发送 1，被标记进度&lt;50 时发送 0。</td></tr><tr><td colspan="4">typedef_packed struct\n{uint16_t mark_progress;\n`radar_mark_data_t:</td></tr></table>

20 © 2026 大疆 版权所有





<div style="text-align: center;"><div style="text-align: center;">表 1-23 0x020D</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>字节偏移量</td><td style='text-align: center; word-wrap: break-word;'>大小</td><td style='text-align: center; word-wrap: break-word;'>说明</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0</td><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>● bit 0-10：除远程兑换外，哨兵机器人成功兑换的允许发弹量，开局为 0，在哨兵机器人成功兑换一定允许发弹量后，该值将变为哨兵机器人成功兑换的允许发弹量值\n● bit 11-14：哨兵机器人成功远程兑换允许发弹量的次数，开局为 0，在哨</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>兵器机器人成功远程兑换允许发弹量后，该值将变为哨兵机器人成功远程兑换允许发弹量的次数\n• bit 15-18：哨兵机器人成功远程兑换血量的次数，开局为 0，在哨兵机器人成功远程兑换血量后，该值将变为哨兵机器人成功远程兑换血量的次数\n• bit 19：哨兵机器人当前是否可以确认免费复活，可以确认免费复活时值为 1，否则为 0\n• bit 20：哨兵机器人当前是否可以兑换立即复活，可以兑换立即复活时值为 1，否则为 0\n• bit 21-30：哨兵机器人当前若兑换立即复活需要花费的金币数。\n• bit 31：保留</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>• bit 0：哨兵当前是否处于脱战状态，处于脱战状态时为 1，否则为 0\n• bit 1-11：队伍 17mm 允许发弹量的剩余可兑换数\n• bit 12-13：哨兵当前姿态，1 为进攻姿态，2 为防御姿态，3 为移动姿态\n• bit 14：己方能量机关是否能够进入正在激活状态，1 为当前可激活\n• bit 15：哨兵当前姿态是否为强化姿态</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>6</td><td style='text-align: center; word-wrap: break-word;'>8</td><td style='text-align: center; word-wrap: break-word;'>• bit 0-7：哨兵进攻姿态弱化前剩余可持续时长（单位秒，下同）\n• bit 8-15：哨兵防御姿态弱化前剩余可持续时长\n• bit 16-23：哨兵移动姿态弱化前剩余可持续时长\n• bit 24-31：保留位\n• bit 32-39：哨兵强化进攻姿态剩余可持续时长\n• bit 40-47：哨兵强化防御姿态剩余可持续时长\n• bit 48-55：哨兵强化移动姿态剩余可持续时长\n• bit 56-63：保留位</td></tr></table>





ROBOMASTER

typedef _packed struct
{
    uint32_t sentry_info;
    uint16_t sentry_info_2;
    uint64_t sentry_info_3;
}
sentry_info_t;

<div style="text-align: center;"><div style="text-align: center;">表1-24 0x020E</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>字节偏移量</td><td style='text-align: center; word-wrap: break-word;'>大小</td><td style='text-align: center; word-wrap: break-word;'>说明</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>● bit 0-1：雷达是否拥有触发双倍易伤的机会，开局为 0，数值为雷达拥有触发双倍易伤的机会，至多为 2\n● bit 2：对方是否正在被触发双倍易伤\n➢ 0：对方未被触发双倍易伤\n➢ 1：对方正在被触发双倍易伤\n● bit 3-4：己方加密等级（即对方干扰波难度等级），开局为 1，最高为 3\n● bit 5：当前是否可以修改密钥，1 为可修改\n● bit 6-7：保留位</td></tr></table>

typedef _packed struct
{
    uint8_t radar_info;
} radar_info_t;

机器人交互数据通过常规链路发送，其数据段包含一个统一的数据段头结构。数据段头结构包括内容ID、发送者和接收者的ID、内容数据段。机器人交互数据包的总长不超过127个字节，减去frame_header、cmd_id和frame_tail的9个字节以及数据段头结构的6个字节，故机器人交互数据的内容数据段最大为112个字节。

每1000毫秒，英雄、工程、步兵、空中机器人、飞镖能够接收数据的上限为3720字节，雷达和哨兵机器人能够接收数据的上限为5120字节。

由于存在多个内容 ID，但整个 cmd_id 上行频率最大为 30Hz，请合理安排带宽。

<div style="text-align: center;"><div style="text-align: center;">表 1-25 0x0301</div> </div>




<table border="1" style="margin: auto; word-wrap: break-word;"><tr><td style="text-align: center; word-wrap: break-word;">字节偏移量</td><td style="text-align: center; word-wrap: break-word;">大小</td><td style="text-align: center; word-wrap: break-word;">说明</td><td style="text-align: center; word-wrap: break-word;">备注</td></tr><tr><td style="text-align: center; word-wrap: break-word;">0</td><td style="text-align: center; word-wrap: break-word;">2</td><td style="text-align: center; word-wrap: break-word;">子内容 ID</td><td style="text-align: center; word-wrap: break-word;">需为开放的子内容 ID</td></tr><tr><td style="text-align: center; word-wrap: break-word;">2</td><td style="text-align: center; word-wrap: break-word;">2</td><td style="text-align: center; word-wrap: break-word;">发送者 ID</td><td style="text-align: center; word-wrap: break-word;">需与自身 ID 匹配，ID 编号详见附录</td></tr><tr><td style="text-align: center; word-wrap: break-word;">4</td><td style="text-align: center; word-wrap: break-word;">2</td><td style="text-align: center; word-wrap: break-word;">接收者 ID</td><td style="text-align: center; word-wrap: break-word;">● 仅限己方通信\n● 需为规则允许的多机通讯接收者\n● 若接收者为选手端，则除雷达系统外，仅可发送至发送者对应的选手端。雷达系统可发送至任意己方选手端。ID 编号详见附录</td></tr><tr><td style="text-align: center; word-wrap: break-word;">6</td><td style="text-align: center; word-wrap: break-word;">x</td><td style="text-align: center; word-wrap: break-word;">内容数据段</td><td style="text-align: center; word-wrap: break-word;">x 最大为 112</td></tr></table>






<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>typedef _packed struct</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>{</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>uint16_t data_cmd_id;</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>uint16_t sender_id;</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>uint16_t receiver_id;</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>uint8_t user_data[x];</td></tr></table>

robot_interaction_data_t;



<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>子内容 ID</td><td style='text-align: center; word-wrap: break-word;'>内容数据段长度</td><td style='text-align: center; word-wrap: break-word;'>功能说明</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0x0200~0x02FF</td><td style='text-align: center; word-wrap: break-word;'>x≤112</td><td style='text-align: center; word-wrap: break-word;'>机器人之间通信</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0x0100</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>选手端删除图层</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0x0101</td><td style='text-align: center; word-wrap: break-word;'>15</td><td style='text-align: center; word-wrap: break-word;'>选手端绘制一个图形</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0x0102</td><td style='text-align: center; word-wrap: break-word;'>30</td><td style='text-align: center; word-wrap: break-word;'>选手端绘制两个图形</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0x0103</td><td style='text-align: center; word-wrap: break-word;'>75</td><td style='text-align: center; word-wrap: break-word;'>选手端绘制五个图形</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0x0104</td><td style='text-align: center; word-wrap: break-word;'>105</td><td style='text-align: center; word-wrap: break-word;'>选手端绘制七个图形</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0x0110</td><td style='text-align: center; word-wrap: break-word;'>45</td><td style='text-align: center; word-wrap: break-word;'>选手端绘制字符图形</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0x0120</td><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>哨兵自主决策指令</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0x0121</td><td style='text-align: center; word-wrap: break-word;'>8</td><td style='text-align: center; word-wrap: break-word;'>雷达自主决策指令</td></tr></table>

<div style="text-align: center;"><div style="text-align: center;">表 1-26 子内容 ID: 0x0100</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>字节偏移量</td><td style='text-align: center; word-wrap: break-word;'>大小</td><td style='text-align: center; word-wrap: break-word;'>说明</td><td style='text-align: center; word-wrap: break-word;'>备注</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>删除操作</td><td style='text-align: center; word-wrap: break-word;'>● 0：空操作\n● 1：删除图层</td></tr></table>

24 © 2026 大疆 版权所有

ROBOMASTER



<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>字节偏移量</td><td style='text-align: center; word-wrap: break-word;'>大小</td><td style='text-align: center; word-wrap: break-word;'>说明</td><td style='text-align: center; word-wrap: break-word;'>备注</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>● 2：删除所有</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>图层数</td><td style='text-align: center; word-wrap: break-word;'>图层数：0~9</td></tr><tr><td colspan="4">typedef _packed struct\n{    uint8_t delete_type;    uint8_t layer;    interaction_layer_delete_t;</td></tr></table>

<div style="text-align: center;"><div style="text-align: center;">表 1-27 子内容 ID: 0x0101</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>字节偏移量</td><td style='text-align: center; word-wrap: break-word;'>大小</td><td style='text-align: center; word-wrap: break-word;'>说明</td><td style='text-align: center; word-wrap: break-word;'>备注</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0</td><td style='text-align: center; word-wrap: break-word;'>3</td><td style='text-align: center; word-wrap: break-word;'>图形名</td><td style='text-align: center; word-wrap: break-word;'>在图形删除、修改等操作中，作为索引</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>3</td><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>图形配置1</td><td style='text-align: center; word-wrap: break-word;'>● bit 0-2: 图形操作\n➢ 0: 空操作\n➢ 1: 增加\n➢ 2: 修改\n➢ 3: 删除\n● bit 3-5: 图形类型\n➢ 0: 直线\n➢ 1: 矩形\n➢ 2: 正圆\n➢ 3: 椭圆\n➢ 4: 圆弧\n➢ 5: 浮点数\n➢ 6: 整型数\n➢ 7: 字符\n● bit 6-9: 图层数 (0~9)\n● bit 10-13: 颜色\n➢ 0: 红/蓝 (己方颜色)</td></tr><tr><td rowspan="9"></td><td rowspan="9"></td><td rowspan="8"></td><td style='text-align: center; word-wrap: break-word;'>1: 黄色</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>2: 绿色</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>3: 橙色</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>4: 紫红色</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>5: 粉色</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>6: 青色</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>7: 黑色</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>8: 白色</td></tr><tr><td colspan="2">bit 14-31: 根据绘制的图形不同, 含义不同, 详见“表 1-28 图形细节参数说明”</td></tr><tr><td rowspan="3">7</td><td rowspan="3">4</td><td rowspan="3">图形配置 2</td><td style='text-align: center; word-wrap: break-word;'>bit 0-9: 线宽, 建议字体大小与线宽比例为 10: 1</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>bit 10-20: 起点/圆心 x 坐标</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>bit 21-31: 起点/圆心 y 坐标</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>11</td><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>图形配置 3</td><td style='text-align: center; word-wrap: break-word;'>根据绘制的图形不同, 含义不同, 详见“表 1-28 图形细节参数说明”</td></tr><tr><td colspan="4">typedef _packed struct</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>{</td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td colspan="4">uint8_t figure_name[3];</td></tr><tr><td colspan="4">uint32_t operate_tpye:3;</td></tr><tr><td colspan="4">uint32_t figure_tpye:3;</td></tr><tr><td colspan="4">uint32_t layer:4;</td></tr><tr><td colspan="4">uint32_t color:4;</td></tr><tr><td colspan="4">uint32_t details_a:9;</td></tr><tr><td colspan="4">uint32_t details_b:9;</td></tr><tr><td colspan="4">uint32_t width:10;</td></tr><tr><td colspan="4">uint32_t start_x:11;</td></tr><tr><td colspan="4">uint32_t start_y:11;</td></tr><tr><td colspan="4">uint32_t details_c:10;</td></tr><tr><td colspan="4">uint32_t details_d:11;</td></tr><tr><td colspan="4">uint32_t details_e:11;</td></tr><tr><td colspan="4">interaction_figure_t;</td></tr></table>





<div style="text-align: center;"><div style="text-align: center;">表 1-28 图形细节参数说明</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>类型</td><td style='text-align: center; word-wrap: break-word;'>details_a</td><td style='text-align: center; word-wrap: break-word;'>details_b</td><td style='text-align: center; word-wrap: break-word;'>details_c</td><td style='text-align: center; word-wrap: break-word;'>details_d</td><td style='text-align: center; word-wrap: break-word;'>details_e</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>直线</td><td style='text-align: center; word-wrap: break-word;'>-</td><td style='text-align: center; word-wrap: break-word;'>-</td><td style='text-align: center; word-wrap: break-word;'>-</td><td style='text-align: center; word-wrap: break-word;'>终点 x 坐标</td><td style='text-align: center; word-wrap: break-word;'>终点 y 坐标</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>矩形</td><td style='text-align: center; word-wrap: break-word;'>-</td><td style='text-align: center; word-wrap: break-word;'>-</td><td style='text-align: center; word-wrap: break-word;'>-</td><td style='text-align: center; word-wrap: break-word;'>对角顶点 x 坐标</td><td style='text-align: center; word-wrap: break-word;'>对角顶点 y 坐标</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>正圆</td><td style='text-align: center; word-wrap: break-word;'>-</td><td style='text-align: center; word-wrap: break-word;'>-</td><td style='text-align: center; word-wrap: break-word;'>半径</td><td style='text-align: center; word-wrap: break-word;'>-</td><td style='text-align: center; word-wrap: break-word;'>-</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>椭圆</td><td style='text-align: center; word-wrap: break-word;'>-</td><td style='text-align: center; word-wrap: break-word;'>-</td><td style='text-align: center; word-wrap: break-word;'>-</td><td style='text-align: center; word-wrap: break-word;'>x 半轴长度</td><td style='text-align: center; word-wrap: break-word;'>y 半轴长度</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>圆弧</td><td style='text-align: center; word-wrap: break-word;'>起始角度</td><td style='text-align: center; word-wrap: break-word;'>终止角度</td><td style='text-align: center; word-wrap: break-word;'>-</td><td style='text-align: center; word-wrap: break-word;'>x 半轴长度</td><td style='text-align: center; word-wrap: break-word;'>y 半轴长度</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>浮点数</td><td style='text-align: center; word-wrap: break-word;'>字体大小</td><td style='text-align: center; word-wrap: break-word;'>无作用</td><td colspan="3">该值除以 1000 即实际显示值</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>整型数</td><td style='text-align: center; word-wrap: break-word;'>字体大小</td><td style='text-align: center; word-wrap: break-word;'>-</td><td colspan="3">32 位整型数， int32_t</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>字符</td><td style='text-align: center; word-wrap: break-word;'>字体大小</td><td style='text-align: center; word-wrap: break-word;'>字符长度</td><td style='text-align: center; word-wrap: break-word;'>-</td><td style='text-align: center; word-wrap: break-word;'>-</td><td style='text-align: center; word-wrap: break-word;'>-</td></tr></table>

角度值含义为： $ 0^{\circ} $指12点钟方向，顺时针绘制。

屏幕位置：（0,0）为屏幕左下角（1920，1080）为屏幕右上角。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//c0f0dc77-641b-4f72-b8c7-27d86673498e/markdown_3/imgs/img_in_image_box_133_1222_178_1266.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A43Z%2F-1%2F%2Fa876db8d5edef1433d027698cc5be527ac8ce7bfaded422812fd6d991138ae6a" alt="Image" width="3%" /></div>


● 浮点数：整型数均为32位，对于浮点数，实际显示的值为输入的值/1000，如在 $ \text{details\_c} $、 $ \text{details\_d} $、 $ \text{details\_e} $对应的字节输入1234，选手端实际显示的值将为1.234。

即使发送的数值超过对应数据类型的限制，图形仍有可能显示，但此时不保证显示的效果。

<div style="text-align: center;"><div style="text-align: center;">表 1-29 子内容 ID: 0x0102</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>字节偏移量</td><td style='text-align: center; word-wrap: break-word;'>大小</td><td style='text-align: center; word-wrap: break-word;'>说明</td><td style='text-align: center; word-wrap: break-word;'>备注</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0</td><td style='text-align: center; word-wrap: break-word;'>15</td><td style='text-align: center; word-wrap: break-word;'>图形 1</td><td style='text-align: center; word-wrap: break-word;'>与 0x0101 的数据段相同</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>15</td><td style='text-align: center; word-wrap: break-word;'>15</td><td style='text-align: center; word-wrap: break-word;'>图形 2</td><td style='text-align: center; word-wrap: break-word;'>与 0x0101 的数据段相同</td></tr></table>

typedef _packed struct

interaction_figure_t interaction_figure[2];

}interaction_figure_2_t;

<div style="text-align: center;"><div style="text-align: center;">表 1-30 子内容 ID: 0x0103</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>字节偏移量</td><td style='text-align: center; word-wrap: break-word;'>大小</td><td style='text-align: center; word-wrap: break-word;'>说明</td><td style='text-align: center; word-wrap: break-word;'>备注</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0</td><td style='text-align: center; word-wrap: break-word;'>15</td><td style='text-align: center; word-wrap: break-word;'>图形 1</td><td style='text-align: center; word-wrap: break-word;'>与 0x0101 的数据段相同</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>15</td><td style='text-align: center; word-wrap: break-word;'>15</td><td style='text-align: center; word-wrap: break-word;'>图形 2</td><td style='text-align: center; word-wrap: break-word;'>与 0x0101 的数据段相同</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>30</td><td style='text-align: center; word-wrap: break-word;'>15</td><td style='text-align: center; word-wrap: break-word;'>图形 3</td><td style='text-align: center; word-wrap: break-word;'>与 0x0101 的数据段相同</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>45</td><td style='text-align: center; word-wrap: break-word;'>15</td><td style='text-align: center; word-wrap: break-word;'>图形 4</td><td style='text-align: center; word-wrap: break-word;'>与 0x0101 的数据段相同</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>60</td><td style='text-align: center; word-wrap: break-word;'>15</td><td style='text-align: center; word-wrap: break-word;'>图形 5</td><td style='text-align: center; word-wrap: break-word;'>与 0x0101 的数据段相同</td></tr></table>

typedef _packed struct

{interaction_figure_3_t;

<div style="text-align: center;"><div style="text-align: center;">表 1-31 子内容 ID: 0x0104</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>字节偏移量</td><td style='text-align: center; word-wrap: break-word;'>大小</td><td style='text-align: center; word-wrap: break-word;'>说明</td><td style='text-align: center; word-wrap: break-word;'>备注</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0</td><td style='text-align: center; word-wrap: break-word;'>15</td><td style='text-align: center; word-wrap: break-word;'>图形 1</td><td style='text-align: center; word-wrap: break-word;'>与 0x0101 的数据段相同</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>15</td><td style='text-align: center; word-wrap: break-word;'>15</td><td style='text-align: center; word-wrap: break-word;'>图形 2</td><td style='text-align: center; word-wrap: break-word;'>与 0x0101 的数据段相同</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>30</td><td style='text-align: center; word-wrap: break-word;'>15</td><td style='text-align: center; word-wrap: break-word;'>图形 3</td><td style='text-align: center; word-wrap: break-word;'>与 0x0101 的数据段相同</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>45</td><td style='text-align: center; word-wrap: break-word;'>15</td><td style='text-align: center; word-wrap: break-word;'>图形 4</td><td style='text-align: center; word-wrap: break-word;'>与 0x0101 的数据段相同</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>60</td><td style='text-align: center; word-wrap: break-word;'>15</td><td style='text-align: center; word-wrap: break-word;'>图形 5</td><td style='text-align: center; word-wrap: break-word;'>与 0x0101 的数据段相同</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>75</td><td style='text-align: center; word-wrap: break-word;'>15</td><td style='text-align: center; word-wrap: break-word;'>图形 6</td><td style='text-align: center; word-wrap: break-word;'>与 0x0101 的数据段相同</td></tr></table>

©2026 大疆 版权所有

ROBOMASTER



<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>字节偏移量</td><td style='text-align: center; word-wrap: break-word;'>大小</td><td style='text-align: center; word-wrap: break-word;'>说明</td><td style='text-align: center; word-wrap: break-word;'>备注</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>90</td><td style='text-align: center; word-wrap: break-word;'>15</td><td style='text-align: center; word-wrap: break-word;'>图形 7</td><td style='text-align: center; word-wrap: break-word;'>与 0x0101 的数据段相同</td></tr><tr><td colspan="4">typedef _packed struct\n{\n    interaction_figure_t interaction_figure[7];\n    interaction_figure_4_t;\n}</td></tr></table>

<div style="text-align: center;"><div style="text-align: center;">表 1-32 子内容 ID: 0x0110</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>字节偏移量</td><td style='text-align: center; word-wrap: break-word;'>大小</td><td style='text-align: center; word-wrap: break-word;'>说明</td><td style='text-align: center; word-wrap: break-word;'>备注</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>数据的内容 ID</td><td style='text-align: center; word-wrap: break-word;'>0x0110</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>发送者的 ID</td><td style='text-align: center; word-wrap: break-word;'>需要校验发送者的 ID 正确性</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>接收者的 ID</td><td style='text-align: center; word-wrap: break-word;'>需要校验接收者的 ID 正确性，仅支持发送机器人对应的选手端</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>6</td><td style='text-align: center; word-wrap: break-word;'>15</td><td style='text-align: center; word-wrap: break-word;'>字符配置</td><td style='text-align: center; word-wrap: break-word;'>详见图形数据介绍</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>21</td><td style='text-align: center; word-wrap: break-word;'>30</td><td style='text-align: center; word-wrap: break-word;'>字符</td><td style='text-align: center; word-wrap: break-word;'>-</td></tr></table>

typedef _packed struct

}ext_client_custom_character_t;

<div style="text-align: center;"><div style="text-align: center;">表 1-33 哨兵自主决策指令：0x0120</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>字节偏移量</td><td style='text-align: center; word-wrap: break-word;'>大小</td><td style='text-align: center; word-wrap: break-word;'>说明</td><td style='text-align: center; word-wrap: break-word;'>备注</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0</td><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>哨兵自主决策相关指令</td><td style='text-align: center; word-wrap: break-word;'>● bit 0：哨兵机器人是否确认复活。\n➢ 0 表示哨兵机器人确认不复活，即使此时哨兵的复活读条已经完成。\n➢ 1 表示哨兵机器人确认复活，若复活读条完成将立即复活。\n● bit 1：哨兵机器人是否确认兑换立即复活。\n➢ 0 表示哨兵机器人确认不兑换立即复活。\n➢ 1 表示哨兵机器人确认兑换立即复活，若此时哨兵机器人符合兑换立即复活的规则要求，则会立即消耗金</td></tr><tr><td rowspan="2"></td><td rowspan="2"></td><td rowspan="2"></td><td style='text-align: center; word-wrap: break-word;'>币兑换立即复活。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>bit 2-12：哨兵将要兑换的发弹量值，开局为 0，修改此值后，哨兵在补血点即可兑换允许发弹量。此值的变化需要单调递增，否则视为不合法。示例：此值开局仅能为 0，此后哨兵可将其从 0 修改至 X，则消耗 X 金币成功兑换 X 允许发弹量。此后哨兵可将其从 X 修改至 X+Y，以此类推。bit 13-16：哨兵远程兑换发弹量的请求次数，开局为 0，修改此值即可请求远程兑换发弹量。此值的变化需要单调递增且每次仅能增加 1，否则视为不合法。示例：此值开局仅能为 0，此后哨兵可将其从 0 修改至 1，则消耗金币远程兑换允许发弹量。此后哨兵可将其从 1 修改至 2，以此类推。bit 17-20：哨兵远程兑换血量的请求次数，开局为 0，修改此值即可请求远程兑换血量。此值的变化需要单调递增且每次仅能增加 1，否则视为不合法。示例：此值开局仅能为 0，此后哨兵可将其从 0 修改至 1，则消耗金币远程兑换血量。此后哨兵可将其从 1 修改至 2，以此类推。在哨兵发送该子命令时，服务器将按照从相对低位到相对高位的原则依次处理这些指令，直至全部成功或不能处理为止。示例：若队伍金币数为 0，此时哨兵战亡，“是否确认复活”的值为 1，“是否确认兑换立即复活”的值为 1，“确认兑换的允许发弹量值”为 100。（假定之前哨兵未兑换过允许发弹量）由于此时队伍金币数不足以使哨兵兑换立即复活，则服务器将会忽视后续指令，等待哨兵发送的下一组指令。bit 21-23：哨兵修改当前姿态指令，1 为进攻姿态，2 为防御姿态，3 为移动姿态，4 为强化进攻姿态，5 为强化防御姿态，6 为强化移动姿态。默认为 3；修改此值即可改变哨兵姿态。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>● bit 24: 哨兵机器人是否确认使能量机关进入正在激活状态，1 为确认。默认为 0。\n● bit 25-31: 保留位。</td></tr><tr><td colspan="4">typedef _packed struct\n{\n    uint32_t sentry_cmd;\n} sentry_cmd_t;</td></tr></table>








<div style="text-align: center;"><div style="text-align: center;">表 1-34 雷达自主决策指令：0x0121</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>字节偏移量</td><td style='text-align: center; word-wrap: break-word;'>大小</td><td style='text-align: center; word-wrap: break-word;'>说明</td><td style='text-align: center; word-wrap: break-word;'>备注</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>雷达是否确认触发双倍易伤</td><td style='text-align: center; word-wrap: break-word;'>开局为0，修改此值即可请求触发双倍易伤，若此时雷达拥有触发双倍易伤的机会，则可触发。此值的变化需要单调递增且每次仅能增加1，否则视为不合法。示例：此值开局仅能为0，此后雷达可将其从0修改至1，若雷达拥有触发双倍易伤的机会，则触发双倍易伤。此后雷达可将其从1修改至2，以此类推。若雷达请求双倍易伤时，双倍易伤正在生效，则第二次双倍易伤将在第一次双倍易伤结束后生效。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>7</td><td style='text-align: center; word-wrap: break-word;'>密钥更新或验证指令</td><td style='text-align: center; word-wrap: break-word;'>每个字节均为ASCII码编码的字母或数字。开局为随机值。byte1为指令类型，byte2-7为密钥值。当byte1值为1时，修改此值即可更新己方加密密钥；当byte1值为2时，修改此值即可将雷达破解的对方密钥传输给服务器以验证是否正确破解。注意：● 仅开局和每次对方破解成功使得加密等级（己方干扰波难度）提高时可以修改密钥，其余时间修改无效。（即使不主动修改，密钥也将重置为一个新的随机值）。● 当byte1值为2时，每次更新验证密钥后的10秒内，再次更新无效。</td></tr></table>

typedef _packed struct
{
    uint8_t radar_cmd;
    uint8_t password_cmd;
    uint8_t password_1;
    uint8_t password_2;
    uint8_t password_3;
    uint8_t password_4;
    uint8_t password_5;
    uint8_t password_6;
} radar_cmd_t;

#### 1.3 小地图交互数据

#### 1.3.1 选手端下发数据

云台手可通过选手端大地图向机器人发送固定数据。

命令码为 0x0303，触发时发送，两次发送间隔不得低于 0.5 秒。

发送方式一：

① 点击己方机器人头像；

②（可选）按下一个键盘按键或点击对方机器人头像；

③ 点击小地图任意位置。该方式向己方选定的机器人发送地图坐标数据，若点击对方机器人头像，则以目标机器人ID代替坐标数据。

##### 发送方式二：

① （可选）按下一个键盘按键或点击对方机器人头像；

② 点击小地图任意位置。该方式向己方所有机器人发送地图坐标数据，若点击对方机器人头像，则以目标机器人 ID 代替坐标数据。

半自动控制方式的机器人对应的操作手可通过选手端大地图向机器人发送固定数据。

命令码为 0x0303，触发时发送，两次发送间隔不得低于 3 秒。

##### 发送方式：

① （可选）按下一个键盘按键或点击对方机器人头像；

② 点击小地图任意位置。该方式向操作手对应的机器人发送地图坐标数据，若点击对方机器人头像，则以目标机器人 ID 代替坐标数据。

一台半自动控制方式的机器人既可以接收云台手发送的信息，也可以接收对应操作手的信息。两种信息的

来源将在下表中“信息来源”中进行区别。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//7351df97-5a1f-4fdd-b749-ee13b82a9646/markdown_1/imgs/img_in_image_box_133_269_178_312.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A46Z%2F-1%2F%2F35f6b85ffaf9000afe0d005e55987a338c70fe293699037c2679fc8ae3b2b4d3" alt="Image" width="3%" /></div>


为降低机器人串口接收设备的偶发不稳定性对通信的影响，0x0303 协议的发送机制有所特殊处理，具体如下：选手端触发 1 次发送后，服务器将以 100ms 的间隔向机器人额外发送 4 次，共 5 次。此后，直到下一次选手端触发发送前，服务器都将以 1Hz 的频率持续定频发送最近一次的包。触发时的连续发送和 1Hz 定频发送计时相互独立。队伍需关注多次收到重复协议内容的处理方式。

<div style="text-align: center;"><div style="text-align: center;">表 1-35 命令码 ID: 0x0303</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>字节偏移量</td><td style='text-align: center; word-wrap: break-word;'>大小</td><td style='text-align: center; word-wrap: break-word;'>说明</td><td style='text-align: center; word-wrap: break-word;'>备注</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0</td><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>目标位置 x 轴坐标，单位 m</td><td style='text-align: center; word-wrap: break-word;'>当发送目标机器人 ID 时，该值为 0</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>目标位置 y 轴坐标，单位 m</td><td style='text-align: center; word-wrap: break-word;'>当发送目标机器人 ID 时，该值为 0</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>8</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>云台手按下的键盘按键通用键值</td><td style='text-align: center; word-wrap: break-word;'>无按键按下，则为 0</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>9</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>对方机器人 ID</td><td style='text-align: center; word-wrap: break-word;'>当发送坐标数据时，该值为 0</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>10</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>信息来源 ID</td><td style='text-align: center; word-wrap: break-word;'>信息来源的 ID，ID 对应关系详见附录</td></tr><tr><td colspan="4">typedef _packed struct\n{\n    float target_position_x;\n    float target_position_y;\n    uint8_t cmd_keyboard;\n    uint8_t target_robot_id;\n    uint16_t cmd_source;\n} map_command_t;</td></tr></table>

#### 1.3.2 选手端接收数据

选手端小地图可接收机器人数据。

雷达可通过常规链路向己方所有选手端发送双方机器人的坐标数据，该位置会在己方选手端小地图显示。

<div style="text-align: center;"><div style="text-align: center;">表 1-36 命令码 ID: 0x0305</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>字节偏移量</td><td style='text-align: center; word-wrap: break-word;'>大小</td><td style='text-align: center; word-wrap: break-word;'>说明</td><td style='text-align: center; word-wrap: break-word;'>备注</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>对方英雄机器人 x 位置坐标，单位：cm</td><td rowspan="2"></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>对方英雄机器人 y 位置坐标，单位：cm</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>对方工程机器人x位置坐标，单位：cm</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>6</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>对方工程机器人y位置坐标，单位：cm</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>8</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>对方3号步兵机器人x位置坐标，单位：cm</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>10</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>对方3号步兵机器人y位置坐标，单位：cm</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>12</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>对方4号步兵机器人x位置坐标，单位：cm</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>14</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>对方4号步兵机器人y位置坐标，单位：cm</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>16</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>对方6号空中机器人x位置坐标，单位：cm</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>18</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>对方6号空中机器人y位置坐标，单位：cm</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>20</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>对方哨兵机器人x位置坐标，单位：cm</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>22</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>对方哨兵机器人y位置坐标，单位：cm</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>24</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>己方英雄机器人x位置坐标，单位：cm</td><td rowspan="2">当x、y超出边界时显示在对应边缘处，当x、y均为0时，视为未发送此机器人坐标。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>26</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>己方英雄机器人y位置坐标，单位：cm</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>28</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>己方工程机器人x位置坐标，单位：cm</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>30</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>己方工程机器人y位置坐标，单位：cm</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>32</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>己方3号步兵机器人x位置坐标，单位：cm</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>34</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>己方3号步兵机器人y位置坐标，单位：cm</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>36</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>己方4号步兵机器人x位置坐标，单位：cm</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>38</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>己方4号步兵机器人y位置坐标，单位：cm</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>40</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>己方6号空中机器人x位置坐标，单位：cm</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>42</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>己方6号空中机器人y位置坐标，单位：cm</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>44</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>己方哨兵机器人x位置坐标，单位：cm</td><td style='text-align: center; word-wrap: break-word;'></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>46</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>己方哨兵机器人y位置坐标，单位：cm</td><td style='text-align: center; word-wrap: break-word;'></td></tr></table>





ROBOMASTER

typedef _packed struct

uint16_t opponent_hero_position_x;

uint16_t opponent_hero_position_y;

uint16_t opponent_engineer_position_x;

uint16_t opponent_engineer_position_y;

uint16_t opponent_infantry_3_position_x;

uint16_t opponent_infantry_3_position_y;

uint16_t opponent_infantry_4_position_x;

uint16_t opponent_infantry_4_position_y;

uint16_t opponent_aerial_position_x;

uint16_t opponent_aerial_position_y;

uint16_t opponent_sentry_position_x;

uint16_t opponent_sentry_position_y;

uint16_t ally_hero_position_x;

uint16_t ally_hero_position_y;

uint16_t ally_engineer_position_x;

uint16_t ally_engineer_position_y;

uint16_t ally_infantry_3_position_x;

uint16_t ally_infantry_3_position_y;

uint16_t ally_infantry_4_position_x;

uint16_t ally_infantry_4_position_y;

uint16_t ally_aerial_position_x;

uint16_t ally_aerial_position_y;

uint16_t ally_sentry_position_x;

uint16_t ally_sentry_position_y;

}map_robot_data_t;

哨兵机器人或半自动控制方式的机器人可通过常规链路向对应的操作手选手端发送路径坐标数据，该路径会在小地图上显示。

<div style="text-align: center;"><div style="text-align: center;">表 1-37 命令码 ID: 0x0307</div> </div>




<table border="1" style="margin: auto; word-wrap: break-word;"><tr><td style="text-align: center; word-wrap: break-word;">字节偏移量</td><td style="text-align: center; word-wrap: break-word;">大小</td><td style="text-align: center; word-wrap: break-word;">说明</td><td style="text-align: center; word-wrap: break-word;">备注</td></tr><tr><td style="text-align: center; word-wrap: break-word;">0</td><td style="text-align: center; word-wrap: break-word;">1</td><td style="text-align: center; word-wrap: break-word;">1：到目标点攻击\n2：到目标点防守\n3：移动到目标点</td><td style="text-align: center; word-wrap: break-word;">-</td></tr><tr><td style="text-align: center; word-wrap: break-word;">1</td><td style="text-align: center; word-wrap: break-word;">2</td><td style="text-align: center; word-wrap: break-word;">路径起点 x 轴坐标，单位：dm</td><td rowspan="2">小地图左下角为坐标原点，水平向右为 X 轴正方向，竖直向上为 Y 轴正方向。显示位置将按照场地尺寸与小地图尺寸等比缩放，超出边界的位置将在边界处显示</td></tr><tr><td style="text-align: center; word-wrap: break-word;">3</td><td style="text-align: center; word-wrap: break-word;">2</td><td style="text-align: center; word-wrap: break-word;">路径起点 y 轴坐标，单位：dm</td></tr><tr><td style="text-align: center; word-wrap: break-word;">5</td><td style="text-align: center; word-wrap: break-word;">49</td><td style="text-align: center; word-wrap: break-word;">路径点 x 轴增量数组，单位：dm</td><td rowspan="2">增量相较于上一个点位进行计算，共 49 个新点位，X 与 Y 轴增量对应组成点位</td></tr><tr><td style="text-align: center; word-wrap: break-word;">54</td><td style="text-align: center; word-wrap: break-word;">49</td><td style="text-align: center; word-wrap: break-word;">路径点 y 轴增量数组，单位：dm</td></tr><tr><td style="text-align: center; word-wrap: break-word;">103</td><td style="text-align: center; word-wrap: break-word;">2</td><td style="text-align: center; word-wrap: break-word;">发送者 ID</td><td style="text-align: center; word-wrap: break-word;">需与自身 ID 匹配，ID 编号详见附录</td></tr></table>




typedef _packed struct
{
    uint8_t intention;
    uint16_t start_position_x;
    uint16_t start_position_y;
    int8_t delta_x[49];
    int8_t delta_y[49];
    uint16_t sender_id;
}map_data_t;

己方机器人可通过常规链路向己方任意选手端发送自定义的消息，该消息会在己方选手端特定位置显示。

<div style="text-align: center;"><div style="text-align: center;">表 1-38 命令码 ID: 0x0308</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>字节偏移量</td><td style='text-align: center; word-wrap: break-word;'>大小</td><td style='text-align: center; word-wrap: break-word;'>说明</td><td style='text-align: center; word-wrap: break-word;'>备注</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>发送者的 ID</td><td style='text-align: center; word-wrap: break-word;'>需要校验发送者的 ID 正确性</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>接收者的 ID</td><td style='text-align: center; word-wrap: break-word;'>需要校验接收者的 ID 正确性，仅支持发送者已方选手端</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>30</td><td style='text-align: center; word-wrap: break-word;'>字符</td><td style='text-align: center; word-wrap: break-word;'>以 utf-16 格式编码发送，支持显示中文。编码发送时请注意数据的大小端问题</td></tr></table>

typedef _packed struct

uint16_t sender_id;

uint16_t receiver_id;
uint8_t user_data[30];
}custom_info_t;

#### 1.5 非链路数据说明

操作手可使用自定义控制器模拟键鼠操作选手端。

<div style="text-align: center;"><div style="text-align: center;">表 1-43 命令码 ID: 0x0306</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>字节偏移量</td><td style='text-align: center; word-wrap: break-word;'>大小</td><td style='text-align: center; word-wrap: break-word;'>说明</td><td style='text-align: center; word-wrap: break-word;'>备注</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>键盘键值:\n• bit 0-7: 按键 1 键值\n• bit 8-15: 按键 2 键值</td><td style='text-align: center; word-wrap: break-word;'>• 仅响应选手端开放的按键\n• 使用通用键值，支持 2 键无冲，键值顺序变更不会改变按下状态，若无新的按键信息，将保持上一帧数据的按下状态</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>• bit 0-11: 鼠标 X 轴像素位置\n• bit 12-15: 鼠标左键状态</td><td rowspan="2">• 位置信息使用绝对像素点值（赛事客户端使用的分辨率为  $ 1920 \times 1080 $，屏幕左上角为 (0, 0))\n• 鼠标按键状态 1 为按下，其他值为未按下，仅在出现鼠标图标后响应该信息，若无新的鼠标信息，选手端将保持上一帧数据的鼠标信息，当鼠标图标消失后该数据不再保持</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>• bit 0-11: 鼠标 Y 轴像素位置\n• bit 12-15: 鼠标右键状态</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>6</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>保留位</td><td style='text-align: center; word-wrap: break-word;'>-</td></tr></table>

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//aecb601c-bb11-4bc5-8121-897fb3474cd0/markdown_3/imgs/img_in_image_box_133_160_177_206.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A46Z%2F-1%2F%2Faded69f6b9e7c7dfdde2e1210ff595b75e2ddd887034e9456b0255b82a224a53" alt="Image" width="3%" /></div>


一次鼠标移动点击需要先发送鼠标未按下及指定位置的数据帧，再发送保持该位置时按下鼠标的数据帧，最后发送保持该位置时鼠标未按下的数据帧

typedef _packed struct
{
    uint16_t key_value;
    uint16_t x_position:12;
    uint16_t mouse_left:4;
    uint16_t y_position:12;
    uint16_t mouse_right:4;
    uint16_t reserved;
}custom_client_data_t;

#### 1.6 雷达无线链路数据说明

<div style="text-align: center;"><div style="text-align: center;">表 1-44 命令码 ID: 0x0A01</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>字节偏移量</td><td style='text-align: center; word-wrap: break-word;'>大小</td><td style='text-align: center; word-wrap: break-word;'>说明</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>对方英雄机器人位置 x 轴坐标，单位：cm</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>对方英雄机器人位置 y 轴坐标，单位：cm</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>对方工程机器人位置 x 轴坐标，单位：cm</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>6</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>对方工程机器人位置 y 轴坐标，单位：cm</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>8</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>对方 3 号步兵机器人位置 x 轴坐标，单位：cm</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>10</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>对方 3 号步兵机器人位置 y 轴坐标，单位：cm</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>12</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>对方 4 号步兵机器人位置 x 轴坐标，单位：cm</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>14</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>对方 4 号步兵机器人位置 y 轴坐标，单位：cm</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>16</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>对方空中机器人位置 x 轴坐标，单位：cm</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>18</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>对方空中机器人位置 y 轴坐标，单位：cm</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>20</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>对方哨兵机器人位置 x 轴坐标，单位：cm</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>22</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>对方哨兵机器人位置 y 轴坐标，单位：cm</td></tr></table>

<div style="text-align: center;"><div style="text-align: center;">表 1-45 命令码 ID: 0x0A02</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>字节偏移量</td><td style='text-align: center; word-wrap: break-word;'>大小</td><td style='text-align: center; word-wrap: break-word;'>说明</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>对方 1 号英雄机器人血量，若该机器人未上场或者被罚下，则血量为 0，下文同理</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>对方 2 号工程机器人血量</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>对方 3 号步兵机器人血量</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>6</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>对方 4 号步兵机器人血量</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>8</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>保留位</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>10</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>对方 7 号哨兵机器人血量</td></tr></table>

<div style="text-align: center;"><div style="text-align: center;">表 1-46 命令码 ID: 0x0A03</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>字节偏移量</td><td style='text-align: center; word-wrap: break-word;'>大小</td><td style='text-align: center; word-wrap: break-word;'>说明</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>对方 1 号英雄机器人允许发弹量</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>对方 3 号步兵机器人允许发弹量（含堡垒提供的储备允许发弹量，下同）</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>对方 4 号步兵机器人允许发弹量</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>6</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>对方 6 号空中机器人允许发弹量</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>8</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>对方 7 号哨兵机器人允许发弹量</td></tr></table>

<div style="text-align: center;"><div style="text-align: center;">表 1-47 命令码 ID: 0x0A04</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>字节偏移量</td><td style='text-align: center; word-wrap: break-word;'>大小</td><td style='text-align: center; word-wrap: break-word;'>说明</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>对方剩余金币数</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>对方累计总金币数</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>● bit 0：对方补给区占领状态\n● bit 1-2：对方中央高地的占领状态，1 为被对方占领，2 为被己方占领\n● bit 3：对方梯形高地的占领状态，1 为已占领\n● bit 4-5：对方堡垒增益点的占领状态，0 为未被占领，1 为被对方占领，2 为被己方占领，3 为被双方占领</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>● bit 6-7：对方前哨站增益点的占领状态，0 为未被占领，1 为被对方占领，2 为被己方占领\n● bit 8：对方基地增益点的占领状态，1 为已占领\n● bit 9：靠近对方一侧飞坡前地形跨越增益点（隧道）中心处场地交互模块卡的状态，1 为检测到对方机器人场地交互模块\n● bit 10：靠近对方一侧飞坡后地形跨越增益点（隧道）中心处场地交互模块卡的状态，1 为检测到对方机器人场地交互模块\n● bit 11：靠近己方一侧飞坡前地形跨越增益点（隧道）中心处场地交互模块卡的状态，1 为检测到对方机器人场地交互模块\n● bit 12：靠近己方一侧飞坡后地形跨越增益点（隧道）中心处场地交互模块卡的状态，1 为检测到对方机器人场地交互模块\n● bit 13：对方地形跨越增益点（高地）上部场地交互模块卡的状态，1 为检测到对方机器人场地交互模块\n● bit 14：对方地形跨越增益点（飞坡）后部场地交互模块卡的状态，1 为检测到对方机器人场地交互模块\n● bit 15：对方地形跨越增益点（公路）上部场地交互模块卡的状态，1 为检测到对方机器人场地交互模块</td></tr></table>





<div style="text-align: center;"><div style="text-align: center;">表 1-48 命令码 ID: 0x0A05</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>字节偏移量</td><td style='text-align: center; word-wrap: break-word;'>大小</td><td style='text-align: center; word-wrap: break-word;'>说明</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>对方英雄机器人回血增益（百分比，值为 10 表示每秒恢复血量上限的 10%，下同）</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>对方英雄机器人射击热量冷却增益具体值（直接值，值为 x 表示热量冷却增加 x/s，下同）</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>3</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>对方英雄机器人防御增益（百分比，值为 50 表示 50% 防御增益，下同）</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>对方英雄机器人负防御增益（百分比，值为 30 表示-30% 防御增益，下同）</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>5</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>对方英雄机器人攻击增益（百分比，值为 50 表示 50% 攻击增益，下同）</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>7</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>对方工程机器人回血增益</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>8</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>对方工程机器人射击热量冷却增益具体值</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>10</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>对方工程机器人防御增益</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>11</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>对方工程机器人负防御增益</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>12</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>对方工程机器人攻击增益</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>14</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>对方3号步兵机器人回血增益</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>15</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>对方3号步兵机器人射击热量冷却增益具体值</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>17</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>对方3号步兵机器人防御增益</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>18</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>对方3号步兵机器人负防御增益</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>19</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>对方3号步兵机器人攻击增益</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>21</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>对方4号步兵机器人回血增益</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>22</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>对方4号步兵机器人射击热量冷却增益具体值</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>24</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>对方4号步兵机器人防御增益</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>25</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>对方4号步兵机器人负防御增益</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>26</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>对方4号步兵机器人攻击增益</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>28</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>对方哨兵机器人回血增益</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>29</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>对方哨兵机器人射击热量冷却增益具体值</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>31</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>对方哨兵机器人防御增益</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>32</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>对方哨兵机器人负防御增益</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>33</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>对方哨兵机器人攻击增益</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>35</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>对方哨兵机器人当前姿态（1为进攻姿态，2为防御姿态，3为移动姿态，4为强化进攻姿态，5为强化防御姿态，6为强化移动姿态）</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>36</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>对方英雄机器人主要状态（0为存活，1为战亡，2为无敌但不虚弱，3为无敌且虚弱，异常离线不会影响此处的状态判断，下同）</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>37</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>对方工程机器人主要状态</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>38</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>对方3号步兵机器人主要状态</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>39</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>对方4号步兵机器人主要状态</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>40</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>对方哨兵机器人主要状态</td></tr></table>








<div style="text-align: center;"><div style="text-align: center;">表 1-49 命令码 ID: 0x0A06</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>字节偏移量</td><td style='text-align: center; word-wrap: break-word;'>大小</td><td style='text-align: center; word-wrap: break-word;'>说明</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0</td><td style='text-align: center; word-wrap: break-word;'>6</td><td style='text-align: center; word-wrap: break-word;'>每个字节均为 ASCII 码编码的字母或数字。</td></tr></table>




### 附录二：ID 编号说明

机器人ID编号如下所示：

1: 红方英雄机器人

2：红方工程机器人

3/4/5：红方步兵机器人（与机器人ID3~5对应）

6：红方空中机器人

7：红方哨兵机器人

8: 红方飞镖

9：红方雷达

10: 红方基地

11：红方前哨站

101：蓝方英雄机器人

102：蓝方工程机器人

103/104/105：蓝方步兵机器人（与机器人ID3~5对应）

106：蓝方空中机器人

107：蓝方哨兵机器人

108：蓝方飞镖

109：蓝方雷达

110：蓝方基地

111：蓝方前哨站

选手端ID如下所示：

0x0101：红方英雄机器人选手端

0x0102：红方工程机器人选手端

0x0103/0x0104/0x0105：红方步兵机器人选手端（与机器人ID3~5对应）

0x0106：红方空中机器人选手端

0x016A：蓝方空中机器人选手端

0x0165：蓝方英雄机器人选手端

0x0166：蓝方工程机器人选手端

0x0167/0x0168/0x0169：蓝方步兵机器人选手端（与机器人ID3~5对应）

0x8080：裁判系统服务器（用于哨兵和雷达自主决策指令）