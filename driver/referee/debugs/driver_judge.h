//
// Created by liaoyang on 2023-12-11.
//

#ifndef INFANTRYCHASIS_JUDGE_DRIVER_COMMUNICATE_H
#define INFANTRYCHASIS_JUDGE_DRIVER_COMMUNICATE_H

#include "main.h"
#include "data_fifo.h"
#include "string.h"
#include "driver_chassis.h"

//数据包相关宏定义
#define PROTOCOL_DATA_MAX_SIZE 128  //协议中数据最大长度
#define UART_RX_DMA_SIZE 1024  //DMA传输数据地址的数组大小
#define JUDGE_FIFO_BUF_LEN  1024 //FIFO长度
#define MAX_CMD_ID 0x0308 //命令码最大值

#define PROTOCOL_FRAME_MAX_SIZE  300 //交互数据最大长度

/* -------------------------------裁判系统数据相关信息----------------------------------*/

/**
  * @brief  帧头定义
  */
typedef struct __packed {
    uint8_t  sof;                 //DN_REG_ID 固定值0xA5
    uint16_t data_length;         //数据段长度
    uint8_t  seq;                 //包序号
    uint8_t  crc8;                //帧头校验
} frame_header_t;

/**
  * @brief  解包步骤定义
  */
typedef enum {
    STEP_HEADER_SOF  = 0,   //检查帧头SOF
    STEP_LENGTH_LOW  = 1,   //检查帧头中数据长度的第一个字节
    STEP_LENGTH_HIGH = 2,   //检查帧头中数据长度的第二个字节
    STEP_FRAME_SEQ   = 3,   //检查包序号
    STEP_HEADER_CRC8 = 4,   //检查帧头CRC8校验
    STEP_DATA_CRC16  = 5,   //检查整包CRC16校验
} unpack_step_e;

/**
  * @brief  数据包中内容
  */
typedef struct {
    fifo_s_t       *data_fifo;    //存储数据包中信息的FIFO
    frame_header_t *frame_header; //帧头
    uint16_t       data_len;      //单纯数据信息长度
    uint8_t        protocol_packet[PROTOCOL_DATA_MAX_SIZE]; //数据包中检验正常后的数据
    unpack_step_e  unpack_step;   //解包步骤
    uint16_t       index;         //当前字节序号
} unpack_data_t;

/**
  * @brief  裁判系统命令码
  */
