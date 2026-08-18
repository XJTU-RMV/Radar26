//
// Created by liaoyang on 2023-12-11.
//

/* -------------------------------based on serial communication protocol 20230707 edition----------------------------*/
#include "driver_judge.h"
#include "cmsis_os.h"
#include "driver_chassis.h"
#include "data_fifo.h"
#include "bsp_usart.h"
#include "task_judge.h"
#include "driver_power.h"
//----------------------------------------------初始化-----------------------------------------------------------//
/* 避免fifo_s被多个任务同时占用 */
/* 接收数据结构体互斥量 */
static osMutexId    judge_rxdata_mutex;
const osMutexAttr_t judge_rxdata_mutex_attr      = {
        .name = "judge_rxdata_mutex"
};

/* 发送数据结构体互斥量 */
static osMutexId         judge_txdata_mutex;
const osMutexAttr_t      judge_txdata_mutex_attr = {
        .name = "judge_txdata_mutex"
};

/* 接收与传输FIFO结构体 */
static fifo_s_t     judge_rxdata_fifo;
static fifo_s_t     judge_txdata_fifo;
/* Fifo中存储数组 */
static uint8_t      judge_rxdata_buf[JUDGE_FIFO_BUF_LEN];
static uint8_t      judge_txdata_buf[JUDGE_FIFO_BUF_LEN];

/* 接收到的数据包 */
unpack_data_t     judge_unpack_obj;
/* 串口相关参数结构体(包括DMA地址) */
usart_param_struct judgement_usart;
/* 裁判系统数据保护结构体 */
judgement_protection_struct judgement_protection;
/* DMA传输数据的内存地址 */
uint8_t judge_dma_rxbuff[UART_RX_DMA_SIZE];


extern float SuperCVoltage;


/**
  * @brief  uart relevant structure init.
  * @param  None
  * @retval None
  */
void judgement_uart_init(void)
{
    /* 创建收发数据互斥量 */
    judge_rxdata_mutex = osMutexNew(&judge_rxdata_mutex_attr);
    judge_txdata_mutex = osMutexNew(&judge_txdata_mutex_attr);

    /* FIFO初始化 */
    fifo_s_init(&judge_rxdata_fifo, judge_rxdata_buf, JUDGE_FIFO_BUF_LEN, judge_rxdata_mutex);
    fifo_s_init(&judge_txdata_fifo, judge_txdata_buf, JUDGE_FIFO_BUF_LEN, judge_txdata_mutex);

    /* 串口相关参数结构体配置 */
    judgement_usart.huart             = &huart6;
    judgement_usart.event             = refereeEventHandle;        //配置串口事件，便于接收到数据后在相应task中解包
    judgement_usart.tx_finish_flag    = 1;
    judgement_usart.data_fifo         = &judge_rxdata_fifo;        //接收数据FIFO结构体
    judgement_usart.buff_size         = UART_RX_DMA_SIZE;          //接收数据数组长度
    judgement_usart.buff              = judge_dma_rxbuff;          //DMA传输数据存入数组地址

    /* 结构体存放接收到的数据 */
    judge_unpack_obj.data_fifo        = &judge_rxdata_fifo;        //和judgement_usart结构体公用FIFO，在中断中将数据存入FIFO，在任务中解算FIFO中数据
    judge_unpack_obj.frame_header     = (frame_header_t *) judge_unpack_obj.protocol_packet; //数据包中信息数据
    judge_unpack_obj.index            = 0;
    judge_unpack_obj.data_len         = 0;
    judge_unpack_obj.unpack_step      = STEP_HEADER_SOF;

    //开启第一次数据接收，此时也使能了串口空闲中断
    HAL_UARTEx_ReceiveToIdle_DMA(judgement_usart.huart,judgement_usart.buff,judgement_usart.buff_size);
}



//----------------------------------------------协议处理-----------------------------------------------------------//

//裁判系统数据接收
/* 包括所有包的数据结构体 */
receive_judge_t judge_rece_mesg;

uint8_t SupplyingFlag;
extern uint16_t judge_chassis_power_buffer_flag;
uint16_t radar_cnt;
//-----------------------------------------裁判系统数据解算-----------------------------------------------------//
/**
  * @brief  根据不同包ID将数据拷贝进对应数据结构体中
  * @param  *p_frame
  * @retval None
  */
void judgement_data_handler(uint8_t *data_packet) {
    frame_header_t *p_header = (frame_header_t *) data_packet;//前五个字节为frame_header数据
    memcpy(p_header, data_packet, HEADER_LEN);

    uint16_t data_length = p_header->data_length;
    uint16_t cmd_id      = *(uint16_t *) (data_packet + HEADER_LEN);
    uint8_t  *data_addr  = data_packet + HEADER_LEN + CMD_LEN;

    switch (cmd_id) {
        case GAME_STATUS_ID:
            if(data_length!=11)
            {
                break;
            }
            else
            {
                memcpy(&judge_rece_mesg.game_status_data, data_addr, data_length);
                break;
            }
        case GAME_RESULT_ID:
            if(data_length!=1)
            {
                break;
            }
            else
            {
                memcpy(&judge_rece_mesg.game_result_data, data_addr, data_length);
                break;
            }
        case GAME_ROBOT_HP_ID://机器人血量数据
            if(data_length!=16)
            {
                break;
            }
            else
            {
                memcpy(&judge_rece_mesg.game_robot_HP_data, data_addr, data_length);
                break;
            }
        case EVENT_DATA_ID:
            if(data_length!=4)
            {
                break;
            }
            else
            {
                memcpy(&judge_rece_mesg.event_data, data_addr, data_length);
                break;
            }
        case REFEREE_WARNING_ID://裁判系统警告ID
            if(data_length!=3)
            {
                break;
            }
            else
            {
                memcpy(&judge_rece_mesg.event_data, data_addr, data_length);
                break;
            }
        case ROBOT_STATUS_ID://比赛机器人状态，10HZ
            if(data_length!=13)
            {
                break;
            }
            else
            {
                memcpy(&judge_rece_mesg.robot_status_data, data_addr, data_length);
                dataFilter(cmd_id);
                break;
            }
            break;
        case POWER_HEAT_DATA_ID://实时功率热量数据，50HZ
            if(data_length!=14)
            {
                break;
            }
            else
            {
                memcpy(&judge_rece_mesg.power_heat_data, data_addr, data_length);
                dataFilter(cmd_id);
                judge_chassis_power_buffer_flag = 1;
                break;
            }
            break;
        case ROBOT_POS_ID://机器人位置，10HZ
            if(data_length!=12)
            {
                break;
            }
            else
            {
                memcpy(&judge_rece_mesg.robot_pos_data, data_addr, data_length);
                break;
            }
        case BUFF_ID://机器人增益，状态改变后发送
            if(data_length!=6)
            {
                break;
            }
            else
            {
                memcpy(&judge_rece_mesg.buff_data, data_addr, data_length);
                break;
            }
        case HURT_ID://伤害状态，伤害发生后发送
            if(data_length!=1)
            {
                break;
            }
            else
            {
                memcpy(&judge_rece_mesg.hurt_data, data_addr, data_length);
                break;
            }
        case SHOOT_DATA_ID://实时射击信息，射击后发送
            if(data_length!=7)
            {
                break;
            }
            else
            {
                memcpy(&judge_rece_mesg.shoot_data, data_addr, data_length);
            }
            break;
        case PROJECTILE_ALLOWANCE_ID://允许发弹量，10Hz
            if(data_length!=8)
            {
                break;
            }
            else
            {
                memcpy(&judge_rece_mesg.projectile_allowance_data, data_addr, data_length);
                break;
            }
        case RFID_STATUS_ID://机器人RFID状态
            if(data_length!=5)
            {
                break;
            }
            else
            {
                memcpy(&judge_rece_mesg.rfid_status_data, data_addr, data_length);
                break;
            }
        case ROBO_INTERACTION_DATA_ID://雷达发送的解析信息
            {
                radar_cnt = radar_cnt < 1000?radar_cnt + 1:0;
                memcpy(&judge_rece_mesg.radar_data_v2, data_addr, data_length);
                if(judge_rece_mesg.radar_data_v2.crc_ID == 0xA5)
                {
                    switch((radar_msg_id_t)judge_rece_mesg.radar_data_v2.msg_ID)
                    {
                    case radar_msg_status:
                        //处理状态类消息
                        memcpy(&judge_rece_mesg.radar_status_frame, judge_rece_mesg.radar_data_v2.msg, sizeof(radar_status_frame_t));//TODO:绘制敌方信息ui
                        break;
                    case radar_msg_location:
                        //处理位置类消息
                        memcpy(&judge_rece_mesg.radar_location_frame, judge_rece_mesg.radar_data_v2.msg, sizeof(radar_location_frame_t));
                        break;
                    default:
                        //未知消息ID，进行错误处理
                        break;
                    }
                }
                else
                {
                    break;
                }
            }

        default:
            break;
    }
    //接收到无误数据，喂狗
    LostCounterFeed(JUDGEMENT_LOST_COUNT);
}

/**
  * @brief  滤掉数据包中大小异常数据
  *
  */
void dataFilter(uint16_t cmd_id)
{
    if(cmd_id == ROBOT_STATUS_ID)
    {
        //检查等级数据是否出现问题
        if(judge_rece_mesg.robot_status_data.robot_level < judgement_protection.robot_level)
        {
            judge_rece_mesg.robot_status_data.robot_level = judgement_protection.robot_level;
        }

        if(judge_rece_mesg.robot_status_data.chassis_power_limit >=120)
        {
            judge_rece_mesg.robot_status_data.chassis_power_limit = 120;
        }
        else if(judge_rece_mesg.robot_status_data.chassis_power_limit <= 35)
        {
            judge_rece_mesg.robot_status_data.chassis_power_limit = 35;
        }
    }
}

/**
  * @brief  解包
  */
void unpack_fifo_data(unpack_data_t *p_obj, uint8_t sof)
{
    uint8_t byte = 0;

    while (fifo_used_count(p_obj->data_fifo))
    {
        // 获取下一个字节数据
        byte = fifo_s_get(p_obj->data_fifo);
        switch (p_obj->unpack_step)
        {
            case STEP_HEADER_SOF:
            {
                if (byte == sof)
                {
                    p_obj->unpack_step = STEP_LENGTH_LOW;
                    p_obj->protocol_packet[p_obj->index++] = byte;
                }
                else
                {
                    p_obj->index = 0;
                }
            }
                break;

            case STEP_LENGTH_LOW:
            {
                p_obj->data_len = byte;
                p_obj->protocol_packet[p_obj->index++] = byte;
                p_obj->unpack_step = STEP_LENGTH_HIGH;
            }
                break;

            case STEP_LENGTH_HIGH:
            {
                p_obj->data_len |= (byte << 8);
                p_obj->protocol_packet[p_obj->index++] = byte;
                //当收到数据长度小于协议中数据最长长度时
                if (p_obj->data_len < (PROTOCOL_DATA_MAX_SIZE))
                {
                    p_obj->unpack_step = STEP_FRAME_SEQ;
                }
                else
                {
                    // 数据帧长度异常时
                    p_obj->unpack_step = STEP_HEADER_SOF;
                    p_obj->index       = 0;
                }
            }
                break;

            case STEP_FRAME_SEQ:
            {
                p_obj->protocol_packet[p_obj->index++] = byte;
                p_obj->unpack_step = STEP_HEADER_CRC8;
            }
                break;

            case STEP_HEADER_CRC8:
            {
                p_obj->protocol_packet[p_obj->index++] = byte;

                if (p_obj->index == HEADER_LEN)
                {
                    //帧头CRC校验正常时
                    if (verify_crc8_check_sum(p_obj->protocol_packet, HEADER_LEN))
                    {
                        p_obj->unpack_step = STEP_DATA_CRC16;
                    }
                    else
                    {
                        //帧头CRC校验异常，返回初始时
                        p_obj->unpack_step = STEP_HEADER_SOF;
                        p_obj->index       = 0;
                    }
                }
                else
                {
                    //收到frame_header长度异常
                    p_obj->unpack_step = STEP_HEADER_SOF;
                    p_obj->index       = 0;
                }
            }
                break;

            case STEP_DATA_CRC16:
            {
                if (p_obj->index < (HEADER_LEN + CMD_LEN + p_obj->data_len + CRC_LEN))
                {
                    p_obj->protocol_packet[p_obj->index++] = byte;
                }

                if (p_obj->index >= (HEADER_LEN + CMD_LEN + p_obj->data_len + CRC_LEN))
                {
                    p_obj->unpack_step = STEP_HEADER_SOF;
                    p_obj->index       = 0;

                    if (verify_crc16_check_sum(p_obj->protocol_packet,HEADER_LEN + CMD_LEN + p_obj->data_len + CRC_LEN))
                    {
                        //命令码
                        uint16_t cmd_id  = *(uint16_t *) (p_obj->protocol_packet + HEADER_LEN);
                        //开始数据解算
                        judgement_data_handler(p_obj->protocol_packet);
                        //数据正常，存入保护数组
                        judgement_protect_handler(cmd_id);
                    }
                }
            }
                break;

            default:
            {
                p_obj->unpack_step = STEP_HEADER_SOF;
                p_obj->index       = 0;
            }
                break;
        }
    }
}

/**
  * @brief  收到数据时存入保护数组，当裁判系统数据丢失时可使用最后一次裁判系统传来数据
  */
void judgement_protect_handler(uint16_t cmd_id)
{
    judgement_protection.judgement_lost_flag = 0;
    switch(cmd_id)
    {
        case ROBOT_STATUS_ID://比赛机器人状态
            judgement_protection.robot_id = judge_rece_mesg.robot_status_data.robot_id;
            judgement_protection.robot_level = judge_rece_mesg.robot_status_data.robot_level;
            judgement_protection.shooter_barrel_cooling_value = judge_rece_mesg.robot_status_data.shooter_barrel_cooling_value;
            judgement_protection.shooter_barrel_heat_limit = judge_rece_mesg.robot_status_data.shooter_barrel_heat_limit;
            judgement_protection.chassis_power_limit = judge_rece_mesg.robot_status_data.chassis_power_limit;
            break;
        case BUFF_ID://机器人增益
            judgement_protection.attack_buff = judge_rece_mesg.buff_data.attack_buff;
            judgement_protection.recovery_buff = judge_rece_mesg.buff_data.recovery_buff;
            judgement_protection.cooling_buff = judge_rece_mesg.buff_data.cooling_buff;
            judgement_protection.defence_buff = judge_rece_mesg.buff_data.defence_buff;
            break;
        default:
            break;
    }

}

/**
  * @brief  将DMA　buffer中数据传给FIFO
  */
void usart_rx_processed(usart_param_struct * _param,uint16_t Size)
{
    static uint8_t Rx_buf_pos = 0;	//本次回调接收的数据在缓冲区的起点
    uint32_t Rx_length = 0;	    //本次回调接收数据的长度

    /* 该段代码逻辑如下
     * 存在多个包数据传输间间隔太短使得无法获得空闲中断情况，故DMA数组第一位不一定为帧头，而可能为上一次数据
     * 由于buffer中数据是累计的，Size为当前DMA buffer中数据多少
     * 当Size比当前保持位置Rx_buf_pos大时，本次收到实际数据为Rx_buf_pos到Size处数据并将其放入FIFO中
     * 当Size比当前保持数据Rx_buf_pos小时，说明buffer已经装满后重写开始从头写入,故需要将Rx_buf_pos到buff_size位置数据放入FIFO，再将从头0到Size的数据再写入
     * */
    if (Size != Rx_buf_pos)
    {
        if (Size > Rx_buf_pos)
        {
            Rx_length = Size - Rx_buf_pos;
            fifo_s_puts(_param->data_fifo,&_param->buff[Rx_buf_pos], Rx_length);
        }
        else
        {
            Rx_length = _param->buff_size - Rx_buf_pos;
            fifo_s_puts(_param->data_fifo,&_param->buff[Rx_buf_pos], Rx_length);
            if (Size > 0)
            {
                fifo_s_puts(_param->data_fifo,&_param->buff[0], Size);
                Rx_length += Size;
            }
        }
    }
    Rx_buf_pos = Size;
    //事件置位，说明收到数据，允许unpack_task开始解包
    osEventFlagsSet(_param->event,UART_IDLE_SIGNAL);
}



