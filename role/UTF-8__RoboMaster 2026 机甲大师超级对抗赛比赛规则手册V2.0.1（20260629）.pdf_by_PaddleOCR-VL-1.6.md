<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//f16ffcaa-fb24-44cd-99d2-a9a26574b33a/markdown_0/imgs/img_in_image_box_1_9_1191_1093.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A44Z%2F-1%2F%2F3144edf118e6db84154b6e8b80f43375011d23876524d407dd615f9af1080641" alt="Image" width="99%" /></div>


# 第二十五届全国大学生机器人大赛 ROBOMASTER 2026 机甲大师超级对抗赛

比赛规则手册

RoboMaster 组委会 编制

2026年6月发布

## 知识产权声明

RoboMaster 组委会（RMOC，RoboMaster Organizing Committee）鼓励并倡导技术创新以及技术开源，并尊重参赛队伍的知识产权。参赛队伍比赛中开发的所有知识产权均归所在队伍所有，组委会不参与处理队伍内部成员之间的知识产权纠纷，参赛队伍须妥善处理本队内部学校成员、企业成员及其他身份的成员之间对知识产权的所有关系。

参赛队伍在使用组委会提供的裁判系统及赛事支持物资过程中，需尊重原产品的所有知识产权归属方，不得针对产品进行反向工程、复制、翻译等任何有损于归属方知识产权的行为。

任何损害组委会及承办单位提供的赛事教育产品知识产权行为，知识产权归属方将依法追究法律责任。

开源资料的相关建议请参阅：https://bbs.robomaster.com/article/4820

## 阅读提示

RoboMaster 比赛为机器人赛事，宗旨是培养青年工程师人才，相关文件中可能涉及敏感用词、名称、操作、技术等内容，这些内容不反映任何现实中存在的技术或行动，也无意涉及任何特定的国家、组织或个人。本手册旨在阐述机器人比赛规则，不得用于 RoboMaster 比赛以外的任何其他目的，不应被认为与真实事件或实体有任何关联。

### 版本号说明

比赛规则文件的版本号采用语义化版本号格式，即 X.Y.Z，具体含义如下：

X：不同赛事阶段的更新（区域赛固定为1，全国赛固定为2，具体年份体现在文件名以及封面中）。

Y：机制、场地等重要内容的更新，例如：比赛机制变更、机器人属性变更。

Z：不改变原有机制、场地的情况下，错误的修正，例如：修正某个错别字、调整某句有歧义的内容、替换某张错误的图纸。

示例：

某赛季的第一版手册（面向区域赛），版本号为：V1.0.0。

在第一版基础上（面向区域赛），调整了部分比赛机制，版本号为：V1.1.0。

在第二版基础上（面向区域赛），修改了3个错别字，版本号为：V1.1.1。

在第三版的基础上（面向全国赛），调整了部分比赛机制，版本号为：V2.0.0。

### 场地图纸图例说明



<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//f16ffcaa-fb24-44cd-99d2-a9a26574b33a/markdown_2/imgs/img_in_image_box_140_238_352_333.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A45Z%2F-1%2F%2F9c7fd06681c592f28a5dd72d4c7bd269430a18ce80afefb8e2859c070f52b68c" alt="Image"" /></td><td style='text-align: center; word-wrap: break-word;'><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//f16ffcaa-fb24-44cd-99d2-a9a26574b33a/markdown_2/imgs/img_in_image_box_489_237_701_335.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A45Z%2F-1%2F%2F179e7d02208ea306659e01ff739d68c653ce9dbe5cf1c71725c10b51b0a93b48" alt="Image"" /></td><td style='text-align: center; word-wrap: break-word;'><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//f16ffcaa-fb24-44cd-99d2-a9a26574b33a/markdown_2/imgs/img_in_image_box_832_237_1052_335.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A45Z%2F-1%2F%2Fd122be1662443a97daf52a6ce02a2c6f36b8e4fd69a04e99d2463a33cb27a6b1" alt="Image"" /></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>双方增益点</td><td style='text-align: center; word-wrap: break-word;'>单方增益点</td><td style='text-align: center; word-wrap: break-word;'>双方禁区</td></tr><tr><td style='text-align: center; word-wrap: break-word;'><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//f16ffcaa-fb24-44cd-99d2-a9a26574b33a/markdown_2/imgs/img_in_image_box_136_438_360_536.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A45Z%2F-1%2F%2Fb3731b0781649516b339cfa699995c8d8530bce6f95574342a3cca650d6a9179" alt="Image"" /></td><td style='text-align: center; word-wrap: break-word;'><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//f16ffcaa-fb24-44cd-99d2-a9a26574b33a/markdown_2/imgs/img_in_image_box_567_434_618_530.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A45Z%2F-1%2F%2Fe8b6dff5498bbedc4215d431126f5357d4289d6ab4976d342e866003d9207fa0" alt="Image"" /></td><td style='text-align: center; word-wrap: break-word;'><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//f16ffcaa-fb24-44cd-99d2-a9a26574b33a/markdown_2/imgs/img_in_image_box_849_444_1031_527.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A45Z%2F-1%2F%2Fb5a4747e1ea6a87fd5dbed1f73e83658a38ea62f4f3be8b3b81c195a296bab53" alt="Image"" /></td></tr><tr><td style='text-align: center; word-wrap: break-word;'>单方禁区</td><td style='text-align: center; word-wrap: break-word;'>战场地面所在的水平面，是战场的最低平面</td><td style='text-align: center; word-wrap: break-word;'>尺寸仅供参考</td></tr></table>

### 修改日志



<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>日期</td><td style='text-align: center; word-wrap: break-word;'>版本</td><td style='text-align: center; word-wrap: break-word;'>修改记录</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>2026.06.29</td><td style='text-align: center; word-wrap: break-word;'>V2.0.1</td><td style='text-align: center; word-wrap: break-word;'>修改英雄机器人各等级对应的射击热量上限，详见“5.4.2 性能体系”</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>2026.06.26</td><td style='text-align: center; word-wrap: break-word;'>V2.0.0</td><td style='text-align: center; word-wrap: break-word;'>● 修改英雄机器人各等级对应的上限血量，详见“5.4.2 性能体系”\n● 修改大能量机关机制，详见“5.5.2 能量机关机制”\n● 修改英雄机器人部署模式机制，详见“5.6.1 英雄机器人特殊机制”\n● 修改空中机器人被雷达反制机制，详见“5.6.3 空中机器人特殊机制”\n● 修改堡垒增益点机制，详见“5.5.3.9 堡垒增益点机制”\n● 新增哨兵机器人强化姿态机制，详见“5.6.4 哨兵机器人特殊机制”\n● 删除“基地血量降至 2000 及以下时，基地护甲将展开”的机制\n● 修改雷达解析电磁波参数，详见“表 5-23 电磁波参数”\n● 修改赛前检录流程，详见“图 6-2 赛前检录流程图”\n● 修改技术暂停安排，详见“6.3.2 参赛队伍技术暂停”\n● 增加判罚细则\n● 更新部分场地图纸</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>● 优化部分内容的语言表述</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>2026.05.19</td><td style='text-align: center; word-wrap: break-word;'>V1.5.0</td><td style='text-align: center; word-wrap: break-word;'>更新基地防御机制</td></tr><tr><td rowspan="5">2026.04.30</td><td rowspan="5">V1.4.2</td><td style='text-align: center; word-wrap: break-word;'>● 修改关于科技核心卡死异常情况的处理方式</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>● 增加禁止能量单元重复使用的判罚细则</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>● 增加关于隧道检测需机器人缓慢通过的描述</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>● 补充基地与前哨站装甲模块中心矩形区域的部分尺寸，详见“图 5-16 矩形区域示意图”</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>● 补充和修正多处描述</td></tr><tr><td rowspan="4">2026.04.17</td><td rowspan="4">V1.4.1</td><td style='text-align: center; word-wrap: break-word;'>● 能量单元装配步骤 2 增加运动阻力说明</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>● 能量单元装配步骤 5 增加安全锁和运动阻力矩说明</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>● 更新雷达基座示意图</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>● 更新判负处理</td></tr><tr><td rowspan="2">2026.03.20</td><td rowspan="2">V1.4.0</td><td style='text-align: center; word-wrap: break-word;'>● 修改雷达解析电磁波相关机制，详见“5.6.6 雷达特殊机制”</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>● 补充雷达解析电磁波详细频谱分布，空口帧结构，时域特征等信息，详见“附录 1 雷达信息波特性”</td></tr><tr><td rowspan="6">2026.02.09</td><td rowspan="6">V1.3.0</td><td style='text-align: center; word-wrap: break-word;'>● 补充雷达解析电磁波机制中部分参数</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>● 完善能量单元装配流程描述</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>● 修改雷达反制空中机器人机制</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>● 修改科技核心四级装配难度两个科技核心的相对位置关系</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>● 增加科技核心四级装配各步骤时间差的要求</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>● 补充和修正多处描述</td></tr><tr><td rowspan="2">2025.12.30</td><td rowspan="2">V1.2.0</td><td style='text-align: center; word-wrap: break-word;'>● 补充装配区部分尺寸，详见“图 4-29 装配区轴测图”</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>● 修正科技核心-能量单元机制中步骤五的描述和图纸错误，详见“图 5-15 步骤 5 示意图”及上方的步骤描述</td></tr></table>







<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>日期</td><td style='text-align: center; word-wrap: break-word;'>版本</td><td style='text-align: center; word-wrap: break-word;'>修改记录</td></tr><tr><td rowspan="2">2025.12.25</td><td rowspan="2">V1.1.0</td><td style='text-align: center; word-wrap: break-word;'>● 补充空中机器人被雷达反制相关机制，详见“5.6.3 空中机器人特殊机制”\n● 补充雷达解析电磁波相关机制，详见“5.6.6 雷达特殊机制”\n● 调整裁判系统机载端模块安装不规范的相关判罚，详见“7.2.1.1 通用规范”\n● 补充场地道具训练示意图，详见“场地道具训练”</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>● 调整操作手的人员范围\n● 补充场地地胶、场地倾斜相关信息\n● 调整装配区、补给区增益点、地形跨越增益点的范围\n● 补充资源站、装配区相关信息以及能量单元-科技核心相关机制\n● 调整基地、前哨站的装甲模块的形状和尺寸\n● 调整射击热量超限的界面遮挡惩罚机制，同时补充不同机制下界面遮挡的细则\n● 调整飞镖检测模块、基地装甲模块的攻击伤害机制\n● 补充激光检测模块离线的处理方式\n● 调整复活机制\n● 调整17mm允许发弹量的兑换上限\n● 完善大能量机关的灯效说明\n● 优化地形跨越增益点（隧道）、堡垒增益点机制\n● 明确哨兵姿态机制的乘算逻辑\n● 明确附属设备的数量限制\n● 调整场地人员的数量限制\n● 补充队长管理职责的相关判罚\n● 修正若干已知错误，优化部分内容的语言表述</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>2025.10.21</td><td style='text-align: center; word-wrap: break-word;'>V1.0.0</td><td style='text-align: center; word-wrap: break-word;'>首次发布</td></tr></table>

## 目录

知识产权声明 ..... 1    
阅读提示 ..... 1    
版本号说明 ..... 1    
场地图纸图例说明 ..... 2    
修改日志 ..... 2    
1 前言 ..... 14    
1.1 关于比赛 ..... 14    
1.2 关于比赛规则文件 ..... 15    
1.3 关于答疑 ..... 15    
2 重要概念 ..... 17    
3 机器人与操作手 ..... 21    
3.1 英雄机器人 ..... 23    
3.2 工程机器人 ..... 24    
3.3 步兵机器人 ..... 25    
3.4 空中机器人 ..... 27    
3.5 哨兵机器人 ..... 28    
3.6 飞镖系统 ..... 30    
3.7 雷达 ..... 30    
4 比赛场地 ..... 31    
4.1 战场概述 ..... 31    
4.2 基地区域 ..... 37    
4.2.1 启动区 ..... 38    
4.2.2 基地 ..... 38    
4.2.3 飞镖发射站 ..... 41    
4.2.4 停机坪 ..... 43

4.2.5 雷达基座 ..... 43    
4.2.6 补给区 ..... 46    
4.2.7 堡垒 ..... 52    
4.3 高地区 ..... 53    
4.3.1 梯形高地 ..... 53    
4.3.2 中央高地 ..... 54    
4.4 公路区 ..... 59    
4.4.1 起伏路段 ..... 60    
4.4.2 飞坡 ..... 61    
4.5 飞行区 ..... 62    
4.6 其它 ..... 62    
4.6.1 可移动道具 ..... 62    
4.6.2 弹丸 ..... 64    
4.6.3 操作间 ..... 64    
5 比赛机制 ..... 66    
5.1 扣血与超限惩罚机制 ..... 66    
5.1.1 攻击伤害或撞击 ..... 66    
5.1.2 射击初速度超限 ..... 67    
5.1.3 射击热量超限和冷却 ..... 68    
5.1.4 底盘功率超限 ..... 69    
5.1.5 裁判系统模块离线 ..... 69    
5.1.6 判罚伤害 ..... 73    
5.2 回血与复活机制 ..... 73    
5.2.1 回血机制 ..... 73    
5.2.2 复活机制 ..... 74    
5.3 经济体系 ..... 75    
5.3.1 经济体系概述 ..... 75

5.3.2 允许发弹量机制.....77    
5.3.3 科技核心-能量单元机制.....78    
5.4 经验及性能体系.....89    
5.4.1 经验体系.....89    
5.4.2 性能体系.....92    
5.5 场地相关机制.....96    
5.5.1 基地及前哨站机制.....96    
5.5.2 能量机关机制.....99    
5.5.3 场地增益机制.....104    
5.6 机器人特殊机制.....110    
5.6.1 英雄机器人特殊机制.....110    
5.6.2 工程机器人特殊机制.....111    
5.6.3 空中机器人特殊机制.....111    
5.6.4 哨兵机器人特殊机制.....113    
5.6.5 飞镖系统特殊机制.....114    
5.6.6 雷达特殊机制.....116    
5.6.7 能量机制.....120    
5.7 自定义客户端.....121    
5.8 赛制及获胜条件.....121    
6 比赛流程.....123    
6.1 赛前检录.....124    
6.2 候场.....125    
6.3 三分钟准备阶段.....126    
6.3.1 官方技术暂停.....127    
6.3.2 参赛队伍技术暂停.....128    
6.4 十五秒裁判系统自检阶段.....129    
6.5 五秒裁判系统自检阶段.....129

6.6 七分钟比赛阶段 ..... 129    
6.7 比赛结束 ..... 129    
6.8 成绩确认 ..... 129    
6.9 退场 ..... 130    
7 违规与判罚 ..... 131    
7.1 判罚体系 ..... 131    
7.1.1 判罚方式 ..... 131    
7.1.2 判罚类型 ..... 131    
7.2 判罚细则 ..... 134    
7.2.1 人员 ..... 134    
7.2.2 机器人 ..... 137    
7.2.3 交互 ..... 140    
7.3 严重违规 ..... 144    
8 异常情况 ..... 145    
9 申诉 ..... 146    
9.1 申诉流程 ..... 147    
9.2 申诉材料 ..... 147    
9.3 申诉结果 ..... 148    
附录1 雷达信息波特性 ..... 149    
附录2 赛前流程说明 ..... 153    
预检录 ..... 153    
场地道具训练 ..... 153    
适应性训练 ..... 154    
附录3 未来规则规划 ..... 155

### 表目录

表2-1 重要概念一览.....17    
表3-1 机器人阵容.....21    
表3-2 操作手阵容.....22    
表3-3 英雄机器人关键特征.....23    
表3-4 工程机器人关键特征.....24    
表3-5 步兵机器人的关键特征.....25    
表3-6 空中机器人的关键特征.....27    
表3-7 哨兵机器人的关键特征.....28    
表3-8 飞镖系统的关键特征.....30    
表3-9 雷达的关键特征.....30    
表4-1 弹丸参数及使用安排.....64    
表5-1 装甲模块对不同类型弹丸的有效检测速度.....66    
表5-2 攻击伤害或撞击的扣血机制.....67    
表5-3 射击初速度超限惩罚机制.....67    
表5-4 机器人异常离线的惩罚机制.....70    
表5-5 机器人定期获得金币的增量一览.....76    
表5-6 兑换规则.....76    
表5-7 机器人允许发弹量一览.....77    
表5-8 （补给区、基地增益点、前哨站增益点兑换时）不同类型弹丸允许发弹量的最小兑换单位.....77    
表5-9 （远程兑换时）不同类型弹丸允许发弹量的最小兑换单位.....78    
表5-10 科技核心位姿与难度等级关系.....82    
表5-11 科技核心灯效汇总.....85    
表5-12 英雄、步兵、空中机器人的等级和经验.....91    
表5-13 英雄机器人整机属性.....92    
表5-14 步兵机器人底盘属性.....93

表 5-15 步兵机器人 17mm 发射机构属性.....94    
表 5-16 空中机器人 17mm 发射机构属性.....95    
表 5-17 平均环数与对应增益.....101    
表 5-18 激活灯臂数与对应增益持续时间.....101    
表 5-19 增益类型一览.....106    
表 5-20 反制状态与被瞄准难度对应表.....112    
表 5-21 “被标记进度” P 的计算逻辑.....117    
表 5-22 P 的阈值与对应目标获得的效果.....117    
表 5-23 电磁波参数.....118    
表 6-1 故障情况.....127    
表 6-2 复活赛技术暂停安排.....128    
表 6-3 全国赛技术暂停安排.....128    
表 7-1 判罚方式.....131    
表 7-2 判罚类型.....131    
表 7-3 冲撞违规判罚标准.....141    
表 7-4 战场禁区准入规则.....142    
表 7-5 严重违规类型.....144

### 图目录

图 1-1 人才培养理念 ..... 14    
图 4-1 战场俯视渲染图 ..... 31    
图 4-2 战场斜视渲染图 ..... 32    
图 4-3 战场轴测渲染图 ..... 32    
图 4-4 战场模块示意图 ..... 33    
图 4-5 战场模块定位尺寸图 ..... 34    
图 4-6 战场倾斜示意图 ..... 35    
图 4-7 风机示意图 ..... 36    
图 4-8 基地区示意图 ..... 37    
图 4-9 机器人启动区示意图 ..... 38    
图 4-10 基地底座示意图 ..... 38    
图 4-11 基地护甲闭合形态尺寸图 ..... 39    
图 4-12 基地护甲展开形态尺寸图 ..... 39    
图 4-13 飞镖检测模块示意图 ..... 40    
图 4-14 飞镖发射站示意图 ..... 41    
图 4-15 滑台滑出示意图 ..... 42    
图 4-16 滑台尺寸图 ..... 42    
图 4-17 停机坪示意图 ..... 43    
图 4-18 雷达基座示意图 ..... 44    
图 4-19 雷达基座的相对位置示意图 ..... 45    
图 4-20 补给区示意图 ..... 46    
图 4-21 资源站示意图 ..... 47    
图 4-22 能量单元放置区示意图 ..... 48    
图 4-23 视觉标签示意图 ..... 49    
图 4-24 无线充电装置放置区示意图 ..... 50

图4-25 无线充电装置示意图 ..... 51    
图4-26 堡垒示意图 ..... 52    
图4-27 梯形高地示意图 ..... 53    
图4-28 中央高地示意图 ..... 54    
图4-29 装配区轴测图 ..... 55    
图4-30 装配区尺寸图 ..... 55    
图4-31 能量机关示意图 ..... 56    
图4-32 能量机关灯臂尺寸示意图 ..... 57    
图4-33 能量机关中心标识尺寸图 ..... 57    
图4-34 前哨站示意图 ..... 58    
图4-35 公路区示意图 ..... 59    
图4-36 起伏路段示意图 ..... 60    
图4-37 凸起示意图 ..... 60    
图4-38 飞坡示意图 ..... 61    
图4-39 能量单元示意图 ..... 63    
图4-40 主操作间布局示意图 ..... 65    
图5-1 射击热量超限及冷却机制 ..... 68    
图5-2 机器人底盘功率检测及超限惩罚机制 ..... 69    
图5-3 装甲模块和超级电容管理模块离线的扣血机制 ..... 71    
图5-4 测速模块离线的断电机制 ..... 72    
图5-5 机器人图传模块与视觉标签的相对位置示意图 ..... 74    
图5-6 科技核心示意图 ..... 79    
图5-7 科技核心坐标示意图 ..... 80    
图5-8 科技核心MARK灯尺寸示意图 ..... 81    
图5-9 科技核心尺寸示意图 ..... 81    
图5-10 球坐标系示意图 ..... 82    
图5-11 科技核心灯效示意图 ..... 84

图5-12 步骤2示意图 ..... 86      
图5-13 步骤3示意图 ..... 87      
图5-14 步骤4示意图 ..... 87      
图5-15 步骤5示意图 ..... 88      
图5-16 矩形区域示意图 ..... 96      
图5-17 基地、前哨站装甲模块示意图 ..... 98      
图5-18 能量机关击打区域示意图 ..... 100      
图5-19 能量机关未激活状态示意图 ..... 102      
图5-20 小能量机关正在激活状态示意图 ..... 102      
图5-21 大能量机关正在激活状态示意图 ..... 103      
图5-22 能量机关可激活标识示意图 ..... 103      
图5-23 能量机关已激活状态示意图 ..... 104      
图5-24 战场增益点分布示意图 ..... 105      
图5-25 场地交互模块卡铺设示意图 ..... 106      
图5-26 己方可部署区域示意图 ..... 110      
图5-27 激光检测模块缩小区域示意图 ..... 112      
图6-1 单场比赛流程图 ..... 123      
图6-2 赛前检录流程图 ..... 124      
图6-3 准备阶段调试区域示意图 ..... 126      
图7-1 飞行高度限制示意图 ..... 139      
图7-2 战场禁区示意图 ..... 142      
图9-1 申诉流程图 ..... 147

## 1 前言

### 1.1 关于比赛

全国大学生机器人大赛 RoboMaster 机甲大师超级对抗赛（RMUC，RoboMaster University Championship）的核心形式是机器人之间的射击对抗。参赛队伍需自行设计、开发和制作符合规范的多台机器人，组成机器人战队出场比赛。在限时七分钟的比赛中，双方通过操控机器人进行战术对抗，击毁对方基地即可获得比赛胜利。

RMUC 致力于培养优秀青年工程师，鼓励参赛队员将所学知识与实践应用相结合，在参赛过程获得持续成长。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//dcb47d70-f561-471c-9a26-c1f6d9271c1a/markdown_2/imgs/img_in_image_box_260_608_909_1383.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A04%3A22Z%2F-1%2F%2F038fe046b6868bb212b23cdfda4727bb83c69abfdd9f6e41efcf736a7393e3a6" alt="Image" width="54%" /></div>


<div style="text-align: center;"><div style="text-align: center;">图 1-1 人才培养理念</div> </div>


### 1.2 关于比赛规则文件

比赛规则文件含规则手册、参赛手册、机器人制作规范手册、通信协议，及上述文件的增补。比赛规则文件适用于所有参赛队伍、裁判、赛事工作人员及其他合作伙伴。

在备赛期间，组委会将根据实际情况不定期更新比赛规则文件。

在比赛期间，为了让参赛队伍能够充分展示技术成果，组委会可能会在如下节点调整比赛规则，但是不会涉及机器人的直接结构变更。

区域赛期间，单个赛区比赛结束后。

复活赛及全国赛期间，某个赛程阶段（例如：小组赛、16进8）完整结束后。

组委会对比赛规则文件拥有最终解释权。比赛期间，仅裁判长代表组委会对比赛规则文件进行解答，有关比赛规则文件的任何疑问只可以咨询裁判长。

更多关于 RMU 的参考资料，请参阅“规则/资料中心”，该站点由 RoboMaster 组委会建设与维护，集中提供参赛所需的官方资料，旨在帮助队伍高效获取信息。内容覆盖范围：

赛事规则：比赛规则手册、机器人制作规范手册、参赛手册、通信协议。

赛事产品：裁判系统（含机载端模块、赛事引擎）、机器人套件&配件、RM Assistant的产品详情、资料下载、购买&售后政策。

☀️

技术评审：技术评审细则、各环节须知。

品牌宣传：品牌宣传素材包。

● 招商指引：招商手册、招商指南。

培训体系：参赛攻略、课程沙龙、开源资料。

### 1.3 关于答疑

当参赛队伍及其他相关人员对比赛规则文件产生疑问时，可通过官方渠道提出问题，组委会将进行答疑。具体流程如下：

1. 提问者填写问卷，提交问题：

https://qingflow.com/f/c5rf6rkkbs02

2. 组委会将反馈更新至：

https://qingflow.com/appView/c5rf6rkkbs02/shareView/c5rf6slgbs02

时效性说明：

比赛期提交的问题，组委会将在1个自然日内反馈；

备赛期提交的问题，组委会将在5个工作日内反馈。

比赛期：自该赛事的报到日开始，至该赛事最后一个比赛日结束。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//8e3b3378-4451-4f90-9d1c-ed33f67f26ee/markdown_0/imgs/img_in_image_box_128_357_169_397.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A49Z%2F-1%2F%2F0adac39b79b71a99262c8b312df31b1b15fdd77175801ed8fe43460da3b99df7" alt="Image" width="3%" /></div>


备赛期：比赛期以外的时期。

注：不同赛事、赛事阶段的比赛期、备赛期单独计算。

答疑与比赛规则文件具有同等效力。当答疑与比赛规则文件存在差异时，以最新发布的答疑或者比赛规则文件为准。每个赛季的答疑仅适用于当赛季。

## 2 重要概念

本章节将简要说明与比赛规则相关的常见重要概念。关于这些概念的详细内容，请根据关键字索引相关章节。

<div style="text-align: center;"><div style="text-align: center;">表2-1 重要概念一览</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>概念</td><td style='text-align: center; word-wrap: break-word;'>定义</td></tr><tr><td colspan="2">机器人</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>机器人主要状态</td><td style='text-align: center; word-wrap: break-word;'>● 存活：机器人裁判系统主控模块正常连入裁判系统服务器且血量不为 0 的状态。\n➢ 脱战：机器人在存活状态下连续 6 秒未发射弹丸且未被扣血。比赛开始时机器人默认为脱战状态。\n● 战亡：机器人血量为 0 的状态（原因包括：装甲模块被攻击或受撞击、裁判系统模块离线、被罚下、因飞镖导致的血量扣除）。\n➢ 罚下：机器人收到红牌警告的状态。\n➢ 临时激活：当机器人战亡后，其底盘和云台被临时上电的状态。此时该机器人的发射机构为断电状态。\n● 异常离线：比赛过程中，由于机器人断电或其他原因，裁判系统主控模块无法连入裁判系统服务器的状态。\n注：机器人战亡后，裁判系统会切断对机器人的电源输出（除 Mini PC）。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>地面机器人</td><td style='text-align: center; word-wrap: break-word;'>包括英雄机器人、工程机器人、步兵机器人、哨兵机器人。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>裁判系统</td><td style='text-align: center; word-wrap: break-word;'>裁判系统是集成计算、通信、控制于一体的针对机器人比赛的电子判罚系统。其包含机载端以及安装在 PC 物理机上的赛事引擎（服务器、裁判端、选手端），具有监测机器人功率、弹丸发射和伤害、根据比赛规则自动判定胜负等功能。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>多机通信</td><td style='text-align: center; word-wrap: break-word;'>机器人间通过裁判系统串口互相通信的交互方式。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>附属设备</td><td style='text-align: center; word-wrap: break-word;'>附属设备包括：自定义控制器、自定义客户端、无线充电装置（发射端）。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>机器人底盘</td><td style='text-align: center; word-wrap: break-word;'>承载机器人动力系统及其附属部件的机构，支撑机器人机体的机构。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>底盘功率</td><td style='text-align: center; word-wrap: break-word;'>机器人产生水平方向上平移、旋转运动的动力系统的功率，详见《RoboMaster 2026 机甲大师高校系列赛机器人制作规范手册》中“裁判系统安装规范”章节中底盘功率的定义。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>发射机构</td><td style='text-align: center; word-wrap: break-word;'>能够让弹丸以固定路径和一定初速度离开机器人的机构。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>发射机构锁定</td><td style='text-align: center; word-wrap: break-word;'>若发射机构锁定，则其处于断电状态。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>发射机构解锁</td><td style='text-align: center; word-wrap: break-word;'>若发射机构解锁，则根据其允许发弹量情况判定上电或断电。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>发射</td><td style='text-align: center; word-wrap: break-word;'>机器人发出弹丸或飞镖的行为。后文“比赛机制”章节中提到的“发射”以裁判系统检测到发射行为为准。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>射击初速度</td><td style='text-align: center; word-wrap: break-word;'>弹丸或飞镖加速完成后，经过裁判系统相关模块检测到的速度值。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>射击热量</td><td style='text-align: center; word-wrap: break-word;'>射击热量随机器人发弹而增加，用于限制机器人连续发弹。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>允许发弹量</td><td style='text-align: center; word-wrap: break-word;'>每台机器人当前可发射的弹丸数量。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>初始血量</td><td style='text-align: center; word-wrap: break-word;'>比赛开始时，裁判系统为机器人设定的血量值。\n注：裁判系统在结算血量时进行四舍五入，保留整数。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>当前血量</td><td style='text-align: center; word-wrap: break-word;'>机器人的实时血量值。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>上限血量</td><td style='text-align: center; word-wrap: break-word;'>机器人血量可以恢复到的最高值。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>经验值</td><td style='text-align: center; word-wrap: break-word;'>机器人升级所需积累的数值，可通过多种方式获得。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>无敌</td><td style='text-align: center; word-wrap: break-word;'>机器人不受弹丸、飞镖、撞击伤害的状态。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>攻击</td><td style='text-align: center; word-wrap: break-word;'>机器人发射弹丸或飞镖的行为。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>击毁</td><td style='text-align: center; word-wrap: break-word;'>一方机器人攻击对方机器人、基地或者前哨站的装甲模块，致使其血量为0。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>占领</td><td style='text-align: center; word-wrap: break-word;'>存活机器人到达增益点，其场地交互模块检测到该区域内的场地交互模块卡或满足其他条件，且机器人获得一定特殊效果。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>固连</td><td style='text-align: center; word-wrap: break-word;'>比赛过程中，机器人之间产生机构连接，使一台机器人往任意方向移动均与另一台机器人保持机构连接的状态。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>冲撞</td><td style='text-align: center; word-wrap: break-word;'>比赛过程中，一方机器人的主动碰撞行为。</td></tr></table>








<div style="text-align: center;"><div style="text-align: center;">场地</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>增益点</td><td style='text-align: center; word-wrap: break-word;'>比赛过程中，一方机器人占领后会产生一定特殊效果的区域。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>禁区</td><td style='text-align: center; word-wrap: break-word;'>禁止机器人进入的区域。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>场地道具</td><td style='text-align: center; word-wrap: break-word;'>战场的组成元素，包括但不限于：基地、前哨站、能量机关。</td></tr></table>

<div style="text-align: center;"><div style="text-align: center;">人员</div> </div>




<table border="1" style="margin: auto; word-wrap: break-word;"><tr><td style="text-align: center; word-wrap: break-word;">仲裁委员会</td><td style="text-align: center; word-wrap: break-word;">由裁判长以及其他组委会相关负责人组成，负责处理申诉等事项。</td></tr><tr><td style="text-align: center; word-wrap: break-word;">裁判</td><td style="text-align: center; word-wrap: break-word;">维持赛场秩序、执行比赛规则的人员。</td></tr><tr><td style="text-align: center; word-wrap: break-word;">裁判长</td><td style="text-align: center; word-wrap: break-word;">比赛期间，对比赛规则文件拥有最终解释权的人员。</td></tr><tr><td style="text-align: center; word-wrap: break-word;">主裁判</td><td style="text-align: center; word-wrap: break-word;">维持赛场秩序、执行比赛规则的首要裁判。</td></tr><tr><td style="text-align: center; word-wrap: break-word;">检录长</td><td style="text-align: center; word-wrap: break-word;">负责领导和分配检录工作的裁判，对检录标准拥有最终解释权。</td></tr><tr><td style="text-align: center; word-wrap: break-word;">参赛队伍</td><td style="text-align: center; word-wrap: break-word;">本赛季报名且已录入报名系统的队伍。</td></tr><tr><td style="text-align: center; word-wrap: break-word;">参赛人员</td><td style="text-align: center; word-wrap: break-word;">本赛季报名且已录入报名系统的人员。</td></tr><tr><td style="text-align: center; word-wrap: break-word;">场地人员</td><td style="text-align: center; word-wrap: break-word;">本赛季报名且已录入报名系统、可进入候场区和赛场区的正式队员、梯队队员、战队指导和指导老师。</td></tr><tr><td style="text-align: center; word-wrap: break-word;">操作手</td><td style="text-align: center; word-wrap: break-word;">在比赛过程中，负责操控机器人的场地人员，包括地面机器人操作手、云台手、飞手。</td></tr><tr><td style="text-align: center; word-wrap: break-word;">违规方</td><td style="text-align: center; word-wrap: break-word;">违规的参赛队伍。</td></tr><tr><td style="text-align: center; word-wrap: break-word;">违规人员</td><td style="text-align: center; word-wrap: break-word;">违规的参赛人员。</td></tr><tr><td style="text-align: center; word-wrap: break-word;">概念</td><td style="text-align: center; word-wrap: break-word;">定义</td></tr><tr><td colspan="2">比赛流程</td></tr><tr><td style="text-align: center; word-wrap: break-word;">比赛时刻说明</td><td style="text-align: center; word-wrap: break-word;">全文所提及的“X分钟 Y秒”，即倒计时为（6-X）：（59-Y）；\n“X分钟 Y秒至 M分钟 N秒期间”，即倒计时为（6-X）：（59-Y）至（7-M）：（60-N）。\n示例：\n● 比赛开始 5 分钟后，即倒计时为 1:59。\n● 比赛开始后的 2 至 5 分钟期间，即倒计时为 4:59-2:00。</td></tr><tr><td style="text-align: center; word-wrap: break-word;">局</td><td style="text-align: center; word-wrap: break-word;">包含准备阶段、裁判系统自检阶段、五秒倒计时、比赛阶段的完整比赛。</td></tr><tr><td style="text-align: center; word-wrap: break-word;">场</td><td style="text-align: center; word-wrap: break-word;">根据不同的赛制，一场比赛可能包含若干局比赛。</td></tr><tr><td style="text-align: center; word-wrap: break-word;">官方技术暂停</td><td style="text-align: center; word-wrap: break-word;">在准备阶段或者裁判系统自检阶段，主裁判发起的技术暂停。</td></tr><tr><td style="text-align: center; word-wrap: break-word;">参赛队伍技术暂停</td><td style="text-align: center; word-wrap: break-word;">在准备阶段，参赛队伍申请的技术暂停。</td></tr><tr><td style="text-align: center; word-wrap: break-word;">常规战损</td><td style="text-align: center; word-wrap: break-word;">在一场比赛的局间三分钟准备阶段内或七分钟比赛阶段内，裁判系统机载端模块出现故障的情况。</td></tr></table>






<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td colspan="2">胜负判定</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>攻击伤害</td><td style='text-align: center; word-wrap: break-word;'>一方机器人或基地、前哨站受到弹丸或飞镖打击产生的血量扣除。\n注：一方机器人、基地、前哨站因违规判罚导致的扣血计入对方攻击伤害。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>非攻击伤害</td><td style='text-align: center; word-wrap: break-word;'>一方机器人因装甲模块受撞击、裁判系统模块离线等导致的血量扣除。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>基地净胜血量</td><td style='text-align: center; word-wrap: break-word;'>每局比赛结束，己方基地剩余血量减去对方基地剩余血量。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>总剩余血量</td><td style='text-align: center; word-wrap: break-word;'>每局比赛结束，己方所有存活机器人剩余血量的总值。</td></tr></table>

## 3 机器人与操作手

RoboMaster 强调机器人以战队形式参赛，要求机器人之间达到均衡合作。关于机器人制作规范，请参阅《RoboMaster 2026 机甲大师高校系列赛机器人制作规范手册》。

机器人阵容如下所示：

<div style="text-align: center;"><div style="text-align: center;">表3-1 机器人阵容</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>种类</td><td style='text-align: center; word-wrap: break-word;'>编号</td><td style='text-align: center; word-wrap: break-word;'>全阵容数量（台）</td><td style='text-align: center; word-wrap: break-word;'>赛事阶段</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>英雄机器人</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>1</td><td rowspan="7">区域赛、复活赛及全国赛</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>工程机器人</td><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>1</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>步兵机器人</td><td style='text-align: center; word-wrap: break-word;'>3/4</td><td style='text-align: center; word-wrap: break-word;'>2</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>空中机器人</td><td style='text-align: center; word-wrap: break-word;'>6</td><td style='text-align: center; word-wrap: break-word;'>1</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>哨兵机器人</td><td style='text-align: center; word-wrap: break-word;'>7</td><td style='text-align: center; word-wrap: break-word;'>1</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>飞镖系统</td><td style='text-align: center; word-wrap: break-word;'>8</td><td style='text-align: center; word-wrap: break-word;'>1</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>雷达</td><td style='text-align: center; word-wrap: break-word;'>9</td><td style='text-align: center; word-wrap: break-word;'>1</td></tr></table>

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//0e256781-3712-4f59-9bc2-1dc2f90c9e6f/markdown_1/imgs/img_in_image_box_128_978_170_1021.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A51Z%2F-1%2F%2Fff66f4472c9cd0d3fb3154b00f555b86fae8decba6c221559bc9b3f233de3bd3" alt="Image" width="3%" /></div>