typedef enum {
//比赛信息
    GAME_STATUS_ID                    = 0x0001,        //比赛状态数据，3HZ
    GAME_RESULT_ID                    = 0x0002,        //比赛结果数据，比赛结束后发送
    GAME_ROBOT_HP_ID                  = 0x0003,        //机器人血量数据，1HZ
    EVENT_DATA_ID                     = 0x0101,        //场地事件数据，事件改变后发送
    //EXI_SUPPLY_PROJECTILE_ACTION_ID   = 0x0102,        //补给站动作标识，补给站弹丸释放时触发发生
    REFEREE_WARNING_ID                = 0X0104,        //裁判警告信息,己方判罚/判负时触发发生
    DART_REMAINING_TIME_ID            = 0X0105,        //飞镖发射口倒计时,3Hz
    ROBOT_STATUS_ID                   = 0x0201,        //机器人性能体系数据，10HZ
    POWER_HEAT_DATA_ID                = 0x0202,        //实时功率热量数据，50HZ
    ROBOT_POS_ID                      = 0x0203,        //机器人位置，10HZ
    BUFF_ID                           = 0x0204,        //机器人增益，3Hz频率发送
    //AIR_SUPPORT_DATA_ID               = 0x0205,        //空中支援时间数据，10Hz
    HURT_ID                           = 0x0206,        //伤害状态，伤害发生后发送
    SHOOT_DATA_ID                     = 0x0207,        //实时射击信息，射击后发送
    PROJECTILE_ALLOWANCE_ID           = 0X0208,        //允许发弹量，10Hz
    RFID_STATUS_ID                    = 0X0209,        //机器人 RFID 状态3Hz
    DART_CLIENT_CMD_ID                = 0X020A,        //飞镖机器人客户端指令数据，10Hz
    GROUND_ROBOT_POSITION_ID          = 0X020B,        //地面机器人位置数据，1Hz
    RADAR_MARK_DATA_ID                = 0X020C,        //雷达标记进度数据，1Hz

//向裁判系统发送 ，机器人间通信
    ROBO_INTERACTION_DATA_ID          = 0x0301,       //交互数据接收信息
    //以下为ROBO_INTERACTION_DATA_ID下子ID
    STU_STU_DATA_ID                   = 0x0211,       //机器人间通信内容ID（0x0201~0x02FF)
    INTERACTION_LAYER_DELETE_ID       = 0x0100,       //客户端删除图形内容ID
    INTERACTION_FIGURE_ID             = 0x0101,       //客户端绘制1个图形内容ID
    INTERACTION_FIGURE2_ID            = 0x0102,       //客户端绘制2个图形内容ID
    INTERACTION_FIGURE3_ID            = 0x0103,       //客户端绘制5个图形内容ID
    INTERACTION_FIGURE4_ID            = 0x0104,       //客户端绘制7个图形内容ID
    INTERACTION_CHARACTER_ID          = 0x0110,       //客户端绘制字符内容ID

//小地图交互数据
    MAP_COMMAND_ID                    = 0X0303,       //选手端下发数据，触发发送
    MAP_ROBOT_DATA_ID                 = 0X0305,       //选手端接收雷达数据，10Hz
    MAP_SENTRY_DATA_ID                = 0X0307,       //选手端小地图接收哨兵数据，1Hz

//图传链数据
    CUSTOM_ROBOT_DATA_ID              = 0X0302,       //自定义控制器与机器人交互数据，发送方触发，上限30Hz
    REMOTE_CONTROL_ID                 = 0X0304,       //键盘鼠标信息，图传串口发送
    CUSTOM_CLINET_DATA_ID             = 0X0306,       //自定义控制器与选手端交互数据，发送方触发，上限30Hz

//通信ID确认
    RED_HERO_ID                       = 0x0001,    //红方英雄机器人ID
    RED_ENGINEER_ID                   = 0x0002,
    RED_INFANTRY3_ID                  = 0x0003,
    RED_INFANTRY4_ID                  = 0x0004,
    RED_INFANTRY5_ID                  = 0x0005,
    RED_AERIAL_ID                     = 0x0006,
    RED_SENTRY_ID                     = 0x0007,
    RED_RADAR_ID                      = 0x0009,
    BLUE_HERO_ID                      = 0x0065,
    BLUE_ENGINEER_ID                  = 0x0066,
    BLUE_INFANTRY3_ID                 = 0x0067,
    BLUE_INFANTRY4_ID                 = 0x0068,
    BLUE_INFANTRY5_ID                 = 0x0069,
    BLUE_AERIAL_ID                    = 0x006A,
    BLUE_SENTRY_ID                    = 0x006B,
    BLUE_RADAR_ID                     = 0x006D,
    RED_HERO_CUSTOM_ID                = 0x0101,    //红方英雄机器人客户端ID
    RED_ENGINEER_CUSTOM_ID            = 0x0102,
    RED_INFANTRY3_CUSTOM_ID           = 0x0103,
    RED_INFANTRY4_CUSTOM_ID           = 0x0104,
    RED_INFANTRY5_CUSTOM_ID           = 0x0105,
    RED_AERIAL_CUSTOM_ID              = 0x0106,
    BLUE_HERO_CUSTOM_ID               = 0x0165,
    BLUE_ENGINEER_CUSTOM_ID           = 0x0166,
    BLUE_INFANTRY3_CUSTOM_ID          = 0x0167,
    BLUE_INFANTRY4_CUSTOM_ID          = 0x0168,
    BLUE_INFANTRY5_CUSTOM_ID          = 0x0169,
    BLUE_AERIAL_CUSTOM_ID             = 0x016A,
} judge_data_cmd_id;

/* -------------------------------裁判系统各数据包信息结构体们----------------------------------*/

/**
  * @brief  (0x0001)
  * @note 比赛状态数据：0x0001。发送频率：3Hz，发送范围：所有机器人
  */