//-----------------------------------------发送数据给裁判系统-----------------------------------------------------//
/* 所有包数据结构体 */
send_judge_t judge_send_msg1,judge_send_msg2,judge_send_msg3,judge_send_mesg, judge_send_msg4;
/* 交互数据 */
robot_interaction_data_t robot_interaction_data;
/* 存储机器人交互数据 */
uint8_t tx_buf[PROTOCOL_FRAME_MAX_SIZE];

/* UI绘制计数器 */
u8 UICount = 0;
/* 添加图形计数器 */
u8 DrawFlag =1 ;
/* 更新图形计数器 */
u8 UpdateFlag = 1;

/*!
 * @brief UI绘图函数接口，判断机器人ID并绘制图像
 */
void StuInteractiveData(void)
{
    //蓝方时
    if(judge_rece_mesg.robot_status_data.robot_id == BLUE_INFANTRY3_ID)//蓝3
    {
        robot_interaction_data.sender_ID     = BLUE_INFANTRY3_ID;
        robot_interaction_data.receiver_ID   = BLUE_INFANTRY3_CUSTOM_ID;
        Graph_send();
    }

    else if(judge_rece_mesg.robot_status_data.robot_id == BLUE_INFANTRY4_ID)//蓝4
    {
        robot_interaction_data.sender_ID     = BLUE_INFANTRY4_ID;
        robot_interaction_data.receiver_ID   = BLUE_INFANTRY4_CUSTOM_ID;
        Graph_send();
    }

    else if(judge_rece_mesg.robot_status_data.robot_id == BLUE_INFANTRY5_ID)//蓝5
    {
        robot_interaction_data.sender_ID     = BLUE_INFANTRY5_ID;
        robot_interaction_data.receiver_ID   = BLUE_INFANTRY5_CUSTOM_ID;
        Graph_send();
    }

    //红方时
    if(judge_rece_mesg.robot_status_data.robot_id == RED_HERO_ID)//红1
    {
        robot_interaction_data.sender_ID     = RED_HERO_ID;
        robot_interaction_data.receiver_ID   = RED_HERO_CUSTOM_ID;
        Graph_send();
    }
    else if(judge_rece_mesg.robot_status_data.robot_id == RED_INFANTRY3_ID)//红3
    {
        robot_interaction_data.sender_ID     = RED_INFANTRY3_ID;
        robot_interaction_data.receiver_ID   = RED_INFANTRY3_CUSTOM_ID;
        Graph_send();
    }
    else if(judge_rece_mesg.robot_status_data.robot_id == RED_INFANTRY4_ID)//红4
    {
        robot_interaction_data.sender_ID     = RED_INFANTRY4_ID;
        robot_interaction_data.receiver_ID   = RED_INFANTRY4_CUSTOM_ID;
        Graph_send();
    }
    else if(judge_rece_mesg.robot_status_data.robot_id == RED_INFANTRY5_ID)//红5
    {
        robot_interaction_data.sender_ID     = RED_INFANTRY5_ID;
        robot_interaction_data.receiver_ID   = RED_INFANTRY5_CUSTOM_ID;
        Graph_send();
    }

    //完成数据打包，允许发送
    osEventFlagsSet(refereeEventHandle,UART_TX_SIGNAL);
}
uint8_t draw_flag_finish=0;
/*!
 * @brief 串口给裁判系统发送数据绘制图形
 */
void Graph_send(void)
{
    UICount++;
    UICount = UICount % 60;
    //每30次添加一次UI图像，其余时刻均更新UI图像(更新图形比绘制更快)
    if(UICount % 30 == 0)
        AddUI();
    else
        UpdateUI();

}

/*!
 * @brief 添加图形
 */
void AddUI()
{
    switch(DrawFlag){
        //绘制云台、底盘功能
        case 0:
            addModeV1();
            DrawFlag = 1 ;
            break;
        case 1:
            addModeV2();
            DrawFlag = 2;
            break;
            //绘制功能框
        case 2:
            addModeBoxV1();
            DrawFlag = 3;
            break;
            //绘制状态信息
        case 3:
            addStatus();
            DrawFlag = 4;
            break;
            //绘制电容
        case 4:
            addSuper_Cap();
            DrawFlag = 5;
            break;
            //绘制自瞄框
        case 5:
            addTarget();
            DrawFlag = 6;
            break;
            //绘制腿长
        case 6:
            addLegLength();
            DrawFlag = 7;
            break;
            //绘制瞄准辅助线
        case 7:
            addBead();
            DrawFlag = 8;
            break;
            //绘制准心
        case 8:
            addPosition();
            DrawFlag = 9;
            break;
            //绘制相对方位
        case 9:
            addEnemyInf();
            DrawFlag = 0;
            break;
        default:
            DrawFlag = 0;
            break;
    }
}

/*!
 * @brief 更新图形
 */
uint8_t err_count=0;
uint8_t mode_count=0;
void UpdateUI()
{
    switch(UpdateFlag){
        case 0:
            updateStatus();
            UpdateFlag = 1;
            break;
        case 1:
            updateModeV1();
            UpdateFlag = 2;
            break;
        case 2:
            updateLegLength();
            UpdateFlag = 3;
            break;
        case 3:
            updatePosition();
            UpdateFlag = 4;
            break;
        case 4:
            updateEnemyInf();
            UpdateFlag = 0;
            break;
        default:
            UpdateFlag = 0;
            break;
    }
}

void addLegLength(void)
{
    for (int k=0;k<5;k++)
    {
        judge_send_msg2.Five_Graph.figure_data_struct[k].operate_type = 1;
    }

    strcpy((char*)judge_send_msg2.Five_Graph.figure_data_struct[0].figure_name,"l1");
    judge_send_msg2.Five_Graph.figure_data_struct[0].figure_type               = 1;
    judge_send_msg2.Five_Graph.figure_data_struct[0].layer			  	     = 6;
    judge_send_msg2.Five_Graph.figure_data_struct[0].color                 = 6;
    judge_send_msg2.Five_Graph.figure_data_struct[0].width                 = 10;
    judge_send_msg2.Five_Graph.figure_data_struct[0].start_x               = 1200;
    judge_send_msg2.Five_Graph.figure_data_struct[0].start_y               = 170;
    judge_send_msg2.Five_Graph.figure_data_struct[0].details_d             = 1210;
    judge_send_msg2.Five_Graph.figure_data_struct[0].details_e		        = 180+(int)(leg_posture_array[0].length*100-9)*2;//左腿腿长



    strcpy((char*)judge_send_msg2.Five_Graph.figure_data_struct[1].figure_name,"l2");
    judge_send_msg2.Five_Graph.figure_data_struct[1].figure_type               = 1;
    judge_send_msg2.Five_Graph.figure_data_struct[1].layer			  	     = 6;
    judge_send_msg2.Five_Graph.figure_data_struct[1].color                 = 5;
    judge_send_msg2.Five_Graph.figure_data_struct[1].width                 = 10;
    judge_send_msg2.Five_Graph.figure_data_struct[1].start_x               = 1230;
    judge_send_msg2.Five_Graph.figure_data_struct[1].start_y               = 170;
    judge_send_msg2.Five_Graph.figure_data_struct[1].details_d             = 1240;
    judge_send_msg2.Five_Graph.figure_data_struct[1].details_e		        = 180+(int)(leg_posture_array[1].length*100-9)*2;//右腿腿长
    strcpy((char*)judge_send_msg2.Five_Graph.figure_data_struct[2].figure_name,"13");
    judge_send_msg2.Five_Graph.figure_data_struct[2].figure_type       = 0;
    judge_send_msg2.Five_Graph.figure_data_struct[2].layer			    = 8;
    judge_send_msg2.Five_Graph.figure_data_struct[2].color 		    = 1;
    judge_send_msg2.Five_Graph.figure_data_struct[2].width             = 2;
    judge_send_msg2.Five_Graph.figure_data_struct[2].start_x           = 1190;
    judge_send_msg2.Five_Graph.figure_data_struct[2].start_y           = 165;
    judge_send_msg2.Five_Graph.figure_data_struct[2].details_c         = 0;
    judge_send_msg2.Five_Graph.figure_data_struct[2].details_d		    = 1250;
    judge_send_msg2.Five_Graph.figure_data_struct[2].details_e		    = 165;

    strcpy((char*)judge_send_msg2.Five_Graph.figure_data_struct[3].figure_name,"14");
    judge_send_msg2.Five_Graph.figure_data_struct[3].figure_type       = 0;
    judge_send_msg2.Five_Graph.figure_data_struct[3].layer			    = 8;
    judge_send_msg2.Five_Graph.figure_data_struct[3].color 		    = 1;
    judge_send_msg2.Five_Graph.figure_data_struct[3].width             = 2;
    judge_send_msg2.Five_Graph.figure_data_struct[3].start_x           = 1190;
    judge_send_msg2.Five_Graph.figure_data_struct[3].start_y           = 205;
    judge_send_msg2.Five_Graph.figure_data_struct[3].details_c         = 0;
    judge_send_msg2.Five_Graph.figure_data_struct[3].details_d		    = 1250;
    judge_send_msg2.Five_Graph.figure_data_struct[3].details_e		    = 205;

    strcpy((char*)judge_send_msg2.Five_Graph.figure_data_struct[4].figure_name,"15");
    judge_send_msg2.Five_Graph.figure_data_struct[4].figure_type       = 0;
    judge_send_msg2.Five_Graph.figure_data_struct[4].layer			    = 8;
    judge_send_msg2.Five_Graph.figure_data_struct[4].color 		    = 1;
    judge_send_msg2.Five_Graph.figure_data_struct[4].width             = 2;
    judge_send_msg2.Five_Graph.figure_data_struct[4].start_x           = 1190;
    judge_send_msg2.Five_Graph.figure_data_struct[4].start_y           = 233;
    judge_send_msg2.Five_Graph.figure_data_struct[4].details_c         = 0;
    judge_send_msg2.Five_Graph.figure_data_struct[4].details_d		    = 1250;
    judge_send_msg2.Five_Graph.figure_data_struct[4].details_e		    = 233;

    robot_interaction_data.data_cmd_id = INTERACTION_FIGURE3_ID ;
    data_packet_pack(ROBO_INTERACTION_DATA_ID, (uint8_t *)&judge_send_msg2.Five_Graph,sizeof(judge_send_msg2.Five_Graph), robot_interaction_data);

}

extern SCFeedback_t superCup;
void addSuper_Cap(void)
{
    for (int k =0;k<2;k++)
        judge_send_msg1.Double_Graph.figure_data_struct[k].operate_type = 1;

    strcpy((char*)judge_send_msg1.Double_Graph.figure_data_struct[0].figure_name,"s1");
    judge_send_msg1.Double_Graph.figure_data_struct[0].figure_type               = 1;
    judge_send_msg1.Double_Graph.figure_data_struct[0].layer			  	     = 6;

    if((GetErrorState()>>SUPERC_LOST_COUNT)&1)
    {
        //不可使用，黑色
        judge_send_msg1.Double_Graph.figure_data_struct[0].color                 = 7;
        judge_send_msg1.Double_Graph.figure_data_struct[0].details_a             = 0;
        judge_send_msg1.Double_Graph.figure_data_struct[0].details_b             = 0;
        judge_send_msg1.Double_Graph.figure_data_struct[0].details_c             = 0;
        judge_send_msg1.Double_Graph.figure_data_struct[0].width                 = 20;
        judge_send_msg1.Double_Graph.figure_data_struct[0].start_x               = 700;
        judge_send_msg1.Double_Graph.figure_data_struct[0].start_y               = 45;
        judge_send_msg1.Double_Graph.figure_data_struct[0].details_d             = 1145;
        judge_send_msg1.Double_Graph.figure_data_struct[0].details_e		        = 25;
    }
    else
    {
        //电容正常
        //电容条
        //
        judge_send_msg1.Double_Graph.figure_data_struct[0].color 		  	= 2;
        judge_send_msg1.Double_Graph.figure_data_struct[0].details_a             = 0;
        judge_send_msg1.Double_Graph.figure_data_struct[0].details_b             = 0;
        judge_send_msg1.Double_Graph.figure_data_struct[0].details_c             = 0;
        judge_send_msg1.Double_Graph.figure_data_struct[0].width                 = 20;
        judge_send_msg1.Double_Graph.figure_data_struct[0].start_x               = 700;
        judge_send_msg1.Double_Graph.figure_data_struct[0].start_y               = 45;
        judge_send_msg1.Double_Graph.figure_data_struct[0].details_d	            = 700 + (int)((pow(superCap.voltCap, 2) - 64.0f) * 445.0f / 612.0f);
        if(judge_send_msg1.Double_Graph.figure_data_struct[0].details_d < 700)
            judge_send_msg1.Double_Graph.figure_data_struct[0].details_d         = 700;
        else if(judge_send_msg1.Double_Graph.figure_data_struct[0].details_d > 1145)
            judge_send_msg1.Double_Graph.figure_data_struct[0].details_d         = 1145;
        judge_send_msg1.Double_Graph.figure_data_struct[0].details_e		        = 25;
    }

    //外框
    strcpy((char*)judge_send_msg1.Double_Graph.figure_data_struct[1].figure_name,"s2");
    judge_send_msg1.Double_Graph.figure_data_struct[1].figure_type               = 1;
    judge_send_msg1.Double_Graph.figure_data_struct[1].layer			  	        = 6;
    //
    judge_send_msg1.Double_Graph.figure_data_struct[1].color 		  	    = 8;
    judge_send_msg1.Double_Graph.figure_data_struct[1].details_a                 = 0;
    judge_send_msg1.Double_Graph.figure_data_struct[1].details_b                 = 0;
    judge_send_msg1.Double_Graph.figure_data_struct[1].width                     = 3;
    judge_send_msg1.Double_Graph.figure_data_struct[1].start_x                   = 690;
    judge_send_msg1.Double_Graph.figure_data_struct[1].start_y                   = 55;
    judge_send_msg1.Double_Graph.figure_data_struct[1].details_c                 = 0;
    judge_send_msg1.Double_Graph.figure_data_struct[1].details_d			        = 1135;
    judge_send_msg1.Double_Graph.figure_data_struct[1].details_e			        = 15;

    robot_interaction_data.data_cmd_id = INTERACTION_FIGURE2_ID ;
    data_packet_pack(ROBO_INTERACTION_DATA_ID, (uint8_t *)&judge_send_msg1.Double_Graph,sizeof(judge_send_msg1.Double_Graph), robot_interaction_data);
}


/*!
 * @brief 绘制准星
 */