操作手阵容如下所示：

<div style="text-align: center;"><div style="text-align: center;">表 3-2 操作手阵容</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>类型</td><td style='text-align: center; word-wrap: break-word;'>所操作的机器人</td><td style='text-align: center; word-wrap: break-word;'>全阵容人数</td></tr><tr><td rowspan="4">地面机器人操作手</td><td style='text-align: center; word-wrap: break-word;'>英雄机器人</td><td style='text-align: center; word-wrap: break-word;'>1</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>工程机器人</td><td style='text-align: center; word-wrap: break-word;'>1</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>步兵机器人</td><td style='text-align: center; word-wrap: break-word;'>2</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>哨兵机器人</td><td style='text-align: center; word-wrap: break-word;'>0</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>云台手</td><td style='text-align: center; word-wrap: break-word;'>空中机器人（可选）、飞镖系统（可选）</td><td style='text-align: center; word-wrap: break-word;'>1</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>飞手</td><td style='text-align: center; word-wrap: break-word;'>空中机器人</td><td style='text-align: center; word-wrap: break-word;'>1</td></tr></table>

操作手只能由本赛季参赛队伍中除指导老师外的场地人员担任。

每局比赛结束后，可以从本场场地人员中除指导老师外的人员中替换操作手。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//0e256781-3712-4f59-9bc2-1dc2f90c9e6f/markdown_2/imgs/img_in_image_box_127_852_170_896.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A53Z%2F-1%2F%2F6884878414740db1bf97865fd4f5bad81cb55c259c0fe1f3c6395f085212381f" alt="Image" width="3%" /></div>


无论空中机器人、飞镖系统是否上场，云台手都可上场操作空中机器人、飞镖系统对应的裁判系统选手端，佩戴对应的耳机，三分钟准备阶段结束后不得移动位置。

飞手需获得飞手资格，并佩戴对应标识，才可在比赛中操控空中机器人。详见《RoboMaster2026机甲大师超级对抗赛参赛手册》的“技术评审”章节。

### 3.1 英雄机器人

英雄机器人是战场上唯一可以发射42mm弹丸的机器人。

<div style="text-align: center;"><div style="text-align: center;">表 3-3 英雄机器人关键特征</div> </div>




<table border="1" style="margin: auto; word-wrap: break-word;"><tr><td style="text-align: center; word-wrap: break-word;">关键特征</td><td style="text-align: center; word-wrap: break-word;">说明</td></tr><tr><td style="text-align: center; word-wrap: break-word;">初始区域</td><td style="text-align: center; word-wrap: break-word;">启动区</td></tr><tr><td style="text-align: center; word-wrap: break-word;">运行方式</td><td style="text-align: center; word-wrap: break-word;">不限，最多配置1个遥控器和1个自定义控制器</td></tr><tr><td style="text-align: center; word-wrap: break-word;">多机通信</td><td style="text-align: center; word-wrap: break-word;">允许</td></tr><tr><td style="text-align: center; word-wrap: break-word;">发射机构</td><td style="text-align: center; word-wrap: break-word;">1个 42mm 发射机构</td></tr><tr><td style="text-align: center; word-wrap: break-word;">射击初速度上限（m/s）</td><td style="text-align: center; word-wrap: break-word;">12，当性能体系选择远程优先，且进入部署模式时，提升为 16.5</td></tr><tr><td style="text-align: center; word-wrap: break-word;">扣血与超限惩罚机制</td><td style="text-align: center; word-wrap: break-word;">● 射击初速度超限：适用\n● 射击热量超限和冷却：适用\n● 底盘功率超限：适用\n● 攻击伤害或撞击：适用\n● 裁判系统模块离线：适用\n● 判罚伤害：适用\n详见“5.1 扣血与超限惩罚机制”</td></tr><tr><td style="text-align: center; word-wrap: break-word;">回血与复活机制</td><td style="text-align: center; word-wrap: break-word;">● 回血方式：占领补给区或远程兑换血量。\n● 复活方式：读条复活或兑换立即复活。\n详见“5.2 回血与复活机制”</td></tr><tr><td style="text-align: center; word-wrap: break-word;">弹丸的装载和补给</td><td style="text-align: center; word-wrap: break-word;">● 三分钟准备阶段，可预装 42mm 和 17mm 弹丸，初始允许发弹量为 0。\n● 七分钟比赛阶段，可通过补给区、基地增益点、前哨站增益点兑换或远程兑换允许发弹量。\n详见“5.3 经济体系”</td></tr><tr><td style="text-align: center; word-wrap: break-word;">经验与性能体系</td><td style="text-align: center; word-wrap: break-word;">适用</td></tr><tr><td style="text-align: center; word-wrap: break-word;"></td><td style="text-align: center; word-wrap: break-word;">注：底盘功率上限、初始血量、上限血量、射击热量上限、射击热量冷却速率等参数与等级、底盘类型、发射机构类型相关，详见“5.4 经验及性能体系”。</td></tr><tr><td style="text-align: center; word-wrap: break-word;">可占领的增益点</td><td style="text-align: center; word-wrap: break-word;">● 基地增益点\n● 中央高地增益点\n● 梯形高地增益点\n● 地形跨越增益点（公路、高地、飞坡、隧道）\n● 前哨站增益点\n● 补给区增益点\n● 堡垒增益点\n详见“5.5.3 场地增益机制”</td></tr></table>




### 3.2 工程机器人

工程机器人可以装配能量单元，以换取多样化的团队增益。

<div style="text-align: center;"><div style="text-align: center;">表 3-4 工程机器人关键特征</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>关键特征</td><td style='text-align: center; word-wrap: break-word;'>说明</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>初始区域</td><td style='text-align: center; word-wrap: break-word;'>启动区</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>运行方式</td><td style='text-align: center; word-wrap: break-word;'>不限，最多配置 1 个遥控器和 1 个自定义控制器</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>多机通信</td><td style='text-align: center; word-wrap: break-word;'>允许</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>发射机构</td><td style='text-align: center; word-wrap: break-word;'>不适用</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>射击初速度上限（m/s）</td><td style='text-align: center; word-wrap: break-word;'>不适用</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>扣血与超限惩罚机制</td><td style='text-align: center; word-wrap: break-word;'>● 射击初速度超限：不适用\n● 射击热量超限和冷却：不适用\n● 底盘功率超限：适用\n● 攻击伤害或撞击：适用</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>● 裁判系统模块离线：适用\n● 判罚伤害：适用\n详见“5.1 扣血与超限惩罚机制”</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>回血与复活机制</td><td style='text-align: center; word-wrap: break-word;'>● 回血方式：占领补给区。\n● 复活方式：读条复活或兑换立即复活。\n详见“5.2 回血与复活机制”</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>弹丸的装载和补给</td><td style='text-align: center; word-wrap: break-word;'>三分钟准备阶段，可预装 42mm 和 17mm 弹丸。\n详见“5.3 经济体系”</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>经验与性能体系</td><td style='text-align: center; word-wrap: break-word;'>初始血量/上限血量为 250，底盘功率上限为 120W，除此之外，不适用经验与性能体系</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>可占领的增益点</td><td style='text-align: center; word-wrap: break-word;'>● 基地增益点\n● 梯形高地增益点\n● 地形跨越增益点（公路、高地、飞坡、隧道）\n● 前哨站增益点\n● 装配区增益点\n● 补给区增益点\n详见“5.5.3 场地增益机制”</td></tr></table>





### 3.3 步兵机器人

步兵机器人可以发射17mm弹丸。

<div style="text-align: center;"><div style="text-align: center;">表 3-5 步兵机器人的关键特征</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>关键特征</td><td style='text-align: center; word-wrap: break-word;'>说明</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>初始区域</td><td style='text-align: center; word-wrap: break-word;'>启动区</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>运行方式</td><td style='text-align: center; word-wrap: break-word;'>不限，最多配置 1 个遥控器和 1 个自定义控制器</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>多机通信</td><td style='text-align: center; word-wrap: break-word;'>允许</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>发射机构</td><td style='text-align: center; word-wrap: break-word;'>1个17mm发射机构</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>射击初速度上限（m/s）</td><td style='text-align: center; word-wrap: break-word;'>25</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>扣血与超限惩罚机制</td><td style='text-align: center; word-wrap: break-word;'>● 射击初速度超限：适用\n● 射击热量超限和冷却：适用\n● 底盘功率超限：适用\n● 攻击伤害或撞击：适用\n● 裁判系统模块离线：适用\n● 判罚伤害：适用\n详见“5.1扣血与超限惩罚机制”</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>回血与复活机制</td><td style='text-align: center; word-wrap: break-word;'>● 回血方式：占领补给区或远程兑换血量。\n● 复活方式：读条复活或兑换立即复活。\n详见“5.2回血与复活机制”</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>弹丸的装载和补给</td><td style='text-align: center; word-wrap: break-word;'>● 三分钟准备阶段，可预装42mm和17mm弹丸，初始允许发弹量为0。\n● 七分钟比赛阶段，可通过补给区、基地增益点、前哨站增益点兑换或远程兑换允许发弹量。\n详见“5.3经济体系”</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>经验与性能体系</td><td style='text-align: center; word-wrap: break-word;'>适用\n注：底盘功率上限、初始血量、上限血量、射击热量上限、射击热量冷却速率等参数与等级、底盘类型相关，详见“5.4经验及性能体系”。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>可占领的增益点</td><td style='text-align: center; word-wrap: break-word;'>● 基地增益点\n● 中央高地增益点\n● 梯形高地增益点\n● 地形跨越增益点（公路、高地、飞坡、隧道）</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>● 前哨站增益点\n● 补给区增益点\n● 堡垒增益点\n详见“5.5.3 场地增益机制”</td></tr></table>








### 3.4 空中机器人

空中机器人可发起空中支援，获得第一视角画面并从空中发射17mm弹丸。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//42cfaf43-60d9-439a-aaf7-67d404dcf9b7/markdown_3/imgs/img_in_image_box_132_583_173_624.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A45Z%2F-1%2F%2Fc98bbfcc4fc1e731ae4660760a4c59ac11a387be79dec7ae9023eed5b3021f4f" alt="Image" width="3%" /></div>


在本文中，当空中机器人正在进行空中支援时，视为存活。

<div style="text-align: center;"><div style="text-align: center;">表 3-6 空中机器人的关键特征</div> </div>




<table border="1" style="margin: auto; word-wrap: break-word;"><tr><td style="text-align: center; word-wrap: break-word;">关键特征</td><td style="text-align: center; word-wrap: break-word;">说明</td></tr><tr><td style="text-align: center; word-wrap: break-word;">初始区域</td><td style="text-align: center; word-wrap: break-word;">停机坪</td></tr><tr><td style="text-align: center; word-wrap: break-word;">运行方式</td><td style="text-align: center; word-wrap: break-word;">不限，最多配置 2 个遥控器和 1 个自定义控制器</td></tr><tr><td style="text-align: center; word-wrap: break-word;">多机通信</td><td style="text-align: center; word-wrap: break-word;">允许</td></tr><tr><td style="text-align: center; word-wrap: break-word;">发射机构</td><td style="text-align: center; word-wrap: break-word;">1 个 17mm 发射机构</td></tr><tr><td style="text-align: center; word-wrap: break-word;">射击初速度上限（m/s）</td><td style="text-align: center; word-wrap: break-word;">25</td></tr><tr><td style="text-align: center; word-wrap: break-word;">扣血与超限惩罚机制</td><td style="text-align: center; word-wrap: break-word;">● 射击初速度超限：适用\n● 射击热量超限和冷却：适用\n● 底盘功率超限：不适用\n● 攻击伤害或撞击：不适用\n● 裁判系统模块离线：适用\n● 判罚伤害：不适用\n详见“5.1 扣血与超限惩罚机制”</td></tr><tr><td style="text-align: center; word-wrap: break-word;">回血与复活机制</td><td style="text-align: center; word-wrap: break-word;">不适用</td></tr><tr><td style="text-align: center; word-wrap: break-word;">弹丸的装载和补给</td><td style="text-align: center; word-wrap: break-word;">● 三分钟准备阶段，可预装 17mm 弹丸，初始允许发弹量为 750\n● 七分钟比赛阶段，不可额外兑换允许发弹量\n详见 “5.3 经济体系”</td></tr><tr><td style="text-align: center; word-wrap: break-word;">经验与性能体系</td><td style="text-align: center; word-wrap: break-word;">适用\n注：射击热量上限、射击热量冷却速率等参数与等级相关，详见 “5.4 经验及性能体系”。</td></tr><tr><td style="text-align: center; word-wrap: break-word;">可占领的增益点</td><td style="text-align: center; word-wrap: break-word;">不适用</td></tr></table>




### 3.5 哨兵机器人

哨兵机器人可全自动或半自动运行，可以发射17mm弹丸。

<div style="text-align: center;"><div style="text-align: center;">表 3-7 哨兵机器人的关键特征</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>关键特征</td><td style='text-align: center; word-wrap: break-word;'>说明</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>初始区域</td><td style='text-align: center; word-wrap: break-word;'>启动区</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>运行方式</td><td style='text-align: center; word-wrap: break-word;'>最多配置 1 个遥控器用于调试</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>多机通信</td><td style='text-align: center; word-wrap: break-word;'>可以向所有己方机器人发送数据，但只能接收雷达的数据</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>发射机构</td><td style='text-align: center; word-wrap: break-word;'>1 个 17mm 发射机构</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>射击初速度上限（m/s）</td><td style='text-align: center; word-wrap: break-word;'>25</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>扣血与超限惩罚机制</td><td style='text-align: center; word-wrap: break-word;'>● 射击初速度超限：适用\n● 射击热量超限和冷却：适用\n● 底盘功率超限：适用\n● 攻击伤害或撞击：适用\n● 裁判系统模块离线：适用\n● 判罚伤害：适用</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>详见“5.1 扣血与超限惩罚机制”</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>● 回血方式：占领补给区或远程兑换血量。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>回血与复活机制</td><td style='text-align: center; word-wrap: break-word;'>● 复活方式：读条复活或兑换立即复活。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>详见“5.2 回血与复活机制”</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>● 三分钟准备阶段,可预装17mm和42mm弹丸,初始允许发弹量为300。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>弹丸的装载和补给</td><td style='text-align: center; word-wrap: break-word;'>● 七分钟比赛阶段,可通过补给区、基地增益点、前哨站增益点兑换或直接获取、远程兑换允许发弹量。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>详见“5.3 经济体系”</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>不适用经验与性能体系，性能与机器人操作方式相关，具体如下：</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>自动哨兵机器人</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>● 初始血量/上限血量为400</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>● 射击热量上限为260</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>● 射击热量冷却速率为30/秒</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>● 底盘功率上限为100W</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>经验与性能体系</td><td style='text-align: center; word-wrap: break-word;'>半自动哨兵机器人</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>● 初始血量/上限血量为200</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>● 射击热量上限为100</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>● 射击热量冷却速率为10/秒</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>● 底盘功率上限为60W</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>详见“5.6.4 哨兵机器人特殊机制”</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>● 基地增益点</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>● 中央高地增益点</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>可占领的增益点</td><td style='text-align: center; word-wrap: break-word;'>● 梯形高地增益点</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>● 地形跨越增益点（公路、高地、飞坡、隧道）</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>● 前哨站增益点</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>● 补给区增益点\n● 堡垒增益点\n详见“5.5.3 场地增益机制”</td></tr></table>








### 3.6 飞镖系统

飞镖系统可通过发射飞镖攻击对方前哨站、基地。

<div style="text-align: center;"><div style="text-align: center;">表 3-8 飞镖系统的关键特征</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>关键特征</td><td style='text-align: center; word-wrap: break-word;'>说明</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>初始区域</td><td style='text-align: center; word-wrap: break-word;'>飞镖发射站</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>运行方式</td><td style='text-align: center; word-wrap: break-word;'>不限，最多配置 1 个遥控器</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>多机通信</td><td style='text-align: center; word-wrap: break-word;'>允许</td></tr></table>

### 3.7 雷达

雷达可自主获取战场信息，并通过多机通信向己方机器人或裁判系统选手端发送信息，还可以截获对方的信息或反制对方空中机器人的空中支援。

<div style="text-align: center;"><div style="text-align: center;">表 3-9 雷达的关键特征</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>关键特征</td><td style='text-align: center; word-wrap: break-word;'>说明</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>初始区域</td><td style='text-align: center; word-wrap: break-word;'>雷达基座</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>运行方式</td><td style='text-align: center; word-wrap: break-word;'>自动运行，最多配置 1 个遥控器用于调试</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>多机通信</td><td style='text-align: center; word-wrap: break-word;'>可以向所有己方机器人发送数据，但只能接收哨兵机器人的数据</td></tr></table>

## 4 比赛场地

### 4.1 战场概述

除特殊标注外，全文描述的所有尺寸均存在一定公差。小于 100mm 的尺寸结构误差在±5mm 以内，大于等于 100mm 的尺寸误差在±5%以内，战场结构的角度误差在±3°以内，场地道具的角度误差在±1°以内，场地说明图纸尺寸参数单位为 mm。为确保场地稳定性和安全性，实际制作时可能会对场地的细节尺寸、工艺进行调整，未在图纸中详细注明的战场元素/尺寸，请以实际场地为准。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//e4730ab3-d19f-481c-b9ec-fe0ee326cb9b/markdown_3/imgs/img_in_image_box_127_531_171_574.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A04%3A49Z%2F-1%2F%2F43ddb62345b6ecfcea82c619e7b7aa201a77dbea9f6f4aa46ab3cedbe1e641dd" alt="Image" width="3%" /></div>


战场为中心对称布局，全文所涉及的场地模块部分描述及说明图以红方图示为例，蓝方同理。场地环境复杂，可能存在不均匀磁场、场馆空调风等不完全对称的环境因素。

● 渲染图仅供示意，场地具体尺寸细节以对应图纸为准；未尽事宜以适应性训练实际情况为准。

战场内设有多处增益点与禁区。为确保文档简洁清晰，本章不作逐一赘述，其具体定义将分别在“5.5.3.1 场地增益点概述”与“7.2.3.2 机器人与场地道具交互”中统一说明。

RMUC 的核心比赛场地被称为 “战场”。战场是一个长为 28m、宽为 15m 的区域，内部为木质结构，表面铺设厚度为 2mm 的 PVC 地胶，地形跨越增益点（高地、公路）的较低处和起伏路段铺设厚度为 2mm 的 PVC 夹线地胶，部分结构存在金属保护层，主要包含基地区、高地区、公路区和飞行区等。战场外围有上边沿距离战场地面高度为 2.4m 的黑色钢制围挡。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//e4730ab3-d19f-481c-b9ec-fe0ee326cb9b/markdown_3/imgs/img_in_image_box_217_982_965_1382.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A04%3A52Z%2F-1%2F%2F0ccec84839ec077c16fb0781dd4bcd3f8fb75fdedc2e8d423d659d0b8ff21864" alt="Image" width="62%" /></div>


<div style="text-align: center;"><div style="text-align: center;">图 4-1 战场俯视渲染图</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//58695d94-2bdf-463a-84f3-2de525f09ff3/markdown_0/imgs/img_in_image_box_156_164_1025_455.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A42Z%2F-1%2F%2F87b6e811f5ed4ce02a0251944b7e7f3cb7d592df2d82e71104d6133253ae2632" alt="Image" width="72%" /></div>


<div style="text-align: center;"><div style="text-align: center;">图 4-2 战场斜视渲染图</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//58695d94-2bdf-463a-84f3-2de525f09ff3/markdown_0/imgs/img_in_image_box_170_590_990_1084.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A42Z%2F-1%2F%2Fd6473743f68fab429f5a9113de3f880fb1ad458d2c53ecd1d32322c8ebf94bfe" alt="Image" width="68%" /></div>


<div style="text-align: center;"><div style="text-align: center;">图 4-3 战场轴测渲染图</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//58695d94-2bdf-463a-84f3-2de525f09ff3/markdown_1/imgs/img_in_image_box_160_166_1034_679.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A42Z%2F-1%2F%2F232e29be7fdcc68b74ba4e58593d3115af6b3a966607e73c707b41fda6d02c38" alt="Image" width="73%" /></div>


<div style="text-align: center;"><div style="text-align: center;">[1] 空中机器人安全绳 [2] 补给区 [3] 公路区 [4] 前哨站 [5] 飞坡 [6] 蓝方装配区 [7] 堡垒 [8] 梯形高地 [9] 停机坪 [10] 飞镖发射站 [11] 雷达基座 [12] 无线充电装置放置区 [13] 资源站 [14] 基地 [15] 公路隧道 [16] 中央高地 [17] 公路隧道 [18] 能量机关 [19] 红方装配区 [20] 飞手操作间 [21] 风机</div> </div>


<div style="text-align: center;"><div style="text-align: center;">图 4-4 战场模块示意图</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//58695d94-2bdf-463a-84f3-2de525f09ff3/markdown_2/imgs/img_in_image_box_133_165_1049_630.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A42Z%2F-1%2F%2F30cd99be1ee80c9fd2875aece2bdc37dab4978188276782bf834ccdf6f8e6ab0" alt="Image" width="76%" /></div>


<div style="text-align: center;"><div style="text-align: center;">[1] 与战场长边平行且为飞镖发射站朝向</div> </div>


<div style="text-align: center;"><div style="text-align: center;">图 4-5 战场模块定位尺寸图</div> </div>


全文场地尺寸以左右倾斜面为基准标注, 实际战场非水平地面, 以战场中轴线为轴, 向长边两侧倾斜  $ 1^{\circ} \sim 2^{\circ} $, 具体如下图所示。战场倾斜会导致弹丸向长边两侧流动。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//58695d94-2bdf-463a-84f3-2de525f09ff3/markdown_3/imgs/img_in_image_box_142_258_185_305.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A43Z%2F-1%2F%2Fde0149a7ab7d841ebb1867f75c941bd6409e46e5ce9df3c0485ceff71089bd50" alt="Image" width="3%" /></div>


为了使弹丸顺利回收，在战场部分木制结构与地面的交线可能存在高度约50mm的开槽，并且在比赛结束后会短暂开启战场木制结构内的涵道风机。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//58695d94-2bdf-463a-84f3-2de525f09ff3/markdown_3/imgs/img_in_image_box_196_377_1041_868.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A43Z%2F-1%2F%2F727387902f080945f979596167a56c056e39df5c20dd9a3e1ad44b018ff16865" alt="Image" width="70%" /></div>


<div style="text-align: center;"><div style="text-align: center;">[1]</div> </div>


<div style="text-align: center;"><div style="text-align: center;">[2]</div> </div>


<div style="text-align: center;"><div style="text-align: center;">[3] 基地底座 [4] 堡垒底座 [5] 装配区底座</div> </div>


<div style="text-align: center;"><div style="text-align: center;">图 4-6 战场倾斜示意图</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//43ab3d95-dc12-49c4-8618-a56b04cae3a0/markdown_0/imgs/img_in_image_box_313_173_881_732.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A42Z%2F-1%2F%2F00f840f3bb92172114f619dba8df01066cb8ba040d6848222e90914f4e779d88" alt="Image" width="47%" /></div>


<div style="text-align: center;"><div style="text-align: center;">[1] 进风口 [2] 出风口</div> </div>


<div style="text-align: center;"><div style="text-align: center;">图 4-7 风机示意图</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//43ab3d95-dc12-49c4-8618-a56b04cae3a0/markdown_0/imgs/img_in_image_box_143_941_186_985.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A42Z%2F-1%2F%2F69de944bc5308dd39d7a4e5c4833ea535cd7d759e9cce90fb723f6b95938f938" alt="Image" width="3%" /></div>


风机在场地中会根据场地木质结外形构嵌入到木质结构中。

### 4.2 基地区

基地区包含启动区、基地、飞镖发射站、停机坪、雷达基座、补给区、堡垒。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//43ab3d95-dc12-49c4-8618-a56b04cae3a0/markdown_1/imgs/img_in_image_box_312_305_896_882.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A42Z%2F-1%2F%2F21f1f6b36ca2e5f85c874571c2c5a2d8d3b84eef9424279c6bb006c372745f88" alt="Image" width="49%" /></div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>[1]</td><td style='text-align: center; word-wrap: break-word;'>停机坪</td><td style='text-align: center; word-wrap: break-word;'>[2]</td><td style='text-align: center; word-wrap: break-word;'>飞手操作间</td><td style='text-align: center; word-wrap: break-word;'>[3]</td><td style='text-align: center; word-wrap: break-word;'>飞镖发射站</td><td style='text-align: center; word-wrap: break-word;'>[4]</td><td style='text-align: center; word-wrap: break-word;'>风机</td><td style='text-align: center; word-wrap: break-word;'>[5]</td><td style='text-align: center; word-wrap: break-word;'>启动区</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>[6]</td><td style='text-align: center; word-wrap: break-word;'>堡垒</td><td style='text-align: center; word-wrap: break-word;'>[7]</td><td style='text-align: center; word-wrap: break-word;'>雷达基座</td><td style='text-align: center; word-wrap: break-word;'>[8]</td><td style='text-align: center; word-wrap: break-word;'>无线充电装置放置区</td><td style='text-align: center; word-wrap: break-word;'>[9]</td><td style='text-align: center; word-wrap: break-word;'>补给区</td><td style='text-align: center; word-wrap: break-word;'>[10]</td><td style='text-align: center; word-wrap: break-word;'>资源站</td></tr></table>

<div style="text-align: center;"><div style="text-align: center;">图 4-8 基地区示意图</div> </div>


#### 4.2.1 启动区

启动区为基地周围的六边形区域，是比赛开始前地面机器人的放置区。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//43ab3d95-dc12-49c4-8618-a56b04cae3a0/markdown_2/imgs/img_in_image_box_366_269_809_720.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A43Z%2F-1%2F%2Fc238c2d023bdd6499cd085a9f7177896fc1b588455eca66b15995a698a70409d" alt="Image" width="37%" /></div>


<div style="text-align: center;"><div style="text-align: center;">[1] 启动区</div> </div>


<div style="text-align: center;"><div style="text-align: center;">图 4-9 机器人启动区示意图</div> </div>


#### 4.2.2 基地

基地是双方攻防的核心，放置于双方启动区中央的基地底座上。

基地由基地主体、6块基地装甲模块、飞镖检测模块、基地护甲等组成。基地护甲有两种形态：护甲闭合和护甲展开。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//43ab3d95-dc12-49c4-8618-a56b04cae3a0/markdown_2/imgs/img_in_image_box_428_1091_770_1456.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A43Z%2F-1%2F%2Fd4537ea9af193385202167a01ae41ab181e624685b824a9b502abce1c271de8d" alt="Image" width="28%" /></div>


<div style="text-align: center;"><div style="text-align: center;">图 4-10 基地底座示意图</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//43ab3d95-dc12-49c4-8618-a56b04cae3a0/markdown_3/imgs/img_in_image_box_271_147_900_649.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A44Z%2F-1%2F%2F3b805fcef607807774f4d8e9499f1679625d63eeb2b5488c353c4b8196ddb652" alt="Image" width="52%" /></div>


<div style="text-align: center;"><div style="text-align: center;">[1] 基地装甲模块</div> </div>


<div style="text-align: center;"><div style="text-align: center;">[2] 飞镖检测模块</div> </div>


<div style="text-align: center;"><div style="text-align: center;">图 4-11 基地护甲闭合形态尺寸图</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//43ab3d95-dc12-49c4-8618-a56b04cae3a0/markdown_3/imgs/img_in_image_box_204_828_982_1184.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A44Z%2F-1%2F%2F8e8ca04db886ec423e2f570af6a0b0ba6d053e7f297df2f5c5a681b065ff687d" alt="Image" width="65%" /></div>


<div style="text-align: center;"><div style="text-align: center;">图 4-12 基地护甲展开形态尺寸图</div> </div>


飞镖检测模块位于基地和前哨站上部，由小装甲模块、飞镖检测传感器和飞镖引导灯组成。

其中飞镖检测模块的小装甲模块可检测飞镖的击打；飞镖检测传感器可检测飞镖触发装置发射的红外光束。当飞镖触发装置向飞镖检测模块的投影完全落在小装甲模块内，且飞镖检测模块同时检测到红外光束和击打时，系统认为该模块被飞镖命中；仅检测到击打时，则系统认为该模块被弹丸击中。飞镖引导灯发射520nm波段的绿色可见光，飞镖引导灯在近似为点光源时其发光强度约为10cd，发光部分直径约为55mm，用于引导飞镖击打目标。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//48108628-5a58-419b-942a-d89076c8d208/markdown_0/imgs/img_in_image_box_128_167_169_214.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A51Z%2F-1%2F%2Fad06647b7d632c6d36582be75719ffc3ca1e6e4d17f96b59a5b246b687c9b73b" alt="Image" width="3%" /></div>


当飞镖触发装置向飞镖检测模块的投影未完全落在小装甲模块内，也有一定概率被飞镖检测模块成功识别。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//48108628-5a58-419b-942a-d89076c8d208/markdown_0/imgs/img_in_image_box_262_268_946_1308.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A51Z%2F-1%2F%2F4b63b3b371300a60cbbb3c66e9c1f992dd242b44993bff612c8d88f5fd900113" alt="Image" width="57%" /></div>


<div style="text-align: center;"><div style="text-align: center;">[1] 小装甲模块 [2] 飞镖检测传感器 [3] 飞镖引导灯</div> </div>


<div style="text-align: center;"><div style="text-align: center;">图 4-13 飞镖检测模块示意图</div> </div>


#### 4.2.3 飞镖发射站

飞镖发射站是飞镖系统的唯一放置区，由发射站主体、滑台和闸门组成。飞镖发射站内设置有照明装置，不可关闭。裁判系统自检阶段飞镖发射站闸门会短暂开启（约5秒），开启期间内，飞镖检测模块会静止于基地固定目标的对应位置。在三分钟准备阶段与十五秒裁判系统自检阶段中，前哨站和基地的飞镖引导灯均亮起。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//48108628-5a58-419b-942a-d89076c8d208/markdown_1/imgs/img_in_image_box_150_385_534_865.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A58Z%2F-1%2F%2Ffa6b271bdbf7a07cff626ae6064e1e7aa6313de2ebd219e38a7e7d3201a18635" alt="Image" width="32%" /></div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//48108628-5a58-419b-942a-d89076c8d208/markdown_1/imgs/img_in_image_box_670_398_1049_874.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A59Z%2F-1%2F%2Ff3459a7e2c84212bf593e4f1fee4db890e7746f363a3a1c691e77ee3d4b849b6" alt="Image" width="31%" /></div>


<div style="text-align: center;"><div style="text-align: center;">[1] 闸门 [2] 状态指示灯</div> </div>


<div style="text-align: center;"><div style="text-align: center;">[3] 飞镖系统放置空间</div> </div>


<div style="text-align: center;"><div style="text-align: center;">[4] 滑台 [5] 发射站主体 [6] 场地边沿</div> </div>


<div style="text-align: center;"><div style="text-align: center;">图 4-14 飞镖发射站示意图</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//48108628-5a58-419b-942a-d89076c8d208/markdown_2/imgs/img_in_image_box_176_146_987_650.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A03%3A01Z%2F-1%2F%2Ffcbcf6f509a3a76e225826ca903b04a9f919b7d9bababce425dc53480c6bcd72" alt="Image" width="68%" /></div>


<div style="text-align: center;"><div style="text-align: center;">图 4-15 滑台滑出示意图</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//48108628-5a58-419b-942a-d89076c8d208/markdown_2/imgs/img_in_image_box_317_731_896_1217.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A03%3A02Z%2F-1%2F%2F229f992473522c33424b0259851d670b87b3c6a15436ec74a63bc2292b9937b0" alt="Image" width="48%" /></div>


<div style="text-align: center;"><div style="text-align: center;">[1] 飞镖系统放置平面 [2] 支撑轮</div> </div>


<div style="text-align: center;"><div style="text-align: center;">图 4-16 滑台尺寸图</div> </div>


#### 4.2.4 停机坪

比赛开始前，空中机器人需放置于停机坪平台上，其投影需在停机坪平台范围内，并按照要求连接安全绳。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//48108628-5a58-419b-942a-d89076c8d208/markdown_3/imgs/img_in_image_box_222_278_994_903.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A03%3A03Z%2F-1%2F%2Fd38d29c342092f7855ad7b83e933e1ffba6bfff6dfd6c699970fa4fc0d60ae8a" alt="Image" width="64%" /></div>


<div style="text-align: center;"><div style="text-align: center;">[1] 停机坪平台</div> </div>


<div style="text-align: center;"><div style="text-align: center;">图 4-17 停机坪示意图</div> </div>


#### 4.2.5 雷达基座

雷达基座用于放置雷达传感器和激光发射装置，上端为面积  $ 3.4m \times 1.16m $ 的平台。平台平面中央与战场中心轴线对齐，距战场地面高度约为  $ 2.5m $，四周有高度为  $ 1.1m $ 的围栏。平台旁边设有传感器数据线槽孔，比赛时根据实际场地情况进行使用。

雷达运算端通过 220V 市电供电，其放置平台放置有：

1 台仅支持 HDMI 信号输入的官方显示设备，其显示分辨率为  $ 1920 \times 1080 $。参赛队伍可将其用于确认雷达运行的情况。

1 根 HDMI 信号线，用于连接雷达和官方显示设备。

1 个新国标 5 孔插座，其中单相两极和单相三极插孔可以同时接入，为雷达供电，该插座不可移动。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//e11727a0-5dd0-43c4-9e52-802253260950/markdown_0/imgs/img_in_image_box_138_160_607_447.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A41Z%2F-1%2F%2F34d1b3e33c8678850f01546c3744fd7720840309e648be3a5b0b4ed8f92a6f38" alt="Image" width="39%" /></div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//e11727a0-5dd0-43c4-9e52-802253260950/markdown_0/imgs/img_in_image_box_161_498_551_802.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A42Z%2F-1%2F%2Fd3b493bf73cc86f09e70a26f4702ef7b0336474a665660a5a225c0bcd6f712b0" alt="Image" width="32%" /></div>


<div style="text-align: center;"><div style="text-align: center;">[1] 雷达信息波</div> </div>


<div style="text-align: center;"><div style="text-align: center;">[4] 雷达传感器放置平台</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//e11727a0-5dd0-43c4-9e52-802253260950/markdown_0/imgs/img_in_image_box_698_189_1029_827.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A42Z%2F-1%2F%2F0b4790c4084bd45b22517ae75c68d4b0860710d26726ea74633f4a3c2f6dc825" alt="Image" width="27%" /></div>


<div style="text-align: center;"><div style="text-align: center;">[2] 传感器数据线槽孔</div> </div>


<div style="text-align: center;"><div style="text-align: center;">[5] 雷达运算端放置平台</div> </div>


<div style="text-align: center;"><div style="text-align: center;">[3] 雷达信息波发射面</div> </div>


<div style="text-align: center;"><div style="text-align: center;">图 4-18 雷达基座示意图</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//e11727a0-5dd0-43c4-9e52-802253260950/markdown_1/imgs/img_in_image_box_241_139_600_409.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A42Z%2F-1%2F%2F06a20ed02a2874bbf7d8b7e1df2b4a9e0463b67a8d3354400aa72ad23001d209" alt="Image" width="30%" /></div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//e11727a0-5dd0-43c4-9e52-802253260950/markdown_1/imgs/img_in_image_box_694_137_965_410.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A42Z%2F-1%2F%2F2f671cf0108d9be71529c0c94d1c04bcceca1d10e40c8448018fcc08469dcfe4" alt="Image" width="22%" /></div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//e11727a0-5dd0-43c4-9e52-802253260950/markdown_1/imgs/img_in_image_box_410_484_796_806.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A42Z%2F-1%2F%2F049a7f1661d2c2161510b8777d8d9a560978d55639f86ec54ed8e84884a2add0" alt="Image" width="32%" /></div>


<div style="text-align: center;"><div style="text-align: center;">[1] 战场出入口 [2] 出入口台阶 [3] 雷达基座</div> </div>


<div style="text-align: center;"><div style="text-align: center;">图 4-19 雷达基座的相对位置示意图</div> </div>


#### 4.2.6 补给区

补给区包括资源站、补给区增益点、无线充电装置放置区，是机器人进行无线充电、血量恢复、补充允许发弹量、获取能量单元的重要区域。同时补给区边缘围挡设置了一个飞镖传递窗口，机器人可以拾取己方飞镖，并通过飞镖传递窗口将飞镖送至场外供队员维修，具体如下图所示。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//e11727a0-5dd0-43c4-9e52-802253260950/markdown_2/imgs/img_in_image_box_116_359_1074_720.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A43Z%2F-1%2F%2Fdcd5405ea68611a3e8825c17d3ff896485c094000594a5653d0f1f075d48b321" alt="Image" width="80%" /></div>


[1] 飞镖传递窗口 [2] 风机 [3] 补给区

<div style="text-align: center;"><div style="text-align: center;">图 4-20 补给区示意图</div> </div>


