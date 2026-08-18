#include "motor_test_task.h"
#include "main.h"
#include "can.h" 
#include "usart.h"    
#include "LK_motor_driver.h"
#include <string.h> 
#include <stdio.h> 

//sudo openocd -f ../st_nucleo_f4.cfg -c "program underlying_driver.elf verify reset exit"
// ================= 全局变量与中断相关 =================
float angle3=0.f, angle4=0.f; 
extern UART_HandleTypeDef huart1;

// 接收相关变量
uint8_t rx_byte_temp;       // 临时存 1 个字节
uint8_t rx_frame_buf[10];   // 存完整的帧
uint8_t rx_cnt = 0;         // 计数器
bool is_receiving_body = false; // 状态标志

// 这是中断回调函数，每收到 1 个字节，硬件会自动调用这里
// 不需要你在 while 循环里调用，它在后台发生！
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
    if(huart->Instance == USART1)
    {
        if (!is_receiving_body) 
        {
            // 状态 0: 等待帧头 0x5A
            if (rx_byte_temp == 0x5A) {
                is_receiving_body = true;
                rx_cnt = 0;
                rx_frame_buf[rx_cnt++] = rx_byte_temp; // 存入 0x5A
            }
        } 
        else 
        {
            // 状态 1: 接收剩余字节
            rx_frame_buf[rx_cnt++] = rx_byte_temp;

            // 满了 10 个字节，开始校验
            if (rx_cnt >= 10) {
                if (rx_frame_buf[9] == 0xED) { // 校验尾部
                    // 校验成功，直接更新全局目标
                    // 注意：这里是中断上下文，越快越好，memcpy 是安全的
                    memcpy(&angle3, &rx_frame_buf[1], 4);
                    memcpy(&angle4, &rx_frame_buf[5], 4);
                }
                // 无论成功失败，重置状态找下一个头
                is_receiving_body = false;
                rx_cnt = 0;
            }
        }
        
        // 【关键】重新开启中断，接收下一个字节
        HAL_UART_Receive_IT(&huart1, &rx_byte_temp, 1);
    }
}

// ================= PID 参数 =================
float m3_POS_kp=35.0f, m3_POS_ki=0.3f, m3_POS_kd=20.f;
float m3_VEL_kp=0.6f,  m3_VEL_ki=0.f,    m3_VEL_kd=2.f;
float m4_POS_kp=40.0f, m4_POS_ki=0.1f,   m4_POS_kd=0.f;
float m4_VEL_kp=0.7f,  m4_VEL_ki=0.f,    m4_VEL_kd=0.f;

#define ANGLE_MIN_DEG   (-180.0f)     
#define ANGLE_MAX_DEG   ( 180.0f)
#define ROUNDS_MIN      (-2.0f)       
#define ROUNDS_MAX      ( 2.0f)
#define LOOP_DT_S       (0.001f)      
#define MAX_ROUNDS_RATE (0.5f) // 既然不抖了，速度可以给快点
#define ANGLE_FEEDBACK_PERIOD_MS (5)  // 发送单圈角度的周期，设为5ms

static inline float clampf(float x, float lo, float hi) {
    if (x < lo) return lo; if (x > hi) return hi; return x;
}

static inline float slew_rate(float target, float current, float delta_max) {
    float d = target - current;
    d = clampf(d, -delta_max, delta_max);
    return current + d;
}

void motor_test_task(void *argument)
{
    // 换电机请修改以下四行参数
    static LK_motor m3(&hcan1, nullptr, 0, 2, ms_6015, 0); // yaw
    m3.motor_set_offset(5882);
    static LK_motor m4(&hcan1, nullptr, 0, 1, ms_6015, 0); // pitch
    m4.motor_set_offset(5000);

    // PID 初始化
    m3.posPid.pid_reset(10.f, 0.1f, m3_POS_kp, m3_POS_ki, m3_POS_kd);
    m3.velPid.pid_reset( 1.f, 0.1f, m3_VEL_kp, m3_VEL_ki, m3_VEL_kd);
    m4.posPid.pid_reset( 1.f, 0.1f, m4_POS_kp, m4_POS_ki, m4_POS_kd);
    m4.velPid.pid_reset(0.8f, 0.1f, m4_VEL_kp, m4_VEL_ki, m4_VEL_kd);
    
    // 【重要】启动 CAN (一定要加)
    HAL_CAN_Start(&hcan1);

    // 【重要】开启第一次串口中断监听
    // 只要调用这一次，后续会在 Callback 里自动续上
    HAL_UART_Receive_IT(&huart1, &rx_byte_temp, 1);

    float r3_cmd = 0.f;
    float r4_cmd = 0.f;
    uint8_t angle_frame[10];

    for(;;)
    {       
        // --------------------------------------------------------
        //  看！这里完全没有串口接收代码了！
        //  只有纯粹的控制逻辑，1ms 跑一次，雷打不动。
        //  数据会在后台自动更新 angle3 和 angle4。
        // --------------------------------------------------------

        // 1) 目标角度限幅
        float a3 = clampf(angle3, ANGLE_MIN_DEG, ANGLE_MAX_DEG);
        float a4 = clampf(angle4, ANGLE_MIN_DEG, ANGLE_MAX_DEG);

        // 2) 角度 -> 圈数
        float r3_target = a3 / 360.0f;
        float r4_target = a4 / 360.0f;

        // 3) 目标圈数限幅
        r3_target = clampf(r3_target, ROUNDS_MIN, ROUNDS_MAX);
        r4_target = clampf(r4_target, ROUNDS_MIN, ROUNDS_MAX);

        // 4) 目标限斜率 (现在这个会非常平滑)
        const float delta_max = MAX_ROUNDS_RATE * LOOP_DT_S; 
        r3_cmd = slew_rate(r3_target, r3_cmd, delta_max);
        r4_cmd = slew_rate(r4_target, r4_cmd, delta_max);

        // 5) 下发目标
        m3.motor_set_rounds(r3_cmd);
        m4.motor_set_rounds(r4_cmd);

        // 5ms 周期上报单圈角度，offset对应0度，ecd减小视为正方向
        static int angle_feedback_cnt = 0;
        if(++angle_feedback_cnt >= ANGLE_FEEDBACK_PERIOD_MS) {
            float yaw_deg = m3.motor_get_angle_deg();
            float pitch_deg = m4.motor_get_angle_deg();
            angle_feedback_cnt = 0;

            angle_frame[0] = 0xA5;
            memcpy(&angle_frame[1], &yaw_deg, sizeof(yaw_deg));
            memcpy(&angle_frame[5], &pitch_deg, sizeof(pitch_deg));
            angle_frame[9] = 0xED;
            HAL_UART_Transmit(&huart1, angle_frame, sizeof(angle_frame), 1);
        }

        osDelay(1); // 这里的 1ms 现在非常精准
    }
}