void addBead(void)
{
    //添加图形
    for (int k=0;k<5;k++)
        judge_send_msg3.Five_Graph.figure_data_struct[k].operate_type = 1;

    strcpy((char*)judge_send_msg3.Five_Graph.figure_data_struct[0].figure_name,"b1");
    judge_send_msg3.Five_Graph.figure_data_struct[0].figure_type       = 0;
    judge_send_msg3.Five_Graph.figure_data_struct[0].layer			    = 8;
    judge_send_msg3.Five_Graph.figure_data_struct[0].color 		    = 8;
    judge_send_msg3.Five_Graph.figure_data_struct[0].details_a         = 0;
    judge_send_msg3.Five_Graph.figure_data_struct[0].details_b         = 0;
    judge_send_msg3.Five_Graph.figure_data_struct[0].width             = 2;
    judge_send_msg3.Five_Graph.figure_data_struct[0].start_x           = 960;
    judge_send_msg3.Five_Graph.figure_data_struct[0].start_y           = 190;
    judge_send_msg3.Five_Graph.figure_data_struct[0].details_c         = 0;
    judge_send_msg3.Five_Graph.figure_data_struct[0].details_d		    = 960;
    judge_send_msg3.Five_Graph.figure_data_struct[0].details_e		    = 540;

    //第二个图形
    strcpy((char*)judge_send_msg3.Five_Graph.figure_data_struct[1].figure_name,"b2");
    judge_send_msg3.Five_Graph.figure_data_struct[1].figure_type       = 0;
    judge_send_msg3.Five_Graph.figure_data_struct[1].layer		 	  	= 8;
    judge_send_msg3.Five_Graph.figure_data_struct[1].color 		  	= 8;
    judge_send_msg3.Five_Graph.figure_data_struct[1].details_a         = 0;
    judge_send_msg3.Five_Graph.figure_data_struct[1].details_b         = 0;
    judge_send_msg3.Five_Graph.figure_data_struct[1].width             = 2;
    judge_send_msg3.Five_Graph.figure_data_struct[1].start_x           = 935 - 80;
    judge_send_msg3.Five_Graph.figure_data_struct[1].start_y           = 490;
    judge_send_msg3.Five_Graph.figure_data_struct[1].details_c         = 0;
    judge_send_msg3.Five_Graph.figure_data_struct[1].details_d	        = 985 + 80;
    judge_send_msg3.Five_Graph.figure_data_struct[1].details_e			= 490;
    //第三个图形
    strcpy((char*)judge_send_msg3.Five_Graph.figure_data_struct[2].figure_name,"b3");

    judge_send_msg3.Five_Graph.figure_data_struct[2].figure_type       = 0;
    judge_send_msg3.Five_Graph.figure_data_struct[2].layer			  	= 8;
    judge_send_msg3.Five_Graph.figure_data_struct[2].color 		    = 8;
    judge_send_msg3.Five_Graph.figure_data_struct[2].details_a         = 0;
    judge_send_msg3.Five_Graph.figure_data_struct[2].details_b         = 0;
    judge_send_msg3.Five_Graph.figure_data_struct[2].width             = 2;
    judge_send_msg3.Five_Graph.figure_data_struct[2].start_x           = 935 - 60;
    judge_send_msg3.Five_Graph.figure_data_struct[2].start_y           = 440;
    judge_send_msg3.Five_Graph.figure_data_struct[2].details_c         = 0;
    judge_send_msg3.Five_Graph.figure_data_struct[2].details_d			= 985 + 60;
    judge_send_msg3.Five_Graph.figure_data_struct[2].details_e			= 440;
    //第四个图形
    strcpy((char*)judge_send_msg3.Five_Graph.figure_data_struct[3].figure_name,"b4");
    judge_send_msg3.Five_Graph.figure_data_struct[3].figure_type       = 0;
    judge_send_msg3.Five_Graph.figure_data_struct[3].layer			  	= 8;
    judge_send_msg3.Five_Graph.figure_data_struct[3].color 		  	= 8;
    judge_send_msg3.Five_Graph.figure_data_struct[3].details_a         = 0;
    judge_send_msg3.Five_Graph.figure_data_struct[3].details_b         = 0;
    judge_send_msg3.Five_Graph.figure_data_struct[3].width             = 2;
    judge_send_msg3.Five_Graph.figure_data_struct[3].start_x           = 935 - 40;
    judge_send_msg3.Five_Graph.figure_data_struct[3].start_y           = 390;
    judge_send_msg3.Five_Graph.figure_data_struct[3].details_c         = 0;
    judge_send_msg3.Five_Graph.figure_data_struct[3].details_d			= 985 + 40;
    judge_send_msg3.Five_Graph.figure_data_struct[3].details_e			= 390;

    strcpy((char*)judge_send_msg3.Five_Graph.figure_data_struct[4].figure_name,"b5");
    judge_send_msg3.Five_Graph.figure_data_struct[4].figure_type       = 0;
    judge_send_msg3.Five_Graph.figure_data_struct[4].layer			  	= 8;
    judge_send_msg3.Five_Graph.figure_data_struct[4].color 		  	= 8;
    judge_send_msg3.Five_Graph.figure_data_struct[4].details_a         = 0;
    judge_send_msg3.Five_Graph.figure_data_struct[4].details_b         = 0;
    judge_send_msg3.Five_Graph.figure_data_struct[4].width             = 2;
    judge_send_msg3.Five_Graph.figure_data_struct[4].start_x           = 935 - 20;
    judge_send_msg3.Five_Graph.figure_data_struct[4].start_y           = 340;
    judge_send_msg3.Five_Graph.figure_data_struct[4].details_c         = 0;
    judge_send_msg3.Five_Graph.figure_data_struct[4].details_d			= 985 + 20;
    judge_send_msg3.Five_Graph.figure_data_struct[4].details_e		    = 340;

    robot_interaction_data.data_cmd_id = INTERACTION_FIGURE3_ID ;
    data_packet_pack(ROBO_INTERACTION_DATA_ID, (uint8_t *)&judge_send_msg3.Five_Graph,sizeof(judge_send_msg3.Five_Graph), robot_interaction_data);
}

/*!
 * @brief 绘制模式文字（联盟赛版本）
 */
void addModeV1(void)
{
    judge_send_msg1.Character_Graph.figure_data_struct.operate_type     = 1;
    judge_send_msg1.Character_Graph.figure_data_struct.figure_type      = 7;
    judge_send_msg1.Character_Graph.figure_data_struct.layer			= 5;
    judge_send_msg1.Character_Graph.figure_data_struct.color 		  	= 6;
    judge_send_msg1.Character_Graph.figure_data_struct.details_a        = 20;
    judge_send_msg1.Character_Graph.figure_data_struct.details_b        = 7;
    judge_send_msg1.Character_Graph.figure_data_struct.width            = 3;

    //初始化一下
    for (int i=0;i<30;i++)
        judge_send_msg1.Character_Graph.data[i]=0;

    strcpy((char*)judge_send_msg1.Character_Graph.figure_data_struct.figure_name,"m1" );
    judge_send_msg1.Character_Graph.figure_data_struct.start_x = 750;
    judge_send_msg1.Character_Graph.figure_data_struct.start_y = 830;
    strcat((char*)judge_send_msg1.Character_Graph.data, "FRI  XJTU  SPIN  AXIAL");



    robot_interaction_data.data_cmd_id = INTERACTION_CHARACTER_ID ;
    data_packet_pack(ROBO_INTERACTION_DATA_ID, (uint8_t *)&judge_send_msg1.Character_Graph,
                     sizeof(judge_send_msg1.Character_Graph), robot_interaction_data);
}

void addModeV2(void)
{
    static int text_cnt = 0;
    judge_send_msg2.Character_Graph.figure_data_struct.operate_type     = 1;
    judge_send_msg2.Character_Graph.figure_data_struct.figure_type      = 7;
    judge_send_msg2.Character_Graph.figure_data_struct.layer			= 5;
    judge_send_msg2.Character_Graph.figure_data_struct.color 		  	= 2;
    judge_send_msg2.Character_Graph.figure_data_struct.details_a        = 20;
    judge_send_msg2.Character_Graph.figure_data_struct.details_b        = 7;
    judge_send_msg2.Character_Graph.figure_data_struct.width            = 3;

    for (int i=0;i<30;i++)
        judge_send_msg2.Character_Graph.data[i]=0;
    if(text_cnt == 0){
        strcpy((char*)judge_send_msg2.Character_Graph.figure_data_struct.figure_name,"m2" );
        judge_send_msg2.Character_Graph.figure_data_struct.color 		  	= 2;
        judge_send_msg2.Character_Graph.figure_data_struct.start_x = 250;
        judge_send_msg2.Character_Graph.figure_data_struct.start_y = 830;
        strcat((char*)judge_send_msg2.Character_Graph.data, "BULLETS: \n\n\n\nAUTO_AIM\n\nENERGY");
        text_cnt = 1;
    }else{
        strcpy((char*)judge_send_msg2.Character_Graph.figure_data_struct.figure_name,"m3" );
        judge_send_msg2.Character_Graph.figure_data_struct.start_x = 1500;
        judge_send_msg2.Character_Graph.figure_data_struct.start_y = 830;
        strcat((char*)judge_send_msg2.Character_Graph.data, "ENEMY: \n\n\n\nUP2\nDOWN2\nANTIF\nHS");
        text_cnt = 0;
    }
    robot_interaction_data.data_cmd_id = INTERACTION_CHARACTER_ID ;
    data_packet_pack(ROBO_INTERACTION_DATA_ID, (uint8_t *)&judge_send_msg2.Character_Graph,
                     sizeof(judge_send_msg2.Character_Graph), robot_interaction_data);
}

/*!
 * @brief 绘制当前模式盒子
 */
uint16_t enemy;

void addModeBoxV1(void)
{
    for(int i=0;i<7;i++)
    {
        judge_send_msg1.Seven_Graph.figure_data_struct[i].operate_type=1;
    }

    //摩擦轮
    strcpy((char*)judge_send_msg1.Seven_Graph.figure_data_struct[0].figure_name,"B1");
    judge_send_msg1.Seven_Graph.figure_data_struct[0].figure_type=1;
    judge_send_msg1.Seven_Graph.figure_data_struct[0].color=4;
    judge_send_msg1.Seven_Graph.figure_data_struct[0].width=2;
    if(controlSignal.controlFlag.friFlag)
    {
        judge_send_msg1.Seven_Graph.figure_data_struct[0].start_y=840;
        judge_send_msg1.Seven_Graph.figure_data_struct[0].start_x=735;
        judge_send_msg1.Seven_Graph.figure_data_struct[0].details_d=820;
        judge_send_msg1.Seven_Graph.figure_data_struct[0].details_e=800;
    }

    //底盘功能
    strcpy((char*)judge_send_msg1.Seven_Graph.figure_data_struct[1].figure_name,"B2");
    judge_send_msg1.Seven_Graph.figure_data_struct[1].figure_type=1;
    judge_send_msg1.Seven_Graph.figure_data_struct[1].color=4;
    judge_send_msg1.Seven_Graph.figure_data_struct[1].width=2;
    if(controlSignal.controlFlag.spinFlag)
    {
        judge_send_msg1.Seven_Graph.figure_data_struct[1].start_y=840;
        judge_send_msg1.Seven_Graph.figure_data_struct[1].start_x=960;
        judge_send_msg1.Seven_Graph.figure_data_struct[1].details_d=1030;
        judge_send_msg1.Seven_Graph.figure_data_struct[1].details_e=800;
    }
    else if(controlSignal.controlFlag.axialFlag)
    {
        judge_send_msg1.Seven_Graph.figure_data_struct[1].start_y=840;
        judge_send_msg1.Seven_Graph.figure_data_struct[1].start_x=1060;
        judge_send_msg1.Seven_Graph.figure_data_struct[1].details_d=1165;
        judge_send_msg1.Seven_Graph.figure_data_struct[1].details_e=800;
    }
    else if(controlSignal.controlFlag.upstairFlag == 1)
    {
        judge_send_msg1.Seven_Graph.figure_data_struct[1].start_y=715;
        judge_send_msg1.Seven_Graph.figure_data_struct[1].start_x=1495;
        judge_send_msg1.Seven_Graph.figure_data_struct[1].details_d=1595;
        judge_send_msg1.Seven_Graph.figure_data_struct[1].details_e=685;
    }
    else if(controlSignal.controlFlag.jumpFlag_low == 1)
    {
        judge_send_msg1.Seven_Graph.figure_data_struct[1].start_y=685;
        judge_send_msg1.Seven_Graph.figure_data_struct[1].start_x=1495;
        judge_send_msg1.Seven_Graph.figure_data_struct[1].details_d=1595;
        judge_send_msg1.Seven_Graph.figure_data_struct[1].details_e=655;
    }
    else if(controlSignal.controlFlag.jumpFlag_high == 1)
    {
        judge_send_msg1.Seven_Graph.figure_data_struct[1].start_y=655;
        judge_send_msg1.Seven_Graph.figure_data_struct[1].start_x=1495;
        judge_send_msg1.Seven_Graph.figure_data_struct[1].details_d=1595;
        judge_send_msg1.Seven_Graph.figure_data_struct[1].details_e=625;
    }
    else
    {
        judge_send_msg1.Seven_Graph.figure_data_struct[1].start_x=840;
        judge_send_msg1.Seven_Graph.figure_data_struct[1].start_y=840;
        judge_send_msg1.Seven_Graph.figure_data_struct[1].details_d=930;
        judge_send_msg1.Seven_Graph.figure_data_struct[1].details_e=800;
    }
    //打符
    strcpy((char*)judge_send_msg1.Seven_Graph.figure_data_struct[2].figure_name,"B3");
    judge_send_msg1.Seven_Graph.figure_data_struct[2].operate_type=1;
    judge_send_msg1.Seven_Graph.figure_data_struct[2].figure_type=1;
    judge_send_msg1.Seven_Graph.figure_data_struct[2].color=4;
    judge_send_msg1.Seven_Graph.figure_data_struct[2].width=2;
    if(controlSignal.controlFlag.visionType==1)
    {
        judge_send_msg1.Seven_Graph.figure_data_struct[2].start_y=715;
        judge_send_msg1.Seven_Graph.figure_data_struct[2].start_x=245;
        judge_send_msg1.Seven_Graph.figure_data_struct[2].details_d=410;
        judge_send_msg1.Seven_Graph.figure_data_struct[2].details_e=685;
    }
    else if(controlSignal.controlFlag.visionType==2)
    {
        judge_send_msg1.Seven_Graph.figure_data_struct[2].start_y=655;
        judge_send_msg1.Seven_Graph.figure_data_struct[2].start_x=245;
        judge_send_msg1.Seven_Graph.figure_data_struct[2].details_d=410;
        judge_send_msg1.Seven_Graph.figure_data_struct[2].details_e=625;
    }
    else
    {
        judge_send_msg1.Seven_Graph.figure_data_struct[2].start_y=715;
        judge_send_msg1.Seven_Graph.figure_data_struct[2].start_x=245;
        judge_send_msg1.Seven_Graph.figure_data_struct[2].details_d=245;
        judge_send_msg1.Seven_Graph.figure_data_struct[2].details_e=715;
    }
    //允许发弹量
    int bullet=judge_rece_mesg.projectile_allowance_data.projectile_allowance_17mm;
    if(bullet < - 1024)
    {
        bullet = -1024;
    }
    strcpy((char*)judge_send_msg1.Seven_Graph.figure_data_struct[3].figure_name,"B4");
    judge_send_msg1.Seven_Graph.figure_data_struct[3].figure_type=6;
    judge_send_msg1.Seven_Graph.figure_data_struct[3].color=6;
    judge_send_msg1.Seven_Graph.figure_data_struct[3].width=3;
    judge_send_msg1.Seven_Graph.figure_data_struct[3].start_y=780;
    judge_send_msg1.Seven_Graph.figure_data_struct[3].start_x=320;
    judge_send_msg1.Seven_Graph.figure_data_struct[3].details_a=30;
    if(bullet>=0)
    {
        judge_send_msg1.Seven_Graph.figure_data_struct[3].details_c=bullet % 1024;
        judge_send_msg1.Seven_Graph.figure_data_struct[3].details_d=bullet / 1024;
        judge_send_msg1.Seven_Graph.figure_data_struct[3].details_e=0;
    }
    else
    {
        judge_send_msg1.Seven_Graph.figure_data_struct[3].details_c=bullet;
        judge_send_msg1.Seven_Graph.figure_data_struct[3].details_d=-1;
        judge_send_msg1.Seven_Graph.figure_data_struct[3].details_e=-1;
    }

    strcpy((char*)judge_send_msg1.Seven_Graph.figure_data_struct[4].figure_name,"B5");
    judge_send_msg1.Seven_Graph.figure_data_struct[4].figure_type=1;
    judge_send_msg1.Seven_Graph.figure_data_struct[4].color=4;
    judge_send_msg1.Seven_Graph.figure_data_struct[4].width=2;
    if (controlSignal.controlFlag.fast_mode)
    {
        judge_send_msg1.Seven_Graph.figure_data_struct[4].start_y=625;
        judge_send_msg1.Seven_Graph.figure_data_struct[4].start_x=1495;
        judge_send_msg1.Seven_Graph.figure_data_struct[4].details_d=1595;
        judge_send_msg1.Seven_Graph.figure_data_struct[4].details_e=595;
    }else
    {
        judge_send_msg1.Seven_Graph.figure_data_struct[4].start_x=840;
        judge_send_msg1.Seven_Graph.figure_data_struct[4].start_y=840;
        judge_send_msg1.Seven_Graph.figure_data_struct[4].details_d=930;
        judge_send_msg1.Seven_Graph.figure_data_struct[4].details_e=800;
    }

    //第六个图形  外框
    strcpy((char*)judge_send_msg1.Seven_Graph.figure_data_struct[5].figure_name,"b6");
    judge_send_msg1.Seven_Graph.figure_data_struct[5].figure_type       = 0;
    judge_send_msg1.Seven_Graph.figure_data_struct[5].layer			  	= 8;
    judge_send_msg1.Seven_Graph.figure_data_struct[5].color 		  	= 4;
    judge_send_msg1.Seven_Graph.figure_data_struct[5].details_a         = 0;
    judge_send_msg1.Seven_Graph.figure_data_struct[5].details_b         = 0;
    judge_send_msg1.Seven_Graph.figure_data_struct[5].width             = 2;
    judge_send_msg1.Seven_Graph.figure_data_struct[5].start_x           = 400;
    judge_send_msg1.Seven_Graph.figure_data_struct[5].start_y           = 0;
    judge_send_msg1.Seven_Graph.figure_data_struct[5].details_c         = 0;
    judge_send_msg1.Seven_Graph.figure_data_struct[5].details_d			= 622;
    judge_send_msg1.Seven_Graph.figure_data_struct[5].details_e			= 333;
    //第七个图形  外
    strcpy((char*)judge_send_msg1.Seven_Graph.figure_data_struct[6].figure_name,"b7");
    judge_send_msg1.Seven_Graph.figure_data_struct[6].figure_type       = 0;
    judge_send_msg1.Seven_Graph.figure_data_struct[6].layer			  	= 8;
    judge_send_msg1.Seven_Graph.figure_data_struct[6].color 		  	= 4;
    judge_send_msg1.Seven_Graph.figure_data_struct[6].details_a         = 0;
    judge_send_msg1.Seven_Graph.figure_data_struct[6].details_b         = 0;
    judge_send_msg1.Seven_Graph.figure_data_struct[6].width             = 2;
    judge_send_msg1.Seven_Graph.figure_data_struct[6].start_x           = 1550;
    judge_send_msg1.Seven_Graph.figure_data_struct[6].start_y           = 0;
    judge_send_msg1.Seven_Graph.figure_data_struct[6].details_c         = 0;
    judge_send_msg1.Seven_Graph.figure_data_struct[6].details_d			= 1328;
    judge_send_msg1.Seven_Graph.figure_data_struct[6].details_e			= 333;

//    if(controlSignal.controlFlag.axialFlag)
//    {
//        judge_send_msg1.Seven_Graph.figure_data_struct[5].start_y = judge_send_msg1.Seven_Graph.figure_data_struct[5].details_e;
//        judge_send_msg1.Seven_Graph.figure_data_struct[6].start_y = judge_send_msg1.Seven_Graph.figure_data_struct[6].details_e;
//    }

    robot_interaction_data.data_cmd_id = INTERACTION_FIGURE4_ID ;
    data_packet_pack(ROBO_INTERACTION_DATA_ID, (uint8_t *)&judge_send_msg1.Seven_Graph,
                     sizeof(judge_send_msg1.Seven_Graph), robot_interaction_data);
}
/*!
 * @brief 添加当前各模块状态
 */