typedef struct __packed {
    /*game_type
    1 ：RoboMaster 机甲大师赛
    2 ：RoboMaster 机甲大师单项赛
    3 ：ICRA RoboMaster 人工智能挑战赛
    4 ：RoboMaster 联盟赛 3V3
    5 ：RoboMaster 联盟赛 1V1*/
    uint8_t  game_type: 4;
    /*game_progress
    0 ：未开始比赛
    1 ：准备阶段
    2 ：自检阶段
    3 ： 5s 倒计时
    4 ：对战中
    5 ：比赛结算中*/
    uint8_t  game_progress: 4;
    uint16_t stage_remain_time;     //当前阶段剩余时间，单位s
    uint64_t SyncTimeStamp;         //机器人接收到该指令的精确 时后生效Unix时间，当机载端收到有效的NTP服务器授
} game_status_t;

/**
  * @brief  (0x0002)
  * @note 比赛结果
  */
typedef struct __packed {
    uint8_t winner;     //0平局  1红方胜利   2蓝方胜利
} game_result_t;

/**
  * @brief  (0x0003)
  * @note 机器人血量数据：0x0003。发送频率：1Hz，发送范围：所有机器人
  */
typedef struct __packed {
    uint16_t ally_1_robot_HP;
    uint16_t ally_2_robot_HP;
    uint16_t ally_3_robot_HP;
    uint16_t ally_4_robot_HP;
    uint16_t reserved;
    uint16_t ally_7_robot_HP;
    uint16_t ally_outpost_HP;
    uint16_t ally_base_HP;
} game_robot_HP_t;

/**
  * @brief  (0x0101)
  * @note 场地时间数据，3Hz
  */
typedef struct __packed {
    /*
    event_type:
    bit 0-2：
        bit 0：己方补给站 1 号补血点占领状态 1 为已占领；
        bit 1：己方补给站 2 号补血点占领状态 1 为已占领；
        bit 2：己方补给站 3 号补血点占领状态 1 为已占领；
    bit 3-6：己方能量机关状态：
        bit 3-4：己方小能量机关的激活状态，0为未激活，1 为已激活，2为正在激活
        bit 5-6：己方大能量机关的激活状态，0为未激活，1 为已激活，2为正在激活
    bit 7-8：己方中央高地的占领状态，1 为被己方占领，2 为被对方占领
    bit 9-10：己方梯形高地的占领状态，1 为已占领；
    bit 11-19：对方飞镖最后一次击中己方前哨站或基地的时间（0-420，开局默认为0）
    bit 20-22：对方飞镖最后一次击中己方前哨站或基地的具体目标，开局默认为 0，1 为击中前哨站，2 为击中基地固定目标，3 为击中基地随机固定目标，4 为击中基地随机移动目标，5为击中基地末端移动目标
    bit 23-24：中心增益点的占领状态，0 为未被占领，1 为被己方占领，2 为被对方占领，3 为被双方占领。（仅 RMUL 适用）
    bit 25-26：己方堡垒增益点的占领状态，0 为未被占领，1 为被己方占领，2 为被对方占领，3 为被双方占领
    bit 27-28：己方前哨站增益点的占领状态，0 为未被占领，1 为被己方占领，2 为被对方占领
    bit 29：己方基地增益点的占领状态，1 为已占领
    bit 30-31：保留位
     */
    uint32_t event_type;
} event_data_t;


/**
  * @brief  (0x0102)
  * @note 补给站补弹动作数据
  */
typedef struct __packed {
    /*补给站口 ID
     1 ： 1 号补给口；
     2 ： 2 号补给口*/
    uint8_t supply_projectile_id;
    /*补弹机器人 ID
     * 0 为当前无机器人补弹
     * 1 为红方英雄机器人补弹
     * 2 为红方工程 机器人补弹
     * 3/4/5 为红方步兵机器人补弹
     * 101 为蓝方英雄机器人补弹
     * 103/104/105 为蓝方步兵机器人补弹*/
    uint8_t supply_robot_id;
    /* 出弹口开闭状态：
     * 0 为关闭
     * 1 为子弹准备中
     * 2 为子弹下落*/
    uint8_t supply_projectile_step;     //出弹口开闭状态
    uint8_t supply_projectile_num;      //补弹数量
} ext_supply_projectile_action_t;


/**
  * @brief  (0x0104)
  * @note 裁判警告信息：cmd_id (0x0104)。发送频率：警告发生后发送，发送范围：己方机器人。
  */
