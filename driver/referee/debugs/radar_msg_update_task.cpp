//
// Created by liangwenhao on 2025/2/20.
//

#include "radar_msg_update_task.h"
extern Super_Cap_t superCap;
extern osSemaphoreId_t RadarMsgReceiveHandle;
extern receive_judge_t judge_rece_mesg;
bool radar_msg_connect;
uint16_t msg_error_cnt = 0;
radar_msg_id_t radar_msg_id;
radar_status_frame_t radar_status_frame;
radar_location_frame_t radar_location_frame;

void radar_msg_update_task(void *argument){
//    superCap.scSet.enable = 1;
    osStatus_t stat;
    stat = osSemaphoreAcquire(RadarMsgReceiveHandle, 0);
    for(;;){
//        super_cap_control();
        stat = osSemaphoreAcquire(RadarMsgReceiveHandle,1000);
        if(stat == osOK){
            radar_msg_connect = true;

            if(judge_rece_mesg.radar_data_v2.frame_tail == 0xA5){
                switch((radar_msg_id_t)judge_rece_mesg.radar_data_v2.msg_ID)
                {
                    case radar_msg_status:
                        //处理状态类消息
                        msg_error_cnt = 0;
                        memcpy(&radar_status_frame, judge_rece_mesg.radar_data_v2.msg, sizeof(radar_status_frame_t));
                        break;
                    case radar_msg_location:
                        //处理位置类消息
                        msg_error_cnt = 0;
                        memcpy(&radar_location_frame, judge_rece_mesg.radar_data_v2.msg, sizeof(radar_location_frame_t));
                        break;
                    default:
                        msg_error_cnt ++ ;
                        //未知消息ID，进行错误处理
                        break;
                }
            }else{
                msg_error_cnt ++ ;
            }

            if(msg_error_cnt > 10){
                radar_msg_connect = false;
                msg_error_cnt = 0;
            }

        }else{
            radar_msg_connect = false;
        }
        osDelay(1);
    }
}