void addStatus(void)
{
    u32 ErrorStatus = GetErrorState();
    //初始化一下
    for (int i=0;i<30;i++)
        judge_send_msg3.Character_Graph.data[i]=0;

    judge_send_msg3.Character_Graph.figure_data_struct.operate_type = 1;
    judge_send_msg3.Character_Graph.figure_data_struct.figure_type = 7;
    judge_send_msg3.Character_Graph.figure_data_struct.color = 3;
    judge_send_msg3.Character_Graph.figure_data_struct.layer = 7;
    judge_send_msg3.Character_Graph.figure_data_struct.width = 5;
    judge_send_msg3.Character_Graph.figure_data_struct.start_x = 20;
    judge_send_msg3.Character_Graph.figure_data_struct.start_y = 790;
    judge_send_msg3.Character_Graph.figure_data_struct.details_a = 20;
    judge_send_msg3.Character_Graph.figure_data_struct.details_b = 9;
    judge_send_msg3.Character_Graph.figure_data_struct.details_c = 0;
    judge_send_msg3.Character_Graph.figure_data_struct.details_d = 0;
    judge_send_msg3.Character_Graph.figure_data_struct.details_e = 0;


    strcpy((char*)judge_send_msg3.Character_Graph.figure_data_struct.figure_name, "E1");
    if((ErrorStatus>>REMOTE_LOST_COUNT)&1)
    {
        strcpy((char*)judge_send_msg3.Character_Graph.data, "Remote!");
    }
    else if((ErrorStatus>>JUDGEMENT_LOST_COUNT)&1)
    {
        strcpy((char*)judge_send_msg3.Character_Graph.data, "Judge!");
    }
    else if((ErrorStatus>>JOINT_MOTOR_0)&1)
    {
        strcpy((char*)judge_send_msg3.Character_Graph.data, "JOINT_MOTOR_0!");
    }
    else if((ErrorStatus>>JOINT_MOTOR_1)&1)
    {
        strcpy((char*)judge_send_msg3.Character_Graph.data, "JOINT_MOTOR_1!");
    }
    else if((ErrorStatus>>JOINT_MOTOR_2)&1)
    {
        strcpy((char*)judge_send_msg3.Character_Graph.data, "JOINT_MOTOR_2!");
    }
    else if((ErrorStatus>>JOINT_MOTOR_3)&1)
    {
        strcpy((char*)judge_send_msg3.Character_Graph.data, "JOINT_MOTOR_3!");
    }
    else if((ErrorStatus>>FRICTION_LOST_COUNT)&1)
    {
        strcpy((char*)judge_send_msg3.Character_Graph.data, "FRICTION!");
    }
    else if((ErrorStatus>>GIMBAL_MOTOR_PITCH)&1)
    {
        strcpy((char*)judge_send_msg3.Character_Graph.data, "PITCH!");
    }
    else if((ErrorStatus>>GIMBAL_MOTOR_YAW)&1)
    {
        strcpy((char*)judge_send_msg3.Character_Graph.data, "YAW!");
    }
    else if((ErrorStatus>>SUPERC_LOST_COUNT)&1)
    {
        strcpy((char*)judge_send_msg3.Character_Graph.data, "SUPERC!");
    }
    else if((ErrorStatus>>VISION_LOST_COUNT)&1)
    {
        strcpy((char*)judge_send_msg3.Character_Graph.data, "VISION!");
    }
    else if((ErrorStatus>>WHEEL_MOTOR_0)&1)
    {
        strcpy((char*)judge_send_msg3.Character_Graph.data, "WHEEL_MOTOR_0!");
    }
    else if((ErrorStatus>>WHEEL_MOTOR_1)&1)
    {
        strcpy((char*)judge_send_msg3.Character_Graph.data, "WHEEL_MOTOR_1!");
    }
    else
    {
        strcpy((char*)judge_send_msg3.Character_Graph.data, "");
    }

    robot_interaction_data.data_cmd_id = INTERACTION_CHARACTER_ID ;
    data_packet_pack(ROBO_INTERACTION_DATA_ID, (uint8_t *)&judge_send_msg3.Character_Graph,
                     sizeof(judge_send_msg3.Character_Graph), robot_interaction_data);
}


/*!
 * @brief 绘制自瞄目标位置
 */
void addTarget(void)
{
    strcpy((char*)judge_send_msg2.Single_Graph.figure_data_struct.figure_name,"t1");
    judge_send_msg2.Single_Graph.figure_data_struct.operate_type=1;
    judge_send_msg2.Single_Graph.figure_data_struct.figure_type=2;
    judge_send_msg2.Single_Graph.figure_data_struct.details_a=0;
    judge_send_msg2.Single_Graph.figure_data_struct.details_b=0;
    judge_send_msg2.Single_Graph.figure_data_struct.details_c=230;

    judge_send_msg2.Single_Graph.figure_data_struct.start_x=960;
    judge_send_msg2.Single_Graph.figure_data_struct.start_y=540;
    judge_send_msg2.Single_Graph.figure_data_struct.details_d=0;
    judge_send_msg2.Single_Graph.figure_data_struct.details_e=0;

    judge_send_msg2.Single_Graph.figure_data_struct.layer=5;
    judge_send_msg2.Single_Graph.figure_data_struct.width=5;

    if(GimbalReceive.auto_aim_flag == 0)
    {
        judge_send_msg2.Single_Graph.figure_data_struct.color = 8;//未识别(白色)
    }
    else if(GimbalReceive.auto_aim_flag == 2){
        judge_send_msg2.Single_Graph.figure_data_struct.color = 6;//识别未完成(青色)
    }
    else
    {
        judge_send_msg2.Single_Graph.figure_data_struct.color = 4;//已识别(紫红色)
    }


    robot_interaction_data.data_cmd_id = INTERACTION_FIGURE_ID ;
    data_packet_pack(ROBO_INTERACTION_DATA_ID, (uint8_t *)&judge_send_msg2.Single_Graph,
                     sizeof(judge_send_msg2.Single_Graph), robot_interaction_data);
}
/*!
 * @brief 绘制机体方位
 */

float ATAN = PI/4;
extern float yaw_offset;
void addPosition(void)
{
    for (int k=0;k<5;k++){
        judge_send_mesg.Five_Graph.figure_data_struct[k].operate_type = 1;
    }

    //指针
    float NowAngle = (yaw_offset - YawMotor.angle) * PI;
    //有灯条的正方向
    strcpy((char*)judge_send_mesg.Five_Graph.figure_data_struct[0].figure_name,"p1");
    judge_send_mesg.Five_Graph.figure_data_struct[0].figure_type        = 0;
    judge_send_mesg.Five_Graph.figure_data_struct[0].layer			     = 9;
    judge_send_mesg.Five_Graph.figure_data_struct[0].color              = 3;
    judge_send_mesg.Five_Graph.figure_data_struct[0].details_a          = 0;
    judge_send_mesg.Five_Graph.figure_data_struct[0].details_b          = 0;
    judge_send_mesg.Five_Graph.figure_data_struct[0].width              = 3;
    judge_send_mesg.Five_Graph.figure_data_struct[0].start_x            = 500 - (int)(54 * sinf(ATAN - NowAngle));
    judge_send_mesg.Five_Graph.figure_data_struct[0].start_y            = 300 - (int)(54 * cosf(ATAN - NowAngle));
    judge_send_mesg.Five_Graph.figure_data_struct[0].details_c          = 0;
    judge_send_mesg.Five_Graph.figure_data_struct[0].details_d	         = 500 + (int)(50 * sinf(ATAN + NowAngle));
    judge_send_mesg.Five_Graph.figure_data_struct[0].details_e		     = 300 - (int)(50 * cosf(ATAN + NowAngle));

    //指针
    strcpy((char*)judge_send_mesg.Five_Graph.figure_data_struct[1].figure_name,"p2");
    judge_send_mesg.Five_Graph.figure_data_struct[1].figure_type        = 0;
    judge_send_mesg.Five_Graph.figure_data_struct[1].layer			     = 9;
    judge_send_mesg.Five_Graph.figure_data_struct[1].color 		     = 4;
    judge_send_mesg.Five_Graph.figure_data_struct[1].details_a          = 0;
    judge_send_mesg.Five_Graph.figure_data_struct[1].details_b          = 0;
    judge_send_mesg.Five_Graph.figure_data_struct[1].width              = 3;
    judge_send_mesg.Five_Graph.figure_data_struct[1].start_x            = 500 ;
    judge_send_mesg.Five_Graph.figure_data_struct[1].start_y            = 300 ;
    judge_send_mesg.Five_Graph.figure_data_struct[1].details_c          = 0;
    judge_send_mesg.Five_Graph.figure_data_struct[1].details_d	         = 500 ;
    judge_send_mesg.Five_Graph.figure_data_struct[1].details_e	   	     = 300 + 40;

    //左长边
    strcpy((char*)judge_send_mesg.Five_Graph.figure_data_struct[2].figure_name,"p3");
    judge_send_mesg.Five_Graph.figure_data_struct[2].figure_type        = 0;
    judge_send_mesg.Five_Graph.figure_data_struct[2].layer			     = 9;
    judge_send_mesg.Five_Graph.figure_data_struct[2].color 		     = 3;
    judge_send_mesg.Five_Graph.figure_data_struct[2].details_a          = 0;
    judge_send_mesg.Five_Graph.figure_data_struct[2].details_b          = 0;
    judge_send_mesg.Five_Graph.figure_data_struct[2].width              = 3;
    judge_send_mesg.Five_Graph.figure_data_struct[2].start_x            = 500 - (int)(50 * sinf(ATAN - NowAngle));
    judge_send_mesg.Five_Graph.figure_data_struct[2].start_y            = 300 - (int)(50 * cosf(ATAN - NowAngle));
    judge_send_mesg.Five_Graph.figure_data_struct[2].details_c          = 0;
    judge_send_mesg.Five_Graph.figure_data_struct[2].details_d	         = 500 - (int)(50 * sinf(ATAN + NowAngle));
    judge_send_mesg.Five_Graph.figure_data_struct[2].details_e	   	     = 300 + (int)(50 * cosf(ATAN + NowAngle));

    //无灯条的正方向
    strcpy((char*)judge_send_mesg.Five_Graph.figure_data_struct[3].figure_name,"p4");
    judge_send_mesg.Five_Graph.figure_data_struct[3].figure_type        = 0;
    judge_send_mesg.Five_Graph.figure_data_struct[3].layer			     = 9;
    judge_send_mesg.Five_Graph.figure_data_struct[3].color 		     = 2;
    judge_send_mesg.Five_Graph.figure_data_struct[3].details_a          = 0;
    judge_send_mesg.Five_Graph.figure_data_struct[3].details_b          = 0;
    judge_send_mesg.Five_Graph.figure_data_struct[3].width              = 3;
    judge_send_mesg.Five_Graph.figure_data_struct[3].start_x            = 500 - (int)(50 * sinf(ATAN + NowAngle));
    judge_send_mesg.Five_Graph.figure_data_struct[3].start_y            = 300 + (int)(50 * cosf(ATAN + NowAngle));
    judge_send_mesg.Five_Graph.figure_data_struct[3].details_c          = 0;
    judge_send_mesg.Five_Graph.figure_data_struct[3].details_d	         = 500 + (int)(50 * sinf(ATAN - NowAngle));
    judge_send_mesg.Five_Graph.figure_data_struct[3].details_e	   	     = 300 + (int)(50 * cosf(ATAN - NowAngle));

    //右长边
    strcpy((char*)judge_send_mesg.Five_Graph.figure_data_struct[4].figure_name,"p5");
    judge_send_mesg.Five_Graph.figure_data_struct[4].figure_type        = 0;
    judge_send_mesg.Five_Graph.figure_data_struct[4].layer			     = 9;
    judge_send_mesg.Five_Graph.figure_data_struct[4].color 		     = 3;
    judge_send_mesg.Five_Graph.figure_data_struct[4].details_a          = 0;
    judge_send_mesg.Five_Graph.figure_data_struct[4].details_b          = 0;
    judge_send_mesg.Five_Graph.figure_data_struct[4].width              = 3;
    judge_send_mesg.Five_Graph.figure_data_struct[4].start_x            = 500 + (int)(50 * sinf(ATAN - NowAngle));
    judge_send_mesg.Five_Graph.figure_data_struct[4].start_y            = 300 + (int)(50 * cosf(ATAN - NowAngle));
    judge_send_mesg.Five_Graph.figure_data_struct[4].details_c          = 0;
    judge_send_mesg.Five_Graph.figure_data_struct[4].details_d	         = 500 + (int)(50 * sinf(ATAN + NowAngle));
    judge_send_mesg.Five_Graph.figure_data_struct[4].details_e	   	     = 300 - (int)(50 * cosf(ATAN + NowAngle));

    robot_interaction_data.data_cmd_id = INTERACTION_FIGURE3_ID;
    data_packet_pack(ROBO_INTERACTION_DATA_ID, (uint8_t *)&judge_send_mesg.Five_Graph,
                     sizeof(judge_send_mesg.Five_Graph) , robot_interaction_data);

}