typedef struct __packed {
    uint8_t level;//判罚等级：1.双方黄牌 2.黄牌 3.红牌 4.判负
    uint8_t offending_robot_id; //违规机器人ID
    uint8_t count;
} referee_warning_t;

/**
  * @brief  (0x0105)
  * @note   飞镖发射口倒计时：cmd_id (0x0105)。发送频率：1Hz 周期发送，发送范围：己方机器人。
  */
typedef struct __packed {
    uint8_t dart_remaining_time;        //己方飞镖发射剩余时间
    uint16_t dart_info;
} dart_remaining_time_t;

/**
  * @brief  (0x0201)
  * @note 比赛机器人状态：0x0201。发送频率：10Hz，发送范围：单一机器人。
  */
typedef struct __packed {
    /*
    *本机器人 ID：
    *1：红方英雄机器人
    *2：红方工程机器人
    *3/4/5：红方步兵机器人
    *6：红方空中机器人
    *7：红方哨兵机器人
    *8：红方飞镖机器人
    *9：红方雷达站
    *10：红方前哨站
    *11：红方基地
    *101：蓝方英雄机器人
    *102：蓝方工程机器人
    *103/104/105：蓝方步兵机器人
    *106：蓝方空中机器人
    *107：蓝方哨兵机器人
    *108：蓝方飞镖机器人
    *109：蓝方雷达站
    *110：蓝方前哨站
    *111：蓝方基地
    */
    uint8_t robot_id;
    uint8_t robot_level;                //机器人当前等级 1 2 3三个
    uint16_t current_HP;                //当前血量
    uint16_t maximum_HP;                //血量上限
    uint16_t shooter_barrel_cooling_value;    //机器人1号枪口每秒冷却值
    uint16_t shooter_barrel_heat_limit;       //机器人1号枪口热量上限
    uint16_t chassis_power_limit;               //机器人底盘功率上限
    //电源管理模块输出情况
    uint8_t mains_power_gimbal_output : 1;      //1 为有 24V 输出， 0 为无 24v 输出
    uint8_t mains_power_chassis_output : 1;     //1 为有 24V 输出， 0 为无 24v 输出
    uint8_t mains_power_shooter_output : 1;     //1 为有 24V 输出， 0 为无 24v 输出

} robot_status_t;


/**
  * @brief  (0x0202)
  * @note 实时功率热量数据：0x0202。发送频率：50Hz，发送范围：单一机器人。
  */
typedef struct __packed {
    uint16_t reserved;
    uint16_t reserved1;
    float reserved2;
    uint16_t chassis_power_buffer;    //缓冲能量(J)
    uint16_t shooter_17mm_barrel_heat; //第1个17mm发射机构的枪口热量
    uint16_t shooter_42mm_barrel_heat;
} power_heat_data_t;

/**
  * @brief  (0x0203)
  * @note   机器人位置：0x0203。发送频率：10Hz，发送范围：单一机器人。
  */
typedef struct __packed {
    float x;
    float y;
    float z;
    float yaw;
} robot_pos_t;

/**
  * @brief  (0x0204)
  * @note   机器人增益：0x0204。发送频率：1Hz 周期发送，发送范围：单一机器人。
  */
typedef struct __packed {
    uint8_t recovery_buff; //机器人回血增益(百分比，10为每秒回复10%最大血量)
    uint8_t cooling_buff;  //机器人枪口冷却倍率
    uint8_t defence_buff;  //机器人防御增益(百分比)
    uint8_t vulnerability_buff;//机器人负防御增益(百分比)
    uint16_t attack_buff;  //机器人攻击增益(百分比)
    uint8_t remaining_energy;//剩余能量
} buff_t;

/**
  * @brief  (0x0205)
  * @note 空中机器人能量状态：0x0205。发送频率：10Hz，发送范围：单一机器人。
  */
typedef struct __packed {
    uint8_t  airforce_status; //空中机器人状态 0.正在冷却 1.冷却完毕 2.空中支援时间
    uint8_t time_remain; //此时状态的剩余时间(s)
} air_support_data_t;

/**
  * @brief  (0x0206)
  * @note 伤害状态：0x0206。发送频率：伤害发生后发送，发送范围：单一机器人。
  */