资源站是工程机器人获取能量单元的区域，其中设置有6个能量单元，均以磁吸的方式固定在能量单元放置区内。工程机器人需沿能量单元旋转对称轴的方向取出能量单元，该过程除克服重力外，还需额外施加至多10N的力以克服磁吸力。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//e11727a0-5dd0-43c4-9e52-802253260950/markdown_3/imgs/img_in_image_box_184_285_1043_1042.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A43Z%2F-1%2F%2F0df0e6fd38919a9504f39052a37d021b41cdd4a9994f3a7c3cb167fd7ee906ee" alt="Image" width="72%" /></div>


<div style="text-align: center;"><div style="text-align: center;">[1] 能量单元放置区 [2] 挡板</div> </div>


<div style="text-align: center;"><div style="text-align: center;">图 4-21 资源站示意图</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//e11727a0-5dd0-43c4-9e52-802253260950/markdown_3/imgs/img_in_image_box_122_1195_165_1243.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A44Z%2F-1%2F%2Ff0fb5e143037f4035d9915671d77b433a44565e4a13ccf5c153c091f57d442f5" alt="Image" width="3%" /></div>


能量单元的实际安装位置相对于图示，可能存在绕对称轴的角度偏差。图示仅做示意，具体请以实际放置情况为准。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//6c54a570-5dc3-4bb8-9e2d-9ec54d75f845/markdown_0/imgs/img_in_image_box_148_159_1047_1222.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A42Z%2F-1%2F%2F6241766419ea1cb72c53ba88afbbad467fcaec282282f1e7e00859f785486a91" alt="Image" width="75%" /></div>


<div style="text-align: center;"><div style="text-align: center;">图 4-22 能量单元放置区示意图</div> </div>


公路区面向补给区的墙体设置有金属材质的视觉标签，用于相机图传模块判断机器人是否位于补给区，如下所示。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//6c54a570-5dc3-4bb8-9e2d-9ec54d75f845/markdown_1/imgs/img_in_image_box_280_243_905_500.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A43Z%2F-1%2F%2Fdbae8921329bd4b305661b876cd5e373b46c2e4d839c9cb5a4d2a3c4d5b15fac" alt="Image" width="52%" /></div>


<div style="text-align: center;"><div style="text-align: center;">[1] 视觉标签</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//6c54a570-5dc3-4bb8-9e2d-9ec54d75f845/markdown_1/imgs/img_in_image_box_433_609_751_922.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A43Z%2F-1%2F%2F85d48420a34ba6ba4906474b67052406e12190184e20c2d4442efb5f1a8e692a" alt="Image" width="26%" /></div>


<div style="text-align: center;"><div style="text-align: center;">红方视觉标签</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//6c54a570-5dc3-4bb8-9e2d-9ec54d75f845/markdown_1/imgs/img_in_image_box_437_1045_757_1356.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A43Z%2F-1%2F%2F36164db3983c05c4e642f6dcb16dc5e123adc932fd23d927bb1e4b743d0653b4" alt="Image" width="26%" /></div>


<div style="text-align: center;"><div style="text-align: center;">蓝方视觉标签</div> </div>


<div style="text-align: center;"><div style="text-align: center;">图 4-23 视觉标签示意图</div> </div>


无线充电装置放置区位于补给区，参赛队伍可以在三分钟准备阶段将其无线充电装置（发射端）放置于无线充电装置放置区，且其投影需在无线充电装置放置区域以内。具体如下图所示：

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//6c54a570-5dc3-4bb8-9e2d-9ec54d75f845/markdown_2/imgs/img_in_image_box_177_259_1020_1078.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A44Z%2F-1%2F%2F67848aa44ca4d43684af42ba53225389c4b886b80a5cdfdc97303892403919ad" alt="Image" width="70%" /></div>


<div style="text-align: center;"><div style="text-align: center;">[1] 无线充电装置放置区</div> </div>


<div style="text-align: center;"><div style="text-align: center;">图 4-24 无线充电装置放置区示意图</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//6c54a570-5dc3-4bb8-9e2d-9ec54d75f845/markdown_2/imgs/img_in_image_box_122_1259_165_1305.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A44Z%2F-1%2F%2Fe85ab534f94091f85d439521302e4eeedf14fdc545aa9b68e065f47149683acb" alt="Image" width="3%" /></div>


组委会在无线充电装置放置区布置了2个XT60母头供电接口，提供 $ 24V\pm1V $直流电，最大总功率为200W。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//6c54a570-5dc3-4bb8-9e2d-9ec54d75f845/markdown_3/imgs/img_in_image_box_139_147_530_366.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A44Z%2F-1%2F%2Fc96127d61a0399ea3775a4babe24b1d68c4f1ce127750b9e2cc8dae477b99e1c" alt="Image" width="32%" /></div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//6c54a570-5dc3-4bb8-9e2d-9ec54d75f845/markdown_3/imgs/img_in_image_box_556_143_1065_300.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A44Z%2F-1%2F%2F1c954b8d798cb25b67de4e5b124fc7c5621f6b99de6ea42ef2dd1ce57c21ac2a" alt="Image" width="42%" /></div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//6c54a570-5dc3-4bb8-9e2d-9ec54d75f845/markdown_3/imgs/img_in_image_box_113_382_532_909.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A44Z%2F-1%2F%2F6273aa20b06b2f32e870721312f39c64881958a09a03a81ada46c74bf2a7b699" alt="Image" width="35%" /></div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//6c54a570-5dc3-4bb8-9e2d-9ec54d75f845/markdown_3/imgs/img_in_image_box_635_416_1044_749.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A44Z%2F-1%2F%2F8462e0f17611db32710bf4caaa7db1b55d07d173d91ff2bd6a3c687e11631647" alt="Image" width="34%" /></div>


<div style="text-align: center;"><div style="text-align: center;">[1] 围挡 [2] 无线充电装置放置区域</div> </div>


<div style="text-align: center;"><div style="text-align: center;">[5] 开关电源 [6] 过线孔</div> </div>


<div style="text-align: center;"><div style="text-align: center;">[3] 线槽翻盖</div> </div>


<div style="text-align: center;"><div style="text-align: center;">[4] 翻盖旋转轴</div> </div>


<div style="text-align: center;"><div style="text-align: center;">[7] XT60 母头接口</div> </div>


<div style="text-align: center;"><div style="text-align: center;">图 4-25 无线充电装置示意图</div> </div>


#### 4.2.7 堡垒

堡垒是基地区的关键防守区域。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//605a4313-25c6-45ef-97bb-94ceabc0cd69/markdown_0/imgs/img_in_image_box_259_278_978_992.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A04%3A11Z%2F-1%2F%2Fe36c89d7322c0bc16bd77e7a4360d34f96942dc92233f6dd8330eed1c5cebe81" alt="Image" width="60%" /></div>


<div style="text-align: center;"><div style="text-align: center;">[1]  $ 20^{\circ} $坡</div> </div>


<div style="text-align: center;"><div style="text-align: center;">图 4-26 堡垒示意图</div> </div>


### 4.3 高地区

高地是战场中高于战场地面的部分区域，红蓝双方半场各1个梯形高地，以及战场中央的中央高地，将战场划分为多个区域，在空间上形成立体战场。

#### 4.3.1 梯形高地

梯形高地位于停机坪附近，相对战场地面高度为 200-400mm。梯形高地上设置有梯形高地增益点，具体位置如下图所示。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//605a4313-25c6-45ef-97bb-94ceabc0cd69/markdown_1/imgs/img_in_image_box_111_483_1067_1025.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A04%3A13Z%2F-1%2F%2Fa6b9544157fa0d155b45542c0e3703c12ad49569f744fe685024a3ad3636196d" alt="Image" width="80%" /></div>


<div style="text-align: center;"><div style="text-align: center;">[1]  $ 43^{\circ} $坡 [2]  $ 23^{\circ} $坡 [3] 风机</div> </div>


<div style="text-align: center;"><div style="text-align: center;">图 4-27 梯形高地示意图</div> </div>


#### 4.3.2 中央高地

中央高地位于战场中部，两端通过坡道与公路区连接。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//605a4313-25c6-45ef-97bb-94ceabc0cd69/markdown_2/imgs/img_in_image_box_180_308_564_676.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A04%3A14Z%2F-1%2F%2F248e3ec40e27df0d327d3b3a5250eaa3774cc499211f738e861311bb9565078a" alt="Image" width="32%" /></div>


<div style="text-align: center;"><div style="text-align: center;">[1] 红方装配区</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//605a4313-25c6-45ef-97bb-94ceabc0cd69/markdown_2/imgs/img_in_image_box_576_318_987_678.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A04%3A14Z%2F-1%2F%2F4d4e35e26ff54e54921c3cd5e622aa80dcba8dfd0041e081b3b5f3e490868329" alt="Image" width="34%" /></div>


<div style="text-align: center;"><div style="text-align: center;">[4] 前哨站</div> </div>


<div style="text-align: center;"><div style="text-align: center;">[2] 能量机关</div> </div>


<div style="text-align: center;"><div style="text-align: center;">[3] 蓝方装配区</div> </div>


 $$ 10.5^{\circ} 坡 $$ 

<div style="text-align: center;"><div style="text-align: center;">[6] 风机</div> </div>


<div style="text-align: center;"><div style="text-align: center;">图 4-28 中央高地示意图</div> </div>


##### 4.3.2.1 装配区

装配区位于战场中央，能量机关正下方。装配区分为红、蓝双方。能量机关下方设置有科技核心，工程机器人可以将能量单元装配至科技核心，具体如下图所示。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//605a4313-25c6-45ef-97bb-94ceabc0cd69/markdown_3/imgs/img_in_image_box_155_310_588_755.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A04%3A16Z%2F-1%2F%2Fc26e9c6c6179718a0e94a3a46095cd3244a9375dcef396f34ba3946cd533a8e1" alt="Image" width="36%" /></div>


<div style="text-align: center;"><div style="text-align: center;">[1] 能量机关</div> </div>


<div style="text-align: center;"><div style="text-align: center;">[2] 科技核心</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//605a4313-25c6-45ef-97bb-94ceabc0cd69/markdown_3/imgs/img_in_image_box_611_303_1040_728.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A04%3A17Z%2F-1%2F%2Ff11e77e520b1f2b3e39a17c5c6e246f71b917abc63e002af8463e610fc9678ac" alt="Image" width="36%" /></div>


<div style="text-align: center;"><div style="text-align: center;">[5] 蓝方装配区</div> </div>


 $$ 12^{\circ} 坡 $$ 

<div style="text-align: center;"><div style="text-align: center;">[3] 红方装配区</div> </div>


 $$ 14^{\circ} 坡 $$ 

 $$ 45^{\circ} 坡 $$ 

 $$ 15^{\circ} 坡 $$ 

<div style="text-align: center;"><div style="text-align: center;">图 4-29 装配区轴测图</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//605a4313-25c6-45ef-97bb-94ceabc0cd69/markdown_3/imgs/img_in_image_box_253_954_959_1456.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A04%3A17Z%2F-1%2F%2F6d6eaec9d3084bba98056405f944125b3005a2774b0ddb3cb7fb5cdb79a62d3a" alt="Image" width="59%" /></div>


<div style="text-align: center;"><div style="text-align: center;">图 4-30 装配区尺寸图</div> </div>


##### 4.3.2.2 能量机关

能量机关位于装配区正上方。能量机关由电机驱动并按照一定规律同步转动。能量机关分为红蓝两侧，一侧为红方能量机关，另一侧为蓝方能量机关。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//427db8d3-19f1-46ca-9a83-13ec69699332/markdown_0/imgs/img_in_image_box_127_334_170_377.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A46Z%2F-1%2F%2Fb82fd904819770f575da68f2ee1bfdcf66642f5d2dc1bf9e91556ece01ef40d4" alt="Image" width="3%" /></div>


能量机关中部由于重量较大，会出现轻微下坠的现象，下坠范围为 0~50mm。

由于观察视角问题及传动间隙，观察一方能量机关时可能会看到对方能量机关的一部分。

能量机关有5个均匀分布的灯臂，具体位置和尺寸如下所示：

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//427db8d3-19f1-46ca-9a83-13ec69699332/markdown_0/imgs/img_in_image_box_300_516_898_1238.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A47Z%2F-1%2F%2Fd1f198d513ca39b159bb652f185573256b458fe33843ec112d070e878fbaf042" alt="Image" width="50%" /></div>


<div style="text-align: center;"><div style="text-align: center;">图 4-31 能量机关示意图</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//427db8d3-19f1-46ca-9a83-13ec69699332/markdown_1/imgs/img_in_image_box_226_176_965_645.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A48Z%2F-1%2F%2F63ddad27a944db49d550dab6250624cf485bd910c0f2f17dff4f0eb4b395ca7d" alt="Image" width="62%" /></div>


<div style="text-align: center;"><div style="text-align: center;">图 4-32 能量机关灯臂尺寸示意图</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//427db8d3-19f1-46ca-9a83-13ec69699332/markdown_1/imgs/img_in_image_box_134_721_177_763.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A48Z%2F-1%2F%2F31c3e102eb06b720840af6f8735d1a1e01c87d59188905a96884231d33e18894" alt="Image" width="3%" /></div>


实际灯臂的圆靶最大直径为 308mm，实际有效检测直径为 300mm。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//427db8d3-19f1-46ca-9a83-13ec69699332/markdown_1/imgs/img_in_image_box_402_806_796_1132.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A48Z%2F-1%2F%2Fc82498beefdec9d08e426cfd85750e5df122ca3b7731ff3e5bc5950bfa16bd5c" alt="Image" width="33%" /></div>


<div style="text-align: center;"><div style="text-align: center;">图 4-33 能量机关中心标识尺寸图</div> </div>


##### 4.3.2.3 前哨站

前哨站放置于前哨站底座上，靠近公路飞坡，由前哨站主体、3块前哨站装甲模块、飞镖检测模块组成。飞镖检测模块示意图请参阅“图4-13飞镖检测模块示意图”。前哨站增益点位于前哨站四周，具体位置如下图所示。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//427db8d3-19f1-46ca-9a83-13ec69699332/markdown_2/imgs/img_in_image_box_244_401_481_584.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A50Z%2F-1%2F%2F05c688d2ed14fce98bb402400babddf8dec70ec6f26885534f29bf541a85cfa9" alt="Image" width="19%" /></div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//427db8d3-19f1-46ca-9a83-13ec69699332/markdown_2/imgs/img_in_image_box_621_339_876_596.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A50Z%2F-1%2F%2F6ebcbb08afe67a34d49fee22d82d9be691610e7a71c9dfa4ff74373afb6cc6eb" alt="Image" width="21%" /></div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//427db8d3-19f1-46ca-9a83-13ec69699332/markdown_2/imgs/img_in_image_box_315_724_581_1022.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A50Z%2F-1%2F%2F318b17168193d1a54500a68b230be0e98572cabdba073096276c05baf0203ef5" alt="Image" width="22%" /></div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//427db8d3-19f1-46ca-9a83-13ec69699332/markdown_2/imgs/img_in_image_box_638_630_973_984.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A51Z%2F-1%2F%2F8e45c5de98c06f4323398197526d5557617b3ea370a67c54f0cc7711a59eb6fb" alt="Image" width="28%" /></div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//427db8d3-19f1-46ca-9a83-13ec69699332/markdown_2/imgs/img_in_image_box_343_1077_525_1267.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A51Z%2F-1%2F%2F8d974c45cb7d9935976e669bfffb3cfc4f9605040c9ffda2fb76752c679122a7" alt="Image" width="15%" /></div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//427db8d3-19f1-46ca-9a83-13ec69699332/markdown_2/imgs/img_in_image_box_644_1051_896_1369.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A51Z%2F-1%2F%2F6a26b76d9ab063af9ca9fdb9a1468466b43d5ef986dbf35862c3eeb5d2ea8991" alt="Image" width="21%" /></div>


<div style="text-align: center;"><div style="text-align: center;">[1] 前哨站底座</div> </div>


<div style="text-align: center;"><div style="text-align: center;">[2] 前哨站 [3] 中部装甲</div> </div>


<div style="text-align: center;"><div style="text-align: center;">图 4-34 前哨站示意图</div> </div>


### 4.4 公路区

公路区包括公路、飞坡、隧道、起伏路段。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//427db8d3-19f1-46ca-9a83-13ec69699332/markdown_3/imgs/img_in_image_box_162_301_997_873.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A52Z%2F-1%2F%2Fbdb113a201ff1ab6c070fa58b0dfcf422df3f74b49255800081d042c901b2759" alt="Image" width="70%" /></div>


<div style="text-align: center;"><div style="text-align: center;">[1]  $ 11^{\circ} $ 坡 [2]  $ 15^{\circ} $ 坡</div> </div>


<div style="text-align: center;"><div style="text-align: center;">图 4-35 公路区示意图</div> </div>


#### 4.4.1 起伏路段

起伏路段位于公路区，其表面按照一定间距、图示方向排布着凸起，如下所示。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//dd09100e-901f-4b2b-ab1b-4e771d699f4c/markdown_0/imgs/img_in_image_box_161_279_1032_821.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A51Z%2F-1%2F%2F6f15844940722e1ee18c246a38d56b393d5e07e9a4aa95647e0cf9fc05bc92c4" alt="Image" width="73%" /></div>


<div style="text-align: center;"><div style="text-align: center;">[1] 起伏路段</div> </div>


<div style="text-align: center;"><div style="text-align: center;">图 4-36 起伏路段示意图</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//dd09100e-901f-4b2b-ab1b-4e771d699f4c/markdown_0/imgs/img_in_image_box_505_965_675_1384.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A51Z%2F-1%2F%2F54c9e1fc5064121dee74c3521a8ca590955a1b3215aaf90a10f64fc20fe4d4bc" alt="Image" width="14%" /></div>


<div style="text-align: center;"><div style="text-align: center;">图 4-37 凸起示意图</div> </div>


#### 4.4.2 飞坡

飞坡位于公路区上，机器人可通过飞坡飞跃沟壑，快速抵达对方半场。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//dd09100e-901f-4b2b-ab1b-4e771d699f4c/markdown_1/imgs/img_in_image_box_275_276_888_568.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A54Z%2F-1%2F%2Fb14391f9e438c92cd571ef1ee74718742fec0245ede9365ef371f73ec003bace" alt="Image" width="51%" /></div>


<div style="text-align: center;"><div style="text-align: center;">[1]</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//dd09100e-901f-4b2b-ab1b-4e771d699f4c/markdown_1/imgs/img_in_image_box_289_592_899_809.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A55Z%2F-1%2F%2F3db6cc1da7a22bd81c19e3fb0de4e307670c66741f6f4512f026170e4983d9e5" alt="Image" width="51%" /></div>


<div style="text-align: center;"><div style="text-align: center;">[1]  $ 17^{\circ} $ 坡</div> </div>


<div style="text-align: center;"><div style="text-align: center;">图 4-38 飞坡示意图</div> </div>


### 4.5 飞行区

飞行区是空中机器人的飞行区域，包括停机坪及上方空域和与梯形高地连接的公路上方空域。

为保证机器人运行安全，空中机器人在比赛过程中需连接安全绳。安全绳的长度为  $ 2.4 \, m $。飞行距离受安全绳卡环限制，卡环距离己方战场宽边约为  $ 14 \, m $。当空中机器人飞行至最远位置时，飞手不应操作空中机器人向前飞行。

为保证机器人运行安全，空中机器人在比赛过程中需通过安全绳与空中机器人回收系统相连接。空中机器人回收系统由钢丝绳、回收装置、拉线盒组成。回收装置和拉线盒悬挂在钢丝绳上，钢丝绳在距离已方场边约14m的位置设置有卡环，拉线盒无法跨越卡环。拉线盒重约800g，内部设置有2.4m的回弹力恒定的软线，软线的静回弹力小于5N，软线末端通过挂钩与空中机器人相连接。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//dd09100e-901f-4b2b-ab1b-4e771d699f4c/markdown_2/imgs/img_in_image_box_130_603_175_648.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A57Z%2F-1%2F%2Fe04e3df7a4b0413b00326a2661f23baa2a60bf429797bab2c9b6ce876e5e5521" alt="Image" width="3%" /></div>


回收装置悬挂于飞手操作间正上方的钢丝绳上，当空中机器人正常飞行时，不会跟随飞机移动，此时只有拉线盒跟随空中机器人移动；当出现空中机器人坠落等情况，且在裁判判断可以且有必要对空中机器人进行回收时，回收装置才会启动，并运动到拉线盒位置对空中机器人进行回收。

拉线盒无旋转接口，若空中机器人进行过多单向旋转动作，拉线盒可能会卡死。

### 4.6 其它

#### 4.6.1 可移动道具

能量单元为可移动道具，可被机器人抓取和携带。能量单元是重量约为  $ 400 \pm 50 $g 的中空柱体，双端不对称。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//dd09100e-901f-4b2b-ab1b-4e771d699f4c/markdown_2/imgs/img_in_image_box_127_1140_170_1188.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A58Z%2F-1%2F%2F1ce251ae9f2a0c5ae1927484e8265547029ef861c019df3c6ab69b5cc2cbd808" alt="Image" width="3%" /></div>


随着比赛的进行，可移动道具表面可能出现轻微破损或灰尘积累，该情况需参赛队伍自行适应，但污损严重的可移动道具将不会被用于正式比赛。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//dd09100e-901f-4b2b-ab1b-4e771d699f4c/markdown_3/imgs/img_in_image_box_355_167_841_1174.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A03%3A00Z%2F-1%2F%2F537dd53b585f4defda27ae6a549456d1c2e7060c85499aa53fb79c87321b3f54" alt="Image" width="40%" /></div>


<div style="text-align: center;"><div style="text-align: center;">[1] 铁片</div> </div>


<div style="text-align: center;"><div style="text-align: center;">图 4-39 能量单元示意图</div> </div>


#### 4.6.2 弹丸

机器人可通过发射弹丸攻击装甲模块，进而造成伤害。比赛中使用的弹丸参数及安排如下所示：

<div style="text-align: center;"><div style="text-align: center;">表 4-1 弹丸参数及使用安排</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>类型</td><td style='text-align: center; word-wrap: break-word;'>外观</td><td style='text-align: center; word-wrap: break-word;'>颜色</td><td style='text-align: center; word-wrap: break-word;'>尺寸</td><td style='text-align: center; word-wrap: break-word;'>质量</td><td style='text-align: center; word-wrap: break-word;'>邵氏硬度</td><td style='text-align: center; word-wrap: break-word;'>材质</td><td style='text-align: center; word-wrap: break-word;'>使用安排</td><td style='text-align: center; word-wrap: break-word;'>额定数量</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>42mm\n发光弹丸</td><td style='text-align: center; word-wrap: break-word;'>与高尔夫球外形相似</td><td style='text-align: center; word-wrap: break-word;'>半透明</td><td style='text-align: center; word-wrap: break-word;'>42.5mm\n $ \pm $0.5mm</td><td style='text-align: center; word-wrap: break-word;'>44.5g\n $ \pm $0.5g</td><td style='text-align: center; word-wrap: break-word;'>90 $ \pm $5A</td><td style='text-align: center; word-wrap: break-word;'>塑胶\nTPE</td><td style='text-align: center; word-wrap: break-word;'>RMUC\n2026 全程</td><td style='text-align: center; word-wrap: break-word;'>100 发/局</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>17mm\n荧光弹丸</td><td style='text-align: center; word-wrap: break-word;'>球形</td><td style='text-align: center; word-wrap: break-word;'>黄绿色</td><td style='text-align: center; word-wrap: break-word;'>16.8mm\n $ \pm $0.2mm</td><td style='text-align: center; word-wrap: break-word;'>3.2g $ \pm $0.1g</td><td style='text-align: center; word-wrap: break-word;'>90 $ \pm $5A</td><td style='text-align: center; word-wrap: break-word;'>塑胶\nTPU</td><td style='text-align: center; word-wrap: break-word;'>RMUC\n2026 全程</td><td style='text-align: center; word-wrap: break-word;'>有限，但不少于 4000 发/局</td></tr></table>

#### 4.6.3 操作间

操作间位于战场外围附近，是比赛时操作手的活动区域。操作间分为主操作间和飞手操作间。主操作间每个操作手桌面长120cm，宽75cm，配置对应数量的电脑，且每台电脑配备对应的显示器、鼠标、键盘、相机图传模块（接收端）及其支架、3个USB Type-A母头接口、1个RS232公头接口、1个1GbE（RJ45）网口和有线耳机等官方设备。飞手操作间仅配备护目镜，用于防止对方雷达激光照射。

主操作间桌面布局图如下，操作间桌面设有显示器、转播摄像头、相机图传模块（接收端）及其支架、键盘、鼠标、设备放置区，其中显示器、转播摄像头、接口的位置固定，不可移动。相机图传模块（接收端）支架固定于桌面上，操作手可在支架移动范围内操作相机图传模块（接收端）。键盘、鼠标可以自由移动，操作手可将自定义控制器、自定义客户端放置于放置区上。具体布局如下图所示：

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//b6b3dd69-17d5-4642-a284-2f0f7b81c446/markdown_1/imgs/img_in_image_box_159_150_568_608.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A44Z%2F-1%2F%2Ff6ff49e512356a6b1403b2a46b355d0a4ef9a53894d63c130a848f6579eb587d" alt="Image" width="34%" /></div>


<div style="text-align: center;"><div style="text-align: center;">[1] 接口位置 [2] 显示器</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//b6b3dd69-17d5-4642-a284-2f0f7b81c446/markdown_1/imgs/img_in_image_box_619_163_1004_550.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A44Z%2F-1%2F%2Fd123648534e6e5bcb1d209d3c4ae5f88cad35cbfdb29b0b9b545fc64c551eca6" alt="Image" width="32%" /></div>


<div style="text-align: center;"><div style="text-align: center;">[3] 键鼠 [4] 可放置区域</div> </div>


<div style="text-align: center;"><div style="text-align: center;">[5] 转播摄像头 [6] 相机图传模块（接收端）及其支架 [7] 置物架</div> </div>


<div style="text-align: center;"><div style="text-align: center;">图 4-40 主操作间布局示意图</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//b6b3dd69-17d5-4642-a284-2f0f7b81c446/markdown_1/imgs/img_in_image_box_122_826_164_869.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A44Z%2F-1%2F%2Fc4b2f6629976ce702a908beed317b1a1f53c170d0293f2518f3e32317176d08c" alt="Image" width="3%" /></div>


禁止将相机图传模块（接收端）从支架上取出，由此产生的后果由参赛队伍自行承担。

## 5 比赛机制

### 5.1 扣血与超限惩罚机制

#### 5.1.1 攻击伤害或撞击

地面机器人、基地、前哨站的装甲模块在受到攻击或者撞击时，可能被扣除血量。具体机制如下：

飞镖检测模块通过装甲模块结合光电管检测飞镖攻击，可以检测飞镖和42mm弹丸的攻击。

装甲模块具备弹丸攻击检测功能。其中，17mm 弹丸的最小检测间隔为 50ms，42mm 弹丸的最小检测间隔为 200ms。

弹丸需以一定的速度接触装甲模块受攻击面才能被有效检测。装甲模块对不同类型弹丸的有效检测速度范围如下表所示：

<div style="text-align: center;"><div style="text-align: center;">表 5-1 装甲模块对不同类型弹丸的有效检测速度</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>装甲模块</td><td style='text-align: center; word-wrap: break-word;'>17mm 弹丸</td><td style='text-align: center; word-wrap: break-word;'>42mm 弹丸</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>● 大装甲模块、小装甲模块\n● 基地装甲模块\n● 前哨站装甲模块</td><td style='text-align: center; word-wrap: break-word;'>大于 12m/s</td><td style='text-align: center; word-wrap: break-word;'>大于 10m/s</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>● 能量机关装甲模块</td><td style='text-align: center; word-wrap: break-word;'>大于 12m/s</td><td style='text-align: center; word-wrap: break-word;'>-</td></tr></table>

实际比赛中，由于弹丸速度衰减和入射角度非装甲模块受攻击面法向，接触到装甲模块受攻击面的弹丸的法向速度与弹丸射击初速度不同。伤害检测以弹丸接触装甲模块受攻击面的速度法向分量为准。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//b6b3dd69-17d5-4642-a284-2f0f7b81c446/markdown_2/imgs/img_in_image_box_132_1211_176_1254.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A44Z%2F-1%2F%2F7e35c593f1725d8f5b48fffab35deb948694fb127100608b619559aef3d606cb" alt="Image" width="3%" /></div>


参赛队伍不得使用42mm弹丸或飞镖击打能量机关。

当一方英雄机器人连续4秒未发射42mm弹丸，对方的机器人、前哨站、基地的所有装甲将屏蔽42mm弹丸伤害，直到英雄机器人发射42mm弹丸。

为确保检测精度、减少误检，部分情况下，裁判系统需等待42mm弹丸的发射信息匹配，因此装甲模块在检测到42mm弹丸打击后，伤害结算可能会略有延迟。

地面机器人、基地、前哨站的装甲模块受到撞击时有概率被判定为弹丸伤害，但是不允许通过撞击（包括与机器人冲撞，抛掷物体等）的方式对对方造成伤害。

在无任何增益的情况下，原始伤害值如下表所示：

<div style="text-align: center;"><div style="text-align: center;">表 5-2 攻击伤害或撞击的扣血机制</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>伤害类型\n作用对象</td><td style='text-align: center; word-wrap: break-word;'>42mm 弹丸</td><td style='text-align: center; word-wrap: break-word;'>17mm 弹丸</td><td style='text-align: center; word-wrap: break-word;'>飞镖</td><td style='text-align: center; word-wrap: break-word;'>撞击</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>机器人装甲模块</td><td style='text-align: center; word-wrap: break-word;'>200</td><td style='text-align: center; word-wrap: break-word;'>20</td><td style='text-align: center; word-wrap: break-word;'>-</td><td style='text-align: center; word-wrap: break-word;'>2</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>基地装甲模块</td><td style='text-align: center; word-wrap: break-word;'>200</td><td style='text-align: center; word-wrap: break-word;'>● 上方前装甲模块：5\n● 其余5块装甲模块：20</td><td style='text-align: center; word-wrap: break-word;'>-</td><td style='text-align: center; word-wrap: break-word;'>-</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>基地飞镖检测模块</td><td style='text-align: center; word-wrap: break-word;'>-</td><td style='text-align: center; word-wrap: break-word;'>-</td><td style='text-align: center; word-wrap: break-word;'>● 固定目标：200\n● 随机固定目标：300\n● 随机移动目标：625\n● 末端移动目标：1000</td><td style='text-align: center; word-wrap: break-word;'>-</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>前哨站中部装甲模块</td><td style='text-align: center; word-wrap: break-word;'>200</td><td style='text-align: center; word-wrap: break-word;'>20</td><td style='text-align: center; word-wrap: break-word;'>-</td><td style='text-align: center; word-wrap: break-word;'>-</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>前哨站飞镖检测模块</td><td style='text-align: center; word-wrap: break-word;'>-</td><td style='text-align: center; word-wrap: break-word;'>-</td><td style='text-align: center; word-wrap: break-word;'>750</td><td style='text-align: center; word-wrap: break-word;'>-</td></tr></table>

#### 5.1.2 射击初速度超限

英雄、步兵、空中、哨兵机器人的射击初速度超限时，该机器人的发射机构会被锁定，一定时间后解锁，时间不累加。

射击初速度超限导致的锁定和解锁与其他情况导致的锁定和解锁相互独立。设定机器人的射击初速度上限为  $ V_{0} $ (m/s)，裁判系统检测到弹丸实际射击初速度为  $ V_{1} $ (m/s)。具体锁定时间如下表所示：

<div style="text-align: center;"><div style="text-align: center;">表 5-3 射击初速度超限惩罚机制</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>17mm 弹丸</td><td style='text-align: center; word-wrap: break-word;'>42mm 弹丸（非部署模式下）</td><td style='text-align: center; word-wrap: break-word;'>42mm 弹丸（部署模式下）</td><td style='text-align: center; word-wrap: break-word;'>锁定时间</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>0 &lt;  $ V_{{1}} $ -  $ V_{{0}} $ &lt; 5</td><td style='text-align: center; word-wrap: break-word;'>$ V_{{0}} $ &lt;  $ V_{{1}} $ ≤ 1.1 *  $ V_{{0}} $</td><td style='text-align: center; word-wrap: break-word;'>$ V_{{0}} $ &lt;  $ V_{{1}} $ ≤ 18</td><td style='text-align: center; word-wrap: break-word;'>15 秒</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>5 ≤  $ V_{{1}} $ -  $ V_{{0}} $ &lt; 10</td><td style='text-align: center; word-wrap: break-word;'>1.1 *  $ V_{{0}} $ &lt;  $ V_{{1}} $ ≤ 1.2 *  $ V_{{0}} $</td><td style='text-align: center; word-wrap: break-word;'>-</td><td style='text-align: center; word-wrap: break-word;'>20 秒</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>10 ≤  $ V_{{1}} $ -  $ V_{{0}} $</td><td style='text-align: center; word-wrap: break-word;'>1.2 *  $ V_{{0}} $ &lt;  $ V_{{1}} $</td><td style='text-align: center; word-wrap: break-word;'>18 &lt;  $ V_{{1}} $</td><td style='text-align: center; word-wrap: break-word;'>当局后续全部时间，且不再解锁</td></tr></table>

#### 5.1.3 射击热量超限和冷却

英雄、步兵、空中、哨兵机器人的射击热量超限时，该机器人的发射机构会被锁定，射击热量超限导致的锁定和解锁与其他情况导致的锁定和解锁相互独立。具体机制如下：

设定机器人的射击热量上限为  $ Q_{0} $，当前射击热量为  $ Q_{1} $，裁判系统每检测到一发 17mm 弹丸，当前射击热量  $ Q_{1} $ 增加 10（与 17mm 弹丸的射击初速度无关）。每检测到一发 42mm 弹丸，当前射击热量  $ Q_{1} $ 增加 100（与 42mm 弹丸的射击初速度无关）。射击热量按 10Hz 的频率结算冷却，每个检测周期热量冷却值=每秒冷却值/10。

当  $ Q_2 > Q_1 > Q_0 $，该机器人对应操作手的第一视角操作界面图传画面断开，且发射机构会被锁定，直到  $ Q_1 = 0 $，第一视角操作界面才会恢复正常，且发射机构解锁。

当  $ Q_{1} > Q_{2} $，该机器人在当局后续全部时间发射机构锁定，且不再解锁。

对于 17mm 发射机构， $ Q_{2}=Q_{0}+100 $;

对于 42mm 发射机构， $ Q_{2}=Q_{0}+200 $。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//6e8833af-7e6b-4ee8-a33a-1f7e70cf1458/markdown_0/imgs/img_in_image_box_137_718_1057_1362.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A44Z%2F-1%2F%2F622c46b55d2a969d870939f716bf227509a37f66348f18267fec5e370b20abf3" alt="Image" width="77%" /></div>


<div style="text-align: center;"><div style="text-align: center;">图 5-1 射击热量超限及冷却机制</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//6e8833af-7e6b-4ee8-a33a-1f7e70cf1458/markdown_0/imgs/img_in_image_box_131_1444_172_1485.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A44Z%2F-1%2F%2Fa97326d247617b2f97f75bfc9eb7e3bfa6c4ec76b589952e4c620dff0aeb4ff9" alt="Image" width="3%" /></div>


因超热量导致图传画面断开时，小地图、自定义 UI 仍可正常使用。

#### 5.1.4 底盘功率超限

裁判系统持续监控机器人底盘功率，机器人底盘需在功率限制范围内运行。地面机器人底盘功率超限时，该机器人将扣除缓冲能量。当缓冲能量耗尽，底盘功率仍超限时，底盘会被断电5秒。裁判系统进行底盘功率检测的结算频率是10Hz。

设定 Z 为缓冲能量，Q 为缓冲能量上限（Q=60J）， $ P_{r} $ 为瞬时底盘输出功率， $ P_{1} $ 为上限功率。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//6e8833af-7e6b-4ee8-a33a-1f7e70cf1458/markdown_1/imgs/img_in_image_box_300_398_916_1084.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A45Z%2F-1%2F%2F27b01ed9f7e5ebcfadafdeaaa8933f2a95d7d42a86c5d1307b718f5c157ed263" alt="Image" width="51%" /></div>


<div style="text-align: center;"><div style="text-align: center;">图 5-2 机器人底盘功率检测及超限惩罚机制</div> </div>


#### 5.1.5 裁判系统模块离线

参赛队伍按照《RoboMaster 2026 机甲大师高校系列赛机器人制作规范手册》要求安装机器人对应的裁判系统模块，在比赛过程中需保持裁判系统各个模块与服务器连接稳定性。裁判系统服务器以 2Hz 的频率检测各个模块的连接状态。

##### 5.1.5.1 异常离线

比赛过程中，若机器人主控模块离线，进入“异常离线”状态，可以重连回比赛，离线过程中会继续结算经验、等级。

<div style="text-align: center;"><div style="text-align: center;">表 5-4 机器人异常离线的惩罚机制</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>机器人种类</td><td style='text-align: center; word-wrap: break-word;'>离线期间的处理方法</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>地面机器人</td><td style='text-align: center; word-wrap: break-word;'>● 发射机构（如有）、云台、底盘断电，每秒扣除上限血量的5%，直至为0\n● 场地交互模块失效\n● 机器人不再检测撞击和弹丸击打造成的伤害和模块离线扣血\n● 复活读条不再增加\n● 多机通信断开</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>空中机器人</td><td style='text-align: center; word-wrap: break-word;'>● 发射机构断电，无法呼叫空中支援\n● 不检测激光发射装置的照射\n● 图传画面断开\n● 多机通信断开</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>雷达</td><td style='text-align: center; word-wrap: break-word;'>● 多机通信断开\n● 激光发射装置及其执行机构断电</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>飞镖</td><td style='text-align: center; word-wrap: break-word;'>● 若在飞镖发射站闸门关闭时离线：飞镖发射站闸门无法开启\n● 若在飞镖发射站闸门开启时离线：飞镖发射站闸门立刻关闭且无法开启</td></tr></table>