void addEnemyInf()
{
    for (int k = 0; k < 5; k++) {
        judge_send_msg4.Five_Graph.figure_data_struct[k].operate_type = 1;
    }
    //TODO:ui位置未改
    if (judge_rece_mesg.robot_status_data.robot_id < 100)//红方
    {
        //敌方英雄
        strcpy((char *) judge_send_msg4.Five_Graph.figure_data_struct[0].figure_name, "h1");
        judge_send_msg4.Five_Graph.figure_data_struct[0].figure_type = 6;//整形
        judge_send_msg4.Five_Graph.figure_data_struct[0].color=6;
        judge_send_msg4.Five_Graph.figure_data_struct[0].width=1;
        judge_send_msg4.Five_Graph.figure_data_struct[0].start_y=900;
        judge_send_msg4.Five_Graph.figure_data_struct[0].start_x=1180;
        judge_send_msg4.Five_Graph.figure_data_struct[0].details_a=25;
        judge_send_msg4.Five_Graph.figure_data_struct[0].details_c=judge_rece_mesg.radar_status_frame.enemy_hp.enemy_hero % 1024;
        judge_send_msg4.Five_Graph.figure_data_struct[0].details_d=judge_rece_mesg.radar_status_frame.enemy_hp.enemy_hero / 1024;
        judge_send_msg4.Five_Graph.figure_data_struct[0].details_e=0;

        //敌方工程
        strcpy((char *) judge_send_msg4.Five_Graph.figure_data_struct[1].figure_name, "h2");
        judge_send_msg4.Five_Graph.figure_data_struct[1].figure_type = 6;//整形
        judge_send_msg4.Five_Graph.figure_data_struct[1].color=6;
        judge_send_msg4.Five_Graph.figure_data_struct[1].width=1;
        judge_send_msg4.Five_Graph.figure_data_struct[1].start_y=900;
        judge_send_msg4.Five_Graph.figure_data_struct[1].start_x=1300;
        judge_send_msg4.Five_Graph.figure_data_struct[1].details_a=25;
        judge_send_msg4.Five_Graph.figure_data_struct[1].details_c=judge_rece_mesg.radar_status_frame.enemy_hp.enemy_engineer % 1024;
        judge_send_msg4.Five_Graph.figure_data_struct[1].details_d=judge_rece_mesg.radar_status_frame.enemy_hp.enemy_engineer / 1024;
        judge_send_msg4.Five_Graph.figure_data_struct[1].details_e=0;

        //敌方步兵3
        strcpy((char *) judge_send_msg4.Five_Graph.figure_data_struct[2].figure_name, "h3");
        judge_send_msg4.Five_Graph.figure_data_struct[2].figure_type = 6;//整形
        judge_send_msg4.Five_Graph.figure_data_struct[2].color=6;
        judge_send_msg4.Five_Graph.figure_data_struct[2].width=1;
        judge_send_msg4.Five_Graph.figure_data_struct[2].start_y=900;
        judge_send_msg4.Five_Graph.figure_data_struct[2].start_x=1420;
        judge_send_msg4.Five_Graph.figure_data_struct[2].details_a=25;
        judge_send_msg4.Five_Graph.figure_data_struct[2].details_c=judge_rece_mesg.radar_status_frame.enemy_hp.enemy_infantry_3 % 1024;
        judge_send_msg4.Five_Graph.figure_data_struct[2].details_d=judge_rece_mesg.radar_status_frame.enemy_hp.enemy_infantry_3 / 1024;
        judge_send_msg4.Five_Graph.figure_data_struct[2].details_e=0;

        //敌方步兵4
        strcpy((char *) judge_send_msg4.Five_Graph.figure_data_struct[3].figure_name, "h4");
        judge_send_msg4.Five_Graph.figure_data_struct[3].figure_type = 6;//整形
        judge_send_msg4.Five_Graph.figure_data_struct[3].color=6;
        judge_send_msg4.Five_Graph.figure_data_struct[3].width=1;
        judge_send_msg4.Five_Graph.figure_data_struct[3].start_y=900;
        judge_send_msg4.Five_Graph.figure_data_struct[3].start_x=1540;
        judge_send_msg4.Five_Graph.figure_data_struct[3].details_a=25;
        judge_send_msg4.Five_Graph.figure_data_struct[3].details_c=judge_rece_mesg.radar_status_frame.enemy_hp.enemy_infantry_4 % 1024;
        judge_send_msg4.Five_Graph.figure_data_struct[3].details_d=judge_rece_mesg.radar_status_frame.enemy_hp.enemy_infantry_4 / 1024;
        judge_send_msg4.Five_Graph.figure_data_struct[3].details_e=0;

        //敌方哨兵
        strcpy((char *) judge_send_msg4.Five_Graph.figure_data_struct[4].figure_name, "h5");
        judge_send_msg4.Five_Graph.figure_data_struct[4].figure_type = 6;//整形
        judge_send_msg4.Five_Graph.figure_data_struct[4].color=6;
        judge_send_msg4.Five_Graph.figure_data_struct[4].width=1;
        judge_send_msg4.Five_Graph.figure_data_struct[4].start_y=900;
        judge_send_msg4.Five_Graph.figure_data_struct[4].start_x=1780;
        judge_send_msg4.Five_Graph.figure_data_struct[4].details_a=25;
        judge_send_msg4.Five_Graph.figure_data_struct[4].details_c=judge_rece_mesg.radar_status_frame.enemy_hp.enemy_sentry % 1024;
        judge_send_msg4.Five_Graph.figure_data_struct[4].details_d=judge_rece_mesg.radar_status_frame.enemy_hp.enemy_sentry / 1024;
        judge_send_msg4.Five_Graph.figure_data_struct[4].details_e=0;
    }
    else
    {
        //敌方英雄
        strcpy((char *) judge_send_msg4.Five_Graph.figure_data_struct[0].figure_name, "h1");
        judge_send_msg4.Five_Graph.figure_data_struct[0].figure_type = 6;//整形
        judge_send_msg4.Five_Graph.figure_data_struct[0].color=6;
        judge_send_msg4.Five_Graph.figure_data_struct[0].width=1;
        judge_send_msg4.Five_Graph.figure_data_struct[0].start_y=900;
        judge_send_msg4.Five_Graph.figure_data_struct[0].start_x=80;
        judge_send_msg4.Five_Graph.figure_data_struct[0].details_a=25;
        judge_send_msg4.Five_Graph.figure_data_struct[0].details_c=judge_rece_mesg.radar_status_frame.enemy_hp.enemy_hero % 1024;
        judge_send_msg4.Five_Graph.figure_data_struct[0].details_d=judge_rece_mesg.radar_status_frame.enemy_hp.enemy_hero / 1024;
        judge_send_msg4.Five_Graph.figure_data_struct[0].details_e=0;

        //敌方工程
        strcpy((char *) judge_send_msg4.Five_Graph.figure_data_struct[1].figure_name, "h2");
        judge_send_msg4.Five_Graph.figure_data_struct[1].figure_type = 6;//整形
        judge_send_msg4.Five_Graph.figure_data_struct[1].color=6;
        judge_send_msg4.Five_Graph.figure_data_struct[1].width=1;
        judge_send_msg4.Five_Graph.figure_data_struct[1].start_y=900;
        judge_send_msg4.Five_Graph.figure_data_struct[1].start_x=320;
        judge_send_msg4.Five_Graph.figure_data_struct[1].details_a=25;
        judge_send_msg4.Five_Graph.figure_data_struct[1].details_c=judge_rece_mesg.radar_status_frame.enemy_hp.enemy_engineer % 1024;
        judge_send_msg4.Five_Graph.figure_data_struct[1].details_d=judge_rece_mesg.radar_status_frame.enemy_hp.enemy_engineer / 1024;
        judge_send_msg4.Five_Graph.figure_data_struct[1].details_e=0;

        //敌方步兵3
        strcpy((char *) judge_send_msg4.Five_Graph.figure_data_struct[2].figure_name, "h3");
        judge_send_msg4.Five_Graph.figure_data_struct[2].figure_type = 6;//整形
        judge_send_msg4.Five_Graph.figure_data_struct[2].color=6;
        judge_send_msg4.Five_Graph.figure_data_struct[2].width=1;
        judge_send_msg4.Five_Graph.figure_data_struct[2].start_y=900;
        judge_send_msg4.Five_Graph.figure_data_struct[2].start_x=440;
        judge_send_msg4.Five_Graph.figure_data_struct[2].details_a=25;
        judge_send_msg4.Five_Graph.figure_data_struct[2].details_c=judge_rece_mesg.radar_status_frame.enemy_hp.enemy_infantry_3 % 1024;
        judge_send_msg4.Five_Graph.figure_data_struct[2].details_d=judge_rece_mesg.radar_status_frame.enemy_hp.enemy_infantry_3 / 1024;
        judge_send_msg4.Five_Graph.figure_data_struct[2].details_e=0;

        //敌方步兵4
        strcpy((char *) judge_send_msg4.Five_Graph.figure_data_struct[3].figure_name, "h4");
        judge_send_msg4.Five_Graph.figure_data_struct[3].figure_type = 6;//整形
        judge_send_msg4.Five_Graph.figure_data_struct[3].color=6;
        judge_send_msg4.Five_Graph.figure_data_struct[3].width=1;
        judge_send_msg4.Five_Graph.figure_data_struct[3].start_y=900;
        judge_send_msg4.Five_Graph.figure_data_struct[3].start_x=560;
        judge_send_msg4.Five_Graph.figure_data_struct[3].details_a=25;
        judge_send_msg4.Five_Graph.figure_data_struct[3].details_c=judge_rece_mesg.radar_status_frame.enemy_hp.enemy_infantry_4 % 1024;
        judge_send_msg4.Five_Graph.figure_data_struct[3].details_d=judge_rece_mesg.radar_status_frame.enemy_hp.enemy_infantry_4 / 1024;
        judge_send_msg4.Five_Graph.figure_data_struct[3].details_e=0;

        //敌方哨兵
        strcpy((char *) judge_send_msg4.Five_Graph.figure_data_struct[4].figure_name, "h5");
        judge_send_msg4.Five_Graph.figure_data_struct[4].figure_type = 6;//整形
        judge_send_msg4.Five_Graph.figure_data_struct[4].color=6;
        judge_send_msg4.Five_Graph.figure_data_struct[4].width=1;
        judge_send_msg4.Five_Graph.figure_data_struct[4].start_y=900;
        judge_send_msg4.Five_Graph.figure_data_struct[4].start_x=680;
        judge_send_msg4.Five_Graph.figure_data_struct[4].details_a=25;
        judge_send_msg4.Five_Graph.figure_data_struct[4].details_c=judge_rece_mesg.radar_status_frame.enemy_hp.enemy_sentry % 1024;
        judge_send_msg4.Five_Graph.figure_data_struct[4].details_d=judge_rece_mesg.radar_status_frame.enemy_hp.enemy_sentry / 1024;
        judge_send_msg4.Five_Graph.figure_data_struct[4].details_e=0;
    }


    robot_interaction_data.data_cmd_id = INTERACTION_FIGURE3_ID;
    data_packet_pack(ROBO_INTERACTION_DATA_ID, (uint8_t *)&judge_send_msg4.Five_Graph,
                     sizeof(judge_send_msg4.Five_Graph) , robot_interaction_data);
}