typedef struct __packed {
    /* bit 0-3 ：
      当血量变化类型为装甲伤害，代表装甲 ID ，
      其中数值为 0-4 号代表机器人的五个装甲片，
      其他血量变化类型，该变量数值为 0 */
    uint8_t armor_id: 4;
    /*hurt_type
     *     bit 4-7 ：血量变化类型
     *     0x0 装甲模块被弹丸攻击导致扣血
     *     0x1 装甲模块或超级电容管理模块离线导致扣血
     *     0x5 装甲模块受到撞击导致扣血
     */
    uint8_t HP_deduction_reason: 4;
} hurt_data_t;

/**
  * @brief  (0x0207)
  * @note 实时射击信息：0x0207。发送频率：射击后发送，发送范围：单一机器人。
  */
typedef struct __packed {
    uint8_t bullet_type; //弹丸类型17/42mm
    uint8_t shooter_id;  //发射机构ID
    uint8_t bullet_freq; //弹丸射速
    float bullet_speed;  //弹丸初速度
} shoot_data_t;

/**
  * @brief  (0x0208)
  * @note 子弹剩余发射数：0x0208。
  * 发送频率：1Hz 周期发送，空中机器人，哨兵机器人以及 ICRA 机器人主控发送，
  * 发送范围：单一机器人。
  */
typedef struct __packed {
    uint16_t projectile_allowance_17mm; //17mm弹丸允许发弹量
    uint16_t projectile_allowance_42mm; //42mm弹丸允许发弹量
    uint16_t remaining_gold_coin;//剩余金币数量
    uint16_t projectile_allowance_fortress;//
} projectile_allowance_t;

/**
  * @brief  (0x0209)
  * @note 机器人 RFID 状态：0x0209。发送频率：1Hz，发送范围：单一机器人。
  */
typedef struct __packed {
    /*
     * bit位值位1/0:是否已检测到该增益点RFID
      bit 1：己方中央高地增益点
      bit 2：对方中央高地增益点
      bit 3：己方梯形高地增益点
      bit 4：对方梯形高地增益点
      bit 5：己方地形跨越增益点（飞坡）（靠近己方一侧飞坡前）
      bit 6：己方地形跨越增益点（飞坡）（靠近己方一侧飞坡后）
      bit 7：对方地形跨越增益点（飞坡）（靠近对方一侧飞坡前）
      bit 8：对方地形跨越增益点（飞坡）（靠近对方一侧飞坡后）
      bit 9：己方地形跨越增益点（中央高地下方）
      bit 10：己方地形跨越增益点（中央高地上方）
      bit 11：对方地形跨越增益点（中央高地下方）
      bit 12：对方地形跨越增益点（中央高地上方）
      bit 13：己方地形跨越增益点（公路下方）
      bit 14：己方地形跨越增益点（公路上方）
      bit 15：对方地形跨越增益点（公路下方）
      bit 16：对方地形跨越增益点（公路上方）
      bit 17：己方堡垒增益点
      bit 18：己方前哨站增益点
      bit 19：己方与资源区不重叠的补给区/RMUL补给区
      bit 20：己方与资源区重叠的补给区
      bit 21：己方装配增益点
      bit 22：对方装配增益点
      bit 23：中心增益点（仅 RMUL 适用）
      bit 24：对方堡垒增益点
      bit 25：对方前哨站增益点
      bit 26：己方地形跨越增益点（隧道）（靠近己方一侧公路区下方）
      bit 27：己方地形跨越增益点（隧道）（靠近己方一侧公路区中间）
      bit 28：己方地形跨越增益点（隧道）（靠近己方一侧公路区上方）
      bit 29：己方地形跨越增益点（隧道）（靠近己方梯形高地较低处）
      bit 30：己方地形跨越增益点（隧道）（靠近己方梯形高地较中间）
      bit 31：己方地形跨越增益点（隧道）（靠近己方梯形高地较高处）

      bit 0：对方地形跨越增益点（隧道）（靠近对方公路一侧下方）
      bit 1：对方地形跨越增益点（隧道）（靠近对方公路一侧中间）
      bit 2：对方地形跨越增益点（隧道）（靠近对方公路一侧上方）
      bit 3：对方地形跨越增益点（隧道）（靠近对方梯形高地较低处）
      bit 4：对方地形跨越增益点（隧道）（靠近对方梯形高地较中间）
      bit 5：对方地形跨越增益点（隧道）（靠近对方梯形高地较高处）
     * RFID 状态不完全代表对应的增益或处罚状态，例如敌方已占领的高地增益点，不 能获取对应的增益效果。
     */
    uint32_t rfid_status;
    uint8_t rfid_status_2;
} rfid_status_t;

