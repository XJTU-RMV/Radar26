# referee_comm.py
# 管理与裁判系统的通信
# 1. 管理消息发送的种类以及发送频率
# 2. 自动接收裁判系统的消息
# 3. 管理0x0301交互数据发送节奏
# -*- coding: utf-8 -*-
from collections import deque
import random
import string
import time
import threading
from enum import Enum
from loguru import logger

from .serial_comm import RefereeSerialManager
from .messages import *
from .protocol import MsgID, OBJECT_ID


class RadarTriggerState(Enum):
    IDLE = 0    # 等待触发
    TRIGGERING = 1  # 正在触发/触发成功


class RefereeCommManager(RefereeSerialManager):
    _instance = None

    def __init__(self, port="/dev/ttyUSB0", baudrate=115200, args=None):
        if self.__class__._instance is not None:
            return self.__class__._instance
        excluded_ports = []
        if args is not None and hasattr(args, "gimbal") and hasattr(args.gimbal, "port"):
            excluded_ports.append(args.gimbal.port)

        super().__init__(port, baudrate, auto_scan=True, excluded_ports=excluded_ports)

        # 注册回调
        self.bind(MsgID.GAME_STATUS.value, self.game_status_message_decode_func)
        self.bind(MsgID.ROBOT_HP.value, self.robot_hp_message_decode_func)
        self.bind(MsgID.ROBOT_DATA.value, self.status_message_decode_func)
        self.bind(MsgID.LAUNCHER_DATA.value, self.dart_status_message_decode_func)
        self.bind(MsgID.RADAR_MARK_PROGRESS.value, self.radar_mark_progress_message_decode_func)
        self.bind(MsgID.RADAR_DECISION_SYNC.value, self.radar_info_message_decode_func)

        # Status flag
        self.faction = "red" if args is None else args.faction
        referee_cfg = args.get("referee", {}) if args is not None else {}
        radar2robot_cfg = referee_cfg.get("radar2robot", {})
        radar2client_cfg = referee_cfg.get("radar2client", {})
        self.double_vulnerability_trigger_after_start_seconds = [
            float(seconds)
            for seconds in referee_cfg.get(
                "double_vulnerability_trigger_after_start_seconds",
                [0.0, 180.0],
            )
        ]
        self.radar2robot_enabled = bool(radar2robot_cfg.get("enabled", True))
        self.radar2robot_send_location = bool(radar2robot_cfg.get("send_location", True))
        self.radar2robot_send_status = bool(radar2robot_cfg.get("send_status", True))
        self.radar2robot_batch_interval = float(radar2robot_cfg.get("batch_interval", 0.7))
        self.interactive_tx_interval = float(radar2robot_cfg.get("tx_interval", 0.1))
        self.radar2client_tx_interval = float(radar2client_cfg.get("tx_interval", 0.2))
        self.radar2robot_receiver_ids = self._get_radar2robot_receiver_ids(
            radar2robot_cfg.get("receivers", ["all"])
        )
        self.game_type = 0
        self.game_progress = 0
        self.stage_remain_time = 0
        self.game_start_flag = False
        self.game_start_monotonic_time = None
        self.robot_hp_msg = RobotHPMessage()
        self.robot_hp_msg_received = False
        self.enemy_outpost_hp = 0
        self.enemy_base_hp = 0
        self.interactive_tx_queue = deque()
        self.next_interactive_tx_time = time.monotonic()
        self.interactive_tx_lock = threading.Lock()
        self.radar2client_stats_lock = threading.Lock()
        self.radar2client_tx_count = 0
        self.radar2client_first_tx_time = None
        self.radar2client_last_tx_time = None
        self.radar2client_current_source_counts = (0, 0, 12)
        self.radar2client_vision_coord_count = 0
        self.radar2client_demod_coord_count = 0
        self.radar2client_unknown_coord_count = 0
        logger.info(
            "[RefereeCommLogic] Radar2Robot periodic send: enabled={} receivers={} "
            "location={} status={} batch_interval={}s tx_interval={}s radar2client_tx_interval={}s",
            self.radar2robot_enabled,
            self.radar2robot_receiver_ids,
            self.radar2robot_send_location,
            self.radar2robot_send_status,
            self.radar2robot_batch_interval,
            self.interactive_tx_interval,
            self.radar2client_tx_interval,
        )

        self.__class__._instance = self

        # TX
        # 1. 雷达 -> 己方机器人
        radar_location_frame = RadarLocationFrame()
        for robot in (
            radar_location_frame.hero,
            radar_location_frame.engineer,
            radar_location_frame.infantry_3,
            radar_location_frame.infantry_4,
            radar_location_frame.aerial,
            radar_location_frame.sentry,
        ):
            robot.is_reliable = 0
            robot.x = -8888
            robot.y = -8888
        self.radar2robot_msg = Radar2RobotMessage(
            is_blue=False,
            msg_ID=Radar2RobotMsgID.LOCATION,
            frame=radar_location_frame,
        )
        self.radar2robot_location_msg = self.radar2robot_msg

        radar_status_frame = RadarStatusFrame()
        radar_status_frame.msg_is_reliable = 0
        self.radar2robot_status_msg = Radar2RobotMessage(
            is_blue=False,
            msg_ID=Radar2RobotMsgID.STATUS,
            frame=radar_status_frame,
        )

        # 2. 雷达 -> 裁判系统
        self.radar2client_msg = Radar2ClientMessage(
            opponent_hero_x=0,
            opponent_hero_y=0,
            opponent_engineer_x=0,
            opponent_engineer_y=0,
            opponent_standard_3_x=0,
            opponent_standard_3_y=0,
            opponent_standard_4_x=0,
            opponent_standard_4_y=0,
            opponent_aircraft_x = 0,
            opponent_aircraft_y = 0,
            opponent_sentry_x=0,
            opponent_sentry_y=0,  # 24 敌方机器人坐标
            ally_hero_x=0,
            ally_hero_y=0,
            ally_engineer_x=0,
            ally_engineer_y=0,
            ally_standard_3_x=0,
            ally_standard_3_y=0,
            ally_standard_4_x=0,
            ally_standard_4_y=0,
            ally_aircraft_x = 0,
            ally_aircraft_y = 0,
            ally_sentry_x=0,
            ally_sentry_y=0,  # 48 己方机器人坐标
        )

        # 3. 飞镖请求易伤指令
        self.dart_info = DartStatusMessage(
            dart_remaining_time=0,
            recent_hit_target=0,
            accumulated_hit_count=0,
            selected_target=0,
            reserve=0,
        )

        self.target = 0
        self.last_target = 0
        self.target_3_counter = 0
        self.target_3_fixed = False

        # 4. 标记进度反馈
        self.radar_mark_progress_msg = RadarMarkMessage()

        # 5. 雷达双倍易伤标记
        self.radar_info_msg = RadarInfoMessage()
        self.double_vulnerability_count = 0 # 雷达拥有触发双倍易伤的机会 (0-2), int
        self.is_double_vulnerability = 0 # 对方是否正在被触发双倍易伤 (0:未触发, 1:正在触发), int
        self.request_count = 0  
        self.pending_double_vulnerability_count = 0
        self.trigger_state = RadarTriggerState.IDLE

        # 6. 解调信息波相关
        self.keys = None
        self.encryption_level = 1 # 己方加密等级,开局为1,最高为3 int, 无需手动更新
        self.can_modify_password = 0 # 当前是否可以修改密钥, int
        self.need_init_key_update = True
        self.break_key_correct = None # None: 未确认/等待中, True: 正确, False: 错误
        self.break_key_pending = False
        self.break_key_start_time = 0.0
        self.break_key_base_level = self.encryption_level
        self.break_key_timeout = 11.0
        self.next_break_key_send_time = 0.0
        self.pending_break_key = None
        self.break_key_active_key = None
        self.break_key_last_key = None

        # self.break_keys(self.keys)

    def break_keys(self, keys):
        """
        破解密钥
        keys: 六位stirng
        """
        now = time.monotonic()
        if now < self.next_break_key_send_time: # 检查是否在冷却
            self.pending_break_key = keys
            logger.info(
                "[RefereeCommLogic] Cached demodulated key during 10s cooldown, remaining={:.1f}s.",
                self.next_break_key_send_time - now,
            )
            return False

        self._send_break_key(keys, now)
        return True

    def _send_break_key(self, keys, now=None):
        now = time.monotonic() if now is None else now
        password_bytes = keys.encode("ascii")
        msg = RadarDecisionMessage(
            is_blue=self.faction == "blue",
            radar_cmd=self.request_count,
            password_cmd=2,
            password_1=password_bytes[0],
            password_2=password_bytes[1],
            password_3=password_bytes[2],
            password_4=password_bytes[3],
            password_5=password_bytes[4],
            password_6=password_bytes[5],
        )
        self._queue_interactive_msg(msg, priority=True)
        self.break_key_correct = None
        self.break_key_pending = True
        self.break_key_start_time = time.monotonic()
        self.break_key_base_level = self.encryption_level
        self.next_break_key_send_time = now + self.break_key_timeout # 下一次可发送时间
        self.break_key_active_key = keys
        self.break_key_last_key = keys
        logger.info("[RefereeCommLogic] Queued demodulated key verification message.")

    def update_keys(self):
        """随机生成一个六位密钥"""
        if self.can_modify_password != 1:
            logger.warning("[RefereeCommLogic] Skip key update: password modification is not allowed now.")
            return None

        charset = string.ascii_letters + string.digits
        password = "".join(random.choice(charset) for _ in range(6))
        password_bytes = password.encode("ascii")

        msg = RadarDecisionMessage(
            is_blue=self.faction == "blue",
            radar_cmd=self.request_count,
            password_cmd=1,
            password_1=password_bytes[0],
            password_2=password_bytes[1],
            password_3=password_bytes[2],
            password_4=password_bytes[3],
            password_5=password_bytes[4],
            password_6=password_bytes[5],
        )
        self._queue_interactive_msg(msg)
        self.keys = password
        logger.info("[RefereeCommLogic] Queued key update message.")
        return password
    
    def pack_radar_decision_message(self) -> RadarDecisionMessage:
        """ 触发双倍易伤"""
        return RadarDecisionMessage(
            is_blue=self.faction == "blue", 
            radar_cmd=self.request_count,
            password_cmd=0,
            password_1=0,
            password_2=0,
            password_3=0,
            password_4=0,
            password_5=0,
            password_6=0,
        )
    
    def reset_double_trigger_state(self):
        self.pending_double_vulnerability_count = 0
        self.trigger_state = RadarTriggerState.IDLE
        self.target = 0
        self.last_target = 0
        self.target_3_counter = 0
        self.target_3_fixed = False


    def get_faction(self):
        return self.faction

    def _get_radar2robot_receiver_ids(self, receivers=None):
        prefix = "B" if self.faction == "blue" else "R"
        receiver_map = {
            "hero": getattr(OBJECT_ID, f"{prefix}_HERO").value,
            "engineer": getattr(OBJECT_ID, f"{prefix}_ENGINEER").value,
            "infantry3": getattr(OBJECT_ID, f"{prefix}_INFANTRY_3").value,
            "infantry4": getattr(OBJECT_ID, f"{prefix}_INFANTRY_4").value,
            "drone": getattr(OBJECT_ID, f"{prefix}_DRONE").value,
            "sentry": getattr(OBJECT_ID, f"{prefix}_SENTRY").value,
        }
        if isinstance(receivers, str):
            receivers = [receivers]
        if receivers is None or "all" in receivers:
            return list(receiver_map.values())
        return [receiver_map[name] for name in receivers]

    def _send_radar2robot_msg(self, msg):
        msg.sender_id = OBJECT_ID.B_RADAR.value if self.faction == "blue" else OBJECT_ID.R_RADAR.value
        for receiver_id in self.radar2robot_receiver_ids:
            msg.receiver_id = receiver_id
            self._queue_interactive_msg(msg)

    def _queue_interactive_msg(self, msg, priority=False):
        with self.interactive_tx_lock:
            if priority:
                self.interactive_tx_queue.appendleft(msg.pack())
            else:
                self.interactive_tx_queue.append(msg.pack())

    def _send_next_interactive_msg(self, now):
        # 按照100ms间隔发送交互数据队列中的消息
        with self.interactive_tx_lock:
            if (
                not self.interactive_tx_queue
                or now < self.next_interactive_tx_time
                or not self.is_connected()
            ):
                return
            data = self.interactive_tx_queue.popleft()
            self.next_interactive_tx_time = now + self.interactive_tx_interval
        self.tx(data)

    def set_radar2client_source_counts(self, vision_count, demod_count, unknown_count):
        with self.radar2client_stats_lock:
            self.radar2client_current_source_counts = (
                int(vision_count),
                int(demod_count),
                int(unknown_count),
            )

    def _record_radar2client_tx(self, now):
        with self.radar2client_stats_lock:
            if self.radar2client_first_tx_time is None:
                self.radar2client_first_tx_time = now
            self.radar2client_last_tx_time = now
            self.radar2client_tx_count += 1
            vision_count, demod_count, unknown_count = self.radar2client_current_source_counts
            self.radar2client_vision_coord_count += vision_count
            self.radar2client_demod_coord_count += demod_count
            self.radar2client_unknown_coord_count += unknown_count

    def get_radar2client_stats(self):
        with self.radar2client_stats_lock:
            elapsed = 0.0
            if (
                self.radar2client_first_tx_time is not None
                and self.radar2client_last_tx_time is not None
            ):
                elapsed = self.radar2client_last_tx_time - self.radar2client_first_tx_time
            avg_freq = self.radar2client_tx_count / elapsed if elapsed > 0 else 0.0
            return {
                "tx_count": self.radar2client_tx_count,
                "elapsed": elapsed,
                "avg_freq": avg_freq,
                "vision_coord_count": self.radar2client_vision_coord_count,
                "demod_coord_count": self.radar2client_demod_coord_count,
                "unknown_coord_count": self.radar2client_unknown_coord_count,
            }

    def reset_radar2client_stats(self):
        with self.radar2client_stats_lock:
            self.radar2client_tx_count = 0
            self.radar2client_first_tx_time = None
            self.radar2client_last_tx_time = None
            self.radar2client_vision_coord_count = 0
            self.radar2client_demod_coord_count = 0
            self.radar2client_unknown_coord_count = 0

    def game_status_message_decode_func(self, cmd_id, data):
        if cmd_id != MsgID.GAME_STATUS.value:
            return
        was_game_start = self.game_start_flag
        stage = data[0]
        self.game_type = stage & 0x0F
        self.game_progress = (stage >> 4) & 0x0F
        self.stage_remain_time = int.from_bytes(data[1:3], "little")
        self.game_start_flag = self.game_progress == 4

        if self.game_start_flag:
            if not was_game_start:
                self.request_count = 0
                self.pending_double_vulnerability_count = 0
                self.trigger_state = RadarTriggerState.IDLE
                self.game_start_monotonic_time = time.monotonic()
                logger.info("[RefereeCommLogic] New game started, reset double vulnerability trigger state.")
            # logger.info("比赛中，距离比赛结束还有 {} s", self.stage_remain_time)
            pass
        else:
            self.game_start_monotonic_time = None
            logger.info(
                "比赛未开始，当前阶段={}，阶段剩余 {} s",
                self.game_progress,
                self.stage_remain_time,
            )

    def status_message_decode_func(self, cmd_id, data):
        if cmd_id == MsgID.ROBOT_DATA.value:
            message = RobotStatusMessage.from_bytes(data)
            self_id = message.robot_id
            if self_id < 100:
                self.faction = "red"
            else:
                self.faction = "blue"
            self.radar2robot_receiver_ids = self._get_radar2robot_receiver_ids()
            # print(f"[STATUS] Robot Status: {message}")

    def robot_hp_message_decode_func(self, cmd_id, data):
        if cmd_id == MsgID.ROBOT_HP.value:
            self.robot_hp_msg = RobotHPMessage.from_bytes(data)
            self.robot_hp_msg_received = True
            self.enemy_outpost_hp = self.robot_hp_msg.enemy_outpost_hp
            self.enemy_base_hp = self.robot_hp_msg.enemy_base_hp

    def dart_status_message_decode_func(self, cmd_id, data):
        if cmd_id == MsgID.LAUNCHER_DATA.value:
            self.dart_info = DartStatusMessage.from_bytes(data)
            self.target = self.dart_info.selected_target

            # print(f"[DART] Dart Status: {self.dart_info}")

    def radar_mark_progress_message_decode_func(self, cmd_id, data):
        if cmd_id == MsgID.RADAR_MARK_PROGRESS.value:
            self.radar_mark_progress_msg = RadarMarkMessage.from_bytes(data)
            # print(
            #     f"[RADAR MARK PROGRESS] Radar Mark Progress: {self.radar_mark_progress_msg}"
            # )

    def radar_info_message_decode_func(self, cmd_id, data):
        """雷达站信息同步回调函数, 会以1hz频率接收"""
        if cmd_id == MsgID.RADAR_DECISION_SYNC.value:
            self.radar_info_msg = RadarInfoMessage.from_bytes(data)
            self.is_double_vulnerability = self.radar_info_msg.is_double_vulnerability
            self.double_vulnerability_count =  self.radar_info_msg.double_vulnerability_count
            new_encryption_level = self.radar_info_msg.encryption_level
            if self.break_key_pending and new_encryption_level > self.break_key_base_level:
                self.break_key_correct = True
                self.break_key_pending = False
                self.pending_break_key = None
                self.break_key_active_key = None
                logger.info("[RefereeCommLogic] Demodulated key confirmed by encryption level update.")
            self.encryption_level = new_encryption_level
            self.can_modify_password = self.radar_info_msg.can_modify_password
            
    def start(self):
        """启动裁判系统通信管理器"""
        status = super().start()
        if not status:
            logger.warning(
                "Failed to start RefereeComm Main Handling Logic."
            )
            return False
        self.message_daemon_stop_event = threading.Event()
        self.message_daemon_thread = threading.Thread(
            target=self.message_daemon, daemon=True
        )
        self.message_daemon_thread.start()
        return True

    def close(self):
        """停止裁判系统通信管理器"""
        self.message_daemon_stop_event.set()
        super().close()

    def message_daemon(self):
        """消息处理守护线程"""
        next_robot_tx_time = time.monotonic()
        next_decision_tx_time = time.monotonic()
        next_radar2client_tx_time = time.monotonic()
        send_robot_location = True

        while not self.message_daemon_stop_event.is_set():

            now = time.monotonic()
            if (
                self.break_key_pending
                and now - self.break_key_start_time >= self.break_key_timeout
            ):
                self.break_key_correct = False
                self.break_key_pending = False
                self.break_key_active_key = None
                logger.warning("[RefereeCommLogic] Demodulated key was not confirmed in 10.0s.")

            if self.pending_break_key is not None and now >= self.next_break_key_send_time:
                pending_key = self.pending_break_key
                self.pending_break_key = None
                self._send_break_key(pending_key, now)
            
            # 1. 雷达 -> 己方机器人，周期发送位置/状态，可通过配置关闭或筛选接收方
            if self.radar2robot_enabled and now >= next_robot_tx_time:
                if self.radar2robot_send_location and self.radar2robot_send_status:
                    if send_robot_location:
                        self._send_radar2robot_msg(self.radar2robot_location_msg)
                    else:
                        self._send_radar2robot_msg(self.radar2robot_status_msg)
                    send_robot_location = not send_robot_location
                elif self.radar2robot_send_location:
                    self._send_radar2robot_msg(self.radar2robot_location_msg)
                elif self.radar2robot_send_status:
                    self._send_radar2robot_msg(self.radar2robot_status_msg)
                next_robot_tx_time = now + self.radar2robot_batch_interval

            # 2. 双倍易伤决策/更新密钥，目标1Hz
            if now >= next_decision_tx_time: 
                next_decision_tx_time = now + 1.0
                # 检查当前是否需要更新密钥
                if self.need_init_key_update and self.can_modify_password == 1:
                    if self.update_keys() is not None:
                        self.need_init_key_update = False
                elif self.can_modify_password == 1 and self.encryption_level < 3:
                    self.update_keys()

                if self.trigger_state == RadarTriggerState.IDLE:
                    if (
                        self.game_start_flag
                        and self.double_vulnerability_count > 0
                        and self.request_count < len(self.double_vulnerability_trigger_after_start_seconds)
                    ):
                        elapsed = now - self.game_start_monotonic_time
                        trigger_after = self.double_vulnerability_trigger_after_start_seconds[self.request_count]
                        if elapsed >= trigger_after:
                            logger.warning(
                                "[RefereeCommLogic] Triggering double vulnerability: "
                                "request={} elapsed={:.1f}s threshold={:.1f}s.",
                                self.request_count + 1,
                                elapsed,
                                trigger_after,
                            )
                            self.request_count += 1
                            self.pending_double_vulnerability_count = self.double_vulnerability_count
                            self._queue_interactive_msg(
                                self.pack_radar_decision_message(),
                                priority=True,
                            )
                            self.trigger_state = RadarTriggerState.TRIGGERING
                else:  # TRIGGERING 状态
                    if self.double_vulnerability_count < self.pending_double_vulnerability_count:
                        logger.warning("[RefereeCommLogic] Double vulnerability confirmed, resetting trigger state.")
                        self.reset_double_trigger_state()

                # 每次循环都更新 last_target
                self.last_target = self.target

            # 3, 雷达 -> 裁判系统坐标
            if now >= next_radar2client_tx_time: 
                if self.tx(self.radar2client_msg.pack()):
                    self._record_radar2client_tx(now)
                next_radar2client_tx_time = now + self.radar2client_tx_interval

            self._send_next_interactive_msg(now)

            time.sleep(0.01)


if __name__ == "__main__":
    # Example usage
    port = "/dev/ttyUSB0"  # Replace with your actual port
    baudrate = 115200

    referee_manager = RefereeCommManager(port, baudrate)
    if referee_manager.start():
        print("RefereeCommManager started successfully.")
    else:
        print("Failed to start RefereeCommManager.")

    try:
        while True:
            referee_manager.summarize()
            time.sleep(1)  # Keep the script running
    except KeyboardInterrupt:
        referee_manager.close()
        print("RefereeCommManager stopped.")