void addEnemyInf2()
{
    for (int k = 0; k < 7; k++) {
        judge_send_msg4.Seven_Graph.figure_data_struct[k].operate_type = 1;
    }
    //TODO:ui位置未改
    if (judge_rece_mesg.robot_status_data.robot_id < 100)//红方
    {
        //敌方英雄
        strcpy((char *) judge_send_msg4.Seven_Graph.figure_data_struct[0].figure_name, "h1");
        judge_send_msg4.Seven_Graph.figure_data_struct[0].figure_type = 6;//整形
        judge_send_msg4.Seven_Graph.figure_data_struct[0].color=6;
        judge_send_msg4.Seven_Graph.figure_data_struct[0].width=3;
        judge_send_msg4.Seven_Graph.figure_data_struct[0].start_y=900;
        judge_send_msg4.Seven_Graph.figure_data_struct[0].start_x=1240;
        judge_send_msg4.Seven_Graph.figure_data_struct[0].details_a=25;
        judge_send_msg4.Seven_Graph.figure_data_struct[0].details_c=judge_rece_mesg.radar_status_frame.enemy_hp.enemy_hero % 1024;
        judge_send_msg4.Seven_Graph.figure_data_struct[0].details_d=judge_rece_mesg.radar_status_frame.enemy_hp.enemy_hero / 1024;
        judge_send_msg4.Seven_Graph.figure_data_struct[0].details_e=0;

        //敌方工程
        strcpy((char *) judge_send_msg4.Seven_Graph.figure_data_struct[1].figure_name, "h2");
        judge_send_msg4.Seven_Graph.figure_data_struct[1].figure_type = 6;//整形
        judge_send_msg4.Seven_Graph.figure_data_struct[1].color=6;
        judge_send_msg4.Seven_Graph.figure_data_struct[1].width=3;
        judge_send_msg4.Seven_Graph.figure_data_struct[1].start_y=900;
        judge_send_msg4.Seven_Graph.figure_data_struct[1].start_x=1300;
        judge_send_msg4.Seven_Graph.figure_data_struct[1].details_a=25;
        judge_send_msg4.Seven_Graph.figure_data_struct[1].details_c=judge_rece_mesg.radar_status_frame.enemy_hp.enemy_engineer % 1024;
        judge_send_msg4.Seven_Graph.figure_data_struct[1].details_d=judge_rece_mesg.radar_status_frame.enemy_hp.enemy_engineer / 1024;
        judge_send_msg4.Seven_Graph.figure_data_struct[1].details_e=0;

        //敌方步兵3
        strcpy((char *) judge_send_msg4.Seven_Graph.figure_data_struct[2].figure_name, "h3");
        judge_send_msg4.Seven_Graph.figure_data_struct[2].figure_type = 6;//整形
        judge_send_msg4.Seven_Graph.figure_data_struct[2].color=6;
        judge_send_msg4.Seven_Graph.figure_data_struct[2].width=3;
        judge_send_msg4.Seven_Graph.figure_data_struct[2].start_y=900;
        judge_send_msg4.Seven_Graph.figure_data_struct[2].start_x=1420;
        judge_send_msg4.Seven_Graph.figure_data_struct[2].details_a=25;
        judge_send_msg4.Seven_Graph.figure_data_struct[2].details_c=judge_rece_mesg.radar_status_frame.enemy_hp.enemy_infantry_3 % 1024;
        judge_send_msg4.Seven_Graph.figure_data_struct[2].details_d=judge_rece_mesg.radar_status_frame.enemy_hp.enemy_infantry_3 / 1024;
        judge_send_msg4.Seven_Graph.figure_data_struct[2].details_e=0;

        //敌方步兵4
        strcpy((char *) judge_send_msg4.Seven_Graph.figure_data_struct[3].figure_name, "h4");
        judge_send_msg4.Seven_Graph.figure_data_struct[3].figure_type = 6;//整形
        judge_send_msg4.Seven_Graph.figure_data_struct[3].color=6;
        judge_send_msg4.Seven_Graph.figure_data_struct[3].width=3;
        judge_send_msg4.Seven_Graph.figure_data_struct[3].start_y=900;
        judge_send_msg4.Seven_Graph.figure_data_struct[3].start_x=1540;
        judge_send_msg4.Seven_Graph.figure_data_struct[3].details_a=25;
        judge_send_msg4.Seven_Graph.figure_data_struct[3].details_c=judge_rece_mesg.radar_status_frame.enemy_hp.enemy_infantry_4 % 1024;
        judge_send_msg4.Seven_Graph.figure_data_struct[3].details_d=judge_rece_mesg.radar_status_frame.enemy_hp.enemy_infantry_4 / 1024;
        judge_send_msg4.Seven_Graph.figure_data_struct[3].details_e=0;

        //敌方哨兵
        strcpy((char *) judge_send_msg4.Seven_Graph.figure_data_struct[4].figure_name, "h5");
        judge_send_msg4.Seven_Graph.figure_data_struct[4].figure_type = 6;//整形
        judge_send_msg4.Seven_Graph.figure_data_struct[4].color=6;
        judge_send_msg4.Seven_Graph.figure_data_struct[4].width=3;
        judge_send_msg4.Seven_Graph.figure_data_struct[4].start_y=900;
        judge_send_msg4.Seven_Graph.figure_data_struct[4].start_x=1780;
        judge_send_msg4.Seven_Graph.figure_data_struct[4].details_a=25;
        judge_send_msg4.Seven_Graph.figure_data_struct[4].details_c=judge_rece_mesg.radar_status_frame.enemy_hp.enemy_sentry % 1024;
        judge_send_msg4.Seven_Graph.figure_data_struct[4].details_d=judge_rece_mesg.radar_status_frame.enemy_hp.enemy_sentry / 1024;
        judge_send_msg4.Seven_Graph.figure_data_struct[4].details_e=0;
    }
    else
    {
        //敌方英雄
        strcpy((char *) judge_send_msg4.Seven_Graph.figure_data_struct[0].figure_name, "h1");
        judge_send_msg4.Seven_Graph.figure_data_struct[0].figure_type = 6;//整形
        judge_send_msg4.Seven_Graph.figure_data_struct[0].color=6;
        judge_send_msg4.Seven_Graph.figure_data_struct[0].width=3;
        judge_send_msg4.Seven_Graph.figure_data_struct[0].start_y=900;
        judge_send_msg4.Seven_Graph.figure_data_struct[0].start_x=80;
        judge_send_msg4.Seven_Graph.figure_data_struct[0].details_a=25;
        judge_send_msg4.Seven_Graph.figure_data_struct[0].details_c=judge_rece_mesg.radar_status_frame.enemy_hp.enemy_hero % 1024;
        judge_send_msg4.Seven_Graph.figure_data_struct[0].details_d=judge_rece_mesg.radar_status_frame.enemy_hp.enemy_hero / 1024;
        judge_send_msg4.Seven_Graph.figure_data_struct[0].details_e=0;

        //敌方工程
        strcpy((char *) judge_send_msg4.Seven_Graph.figure_data_struct[1].figure_name, "h2");
        judge_send_msg4.Seven_Graph.figure_data_struct[1].figure_type = 6;//整形
        judge_send_msg4.Seven_Graph.figure_data_struct[1].color=6;
        judge_send_msg4.Seven_Graph.figure_data_struct[1].width=3;
        judge_send_msg4.Seven_Graph.figure_data_struct[1].start_y=900;
        judge_send_msg4.Seven_Graph.figure_data_struct[1].start_x=320;
        judge_send_msg4.Seven_Graph.figure_data_struct[1].details_a=25;
        judge_send_msg4.Seven_Graph.figure_data_struct[1].details_c=judge_rece_mesg.radar_status_frame.enemy_hp.enemy_engineer % 1024;
        judge_send_msg4.Seven_Graph.figure_data_struct[1].details_d=judge_rece_mesg.radar_status_frame.enemy_hp.enemy_engineer / 1024;
        judge_send_msg4.Seven_Graph.figure_data_struct[1].details_e=0;

        //敌方步兵3
        strcpy((char *) judge_send_msg4.Seven_Graph.figure_data_struct[2].figure_name, "h3");
        judge_send_msg4.Seven_Graph.figure_data_struct[2].figure_type = 6;//整形
        judge_send_msg4.Seven_Graph.figure_data_struct[2].color=6;
        judge_send_msg4.Seven_Graph.figure_data_struct[2].width=3;
        judge_send_msg4.Seven_Graph.figure_data_struct[2].start_y=900;
        judge_send_msg4.Seven_Graph.figure_data_struct[2].start_x=440;
        judge_send_msg4.Seven_Graph.figure_data_struct[2].details_a=25;
        judge_send_msg4.Seven_Graph.figure_data_struct[2].details_c=judge_rece_mesg.radar_status_frame.enemy_hp.enemy_infantry_3 % 1024;
        judge_send_msg4.Seven_Graph.figure_data_struct[2].details_d=judge_rece_mesg.radar_status_frame.enemy_hp.enemy_infantry_3 / 1024;
        judge_send_msg4.Seven_Graph.figure_data_struct[2].details_e=0;

        //敌方步兵4
        strcpy((char *) judge_send_msg4.Seven_Graph.figure_data_struct[3].figure_name, "h4");
        judge_send_msg4.Seven_Graph.figure_data_struct[3].figure_type = 6;//整形
        judge_send_msg4.Seven_Graph.figure_data_struct[3].color=6;
        judge_send_msg4.Seven_Graph.figure_data_struct[3].width=3;
        judge_send_msg4.Seven_Graph.figure_data_struct[3].start_y=900;
        judge_send_msg4.Seven_Graph.figure_data_struct[3].start_x=560;
        judge_send_msg4.Seven_Graph.figure_data_struct[3].details_a=25;
        judge_send_msg4.Seven_Graph.figure_data_struct[3].details_c=judge_rece_mesg.radar_status_frame.enemy_hp.enemy_infantry_4 % 1024;
        judge_send_msg4.Seven_Graph.figure_data_struct[3].details_d=judge_rece_mesg.radar_status_frame.enemy_hp.enemy_infantry_4 / 1024;
        judge_send_msg4.Seven_Graph.figure_data_struct[3].details_e=0;

        //敌方哨兵
        strcpy((char *) judge_send_msg4.Seven_Graph.figure_data_struct[4].figure_name, "h5");
        judge_send_msg4.Seven_Graph.figure_data_struct[4].figure_type = 6;//整形
        judge_send_msg4.Seven_Graph.figure_data_struct[4].color=6;
        judge_send_msg4.Seven_Graph.figure_data_struct[4].width=3;
        judge_send_msg4.Seven_Graph.figure_data_struct[4].start_y=900;
        judge_send_msg4.Seven_Graph.figure_data_struct[4].start_x=680;
        judge_send_msg4.Seven_Graph.figure_data_struct[4].details_a=25;
        judge_send_msg4.Seven_Graph.figure_data_struct[4].details_c=judge_rece_mesg.radar_status_frame.enemy_hp.enemy_sentry % 1024;
        judge_send_msg4.Seven_Graph.figure_data_struct[4].details_d=judge_rece_mesg.radar_status_frame.enemy_hp.enemy_sentry / 1024;
        judge_send_msg4.Seven_Graph.figure_data_struct[4].details_e=0;
    }


    robot_interaction_data.data_cmd_id = INTERACTION_FIGURE4_ID;
    data_packet_pack(ROBO_INTERACTION_DATA_ID, (uint8_t *)&judge_send_msg4.Seven_Graph,
                     sizeof(judge_send_msg4.Seven_Graph) , robot_interaction_data);
}


void updateLegLength(void) {
    for (int k = 0; k < 5; k++) {
        judge_send_msg1.Five_Graph.figure_data_struct[k].operate_type = 2;
    }

    strcpy((char *) judge_send_msg1.Five_Graph.figure_data_struct[0].figure_name, "l1");
    judge_send_msg1.Five_Graph.figure_data_struct[0].figure_type = 1;
    judge_send_msg1.Five_Graph.figure_data_struct[0].layer = 6;
    judge_send_msg1.Five_Graph.figure_data_struct[0].color = 6;
    judge_send_msg1.Five_Graph.figure_data_struct[0].width = 10;
    judge_send_msg1.Five_Graph.figure_data_struct[0].start_x = 1200;
    judge_send_msg1.Five_Graph.figure_data_struct[0].start_y = 170;
    judge_send_msg1.Five_Graph.figure_data_struct[0].details_d = 1210;
    judge_send_msg1.Five_Graph.figure_data_struct[0].details_e =
            180 + (int) (leg_posture_array[0].length * 100 - 9) * 2;

    strcpy((char *) judge_send_msg1.Five_Graph.figure_data_struct[1].figure_name, "l2");
    judge_send_msg1.Five_Graph.figure_data_struct[1].figure_type = 1;
    judge_send_msg1.Five_Graph.figure_data_struct[1].layer = 6;
    judge_send_msg1.Five_Graph.figure_data_struct[1].color = 5;
    judge_send_msg1.Five_Graph.figure_data_struct[1].width = 10;
    judge_send_msg1.Five_Graph.figure_data_struct[1].start_x = 1230;
    judge_send_msg1.Five_Graph.figure_data_struct[1].start_y = 170;
    judge_send_msg1.Five_Graph.figure_data_struct[1].details_d = 1240;
    judge_send_msg1.Five_Graph.figure_data_struct[1].details_e =
            180 + (int) (leg_posture_array[1].length * 100 - 9) * 2;

    strcpy((char *) judge_send_msg1.Five_Graph.figure_data_struct[2].figure_name, "t1");
    judge_send_msg1.Five_Graph.figure_data_struct[2].operate_type = 2;
    judge_send_msg1.Five_Graph.figure_data_struct[2].figure_type = 2;
    judge_send_msg1.Five_Graph.figure_data_struct[2].details_a = 0;
    judge_send_msg1.Five_Graph.figure_data_struct[2].details_b = 0;
    judge_send_msg1.Five_Graph.figure_data_struct[2].details_c = 230;

    judge_send_msg1.Five_Graph.figure_data_struct[2].start_x = 960;
    judge_send_msg1.Five_Graph.figure_data_struct[2].start_y = 540;
    judge_send_msg1.Five_Graph.figure_data_struct[2].details_d = 0;
    judge_send_msg1.Five_Graph.figure_data_struct[2].details_e = 0;

    judge_send_msg1.Five_Graph.figure_data_struct[2].layer = 5;
    judge_send_msg1.Five_Graph.figure_data_struct[2].width = 5;

    if(GimbalReceive.auto_aim_flag == 0)
    {
        judge_send_msg1.Five_Graph.figure_data_struct[2].color = 8;//未识别(白色)
    }
    else if(GimbalReceive.auto_aim_flag == 2){
        judge_send_msg1.Five_Graph.figure_data_struct[2].color = 6;//识别未完成(青色)
    }
    else
    {
        judge_send_msg1.Five_Graph.figure_data_struct[2].color = 4;//已识别(紫红色)
    }

    strcpy((char *) judge_send_msg1.Five_Graph.figure_data_struct[3].figure_name, "s1");
    judge_send_msg1.Five_Graph.figure_data_struct[3].figure_type = 1;
    judge_send_msg1.Five_Graph.figure_data_struct[3].layer = 6;

    if ((GetErrorState() >> SUPERC_LOST_COUNT) & 1) {
        //不可使用，黑色
        judge_send_msg1.Five_Graph.figure_data_struct[3].color = 7;
        judge_send_msg1.Five_Graph.figure_data_struct[3].details_a = 0;
        judge_send_msg1.Five_Graph.figure_data_struct[3].details_b = 0;
        judge_send_msg1.Five_Graph.figure_data_struct[3].details_c = 0;
        judge_send_msg1.Five_Graph.figure_data_struct[3].width = 20;
        judge_send_msg1.Five_Graph.figure_data_struct[3].start_x = 700;
        judge_send_msg1.Five_Graph.figure_data_struct[3].start_y = 45;
        judge_send_msg1.Five_Graph.figure_data_struct[3].details_d = 1145;
        judge_send_msg1.Five_Graph.figure_data_struct[3].details_e = 25;
    } else {

        judge_send_msg1.Five_Graph.figure_data_struct[3].color = 2;
        judge_send_msg1.Five_Graph.figure_data_struct[3].details_a = 0;
        judge_send_msg1.Five_Graph.figure_data_struct[3].details_b = 0;
        judge_send_msg1.Five_Graph.figure_data_struct[3].details_c = 0;
        judge_send_msg1.Five_Graph.figure_data_struct[3].width = 20;
        judge_send_msg1.Five_Graph.figure_data_struct[3].start_x = 700;
        judge_send_msg1.Five_Graph.figure_data_struct[3].start_y = 45;
        judge_send_msg1.Five_Graph.figure_data_struct[3].details_d =
                700 + (int) ((pow(superCap.voltCap, 2) - 64.0f) * 445.0f / 612.0f); //8-27V
        if (judge_send_msg1.Five_Graph.figure_data_struct[3].details_d < 700)
            judge_send_msg1.Five_Graph.figure_data_struct[3].details_d = 700;
        else if (judge_send_msg1.Five_Graph.figure_data_struct[3].details_d > 1135)
            judge_send_msg1.Five_Graph.figure_data_struct[3].details_d = 1135;
        judge_send_msg1.Five_Graph.figure_data_struct[3].details_e = 25;

        robot_interaction_data.data_cmd_id = INTERACTION_FIGURE3_ID;
        data_packet_pack(ROBO_INTERACTION_DATA_ID, (uint8_t *) &judge_send_msg1.Five_Graph,
                         sizeof(judge_send_msg1.Five_Graph), robot_interaction_data);

    }
}


/*!
 * @brief 给当前模式画个框（联盟赛版本）
 */