/**
  * @brief  (0x020A)
  * @note   飞镖机器人客户端指令数据：0x020A。发送频率：10Hz，发送范围：单一机器人。
  */
typedef struct __packed {
    uint8_t dart_launch_opening_status; //飞镖发射站状态 1.关闭 2.开启中或关闭中 0.开启
    uint8_t dart_attack_target;  //打击目标 0.前哨战 1.基地
    uint16_t target_change_time; //切换打击目标时的比赛剩余时间(s)
    uint16_t latest_launch_cmd_time; //最后一次操作手确定发射指令时的比赛剩余时间(s)
} dart_client_cmd_t;

/*****************************************机器人发送的交互数据************************************************/

/**
  * @brief  student student data(0x0301)---(0x0201~0x02FF)
  * 学生机器人间通信
  */
#define X 113
typedef struct __packed {
    uint8_t data[X];
} interaction_message_t;

/**
  * @brief  (0x0301)
  * @note  机器人交互数据
  */
typedef struct __packed {
    /**
     * data_cmd_id:子内容id:
     * 0x0200-0x02FF 机器人间通信
     * 0x0100 选手端删除图层
     * 0x0101 选手端绘制一个图形
     * 0x0102 选手端绘制两个图形
     * 0x0103 选手端绘制五个图形
     * 0x0104 选手端绘制七个图形
     * 0x0110 选手端绘制字符图形
     * 0x0120 哨兵自主决策指令
     * 0x0121 雷达自主决策指令
     */
    uint16_t data_cmd_id;//子内容id
    uint16_t sender_ID; //发送者ID
    uint16_t receiver_ID; //接收者ID
} robot_interaction_data_t;

typedef struct __packed {
    robot_interaction_data_t robot_interaction_data;
    uint8_t msg_ID;
    uint8_t msg[110];
    uint8_t crc_ID;
} radar_data_v2_t;

enum radar_msg_id_t{
    radar_msg_status = 1,
    radar_msg_location = 2,
};

typedef struct __packed {
    uint8_t is_reliable;        //是否可信
    float x;
    float y;
} enemy_robot_coo;

typedef struct __packed{
    uint16_t enemy_hero;
    uint16_t enemy_engineer;
    uint16_t enemy_infantry_3;
    uint16_t enemy_infantry_4;
    uint16_t enemy_aerial;
    uint16_t enemy_sentry;
}robot_id_t;

#pragma pack(1)
typedef struct{
    uint8_t msg_is_reliable;
    robot_id_t enemy_hp;
    robot_id_t ammunition_allowed;
    robot_id_t defense_buff;
    robot_id_t defense_defense_reduction;          // 负防御增益
    robot_id_t hp_regen_buff;           // 回血增益
    robot_id_t heat_cooling_buff;       // 枪口热量冷却增益
    robot_id_t attack_buff;             // 攻击增益
    robot_id_t enemy_is_invincible;     // 敌方机器人是否处于无敌状态
    uint16_t enemy_economy_remaining;    // 敌方剩余总金币数
    uint16_t enemy_economy_total;        // 敌方总金币数
    uint8_t enemy_outpost_is_survive;   //敌方前哨站是否存活
    uint8_t base_armor_enabled;         //基地装甲是否开启
    uint8_t is_hero_strike;             //英雄是否在吊射
    uint8_t is_engineer_redeem;         //工程是否在兑换
    uint8_t is_enemy_constrained_defense;//敌方是否登上对面堡垒
    uint8_t is_enemy_invade_fortress;    //敌方是否占领我方堡垒
    uint8_t is_enemy_revive_outpost;     //敌方是否复活在前哨站

    //    uint8_t reserved_1;
    //    uint32_t reserved_2;
    //    uint32_t reserved_3;
    //    uint32_t reserved_4;
    //    uint32_t reserved_5;
}radar_status_frame_t;
#pragma pack()