##### 5.1.5.2 装甲模块或超级电容管理模块离线

若地面机器人因自身设计及结构等问题造成装甲模块或超级电容管理模块离线，该机器人将被扣除血量。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//6e8833af-7e6b-4ee8-a33a-1f7e70cf1458/markdown_3/imgs/img_in_image_box_432_260_729_966.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A46Z%2F-1%2F%2Fdad414c4fb04a3c4b8325140f24d7837b9e92a94c7964a71383441c1f9d22b57" alt="Image" width="24%" /></div>


<div style="text-align: center;"><div style="text-align: center;">图 5-3 装甲模块和超级电容管理模块离线的扣血机制</div> </div>


##### 5.1.5.3 测速模块离线

若英雄、步兵、哨兵、空中机器人装载的 17mm 测速模块或 42mm 测速模块离线，该机器人的 17mm 或 42mm 发射机构将立即锁定，测速模块离线导致的锁定和解锁与其他情况导致的锁定与解锁相互独立。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//66014972-55a9-4190-b899-d0fbf760c86a/markdown_0/imgs/img_in_image_box_314_302_879_1087.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A43Z%2F-1%2F%2Fbee19c49fc681ce72384a69351e0cfbe1b359b9b5c5af607b838fd57858f749d" alt="Image" width="47%" /></div>


<div style="text-align: center;"><div style="text-align: center;">图 5-4 测速模块离线的断电机制</div> </div>


##### 5.1.5.4 定位模块离线

若英雄、工程、步兵、空中、哨兵机器人装载的定位模块离线，对方雷达对该机器人的标记将始终视为“准确”，己方雷达对该机器人的标记始终视为“错误”。

##### 5.1.5.5 激光检测模块离线

若空中机器人装载的激光检测模块离线，则在空中机器人发起空中支援期间，其始终视为被对方激光发射装置持续照射。

#### 5.1.6 判罚伤害

当地面机器人受到黄牌或红牌警告等判罚时，可能被扣除血量，详见“7.1判罚体系”。

### 5.2 回血与复活机制

除在异常离线或者被罚下的状态以外，地面机器人均可以回血和复活。

#### 5.2.1 回血机制

##### 补给区回血

地面机器人占领己方补给区增益点时，将获得每秒上限血量10%的回血增益。在比赛开始4分钟后，当机器人处于脱战状态，且占领己方补给区增益点时，其将获得每秒上限血量25%的回血增益；当机器人不处于脱战状态，每秒上限血量25%的回血增益立即失效。

##### 远程兑换血量

在一局比赛中，英雄机器人、步兵机器人、哨兵机器人处于脱战状态时，可以花费金币远程兑换血量。当确定远程兑换血量6秒后，该机器人增加此时上限血量的60%，但不会超过上限血量。

若确定远程兑换血量6秒内，机器人战亡，则远程兑换血量无效，且金币不会返还。

机器人是否位于补给区的判断方式：当机器人的场地交互模块检测到补给区场地交互模块卡，或机器人位于规则设定下的补给区时，机器人的相机图传模块识别到补给区视觉标签，均视为其位于补给区。存活机器人位于己方补给区时，视为占领补给区增益点。

仅当视觉标签位于图传模块图像中心区域且图传模块无明显滚转角时，图传模块能够识别视觉标签。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//66014972-55a9-4190-b899-d0fbf760c86a/markdown_2/imgs/img_in_image_box_185_153_977_943.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A43Z%2F-1%2F%2F867483f0a25eea00c6c92a2aac12df2a7c85d160888d3c129d076040c5d4294f" alt="Image" width="66%" /></div>


<div style="text-align: center;"><div style="text-align: center;">[1] 视觉标签 [2] 机器人图传范围 [3] 可识别区</div> </div>


<div style="text-align: center;"><div style="text-align: center;">图 5-5 机器人图传模块与视觉标签的相对位置示意图</div> </div>


#### 5.2.2 复活机制

机器人战亡时，其射击热量将被重置为0，缓冲能量将被重置为缓冲能量上限。战亡的机器人可以通过完成复活读条复活，或在复活读条进行过程中通过金币兑换立即复活。

当通过完成复活读条复活时，所需的复活读条与机器人战亡时比赛剩余时长和机器人累计兑换立即复活的次数相关，具体公式如下：

 $$  所需复活读条 =10+\frac{420- 比赛剩余时长 }{10}+20* 累计兑换立即复活次数 $$ 

比赛剩余时长单位为秒。小数部分四舍五入，保留整数。

示例：在比赛剩余120秒时，一台机器人战亡，且此前其已经进行过2次兑换立即复活，则其本次复活读条长度为 $ 10+\frac{420-120}{10}+20*2=80 $。

机器人战亡后会立即开始复活读条，自机器人战亡时刻开始，每秒读条进度增加1；当机器人位于补给区增益点或该方基地血量低于2000，每秒读条进度提高为4。

通过完成复活读条复活时：

保持战亡前的等级与经验值，暂时处于无敌状态，持续30秒。

➢ 血量恢复至上限血量的10%。

进入“虚弱”状态。

此后，在其检测到可占领的前哨站、基地增益点或补给区增益点的场地交互模块卡后，其“虚弱”状态解除，若其因当次复活获得的无敌状态已累计超过10秒，则无敌状态解除；若其因当次复活获得的无敌状态未计满10秒，则无敌状态计满10秒后解除。

当通过使用金币兑换立即复活时：

保持战亡前的等级与经验值，暂时处于虚弱与无敌状态，持续3秒，此后虚弱与无敌状态解除。

➢ 血量恢复至上限血量的 100%。

➢ 底盘功率上限提高1倍（但不超过200W），持续4秒。

此后，在其检测到可占领的前哨站、基地增益点或补给区增益点的场地交互模块卡后，其“虚弱”状态解除。

“虚弱”状态下的机器人：

发射机构锁定。

☑ 无法占领任何增益点且无法重建前哨站。

### 5.3 经济体系

#### 5.3.1 经济体系概述

三分钟准备阶段，地面机器人均可预装42mm和17mm弹丸，空中机器人仅可预装17mm弹丸。

比赛开始时，双方各获得一定量的初始金币，随着比赛的推进，双方将定期获得金币，具体增量如下表所示。比赛过程中，也可通过装配能量单元的方式获得额外金币。金币可以用于兑换空中支援、17mm/42mm允许发弹量、远程回血、立即复活。

<div style="text-align: center;"><div style="text-align: center;">表 5-5 机器人定期获得金币的增量一览</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>比赛倒计时</td><td style='text-align: center; word-wrap: break-word;'>红方</td><td style='text-align: center; word-wrap: break-word;'>蓝方</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>06:59</td><td style='text-align: center; word-wrap: break-word;'>400（初始）</td><td style='text-align: center; word-wrap: break-word;'>400（初始）</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>05:59</td><td style='text-align: center; word-wrap: break-word;'>50</td><td style='text-align: center; word-wrap: break-word;'>50</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>04:59</td><td style='text-align: center; word-wrap: break-word;'>50</td><td style='text-align: center; word-wrap: break-word;'>50</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>03:59</td><td style='text-align: center; word-wrap: break-word;'>50</td><td style='text-align: center; word-wrap: break-word;'>50</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>02:59</td><td style='text-align: center; word-wrap: break-word;'>50</td><td style='text-align: center; word-wrap: break-word;'>50</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>01:59</td><td style='text-align: center; word-wrap: break-word;'>50</td><td style='text-align: center; word-wrap: break-word;'>50</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>00:59</td><td style='text-align: center; word-wrap: break-word;'>150</td><td style='text-align: center; word-wrap: break-word;'>150</td></tr></table>

<div style="text-align: center;"><div style="text-align: center;">表 5-6 兑换规则</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>兑换项目</td><td style='text-align: center; word-wrap: break-word;'>兑换比例</td><td style='text-align: center; word-wrap: break-word;'>兑换上限</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>17mm 允许发弹量</td><td style='text-align: center; word-wrap: break-word;'>● 远程兑换：150 金币/100 发\n● 非远程兑换：10 金币/10 发</td><td style='text-align: center; word-wrap: break-word;'>1000 发/队</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>42mm 允许发弹量</td><td style='text-align: center; word-wrap: break-word;'>● 远程兑换：150 金币/10 发\n● 非远程兑换：10 金币/1 发</td><td style='text-align: center; word-wrap: break-word;'>100 发/队</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>空中支援时间</td><td style='text-align: center; word-wrap: break-word;'>1 金币/1 秒</td><td style='text-align: center; word-wrap: break-word;'>不限</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>血量（远程兑换）</td><td style='text-align: center; word-wrap: break-word;'>50+ROUNDUP( $ \frac{420-比赛剩余时长}{60} $*20)金币/1 次</td><td style='text-align: center; word-wrap: break-word;'>次数不限</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>立即复活</td><td style='text-align: center; word-wrap: break-word;'>ROUNDUP( $ \frac{420-比赛剩余时长}{60} $)*80+机器人等级*20金币/1 台</td><td style='text-align: center; word-wrap: break-word;'>次数不限</td></tr></table>

时长单位为秒。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//ae8f2d29-b9a9-4072-8d1c-e07e3b207d5e/markdown_0/imgs/img_in_image_box_134_1346_177_1386.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A44Z%2F-1%2F%2F161c47d4ac8c00d87ac252752d074797a2a340d26f9239b433753fd2c97c76c6" alt="Image" width="3%" /></div>


ROUNDUP 表示向上取整，精确至个位。

17mm 允许发弹量的兑换上限是指通过金币兑换的允许发弹量上限。

#### 5.3.2 允许发弹量机制

机器人每发射1发弹丸，所发射的弹丸类型对应的允许发弹量减少1发。

在以下特殊情况下，对方的机器人、前哨站、基地的所有装甲将屏蔽 42mm 弹丸伤害，直到英雄机器人变为存活状态且允许发弹量大于 0:

英雄机器人由存活状态变为战亡、异常离线的3秒后。

英雄机器人在允许发弹量为0时发射42mm弹丸（出现超发行为）。

英雄机器人战亡后发射第3发42mm弹丸后。

各机器人的初始允许发弹量和机制适用情况如下表所示：

<div style="text-align: center;"><div style="text-align: center;">表 5-7 机器人允许发弹量一览</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>机器人</td><td style='text-align: center; word-wrap: break-word;'>初始允许发弹量</td><td style='text-align: center; word-wrap: break-word;'>允许发弹量机制</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>英雄机器人</td><td style='text-align: center; word-wrap: break-word;'>0</td><td rowspan="2">补给区、基地增益点、前哨站增益点兑换或远程兑换允许发弹量。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>步兵机器人</td><td style='text-align: center; word-wrap: break-word;'>0</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>哨兵机器人</td><td style='text-align: center; word-wrap: break-word;'>300</td><td style='text-align: center; word-wrap: break-word;'>补给区、基地增益点、前哨站增益点兑换，远程兑换允许发弹量或补给区获取。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>空中机器人</td><td style='text-align: center; word-wrap: break-word;'>750</td><td style='text-align: center; word-wrap: break-word;'>不可额外获得允许发弹量。</td></tr></table>

补给区、基地增益点、前哨站增益点兑换

当英雄、步兵、哨兵机器人占领补给区、基地增益点、前哨站增益点时，操作手可通过裁判系统选手端兑换允许发弹量；哨兵机器人还可通过裁判系统串口自行兑换允许发弹量。具体可兑换类型和最小兑换单位如下表所示：

<div style="text-align: center;"><div style="text-align: center;">表 5-8 （补给区、基地增益点、前哨站增益点兑换时）不同类型弹丸允许发弹量的最小兑换单位</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>17mm 允许发弹量</td><td style='text-align: center; word-wrap: break-word;'>42mm 允许发弹量</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>10 发</td><td style='text-align: center; word-wrap: break-word;'>1 发</td></tr></table>

##### 远程兑换

若机器人处于脱战状态，操作手可通过裁判系统选手端远程兑换允许发弹量，哨兵机器人可通过裁判系统串口自行远程兑换允许发弹量。具体可兑换类型和最小兑换单位如下表所示：

<div style="text-align: center;"><div style="text-align: center;">表 5-9 （远程兑换时）不同类型弹丸允许发弹量的最小兑换单位</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>17mm 允许发弹量</td><td style='text-align: center; word-wrap: break-word;'>42mm 允许发弹量</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>100 发</td><td style='text-align: center; word-wrap: break-word;'>10 发</td></tr></table>

远程兑换成功后，允许发弹量将在6秒后生效。

##### 补给区获取

比赛开始后，每隔1分钟，哨兵机器人可以通过占领己方补给区增益点获取100发允许发弹量，未通过此方式获取的允许发弹量可以累积。

示例：若哨兵机器人从未占领己方补给区增益点，在比赛剩余30秒时占领己方补给区增益点，则哨兵机器人允许发弹量将增加600。

#### 5.3.3 科技核心-能量单元机制

比赛过程中，工程机器人将其携带的能量单元装配入科技核心，以换取金币和团队增益。

对于每个科技核心而言，以底座正面与战场地面相交线段中点为原点 O，底座正面法线指向科技核心的方向为 X 轴负方向，竖直向上为 Z 轴正方向，建立右手直角坐标系，命名为装配坐标系 OXYZ。以能量单元装配柱前表面的几何中心为原点 E 建立右手直角坐标系 EX'YZ'，其中 X',Y',Z'轴均与 X,Y,Z 轴平行且正方向一致。能量单元装配柱前表面的单位法向量为  $  \mathbf{e}^*  $。基于科技核心坐标系建立球坐标系  $  (\mathbf{r},\theta,\phi)  $， $ \theta $ 为  $  \mathbf{e}^\star  $ 在  $  \mathbf{X}'\mathbf{Y}'  $ 平面的投影和正  $  \mathbf{X}  $ 轴的夹角， $ \theta \in [-90,90] $； $ \phi $ 为  $  \mathbf{e}^\star  $ 和正  $  \mathbf{Z}  $ 轴的夹角， $ \phi \in [0,90] $。另定义  $  \alpha  $ 为科技核心围绕  $  \mathbf{e}^\star  $ 方向的旋转角度，逆时针旋转为  $  \alpha  $ 为正， $  \alpha \in [-45,45]  $。

能量单元装配柱前表面中心点 E 在 OXYZ 坐标系下的坐标 (x,y,z)，单位法向量  $ \vec{e} $ 在科技核心球坐标系下的方位坐标 ( $ \theta,\phi $) 与科技核心围绕  $ \vec{e} $ 方向的旋转角度  $ \alpha $ 的组合 (x,y,z, $ \theta $, $ \phi $, $ \alpha $) 称为科技核心的位姿。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//ae8f2d29-b9a9-4072-8d1c-e07e3b207d5e/markdown_3/imgs/img_in_image_box_194_139_982_768.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A45Z%2F-1%2F%2Fd47ea43ec9d4484ec8a9ff3f670cd71904fe2db1084fe46e432d7cd3cf2cf064" alt="Image" width="66%" /></div>


<div style="text-align: center;"><div style="text-align: center;">[1] 科技核心 [2] 装配柱 [3] 底座</div> </div>


<div style="text-align: center;"><div style="text-align: center;">图 5-6 科技核心示意图</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//ae8f2d29-b9a9-4072-8d1c-e07e3b207d5e/markdown_3/imgs/img_in_image_box_253_925_960_1352.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A45Z%2F-1%2F%2F016acb36d43fc1b768c294f52d75f50cee99aa9d4bddbdd1adfdedaffe3c26b7" alt="Image" width="59%" /></div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//b4e17871-a18b-472e-8bd6-3ef70449d3bb/markdown_0/imgs/img_in_image_box_265_133_950_1383.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A44Z%2F-1%2F%2Fecfb46d90f94b450211dff710a9ea9549c484063e24f63b7d77db538de9f6aaf" alt="Image" width="57%" /></div>


<div style="text-align: center;"><div style="text-align: center;">[1] Q 轴 [2] P 轴</div> </div>


<div style="text-align: center;"><div style="text-align: center;">图 5-7 科技核心坐标示意图</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//b4e17871-a18b-472e-8bd6-3ef70449d3bb/markdown_1/imgs/img_in_image_box_375_156_804_619.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A45Z%2F-1%2F%2Fcc3aa8c13f0e2ec7d15c97642fbd44a61942a9c2cd56ed9d5115f3247e2ad057" alt="Image" width="36%" /></div>


<div style="text-align: center;"><div style="text-align: center;">图 5-8 科技核心 MARK 灯尺寸示意图</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//b4e17871-a18b-472e-8bd6-3ef70449d3bb/markdown_1/imgs/img_in_image_box_368_715_798_1259.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A45Z%2F-1%2F%2F68a265b865e1aaab9ca5bf9dedf42bd66f26d567598dd091495f905ae440ecfc" alt="Image" width="36%" /></div>


<div style="text-align: center;"><div style="text-align: center;">图 5-9 科技核心尺寸示意图</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//b4e17871-a18b-472e-8bd6-3ef70449d3bb/markdown_2/imgs/img_in_image_box_421_155_766_492.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A45Z%2F-1%2F%2F05889784c6ecabc2b557f542fe54a9a1726184c78e5e8b83c65fe2fb7662c2cd" alt="Image" width="28%" /></div>


<div style="text-align: center;"><div style="text-align: center;">图 5-10 球坐标系示意图</div> </div>


科技核心的初始位置的位姿为 x=-200, y=200, z=800,  $ \theta=0 $,  $ \phi=90 $, a=0。上文所涉及的长度单位均为 mm, 角度单位均为°。

科技核心位姿范围满足以下条件：

科技核心任意结构不会超出底座正面所在平面；

科技核心位姿与难度等级相关，具体关系如下：

<div style="text-align: center;"><div style="text-align: center;">表 5-10 科技核心位姿与难度等级关系</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>难度</td><td style='text-align: center; word-wrap: break-word;'>x</td><td style='text-align: center; word-wrap: break-word;'>y</td><td style='text-align: center; word-wrap: break-word;'>z</td><td style='text-align: center; word-wrap: break-word;'>$ \theta $</td><td style='text-align: center; word-wrap: break-word;'>$ \phi $</td><td style='text-align: center; word-wrap: break-word;'>$ \alpha $</td><td style='text-align: center; word-wrap: break-word;'>平移要求</td><td style='text-align: center; word-wrap: break-word;'>旋转要求</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>一级</td><td style='text-align: center; word-wrap: break-word;'>[-100,0]</td><td style='text-align: center; word-wrap: break-word;'>[100,300]</td><td style='text-align: center; word-wrap: break-word;'>[500,700]</td><td style='text-align: center; word-wrap: break-word;'>0</td><td style='text-align: center; word-wrap: break-word;'>90</td><td style='text-align: center; word-wrap: break-word;'>0</td><td style='text-align: center; word-wrap: break-word;'>无平移要求</td><td rowspan="2">无旋转要求</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>二级</td><td style='text-align: center; word-wrap: break-word;'>[-100,0]</td><td style='text-align: center; word-wrap: break-word;'>[100,300]</td><td style='text-align: center; word-wrap: break-word;'>[500,700]</td><td style='text-align: center; word-wrap: break-word;'>[-90,90]</td><td style='text-align: center; word-wrap: break-word;'>[0,90]</td><td style='text-align: center; word-wrap: break-word;'>[-45,45]</td><td style='text-align: center; word-wrap: break-word;'>放入后平移100mm</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>三级</td><td style='text-align: center; word-wrap: break-word;'>[-100,0]</td><td style='text-align: center; word-wrap: break-word;'>[100,300]</td><td style='text-align: center; word-wrap: break-word;'>[500,700]</td><td style='text-align: center; word-wrap: break-word;'>[-90,90]</td><td style='text-align: center; word-wrap: break-word;'>[0,90]</td><td style='text-align: center; word-wrap: break-word;'>[-45,45]</td><td style='text-align: center; word-wrap: break-word;'>放入后平移100mm</td><td rowspan="2">完成平移后，以Q轴为旋转轴，详见“图5-7 科技核心坐标示意图”，在绕Q轴顺逆时针各至多90°旋转范围内以5°的精准度将其旋转至指定角度</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>四级</td><td style='text-align: center; word-wrap: break-word;'>[-100,0]</td><td style='text-align: center; word-wrap: break-word;'>[100,300]</td><td style='text-align: center; word-wrap: break-word;'>[500,700]</td><td style='text-align: center; word-wrap: break-word;'>[-90,90]</td><td style='text-align: center; word-wrap: break-word;'>[0,90]</td><td style='text-align: center; word-wrap: break-word;'>[-45,45]</td><td style='text-align: center; word-wrap: break-word;'>放入后平移100mm</td></tr></table>

每周比赛中，红蓝双方科技核心在同一难度等级下，位姿变化情况相同。三级难度和四级难度的位姿取值范围与平移、旋转要求相同，但四级难度状态下，另一方的科技核心将临时移动到该方位置，此时，另一方科技核心坐标 x'y'z'与该方科技核心 xyz 的位置关系为：x'=x，y - y'≤400，z'=z，旋转要求随机，装配方需完成双方科技核心的装配。选择四级难度后，工程机器人需要在科技核心到位后 45 秒内完成装配。一次失败的四级难度装配将会使该方在后续 90 秒内无法进行四级难度的尝试。

##### 四级难度装配优先级

若一方没有正在尝试装配，另一方选择四级难度，则科技核心立即移动至指定位置。

若一方正在尝试装配非四级难度，另一方选择四级难度，则正装配的一方有15秒缓冲时间以确认或退出装配，此后科技核心立即移动至指定位置。在这种情况下，尝试四级难度的一方若装配失败，本局内将无法再次尝试四级难度，且每10秒获得的金币减少25。

若在缓冲时间内工程机器人未离开科技核心，可能会造成机构干涉或损坏。

若一方正在尝试装配四级难度，另一方不能选择四级难度。

工程机器人可以自主选择难度等级，但必须完成上一个难度等级的装配，才能选择下一个难度等级，可选的难度等级将受一定条件限制，具体如表所示：



<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>比赛时间</td><td style='text-align: center; word-wrap: break-word;'>可选择的难度等级</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>比赛开始时</td><td style='text-align: center; word-wrap: break-word;'>双方仅可选择一级难度</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>比赛开始 1 分钟后</td><td style='text-align: center; word-wrap: break-word;'>双方可选择一、二级难度</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>比赛开始 2 分钟后</td><td style='text-align: center; word-wrap: break-word;'>双方可选择一、二、三级难度</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>比赛开始 3 分钟后</td><td style='text-align: center; word-wrap: break-word;'>双方可选择一、二、三、四级难度</td></tr></table>

装配成功后，根据当次装配是否为首次完成，队伍将会获得不同的收益，具体如下表所示：



<table border="1" style="margin: auto; word-wrap: break-word;"><tr><td style="text-align: center; word-wrap: break-word;">完成难度</td><td style="text-align: center; word-wrap: break-word;">首次完成收益</td><td style="text-align: center; word-wrap: break-word;">非首次完成收益</td></tr><tr><td style="text-align: center; word-wrap: break-word;">一级</td><td style="text-align: center; word-wrap: break-word;">此后，该方每 10 秒获得 50 金币。</td><td style="text-align: center; word-wrap: break-word;">此后，该方每 10 秒额外获得 5 金币</td></tr><tr><td style="text-align: center; word-wrap: break-word;">二级</td><td style="text-align: center; word-wrap: break-word;">● 解锁机器人等级上限：完成该难度的装配任务前，该方机器人等级上限为 5 级，完成后，等级上限提高为 7 级。</td><td style="text-align: center; word-wrap: break-word;">此后，该方每 10 秒额外获得 10 金币</td></tr><tr><td style="text-align: center; word-wrap: break-word;"></td><td style="text-align: center; word-wrap: break-word;">● 此后，该方每 10 秒额外获得 25 金币。</td><td style="text-align: center; word-wrap: break-word;"></td></tr><tr><td style="text-align: center; word-wrap: break-word;">三级</td><td style="text-align: center; word-wrap: break-word;">● 该方地面机器人、前哨站、基地获得 25%防御增益，持续到比赛结束，且机器人战亡后该增益保留。\n● 该方机器人等级上限提高为 10 级。\n● 此后，该方每 10 秒额外获得 25 金币。</td><td style="text-align: center; word-wrap: break-word;">此后，该方每 10 秒额外获得 15 金币</td></tr><tr><td style="text-align: center; word-wrap: break-word;">四级</td><td style="text-align: center; word-wrap: break-word;">● 该方地面机器人、前哨站、基地获得 50%防御增益，持续到比赛结束，且机器人战亡后该增益保留。\n● 基地血量增加 2000，溢出的血量转化为等值的虚拟护盾，后续基地受到伤害时，优先扣除虚拟护盾血量，再扣除基地本身血量。\n● 此后，该方每 10 秒额外获得 50 金币。</td><td style="text-align: center; word-wrap: break-word;">仅限完成一次</td></tr></table>




<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//9ecced69-acbb-4231-87dc-a30f55bac402/markdown_0/imgs/img_in_image_box_135_828_178_870.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A46Z%2F-1%2F%2Fb7bf70101a11a9da685ea36f505b7389592d7a98fc0c937e8da9326f8d1da318" alt="Image" width="3%" /></div>


示例：一方在一局比赛中成功五次装配任务，难度等级依次为一级、二级、三级、二级、一级，则其每10秒获得的金币数量为 $ 50+25+25+10+5=115 $。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//9ecced69-acbb-4231-87dc-a30f55bac402/markdown_0/imgs/img_in_image_box_416_1008_756_1358.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A47Z%2F-1%2F%2F3a3343cceb16db25a9d100bfdfc2c98811632deec055f1d2c8f868df0353fbf5" alt="Image" width="28%" /></div>


<div style="text-align: center;"><div style="text-align: center;">[1] 第一组灯 [2] 第二组灯 [3] 第三组灯</div> </div>


<div style="text-align: center;"><div style="text-align: center;">图 5-11 科技核心灯效示意图</div> </div>


<div style="text-align: center;"><div style="text-align: center;">表 5-11 科技核心灯效汇总</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>状态</td><td style='text-align: center; word-wrap: break-word;'>灯效</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>比赛进行中，未进入装配流程</td><td style='text-align: center; word-wrap: break-word;'>● 第一组灯全灭\n● 第二、三组灯常亮，显示队伍对应的颜色（红色或蓝色）</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>比赛进行中，已选择装配难度，机械臂未运动到位</td><td style='text-align: center; word-wrap: break-word;'>● 第一组灯呈现流水灯效\n● 第二、三组灯常亮，显示队伍对应的颜色（红色或蓝色）</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>比赛进行中，已选择装配难度，机械臂已运动到位</td><td style='text-align: center; word-wrap: break-word;'>● 第一组灯以 1Hz 频率白色闪烁\n● 第二、三组灯以 1Hz 频率闪烁，显示队伍对应的颜色（红色或蓝色）</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>步骤 2 完成</td><td style='text-align: center; word-wrap: break-word;'>● 第一组灯以 1Hz 频率白色闪烁\n● 第二组灯以 1Hz 频率闪烁，显示队伍对应的颜色（红色或蓝色）\n● 第三组灯以 3Hz 频率闪烁，显示队伍对应的颜色（红色或蓝色）</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>步骤 3 完成</td><td style='text-align: center; word-wrap: break-word;'>● 第一组灯以 1Hz 频率白色闪烁\n● 第二、三组灯以 3Hz 频率闪烁，显示队伍对应的颜色（红色或蓝色）</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>步骤 4 完成</td><td style='text-align: center; word-wrap: break-word;'>● 第一组灯以 1Hz 频率白色闪烁\n● 第二、三组灯常亮，显示队伍对应的颜色（红色或蓝色）</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>步骤 5 进行中</td><td style='text-align: center; word-wrap: break-word;'>● 第一组灯灯效如下：\n➢ 指定角度位置亮起队伍对应的颜色（红色或蓝色），不闪烁\n➢ 其他角度位置匹配能量单元当前旋转角度亮起白色灯，不闪烁\n● 第二、三组灯常亮，显示队伍对应的颜色（红色或蓝色）</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>步骤 5 完成</td><td style='text-align: center; word-wrap: break-word;'>● 第一组灯中，指定角度位置亮起绿色灯，不闪烁\n● 第二、三组灯常亮，显示队伍对应的颜色（红色或蓝色）</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>已确认装配，回收能量单元中</td><td style='text-align: center; word-wrap: break-word;'>● 第一组灯以 3Hz 频率白色闪烁\n● 第二、三组灯以 3Hz 频率闪烁，显示队伍对应的颜色（红色或蓝色）</td></tr></table>

要完整实现能量单元装配，必须完成以下步骤：

1. 工程机器人占领装配区增益点后，操作手在裁判系统选手端选择装配难度。

2. 科技核心运动到相应位姿（可装配状态）后，出现相应灯效提示，工程机器人将能量单元下方的开口对准能量单元装配柱，沿 x 负向插入 100mm，到达底部后出现对应灯效提示，则步骤 2 完成，如下图所示。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//9ecced69-acbb-4231-87dc-a30f55bac402/markdown_2/imgs/img_in_image_box_169_348_212_393.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A49Z%2F-1%2F%2F62719e26d4c686326f2025aa81c594e5b01f1d3e43f0a350de9bf4e8aa2fd343" alt="Image" width="3%" /></div>


当且仅当科技核心运动到相应位姿后，才能插入能量单元，提早插入能量单元无法正常进行后续装配流程。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//9ecced69-acbb-4231-87dc-a30f55bac402/markdown_2/imgs/img_in_image_box_466_501_752_926.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A49Z%2F-1%2F%2Ff6051e28cc6c4b2e6c710200609ba749b19fe4c1cb8496417a892aba9b02ec76" alt="Image" width="24%" /></div>


<div style="text-align: center;"><div style="text-align: center;">[1] 3Hz 闪烁</div> </div>


<div style="text-align: center;"><div style="text-align: center;">图 5-12 步骤2 示意图</div> </div>


3. 工程机器人将已固定在能量单元装配柱的能量单元沿 z 轴正向移动 100mm，到达 100mm 处出现对应灯效提示，则步骤 3 完成，如下图所示。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//9ecced69-acbb-4231-87dc-a30f55bac402/markdown_2/imgs/img_in_image_box_163_1197_206_1242.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A50Z%2F-1%2F%2F945864a397d6667c5d75c46a9a366815210c9c31cf5fdf09eaeb4a31ff307175" alt="Image" width="3%" /></div>


能量单元实际不透明，此处仅示意灯效。

该步骤中，除克服能量单元重力所必需的力外，移动阻力至多10N。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//9ecced69-acbb-4231-87dc-a30f55bac402/markdown_3/imgs/img_in_image_box_429_165_803_581.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A51Z%2F-1%2F%2Fed72fcfadc451f3a46d6f1513ee13f1f16b41af52c15ea949fac0da31a8ac9a6" alt="Image" width="31%" /></div>


<div style="text-align: center;"><div style="text-align: center;">[1] 3Hz 闪烁</div> </div>


<div style="text-align: center;"><div style="text-align: center;">图 5-13 步骤3 示意图</div> </div>


4. 工程机器人以 P 轴为旋转轴，将能量单元向上旋转  $ 90^{\circ} $，到达  $ 90^{\circ} $ 处出现对应灯效提示，则步骤 4 完成，如下图所示。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//9ecced69-acbb-4231-87dc-a30f55bac402/markdown_3/imgs/img_in_image_box_467_854_740_1235.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A51Z%2F-1%2F%2Fa78942c537db0737b27e763d54fa06bf09483572ed18bbc82bf33fe1fc91feb8" alt="Image" width="22%" /></div>


<div style="text-align: center;"><div style="text-align: center;">图 5-14 步骤4示意图</div> </div>


5. 工程机器人以 Q 轴为旋转轴，将能量单元旋转至指定角度，直到出现对应灯效提示（在正确位置停留至多 0.2s 后出现），则步骤 5 完成，如下图所示。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//da511ae4-2d11-4ad5-83f1-cf963876fb2e/markdown_0/imgs/img_in_image_box_253_179_966_582.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A04%3A19Z%2F-1%2F%2F8d352ac018a512b36ca99bcf2c998dc809c8eb66dc1ec07903b72f63577bea3f" alt="Image" width="59%" /></div>


<div style="text-align: center;"><div style="text-align: center;">图 5-15 步骤 5 示意图</div> </div>


如操作手按下“确认装配”按键后，科技核心未检测到能量单元按照要求正确装配，则在此后的1秒内，将不会再接收“确认装配”的指令输入。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//da511ae4-2d11-4ad5-83f1-cf963876fb2e/markdown_0/imgs/img_in_image_box_142_775_188_821.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A04%3A23Z%2F-1%2F%2F13e5e9884b1e70660fc83a93704d7bd1351bbe5b88363d4ea2a5f26d9afd6a92" alt="Image" width="3%" /></div>


该步骤中，除克服能量单元重力所必需的力外，旋转阻力矩约为  $ 0.3 \sim 0.6 \, N \cdot m $。

出于安全考虑，该步骤中，在正确位置持续停留超过2s后，旋转机构会锁定，此时工程机器人机构可以脱离能量单元，能量单元仍将保持在原位。

该步骤中，能量单元装配柱将存在一自然回到  $ 0^{\circ} $ 的力矩，最大值为  $ 0.6\,\text{N}\cdot\text{m} $。

6. 操作手下对应按键确认装配完成，若科技核心检测到能量单元被完全放入，并正确按照相应平移和旋转要求装配，则会进行能量单元回收，并给予该方对应收益。

对于一级难度，完成步骤1、2、6，视为装配成功；

对于二级难度，完成步骤1、2、3、6，视为装配成功；

对于三级难度，完成步骤1、2、3、4、5、6，视为装配成功。

对于四级难度，要实现能量单元装配，工程机器人不仅需完成步骤1、2、3、4、5、6，还需在除步骤1、步骤4外的每个装配步骤完成后的5秒内，在另一个科技核心处也完成该步骤。在两个科技核心均完成步骤6后，若科技核心检测到两个能量单元均被完全放入，并正确按照相应平移和旋转要求完成装配，且满足时间要求，则会进行能量单元回收，并给予该方对应收益，否则视为装配失败。

此外，操作手在装配过程中，需注意以下事项：

操作手在选择装配难度后，若科技核心内已有能量单元，则不得更改装配难度，且在能量单元装配成

功前，相同装配难度下的科技核心位姿将保持一致。

工程机器人操作手在确认进行能量单元装配后，不得对能量单元进行任何进一步操作或干预，否则可能导致装配失败。

装配过程中，工程机器人可以将能量单元取出，该过程除克服重力外，还需额外沿能量单元旋转对称轴方向向外施加至多10N力即可取出。在科技核心传感器检测到能量单元被取出时，装配过程将立即失败。

装配过程中，若工程机器人连续15秒未检测到装配区交互模块卡，则判定当次装配失败并自动退出；随后，科技核心将立即执行能量单元回收操作。

科技核心在运行过程中不具备障碍物检测与主动避障功能。若在运动路径中受到阻挡，系统将触发过载警报并短暂悬停，随后尝试恢复运动。若工程机器人因与科技核心发生接触或碰撞导致机构损坏，其产生的所有损失由参赛队伍自行承担。

若工程机器人抓取能量单元后战亡，当次装配立即视为失败。待操作手手动取消装配后，科技核心将执行能量单元回收操作。

若一方工程机器人在装配时战亡，且另一方此时选择了四级难度，则战亡机器人将被临时激活，操作手可控制该战亡机器人脱离科技核心。

工程机器人装配时需操作能量单元而不是科技核心的可动结构及其他本体结构。

面向科技核心，在装配过程中，能量单元可绕Q轴沿顺时针或逆时针旋转90°。

### 5.4 经验及性能体系

#### 5.4.1 经验体系

比赛开始时，英雄、步兵、空中机器人的机器人等级均为1级，可通过增加经验值实现等级提升，其余机器人均不适用经验体系。

比赛过程中，机器人可以通过多种方式增加经验值，具体如下表所示：



