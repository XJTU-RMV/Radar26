import serial
import struct
import time
import math
import threading

class GimbalController:
    def __init__(self, port, baudrate=115200):
        """
        初始化云台控制器
        :param port: 串口号 (Windows: 'COM3', Linux: '/dev/ttyUSB0')
        :param baudrate: 波特率 (必须与 STM32 cubemx 设置一致)
        """
        self.port = port
        self.baudrate = baudrate
        self.ser = None
        self.running = False
        self._rx_buf = bytearray()
        self.lock = threading.Lock()
        self.reconnect_interval = 1.0
        self.last_connect_attempt = 0.0
        self.last_error = None
        self.connected = False
        self._open_port()

    def _open_port(self):
        now = time.monotonic()
        if now - self.last_connect_attempt < self.reconnect_interval:
            return False
        self.last_connect_attempt = now

        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=0.1,  # 读取超时
                write_timeout=0.1
            )
            self.connected = True
            self.last_error = None
            print(f"[Info] Serial {self.port} opened successfully.")
            return True
        except serial.SerialException as e:
            self.ser = None
            self.connected = False
            self.last_error = e
            print(f"[Error] Failed to open serial port {self.port}: {e}")
            return False

    def _close_port(self):
        if self.ser is not None:
            try:
                if self.ser.is_open:
                    self.ser.close()
                    print("[Info] Serial closed.")
            except Exception as e:
                print(f"[Error] Close serial failed: {e}")
        self.ser = None
        self.connected = False

    def _ensure_connected(self):
        if self.ser is not None and self.ser.is_open:
            return True
        self._close_port()
        return self._open_port()

    def is_connected(self):
        return self.ser is not None and self.ser.is_open

    def set_angle(self, yaw: float, pitch: float):
        """
        发送目标角度给 STM32
        协议: 0x5A (1B) + Yaw(4B float) + Pitch(4B float) + 0xED (1B) = 10 Bytes
        """
        with self.lock:
            if not self._ensure_connected():
                return

            try:
                # struct.pack('<ff', ...) :
                # '<' 代表小端模式 (Little Endian)，STM32 默认也是小端
                # 'f' 代表 C语言中的 float (4字节)
                data_payload = struct.pack('<ff', -yaw, -pitch) # 取负使得转动角度满足直觉

                # 拼接帧头 (0x5A) 和 帧尾 (0xED)
                frame = b'\x5A' + data_payload + b'\xED'

                self.ser.write(frame)

            except (serial.SerialException, OSError) as e:
                print(f"[Error] Send failed, serial disconnected: {e}")
                self.last_error = e
                self._close_port()

    def get_angle(self):
        """
        读取 STM32 周期上报的单圈角度
        协议: 0xA5 (1B) + yaw_deg(4B float) + pitch_deg(4B float) + 0xED (1B) = 10 Bytes
        返回: (yaw_deg, pitch_deg) 或 None
        """
        with self.lock:
            if not self._ensure_connected():
                return None

            try:
                waiting = self.ser.in_waiting
                if waiting > 0:
                    self._rx_buf.extend(self.ser.read(waiting))

                frame_len = 10
                header = 0xA5
                tail = 0xED
                latest_angles = None

                while len(self._rx_buf) >= frame_len:
                    if self._rx_buf[0] != header:
                        del self._rx_buf[0]
                        continue

                    if self._rx_buf[frame_len - 1] != tail:
                        del self._rx_buf[0]
                        continue

                    frame = bytes(self._rx_buf[:frame_len])
                    del self._rx_buf[:frame_len]
                    latest_angles = struct.unpack('<ff', frame[1:9])

                if latest_angles is not None:
                    return latest_angles

            except (serial.SerialException, OSError) as e:
                print(f"[Error] Read angle failed, serial disconnected: {e}")
                self.last_error = e
                self._rx_buf.clear()
                self._close_port()

        return None

    def close(self):
        with self.lock:
            if self.ser and self.ser.is_open:
                try:
                    self.ser.flush() # 确保缓冲区数据已发送
                except Exception as e:
                    print(f"[Error] Flush serial failed: {e}")
            self._close_port()

    # 支持 with 语句 (上下文管理器)
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

# --- 测试示例 ---
if __name__ == "__main__":
    
    # 请修改为你的实际串口号
    # Windows 例子: 'COM3'
    # Linux/Mac 例子: '/dev/tty.usbmodem...' 或 '/dev/ttyUSB0'
    PORT_NAME = '/dev/ttyACM0' 
    
    # try:
    #     with GimbalController(PORT_NAME, 115200) as gimbal:
    #         print("Starting control loop... Press Ctrl+C to stop.")
            
    #         t = 0
    #         while True:
    #             # 1. 生成测试波形 (正弦波)
    #             # 让 Yaw 在 -30 到 30 度之间摆动
    #             # 让 Pitch 在 -10 到 10 度之间摆动
    #             yaw_cmd = 5.0 * math.sin(t)
    #             pitch_cmd = 3.0 * math.cos(t)
                
    #             # 2. 发送指令
    #             gimbal.set_angle(yaw_cmd, pitch_cmd)
                
    #             # 3. 读取并打印 STM32 的反馈 (如果有)
    #             # feedback = gimbal.read_feedback()
    #             # if feedback:
    #             #     print(f"STM32 Feedback: {feedback}")
                
    #             # 4. 控制发送频率
    #             # STM32 端你是 1ms 循环，这里发 20ms-50ms 一次足够了
    #             # 太快可能会把串口缓冲区塞满，虽然我们加了非阻塞保护
    #             time.sleep(0.02) 
                
    #             t += 0.05 # 时间步进

    # except KeyboardInterrupt:
    #     print("\nStopped by user.")
    # except Exception as e:
    #     print(f"An error occurred: {e}")

    try:
        with GimbalController(PORT_NAME, 115200) as gimbal:

            # while True:
                # angle = gimbal.get_angle()
                # if angle is not None:
                #     yaw, pitch = angle
                #     print(f"yaw: {yaw:2f}, pitch: {pitch:2f}")
                #     time.sleep(0.05)

            # 测试延迟
            
            gimbal.set_angle(0, 0)
            while True:
                angle = gimbal.get_angle()
                if angle is not None:
                    yaw, pitch = angle
                    print(f"yaw: {yaw:2f}, pitch: {pitch:2f}")
                    time.sleep(0.01)

    except KeyboardInterrupt:
        print("\nStopped by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
