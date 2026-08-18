//
// Created by liangwenhao on 2025/2/20.
//

#ifndef _SUPER_CAPACITOR_TASK_H
#define _SUPER_CAPACITOR_TASK_H
#include "super_capacitor_driver.h"
#include "pid_driver.h"

enum radar_msg_id_t{
    radar_msg_status = 0,
    radar_msg_location = 1,
};

#ifdef __cplusplus
extern "C" {
#endif
//C
void radar_msg_update_task(void *argument);
#ifdef __cplusplus
}
#endif
//C++
#endif //_SUPER_CAPACITOR_TASK_H