#pragma pack(1)
typedef struct{
    enemy_robot_coo hero;
    enemy_robot_coo engineer;
    enemy_robot_coo infantry_3;
    enemy_robot_coo infantry_4;
    enemy_robot_coo aerial;
    enemy_robot_coo sentry;
}radar_location_frame_t;
#pragma pack(1)

/**
  * @brief  选手端删除图层(0x0301)---(0x0100)
  */
typedef struct __packed {
    uint8_t delete_type;//0 空操作 1 删除图层 2 删除所有
    uint8_t layer;//图层数0-9
} interaction_layer_delete_t;

/**
  * @brief  绘制一个图形相关参数
  */
typedef struct __packed {
    uint8_t  figure_name[3];//图形名
    uint32_t operate_type: 3;//图形操作 0空操作 1增加 2修改 3删除
    uint32_t figure_type: 3;//图形类型
    /*
     * figure_type:
     * 0:直线 1:矩形 2:正圆 3:椭圆 4:圆弧 5:浮点数 6：整形数 7:字符
     * */
    uint32_t layer: 4;//图层数0-9
    uint32_t color: 4;
    /*
     * color:
     * 0:红/蓝 1:黄色 2：绿色 3:橙色 4:紫红色 5:粉色 6:青色 7:黑色 8:白色
     * */

    //以下参数为图像具体参数，参考串口协议
    uint32_t details_a: 9;
    uint32_t details_b: 9;
    uint32_t width: 10;
    uint32_t start_x: 11;
    uint32_t start_y: 11;
    uint32_t details_c: 10;
    uint32_t details_d: 11;
    uint32_t details_e: 11;
} figure_data_struct_t;//※一个图形，一个图形。见通信协议25页

/**
  * @brief  选手端绘制一个图形(0x0301)---(0x0101)
  */
typedef struct __packed {
    figure_data_struct_t figure_data_struct;
} interaction_figure_t;

/**
  * @brief  选手端绘制两个图形(0x0301)---(0x0102)
  */
typedef struct __packed {
    figure_data_struct_t figure_data_struct[2];
} interaction_figure_2_t;

/**
  * @brief  选手端绘制五个图形(0x0301)---(0x0103)
  */
typedef struct __packed {
    figure_data_struct_t figure_data_struct[5];
} interaction_figure_5_t;

/**
  * @brief  选手端绘制七个图形(0x0301)---(0x0104)
  */
typedef struct __packed {
    figure_data_struct_t figure_data_struct[7];
} interaction_figure_7_t;

/**
  * @brief  选手端绘制字符(0x0301)---(0x0110)
  */
typedef struct __packed {
    figure_data_struct_t figure_data_struct;
    uint8_t              data[30];
} interaction_characer_t;//字符型

/**
  * @brief costum_interactive_data_t(0x0302)
  */
typedef struct __packed {
    uint8_t data[30];
} ext_custum_interactive_data_t;

/**
  * @brief Interactive information of small map(0x0303)
  */
typedef struct __packed {
    float    target_position_x;
    float    target_position_y;
    float    target_position_z;
    uint8_t  commd_keyboard;
    uint16_t target_robot_ID;
} ext_minimap_t;

/**
  * @brief Picture transmission remote control information(0x0304)
  */
typedef struct __packed {
    int16_t  mouse_x;
    int16_t  mouse_y;
    int16_t  mouse_z;
    int8_t   left_button_down;
    int8_t   right_button_down;
    uint16_t keyboard_value;
    uint16_t reserved;
} ext_interactive_information_t;

/**
  * @brief  接收数据结构体实例化
  */