<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>行为类型</td><td style='text-align: center; word-wrap: break-word;'>获得经验</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>发射弹丸</td><td style='text-align: center; word-wrap: break-word;'>● 步兵、空中机器人：每发射 1 发弹丸，获得 1 点经验。\n● 英雄机器人：每发射 1 发弹丸，获得 10 点经验。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>造成攻击伤害</td><td style='text-align: center; word-wrap: break-word;'>● 对机器人造成攻击伤害：每造成 1 点伤害，攻击方获得 4 点经验。\n● 对前哨站装甲模块造成攻击伤害：每造成 1 点伤害，攻击方获得 2 点经验。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>● 对基地装甲模块造成攻击伤害：每造成2点伤害，攻击方获得1点经验，伤害为奇数时，向上取整。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>当一方机器人、基地或前哨站受到攻击伤害，但裁判系统未检测到伤害具体来源，伤害来源不能获取经验或伤害来源为判罚/己方机器人：若为弹丸伤害，经验将平均分给另一方的能够正常造成该类型弹丸伤害且能够获得经验的所有存活机器人；若为非弹丸伤害，经验将平均分给另一方此时所有存活的英雄、步兵、空中机器人。平均值进行四舍五入，精确到小数点后一位。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>示例：蓝方某步兵机器人受到了120点17mm弹丸伤害，但系统未检测到伤害来源。此时红方有2台存活的步兵机器人，1台正在进行空中支援的空中机器人和1台存活的英雄机器人，则每台步兵和空中机器人所获得的经验为 $ \frac{4*120}{3}=160 $，英雄机器人不获得经验。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>以下计算中，工程、哨兵机器人均视为1级。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>● 若存在击毁者且击毁者可以获取经验：</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>➢ 当被击毁者等级大于等于击毁者等级时，经验计算方式如下：击毁者所获得的经验= $ 50 \times $被击毁者等级 $ (1+0.2 \times $被击毁者与击毁者等级差 $ \downarrow) $。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>➢ 当被击毁者等级小于击毁者等级时，被击毁者与击毁者等级差视为0，经验计算方式如下：击毁者所获得的经验= $ 50 \times $被击毁者等级</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>机器人战亡</td><td style='text-align: center; word-wrap: break-word;'>● 若裁判系统未检测到击毁者或者击毁者不能获得经验：</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>➢ 若为弹丸伤害，击毁者等级视为另一方能够正常造成该类型弹丸伤害的所有存活机器人的平均经验所对应的等级，且经验将平均分给上述机器人。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>➢ 若为非弹丸伤害，经验将平均分给另一方此时所有存活的英雄、步兵、空中机器人。平均值进行四舍五入，精确到小数点后一位。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>机器人因装甲模块被攻击外的其他原因导致变为战亡、异常离线或裁判系统无法检测到击毁者时，均视为找不到击毁者。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>示例一：一台2级步兵机器人击毁了对方一台6级步兵机器人，则击毁者获得的经验为 $ 50 \times 6 \times (1 + (6-2) \times 0.2) = 540 $。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>示例二：红方一台9级步兵机器人战亡，未检测到击毁者，此时蓝方有2台总经验分别为1250、4000的步兵机器人与1台总经验为3000的空中机器人存活，平均经验为2750，对应机器人等级为6级，则蓝方的2台步兵机器人和1台空中机器人，每台获得的经验为 $ \frac{50*9* (1 + (9-6) *0.2)}{3} $=240。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>激活小能量机关</td><td style='text-align: center; word-wrap: break-word;'>详见“5.5.2能量机关机制”。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>激活大能量机关</td><td style='text-align: center; word-wrap: break-word;'>详见“5.5.2能量机关机制”。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>通过部署模式造成伤害</td><td style='text-align: center; word-wrap: break-word;'>每通过部署模式造成一次伤害，获得100点经验，详见：“5.6.1英雄机器人特殊机制”。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>获得地形跨越增益</td><td style='text-align: center; word-wrap: break-word;'>机器人首次获得地形跨越增益（公路）、地形跨越增益（高地）、地形跨越增益（飞坡）、地形跨越增益（隧道）时，均可获得300点经验。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>飞镖命中前哨站/基地</td><td style='text-align: center; word-wrap: break-word;'>详见“5.5.1基地及前哨站机制”。</td></tr></table>








<div style="text-align: center;"><div style="text-align: center;">表 5-12 英雄、步兵、空中机器人的等级和经验</div> </div>




<table border="1" style="margin: auto; word-wrap: break-word;"><tr><td style="text-align: center; word-wrap: break-word;">等级</td><td style="text-align: center; word-wrap: break-word;">升级所需总经验</td></tr><tr><td style="text-align: center; word-wrap: break-word;">1</td><td style="text-align: center; word-wrap: break-word;">0</td></tr><tr><td style="text-align: center; word-wrap: break-word;">2</td><td style="text-align: center; word-wrap: break-word;">550</td></tr><tr><td style="text-align: center; word-wrap: break-word;">3</td><td style="text-align: center; word-wrap: break-word;">1100</td></tr><tr><td style="text-align: center; word-wrap: break-word;">4</td><td style="text-align: center; word-wrap: break-word;">1650</td></tr><tr><td style="text-align: center; word-wrap: break-word;">5</td><td style="text-align: center; word-wrap: break-word;">2200</td></tr><tr><td style="text-align: center; word-wrap: break-word;">6</td><td style="text-align: center; word-wrap: break-word;">2750</td></tr><tr><td style="text-align: center; word-wrap: break-word;">7</td><td style="text-align: center; word-wrap: break-word;">3300</td></tr><tr><td style="text-align: center; word-wrap: break-word;">8</td><td style="text-align: center; word-wrap: break-word;">3850</td></tr><tr><td style="text-align: center; word-wrap: break-word;">9</td><td style="text-align: center; word-wrap: break-word;">4400</td></tr><tr><td style="text-align: center; word-wrap: break-word;">10</td><td style="text-align: center; word-wrap: break-word;">5000</td></tr></table>




#### 5.4.2 性能体系

三分钟准备阶段开始后，英雄机器人的操作手可以选择整机类型，步兵机器人的操作手可选择机器人的底盘和发射机构类型，空中机器人不可选择发射机构类型，其他机器人均不适用性能体系。

七分钟比赛阶段开始后且机器人底盘和发射机构类型选择完毕后，整局比赛期间不可更换。若不选择整机、底盘或发射机构类型，则在七分钟比赛阶段开始后，整机类型默认为“远程优先”，底盘类型默认为“血量优先”，发射机构类型默认为“冷却优先”。机器人升级后，血量上限提升的部分将被立即添加至机器人的当前血量。

<div style="text-align: center;"><div style="text-align: center;">表 5-13 英雄机器人整机属性</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>发射机构类型</td><td style='text-align: center; word-wrap: break-word;'>等级</td><td style='text-align: center; word-wrap: break-word;'>上限血量</td><td style='text-align: center; word-wrap: break-word;'>底盘功率上限 (W)</td><td style='text-align: center; word-wrap: break-word;'>射击热量上限</td><td style='text-align: center; word-wrap: break-word;'>射击热量冷却速率（每秒）</td></tr><tr><td rowspan="10">近战优先</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>260</td><td style='text-align: center; word-wrap: break-word;'>70</td><td style='text-align: center; word-wrap: break-word;'>200</td><td style='text-align: center; word-wrap: break-word;'>12</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>300</td><td style='text-align: center; word-wrap: break-word;'>75</td><td style='text-align: center; word-wrap: break-word;'>210</td><td style='text-align: center; word-wrap: break-word;'>14</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>3</td><td style='text-align: center; word-wrap: break-word;'>330</td><td style='text-align: center; word-wrap: break-word;'>80</td><td style='text-align: center; word-wrap: break-word;'>220</td><td style='text-align: center; word-wrap: break-word;'>16</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>360</td><td style='text-align: center; word-wrap: break-word;'>85</td><td style='text-align: center; word-wrap: break-word;'>230</td><td style='text-align: center; word-wrap: break-word;'>18</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>5</td><td style='text-align: center; word-wrap: break-word;'>400</td><td style='text-align: center; word-wrap: break-word;'>90</td><td style='text-align: center; word-wrap: break-word;'>240</td><td style='text-align: center; word-wrap: break-word;'>20</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>6</td><td style='text-align: center; word-wrap: break-word;'>430</td><td style='text-align: center; word-wrap: break-word;'>95</td><td style='text-align: center; word-wrap: break-word;'>250</td><td style='text-align: center; word-wrap: break-word;'>22</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>7</td><td style='text-align: center; word-wrap: break-word;'>460</td><td style='text-align: center; word-wrap: break-word;'>100</td><td style='text-align: center; word-wrap: break-word;'>260</td><td style='text-align: center; word-wrap: break-word;'>24</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>8</td><td style='text-align: center; word-wrap: break-word;'>500</td><td style='text-align: center; word-wrap: break-word;'>105</td><td style='text-align: center; word-wrap: break-word;'>270</td><td style='text-align: center; word-wrap: break-word;'>26</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>9</td><td style='text-align: center; word-wrap: break-word;'>530</td><td style='text-align: center; word-wrap: break-word;'>110</td><td style='text-align: center; word-wrap: break-word;'>280</td><td style='text-align: center; word-wrap: break-word;'>28</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>10</td><td style='text-align: center; word-wrap: break-word;'>600</td><td style='text-align: center; word-wrap: break-word;'>120</td><td style='text-align: center; word-wrap: break-word;'>300</td><td style='text-align: center; word-wrap: break-word;'>30</td></tr><tr><td rowspan="2">远程优先</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>200</td><td style='text-align: center; word-wrap: break-word;'>50</td><td style='text-align: center; word-wrap: break-word;'>160</td><td style='text-align: center; word-wrap: break-word;'>20</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>220</td><td style='text-align: center; word-wrap: break-word;'>55</td><td style='text-align: center; word-wrap: break-word;'>162</td><td style='text-align: center; word-wrap: break-word;'>23</td></tr><tr><td rowspan="8"></td><td style='text-align: center; word-wrap: break-word;'>3</td><td style='text-align: center; word-wrap: break-word;'>240</td><td style='text-align: center; word-wrap: break-word;'>60</td><td style='text-align: center; word-wrap: break-word;'>164</td><td style='text-align: center; word-wrap: break-word;'>26</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>260</td><td style='text-align: center; word-wrap: break-word;'>65</td><td style='text-align: center; word-wrap: break-word;'>166</td><td style='text-align: center; word-wrap: break-word;'>29</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>5</td><td style='text-align: center; word-wrap: break-word;'>280</td><td style='text-align: center; word-wrap: break-word;'>70</td><td style='text-align: center; word-wrap: break-word;'>168</td><td style='text-align: center; word-wrap: break-word;'>32</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>6</td><td style='text-align: center; word-wrap: break-word;'>300</td><td style='text-align: center; word-wrap: break-word;'>75</td><td style='text-align: center; word-wrap: break-word;'>170</td><td style='text-align: center; word-wrap: break-word;'>35</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>7</td><td style='text-align: center; word-wrap: break-word;'>320</td><td style='text-align: center; word-wrap: break-word;'>80</td><td style='text-align: center; word-wrap: break-word;'>175</td><td style='text-align: center; word-wrap: break-word;'>38</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>8</td><td style='text-align: center; word-wrap: break-word;'>340</td><td style='text-align: center; word-wrap: break-word;'>85</td><td style='text-align: center; word-wrap: break-word;'>180</td><td style='text-align: center; word-wrap: break-word;'>41</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>9</td><td style='text-align: center; word-wrap: break-word;'>360</td><td style='text-align: center; word-wrap: break-word;'>90</td><td style='text-align: center; word-wrap: break-word;'>185</td><td style='text-align: center; word-wrap: break-word;'>44</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>10</td><td style='text-align: center; word-wrap: break-word;'>400</td><td style='text-align: center; word-wrap: break-word;'>100</td><td style='text-align: center; word-wrap: break-word;'>190</td><td style='text-align: center; word-wrap: break-word;'>50</td></tr></table>





<div style="text-align: center;"><div style="text-align: center;">表 5-14 步兵机器人底盘属性</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>底盘类型</td><td style='text-align: center; word-wrap: break-word;'>等级</td><td style='text-align: center; word-wrap: break-word;'>上限血量</td><td style='text-align: center; word-wrap: break-word;'>底盘功率上限（W）</td></tr><tr><td rowspan="10">功率优先</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>150</td><td style='text-align: center; word-wrap: break-word;'>60</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>175</td><td style='text-align: center; word-wrap: break-word;'>65</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>3</td><td style='text-align: center; word-wrap: break-word;'>200</td><td style='text-align: center; word-wrap: break-word;'>70</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>225</td><td style='text-align: center; word-wrap: break-word;'>75</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>5</td><td style='text-align: center; word-wrap: break-word;'>250</td><td style='text-align: center; word-wrap: break-word;'>80</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>6</td><td style='text-align: center; word-wrap: break-word;'>275</td><td style='text-align: center; word-wrap: break-word;'>85</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>7</td><td style='text-align: center; word-wrap: break-word;'>300</td><td style='text-align: center; word-wrap: break-word;'>90</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>8</td><td style='text-align: center; word-wrap: break-word;'>325</td><td style='text-align: center; word-wrap: break-word;'>95</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>9</td><td style='text-align: center; word-wrap: break-word;'>350</td><td style='text-align: center; word-wrap: break-word;'>100</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>10</td><td style='text-align: center; word-wrap: break-word;'>400</td><td style='text-align: center; word-wrap: break-word;'>100</td></tr><tr><td rowspan="10">血量优先</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>200</td><td style='text-align: center; word-wrap: break-word;'>45</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>225</td><td style='text-align: center; word-wrap: break-word;'>50</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>3</td><td style='text-align: center; word-wrap: break-word;'>250</td><td style='text-align: center; word-wrap: break-word;'>55</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>275</td><td style='text-align: center; word-wrap: break-word;'>60</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>5</td><td style='text-align: center; word-wrap: break-word;'>300</td><td style='text-align: center; word-wrap: break-word;'>65</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>6</td><td style='text-align: center; word-wrap: break-word;'>325</td><td style='text-align: center; word-wrap: break-word;'>70</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>7</td><td style='text-align: center; word-wrap: break-word;'>350</td><td style='text-align: center; word-wrap: break-word;'>75</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>8</td><td style='text-align: center; word-wrap: break-word;'>375</td><td style='text-align: center; word-wrap: break-word;'>80</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>9</td><td style='text-align: center; word-wrap: break-word;'>400</td><td style='text-align: center; word-wrap: break-word;'>90</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>10</td><td style='text-align: center; word-wrap: break-word;'>400</td><td style='text-align: center; word-wrap: break-word;'>100</td></tr></table>





<div style="text-align: center;"><div style="text-align: center;">表 5-15 步兵机器人 17mm 发射机构属性</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>发射机构类型</td><td style='text-align: center; word-wrap: break-word;'>等级</td><td style='text-align: center; word-wrap: break-word;'>射击热量上限</td><td style='text-align: center; word-wrap: break-word;'>射击热量冷却速率（每秒）</td></tr><tr><td rowspan="8">爆发优先</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>170</td><td style='text-align: center; word-wrap: break-word;'>5</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>180</td><td style='text-align: center; word-wrap: break-word;'>7</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>3</td><td style='text-align: center; word-wrap: break-word;'>190</td><td style='text-align: center; word-wrap: break-word;'>9</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>200</td><td style='text-align: center; word-wrap: break-word;'>11</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>5</td><td style='text-align: center; word-wrap: break-word;'>210</td><td style='text-align: center; word-wrap: break-word;'>12</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>6</td><td style='text-align: center; word-wrap: break-word;'>220</td><td style='text-align: center; word-wrap: break-word;'>13</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>7</td><td style='text-align: center; word-wrap: break-word;'>230</td><td style='text-align: center; word-wrap: break-word;'>14</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>8</td><td style='text-align: center; word-wrap: break-word;'>240</td><td style='text-align: center; word-wrap: break-word;'>16</td></tr><tr><td rowspan="2"></td><td style='text-align: center; word-wrap: break-word;'>9</td><td style='text-align: center; word-wrap: break-word;'>250</td><td style='text-align: center; word-wrap: break-word;'>18</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>10</td><td style='text-align: center; word-wrap: break-word;'>260</td><td style='text-align: center; word-wrap: break-word;'>20</td></tr><tr><td rowspan="10">冷却优先</td><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>40</td><td style='text-align: center; word-wrap: break-word;'>12</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>48</td><td style='text-align: center; word-wrap: break-word;'>14</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>3</td><td style='text-align: center; word-wrap: break-word;'>56</td><td style='text-align: center; word-wrap: break-word;'>16</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>64</td><td style='text-align: center; word-wrap: break-word;'>18</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>5</td><td style='text-align: center; word-wrap: break-word;'>72</td><td style='text-align: center; word-wrap: break-word;'>20</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>6</td><td style='text-align: center; word-wrap: break-word;'>80</td><td style='text-align: center; word-wrap: break-word;'>22</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>7</td><td style='text-align: center; word-wrap: break-word;'>88</td><td style='text-align: center; word-wrap: break-word;'>24</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>8</td><td style='text-align: center; word-wrap: break-word;'>96</td><td style='text-align: center; word-wrap: break-word;'>26</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>9</td><td style='text-align: center; word-wrap: break-word;'>114</td><td style='text-align: center; word-wrap: break-word;'>28</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>10</td><td style='text-align: center; word-wrap: break-word;'>120</td><td style='text-align: center; word-wrap: break-word;'>30</td></tr></table>





<div style="text-align: center;"><div style="text-align: center;">表 5-16 空中机器人 17mm 发射机构属性</div> </div>




<table border="1" style="margin: auto; word-wrap: break-word;"><tr><td style="text-align: center; word-wrap: break-word;">等级</td><td style="text-align: center; word-wrap: break-word;">射击热量上限</td><td style="text-align: center; word-wrap: break-word;">射击热量冷却速率（每秒）</td></tr><tr><td style="text-align: center; word-wrap: break-word;">1</td><td style="text-align: center; word-wrap: break-word;">100</td><td style="text-align: center; word-wrap: break-word;">20</td></tr><tr><td style="text-align: center; word-wrap: break-word;">2</td><td style="text-align: center; word-wrap: break-word;">110</td><td style="text-align: center; word-wrap: break-word;">30</td></tr><tr><td style="text-align: center; word-wrap: break-word;">3</td><td style="text-align: center; word-wrap: break-word;">120</td><td style="text-align: center; word-wrap: break-word;">40</td></tr><tr><td style="text-align: center; word-wrap: break-word;">4</td><td style="text-align: center; word-wrap: break-word;">130</td><td style="text-align: center; word-wrap: break-word;">50</td></tr><tr><td style="text-align: center; word-wrap: break-word;">5</td><td style="text-align: center; word-wrap: break-word;">140</td><td style="text-align: center; word-wrap: break-word;">60</td></tr><tr><td style="text-align: center; word-wrap: break-word;">6</td><td style="text-align: center; word-wrap: break-word;">150</td><td style="text-align: center; word-wrap: break-word;">70</td></tr><tr><td style="text-align: center; word-wrap: break-word;">7</td><td style="text-align: center; word-wrap: break-word;">160</td><td style="text-align: center; word-wrap: break-word;">80</td></tr><tr><td style="text-align: center; word-wrap: break-word;">8</td><td style="text-align: center; word-wrap: break-word;">170</td><td style="text-align: center; word-wrap: break-word;">90</td></tr><tr><td style="text-align: center; word-wrap: break-word;">9</td><td style="text-align: center; word-wrap: break-word;">180</td><td style="text-align: center; word-wrap: break-word;">100</td></tr><tr><td style="text-align: center; word-wrap: break-word;">10</td><td style="text-align: center; word-wrap: break-word;">200</td><td style="text-align: center; word-wrap: break-word;">120</td></tr></table>




### 5.5 场地相关机制

#### 5.5.1 基地及前哨站机制

基地血量为 5000，且开局拥有 150 的虚拟护盾，前哨站血量为 1500。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//43a3399e-b1d4-473e-a3b0-c57d79bcd48c/markdown_0/imgs/img_in_image_box_128_706_170_747.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A57Z%2F-1%2F%2Ff406839908fac2d51ab530b58724517fe993afc881a9a0689ab7ca5347c36aae" alt="Image" width="3%" /></div>


虚拟护盾的扣除不视为基地血量的损失，但计入对方造成的总伤害。

基地、前哨站的装甲模块（不含飞镖检测模块）中心设置了一处  $ 10mm \times 10mm $ 的矩形区域，如下图所示，若弹丸命中该区域，则此次攻击获得 150% 攻击增益。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//43a3399e-b1d4-473e-a3b0-c57d79bcd48c/markdown_0/imgs/img_in_image_box_337_883_856_1348.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A57Z%2F-1%2F%2F8a0944ec97cd73c5d257c57d5652122a8111f0e6ec4cb15a9fde209ea844e823" alt="Image" width="43%" /></div>


<div style="text-align: center;"><div style="text-align: center;">[1] 有效检测区域详细尺寸 [2] 暴击区域尺寸</div> </div>


<div style="text-align: center;"><div style="text-align: center;">图 5-16 矩形区域示意图</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//43a3399e-b1d4-473e-a3b0-c57d79bcd48c/markdown_1/imgs/img_in_image_box_301_215_893_1397.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A03%3A00Z%2F-1%2F%2F536567219d31332c4b7f677e5c46afb1f231658b27f7a62cbac89fcfff503c42" alt="Image" width="49%" /></div>


Å

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//43a3399e-b1d4-473e-a3b0-c57d79bcd48c/markdown_2/imgs/img_in_image_box_300_220_888_1400.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A03%3A03Z%2F-1%2F%2F0b4b2c7c594624434a0c107a658b098b96860bf2e338613dbfad78c7df0db989" alt="Image" width="49%" /></div>


<div style="text-align: center;"><div style="text-align: center;">图 5-17 基地、前哨站装甲模块示意图</div> </div>


当一方前哨站存活，基地处于无敌状态。

当一方前哨站被击毁后，另一方可以占领被击毁的前哨站对应的增益点。详见“5.5.3.6 前哨站增益点机制”。

一方每累计损失1000点基地血量，获得1次可积累的“重建前哨站”机会。英雄、步兵、哨兵机器人通过连续检测己方前哨站增益点场地交互模块卡10秒，或工程机器人连续检测己方前哨站增益点场地交互模块卡5秒（不同机器人占领时长独立计算），即可“重建”被击毁的前哨站，使前哨站恢复存活状态并具有750点血量。在比赛开始5分钟后，前哨站不能够再被重建。

前哨站的中部装甲可旋转，其初始位置请参照“图4-33能量机关中心标识尺寸图”。比赛开始后，中部装甲开始旋转，旋转5秒内达到 $ 0.8\pi rad/s $的速度，随后保持匀速转动，方向随机。每局比赛中，红蓝双方的前哨站旋转方向保持一致且固定不变。

当满足以下任意条件时，一方前哨站装甲停止旋转：

该方前哨站首次被击毁。

对方基地护甲展开。

比赛开始3分钟后。

停止旋转后的前哨站装甲在当局不会再次旋转。

双方前哨站同时停止旋转时，中部装甲达到初始位置的时间可能略有差异。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//43a3399e-b1d4-473e-a3b0-c57d79bcd48c/markdown_3/imgs/img_in_image_box_142_892_185_932.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A03%3A06Z%2F-1%2F%2Fb081ba780d66a235202b02d51ead6a01bb0a653370f015bbbce37ef0fffde0dc" alt="Image" width="3%" /></div>


在前哨站存活的情况下，前哨站的飞镖引导灯常亮，基地的飞镖引导灯熄灭；前哨站被击毁时，前哨站的飞镖引导灯熄灭，基地的飞镖引导灯点亮。

#### 5.5.2 能量机关机制

机器人可通过弹丸击打的方式激活能量机关。双方可同时击打能量机关。红方的能量机关被激活后仅为红方提供增益，蓝方同理。

能量机关在比赛中持续旋转，但旋转策略根据状态变化：

红蓝双方能量机关共轴旋转，即红方能量机关顺时针旋转时，蓝方能量机关相应地逆时针旋转（旋转方向以面朝该方能量机关时的旋转方向进行确定）。每局比赛开始前，能量机关旋转方向随机。该局比赛中，能量机关旋转方向保持一致。

- 小能量机关的转速固定为 $ \frac{1}{3}\pi rad/s $。

非正在激活状态的大能量机关转速固定为 $ \frac{1}{3}\pi rad/s $。

● 正在激活状态的大能量机关转速按照三角函数呈周期性变化。速度目标函数为： $ spd=a*\sin(\omega*t)+b $，其中 spd 的单位为 rad/s，t 的单位为 s，a 的取值范围为 0.780~1.045， $ \omega $ 的取值范围为 1.884~2.000，

b 始终满足 b=2.090-a。每次大能量机关进入可激活状态时，所有参数重置，其中 t 重置为 0，a 和  $ \omega $ 重置为取值范围内任意值。能量机关的实际转速与速度目标函数的时间误差在 500ms 内。

一方激活能量机关后，在其持续时间结束前，该方所有存活机器人都会获得一定增益，且该方的能量机关进入已激活状态。能量机关增益效果结束后，能量机关进入未激活状态。双方可以同时拥有能量机关增益。

一方激活能量机关后，在其持续时间结束前，该方所有存活机器人都会获得一定增益，且该方的能量机关进入已激活状态。能量机关增益效果结束后，能量机关进入未激活状态。双方可以同时拥有能量机关增益。

根据时间，能量机关划分两个阶段：小能量机关和大能量机关。比赛开始到比赛开始3分钟，为小能量机关；比赛开始3分钟后，为大能量机关。

小能量机关：双方的小能量机关状态相互独立。比赛开始及比赛开始1分30秒时，双方各获得1次激活小能量机关的机会，该机会可累积。步兵操作手通过裁判系统选手端或哨兵机器人通过裁判系统串口可触发未激活状态的小能量机关进入正在激活状态。小能量机关进入正在激活状态20秒后，若其仍未被激活，则将恢复为未激活状态。一方机器人成功激活小能量机关后，该方所有机器人、前哨站、基地均获得25%的防御增益，持续45秒。小能量机关增益持续期间内，所有英雄、步兵、空中机器人在获得经验时，额外获得原经验100%的经验，一方在一次小能量机关增益期间内通过此方式最多共获得1200点额外经验。

大能量机关：双方的大能量机关状态相互独立。比赛开始3分钟、4分15秒、5分30秒时，双方各获得1次激活大能量机关的机会，该机会可累积。步兵操作手通过裁判系统选手端或哨兵机器人通过裁判系统串口可触发未激活状态的大能量机关进入正在激活状态。大能量机关进入正在激活状态20秒后，若其仍未被激活，则将恢复为未激活状态。大能量机关的每块装甲模块被划分为1~10环。一方大能量机关被激活后，系统将根据其击中的平均环数和激活灯臂数、为该方所有机器人提供时间不等、效果不同的攻击、防御和热量冷却增益，为该方前哨站、基地提供相应的防御增益，详见“表5-17平均环数与对应增益”。同时，大能量机关被激活时，将有750点经验平均分给激活方所有存活的英雄、步兵、空中机器人。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//09f1bffd-2115-4ca3-9876-99b629a70531/markdown_0/imgs/img_in_image_box_350_1047_854_1460.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A44Z%2F-1%2F%2F3abf2f6e781c0d19c248d29d414aa9621fe0d31428040e5f1bc09fd12688bc56" alt="Image" width="42%" /></div>


<div style="text-align: center;"><div style="text-align: center;">图 5-18 能量机关击打区域示意图</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//09f1bffd-2115-4ca3-9876-99b629a70531/markdown_1/imgs/img_in_image_box_130_158_171_196.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A44Z%2F-1%2F%2Fc68a0fcb8fb9fb1f07fce6fd58213c77b4e74990fadea30a133165969d2005ad" alt="Image" width="3%" /></div>


能量机关装甲模块对弹丸击打位置的检测精度为径向  $ 1 \, mm $。

<div style="text-align: center;"><div style="text-align: center;">表 5-17 平均环数与对应增益</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>平均环数区间</td><td style='text-align: center; word-wrap: break-word;'>攻击增益</td><td style='text-align: center; word-wrap: break-word;'>防御增益</td><td style='text-align: center; word-wrap: break-word;'>热量冷却增益</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>[1,3]</td><td style='text-align: center; word-wrap: break-word;'>150%</td><td style='text-align: center; word-wrap: break-word;'>25%</td><td style='text-align: center; word-wrap: break-word;'>无</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>(3,7]</td><td style='text-align: center; word-wrap: break-word;'>150%</td><td style='text-align: center; word-wrap: break-word;'>25%</td><td style='text-align: center; word-wrap: break-word;'>2 倍</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>(7,8]</td><td style='text-align: center; word-wrap: break-word;'>200%</td><td style='text-align: center; word-wrap: break-word;'>25%</td><td style='text-align: center; word-wrap: break-word;'>2 倍</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>(8,9]</td><td style='text-align: center; word-wrap: break-word;'>200%</td><td style='text-align: center; word-wrap: break-word;'>25%</td><td style='text-align: center; word-wrap: break-word;'>3 倍</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>(9,10]</td><td style='text-align: center; word-wrap: break-word;'>300%</td><td style='text-align: center; word-wrap: break-word;'>50%</td><td style='text-align: center; word-wrap: break-word;'>5 倍</td></tr></table>

<div style="text-align: center;"><div style="text-align: center;">表 5-18 激活灯臂数与对应增益持续时间</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>激活灯臂数</td><td style='text-align: center; word-wrap: break-word;'>增益持续时间（秒）</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>5</td><td style='text-align: center; word-wrap: break-word;'>30</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>6</td><td style='text-align: center; word-wrap: break-word;'>35</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>7</td><td style='text-align: center; word-wrap: break-word;'>40</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>8</td><td style='text-align: center; word-wrap: break-word;'>45</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>9</td><td style='text-align: center; word-wrap: break-word;'>50</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>10</td><td style='text-align: center; word-wrap: break-word;'>60</td></tr></table>

一方每次成功激活己方大能量机关，都会使己方能量机关的有效击打区域缩小，仅剩部分环数的装甲模块可继续检测弹丸命中，具体关系见下表：



<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>己方大能量机关累计被激活次数</td><td style='text-align: center; word-wrap: break-word;'>可继续检测的环数</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>1 次</td><td style='text-align: center; word-wrap: break-word;'>4, 5, 6, 7, 8, 9, 10 环</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>2 次</td><td style='text-align: center; word-wrap: break-word;'>7, 8, 9, 10 环</td></tr></table>

##### 5.5.2.1 能量机关的状态

能量机关状态可分为4种状态：未激活、正在激活、已激活和激活失败。

## 1. 未激活状态

能量机关进入未激活状态时，状态如下所示：

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//09f1bffd-2115-4ca3-9876-99b629a70531/markdown_2/imgs/img_in_image_box_385_377_810_715.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A45Z%2F-1%2F%2Fdb42a0bc6eb125be2d6812ef01513cf997743dc55a954212eb9b2450f570a405" alt="Image" width="35%" /></div>


<div style="text-align: center;"><div style="text-align: center;">图 5-19 能量机关未激活状态示意图</div> </div>


## 2. 正在激活状态

##### 小能量机关

当小能量机关进入正在激活状态，能量机关随机点亮5块装甲模块中的任意1个，被点亮的装甲模块亮起特殊灯效，并且该装甲模块对应的灯臂中轴有箭头状流动灯效。此时，若弹丸在2.5秒内击中任意一个被点亮的装甲模块，该灯臂会被完全点亮并亮起相应灯效，与此同时，能量机关随机点亮其余4块装甲模块中的任意一个，以此类推。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//09f1bffd-2115-4ca3-9876-99b629a70531/markdown_2/imgs/img_in_image_box_137_1075_1050_1381.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A45Z%2F-1%2F%2F44eac1c05b930b2ec3e33569e8077eb80370aca3c1f0f90817d927bbfe73f2e3" alt="Image" width="76%" /></div>


<div style="text-align: center;"><div style="text-align: center;">图 5-20 小能量机关正在激活状态示意图</div> </div>


##### 大能量机关

当大能量机关进入正在激活状态，能量机关随机点亮5块装甲模块中的任意2个，被点亮的装甲模块亮起特殊灯效，并且该装甲模块对应的灯臂中轴有箭头状流动灯效。此时，若弹丸在2.5秒内击中任意一个被点亮的装甲模块的可检测区域，该灯臂会改变相应灯效，此后1秒内，机器人可以击中另一个被点亮的装甲模块，不论是否成功，能量机关都将重新随机点亮5块装甲模块中的任意2个，以此类推。大能量机关的灯臂中部灯效将指示激活进度，如当前已激活第一组，正在激活第二组，则中部灯臂将亮起约 $ \frac{1}{5} $，此后若成功激活第二组（击中第二组中第一块被点亮的装甲即视为成功激活第二组，不论第二组中第二块装甲是否被击中，在开始激活第三组时灯效发生改变），则中部灯臂将亮起约 $ \frac{2}{5} $。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//09f1bffd-2115-4ca3-9876-99b629a70531/markdown_3/imgs/img_in_image_box_128_522_172_568.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A46Z%2F-1%2F%2F1e1176c3bbea3b06aaef302ba7f55d244ab02bb4dc608f22539034fb4b99c5e3" alt="Image" width="3%" /></div>


为确保时序匹配，激活流程中，能量机关在重新随机点亮5块装甲模块中的任意2个前，灯臂和装甲模块灯效将熄灭至多200ms。

具体灯效如下图所示：

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//09f1bffd-2115-4ca3-9876-99b629a70531/markdown_3/imgs/img_in_image_box_132_674_1056_898.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A46Z%2F-1%2F%2Fd8a3476eaca7b1c1ae43619a6b487696e3dd494642cf2adf926d44c6025b3dd3" alt="Image" width="77%" /></div>


<div style="text-align: center;"><div style="text-align: center;">图 5-21 大能量机关正在激活状态示意图</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//09f1bffd-2115-4ca3-9876-99b629a70531/markdown_3/imgs/img_in_image_box_384_1005_817_1426.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A46Z%2F-1%2F%2F62a25f6f36266fda682750e992bcc2ebe4e470ea97a3666693b286d54a04b187" alt="Image" width="36%" /></div>


<div style="text-align: center;"><div style="text-align: center;">图 5-22 能量机关可激活标识示意图</div> </div>


## 3. 已激活状态

若5组灯臂全部激活，此时能量机关处于已激活状态，如下所示：

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//a39d132a-6ebf-4f5d-a9f3-a1864e101432/markdown_0/imgs/img_in_image_box_392_261_814_593.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A44Z%2F-1%2F%2F61784c247adb29af52f5f3acf82a89a93215e1a7d5e81d5d555f0ba2f138cade" alt="Image" width="35%" /></div>


<div style="text-align: center;"><div style="text-align: center;">图 5-23 能量机关已激活状态示意图</div> </div>


## 4. 激活失败

激活过程中，若出现以下任意一种情况，则此次激活失败，能量机关重置正在激活状态：

未能在2.5秒内击中点亮的装甲模块。

击中非随机点亮的装甲模块。

#### 5.5.3 场地增益机制

##### 5.5.3.1 场地增益点概述

全场各增益点分布如下图所示。战场增益点均铺设场地交互模块卡，场地交互模块卡可能存在死区，参赛队伍需自行调整适应。场地交互模块的检测可能存在延迟，机器人的占领状态的失效均有2秒延迟。若占领机器人战亡，增益失效。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//a39d132a-6ebf-4f5d-a9f3-a1864e101432/markdown_1/imgs/img_in_image_box_158_189_1051_811.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A45Z%2F-1%2F%2Fb0f3a0d635d4d594cd49276ea93adbfb5a484b64f643dfbe3382c0ba30e66b5b" alt="Image" width="74%" /></div>


<div style="text-align: center;"><div style="text-align: center;">[1] 补给区增益点</div> </div>


<div style="text-align: center;"><div style="text-align: center;">[2] 地形跨越增益点（公路）</div> </div>


<div style="text-align: center;"><div style="text-align: center;">[5] 梯形高地 [6] 基地增益点增益点</div> </div>


<div style="text-align: center;"><div style="text-align: center;">[9] 前哨站增 [10] 地形跨越增益点 益点（隧道）</div> </div>


<div style="text-align: center;"><div style="text-align: center;">地形跨越增益点（隧道）</div> </div>


<div style="text-align: center;"><div style="text-align: center;">[7] 堡垒增益点</div> </div>


<div style="text-align: center;"><div style="text-align: center;">[4] 地形跨越增益点（飞坡）</div> </div>


<div style="text-align: center;"><div style="text-align: center;">[11] 中央高地增益点兼地形跨越增益点（高地）</div> </div>


<div style="text-align: center;"><div style="text-align: center;">[8] 地形跨越增益点（高地）</div> </div>


<div style="text-align: center;"><div style="text-align: center;">[12] 装配区增益点</div> </div>


<div style="text-align: center;"><div style="text-align: center;">图 5-24 战场增益点分布示意图</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//a39d132a-6ebf-4f5d-a9f3-a1864e101432/markdown_1/imgs/img_in_image_box_127_1241_170_1287.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A45Z%2F-1%2F%2F3fdcc1c1879d0e57a61ff1c587f2b89aa173cf0a28139db28e9f6de8e38fa949" alt="Image" width="3%" /></div>


实际比赛中，受实际地形限制，地形跨越增益（隧道）的场地交互模块卡部分铺设面积显著小于其他增益区的铺设面积。机器人在通过时建议速度保持在0.8m/s以下以确保稳定检测。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//a39d132a-6ebf-4f5d-a9f3-a1864e101432/markdown_2/imgs/img_in_image_box_161_162_1042_602.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A45Z%2F-1%2F%2F26188e5bc991748bf146760da818c7283fd531415c8cc9f14b6e74224ee52723" alt="Image" width="73%" /></div>


<div style="text-align: center;"><div style="text-align: center;">[1] 场地交互模块卡镶嵌位置</div> </div>


<div style="text-align: center;"><div style="text-align: center;">图 5-25 场地交互模块卡铺设示意图</div> </div>