void updateModeV1(void)
{
    for(int i=0;i<7;i++)
    {
        judge_send_msg1.Seven_Graph.figure_data_struct[i].operate_type=2;
    }

    //第一个 摩擦轮
    strcpy((char*)judge_send_msg1.Seven_Graph.figure_data_struct[0].figure_name,"B1");
    if(controlSignal.controlFlag.friFlag)
    {
        judge_send_msg1.Seven_Graph.figure_data_struct[0].start_y=840;
        judge_send_msg1.Seven_Graph.figure_data_struct[0].start_x=735;
        judge_send_msg1.Seven_Graph.figure_data_struct[0].details_d=820;
        judge_send_msg1.Seven_Graph.figure_data_struct[0].details_e=800;
    }else{
        judge_send_msg1.Seven_Graph.figure_data_struct[0].start_y=0;
        judge_send_msg1.Seven_Graph.figure_data_struct[0].start_x=0;
        judge_send_msg1.Seven_Graph.figure_data_struct[0].details_d=0;
        judge_send_msg1.Seven_Graph.figure_data_struct[0].details_e=0;
    }

    //第二个  底盘功能
    strcpy((char*)judge_send_msg1.Seven_Graph.figure_data_struct[1].figure_name,"B2");
    if(controlSignal.controlFlag.spinFlag)
    {
        judge_send_msg1.Seven_Graph.figure_data_struct[1].start_y=840;
        judge_send_msg1.Seven_Graph.figure_data_struct[1].start_x=960;
        judge_send_msg1.Seven_Graph.figure_data_struct[1].details_d=1030;
        judge_send_msg1.Seven_Graph.figure_data_struct[1].details_e=800;
    }
    else if(controlSignal.controlFlag.axialFlag)
    {
        judge_send_msg1.Seven_Graph.figure_data_struct[1].start_y=840;
        judge_send_msg1.Seven_Graph.figure_data_struct[1].start_x=1060;
        judge_send_msg1.Seven_Graph.figure_data_struct[1].details_d=1165;
        judge_send_msg1.Seven_Graph.figure_data_struct[1].details_e=800;
    } else if(controlSignal.controlFlag.upstairFlag == 1)
    {
        judge_send_msg1.Seven_Graph.figure_data_struct[1].start_y=715;
        judge_send_msg1.Seven_Graph.figure_data_struct[1].start_x=1495;
        judge_send_msg1.Seven_Graph.figure_data_struct[1].details_d=1595;
        judge_send_msg1.Seven_Graph.figure_data_struct[1].details_e=685;
    }
    else if(controlSignal.controlFlag.jumpFlag_low == 1)
    {
        judge_send_msg1.Seven_Graph.figure_data_struct[1].start_y=685;
        judge_send_msg1.Seven_Graph.figure_data_struct[1].start_x=1495;
        judge_send_msg1.Seven_Graph.figure_data_struct[1].details_d=1595;
        judge_send_msg1.Seven_Graph.figure_data_struct[1].details_e=655;
    }
    else if(controlSignal.controlFlag.jumpFlag_high == 1)
    {
        judge_send_msg1.Seven_Graph.figure_data_struct[1].start_y=655;
        judge_send_msg1.Seven_Graph.figure_data_struct[1].start_x=1495;
        judge_send_msg1.Seven_Graph.figure_data_struct[1].details_d=1595;
        judge_send_msg1.Seven_Graph.figure_data_struct[1].details_e=625;
    }
    else{
        judge_send_msg1.Seven_Graph.figure_data_struct[1].start_x=840;
        judge_send_msg1.Seven_Graph.figure_data_struct[1].start_y=840;
        judge_send_msg1.Seven_Graph.figure_data_struct[1].details_d=930;
        judge_send_msg1.Seven_Graph.figure_data_struct[1].details_e=800;
    }
    //第三个  打符
    strcpy((char*)judge_send_msg1.Seven_Graph.figure_data_struct[2].figure_name,"B3");
    if(controlSignal.controlFlag.visionType==1)
    {
        judge_send_msg1.Seven_Graph.figure_data_struct[2].start_y=715;
        judge_send_msg1.Seven_Graph.figure_data_struct[2].start_x=245;
        judge_send_msg1.Seven_Graph.figure_data_struct[2].details_d=410;
        judge_send_msg1.Seven_Graph.figure_data_struct[2].details_e=685;
    }
    else if(controlSignal.controlFlag.visionType==2)
    {
        judge_send_msg1.Seven_Graph.figure_data_struct[2].start_y=655;
        judge_send_msg1.Seven_Graph.figure_data_struct[2].start_x=245;
        judge_send_msg1.Seven_Graph.figure_data_struct[2].details_d=370;
        judge_send_msg1.Seven_Graph.figure_data_struct[2].details_e=625;
    }
    else
    {
        judge_send_msg1.Seven_Graph.figure_data_struct[2].start_y=715;
        judge_send_msg1.Seven_Graph.figure_data_struct[2].start_x=245;
        judge_send_msg1.Seven_Graph.figure_data_struct[2].details_d=245;
        judge_send_msg1.Seven_Graph.figure_data_struct[2].details_e=715;
    }
    //第四个图形  允许发弹量
    int bullet=judge_rece_mesg.projectile_allowance_data.projectile_allowance_17mm;
    if(bullet < - 1024)
    {
        bullet = -1024;
    }
    strcpy((char*)judge_send_msg1.Seven_Graph.figure_data_struct[3].figure_name,"B4");
    judge_send_msg1.Seven_Graph.figure_data_struct[3].figure_type=6;
    judge_send_msg1.Seven_Graph.figure_data_struct[3].color=6;
    judge_send_msg1.Seven_Graph.figure_data_struct[3].width=3;
    judge_send_msg1.Seven_Graph.figure_data_struct[3].start_y=780;
    judge_send_msg1.Seven_Graph.figure_data_struct[3].start_x=320;
    judge_send_msg1.Seven_Graph.figure_data_struct[3].details_a=30;
    if(bullet>=0)
    {
        judge_send_msg1.Seven_Graph.figure_data_struct[3].details_c=bullet % 1024;
        judge_send_msg1.Seven_Graph.figure_data_struct[3].details_d=bullet / 1024;
        judge_send_msg1.Seven_Graph.figure_data_struct[3].details_e=0;
    }
    else
    {
        judge_send_msg1.Seven_Graph.figure_data_struct[3].details_c=bullet;
        judge_send_msg1.Seven_Graph.figure_data_struct[3].details_d=-1;
        judge_send_msg1.Seven_Graph.figure_data_struct[3].details_e=-1;
    }

    strcpy((char*)judge_send_msg1.Seven_Graph.figure_data_struct[4].figure_name,"B5");
    judge_send_msg1.Seven_Graph.figure_data_struct[4].figure_type=1;
    judge_send_msg1.Seven_Graph.figure_data_struct[4].color=4;
    judge_send_msg1.Seven_Graph.figure_data_struct[4].width=2;
    if (controlSignal.controlFlag.fast_mode)
    {
        judge_send_msg1.Seven_Graph.figure_data_struct[4].start_y=625;
        judge_send_msg1.Seven_Graph.figure_data_struct[4].start_x=1495;
        judge_send_msg1.Seven_Graph.figure_data_struct[4].details_d=1595;
        judge_send_msg1.Seven_Graph.figure_data_struct[4].details_e=595;
    }else
    {
        judge_send_msg1.Seven_Graph.figure_data_struct[4].start_x=840;
        judge_send_msg1.Seven_Graph.figure_data_struct[4].start_y=840;
        judge_send_msg1.Seven_Graph.figure_data_struct[4].details_d=930;
        judge_send_msg1.Seven_Graph.figure_data_struct[4].details_e=800;
    }

    //第六个图形  外框
    strcpy((char*)judge_send_msg1.Seven_Graph.figure_data_struct[5].figure_name,"b6");
    judge_send_msg1.Seven_Graph.figure_data_struct[5].start_x           = 400;
    judge_send_msg1.Seven_Graph.figure_data_struct[5].start_y           = 0;
    judge_send_msg1.Seven_Graph.figure_data_struct[5].details_d			= 622;
    judge_send_msg1.Seven_Graph.figure_data_struct[5].details_e			= 333;
    //第七个图形  外
    strcpy((char*)judge_send_msg1.Seven_Graph.figure_data_struct[6].figure_name,"b7");
    judge_send_msg1.Seven_Graph.figure_data_struct[6].start_x           = 1550;
    judge_send_msg1.Seven_Graph.figure_data_struct[6].start_y           = 0;
    judge_send_msg1.Seven_Graph.figure_data_struct[6].details_d			= 1328;
    judge_send_msg1.Seven_Graph.figure_data_struct[6].details_e			= 333;

//    if(controlSignal.controlFlag.axialFlag)
//    {
//        judge_send_msg1.Seven_Graph.figure_data_struct[5].start_y = judge_send_msg1.Seven_Graph.figure_data_struct[5].details_e;
//        judge_send_msg1.Seven_Graph.figure_data_struct[6].start_y = judge_send_msg1.Seven_Graph.figure_data_struct[6].details_e;
//    }

    robot_interaction_data.data_cmd_id = INTERACTION_FIGURE4_ID ;
    data_packet_pack(ROBO_INTERACTION_DATA_ID, (uint8_t *)&judge_send_msg1.Seven_Graph,
                     sizeof(judge_send_msg1.Seven_Graph), robot_interaction_data);
}



/*!
 * @brief 更新当前方位
 */
void updatePosition(void){
    float NowAngle = (yaw_offset - YawMotor.angle) * PI;

    for(int i=0;i<5;i++){
        judge_send_mesg.Five_Graph.figure_data_struct[i].operate_type=2;
        judge_send_mesg.Five_Graph.figure_data_struct[i].figure_type=1;
        judge_send_mesg.Five_Graph.figure_data_struct[i].color=4;
        judge_send_mesg.Five_Graph.figure_data_struct[i].width=3;
        judge_send_mesg.Five_Graph.figure_data_struct[i].layer=5;
        judge_send_mesg.Five_Graph.figure_data_struct[i].start_x=0;
        judge_send_mesg.Five_Graph.figure_data_struct[i].start_y=0;
        judge_send_mesg.Five_Graph.figure_data_struct[i].details_a=0;
        judge_send_mesg.Five_Graph.figure_data_struct[i].details_b=0;
        judge_send_mesg.Five_Graph.figure_data_struct[i].details_c=0;
        judge_send_mesg.Five_Graph.figure_data_struct[i].details_d=0;
        judge_send_mesg.Five_Graph.figure_data_struct[i].details_e=0;
    }

    //当前位置
    //有灯条的正方向
    strcpy((char*)judge_send_mesg.Five_Graph.figure_data_struct[0].figure_name,"p1");
    judge_send_mesg.Five_Graph.figure_data_struct[0].figure_type        = 0;
    judge_send_mesg.Five_Graph.figure_data_struct[0].layer			     = 9;
    judge_send_mesg.Five_Graph.figure_data_struct[0].color              = 3;
    judge_send_mesg.Five_Graph.figure_data_struct[0].details_a          = 0;
    judge_send_mesg.Five_Graph.figure_data_struct[0].details_b          = 0;
    judge_send_mesg.Five_Graph.figure_data_struct[0].width              = 3;
    judge_send_mesg.Five_Graph.figure_data_struct[0].start_x            = 500 - (int)(50 * sinf(ATAN - NowAngle));
    judge_send_mesg.Five_Graph.figure_data_struct[0].start_y            = 300 - (int)(50 * cosf(ATAN - NowAngle));
    judge_send_mesg.Five_Graph.figure_data_struct[0].details_c          = 0;
    judge_send_mesg.Five_Graph.figure_data_struct[0].details_d	         = 500 + (int)(50 * sinf(ATAN + NowAngle));
    judge_send_mesg.Five_Graph.figure_data_struct[0].details_e		     = 300 - (int)(50 * cosf(ATAN + NowAngle));

    //左长边
    strcpy((char*)judge_send_mesg.Five_Graph.figure_data_struct[1].figure_name,"p3");
    judge_send_mesg.Five_Graph.figure_data_struct[1].figure_type        = 0;
    judge_send_mesg.Five_Graph.figure_data_struct[1].layer			     = 9;
    judge_send_mesg.Five_Graph.figure_data_struct[1].color 		     = 3;
    judge_send_mesg.Five_Graph.figure_data_struct[1].details_a          = 0;
    judge_send_mesg.Five_Graph.figure_data_struct[1].details_b          = 0;
    judge_send_mesg.Five_Graph.figure_data_struct[1].width              = 3;
    judge_send_mesg.Five_Graph.figure_data_struct[1].start_x            = 500 - (int)(50 * sinf(ATAN - NowAngle));
    judge_send_mesg.Five_Graph.figure_data_struct[1].start_y            = 300 - (int)(50 * cosf(ATAN - NowAngle));
    judge_send_mesg.Five_Graph.figure_data_struct[1].details_c          = 0;
    judge_send_mesg.Five_Graph.figure_data_struct[1].details_d	         = 500 - (int)(50 * sinf(ATAN + NowAngle));
    judge_send_mesg.Five_Graph.figure_data_struct[1].details_e	   	     = 300 + (int)(50 * cosf(ATAN + NowAngle));

    //无灯条的正方向
    strcpy((char*)judge_send_mesg.Five_Graph.figure_data_struct[2].figure_name,"p4");
    judge_send_mesg.Five_Graph.figure_data_struct[2].figure_type        = 0;
    judge_send_mesg.Five_Graph.figure_data_struct[2].layer			     = 9;
    judge_send_mesg.Five_Graph.figure_data_struct[2].color 		     = 2;
    judge_send_mesg.Five_Graph.figure_data_struct[2].details_a          = 0;
    judge_send_mesg.Five_Graph.figure_data_struct[2].details_b          = 0;
    judge_send_mesg.Five_Graph.figure_data_struct[2].width              = 3;
    judge_send_mesg.Five_Graph.figure_data_struct[2].start_x            = 500 - (int)(50 * sinf(ATAN + NowAngle));
    judge_send_mesg.Five_Graph.figure_data_struct[2].start_y            = 300 + (int)(50 * cosf(ATAN + NowAngle));
    judge_send_mesg.Five_Graph.figure_data_struct[2].details_c          = 0;
    judge_send_mesg.Five_Graph.figure_data_struct[2].details_d	         = 500 + (int)(50 * sinf(ATAN - NowAngle));
    judge_send_mesg.Five_Graph.figure_data_struct[2].details_e	   	     = 300 + (int)(50 * cosf(ATAN - NowAngle));

    //右长边
    strcpy((char*)judge_send_mesg.Five_Graph.figure_data_struct[3].figure_name,"p5");
    judge_send_mesg.Five_Graph.figure_data_struct[3].figure_type        = 0;
    judge_send_mesg.Five_Graph.figure_data_struct[3].layer			     = 9;
    judge_send_mesg.Five_Graph.figure_data_struct[3].color 		     = 3;
    judge_send_mesg.Five_Graph.figure_data_struct[3].details_a          = 0;
    judge_send_mesg.Five_Graph.figure_data_struct[3].details_b          = 0;
    judge_send_mesg.Five_Graph.figure_data_struct[3].width              = 3;
    judge_send_mesg.Five_Graph.figure_data_struct[3].start_x            = 500 + (int)(50 * sinf(ATAN - NowAngle));
    judge_send_mesg.Five_Graph.figure_data_struct[3].start_y            = 300 + (int)(50 * cosf(ATAN - NowAngle));
    judge_send_mesg.Five_Graph.figure_data_struct[3].details_c          = 0;
    judge_send_mesg.Five_Graph.figure_data_struct[3].details_d	         = 500 + (int)(50 * sinf(ATAN + NowAngle));
    judge_send_mesg.Five_Graph.figure_data_struct[3].details_e	   	     = 300 - (int)(50 * cosf(ATAN + NowAngle));

    robot_interaction_data.data_cmd_id = INTERACTION_FIGURE3_ID;
    data_packet_pack(ROBO_INTERACTION_DATA_ID, (uint8_t *)&judge_send_mesg.Five_Graph,
                     sizeof(judge_send_mesg.Five_Graph) , robot_interaction_data);
}


/*!
 * @brief 更新当前状态信息
 */
void updateStatus(void)
{
    u32 ErrorStatus = GetErrorState();
    //初始化一下
    for (int i=0;i<30;i++)
        judge_send_msg3.Character_Graph.data[i]=0;

    judge_send_msg3.Character_Graph.figure_data_struct.operate_type = 2;
    judge_send_msg3.Character_Graph.figure_data_struct.figure_type = 7;
    judge_send_msg3.Character_Graph.figure_data_struct.color = 3;
    judge_send_msg3.Character_Graph.figure_data_struct.layer = 7;
    judge_send_msg3.Character_Graph.figure_data_struct.width = 5;
    judge_send_msg3.Character_Graph.figure_data_struct.start_x = 20;
    judge_send_msg3.Character_Graph.figure_data_struct.start_y = 790;
    judge_send_msg3.Character_Graph.figure_data_struct.details_a = 20;
    judge_send_msg3.Character_Graph.figure_data_struct.details_b = 9;
    judge_send_msg3.Character_Graph.figure_data_struct.details_c = 0;
    judge_send_msg3.Character_Graph.figure_data_struct.details_d = 0;
    judge_send_msg3.Character_Graph.figure_data_struct.details_e = 0;


    strcpy((char*)judge_send_msg3.Character_Graph.figure_data_struct.figure_name, "E1");
    if((ErrorStatus>>REMOTE_LOST_COUNT)&1)
    {
        strcpy((char*)judge_send_msg3.Character_Graph.data, "Remote!");
    }
    else if((ErrorStatus>>JUDGEMENT_LOST_COUNT)&1)
    {
        strcpy((char*)judge_send_msg3.Character_Graph.data, "Judge!");
    }
    else if((ErrorStatus>>JOINT_MOTOR_0)&1)
    {
        strcpy((char*)judge_send_msg3.Character_Graph.data, "JOINT_MOTOR_0!");
    }
    else if((ErrorStatus>>JOINT_MOTOR_1)&1)
    {
        strcpy((char*)judge_send_msg3.Character_Graph.data, "JOINT_MOTOR_1!");
    }
    else if((ErrorStatus>>JOINT_MOTOR_2)&1)
    {
        strcpy((char*)judge_send_msg3.Character_Graph.data, "JOINT_MOTOR_2!");
    }
    else if((ErrorStatus>>JOINT_MOTOR_3)&1)
    {
        strcpy((char*)judge_send_msg3.Character_Graph.data, "JOINT_MOTOR_3!");
    }
    else if((ErrorStatus>>FRICTION_LOST_COUNT)&1)
    {
        strcpy((char*)judge_send_msg3.Character_Graph.data, "FRICTION!");
    }
    else if((ErrorStatus>>GIMBAL_MOTOR_PITCH)&1)
    {
        strcpy((char*)judge_send_msg3.Character_Graph.data, "PITCH!");
    }
    else if((ErrorStatus>>GIMBAL_MOTOR_YAW)&1)
    {
        strcpy((char*)judge_send_msg3.Character_Graph.data, "YAW!");
    }
    else if((ErrorStatus>>SUPERC_LOST_COUNT)&1)
    {
        strcpy((char*)judge_send_msg3.Character_Graph.data, "SUPERC!");
    }
    else if((ErrorStatus>>VISION_LOST_COUNT)&1)
    {
        strcpy((char*)judge_send_msg3.Character_Graph.data, "VISION!");
    }
    else if((ErrorStatus>>WHEEL_MOTOR_0)&1)
    {
        strcpy((char*)judge_send_msg3.Character_Graph.data, "WHEEL_MOTOR_0!");
    }
    else if((ErrorStatus>>WHEEL_MOTOR_1)&1)
    {
        strcpy((char*)judge_send_msg3.Character_Graph.data, "WHEEL_MOTOR_1!");
    }
    else
    {
        strcpy((char*)judge_send_msg3.Character_Graph.data, "");
    }

    robot_interaction_data.data_cmd_id = INTERACTION_CHARACTER_ID ;
    data_packet_pack(ROBO_INTERACTION_DATA_ID, (uint8_t *)&judge_send_msg3.Character_Graph,
                     sizeof(judge_send_msg3.Character_Graph), robot_interaction_data);
}