typedef struct {
    game_status_t                  game_status_data;              //0x0001
    game_result_t                  game_result_data;              //0x0002
    game_robot_HP_t                game_robot_HP_data;             //0x0003
    event_data_t                   event_data;                    //0x0101
    ext_supply_projectile_action_t supply_projectile_action_data; //0x0102
    referee_warning_t              referee_warning_data;          //0x0104
    dart_remaining_time_t          dart_remaining_data;           //0x0105
    robot_status_t                 robot_status_data;             //0x0201
    power_heat_data_t              power_heat_data;               //0x0202
    robot_pos_t                    robot_pos_data;                //0x0203
    buff_t                         buff_data;                     //0x0204
    air_support_data_t             air_support_data;              //0x0205
    hurt_data_t                    hurt_data;                     //0x0206
    shoot_data_t                   shoot_data;                    //0x0207
    robot_interaction_data_t       robot_interaction_data;
    radar_data_v2_t                radar_data_v2;
    radar_status_frame_t           radar_status_frame;
    radar_location_frame_t         radar_location_frame;
    projectile_allowance_t         projectile_allowance_data;     //0x0208
    rfid_status_t                  rfid_status_data;              //0x0209
    dart_client_cmd_t              dart_client_cmd_data;          //0x020A
    ext_custum_interactive_data_t  custom_interactive_data;       //0x0302
    ext_minimap_t                  mini_map_data;                 //0x0303
    ext_interactive_information_t  interactive_information_data;  //0x0304
} receive_judge_t;

/**
  * @brief  机器人发送给裁判系统的数据结构体集
  */
typedef struct{
    interaction_layer_delete_t  Delete_Graph;
    interaction_figure_t  Single_Graph;
    interaction_figure_2_t  Double_Graph;
    interaction_figure_5_t  Five_Graph;
    interaction_figure_7_t  Seven_Graph;
    interaction_characer_t  Character_Graph;
} send_judge_t;

/* -------------------------------串口数据相关结构体----------------------------------*/
typedef struct {
    UART_HandleTypeDef *huart;
    uint8_t tx_finish_flag; //发送数据完成标志位
    osEventFlagsId_t event; //配置串口事件，便于接收到数据后在相应task中解包

    fifo_s_t *data_fifo;    //接收数据FIFO
    uint16_t buff_size;     //FIFO中内存大小
    uint8_t *buff;          //FIFO中存储对于数组
    uint16_t read_index;
    uint16_t write_index;
} usart_param_struct;

/* -------------------------------裁判系统数据保存结构体----------------------------------*/
typedef struct {
    uint8_t judgement_lost_flag;               //裁判系统丢失标志位，为1则裁判系统数据丢失
    uint8_t robot_id;
    uint8_t robot_level;                       //机器人最高等级
    uint16_t shooter_barrel_cooling_value;    //机器人枪口每秒冷却值
    uint16_t shooter_barrel_heat_limit;   //机器人枪口热量上限
    uint16_t chassis_power_limit;              //机器人底盘功率上限
    uint8_t recovery_buff;                     //机器人回血增益(百分比，10为每秒回复10%最大血量)
    uint8_t cooling_buff;                      //机器人枪口冷却倍率
    uint8_t defence_buff;                      //机器人防御增益(百分比)
    uint16_t attack_buff;                      //机器人攻击增益(百分比)
} judgement_protection_struct;
//收到裁判系统数据处理函数
void judgement_uart_init(void);
void dataFilter(uint16_t cmd_id);
void judgement_protect_handler(uint16_t cmd_id);
void usart_rx_processed(usart_param_struct * _param,uint16_t Size);
void unpack_fifo_data(unpack_data_t *p_obj, uint8_t sof);

//给裁判系统发送数据处理函数
uint32_t send_packed_fifo_data(uint8_t sof);
void StuInteractiveData(void);
void Graph_send(void);
void data_packet_pack(uint16_t cmd_id, uint8_t *p_data, uint16_t len,robot_interaction_data_t robot_interaction_data_);
uint8_t *protocol_packet_pack(uint16_t cmd_id, uint8_t *p_data, uint16_t len, uint8_t *tx_buf,robot_interaction_data_t robot_interaction_data_);
extern receive_judge_t judge_rece_mesg;

//UI绘制
void AddUI();
void UpdateUI();

void addLegLength(void);
void addSuper_Cap(void);
void addBead(void);
void addModeV1();
void addModeV2(void);
void addModeBoxV1(void);
void addStatus(void);
void addTarget(void);
void addPosition(void);
void addEnemyInf(void);

void updateLegLength(void);
void updatePosition(void);
void updateModeV1(void);
void updateStatus();
void updateEnemyInf(void);

#endif //INFANTRYCHASIS_JUDGE_DRIVER_COMMUNICATE_H