<div style="text-align: center;"><div style="text-align: center;">表 5-19 增益类型一览</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>类型</td><td style='text-align: center; word-wrap: break-word;'>注解</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>攻击增益</td><td style='text-align: center; word-wrap: break-word;'>提高弹丸攻击造成的伤害值。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>防御增益</td><td style='text-align: center; word-wrap: break-word;'>$ \underline{\text{改变受弹丸攻击、撞击造成的伤害值。负防御增益简称为“易伤”。}} $\n $ \uwave{\text{防御增益不适用于因违规判罚、裁判系统模块离线、飞镖等导致的扣血。}} $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>射击热量冷却增益</td><td style='text-align: center; word-wrap: break-word;'>提高射击热量冷却速率。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>缓冲能量增益</td><td style='text-align: center; word-wrap: break-word;'>额外获得底盘功率缓冲能量。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>回血增益</td><td style='text-align: center; word-wrap: break-word;'>机器人每秒恢复一定血量，直至达到上限血量。</td></tr></table>

攻击增益使机器人造成的弹丸伤害变为：原始伤害 $ ^{*} $攻击增益。

防御增益使机器人、基地、前哨站受到的攻击伤害变为：原始伤害 $ ^{*} $（1-防御增益）。

关于原始伤害，详见：“表5-2攻击伤害或撞击的扣血机制”。

示例一：若红方机器人拥有200%攻击增益，蓝方机器人拥有25%防御增益，且此时被对方雷达机器人标记进度大于100，则红方发射一发42mm弹丸击中蓝方机器人，蓝方机器人受到的伤害为： $ 200 \times 200\% \times (1 - 25\% + 15\%) = 360 $。

示例二：若红方机器人拥有 200% 攻击增益，且此时蓝方英雄机器人被对方雷达标记进度大于 100，则红方发射一发 42mm 弹丸击中蓝方英雄机器人，蓝方英雄机器人受到的伤害为： $ 200 \times 200\% \times (1 + 15\%) = 460 $。

当机器人获得的同类增益超过一个时，取最大增益效果，包括攻击、防御、易伤、回血和射击热量冷却增益。

示例一：红方步兵机器人通过激活大能量机关获得了25%防御增益，若此时其又占领了己方基地增益点，则其拥有50%防御增益，此后若其又获得15%易伤，则其拥有35%防御增益。

示例二：蓝方步兵机器人通过激活大能量机关获得了25%防御增益，若此时其又占领了对方堡垒增益点，则其拥有75%易伤，此后若其又获得15%易伤，则其仍拥有75%易伤。

经过增益计算后的最终伤害值或回血值若非整数，则四舍五入。

##### 5.5.3.2 基地增益点机制

基地增益点可由己方地面机器人占领。同一方的多台机器人可同时占领基地增益点。

在七分钟比赛阶段，占领己方基地增益点的机器人可以获得50%防御增益，兑换允许发弹量，以及解除“虚弱”状态。关于“虚弱”状态，详见“5.2.2复活机制”。

##### 5.5.3.3 中央高地增益点机制

英雄、步兵、哨兵机器人均可占领中央高地增益点。不相连的中央高地增益点占领关系相互独立，且其场地交互模块卡铺设范围与两处地形跨越增益点（高地）的较高处一致。同一方的多台机器人可同时占领中央高地增益点。若一方机器人占领中央高地增益点，另一方机器人无法同时占领。

占领中央高地增益点的机器人获得25%防御增益。

##### 5.5.3.4 梯形高地增益点机制

所有己方地面机器人均可占领己方梯形高地增益点。同一方的多台机器人可同时占领梯形高地增益点。若一方的梯形高地增益点被该方机器人占领，占领梯形高地增益点的机器人获得50%防御增益。

##### 5.5.3.5 地形跨越增益点机制

中央高地各有2处地形跨越增益点（高地），双方公路区各有2处地形跨越增益点（公路）、2处地形跨越增益点（飞坡）、6处地形跨越增益点（隧道）。

地面机器人均可占领地形跨越增益点。同一方的多台机器人、双方机器人均可同时占领地形跨越增益点。

同一台机器人需在 X 秒内检测到一方场地每一处同类型地形跨越增益点的场地交互模块卡，且途中不能检测到其他场地交互模块卡。对于地形跨越增益（公路/高地），必须先检测到较低处增益点，再检测到较高处增益点，才能触发地形跨越增益；对于地形跨越增益点（隧道），必须按顺序检测到一端、中间、另一端增益点才能触发增益。地形跨越增益点（公路）与地形跨越增益点（隧道）的 X 为 3，地形跨越增益点（高地）的 X 为 5，地形跨越增益点（飞坡）的 X 为 10，具体增益如下：

##### 地形跨越增益（飞坡）

25%防御增益，持续时间为30秒。

##### 地形跨越增益（高地）

25%防御增益，持续时间为30秒。

##### 地形跨越增益（公路）

25%防御增益，持续时间为5秒。

同一机器人在获得地形跨越增益（公路）后的15秒内，不能重复获得地形跨越增益（公路）。

##### 地形跨越增益（隧道）

50%防御增益，持续时间为10秒。

2 倍热量冷却增益，持续时间为 120 秒。

当机器人在持有地形跨越增益（飞坡、高地或公路）的状态下，若再次获得同类增益，机器人将获得50%的防御增益。同时，该防御增益的剩余持续时间将更新为：当前已持有增益的剩余时间与新获得增益的初始持续时间中的较大值。

##### 示例：

若机器人先获得地形跨越增益（飞坡）初始30秒，在第10秒时（剩余20秒）获得了地形跨越增益（公路，初始5秒），则剩余时间取较大值20秒。

若机器人先获得地形跨越增益（飞坡），在第29秒时（剩余1秒）获得了地形跨越增益（公路，初始5秒），则剩余时间更新为5秒。

机器人战亡后，已获得的地形跨越增益将会被清除。

##### 5.5.3.6 前哨站增益点机制

在己方前哨站存活的情况下，英雄、工程、步兵、哨兵机器人均可占领己方前哨站增益点。在对方前哨站被击毁、己方前哨站存活且比赛开始5分钟内，己方的英雄、工程、步兵、哨兵机器人可以占领对方前哨站增益点。同一方的多台机器人可同时占领前哨站增益点。

占领前哨站增益点的机器人可以兑换允许发弹量（详见“5.3.2 允许发弹量机制”），获得25%防御增益，并解除“虚弱”及其对应的无敌状态。关于“虚弱”状态，详见“5.2.2 复活机制”。

##### 5.5.3.7 装配区增益点机制

装配区增益点仅可由己方工程机器人占领。

占领装配区增益点的工程机器人将处于无敌状态，最长累计180秒（离开增益区后重新占领，时间不重置）。

##### 5.5.3.8 补给区增益点机制

地面机器人均可占领己方补给区增益点。同一方的多台机器人可同时占领补给区增益点。

占领己方补给区增益点的机器人可提升复活读条速度或获得回血增益。具体实现形式和数值请参阅“5.2 回血与复活机制”。

占领补给区增益点后，工程机器人将处于无敌状态。

##### 5.5.3.9 堡垒增益点机制

堡垒增益点可被英雄、步兵、哨兵机器人占领。双方可同时占领，同一时间仅能被一台己方机器人占领且只有最先占领的机器人获得增益，但可同时被多台对方机器人占领。

在己方前哨站首次被击毁前，堡垒增益点处于失效状态。在己方前哨站被首次击毁后，堡垒增益点生效。

##### 己方占领效果

定义己方基地血量上限减去本局中血量最低值的差值为 $ \Delta $。

占领堡垒增益点的己方机器人获得50%防御增益，且获得值为w的射击热量冷却增益，w与Δ相关，具体关系为： $ w = \frac{\Delta}{40} $（向下取整），w的上限为75。该射击热量冷却增益与其他来源的射击热量冷却增益的效果取最高。

##### 示例：

一台射击热量冷却速率为 40/秒的机器人，同时获得了堡垒增益点提供的值为 75 的射击热量冷却增益和 5 倍射击热量冷却增益。由于  $ 40*5>40+75 $，故机器人实际射击热量冷却速率为 200/秒。

机器人占领堡垒后，堡垒增益区将为机器人提供“储备允许发弹量”（独立于机器人自身拥有的允许发弹量），其上限为N。占领堡垒增益区的机器人在发射弹丸时，优先消耗“储备允许发弹量”，“储备允许发弹量”耗尽后再消耗机器人自身的允许发弹量。步兵和哨兵机器人每发射一发17mm弹丸，消耗1储备允许发弹量；英雄机器人每发射1发42mm弹丸，消耗10储备允许发弹量。

 $$  N=100+2^{*}\frac{\Delta}{15}( 向下取整 ),\ N 至多为 500。 $$ 

##### 对方占领效果

当比赛进行3分钟且对方前哨站被击毁后，英雄、步兵、哨兵机器人可以占领对方的堡垒增益点。

正在占领对方堡垒增益点的机器人获得100%易伤，当一方机器人单次占领时间计满20秒，对方基地护甲展开。占领对方堡垒增益点的计时可以在机器人死亡或占领状态失效后保留3秒，保留期间计时暂停。对方基地护甲展开后，占领对方堡垒增益点的机器人不再获得易伤。

### 5.6 机器人特殊机制

#### 5.6.1 英雄机器人特殊机制

当英雄机器人选择了“远程优先”的整机类型且位于己方可部署区域（详见“图5-26己方可部署区域示意图”）时，可以选择进入“部署模式”。确认进入“部署模式”1秒后，英雄机器人进入“部署模式”，在该模式下，英雄机器人底盘断电，失去图传画面，获得25%防御增益，射击初速度上限提升为16.5m/s，且发射42mm弹丸攻击基地时具有150%攻击增益。英雄机器人每次退出部署模式时，8秒后才能再次进入部署模式。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//ce90333b-998c-45d7-ad51-eebae986bc10/markdown_2/imgs/img_in_image_box_127_755_169_796.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A46Z%2F-1%2F%2Fa7bd1d6d973bbaf2e4a7a15847648fa4cb2013d677ed7ef5b07631dfb818274a" alt="Image" width="3%" /></div>


<div style="text-align: center;"><div style="text-align: center;">英雄机器人在部署模式下战亡，不会退出部署模式。</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//ce90333b-998c-45d7-ad51-eebae986bc10/markdown_2/imgs/img_in_image_box_164_823_1046_1352.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A46Z%2F-1%2F%2F3b20f353a4593bd4a4b694ebd9dced3022c767764e6c9bc859babaf067b05e0b" alt="Image" width="74%" /></div>


<div style="text-align: center;"><div style="text-align: center;">[1] 红方己方可部署区域 [2] 蓝方己方可部署区域</div> </div>


<div style="text-align: center;"><div style="text-align: center;">图 5-26 己方可部署区域示意图</div> </div>


英雄机器人是否位于已方可部署区域的判断条件：

① 英雄机器人场地交互模块未检测到对方可部署区域场地交互模块卡。

② 英雄机器人场地交互模块检测到已方可部署区域场地交互模块卡，或定位模块的坐标位于已方可部署区域内。

当条件 $ ^{①} $、 $ ^{②} $同时满足时，视为英雄机器人位于已方可部署区域。当条件 $ ^{①} $、 $ ^{②} $任一不满足时，英雄机器人会自动退出部署模式。

关于英雄机器人进入和退出“部署模式”的操作方式，详见：裁判系统选手端界面说明。

在英雄部署模式下，官方客户端与自定义客户端的图传视频流都将被切断，但自定义客户端的自定义数据流不受影响。

因英雄部署模式导致失去图传画面后，小地图、自定义 UI 仍可正常使用。

#### 5.6.2 工程机器人特殊机制

在比赛的前3分钟内，工程机器人只要存活便拥有50%防御增益。

#### 5.6.3 空中机器人特殊机制

##### 空中支援

每局比赛中，空中机器人拥有750发允许发弹量。在七分钟比赛阶段，空中机器人不能从任何途径获取弹丸。

比赛开始时，空中机器人拥有30秒空中支援时间，随后每1分钟获得额外20秒空中支援时间。

云台手可以通过裁判系统选手端呼叫或暂停空中支援。在空中支援时间内，空中机器人将获得第一视角画面，同时空中机器人与停机坪不接触时，可发射弹丸。空中支援期间，机器人发射机构解锁，反之锁定。

在空中支援时间耗尽后，若云台手未暂停空中支援，此后每秒额外的空中支援时间都将消耗1金币，详见“表5-6兑换规则”。

##### 空中机器人被雷达反制

雷达系统上可安装激光发射装置，用于瞄准和照射空中机器人上的激光检测模块。仅在对方空中机器人发起空中支援时，己方雷达系统上的激光发射装置及其执行机构上电。空中机器人具有“被瞄准进度”P，取值范围为0（初始及最小值）至100（最大值）。当P达到 $ P_{0} $时，空中机器人的发射机构被锁定，同时P归零，锁定状态持续45秒后解除，发射机构锁定期间P不增长。每局比赛中，最多可通过该机制对空中机器人发射机构进行5次锁定。

激光检测模块的被瞄准难度有三种，具体如下：

难度一：激光检测模块无特殊变化， $ P_{0} $ 为 50;

难度二：激光检测模块的可检测区域纵向缩减为原面积的 $ \frac{3}{5} $， $ P_{0} $为100。

难度三：激光检测模块的可检测区域纵向缩减为原面积的 $ \frac{1}{5} $，且不再主动发光， $ P_{0} $为100。

每次尝试通过该机制锁定对方空中机器人发射机构时，激光检测模块的被瞄准难度将有所不同，具体如下表：

<div style="text-align: center;"><div style="text-align: center;">表 5-20 反制状态与被瞄准难度对应表</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>当前状态</td><td style='text-align: center; word-wrap: break-word;'>被瞄准难度</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>第一次反制成功前</td><td style='text-align: center; word-wrap: break-word;'>难度一</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>第二次反制成功前</td><td style='text-align: center; word-wrap: break-word;'>难度二</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>第三次反制成功前</td><td style='text-align: center; word-wrap: break-word;'>难度二</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>第四次反制成功前</td><td style='text-align: center; word-wrap: break-word;'>难度三</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>第五次反制成功前</td><td style='text-align: center; word-wrap: break-word;'>难度三</td></tr></table>

从第四次被反制成功开始（含第四次），空中机器人可以选择花费等同于相同等级地面机器人兑换立即复活所需金币数的两倍金币（详见“表5-6兑换规则”），解除被反制状态并立即呼叫空中支援。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//961a0902-ac10-435a-8df2-8a16f0317db6/markdown_0/imgs/img_in_image_box_285_936_936_1389.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A45Z%2F-1%2F%2Fe3009a2c49a377fc4ff2b1ef30bad6e89d40c80768eaed4169cc9fcd9c699aff" alt="Image" width="54%" /></div>


<div style="text-align: center;"><div style="text-align: center;">[1] 第一次减少区域 [2] 第二次减少区域</div> </div>


<div style="text-align: center;"><div style="text-align: center;">图 5-27 激光检测模块缩小区域示意图</div> </div>


“被瞄准进度”计算逻辑如下所示：

##### 参数设定：

t: 当前激光连续照射的时长

 $ \Delta t $：判定周期，固定为0.1秒

n：连续判定次数（照射开始时 n=0，每触发一次判定 n 加 1）

##### 判定规则：

当空中机器人激光检测模块未被激光照射时，进度 P 以速率 0.5/s 匀速衰减，但不会小于 0，同时 t、n 立即归零；

当空中机器人激光检测模块被激光照射时，P 停止衰减。每当 t 累计满 0.1 秒，触发一次进度增加：

第1个0.1秒：P=P+0.6

第2个0.1秒：P=P+1.2

第n个0.1秒：P=P+0.6^{*}n

若单次持续照射时间不足 0.1 秒即中断，则 t、n 立即归零。

#### 5.6.4 哨兵机器人特殊机制

三分钟准备阶段开始后，十五秒裁判系统自检阶段前，云台手可选择对应哨兵机器人的操作方式为自动控制或半自动控制。若在指定时间内未选择操作方式，则在七分钟比赛阶段开始后，默认为自动控制。哨兵机器人可以通过向裁判系统服务器发送信息的方式自主兑换允许发弹量、远程兑换发弹量、远程兑换血量、确认复活、兑换立即复活、切换姿态。

此外，云台手可以通过裁判系统选手端相关指令干预哨兵机器人的行动，具体指令包括：

转发小地图标记

在补给区、基地增益点、前哨站增益点购买允许发弹量

确认复活

远程兑换发弹量

远程兑换血量

远程兑换立即复活

切换姿态

对于半自动哨兵，上述操作无需消耗金币；对于自动哨兵，云台手每进行一次上述的操作，需要花费50金币。

哨兵机器人拥有“姿态”系统，可以强化部分能力而削弱其他能力。哨兵机器人开局默认处于移动姿态。姿态切换具有5秒的冷却时间。每局中，哨兵机器人若累计处于一个姿态时间超过3分钟，该姿态效果下降。哨兵可以进入强化姿态，其能力将进一步强化，但每种强化姿态至多仅能累计进入15s，不同强化姿态的计时相互独立，超时后便不能再进入强化的该姿态，具体如下表所示：



<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>姿态</td><td style='text-align: center; word-wrap: break-word;'>强化姿态的效果</td><td style='text-align: center; word-wrap: break-word;'>默认效果</td><td style='text-align: center; word-wrap: break-word;'>下降后的效果</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>进攻姿态</td><td style='text-align: center; word-wrap: break-word;'>当前热量始终为 0，发射弹丸不增加热量，底盘功率降为 $ \frac{1}{2} $，获得 25%易伤</td><td style='text-align: center; word-wrap: break-word;'>获得 3 倍热量冷却增益，底盘功率降为 $ \frac{1}{2} $，获得 25%易伤</td><td style='text-align: center; word-wrap: break-word;'>获得 2 倍热量冷却增益，底盘功率降为 $ \frac{1}{2} $，获得 25%易伤</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>防御姿态</td><td style='text-align: center; word-wrap: break-word;'>获得 99%防御增益，底盘功率降为 $ \frac{1}{2} $，热量冷却速率降为 $ \frac{1}{3} $</td><td style='text-align: center; word-wrap: break-word;'>获得 50%防御增益，底盘功率降为 $ \frac{1}{2} $，热量冷却速率降为 $ \frac{1}{3} $</td><td style='text-align: center; word-wrap: break-word;'>获得 25%防御增益，底盘功率降为 $ \frac{1}{2} $，热量冷却速率降为 $ \frac{1}{3} $</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>移动姿态</td><td style='text-align: center; word-wrap: break-word;'>底盘功率上限提高为 200W，获得 25%易伤，热量冷却速率降为 $ \frac{1}{3} $</td><td style='text-align: center; word-wrap: break-word;'>底盘功率上限提高为 1.5 倍，获得 25%易伤，热量冷却速率降为 $ \frac{1}{3} $</td><td style='text-align: center; word-wrap: break-word;'>底盘功率上限提高为 1.2 倍，获得 25%易伤，热量冷却速率降为 $ \frac{1}{3} $</td></tr></table>

上述计算均取整数值。

热量冷却与底盘功率上限的变化，在哨兵机器人已完成热量冷却增益和其他底盘功率计算的值的基础上乘算。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//961a0902-ac10-435a-8df2-8a16f0317db6/markdown_2/imgs/img_in_image_box_141_1075_184_1117.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A47Z%2F-1%2F%2F0c0840114d9bffb383fc98e51023c25a963a5266c0350f77c674a0e6d47699e6" alt="Image" width="3%" /></div>


示例一：自动哨兵在默认防御姿态下的基础热量冷却速率为30每秒，随后其通过激活大能量机关获得3倍射击热量冷却增益，又通过占领堡垒增益点获得75每秒的射击热量冷却增益。先在这两者中取较大者（即+75每秒），此时自动哨兵的热量冷却速率为 $ 30+75=105 $，随后再乘算防御姿态对应的冷却速率衰减系数 $ \left(\frac{1}{3}\right) $，最终得到自动哨兵的实际热量冷却速率为 $ 105*\frac{1}{3}=35 $。

示例二：哨兵机器人当局已处于移动姿态下累计2分50秒，且未进入过其他姿态，此后其切换为强化移动姿态，则15秒后，将自动切换回移动姿态，且适用下降后的移动姿态效果。

#### 5.6.5 飞镖系统特殊机制

每周比赛中，飞镖系统可装载4枚飞镖，飞镖发射站闸门有2次开启机会，比赛开始30秒后和比赛开始4分钟后各1次，云台手可自行选择合适的时间使用，未使用的机会可累积。

##### 飞镖发射站闸门开闭

比赛过程中，云台手可使用键盘和鼠标在裁判系统选手端上控制发射站闸门开启。在闸门开启或闭合过程中，云台手不可控制飞镖发射。裁判系统选手端会显示闸门的开启和闭合的状态。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//961a0902-ac10-435a-8df2-8a16f0317db6/markdown_3/imgs/img_in_image_box_128_300_169_340.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A47Z%2F-1%2F%2F91f83c2904b545f9ab376e54986a42a510c928cec9817acf1625243be339a04e" alt="Image" width="3%" /></div>


#### 闸门完全开启耗时约7秒

当发射站闸门完全开启后，云台手可通过控制飞镖系统发射飞镖，时长为30秒。同时，对方前哨站或基地的飞镖检测模块将会刷新检测窗口期，持续时间为40秒。发射的飞镖需在检测窗口期命中飞镖检测模块，否则攻击无效。

当发射站第一次关闭闸门后，飞镖发射站将会进入15秒的冷却期。冷却期结束后，方可第二次开启闸门。冷却期间，飞镖发射站闸门不可开启。

##### 飞镖目标选择

当前哨站被击毁后，云台手在控制飞镖发射站闸门开启前，可以通过裁判系统选手端选择此次飞镖要击打的目标为“固定目标”、“随机固定目标”、“随机移动目标”、“末端移动目标”。

若选择“固定目标”，飞镖检测模块将保持初始位置不变。

若选择“随机固定目标”，则在飞镖发射站闸门开启时，基地的飞镖检测模块将开始移动，并在飞镖发射站闸门完全开启前相对初始位置移动到另一个随机位置。飞镖检测窗口期结束后恢复初始位置。在检测窗口期内，若飞镖命中，则飞镖检测模块将会移动至一个新的位置。

若选择“随机移动目标”，则在飞镖发射站闸门开启时，基地的飞镖检测模块将开始移动，在检测到任一飞镖发出后，移动到不同于飞镖发出时位置的新位置，且在600ms内完成移动并静止。检测窗口期内，在飞镖命中或检测到第一发飞镖发出的10秒后，飞镖检测模块将会重新开始移动，直到检测到下一发飞镖发出。

若选择“末端移动目标”，则在飞镖发射站闸门开启时，基地的飞镖检测模块将开始移动，在检测到任一飞镖发出的1.2秒后，开始移动到不同于飞镖发出时位置的新位置，且在600ms内完成移动并静止。检测窗口期内，在飞镖命中或检测到第一发飞镖发出的10秒后，飞镖检测模块将会重新开始移动，直到检测到下一发飞镖发出。

飞镖检测模块和飞镖引导灯在移动时相对位置不变，且始终相对初始位置在同一平面内移动。移动的范围为：平行于场地宽边方向相对于初始位置[-280mm,280mm]。

##### 飞镖命中收益

以下均为飞镖命中目标后除去本身对目标造成的伤害以外获得的收益：

当飞镖首次、第二次、第三次、第四次命中对方前哨站、基地的“固定目标”、“随机固定目标”时，对方所有操作手界面、小地图中的机器人位置、自定义UI分别被遮挡10秒（首次）、5秒（第二次）、

3 秒（第三次）、2 秒（第四次）。当飞镖命中对方基地时，己方存活的英雄、步兵、空中机器人分别平分 200（固定目标）、600（随机固定目标）点经验。

当飞镖命中对方基地“随机固定目标”时，使对方当前持有的地形跨越、能量机关增益暂时失效，即正常计时但无增益效果，失效持续时间与上述对应的被遮挡时间相同。

当飞镖命中对方基地“随机移动目标”、“末端移动目标”时，对方所有操作手界面、小地图中的机器人位置、自定义UI被遮挡10秒，己方存活的英雄、步兵、空中机器人平分2500点经验，使对方当前持有的地形跨越、能量机关增益失效。

若选择“随机移动目标”、“末端移动目标”后命中基地飞镖检测模块，对方全部存活的地面机器人分别立即扣除各自当前上限血量10%（随机移动目标）、25%（末端移动目标）的血量（计入对方全队总伤害，但该扣血本身以及导致的机器人战亡不会产生经验）。若连续命中，则被遮挡时间叠加计算。

若选择“固定目标”、“随机固定目标”后4发飞镖全部命中基地，或选择“随机移动目标”、“末端移动目标”后任意一发飞镖命中基地，对方基地护甲将立刻展开。

当基地或前哨站的飞镖引导灯亮起时，若飞镖命中基地或者前哨站，其对应的增益点暂时失效，持续时间为30秒，若连续命中，则失效时间刷新。每次飞镖命中后，对应目标的检测窗口将关闭2秒。

● 操作手界面、小地图中的机器人位置、自定义 UI 被遮挡期间，操作手可以主动选择通过半自动控制方式控制机器人，具体而言：裁判系统选手端将会显示与云台手所获得的界面近似的大地图界面，操作手可以通过在大地图界面点击向机器人发送指令控制机器人，两次发送间隔不得短于3秒。

自定义客户端仍可以正常接受图传画面等数据。

#### 5.6.6 雷达特殊机制

雷达的功能包括：雷达识别、雷达反制、雷达解析信息波，具体如下：

##### 雷达识别

雷达可识别双方地面机器人、空中机器人的位置，并将该机器人的坐标发送至裁判系统服务器。每台地面机器人及空中机器人均有“被标记进度”P，取值范围为0（初始及最小值）至150（最大值）。裁判系统根据雷达识别的精准度实时更新P，连续标记准确将使P加速上涨；反之，连续标记错误或者数据中断则会使P加速衰减。当P达到一定阈值，对应目标将获得一定的效果。此外，通过持续标记维持对方的易伤状态，雷达还可以解锁“双倍易伤”效果。

受比赛现场无线环境影响，或定位模块受到较大面积的遮挡时，机器人定位模块检测到的坐标有较小概率出现间歇或持续性漂移。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//1445599c-e2d0-42e8-8ce3-ffc46827b56d/markdown_0/imgs/img_in_image_box_134_1423_176_1469.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A04%3A10Z%2F-1%2F%2F01da2b56bbd3e9339b59dee1406d264b38304b6e9acfd029cd7b0607906ec06e" alt="Image" width="3%" /></div>


##### 参数设定：

● d：识别误差，即“雷达所发送的坐标”与“机器人实际平面坐标”的直线距离，分为三个等级：

➢ 准确：d<0.8m

➢ 半准确： $ 0.8m \leq d < 1.6m $

➢ 错误： $ d \geqslant 1.6m $

x：当前标记的影响值（即进度改变量），初值为0。

☑ 判定频率：由雷达发送频率决定。

##### 进度P的计算逻辑：

每当裁判系统接收到雷达数据，或数据中断时，先更新 x，后更新 P。

<div style="text-align: center;"><div style="text-align: center;">表 5-21 “被标记进度” P 的计算逻辑</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>标记状态</td><td style='text-align: center; word-wrap: break-word;'>X 的更新逻辑</td><td style='text-align: center; word-wrap: break-word;'>P 的更新逻辑</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>准确</td><td style='text-align: center; word-wrap: break-word;'>若上一次标记为准确或者半准确，则 x=x+1.0；否则 x=1.0</td><td rowspan="4">P=P+x\n若计算结果 P&lt;0，则\nP 取 0；若计算结果\nP&gt;150，则 P 取 150。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>半准确</td><td style='text-align: center; word-wrap: break-word;'>若上一次标记为准确或者半准确，则 x=x+0.5；否则 x=0.5</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>错误</td><td style='text-align: center; word-wrap: break-word;'>若上一次标记错误/中断，则 x=x-0.8；否则 x=-0.8</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>数据中断</td><td style='text-align: center; word-wrap: break-word;'>裁判系统每累计 0.5 秒未收到数据，视为触发一次“错误”判定</td></tr></table>

示例：若一方雷达以5Hz频率、100%的准确率连续向裁判系统服务器发送对方工程机器人的坐标，则在0~1秒内，以0.2秒为间隔，对方工程机器人的被标记进度分别为1、3、6、10、15，在第3.0秒，该机器人的被标记进度将达到120。此后，若雷达以5Hz频率、0%的准确率向裁判系统服务器发送该机器人的坐标，则在3.0~4.0秒内，以0.2秒为间隔，该机器人的被标记进度分别为119.2、117.6、115.2、112、108。此后若雷达连续1.0秒未发送工程机器人的坐标，则在4.0~5.0秒内，该机器人的被标记进度将为103.2、97.6（在之前错误的基础上被判定为额外连续两次错误）。此后，若雷达又发送了连续两次工程机器人的正确坐标，则该机器人的被标记进度将为98.6、100.6。

P 的阈值与对应效果：

<div style="text-align: center;"><div style="text-align: center;">表 5-22 P 的阈值与对应目标获得的效果</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>目标类型</td><td style='text-align: center; word-wrap: break-word;'>P 的取值区间</td><td style='text-align: center; word-wrap: break-word;'>小地图显示效果</td><td style='text-align: center; word-wrap: break-word;'>增益（仅限地面机器人）</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>对方机器人</td><td style='text-align: center; word-wrap: break-word;'>[0,100)</td><td style='text-align: center; word-wrap: break-word;'>己方雷达发送的该机器人坐标对应的位置</td><td style='text-align: center; word-wrap: break-word;'>无额外效果</td></tr><tr><td rowspan="2"></td><td style='text-align: center; word-wrap: break-word;'>[100,120)</td><td style='text-align: center; word-wrap: break-word;'>● 该机器人定位模块检测到的实际位置\n● 特殊标识</td><td style='text-align: center; word-wrap: break-word;'>15%易伤</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>[120,150]</td><td style='text-align: center; word-wrap: break-word;'>● 该机器人定位模块检测到的实际位置\n● 特殊标识</td><td style='text-align: center; word-wrap: break-word;'>20%易伤</td></tr><tr><td rowspan="2">己方机器人</td><td style='text-align: center; word-wrap: break-word;'>[0,50)</td><td style='text-align: center; word-wrap: break-word;'>己方雷达发送的该机器人坐标对应的位置</td><td style='text-align: center; word-wrap: break-word;'>无额外效果</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>[50,150]</td><td style='text-align: center; word-wrap: break-word;'>● 该机器人定位模块检测到的实际位置\n● 特殊标识</td><td style='text-align: center; word-wrap: break-word;'>无额外效果</td></tr></table>





双倍易伤机制：当雷达每累计使对方机器人易伤1分钟（同时有多台机器人易伤时，时间不累加），将会获得1次触发“双倍易伤”的机会，雷达可以通过裁判系统主动发送命令消耗机会，并使当前所有来源于雷达的易伤数值翻倍，持续30秒。每局比赛中，雷达至多可以触发2次“双倍易伤”。

##### 雷达反制

详见“5.6.3 空中机器人特殊机制”。

##### 雷达解析电磁波

比赛过程中，双方雷达基座将放置官方发射源，该发射源将发射电磁波，其中包含载有对方队伍信息的信息波，以及相近频段的干扰波。红方广播源/干扰源放置在红方雷达基座，包含有蓝方队伍的信息，反之同理。参赛队伍可以在雷达上制作并安装天线和解调电路，以解析、识别信息波和干扰波，并为己方提供信息和优势。

电磁波的调制方式为 2-GFSK，即二进制高斯频移键控；FSK 映射关系为：0→-1，1→+1；各等级电磁波的相关参数如下表所示：

<div style="text-align: center;"><div style="text-align: center;">表 5-23 电磁波参数</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>波源</td><td style='text-align: center; word-wrap: break-word;'>中心频点(Mhz)</td><td style='text-align: center; word-wrap: break-word;'>带宽 (Mhz)</td><td style='text-align: center; word-wrap: break-word;'>功率强度(dBm)</td><td style='text-align: center; word-wrap: break-word;'>高斯滤波参数</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>红方广播源</td><td style='text-align: center; word-wrap: break-word;'>433.2</td><td style='text-align: center; word-wrap: break-word;'>0.54</td><td style='text-align: center; word-wrap: break-word;'>-60</td><td style='text-align: center; word-wrap: break-word;'>SPS:47,BT:0.35,Sample Rate:1M,</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>Sensitivity:1.5628 rad/sample</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>红方一级干扰源</td><td style='text-align: center; word-wrap: break-word;'>432.2</td><td style='text-align: center; word-wrap: break-word;'>0.94</td><td style='text-align: center; word-wrap: break-word;'>-10</td><td style='text-align: center; word-wrap: break-word;'>SPS:47,BT:0.35,Sample Rate:1M,\nSensitivity:2.8194 rad/sample</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>红方二级干扰源</td><td style='text-align: center; word-wrap: break-word;'>432.5</td><td style='text-align: center; word-wrap: break-word;'>0.86</td><td style='text-align: center; word-wrap: break-word;'>-10</td><td style='text-align: center; word-wrap: break-word;'>SPS:47,BT:0.35,Sample Rate:1M,\nSensitivity:2.5681 rad/sample</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>红方三级干扰源</td><td style='text-align: center; word-wrap: break-word;'>432.8</td><td style='text-align: center; word-wrap: break-word;'>0.25</td><td style='text-align: center; word-wrap: break-word;'>-10</td><td style='text-align: center; word-wrap: break-word;'>SPS:47,BT:0.35,Sample Rate:1M,\nSensitivity:0.6517 rad/sample</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>蓝方广播源</td><td style='text-align: center; word-wrap: break-word;'>433.92</td><td style='text-align: center; word-wrap: break-word;'>0.54</td><td style='text-align: center; word-wrap: break-word;'>-60</td><td style='text-align: center; word-wrap: break-word;'>SPS:47,BT:0.35,Sample Rate:1M,\nSensitivity: 1.5628 rad/sample</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>蓝方一级干扰源</td><td style='text-align: center; word-wrap: break-word;'>434.92</td><td style='text-align: center; word-wrap: break-word;'>0.94</td><td style='text-align: center; word-wrap: break-word;'>-10</td><td style='text-align: center; word-wrap: break-word;'>SPS:47,BT:0.35,Sample Rate:1M,\nSensitivity: 2.8194 rad/sample</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>蓝方二级干扰源</td><td style='text-align: center; word-wrap: break-word;'>434.62</td><td style='text-align: center; word-wrap: break-word;'>0.86</td><td style='text-align: center; word-wrap: break-word;'>-10</td><td style='text-align: center; word-wrap: break-word;'>SPS:47,BT:0.35,Sample Rate:1M,\nSensitivity: 2.5681 rad/sample</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>蓝方三级干扰源</td><td style='text-align: center; word-wrap: break-word;'>434.32</td><td style='text-align: center; word-wrap: break-word;'>0.25</td><td style='text-align: center; word-wrap: break-word;'>-10</td><td style='text-align: center; word-wrap: break-word;'>SPS:47,BT:0.35,Sample Rate:1M,\nSensitivity: 0.6517 rad/sample</td></tr></table>





##### 参数之间关系：

 $$ \mathrm{SPS}( 每符号采样数 )\quad\mathrm{Sample~Rate}/\mathrm{Symbol~Rate} $$ 

 $$ \mathrm{Sample~Rate~( 采样率 )}=1\mathrm{M},\mathrm{ 采样率是指每秒采样数 } $$ 

 $$  Symbol~Rate\ ( 符号率 )= 波特率 = 比特率 \ (2FSK~ 下降符号 ~1bit) $$ 

 $$  BT\ ( 高斯滤波器带宽时间积 )=0.35 $$ 

 $$  Sensitivity( 调频灵敏度 )=2*pi*\Delta f/Sample Rate( 单位：rad/sample) $$ 

频偏 $ \Delta f $ = signal_bandwidth / 2 - Sample Rate / SPS
带宽 B = signal_bandwidth （PlutoSDR RF 滤波器带宽）
详细频谱分布，空口帧结构，时域特征等信息，可参阅“附录1 雷达信息波特性”。
信息波将包含对方的以下信息：
各机器人位置
各机器人血量
各机器人剩余发弹量
各机器人当前持有的增益
队伍剩余经济
队伍总经济
对方各增益点被占领状态

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//98407028-77d6-48ba-890e-9ce040283ace/markdown_0/imgs/img_in_image_box_123_722_165_763.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A57Z%2F-1%2F%2F611b73f3ad4cc35db0e3fd59054c7c3d22916ce7af6aad9287a7b9be98612652" alt="Image" width="3%" /></div>


具体通信协议结构，请参阅：《RoboMaster 2026 机甲大师高校系列赛通信协议》。

干扰波不含具体信息，但含有一个对方自定义的6位（数字字母组合）密钥，开局和对应方干扰波难度变化时，密钥重置为随机值。

开局，双方干扰波默认均为一级难度。

雷达可以解析该密钥并发送给赛事引擎服务器，若解析成功，则后续对方干扰波解析难度提升1级，即己方雷达基座放置的干扰源难度提升1级。当对方干扰波难度高于己方，对方雷达对己方机器人即使准确标记，也不会产生易伤或积累“双倍易伤”进度。

#### 5.6.7 能量机制