void updateEnemyInf()
{
     for (int k = 0; k < 5; k++) {
        judge_send_msg4.Five_Graph.figure_data_struct[k].operate_type = 1;
    }
    //TODO:ui位置未改
    if (judge_rece_mesg.robot_status_data.robot_id < 100)//红方
    {
        //敌方英雄
        strcpy((char *) judge_send_msg4.Five_Graph.figure_data_struct[0].figure_name, "h1");
        judge_send_msg4.Five_Graph.figure_data_struct[0].figure_type = 6;//整形
        judge_send_msg4.Five_Graph.figure_data_struct[0].color=6;
        judge_send_msg4.Five_Graph.figure_data_struct[0].width=1;
        judge_send_msg4.Five_Graph.figure_data_struct[0].start_y=900;
        judge_send_msg4.Five_Graph.figure_data_struct[0].start_x=1180;
        judge_send_msg4.Five_Graph.figure_data_struct[0].details_a=25;
        judge_send_msg4.Five_Graph.figure_data_struct[0].details_c=judge_rece_mesg.radar_status_frame.enemy_hp.enemy_hero % 1024;
        judge_send_msg4.Five_Graph.figure_data_struct[0].details_d=judge_rece_mesg.radar_status_frame.enemy_hp.enemy_hero / 1024;
        judge_send_msg4.Five_Graph.figure_data_struct[0].details_e=0;

        //敌方工程
        strcpy((char *) judge_send_msg4.Five_Graph.figure_data_struct[1].figure_name, "h2");
        judge_send_msg4.Five_Graph.figure_data_struct[1].figure_type = 6;//整形
        judge_send_msg4.Five_Graph.figure_data_struct[1].color=6;
        judge_send_msg4.Five_Graph.figure_data_struct[1].width=1;
        judge_send_msg4.Five_Graph.figure_data_struct[1].start_y=900;
        judge_send_msg4.Five_Graph.figure_data_struct[1].start_x=1300;
        judge_send_msg4.Five_Graph.figure_data_struct[1].details_a=25;
        judge_send_msg4.Five_Graph.figure_data_struct[1].details_c=judge_rece_mesg.radar_status_frame.enemy_hp.enemy_engineer % 1024;
        judge_send_msg4.Five_Graph.figure_data_struct[1].details_d=judge_rece_mesg.radar_status_frame.enemy_hp.enemy_engineer / 1024;
        judge_send_msg4.Five_Graph.figure_data_struct[1].details_e=0;

        //敌方步兵3
        strcpy((char *) judge_send_msg4.Five_Graph.figure_data_struct[2].figure_name, "h3");
        judge_send_msg4.Five_Graph.figure_data_struct[2].figure_type = 6;//整形
        judge_send_msg4.Five_Graph.figure_data_struct[2].color=6;
        judge_send_msg4.Five_Graph.figure_data_struct[2].width=1;
        judge_send_msg4.Five_Graph.figure_data_struct[2].start_y=900;
        judge_send_msg4.Five_Graph.figure_data_struct[2].start_x=1420;
        judge_send_msg4.Five_Graph.figure_data_struct[2].details_a=25;
        judge_send_msg4.Five_Graph.figure_data_struct[2].details_c=judge_rece_mesg.radar_status_frame.enemy_hp.enemy_infantry_3 % 1024;
        judge_send_msg4.Five_Graph.figure_data_struct[2].details_d=judge_rece_mesg.radar_status_frame.enemy_hp.enemy_infantry_3 / 1024;
        judge_send_msg4.Five_Graph.figure_data_struct[2].details_e=0;

        //敌方步兵4
        strcpy((char *) judge_send_msg4.Five_Graph.figure_data_struct[3].figure_name, "h4");
        judge_send_msg4.Five_Graph.figure_data_struct[3].figure_type = 6;//整形
        judge_send_msg4.Five_Graph.figure_data_struct[3].color=6;
        judge_send_msg4.Five_Graph.figure_data_struct[3].width=1;
        judge_send_msg4.Five_Graph.figure_data_struct[3].start_y=900;
        judge_send_msg4.Five_Graph.figure_data_struct[3].start_x=1540;
        judge_send_msg4.Five_Graph.figure_data_struct[3].details_a=25;
        judge_send_msg4.Five_Graph.figure_data_struct[3].details_c=judge_rece_mesg.radar_status_frame.enemy_hp.enemy_infantry_4 % 1024;
        judge_send_msg4.Five_Graph.figure_data_struct[3].details_d=judge_rece_mesg.radar_status_frame.enemy_hp.enemy_infantry_4 / 1024;
        judge_send_msg4.Five_Graph.figure_data_struct[3].details_e=0;

        //敌方哨兵
        strcpy((char *) judge_send_msg4.Five_Graph.figure_data_struct[4].figure_name, "h5");
        judge_send_msg4.Five_Graph.figure_data_struct[4].figure_type = 6;//整形
        judge_send_msg4.Five_Graph.figure_data_struct[4].color=6;
        judge_send_msg4.Five_Graph.figure_data_struct[4].width=1;
        judge_send_msg4.Five_Graph.figure_data_struct[4].start_y=900;
        judge_send_msg4.Five_Graph.figure_data_struct[4].start_x=1780;
        judge_send_msg4.Five_Graph.figure_data_struct[4].details_a=25;
        judge_send_msg4.Five_Graph.figure_data_struct[4].details_c=judge_rece_mesg.radar_status_frame.enemy_hp.enemy_sentry % 1024;
        judge_send_msg4.Five_Graph.figure_data_struct[4].details_d=judge_rece_mesg.radar_status_frame.enemy_hp.enemy_sentry / 1024;
        judge_send_msg4.Five_Graph.figure_data_struct[4].details_e=0;
    }
    else
    {
        //敌方英雄
        strcpy((char *) judge_send_msg4.Five_Graph.figure_data_struct[0].figure_name, "h1");
        judge_send_msg4.Five_Graph.figure_data_struct[0].figure_type = 6;//整形
        judge_send_msg4.Five_Graph.figure_data_struct[0].color=6;
        judge_send_msg4.Five_Graph.figure_data_struct[0].width=1;
        judge_send_msg4.Five_Graph.figure_data_struct[0].start_y=900;
        judge_send_msg4.Five_Graph.figure_data_struct[0].start_x=80;
        judge_send_msg4.Five_Graph.figure_data_struct[0].details_a=25;
        judge_send_msg4.Five_Graph.figure_data_struct[0].details_c=judge_rece_mesg.radar_status_frame.enemy_hp.enemy_hero % 1024;
        judge_send_msg4.Five_Graph.figure_data_struct[0].details_d=judge_rece_mesg.radar_status_frame.enemy_hp.enemy_hero / 1024;
        judge_send_msg4.Five_Graph.figure_data_struct[0].details_e=0;

        //敌方工程
        strcpy((char *) judge_send_msg4.Five_Graph.figure_data_struct[1].figure_name, "h2");
        judge_send_msg4.Five_Graph.figure_data_struct[1].figure_type = 6;//整形
        judge_send_msg4.Five_Graph.figure_data_struct[1].color=6;
        judge_send_msg4.Five_Graph.figure_data_struct[1].width=1;
        judge_send_msg4.Five_Graph.figure_data_struct[1].start_y=900;
        judge_send_msg4.Five_Graph.figure_data_struct[1].start_x=320;
        judge_send_msg4.Five_Graph.figure_data_struct[1].details_a=25;
        judge_send_msg4.Five_Graph.figure_data_struct[1].details_c=judge_rece_mesg.radar_status_frame.enemy_hp.enemy_engineer % 1024;
        judge_send_msg4.Five_Graph.figure_data_struct[1].details_d=judge_rece_mesg.radar_status_frame.enemy_hp.enemy_engineer / 1024;
        judge_send_msg4.Five_Graph.figure_data_struct[1].details_e=0;

        //敌方步兵3
        strcpy((char *) judge_send_msg4.Five_Graph.figure_data_struct[2].figure_name, "h3");
        judge_send_msg4.Five_Graph.figure_data_struct[2].figure_type = 6;//整形
        judge_send_msg4.Five_Graph.figure_data_struct[2].color=6;
        judge_send_msg4.Five_Graph.figure_data_struct[2].width=1;
        judge_send_msg4.Five_Graph.figure_data_struct[2].start_y=900;
        judge_send_msg4.Five_Graph.figure_data_struct[2].start_x=440;
        judge_send_msg4.Five_Graph.figure_data_struct[2].details_a=25;
        judge_send_msg4.Five_Graph.figure_data_struct[2].details_c=judge_rece_mesg.radar_status_frame.enemy_hp.enemy_infantry_3 % 1024;
        judge_send_msg4.Five_Graph.figure_data_struct[2].details_d=judge_rece_mesg.radar_status_frame.enemy_hp.enemy_infantry_3 / 1024;
        judge_send_msg4.Five_Graph.figure_data_struct[2].details_e=0;

        //敌方步兵4
        strcpy((char *) judge_send_msg4.Five_Graph.figure_data_struct[3].figure_name, "h4");
        judge_send_msg4.Five_Graph.figure_data_struct[3].figure_type = 6;//整形
        judge_send_msg4.Five_Graph.figure_data_struct[3].color=6;
        judge_send_msg4.Five_Graph.figure_data_struct[3].width=1;
        judge_send_msg4.Five_Graph.figure_data_struct[3].start_y=900;
        judge_send_msg4.Five_Graph.figure_data_struct[3].start_x=560;
        judge_send_msg4.Five_Graph.figure_data_struct[3].details_a=25;
        judge_send_msg4.Five_Graph.figure_data_struct[3].details_c=judge_rece_mesg.radar_status_frame.enemy_hp.enemy_infantry_4 % 1024;
        judge_send_msg4.Five_Graph.figure_data_struct[3].details_d=judge_rece_mesg.radar_status_frame.enemy_hp.enemy_infantry_4 / 1024;
        judge_send_msg4.Five_Graph.figure_data_struct[3].details_e=0;

        //敌方哨兵
        strcpy((char *) judge_send_msg4.Five_Graph.figure_data_struct[4].figure_name, "h5");
        judge_send_msg4.Five_Graph.figure_data_struct[4].figure_type = 6;//整形
        judge_send_msg4.Five_Graph.figure_data_struct[4].color=6;
        judge_send_msg4.Five_Graph.figure_data_struct[4].width=1;
        judge_send_msg4.Five_Graph.figure_data_struct[4].start_y=900;
        judge_send_msg4.Five_Graph.figure_data_struct[4].start_x=680;
        judge_send_msg4.Five_Graph.figure_data_struct[4].details_a=25;
        judge_send_msg4.Five_Graph.figure_data_struct[4].details_c=judge_rece_mesg.radar_status_frame.enemy_hp.enemy_sentry % 1024;
        judge_send_msg4.Five_Graph.figure_data_struct[4].details_d=judge_rece_mesg.radar_status_frame.enemy_hp.enemy_sentry / 1024;
        judge_send_msg4.Five_Graph.figure_data_struct[4].details_e=0;
    }

    robot_interaction_data.data_cmd_id = INTERACTION_FIGURE3_ID;
    data_packet_pack(ROBO_INTERACTION_DATA_ID, (uint8_t *)&judge_send_msg4.Five_Graph,
                     sizeof(judge_send_msg4.Five_Graph) , robot_interaction_data);
}

/*!
 * @brief 将机器人交互数据打包
 * @param cmd_id 裁判系统命令码
 * @param p_data 数据源
 * @param len    数据长度
 * @param robot_interaction_data 机器人交互数据包(0x0301)
 */
void data_packet_pack(uint16_t cmd_id, uint8_t *p_data, uint16_t len,
                      robot_interaction_data_t robot_interaction_data_)
{
    //包长度5+2+len+2
    uint16_t frame_length = HEADER_LEN + CMD_LEN + len + CRC_LEN + INTERACTIVE_HEADER_LEN;

    protocol_packet_pack(cmd_id, p_data, len, tx_buf, robot_interaction_data_);

    //数据从tx_buf存入fifo
    fifo_s_puts(&judge_txdata_fifo, tx_buf, frame_length);
}

/*!
 * @brief 将数据打包存入tx_buf数组
 * @param cmd_id 裁判系统命令码
 * @param p_data  数据源
 * @param len 有效数据长度
 * @param tx_buf 将数据打包存入的数组
 * @param robot_interaction_data_ 机器人交互数据包(0x0301)
 * @return
 */
uint8_t *protocol_packet_pack(uint16_t cmd_id, uint8_t *p_data, uint16_t len, uint8_t *tx_buf,
                              robot_interaction_data_t robot_interaction_data_) {
    uint16_t       frame_length = HEADER_LEN + CMD_LEN + len + CRC_LEN + INTERACTIVE_HEADER_LEN;
    frame_header_t *p_header    = (frame_header_t *) tx_buf;

    p_header->sof         = DN_REG_ID;
    p_header->data_length = len + 6;
    p_header->seq         = 0;

    memcpy(&tx_buf[HEADER_LEN], (uint8_t *) &cmd_id, CMD_LEN);
    append_crc8_check_sum(tx_buf, HEADER_LEN);
    memcpy(&tx_buf[HEADER_LEN + CMD_LEN], (uint8_t *) &robot_interaction_data_, INTERACTIVE_HEADER_LEN);
    memcpy(&tx_buf[HEADER_LEN + CMD_LEN + INTERACTIVE_HEADER_LEN], p_data, len);
    append_crc16_check_sum(tx_buf, frame_length);
    return tx_buf;
}

/*!
 * @brief 将数据从FIFO中取出存入data_buf并发送
 * @param pfifo 发送数据FIFO
 * @param sof 帧头
 * @return
 */
uint32_t send_packed_fifo_data(uint8_t sof) {
    uint8_t  data_buf[JUDGE_FIFO_BUF_LEN];
    uint32_t fifo_count = fifo_used_count(&judge_txdata_fifo);
    if (fifo_count)
    {
        fifo_s_gets(&judge_txdata_fifo, data_buf, fifo_count);
        if (sof == DN_REG_ID)
            usart_dma_send(&judgement_usart, data_buf, fifo_count);
        else
            return 0;
    }
    return fifo_count;
}