每周比赛中，每台英雄、步兵、哨兵机器人各具有20000的初始底盘能量和40000的底盘能量上限。在底盘能量消耗至0后，机器人将进入“节能”状态。处于“节能”状态下的机器人，其底盘功率上限基础值将变为35W。在底盘能量大于等于25000时，机器人底盘功率上限基础值将变为对应性能体系和等级底盘功率上限基础值的125%，最高不会超过200W。

##### 底盘能量的消耗

电源管理模块 “Chassis” 接口每输出 1J 能量，底盘能量减少 1。底盘能量不会变为负值。

##### 底盘能量的补充

占领补给区增益点时，机器人可以通过无线充电补充底盘能量。

在超级电容管理模块接口（输入）正在向超级电容传输能量时，超级电容管理模块接口（输入）与电源管理模块 Chassis 接口的输出能量之差每达到 1J，底盘能量增加 8。

### 5.7 自定义客户端

自定义客户端是参赛队伍自制的一套多用途设备，用于接收裁判系统赛事引擎服务器发送的比赛相关信息与机器人图传画面，并向赛事引擎服务器发送赛事专用交互指令，以拓展人机交互可能性。

典型的自定义客户端可由一个显示设备、一个运算平台（包括存储器、控制器与运算器）及一组输入设备组成；也可采用一体化形式，例如：带有网口的手持平板设备。

示例：某队伍制作了自定义客户端，能够接收机器人图传并在自制显示器上呈现，同时叠加通过非官方链路显示的自制 UI，并通过自定义控制器或自制手柄对机器人进行操控。由此，该队伍无需使用官方裁判系统选手端亦能完成比赛。

自定义客户端可以通过操作间设置的 RJ45 接口有线接入赛事引擎服务器并收发相关内容，且可以自行与自定义控制器有线通信。

自定义客户端可以接收裁判系统选手端显示且己方可获取的赛事信息，例如：双方血量、己方经济、比赛剩余时间以及比赛关键事件的播报等。

自定义客户端可向裁判系统发送选手端所支持的赛事指令，例如：赛前选择性能体系、赛中兑换允许发弹量、以及发起空中支援等主动指令。

### 5.8 赛制及获胜条件

RMUC 2026 的正式比赛分为两个阶段：小组赛和淘汰赛。小组赛的赛制为 BO2 或 BO3，淘汰赛的赛制为 BO3 或 BO5。

单局比赛的胜负按下列编号的优先顺序逐项判定，直至得出最终结果：

1. 一局比赛时间耗尽或一方基地被击毁时，基地剩余血量高的一方获胜。

2. 一局比赛时间耗尽时，若双方基地剩余血量一致且前哨站均未被击毁过，前哨站剩余血量高的一方获胜。

3. 一局比赛时间耗尽时，若双方基地剩余血量一致，仅一方前哨站被击毁过，前哨站未被击毁过的一方获胜。

4. 一局比赛时间耗尽时，若双方基地剩余血量一致，前哨站血量一致或均被击毁过，全队攻击伤害高的一方获胜。

5. 一局比赛时间耗尽时，若双方基地剩余血量一致，前哨站血量一致或均被击毁过，全队攻击伤害一致，

全队总剩余血量高的一方获胜。

6. 若上述条件无法判定胜负，该局比赛视为平局。在 BO3 和 BO5 的对局中，出现平局则立即加赛一局，直至分出胜负。

## 6 比赛流程

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//98407028-77d6-48ba-890e-9ce040283ace/markdown_3/imgs/img_in_image_box_168_243_1048_1344.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A03%3A06Z%2F-1%2F%2Fa67c5c55533dfbaa3d279d92010d3c17c3429b195e1764d349a70fe0665fdf54" alt="Image" width="73%" /></div>


<div style="text-align: center;"><div style="text-align: center;">图 6-1 单场比赛流程图</div> </div>


### 6.1 赛前检录

预检录与适应性训练的检录结果，仅供参考，不作为正式比赛的检录通过依据。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//9b01633a-168c-4c9d-99a0-c33c9b5cf572/markdown_0/imgs/img_in_image_box_126_304_171_347.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A57Z%2F-1%2F%2F5285b921bbc976d9ca36aaa07b2520b59a52fe4e31d37b6db9c8faaa944f366f" alt="Image" width="3%" /></div>


正式比赛的检录结果仅对当场比赛生效。

通过检录仅证明检录时机器人满足检录通过标准，参赛队伍需自行保证机器人始终满足制作规范手册的要求。在检录时需向检录人员主动展示机器人的所有的功能。

为确保参赛队伍制作的机器人符合《RoboMaster 2026 机甲大师高校系列赛机器人制作规范手册》的要求，建议参赛队伍在每场比赛开始前 60 分钟到检录区进行检录，如参赛队伍在每场比赛开始前 55 分钟未开始检录则取消该队伍备用机器人上场资格，如参赛队伍在每场比赛开始前 50 分钟未开始检录则取消 1 台地面机器人上场资格，在比赛开始前 45 分钟未到达检录区的机器人停止进入检录区。检录流程如下：

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//9b01633a-168c-4c9d-99a0-c33c9b5cf572/markdown_0/imgs/img_in_image_box_164_620_1024_1086.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A58Z%2F-1%2F%2Fb3ce27f5047a5e4a3610bbb9ecf4cef9de8160985222617b1a22bac58d95762c" alt="Image" width="72%" /></div>


<div style="text-align: center;"><div style="text-align: center;">图 6-2 赛前检录流程图</div> </div>


##### 备用机器人规定如下：

预检录时，每支队伍至多可以携带10台机器人进行登记注册以及预检录，在同一个赛事阶段的后续比赛过程中，参赛队伍的机器人和备用机器人均需在登记注册名单内，且同一个赛事阶段过程中不可进行更换。注册机器人使用唯一特殊标识对机器人主体结构进行标记（标识方式包括不限于：防拆标签、激光打标，具体实现形式以现场为准），在后续的比赛检录过程中会对标识进行识别；如机器人在比赛期间需进行维护会对机器人唯一特殊标识产生影响，需在指定渠道提交相关变动信息。

复活赛结束后，机器人名单允许重新注册，具体时间安排以组委会最新通知为准。

每场比赛，每支参赛队伍至多可以携带2台备用机器人、10个自定义控制器、10个自定义客户端、2个无线充电装置（发射端）；无论备用机器人是否为飞镖系统，BO2和BO3赛制的一场比赛至多可以携带4枚备用飞镖，BO5赛制的一场比赛至多可以携带8枚备用飞镖。

赛前检录时，参赛队伍需声明己方所携带的备用机器人类型。备用的英雄、工程机器人需在检录区贴好装甲贴纸，当备用机器人需要作为步兵或哨兵机器人上场时，场地人员需及时向裁判领取相应的装甲贴纸。装甲贴纸的粘贴需遵循《RoboMaster 2026 机甲大师高校系列赛机器人制作规范手册》的规定。

每支参赛队伍至多可借用2台备用机器人的裁判系统。

### 6.2 候场

参赛队伍需在每场比赛开始前至少10分钟到达候场区。候场区工作人员将核查参赛机器人的PASS卡和场地人员的信息。

每支队伍的场地人员数量限制如下：

1 名指导老师。

2 名战队指导。

22名正式队员/梯队队员，其中梯队队员不能超过2名。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//9b01633a-168c-4c9d-99a0-c33c9b5cf572/markdown_1/imgs/img_in_image_box_133_895_175_937.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A03%3A01Z%2F-1%2F%2Ff1e49e19d1fb74f3036c711ff4117385e59b2948a13251f265acaa3a791488bf" alt="Image" width="3%" /></div>


2026 赛季场地人员数量增加，因此不再额外设置老队员以及宣传人员入场活动。

场地人员中需有1人佩戴队长指定标识，履行队长职能。参赛队伍进入候场区后，如需维修机器人，需获得裁判许可。只有当候场区工作人员撕除机器人上的PASS卡后，机器人方可离开候场区进行维修。完成维修后，机器人需重新到检录区进行检录，再次通过赛前检录才可返回候场区。如因此耽误时间导致未按时到达候场区，机器人不能上场比赛，后果由参赛队伍承担。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//9b01633a-168c-4c9d-99a0-c33c9b5cf572/markdown_1/imgs/img_in_image_box_128_1167_173_1214.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A03%3A02Z%2F-1%2F%2F62551a71c66c88436e302eb3f36bec2191589c491fddf66577c18b56a09cba98" alt="Image" width="3%" /></div>


队长指定标识：任一佩戴队长指定标识的场地人员在比赛期间履行队长职能。队长需把控队伍比赛流程，确认成绩、申诉等。

参赛队伍从候场区发往赛场后，进入赛场的等候区放置机器人。裁判批准后，参赛队伍携带机器人到达战场入口处待命。裁判根据比赛流程，开门并引导队员入场。开门的同时启动三分钟准备阶段的倒计时。

### 6.3 三分钟准备阶段

在 BO5 赛制比赛的第二局比赛和第四局比赛结束后，双方队伍有 10 分钟时间调试机器人。10 分钟时间结束后立即进入下一局比赛的三分钟准备阶段。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//9b01633a-168c-4c9d-99a0-c33c9b5cf572/markdown_2/imgs/img_in_image_box_127_323_172_368.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A03%3A05Z%2F-1%2F%2F18829d7ea8f808ff4bd96d684b6b68a303bf0b30e7f0bb13e5d64100a9fd2976" alt="Image" width="3%" /></div>


参赛队伍抵达赛场时，可在指定位置领取该场所需的所有42mm发光弹丸。关于弹丸领取数量限制，请参阅“4.6.2弹丸”，例如：BO3赛制可一次性领取300颗42mm发光弹丸。

在上一场比赛结束且雷达已撤出雷达基座后，参赛队伍即可将雷达提前布置于雷达基座上。

三分钟准备阶段内，场地人员需将机器人置于各自初始区域，检查机器人的裁判系统是否正常运行，为机器人预装弹丸，为飞镖系统装载飞镖，将雷达布置于雷达基座上，将安全绳连接在空中机器人上。场地人员可维修机器人或更换其等效部件，但需满足规范文件要求。场地人员需在己方机器人初始区域附近调试机器人，每支队伍仅允许一名场地人员离开初始区域配合调试，但不可越过中央高地。初始区域如下图所示：

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//9b01633a-168c-4c9d-99a0-c33c9b5cf572/markdown_2/imgs/img_in_image_box_155_710_1040_1229.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A03%3A06Z%2F-1%2F%2F935e4326f011273f2eaa6d4dd8b9e56f4561f6f0eba3f983d19d871068156abb" alt="Image" width="74%" /></div>


<div style="text-align: center;"><div style="text-align: center;">[1] 红方停机坪及其初始区域附近</div> </div>


<div style="text-align: center;"><div style="text-align: center;">[3] 蓝方停机坪及其初始区域附近</div> </div>


<div style="text-align: center;"><div style="text-align: center;">[2] 红方基地及其初始区域附近</div> </div>


<div style="text-align: center;"><div style="text-align: center;">[4] 蓝方基地及其初始区域附近</div> </div>


<div style="text-align: center;"><div style="text-align: center;">图 6-3 准备阶段调试区域示意图</div> </div>


等效部件：相同材质、形态、功能的标准模组或零件，如同型号电机、自制摩擦轮模组等。承载机器人机体的主要结构不可作为等效部件被替换，如机器人的底盘、空中机器人的机体等。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//9b01633a-168c-4c9d-99a0-c33c9b5cf572/markdown_3/imgs/img_in_image_box_127_254_172_299.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A03%3A08Z%2F-1%2F%2F404946b098380cbdd01d6ca3a4a7a99acff512dca673081dba56ed1221047e94" alt="Image" width="3%" /></div>


若“等效部件”包含裁判系统模块，参赛队伍需自行保证裁判系统机载端模块可以正常使用（包括版本号、传感器校准、安装规范等）。当“等效部件”中裁判系统机载端模块出现异常时，后果需自行承担，且不会触发官方技术暂停。

三分钟准备阶段还剩1分30秒时，建议操作手进入操作间完成键盘和鼠标（均可自带）的调试，接入操作间电脑的USB键盘和鼠标，应为具备合法资质的正规厂商生产，并符合USB HID协议规范。检查确认机器人操控以及官方设备运行正常。若官方设备无法正常运行，场地人员需在三分钟准备阶段还剩15秒前提出，否则裁判不给予技术暂停。三分钟准备阶段期间，操作间除上场机器人对应的操作手及云台手外，至多额外允许1人进入操作间进行赛前战术部署，在三分钟准备阶段结束前，非上场机器人对应的操作手和云台手外的人员必须离开操作间。

三分钟准备阶段剩余30秒时，战场内所有机器人需上电，战场内人员有序离场；三分钟准备阶段剩余15秒时仍未上电的机器人需搬离战场。三分钟准备阶段结束后，场地人员需将哨兵机器人、雷达的遥控器放置于战场入口或操作间入口的指定区域。

#### 6.3.1 官方技术暂停

在三分钟准备阶段内，当裁判系统或官方设备等发生故障或机器人需要临时检录时（故障情况如下表所示），主裁判可以发起官方技术暂停，暂停倒计时。暂停发起时间由主裁判视情况而定。

官方技术暂停期间，场地人员需按照裁判要求配合排除裁判系统或官方设备相关故障，不可以维修其它故障。若裁判系统发生故障需进行更换，需遵循《RoboMaster 2026 机甲大师高校系列赛机器人制作规范手册》中更换裁判系统机载端的时间限制。当裁判系统或官方设备相关故障被排除、主裁判恢复倒计时后，场地人员需遵循三分钟准备阶段的规范，在规定的时间点离开战场。

<div style="text-align: center;"><div style="text-align: center;">表 6-1 故障情况</div> </div>




<table border="1" style="margin: auto; word-wrap: break-word;"><tr><td style="text-align: center; word-wrap: break-word;">条例</td><td style="text-align: center; word-wrap: break-word;">描述</td></tr><tr><td style="text-align: center; word-wrap: break-word;">1</td><td style="text-align: center; word-wrap: break-word;">操作间官方设备发生故障，战场内关键比赛道具出现结构性损坏或功能异常。</td></tr><tr><td style="text-align: center; word-wrap: break-word;">2</td><td style="text-align: center; word-wrap: break-word;">首局三分钟准备阶段内，裁判系统机载端模块出现故障，例如：装甲模块损坏、测速模块离线等情况。</td></tr><tr><td style="text-align: center; word-wrap: break-word;">3</td><td style="text-align: center; word-wrap: break-word;">三分钟准备阶段内，裁判系统主控无法连接服务器，或者机器人无法正常将图像传回操作间。</td></tr><tr><td style="text-align: center; word-wrap: break-word;">4</td><td style="text-align: center; word-wrap: break-word;">其他由主裁判判定需要官方技术暂停的情况。</td></tr></table>




由于无法判断故障情况是裁判系统模块本身出现故障，还是因为参赛机器人电路、结构设计的缺陷所致，或因前期比赛中机器人对抗所致，除上述条例3情况以外，常规战损不触发官方技术暂停，裁判会提供备用的裁判系统模块。参赛队伍可以申请“参赛队伍技术暂停”对机器人进行维修。

如果经裁判排查，上述条例2、3所述的故障情况是参赛队伍原因导致，裁判会说明情况，并结束官方技术暂停。

#### 6.3.2 参赛队伍技术暂停

若机器人的机械结构、软件系统、带入操作间的键盘鼠标等设备出现故障，参赛队伍仅可在三分钟准备阶段的十五秒倒计时之前，由场地人员向战场或操作间内的裁判申请“参赛队伍技术暂停”，并说明申请理由。参赛队伍技术暂停申请一旦发起并传达至主裁判，此次技术暂停不可撤销或修改。

参赛队伍技术暂停经主裁判确认后，无论由哪方发起，裁判将同时通知双方参赛队伍。参赛队伍技术暂停时间内，双方队伍均可正常继续调试、维修机器人。

主裁判确认双方队伍均准备就绪后，可提前结束技术暂停。即使参赛队伍没有进入战场或提前结束技术暂停，消耗的机会依然是参赛队伍申请时声明的时间对应的机会。

为保证后续赛程按时进行，同一个三分钟准备阶段双方一共只能发起1次参赛队伍技术暂停，遵循先到先得的原则。赛后成绩确认表上会记录比赛中是否有技术暂停机会被消耗。

同一赛事阶段的不同赛程阶段中，参赛队伍技术暂停的安排如下所示：

<div style="text-align: center;"><div style="text-align: center;">表 6-2 复活赛技术暂停安排</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>赛程阶段</td><td style='text-align: center; word-wrap: break-word;'>安排</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>小组赛</td><td style='text-align: center; word-wrap: break-word;'>1 次两分钟技术暂停，若同一赛事阶段的上个赛程阶段的技术暂停机会未使用，可在同一赛事阶段中可继续使用</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>淘汰赛</td><td style='text-align: center; word-wrap: break-word;'>1 次三分钟技术暂停</td></tr></table>

<div style="text-align: center;"><div style="text-align: center;">表 6-3 全国赛技术暂停安排</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>赛程阶段</td><td style='text-align: center; word-wrap: break-word;'>安排</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>小组赛</td><td style='text-align: center; word-wrap: break-word;'>2 次两分钟技术暂停，若同一赛事阶段的上个赛程阶段的技术暂停机会未使</td></tr><tr><td style='text-align: center; word-wrap: break-word;'></td><td style='text-align: center; word-wrap: break-word;'>用，可在同一赛事阶段中可继续使用</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>淘汰赛</td><td style='text-align: center; word-wrap: break-word;'>1 次三分钟技术暂停</td></tr></table>





### 6.4 十五秒裁判系统自检阶段

三分钟准备阶段结束后，比赛进入十五秒裁判系统自检阶段。自检过程中，裁判系统服务器会自动检测裁判系统选手端连接状态、机器人裁判系统模块状态、场地道具状态，并且重置所有机器人血量，确保比赛开始时所有机器人为满血状态。

### 6.5 五秒裁判系统自检阶段

十五秒裁判系统自检阶段结束后，比赛进入五秒倒计时。此时，裁判系统选手端将不响应机器人控制指令（包括自定义控制器、自定义客户端），倒计时结束后裁判系统选手端恢复响应机器人控制指令，比赛立即开始。

### 6.6 七分钟比赛阶段

七分钟比赛阶段，两支队伍的机器人在核心比赛场地（战场）内进行射击对抗。

### 6.7 比赛结束

当一局比赛时间耗尽或一方队伍提前触发获胜条件时，一局比赛结束。获胜条件参阅“5.8 赛制及获胜条件”。当场比赛决出胜负或结束所有局次后，一场比赛结束。

### 6.8 成绩确认

一场比赛中，裁判会在成绩确认表上记录每一局比赛的主要判罚情况、比赛结束时的关键结算信息、胜负情况和参赛队伍技术暂停机会使用情况等。

队长需在一场比赛结束后5分钟内签字确认比赛成绩。如果队长在5分钟内未签字确认成绩，也未提出申诉，视为确认比赛成绩。

### 6.9 退场

一场比赛结束后，参赛队伍需将机器人断电搬离战场，并前往退弹区进行退弹。在退弹区，参赛队伍需按照工作人员指引，主动归还相关物资，清空机器人装载的弹丸，主动归还所有比赛使用的弹丸。

## 7 违规与判罚

为保证比赛的公平性、严肃比赛纪律，参赛队伍、参赛人员、机器人需严格遵循比赛规则。如有违规，裁判将对违规行为给予相应的判罚。在比赛正式开始前发出的部分违规判罚会在比赛正式开始后执行。比赛中的重大判罚和所有申诉会进行公示。

本章所有违规条例对应的判罚由主裁判根据比赛实际情况判定。若比赛过程中出现影响比赛公平性但是判罚细则和严重违规未涉及的情况，由主裁判根据实际情况进行判定。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//b52d25fd-9a77-4131-9a6d-f5f05d88918b/markdown_3/imgs/img_in_image_box_135_487_180_531.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A05%3A00Z%2F-1%2F%2F3a79e10de45fadb5d9ce427504a152d891904119970b5e40f5247f1871c2a693" alt="Image" width="3%" /></div>


一方行为使对方直接产生违规行为，不视为对方违规，但对方需及时终止违规行为。

### 7.1 判罚体系

#### 7.1.1 判罚方式

赛事期间，裁判系统或裁判将对不符合赛事规则的参赛人员和机器人作出判罚。判罚方式如下：

<div style="text-align: center;"><div style="text-align: center;">表 7-1 判罚方式</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>判罚方式</td><td style='text-align: center; word-wrap: break-word;'>说明</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>裁判系统自动判罚</td><td style='text-align: center; word-wrap: break-word;'>“5.1 扣血与超限惩罚机制”中除攻击伤害或撞击、判罚伤害外均属于裁判系统自动判罚。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>裁判系统人工判罚</td><td style='text-align: center; word-wrap: break-word;'>裁判操作服务器对机器人的违规行为发出的判罚。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>裁判人工判罚</td><td style='text-align: center; word-wrap: break-word;'>适用于无法使用裁判系统进行判罚的场景，如口头警告、取消比赛资格等。</td></tr></table>

#### 7.1.2 判罚类型

比赛期间的人工判罚类型如下表所示：

<div style="text-align: center;"><div style="text-align: center;">表 7-2 判罚类型</div> </div>




<table border="1" style="margin: auto; word-wrap: break-word;"><tr><td style="text-align: center; word-wrap: break-word;">判罚类型</td><td style="text-align: center; word-wrap: break-word;">说明</td></tr><tr><td style="text-align: center; word-wrap: break-word;">口头警告</td><td style="text-align: center; word-wrap: break-word;">口头警示</td></tr><tr><td style="text-align: center; word-wrap: break-word;">黄牌警告</td><td style="text-align: center; word-wrap: break-word;">● 一方黄牌：</td></tr><tr><td style="text-align: center; word-wrap: break-word;"></td><td style="text-align: center; word-wrap: break-word;">➢ 若违规机器人为哨兵机器人，则其底盘断电 2 秒，其它机器人操作界面被遮挡 2 秒。\n➢ 若违规机器人不为哨兵机器人，则其操作界面被遮挡 5 秒，其它机器人操作界面被遮挡 2 秒。\n➢ 裁判系统自动扣除违规机器人当前上限血量的 15%，其余存活机器人被扣除当前上限血量的 5%。机器人每次收到黄牌警告后的 30 秒内，若再次收到黄牌警告，则扣除当前上限血量的百分比是前一次的 2 倍，其余存活机器人被扣除当前上限血量的 5%。\n➢ 每局比赛中，工程机器人累计收到 2 次黄牌警告，将同时收到红牌警告；其余每台机器人累计收到 3 次黄牌警告时，将同时收到红牌警告。\n● 双方黄牌：\n所有操作手操作界面被遮挡 2 秒，所有机器人被扣除上限血量的 5%，不计入单台机器人累计黄牌次数。\n● 若连续收到黄牌警告，则操作界面被遮挡时间叠加计算，且 30 秒计时重置。\n● 若机器人剩余血量小于等于判罚需扣除的血量，则机器人血量降为 1。\n● 因违规判罚导致的底盘断电、操作界面遮挡等时长与比赛机制相互独立，不叠加计算。\n● 因黄牌警告导致界面遮挡时，图传画面、小地图、自定义 UI 均不可使用。</td></tr><tr><td style="text-align: center; word-wrap: break-word;">红牌警告（罚下）</td><td style="text-align: center; word-wrap: break-word;">● 罚下机器人：\n➢ 若在进入十五秒裁判系统自检阶段前罚下机器人，则违规机器人不允许上场，需搬离战场，且当场所有局比赛中不允许有其他机器人进行替补。\n➢ 若在十五秒裁判系统自检阶段罚下机器人，则红牌警告将在比赛开始后发出。\n➢ 若在比赛中罚下空中机器人，则空中机器人发射机构断电，图传连接被断开，飞手不可再次起浆，云台手无法呼叫空中支援；若空中机器人处于飞</td></tr><tr><td style="text-align: center; word-wrap: break-word;"></td><td style="text-align: center; word-wrap: break-word;">行状态，飞手需立即将其降落至指定位置。</td></tr><tr><td style="text-align: center; word-wrap: break-word;"></td><td style="text-align: center; word-wrap: break-word;">若在比赛中罚下飞镖系统，则飞镖发射按键被立即屏蔽，飞镖发射站闸门不可被开启，若闸门已经开启，则会被立即关闭。</td></tr><tr><td style="text-align: center; word-wrap: break-word;"></td><td style="text-align: center; word-wrap: break-word;">若在比赛中罚下雷达，则其激光发射装置及其执行机构将被断电且雷达的多机通信将被断开（仅能单向接收，不再能发送）。</td></tr><tr><td style="text-align: center; word-wrap: break-word;"></td><td style="text-align: center; word-wrap: break-word;">若在比赛中罚下除空中机器人、飞镖和雷达外的其它机器人，机器人血量立即变为0，图传画面变为黑白。</td></tr><tr><td style="text-align: center; word-wrap: break-word;"></td><td style="text-align: center; word-wrap: break-word;">罚下附属设备：对应设备不允许上场。</td></tr><tr><td style="text-align: center; word-wrap: break-word;"></td><td style="text-align: center; word-wrap: break-word;">罚下场地人员：裁判要求被罚下的场地人员立即离开赛场区域，且当场的所有局比赛中不允许有其它场地人员进行替补。若罚下操作手，所对应操作的机器人当局被罚下，且在当场所有局比赛都不允许上场，也不得有机器人进行替补；其中，若罚下云台手，空中机器人和飞镖系统均被罚下，且在当场所有局比赛均不允许上场，也不得有机器人进行替补。</td></tr><tr><td style="text-align: center; word-wrap: break-word;"></td><td style="text-align: center; word-wrap: break-word;">若对一局比赛发出判负处罚（以下称“当局判负”），具体细则如下：</td></tr><tr><td style="text-align: center; word-wrap: break-word;"></td><td style="text-align: center; word-wrap: break-word;">若七分钟比赛阶段前发出判负处罚（包含三分钟准备阶段和十五秒裁判系统自检阶段），违规方基地血量为0，违规方其余机器人血量为全满。另一方基地和机器人血量为全满。当局比赛时间视为1秒，两方全队总伤害均视为0。</td></tr><tr><td style="text-align: center; word-wrap: break-word;"></td><td style="text-align: center; word-wrap: break-word;">若七分钟比赛阶段发出判负处罚，当局比赛直接结束，违规方基地血量为0，违规方其余机器人血量以比赛结束时的血量为准，另一方基地和机器人血量以比赛结束时的血量为准。</td></tr><tr><td style="text-align: center; word-wrap: break-word;"></td><td style="text-align: center; word-wrap: break-word;">若七分钟比赛阶段结束后发出判负处罚，违规方基地血量为0，违规方其余机器人血量以比赛结束时的血量为准，另一方基地和机器人血量以比赛结束时的血量为准。</td></tr><tr><td style="text-align: center; word-wrap: break-word;"></td><td style="text-align: center; word-wrap: break-word;">若对一场比赛发出判负处罚（以下称“当场判负”），即对该场所有局比赛发出判负处罚，每局比赛的血量结算参考上述描述。</td></tr><tr><td style="text-align: center; word-wrap: break-word;">取消评奖资格</td><td style="text-align: center; word-wrap: break-word;">参赛人员被取消评奖资格。</td></tr><tr><td style="text-align: center; word-wrap: break-word;"></td><td style="text-align: center; word-wrap: break-word;">参赛队伍被取消评奖资格。</td></tr><tr><td style="text-align: center; word-wrap: break-word;">取消比赛资格</td><td style="text-align: center; word-wrap: break-word;">● 参赛人员被取消比赛资格和评奖资格。\n● 参赛队伍被取消比赛资格和评奖资格，保留本赛季队伍战绩，作为其他队伍晋级的参考依据。</td></tr></table>











### 7.2 判罚细则

本节介绍违规判罚细则。序号为 R# 规则明确指出了参赛队伍、参赛人员和参赛机器人需遵循的规则。

#### 7.2.1 人员

##### 7.2.1.1 通用规范

R1 参赛队伍需满足《RoboMaster 2026 机甲大师超级对抗赛参赛手册》的要求。

违规判罚：最高取消违规方的比赛资格。

R2 参赛人员及其行为不得干扰官方设备、赛事流程的正常运转或组委会人员的正常工作。

违规判罚：最高取消违规方的比赛资格。

R3 参赛队伍不得在比赛相关区域（包含但不限于备场区、检录区、候场区和赛场区等）自行架设无线设备或使用对讲机。

违规判罚：最高取消违规方的比赛资格。

R4 参赛队伍不得破坏官方设备（包括但不限于赛场区、候场区、备场区、检录区的设备）。违规判罚：最高取消违规方的比赛资格，并要求违规方照价赔偿。

R5 除因比赛需要而进入候场区、赛场区的场地人员，其它参赛人员无特殊原因，不得进入候场区和赛场区。

违规判罚：最高取消违规人员的比赛资格。

R6 因比赛需要已进入候场区或赛场区的场地人员未经裁判同意不得擅自离开候场区或赛场区，或更换场地人员。

违规判罚：违规人员本场比赛不得进入候场区和赛场区，最高取消违规人员的比赛资格。

R7 除在检录区进行预置的弹丸外，参赛队伍不得自行携带比赛使用的弹丸进入候场区或赛场区。

违规判罚：没收弹丸，最高取消违规人员的比赛资格。

R8 一场比赛结束后，场地人员需立即将机器人断电并搬离赛场，在退弹区清空机器人内部的弹丸。

违规判罚：违规机器人将被扣留在退弹区，直至清空弹丸。

R9 一场比赛结束后，场地人员需在退弹区归还所有比赛使用的弹丸。

违规判罚：没收弹丸且取消违规人员在当前赛区后续场次进入赛场的资格。最高取消违规人员的比赛资格。

R10 除突发情况外，参赛队伍需在每场比赛开始前至少 55 分钟到达检录区进行赛前检录，且队伍需在每场比赛开始前 10 分钟到达候场并准备就绪。

违规判罚：最高当场判负。

R11 未经裁判许可，机器人通过检录后至当场比赛结束前，不得在非战场区域开电调试或维修机器人。

违规判罚：最高当场判负。

R12 每支队伍进入备场区、检录区、候场区、赛场区等指定区域的人员身份和数量需要符合要求。

违规判罚：最高取消违规方的比赛资格。

R13 场地人员需佩戴对应标识，且标识不被遮挡。其中，需有一人佩戴队长指定标识。

违规判罚：最高取消违规人员的比赛资格。

R14 未经裁判许可，进入赛场的场地人员不得与外界进行任何通信。

违规判罚：最高取消违规人员的比赛资格。

R15除雷达、放置在战场内的无线充电装置外，场地人员不得在赛场区域使用官方设备电源给自备设备供电，但可自行携带电源。

违规判罚：最高取消违规人员的比赛资格。

R16除特殊情况外，场地人员禁止穿拖鞋进入赛场。

违规判罚：最高对违规人员发出红牌警告。

R17 在申诉过程中，申诉方需提供有效的证据或依据的规范文件中相关条例。

违规判罚：最高取消违规人员的比赛资格。

R18队长负有管理职责，在备赛、参赛过程中须确保：

参赛机器人需通过机器人整机成品及开源机器人使用规范审查工作；

战队指导、梯队队员及其他无获奖资格人员，在参赛过程中不得出现违规行为；

及时制止其他违规行为。

违规判罚：根据违规情况确定队长的管理责任，最高取消违规人员的比赛资格。

##### 7.2.1.2 战场规范

R19 场地人员进入战场内需佩戴护目镜。

违规判罚：口头警告同时将违规人员罚出战场。若警告无效，对违规人员发出红牌警告。

R20 官方技术暂停期间，场地人员不可维修除裁判系统相关模块外的其他故障。

违规判罚：口头警告。若警告无效，对违规人员发出红牌警告。

R21 三分钟准备阶段结束后，场地人员需回到战场外的指定区域。比赛过程中，未经裁判许可，场地人员不得离开该区域。

违规判罚：口头警告。若警告无效，对违规人员发出红牌警告。

R22 三分钟准备阶段剩余 30 秒后参赛队员禁止在赛场内继续调试机器人。

违规判罚：口头警告。若警告无效，在比赛开始后给予违规机器人红牌警告。

R23 三分钟准备阶段结束后，哨兵机器人、雷达的遥控器需放置于战场入口或操作间入口的指定区域，其他机器人的遥控器需放置于操作间内或战场入口指定位置。

违规判罚：若在七分钟比赛阶段前，口头警告，若警告无效，对违规机器人发出红牌警告；若在七分钟比赛阶段，对违规机器人发出红牌警告。

R24 五秒倒计时开始后，场地人员不得操作位于操作间外的上场机器人对应的遥控器。

违规判罚：对违规机器人发出红牌警告，最高当局判负。

R25 场地人员需确保己方机器人安全运转，不会对赛场中任何人员和设备造成伤害。

违规判罚：违规方需承担相应责任。

R26 比赛过程中，禁止通过飞镖检测窗口进行机器人维修。

违规判罚：对违规机器人及违规人员发出红牌警告。

##### 7.2.1.3 操作间规范

R27 三分钟准备阶段内，操作间除上场机器人对应的操作手及云台手外至多允许多进入1人，且在三分钟准备阶段结束前非上场机器人对应的操作手和云台手外的人员须离开操作间。

违规判罚：口头警告。若警告无效，对违规人员发出红牌警告。

R28 未经裁判许可，十五秒裁判系统自检阶段内及七分钟比赛阶段中，操作手需位于对应操作间内，操作对应的机器人的控制设备，佩戴对应的耳机，三分钟准备阶段结束后不得移动位置。

违规判罚：口头警告。若警告无效，对违规人员发出红牌警告。

R29 操作手在五秒倒计时前未到达操作间，或在七分钟比赛阶段离开操作间。

违规判罚：对违规人员发出红牌警告。

R30 七分钟比赛阶段中，云台手可以同时配置空中机器人的云台遥控器、自定义控制器和飞镖的遥控器，飞手仅可配置一个遥控器，除此之外，每位操作手需按照对应机器人控制方式的要求配置控制设备及自定义客户端。

违规判罚：口头警告。若警告无效，对违规人员发出红牌警告。

R31 禁止在操作间内使用自带的耳机或电脑（除自定义客户端外）。

违规判罚：口头警告。若警告无效，当局判负。

R32 操作间提供 3 个 USB Type-A 母头接口，禁止扩展。非正规厂商生产、自制、改装或不符合 USB HID 协议规范的 USB 键盘和鼠标不得接入操作间电脑。

违规判罚：口头警告并禁止违规设备使用。若警告无效，对违规人员发出红牌警告。

R33 比赛过程中，不可与操作间外进行通信。

违规判罚：口头警告。若警告无效，当局判负。

R34 比赛过程中，操控空中机器人的飞手需获得飞手资格并佩戴对应标识。

违规判罚：对违规人员发出红牌警告，最高取消违规方比赛资格。

#### 7.2.2 机器人

##### 7.2.2.1 通用规范

R35 上场比赛的机器人及相关设备需通过赛前检录。

违规判罚：当局判负。

R36 一场比赛的首局，机器人需要满足最低上场阵容。

违规判罚：当场判负。

R37 机器人需符合《RoboMaster 2026 机甲大师高校系列赛机器人制作规范手册》要求。

违规判罚：最高取消违规方的比赛资格。

组委会将不定期抽查机器人。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//45397596-3428-48c9-814d-e46fb39cf3e6/markdown_1/imgs/img_in_image_box_169_1389_215_1433.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A59Z%2F-1%2F%2Fccdb8bb8bff07f9f8bd6bdc6ccefc2c440e66b8d24dcc6656c6c4310563f8d51" alt="Image" width="3%" /></div>


若举报机器人不符合机器人制作规范，举报者需提供相应证据。

在比赛过程中，若定位模块、测速模块的安装不符合要求，该局视为对应模块离线。

R38 在发生争议时，参赛队伍有责任向组委会展示机器人机械、电路设计图纸以及相关代码文件，并回答相关技术咨询。

违规判罚：最高取消违规方的比赛资格。

R39 在十五秒裁判系统自检阶段前，机器人需粘贴符合规范文件的装甲贴纸。

违规判罚：口头警告。若警告无效，对违规机器人发出红牌警告。

R40 在候场区等待时，参赛人员不得擅自携带机器人离开候场区。

违规判罚：口头警告。若警告无效，对违规人员和机器人发出红牌警告，最高取消违规人员的比赛资格。

R41 机器人不得存在或出现包括但不限于短路、坠毁、冒烟、明火、零件掉落地面、气瓶爆炸等安全隐患；若存在或出现安全隐患，参赛人员需配合裁判执行相应操作。

违规判罚：清场前，场地人员需在裁判要求下解决安全问题，否则违规机器人不得上场。若在比赛过程中，口头警告，若警告无效，对违规人员或对违规机器人发出红牌警告。若安全隐患情节严重，主裁判按照“8异常情况”进行处理。

R42 任何机器人不得向场外持续发射弹丸。

违规判罚：口头警告。若警告无效，对违规机器人发出红牌警告。

R43飞镖系统不得向战场外发射飞镖。

违规判罚：对违规机器人发出红牌警告。

R44 三分钟准备阶段至清场前战场内的机器人不得离开对应的调试区域。清场后至十五秒裁判系统自检阶段和五秒倒计时阶段，战场内的机器人不得离开对应的初始区域。

违规判罚：最高对违规机器人发出红牌警告。

R45 三分钟准备阶段，若需发射弹丸，需将弹丸发射至清弹袋中。

违规判罚：最高对违规机器人发出红牌警告。

R46 三分钟准备阶段，机器人更换的模组或零件需满足“等效部件”的要求。

违规判罚：最高对违规机器人发出红牌警告。

##### 7.2.2.2 地面机器人

R47 比赛过程中，任何存活机器人不得使用自身结构遮挡自身的任意装甲模块，任何机器人不可遮挡己方其他存活机器人装甲模块超过 1 块。工程机器人在抓取或携带可移动道具时，允许被携带的可移动道具和相关自身结构遮挡其中 1 块自身装甲模块，且允许每次遮挡的装甲模块为不同的装甲模块，但不允许同时遮挡多块装甲模块。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//45397596-3428-48c9-814d-e46fb39cf3e6/markdown_3/imgs/img_in_image_box_169_173_215_221.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A03%3A04Z%2F-1%2F%2Fd433a79bcaa6d8468dce4fc506c32d4109616d2293af9a69550ac03dfc1a677f" alt="Image" width="3%" /></div>


英雄机器人、步兵机器人和哨兵机器人在携带可移动道具时，不允许遮挡自身装甲模块。

若被遮挡的装甲模块发生模块离线，则不视为违规。

违规判罚：如遮挡1块装甲模块，根据主观意图对违规方发出警告，若为主动遮挡，发生违规时发出黄牌警告并进行口头警告，若警告无效，则发出红牌警告；若为被动遮挡，发生违规时发出1次黄牌警告。如遮挡装甲模块数量大于1，发生违规时发出黄牌警告并进行口头警告，若警告无效，则发出红牌警告。

##### 7.2.2.3 空中机器人

R48 飞手使用的遥控器仅能用于空中机器人起飞、降落、校准等用于控制空中机器人机体的功能，不得用于其他用途。

违规判罚：最高取消违规方的比赛资格。

R49 三分钟准备阶段内，场地人员可在停机坪附近调试空中机器人，但不得启动桨叶。

违规判罚：最高对违规人员和违规机器人发出红牌警告。

R50 安全绳的挂钩需连接在空中机器人竖直刚性保护杆的刚性圆环上。

违规判罚：对违规机器人发出红牌警告。在同场次其他局次和本赛事阶段后续所有场次，空中机器人不得上场。

R51 比赛过程中，空中机器人最低点距离场地地面的距离不得小于 1.5m，且空中机器人云台发射机构所搭载的 17mm 测速模块任何部分不可超过飞行区场地围挡最高处。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//45397596-3428-48c9-814d-e46fb39cf3e6/markdown_3/imgs/img_in_image_box_145_989_1039_1225.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A03%3A05Z%2F-1%2F%2F7ad968d266ecdd1e7712983bb24272e79a3b379e938a0c8495357a00e7fbbdbd" alt="Image" width="75%" /></div>


<div style="text-align: center;"><div style="text-align: center;">[3] 最低限高 [4] 围挡最高处 [5] 围挡</div> </div>


<div style="text-align: center;"><div style="text-align: center;">图 7-1 飞行高度限制示意图</div> </div>


违规判罚：对飞手发出手势或口头警告，提醒飞手调整飞行高度。若警告无效，对违规机器人发出红牌警告，并在同一场次的其它局比赛中不得上场。

R52 比赛过程中，空中机器人不得飞出战场外。

违规判罚：对违规机器人发出红牌警告，并取消飞手资格。在同场次其他局次该空中机器人不得上场。R53 比赛过程中，空中机器人与停机坪接触时禁止发射弹丸。

违规判罚：最高对违规机器人发出红牌警告。

R54 比赛过程中，若空中机器人出现故障，或因动力系统与供电系统设计不合理导致战损，该机器人需通过裁判检查、且主裁判确认无安全隐患的情况下才可继续上场。

违规判罚：对违规机器人发出红牌警告。在同一场次的其它局比赛中，该违规机器人不得上场。

如空中机器人坠落在战场内，裁判会根据实际情况将空中机器人回收至停机坪，回收过程中产生的影响，由参赛队伍自行承担。但也可能由于机器人结构损坏严重、安全绳挂钩脱落、比赛即将结束等原因不进行回收。

- 如空中机器人坠落在战场内，裁判会根据实际情况将空中机器人回收至停机坪，回收过程中产生的影响，由参赛队伍自行承担。但也可能由于机器人结构损坏严重、安全绳挂钩脱落、比赛即将结束等原因不进行回收。

因考虑安全问题，若空中机器人在比赛过程中出现飞行不稳定的情况，主裁判会将该空中机器人罚下，飞手应尽快将空中机器人降落并停桨，不得再操作该空中机器人。

##### 7.2.2.4 其他机器人

R55除在七分钟比赛阶段，飞镖系统不得处于待发射状态。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//dedc3249-151d-4f38-a40e-429e9afeb01a/markdown_0/imgs/img_in_image_box_169_826_217_875.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A51Z%2F-1%2F%2F4540b1c678197c52e951a8e94c5f6b39294e35f32e73517998bd39d2d58b4e4c" alt="Image" width="4%" /></div>


待发射状态：用于给飞镖提供初始动能的储能元件处于拉紧、充气、转动状态。储能元件包括但不限于皮筋、气缸、摩擦轮等。

违规判罚：口头警告，若警告无效，对违规机器人发出红牌警告。

#### 7.2.3 交互

##### 7.2.3.1 机器人交互

R56 一方机器人不得使用自身任意结构冲撞对方机器人。若战亡机器人造成关键移动路径的阻挡，可缓慢将其推开。

空中机器人在飞行时，地面机器人与空中机器人产生冲撞，违规机器人为空中机器人。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//dedc3249-151d-4f38-a40e-429e9afeb01a/markdown_0/imgs/img_in_image_box_169_1280_216_1325.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A51Z%2F-1%2F%2Fe8bb1bc8bcf0c8d1ed01215019f90fe4fa24920b312c7648578dde5100a0fc1e" alt="Image" width="3%" /></div>


空中机器人落在战场表面后或者回收过程中，地面机器人与空中机器人产生冲撞，违规机器人为地面机器人。

地面机器人与地面机器人产生冲撞，违规机器人为裁判判定的主动方。

违规判罚：根据主观意图及冲撞程度，对违规机器人发出警告。

<div style="text-align: center;"><div style="text-align: center;">表 7-3 冲撞违规判罚标准</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>违规等级</td><td style='text-align: center; word-wrap: break-word;'>说明</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>黄牌警告</td><td style='text-align: center; word-wrap: break-word;'>● 主动地产生正面、快速冲撞\n● 主动推动使对方机器人产生明显移动\n● 主动推动对方机器人阻碍其正常运动</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>红牌警告</td><td style='text-align: center; word-wrap: break-word;'>● 主动地产生正面、快速、反复或剧烈的冲撞\n● 主动推动使对方机器人产生较远距离的移动\n● 主动推动对方机器人严重阻碍其正常运动</td></tr></table>

若冲撞行为对对方机器人造成严重后果或影响比赛公平性，在同一赛事阶段的下一局比赛中，该违规机器人（仅针对机器人编号）不得上场，且不允许有其他机器人进行替补。

R57 一方机器人不得因主动干扰、阻挡或冲撞等行为致使自身的任意结构固连对方机器人（不可复活的机器人除外）。

违规判罚：从可判断为固连现象时开始计时，根据违规时长对违规机器人发出警告，违规大于10秒时发出第一次黄牌警告，随后每20秒发出1次黄牌警告，直至违规机器人被罚下。无论违规机器人是否处于存活状态，当违规时间大于90秒时，根据违规方行为的主观意图最高当局判负。

R58一方机器人不可主动攻击对方空中机器人、飞镖发射架、雷达、无线充电装置。

违规判罚：最高取消违规方的比赛资格。

R59 一方机器人及其行为均不可阻挡另一方机器人进入其补给区。

违规判罚：对违规机器人发出黄牌警告。若警告无效，对违规机器人发出红牌警告。

R60 机器人不可主动携带对方飞镖。

违规判罚：口头警告，若警告无效，对违规机器人发出红牌警告。

##### 7.2.3.2 机器人与场地道具交互

战场中设置了多处禁区。禁区空间包含地面及其竖直上空区域。机器人本体或其携带物（如可移动道具）只要接触或进入该空间范围，均判定为进入禁区。禁区范围如下图所示。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//dedc3249-151d-4f38-a40e-429e9afeb01a/markdown_2/imgs/img_in_image_box_184_342_1036_870.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A56Z%2F-1%2F%2F1d7354595125cc3ab41ec7880696d158694cc06a6f2c321f48e32cd544b3581b" alt="Image" width="71%" /></div>


<div style="text-align: center;"><div style="text-align: center;">[1] 补给禁区 [2] 装配禁区 [3] 公路禁区</div> </div>


<div style="text-align: center;"><div style="text-align: center;">[4] 基地禁区 [5] 停机坪禁区</div> </div>


<div style="text-align: center;"><div style="text-align: center;">图 7-2 战场禁区示意图</div> </div>


机器人与禁区的互动需遵守以下规则，否则视为违规进入禁区。

单方禁区：仅允许所属方机器人进入，禁止对方所有机器人进入。

双方禁区：禁止双方所有机器人进入。

<div style="text-align: center;"><div style="text-align: center;">表 7-4 战场禁区准入规则</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>禁区名称</td><td style='text-align: center; word-wrap: break-word;'>禁区属性</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>补给禁区</td><td style='text-align: center; word-wrap: break-word;'>单方禁区</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>装配禁区</td><td style='text-align: center; word-wrap: break-word;'>单方禁区</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>公路禁区</td><td style='text-align: center; word-wrap: break-word;'>双方禁区</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>基地禁区</td><td style='text-align: center; word-wrap: break-word;'>双方禁区</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>停机坪禁区</td><td style='text-align: center; word-wrap: break-word;'>单方禁区</td></tr></table>





R61 地面机器人不得违规进入基地禁区、公路禁区或停机坪禁区。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//dedc3249-151d-4f38-a40e-429e9afeb01a/markdown_3/imgs/img_in_image_box_166_486_211_531.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A59Z%2F-1%2F%2Fcd81bfa2ae40c79dbe4a22c9b7896fea9c54025bb3aa0fc35d720f91ad4d05f9" alt="Image" width="3%" /></div>


当机器人从飞坡坡底到坡顶完整经过 $ 17^{\circ} $坡后飞入公路禁区失去移动能力导致无法离开禁区不视为违规，其余情况均视为违规。

违规判罚：根据停留时长和违规行为的影响程度，对违规机器人发出警告。违规大于3秒时发出第一次黄牌警告，随后每10秒发出1次黄牌警告，直至违规机器人被罚下。若在禁区内停留导致对方机器人严重损坏，对违规机器人发出红牌警告。

R62 地面机器人不得违规进入补给禁区、装配禁区。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//dedc3249-151d-4f38-a40e-429e9afeb01a/markdown_3/imgs/img_in_image_box_169_782_215_829.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A59Z%2F-1%2F%2Fafc58c6e712bb37f9450b0dfb99e5c069cc10136ad11b6311151ceb43e083b3d" alt="Image" width="3%" /></div>


若机器人在任意禁区内处于战亡和被罚下时，裁判根据现场情况可将该机器人设置为临时激活状态，并引导该机器人操作手操作机器人离开禁区。

违规判罚：根据停留时长和违规行为的影响程度，对违规机器人发出警告。违规时长大于3秒时发出第一次黄牌警告，随后每5秒发出1次黄牌警告，直至违规机器人被罚下。处于战亡或异常离线状态的机器人在禁区停留时长大于20秒，最高当局判负。

R63 机器人不得将可移动道具放入双方公路禁区、己方补给禁区、双方基地禁区和对方飞镖发射站内。

违规判罚：对违规机器人发出黄牌警告，若后续可移动道具对对方机器人飞坡、补给弹丸、飞镖发射和飞镖命中产生决定性影响，或影响任意核心道具正常工作，将对违规机器人发出红牌警告。

R64 不可将无线调试器、比赛使用的可移动道具带入赛场。比赛过程中，机器人仅可使用由组委会在赛场内提供的官方专用弹丸以及可移动道具。

违规判罚：没收带入赛场的物品，如对比赛造成影响最高取消违规方的比赛资格。

R65 机器人不得获取或以任意方式携带、使用已经装配成功的能量单元。

违规判罚：当局判负。

R66 比赛过程中，机器人不得破坏战场、场地道具或弹丸，亦不可影响场地道具的正常功能。

违规判罚：最高取消违规方的比赛资格。

R67 不得使用 42mm 弹丸或飞镖击打能量机关。

违规判罚：最高对违规机器人发出红牌警告。

R68 机器人在装配过程中不得操作除能量单元外科技核心的可动结构及其他本体结构。

违规判罚：当局判负。

### 7.3 严重违规

若参赛中出现如下所示的行为，会被判定为严重违规。对于严重违规，组委会最高将取消违规方的比赛资格。若行为违反当地法律法规，组委会将配合有关部门追究违法者的法律责任。

<div style="text-align: center;"><div style="text-align: center;">表 7-5 严重违规类型</div> </div>




<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>条例</td><td style='text-align: center; word-wrap: break-word;'>类型</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>1</td><td style='text-align: center; word-wrap: break-word;'>恶意破坏场地、道具等官方设备或其他参赛队伍机器人、设备等行为。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>2</td><td style='text-align: center; word-wrap: break-word;'>弄虚作假、冒名顶替或其他不诚信参赛的行为。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>3</td><td style='text-align: center; word-wrap: break-word;'>修改或破坏裁判系统，使用技术手段干扰裁判系统的任何检测功能。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>4</td><td style='text-align: center; word-wrap: break-word;'>不符合规范文件且被裁判长判定为严重违规的情况。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>5</td><td style='text-align: center; word-wrap: break-word;'>不服从判罚、不配合检查、故意拖延、干扰秩序、无故弃权或罢赛等其他妨碍比赛的行为。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>6</td><td style='text-align: center; word-wrap: break-word;'>消极比赛、操控比赛等行为。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>7</td><td style='text-align: center; word-wrap: break-word;'>为获得不正当比赛成绩或谋取不正当利益，给予他人财物或非法索取、收受他人财物。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>8</td><td style='text-align: center; word-wrap: break-word;'>出现诋毁、谩骂、比不当手势、恶意起哄、恶意投掷物品等不文明、不道德的言行。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>9</td><td style='text-align: center; word-wrap: break-word;'>发表、传播或向媒体散布不实或不负责任的言论。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>10</td><td style='text-align: center; word-wrap: break-word;'>蓄意攻击、冲撞他人，做出危害自身或他人安全的行为。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>11</td><td style='text-align: center; word-wrap: break-word;'>携带危险品或违禁品。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>12</td><td style='text-align: center; word-wrap: break-word;'>其他违反比赛精神，被判定为严重违规的行为。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>13</td><td style='text-align: center; word-wrap: break-word;'>其他有悖社会主义核心价值观、违背体育道德、违反公序良俗、违反赛风赛纪、造成不良社会影响或违反法律法规的言行。</td></tr></table>

## 8 异常情况

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//bf3c614b-c3b1-45a6-bd9a-45c7165f7c08/markdown_1/imgs/img_in_image_box_133_270_177_316.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A04%3A18Z%2F-1%2F%2F93ed918d33b74d7fc2ed1c6da0c2af9d2419de470de6ef7380315786c4c4a7fa" alt="Image" width="3%" /></div>


裁判的人工判罚和对异常情况处理会存在一定延迟，若对比赛结果产生重大影响，裁判长会根据实际情况确定最终的处理结果。

若出现以下异常情况，将按照对应方式处理，双方队伍不得有异议，处理方式如下：

当出现严重的安全隐患或异常状况时，例如：电池爆燃、场馆停电、高压气瓶爆炸或场内人员冲突等，主裁判发现并确认后，将通知双方操作手，同时通过裁判系统罚下所有机器人，该局比赛结果作废，待隐患或异常排除后，重新开始比赛。组委会将优先处理安全问题，并在可能范围内尽力保护机器人，无法保证完全不会对机器人产生影响，因安全处置而导致的任何损失或影响，均由参赛队自行承担。

比赛过程中，若战场中非关键道具出现损坏，例如地胶损坏、场地灯条损坏、基地灯效损坏等不影响比赛公平的情况，则比赛正常进行。

比赛过程中，若出现机器人装甲灯效、灯条灯效异常，装甲模块贴纸损坏等情况，则比赛正常进行。

比赛过程中，若关键官方设备、道具出现功能异常或结构损坏，影响了比赛的公平性，例如：现场网络异常导致机器人离线、击打能量机关后没有触发增益效果、场地道具机构无法正常运行，裁判将通过裁判系统手动处理此类故障。如故障无法手动处理，裁判将通知双方操作手，同时罚下所有机器人，该局比赛立即结束，比赛结果作废。问题排除后，重新开始比赛。

比赛过程中，若关键官方设备、道具出现功能异常或结构损坏，影响了比赛的公平性，主裁判未及时确认并结束比赛，导致原本应该结束的比赛继续进行并出现了胜负结果，当场比赛结束后5分钟内，裁判长查实后，该局比赛结果作废，需重赛一局。

若出现严重违规行为明显触发判负处罚，但主裁判未及时确认并执行，当场比赛结束后5分钟内，裁判长查实后，该局比赛结果作废，对违规方追加判负处罚。

比赛过程中，若出现可能影响比赛公平性的情况，当场比赛结束后5分钟内，裁判长将情况告知双方队长并暂停成绩确认流程，在此后60分钟内查实并将最终处理方式告知双方队长。双方均不能对处理结果产生异议。

## 9 申诉

每支参赛队伍在区域赛、复活赛和全国赛各有1次申诉机会，不可叠加使用。如果申诉成功则保留本次申诉机会，否则将消耗1次申诉机会。无申诉机会时，仲裁委员会将不再受理该参赛队伍的任何申诉。受理申诉后，仲裁委员会对申诉材料和相关证据进行仲裁，裁判长代表仲裁委员会将申诉结果告知双方，仲裁委员会对申诉结果拥有最终解释权。

以下情况不可作为申诉依据：

违规判罚中的口头警告、黄牌警告和红牌警告。

发起技术暂停的类型及流程。

裁判系统机载端出现“常规战损”。

在成绩确认表上签字后或一场比赛结束超过5分钟，不可发起申诉。

### 9.1 申诉流程

参赛队伍如需申诉，应遵循以下流程：

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//bf3c614b-c3b1-45a6-bd9a-45c7165f7c08/markdown_3/imgs/img_in_image_box_118_281_1077_1307.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A04%3A21Z%2F-1%2F%2Fae1d1a24eccd7dffa661dd920b3daffabc81c5254b01cb68729b5686a36f574d" alt="Image" width="80%" /></div>


<div style="text-align: center;"><div style="text-align: center;">图 9-1 申诉流程图</div> </div>


### 9.2 申诉材料

参赛队伍提交的申诉材料，单个文件大小不得超过500MB，并且不超过10个文件。

### 9.3 申诉结果

申诉结果包括：维持原比赛成绩、被申诉方判负、双方重赛。仲裁委员会确认申诉结果后，双方不得对申诉结果提出异议。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//54b2f760-7e17-4d49-a032-af662fa47437/markdown_0/imgs/img_in_image_box_134_348_178_393.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A45Z%2F-1%2F%2F2ba3ba2d55a0fff5b248a6faee44453f6365d197bc90a67f658ac988d89672eb" alt="Image" width="3%" /></div>


申诉成功：被申诉方判负、双方重赛。

申诉失败：维持原比赛成绩。

如果仲裁沟通环节告知结果为双方重赛，但双方均不接受重赛，则视为申诉失败，维持原比赛成绩。

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//54b2f760-7e17-4d49-a032-af662fa47437/markdown_0/imgs/img_in_image_box_126_548_170_592.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A45Z%2F-1%2F%2Fe3ce3b599c74d5514c2a96cf4cf47a920e2ccba4dcadfb5be48e65d6b6c15fa6" alt="Image" width="3%" /></div>


在不影响整体赛程的情况下，原则上会将重赛时间安排在当天所有比赛结束后，以实际情况为准。

重赛赛程与常规赛程的流程一致，双方需按照组委会规定的时间、遵守相关规定进行比赛。

如申诉局次对场次的胜负关系产生影响，场次的胜负需重新判定。

示例：一场 BO3 的比赛结果为 1:2，第一局胜利方为红方，第二局和第三局为蓝方，比赛结束后红方对第二局发起申诉并且申诉结果为：双方重赛，重赛局次若为红方胜利最终比赛结果为 2:0，若重赛局次为蓝方胜利比赛最终结果为 1:2。

## 附录1 雷达信息波特性

频谱分布示意图

红方广播源 + 红方一级干扰源：

<div style="text-align: center;"><div style="text-align: center;">红方广播源+红方一级干扰源</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//54b2f760-7e17-4d49-a032-af662fa47437/markdown_1/imgs/img_in_chart_box_177_363_1010_710.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A45Z%2F-1%2F%2F5ce430e5af609c0e5696cd89da0e81601e01dee2365f30cac658134be00be2ee" alt="Image" width="69%" /></div>


<div style="text-align: center;"><div style="text-align: center;">红方广播源 + 红方二级干扰源：</div> </div>


<div style="text-align: center;"><div style="text-align: center;">红方广播源+红方二级干扰源</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//54b2f760-7e17-4d49-a032-af662fa47437/markdown_1/imgs/img_in_chart_box_177_807_1012_1145.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A45Z%2F-1%2F%2F316875860d6db6d47fd13f529074360ae8e9ed178afde1d1ad8132d8fff47cca" alt="Image" width="70%" /></div>


红方广播源 + 红方三级干扰源：

<div style="text-align: center;"><div style="text-align: center;">红方广播源+红方三级干扰源</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//54b2f760-7e17-4d49-a032-af662fa47437/markdown_2/imgs/img_in_chart_box_177_220_1011_553.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A46Z%2F-1%2F%2F7ccc84e33537be6d1c0d5d1981dbea70e6561b6285f463286fc5db444fef8a18" alt="Image" width="70%" /></div>


<div style="text-align: center;"><div style="text-align: center;">蓝方广播源 + 一级干扰源：</div> </div>


<div style="text-align: center;"><div style="text-align: center;">蓝方广播源+蓝方一级干扰源</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//54b2f760-7e17-4d49-a032-af662fa47437/markdown_2/imgs/img_in_chart_box_178_657_1010_992.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A46Z%2F-1%2F%2F3965db63698e0160f56b6abc944957a1dac74a327ca0c230c6fead24cddb15c3" alt="Image" width="69%" /></div>


蓝方广播源 + 二级干扰源：

<div style="text-align: center;"><div style="text-align: center;">蓝方广播源+蓝方二级干扰源</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//54b2f760-7e17-4d49-a032-af662fa47437/markdown_2/imgs/img_in_chart_box_178_1095_1009_1426.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A46Z%2F-1%2F%2Fbe98a5577ad8c378db0029b9712904cf2f985407b683cc2f2c5208e72318a628" alt="Image" width="69%" /></div>


蓝方广播源+三级干扰源：

<div style="text-align: center;"><div style="text-align: center;">蓝方广播源 + 蓝方三级干扰源</div> </div>


<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//54b2f760-7e17-4d49-a032-af662fa47437/markdown_3/imgs/img_in_chart_box_181_221_1010_553.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A47Z%2F-1%2F%2Fbb3cf81d568ba92a3c4f753b993888598a19d877ed3970adc96041ce82299542" alt="Image" width="69%" /></div>


##### 空口帧结构

每个发射数据包在空口的结构如下：

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//54b2f760-7e17-4d49-a032-af662fa47437/markdown_3/imgs/img_in_image_box_180_682_1011_948.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A02%3A47Z%2F-1%2F%2F47fb9a09892b71f1055d68b39d427a60298c9d270a8f0595fd709c57223d1f6c" alt="Image" width="69%" /></div>


空口帧结构表：



<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>字段</td><td style='text-align: center; word-wrap: break-word;'>长度</td><td style='text-align: center; word-wrap: break-word;'>值/说明</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Access Code</td><td style='text-align: center; word-wrap: break-word;'>8 字节(64bits)</td><td style='text-align: center; word-wrap: break-word;'>信息波：0x2F6F4C74B914492E，干扰波：0x16E8D377151C712D（大端序）。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Header</td><td style='text-align: center; word-wrap: break-word;'>4 字节(32bits)</td><td style='text-align: center; word-wrap: break-word;'>包含两份相同的 Payload Length（各 16 bits，大端序，值为 15 即 0x000F）。接收端校验两份是否一致，不一致则丢包。</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>Payload</td><td style='text-align: center; word-wrap: break-word;'>15 字节</td><td style='text-align: center; word-wrap: break-word;'>有效载荷数据。</td></tr></table>

注：红蓝双方使用相同的 Access Code。即红方和蓝方的信息波均使用 0x2F6F4C74B914492E，红方和蓝方的干扰波均使用 0x16E8D377151C712D。

发送的数据流按 15 字节为一组进行切片，每组作为一个空口包的 Payload，加上 Access Code 和 Header

后发射。即数据帧（含 SOF、CRC 等所有字段）会被连续划分为 15 字节的分片，依次组成空口包发出。调制链路补充说明：



<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>项目</td><td style='text-align: center; word-wrap: break-word;'>说明</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>前导码(Preamble)</td><td style='text-align: center; word-wrap: break-word;'>无独立前导码，帧以 Access Code 直接起始</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>包间隔</td><td style='text-align: center; word-wrap: break-word;'>无固定包间隔，数据到达即发射</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>高斯滤波器截断长度</td><td style='text-align: center; word-wrap: break-word;'>默认 4 个符号周期(GNURadio digital_gfsk_mod 默认值)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>数据白化(Whitening)</td><td style='text-align: center; word-wrap: break-word;'>无</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>前向纠错（FEC）</td><td style='text-align: center; word-wrap: break-word;'>无</td></tr></table>

GFSK 调制后的时域特征（以红方广播源为例）：



<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>特征</td><td style='text-align: center; word-wrap: break-word;'>值</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>每 bit 持续时间</td><td style='text-align: center; word-wrap: break-word;'>47µs</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>每包持续时间</td><td style='text-align: center; word-wrap: break-word;'>10.15ms(216bits*47µs)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>bit=1 瞬时频偏</td><td style='text-align: center; word-wrap: break-word;'>+248,723Hz</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>bit=0 瞬时频偏</td><td style='text-align: center; word-wrap: break-word;'>-248,723Hz</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>高斯滤波器 3dB 带宽</td><td style='text-align: center; word-wrap: break-word;'>BT/Tb=0.35/47µs≈7,447Hz</td></tr></table>

##### 数据帧协议

数据推送速率：



<table border=1 style='margin: auto; word-wrap: break-word;'><tr><td style='text-align: center; word-wrap: break-word;'>波源</td><td style='text-align: center; word-wrap: break-word;'>推送速率</td><td style='text-align: center; word-wrap: break-word;'>数据内容</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>信息波</td><td style='text-align: center; word-wrap: break-word;'>1400byte/s</td><td style='text-align: center; word-wrap: break-word;'>全部为有效数据 0X0A01-0X0A05(10Hz)</td></tr><tr><td style='text-align: center; word-wrap: break-word;'>干扰波</td><td style='text-align: center; word-wrap: break-word;'>1350byte/s</td><td style='text-align: center; word-wrap: break-word;'>包含 0x0A06 数据（10Hz），其余字节为随机填充</td></tr></table>

具体通信协议结构，请参阅：《RoboMaster 2026 机甲大师高校系列赛通信协议》。

## 附录2 赛前流程说明

<div style="text-align: center;"><img src="https://pplines-online.bj.bcebos.com/deploy/official/paddleocr/pp-ocr-vl-16-online//f2602f19-7916-417e-9617-ce56e9c0bfd5/markdown_1/imgs/img_in_image_box_134_260_178_304.jpg?authorization=bce-auth-v1%2FALTAKDN8mY5KlNI7zaRpLmOqrw%2F2026-07-09T08%3A04%3A36Z%2F-1%2F%2Fdabb22a5ad6b1f7f6e0a880becdfb0d8d1f7841595ddf42c114567be01c43487" alt="Image" width="3%" /></div>


本赛季将不单独设置哨兵建图环节。

### 预检录

预检录为正式检录前设置的检查环节，旨在帮助参赛队伍提前发现并解决机器人存在的问题。组委会将在预检录及适应性训练期间尽力协助参赛队伍排查与处理机器人故障，但预检录结果不等同于正式比赛检录结果；如正式检录时发现机器人不符合检录通过标准，该机器人仍不得上场参赛。

仅在预检录期间可进行唯一标识登记；预检录结束后，仅允许对已登记唯一标识的机器人进行更换补登记。若战队需维修或更换带有唯一标识的部件，必须向组委会申请报备并重新注册与标识。每支队伍在同一赛区最多可发起6次此类报备；未经报备私自更换带有唯一标识的部件，将导致该机器人失去上场资格。

非紧急情况报备方式：若距离参赛队下一场比赛超过2小时，或处于组委会非工作时段内，参赛队可以自主更换相关部件，并在【机器人唯一标识补登记】提交更换前后的的机器人详细照片或更换过程全程视频，在同一链接预约检查时间，在约定时间到达第二检录区，组委会将有专人进行审核。审核通过的机器人将重新获得唯一标识。

紧急情况报备方式：若距离参赛队下一场比赛不足2小时且处于组委会工作时段内，参赛队应在第二检录区联系裁判申报紧急维修。组委人员确认后将随队前往赛队备场区，全程监督维修过程。此情形下，机器人可在未补齐全部唯一标识的情况下通过检录并参加本场比赛，但在该队下一场比赛结束后，机器人必须移至第二检录区接受二次审核并补全唯一标识。

### 场地道具训练

道具训练提供与正式比赛相似的场地道具与木制结构供参赛队伍测试。训练前不要求通过赛前检录，参赛队伍需自行确保机器人裁判系统正常；若现场裁判系统出现故障，相关耗时将计入该队的训练时间。

##### 时间与预约：

各参赛队须提前20分钟到候场区等候，未按时到达者训练时间照常计时且不顺延。每支队伍共有两次训练机会，每次30分钟（含进退场）。首次时段由组委会安排，第二次由参赛队自行预约；请严格按照时段进退场，不得占用他队训练时间。

##### 人员与设备：

每支队伍最多12人进入训练场地，入场人员须佩戴护目镜。组委会仅提供2台用于图传信道的操作手电脑；如需接入更多机器人选手端，可自带电脑，但不得连入赛事网络。

##### 道具、弹丸与安全：

组委会仅提供可移动道具用于测试，不提供 17mm 或 42mm 弹丸；需测试时请各队自备。使用 42mm 弹丸测试时请注意避免主动击打能量机关。因场馆条件限制，训练场地可能受环境光影响，参赛队需自行适应。若队伍不服从现场裁判或出现其他违规行为，将被取消道具训练资格并立即请离场；情节严重者同时取消适应性训练资格。

### 适应性训练

适应性训练为参赛队伍在正式比赛前的一次调试与适应机会，主要目的包括：

熟悉比赛环境与流程。

测试并调整机器人状态与策略。

##### 适应性训练的规则：

训练时程紧凑，且以调试为主；在无重大官方设备故障的情况下，默认不暂停训练。

若出现裁判系统（机载端）异常，组委会可给予最多2分钟的官方技术暂停以处理故障；该暂停时长计入适应性训练总体时间。

适应性训练期间不提供参赛队伍技术暂停机会。

##### 自由调试阶段规定：

进行发弹测试时，参赛队伍可向裁判申请借用清弹袋，并仅向清弹袋内发射。

自由调试阶段的比赛阶段状态为“未开始”，参赛队需自行适应并熟悉比赛各阶段的切换与要求。

##### 参与资格与阶段划分：

未按时通过检录或存在安全隐患的机器人不得参加适应性训练。

因严重不符合检录标准而未通过检录的机器人，仅允许参加适应性训练中的自由调试阶段。

● 参加适应性训练的机器人数量不得超过各赛项规定的最高机器人阵容限制。

## 附录3 未来规则规划

在未来赛季，组委会将加强下表中所述机器人能力、场景适应性、技术方向的引导和鼓励。



<table border="1" style="margin: auto; word-wrap: break-word;"><tr><td style="text-align: center; word-wrap: break-word;">机器人核心系统</td><td style="text-align: center; word-wrap: break-word;">子系统</td><td style="text-align: center; word-wrap: break-word;">能力/技术方向</td><td style="text-align: center; word-wrap: break-word;">典型机器人</td></tr><tr><td rowspan="3">感知系统</td><td style="text-align: center; word-wrap: break-word;">外部传感器</td><td style="text-align: center; word-wrap: break-word;">单机多传感器信息融合</td><td style="text-align: center; word-wrap: break-word;">全部</td></tr><tr><td style="text-align: center; word-wrap: break-word;">多机通信</td><td style="text-align: center; word-wrap: break-word;">多机信息融合</td><td style="text-align: center; word-wrap: break-word;">全部</td></tr><tr><td style="text-align: center; word-wrap: break-word;">制导系统</td><td style="text-align: center; word-wrap: break-word;">自身运动状态获取</td><td style="text-align: center; word-wrap: break-word;">飞镖系统</td></tr><tr><td rowspan="3">决策系统</td><td style="text-align: center; word-wrap: break-word;">运算平台</td><td style="text-align: center; word-wrap: break-word;">低功耗运行</td><td style="text-align: center; word-wrap: break-word;">全部</td></tr><tr><td style="text-align: center; word-wrap: break-word;">决策算法</td><td style="text-align: center; word-wrap: break-word;">● 无外部干涉/低外部干涉下的自主决策能力(特别是语义分析和极端条件下的非保守决策能力)\n● 有限算力下的低时间复杂度高效算法设计</td><td style="text-align: center; word-wrap: break-word;">哨兵机器人、雷达系统</td></tr><tr><td style="text-align: center; word-wrap: break-word;">制导系统</td><td style="text-align: center; word-wrap: break-word;">目标定位和自主识别</td><td style="text-align: center; word-wrap: break-word;">飞镖系统</td></tr><tr><td rowspan="4">执行系统</td><td style="text-align: center; word-wrap: break-word;">移动机构</td><td style="text-align: center; word-wrap: break-word;">● 以折叠/变形形式跨越狭窄地形\n● 稳定通过崎岖，高低差等恶劣地形</td><td style="text-align: center; word-wrap: break-word;">地面机器人</td></tr><tr><td style="text-align: center; word-wrap: break-word;">弹丸发射机构</td><td style="text-align: center; word-wrap: break-word;">● 非摩擦轮的新式发射机构(如气动，电磁发射等)\n● 异形击打目标识别、高精度发射\n● 超视距远程打击</td><td style="text-align: center; word-wrap: break-word;">英雄、步兵、哨兵机器人</td></tr><tr><td style="text-align: center; word-wrap: break-word;">物体操作机构</td><td style="text-align: center; word-wrap: break-word;">● 多自由度柔性运动机构\n● 多自由度末端执行器</td><td style="text-align: center; word-wrap: break-word;">工程机器人</td></tr><tr><td style="text-align: center; word-wrap: break-word;">飞行与动力系统</td><td style="text-align: center; word-wrap: break-word;">● 高载重比设计\n● 折叠与变形，低体积运输</td><td style="text-align: center; word-wrap: break-word;">空中机器人</td></tr><tr><td rowspan="4"></td><td style="text-align: center; word-wrap: break-word;">制导机构</td><td style="text-align: center; word-wrap: break-word;">● 含动力，能够自主改变轨迹（非飞行器），特别是末端机动能力\n● 非抛物线轨道设计</td><td style="text-align: center; word-wrap: break-word;">飞镖系统</td></tr><tr><td style="text-align: center; word-wrap: break-word;">模块化机构</td><td style="text-align: center; word-wrap: break-word;">设计能够脱离机器人整体系统独立执行单一功能，也能够快速整合成为机器人系统一部分的功能模块，如独立弹丸发射机构等</td><td style="text-align: center; word-wrap: break-word;">地面机器人</td></tr><tr><td style="text-align: center; word-wrap: break-word;">整机</td><td style="text-align: center; word-wrap: break-word;">低功耗运行</td><td style="text-align: center; word-wrap: break-word;">全部</td></tr><tr><td style="text-align: center; word-wrap: break-word;">整机</td><td style="text-align: center; word-wrap: break-word;">● 复杂环境下达成自主决策效果的能力\n● 自动机器人与手动机器人有机协同</td><td style="text-align: center; word-wrap: break-word;">哨兵机器人、雷达系统</td></tr><tr><td style="text-align: center; word-wrap: break-word;">人机交互</td><td style="text-align: center; word-wrap: break-word;">整机</td><td style="text-align: center; word-wrap: break-word;">● 机器人高效准确向人类传递做出决策所必须的信息\n● 降低操作机器人本身的难度，强调人类决策的不可替代性</td><td style="text-align: center; word-wrap: break-word;">全部</td></tr></table>




邮箱：robomaster@dji.com

论坛：https://bbs.robomaster.com

官网：https://www.robomaster.com

电话：+86 0755-84357613（周一至周五10:30-19:30）

地址：广东省深圳市南山区西丽街道仙茶路与兴科路交叉口大疆天空之城T222F

