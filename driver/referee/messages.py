# 这里放置所有消息类型的定义
import struct
import ctypes
from enum import IntEnum
from abc import ABC, abstractmethod
from driver.referee.protocol import Crc, MsgID, SubCmdID, OBJECT_ID


try:
    import numpy as np
except ModuleNotFoundError:
    class _UInt8(int):
        pass

    class _UInt16(int):
        pass

    class _UInt32(int):
        pass

    class _Int8(int):
        pass

    class _Int16(int):
        pass

    class _Int32(int):
        pass

    class _Float32(float):
        pass

    class _NumpyScalarCompat:
        uint8 = _UInt8
        uint16 = _UInt16
        uint32 = _UInt32
        int8 = _Int8
        int16 = _Int16
        int32 = _Int32
        float32 = _Float32

    np = _NumpyScalarCompat()


class BaseMsg(ABC):
    def __init__(self):
        self.packed_buffer = b""

    @abstractmethod
    def pack(self):
        """Pack the message into the binary format"""
        return self.packed_buffer

    def get_packed_buffer(self):
        return self.packed_buffer


class RefereeGenericMessage(BaseMsg):
    """
    RoboMaster protocol message format:
    Frame structure: frame_header(5-byte) + cmd_id(2-byte) + data(n-byte) + frame_tail(2-byte CRC16)
    Frame header: SOF(1-byte) + data_length(2-byte) + seq(1-byte) + CRC8(1-byte)
    按照 RoboMaster 官方定义的帧结构，将原始数据打包成符合硬件通信标准的二进制字节流。
    """

    format_string = "BBBH B s H"
    SOF = 0xA5

    def __init__(self, command_id: np.uint16, *data_fields):    # 命令码，数据字段
        super().__init__()
        assert isinstance(command_id, np.uint16), "command_id must be np.uint16"
        self.command_id = command_id
        self.seq: int = 0
        self.data_fields = data_fields  # 字节流数据, tuple

    def pack(self):
        # 1. Prepare packed payload data
        packed_data = b"".join(self._pack_one_field(field) for field in self.data_fields)   # 如果是交互型数据，还包含数据头，因此这里遍历tuple，将字节流连起来

        # 2. Calculate data_length (cmd_id + data)
        data_length = len(packed_data)  # 2 bytes for cmd_id + data length

        # 3. Pack frame header (without CRC8)
        header_without_crc = struct.pack("<BHB", self.SOF, data_length, self.seq)

        # 4. Calculate CRC8 for header
        crc8_header = Crc.get_crc8_check_sum(header_without_crc)

        # 5. Complete frame header
        frame_header = header_without_crc + struct.pack("B", crc8_header)

        # 6. Pack cmd_id
        cmd_id_packed = struct.pack("H", int(self.command_id))

        # 7. Combine header + cmd_id + data
        message_without_tail = frame_header + cmd_id_packed + packed_data

        # 8. Calculate CRC16 for entire message
        crc16_tail = Crc.get_crc16_check_sum(message_without_tail)

        # 9. Pack final message
        self.packed_buffer = message_without_tail + struct.pack("H", crc16_tail)

        return self.packed_buffer

    def _pack_one_field(self, data):
        """
        将 Python/Numpy 的各种数据类型转换为 C 语言风格的二进制字节
        """
        if isinstance(data, bytes):
            return data
        elif isinstance(data, np.uint8):  # uint8
            return struct.pack("B", int(data))
        elif isinstance(data, np.uint16):  # uint16
            return struct.pack("H", int(data))
        elif isinstance(data, np.uint32):  # uint32
            return struct.pack("I", int(data))
        elif isinstance(data, np.int8):  # int8
            return struct.pack("b", int(data))
        elif isinstance(data, np.int16):  # int16
            return struct.pack("h", int(data))
        elif isinstance(data, np.int32):  # int32
            return struct.pack("i", int(data))
        elif isinstance(data, np.float32):  # float32
            return struct.pack("f", float(data))
        else:
            raise TypeError(
                f"Unsupported data type: {type(data)}. Supported types are: uint8, uint16, uint32, int8, int16, int32, float32."
            )

class Sentry2RadarData(ctypes.Structure):
    """
    Sentry to Radar data structure.
    This structure is used to send data from sentry to radar.
    """

    _pack_ = 1
    _fields_ = [
        ("hero_x", ctypes.c_float),  # Friend Hero X position
        ("hero_y", ctypes.c_float),  # Friend Hero Y position
        ("engineer_x", ctypes.c_float),  # Friend Engineer X position
        ("engineer_y", ctypes.c_float),  # Friend Engineer Y position
        ("standard_3_x", ctypes.c_float),  # Friend Standard 3 X position
        ("standard_3_y", ctypes.c_float),  # Friend Standard 3 Y position
        ("standard_4_x", ctypes.c_float),  # Friend Standard 4 X position
        ("standard_4_y", ctypes.c_float),  # Friend Standard 4 Y position
        ("sentry_x", ctypes.c_float),  # Friend Sentry X position
        ("sentry_y", ctypes.c_float),  # Friend Sentry Y position
        ("flag", ctypes.c_uint8),  # Flags for received
    ]

################################################# 雷达 -> 己方机器人
class Radar2RobotMsgID(IntEnum):
    STATUS = 1
    LOCATION = 2


class EnemyRobotCoo(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("is_reliable", ctypes.c_uint8),
        ("x", ctypes.c_float),
        ("y", ctypes.c_float),
    ]


class RadarLocationFrame(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("hero", EnemyRobotCoo),
        ("engineer", EnemyRobotCoo),
        ("infantry_3", EnemyRobotCoo),
        ("infantry_4", EnemyRobotCoo),
        ("aerial", EnemyRobotCoo),
        ("sentry", EnemyRobotCoo),
    ]


class RadarRobotID(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("enemy_hero", ctypes.c_uint16),
        ("enemy_engineer", ctypes.c_uint16),
        ("enemy_infantry_3", ctypes.c_uint16),
        ("enemy_infantry_4", ctypes.c_uint16),
        ("enemy_aerial", ctypes.c_uint16),
        ("enemy_sentry", ctypes.c_uint16),
    ]


class RadarStatusFrame(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("msg_is_reliable", ctypes.c_uint8),
        ("enemy_hp", RadarRobotID), # 信息波得到
        ("ammunition_allowed", RadarRobotID), # 允许发弹量，信息波得到
        ("defense_buff", RadarRobotID), # 信息波得到
        ("defense_defense_reduction", RadarRobotID), # 信息波得到
        ("hp_regen_buff", RadarRobotID), # 信息波得到
        ("heat_cooling_buff", RadarRobotID), # 信息波得到
        ("attack_buff", RadarRobotID), # 信息波得到
        ("enemy_is_invincible", RadarRobotID), # 对方机器人是否处于无敌状态，信息波得到
        ("enemy_economy_remaining", ctypes.c_uint16), # 地方剩余经济， 信息波得到
        ("enemy_economy_total", ctypes.c_uint16), # 敌方总经济， 信息波得到
        ("enemy_outpost_is_destroyed", ctypes.c_uint8), # 前哨站是否被摧毁
        ("base_armor_enabled", ctypes.c_uint8), # 基地装甲是否打开
        ("is_hero_strike", ctypes.c_uint8), # 英雄是否在吊射
        ("is_engineer_redeem", ctypes.c_uint8), # 工程是否在兑换
        ("is_enemy_constrained_defense", ctypes.c_uint8), # 敌方是否登上地面堡垒
        ("is_enemy_invade_fortress", ctypes.c_uint8), # 敌方是否占领我方堡垒
        ("is_enemy_revive_outpost", ctypes.c_uint8), # 敌方是否在前哨站
    ]


class Radar2RobotData(ctypes.Structure):
    """
    Radar to robot data structure.
    This structure is used to send data from radar to allied robots.
    """

    _pack_ = 1
    _fields_ = [
        ("msg_ID", ctypes.c_uint8),
        ("msg", ctypes.c_uint8 * 110),
        ("frame_tail", ctypes.c_uint8),
    ]

######################################################### end

class DartStatData(ctypes.Structure):
    """
    飞镖发射相关数据
    """

    _pack_ = 1
    _fields_ = [
        ("dart_remaining_time", ctypes.c_uint8),  # 己方飞镖发射剩余时间
        ("recent_hit_target", ctypes.c_uint16, 3),  # 最近一次己方飞镖击中的目标， 0-5
        ("accumulated_hit_count", ctypes.c_uint16, 3),  # 对方最近被击中的目标累计被击中计次数， 0-4
        ("selected_target", ctypes.c_uint16, 3),  # 己方飞镖此时选定的击打目标， 0-4
        ("reserve", ctypes.c_uint16, 7),  # Reserved for future use, 7 bits
    ]


class RadarMarkProgressData(ctypes.Structure):
    """
    对方/己方机器人标记进度与特殊标识情况 (2 bytes)
    """

    _pack_ = 1
    _fields_ = [
        ("enemy_hero", ctypes.c_uint16, 1),        # bit 0: 对方 1 号英雄机器人易伤情况
        ("enemy_engineer", ctypes.c_uint16, 1),    # bit 1: 对方 2 号工程机器人易伤情况
        ("enemy_standard_3", ctypes.c_uint16, 1),  # bit 2: 对方 3 号步兵机器人易伤情况
        ("enemy_standard_4", ctypes.c_uint16, 1),  # bit 3: 对方 4 号步兵机器人易伤情况
        ("enemy_aircraft", ctypes.c_uint16, 1),    # bit 4: 对方空中机器人特殊标识情况
        ("enemy_sentry", ctypes.c_uint16, 1),      # bit 5: 对方哨兵机器人易伤情况
        ("our_hero", ctypes.c_uint16, 1),          # bit 6: 己方 1 号英雄机器人特殊标识情况
        ("our_engineer", ctypes.c_uint16, 1),      # bit 7: 己方 2 号工程机器人特殊标识情况
        ("our_standard_3", ctypes.c_uint16, 1),    # bit 8: 己方 3 号步兵机器人特殊标识情况
        ("our_standard_4", ctypes.c_uint16, 1),    # bit 9: 己方 4 号步兵机器人特殊标识情况
        ("our_aircraft", ctypes.c_uint16, 1),      # bit 10: 己方空中机器人特殊标识情况
        ("our_sentry", ctypes.c_uint16, 1),        # bit 11: 己方哨兵机器人特殊标识情况
        ("enemy_aircraft_aimed", ctypes.c_uint16, 1),       # bit 12: 对方空中机器人被己方雷达激光瞄准
        ("enemy_aircraft_countered", ctypes.c_uint16, 1),   # bit 13: 对方空中机器人处于被反制状态
        ("our_aircraft_aimed", ctypes.c_uint16, 1),         # bit 14: 己方空中机器人被对方雷达激光瞄准
        ("our_aircraft_countered", ctypes.c_uint16, 1),     # bit 15: 己方空中机器人处于被反制状态
    ]


class RobotHPData(ctypes.Structure):
    """
    机器人血量数据(20 bytes)
    """

    _pack_ = 1
    _fields_ = [
        ("ally_hero_hp", ctypes.c_uint16),
        ("ally_engineer_hp", ctypes.c_uint16),
        ("ally_infantry_3_hp", ctypes.c_uint16),
        ("ally_infantry_4_hp", ctypes.c_uint16),
        ("ally_total_damage_delta", ctypes.c_int16),
        ("ally_sentry_hp", ctypes.c_uint16),
        ("ally_outpost_hp", ctypes.c_uint16),
        ("ally_base_hp", ctypes.c_uint16),
        ("enemy_outpost_hp", ctypes.c_uint16),
        ("enemy_base_hp", ctypes.c_uint16),
    ]


class RadarInfoData(ctypes.Structure):
    """
    雷达信息同步(1 bytes)
    """

    _pack_ = 1
    _fields_ = [
        ("double_vulnerability_count", ctypes.c_uint8, 2),  # 雷达拥有触发双倍易伤的机会 (0-2)
        ("is_double_vulnerability", ctypes.c_uint8, 1),  # 对方是否正在被触发双倍易伤 (0:未触发, 1:正在触发)
        ("encryption_level", ctypes.c_uint8, 2),  # 己方加密等级 (1-3)
        ("can_modify_password", ctypes.c_uint8, 1),  # 当前是否可以修改密钥 (1:可修改)
        ("reserve", ctypes.c_uint8, 2),  # 保留位
    ]


class RobotStatusData(ctypes.Structure):
    """
    机器人性能体系数据(17 bytes)
    """

    _pack_ = 1
    _fields_ = [
        ("robot_id", ctypes.c_uint8),  # Robot ID (1 byte)
        ("robot_level", ctypes.c_uint8),  # Robot level (1 byte)
        ("current_hp", ctypes.c_uint16),  # Current HP (2 byte)
        ("max_hp", ctypes.c_uint16),  # Max HP (2 byte)
        ("shooter_barrel_cooling_value", ctypes.c_uint16),  # Shooter barrel cooling value (2 byte)
        ("shooter_barrel_heat_limit", ctypes.c_uint16),  # Shooter barrel heat limit (2 byte)
        ("chassis_power_limit", ctypes.c_uint16),  # Chassis power limit (2 byte)
        ("bullet_speed_limit", ctypes.c_float),  # Bullet speed limit (4 byte)
        ("power_management_gimbal_output", ctypes.c_uint8, 1),
        ("power_management_chassis_output", ctypes.c_uint8, 1),  # Power management chassis output (1 bit)
        ("power_management_shooter_output", ctypes.c_uint8, 1),  # Power
        ("reserve", ctypes.c_uint8, 5),  # Reserved bits for future use
    ]


class Radar2ClientData(ctypes.Structure):
    """
    发送给裁判系统的消息，48 bytes
    """

    _pack_ = 1
    _fields_ = [
        ("opponent_hero_x", ctypes.c_uint16),
        ("opponent_hero_y", ctypes.c_uint16),
        ("opponent_engineer_x", ctypes.c_uint16),
        ("opponent_engineer_y", ctypes.c_uint16),
        ("opponent_standard_3_x", ctypes.c_uint16),
        ("opponent_standard_3_y", ctypes.c_uint16),
        ("opponent_standard_4_x", ctypes.c_uint16),
        ("opponent_standard_4_y", ctypes.c_uint16),
        ("opponent_aircraft_x", ctypes.c_uint16),
        ("opponent_aircraft_y", ctypes.c_uint16),
        ("opponent_sentry_x", ctypes.c_uint16),
        ("opponent_sentry_y", ctypes.c_uint16),
        ("ally_hero_x", ctypes.c_uint16),
        ("ally_hero_y", ctypes.c_uint16),
        ("ally_engineer_x", ctypes.c_uint16),
        ("ally_engineer_y", ctypes.c_uint16),
        ("ally_standard_3_x", ctypes.c_uint16),
        ("ally_standard_3_y", ctypes.c_uint16),
        ("ally_standard_4_x", ctypes.c_uint16),
        ("ally_standard_4_y", ctypes.c_uint16),
        ("ally_aircraft_x", ctypes.c_uint16),
        ("ally_aircraft_y", ctypes.c_uint16),
        ("ally_sentry_x", ctypes.c_uint16),
        ("ally_sentry_y", ctypes.c_uint16),
    ]


class RadarDecisionData(ctypes.Structure):
    """
    发动双倍易伤， 破解/更新密钥
    """

    _pack_ = 1
    _fields_ = [
        ("radar_cmd", ctypes.c_uint8),  # Radar command (1 byte) 是否开启双倍易伤
        ("password_cmd", ctypes.c_uint8), # 1: 更新密钥， 2: 破解密钥， 有10s CD
        ("password_1", ctypes.c_uint8), # 密钥1
        ("password_2", ctypes.c_uint8), # 密钥2
        ("password_3", ctypes.c_uint8), # 密钥3
        ("password_4", ctypes.c_uint8), # 密钥4
        ("password_5", ctypes.c_uint8), # 密钥5
        ("password_6", ctypes.c_uint8) # 密钥6
    ]


class StructureMessage(BaseMsg):
    STRUCT_CLASS = None

    def __init__(self, msg_id, **kwargs):
        if self.STRUCT_CLASS is None:
            raise NotImplementedError("struct class must be defined in subclass")

        super().__init__()
        self.struct_data = self.STRUCT_CLASS()
        self.msg_id = np.uint16(msg_id)

        for field, value in kwargs.items():
            if hasattr(self.struct_data, field):
                setattr(self.struct_data, field, value)
            else:
                raise ValueError(
                    f"Field {field} not found in {self.STRUCT_CLASS.__name__}"
                )

    def pack(self):
        msg = RefereeGenericMessage(self.msg_id, bytes(self.struct_data))

        self.packed_buffer = msg.pack()
        return self.packed_buffer

    @classmethod
    def from_bytes(cls, data: bytes):
        if cls.STRUCT_CLASS is None:
            raise NotImplementedError("struct class must be defined in subclass")

        if len(data) < ctypes.sizeof(cls.STRUCT_CLASS):
            raise ValueError(
                f"Data length {len(data)} is less than struct size {ctypes.sizeof(cls.STRUCT_CLASS)}"
            )

        instance = cls.__new__(cls)
        BaseMsg.__init__(instance)
        instance.struct_data = cls.STRUCT_CLASS.from_buffer_copy(data)
        instance.msg_id = cls._get_msg_id()
        return instance

    def __getattr__(self, item):
        if hasattr(self.struct_data, item):
            return getattr(self.struct_data, item)
        raise AttributeError(f"{item} not found in {self.STRUCT_CLASS.__name__}")

    def __setattr__(self, name, value):
        if name in ["struct_data", "msg_id", "packed_buffer"]:
            super().__setattr__(name, value)
        elif hasattr(self, "struct_data") and hasattr(self.struct_data, name):
            setattr(self.struct_data, name, value)
        else:
            super().__setattr__(name, value)

    def __str__(self):
        text = ""
        if hasattr(self, "struct_data"):
            for field in self.STRUCT_CLASS._fields_:
                name = field[0]
                value = getattr(self.struct_data, name)
                text += f"{field}: {value}\n"
        return text 

    @classmethod
    def _get_msg_id(cls):
        """子类可以重写此方法返回对应的消息ID"""
        raise NotImplementedError("子类必须实现 _get_msg_id 方法")


class InteractiveStructMessage(BaseMsg):
    STRUCT_CLASS = None  # 子类需要定义
    SUB_CMD_ID = None  # 子类需要定义

    def __init__(self, sender_id, receiver_id, **kwargs):
        if self.STRUCT_CLASS is None or self.SUB_CMD_ID is None:
            raise NotImplementedError("子类必须定义 STRUCT_CLASS 和 SUB_CMD_ID")

        super().__init__()
        self.sub_cmd_id = self.SUB_CMD_ID
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.data = self.STRUCT_CLASS()

        for key, value in kwargs.items():
            if hasattr(self.data, key):
                setattr(self.data, key, value)

    def pack(self):
        # 1. 手动拼接交互协议头（6 字节）：子命令 ID + 发送者 ID + 接收者 ID
        interactive_header = struct.pack(
            "<HHH", 
            int(self.sub_cmd_id), 
            int(self.sender_id), 
            int(self.receiver_id)
        )
        
        # 2. 拼接结构体数据
        payload = interactive_header + bytes(self.data)
        
        # 3. 直接调用通用的裁判系统消息打包类（MsgID 为 0x0301）
        msg = RefereeGenericMessage(
            np.uint16(MsgID.INTERACTIVE_DATA.value), 
            payload
        )
        
        self.packed_buffer = msg.pack()
        return self.packed_buffer

    def __getattr__(self, name):
        if hasattr(self.data, name):
            return getattr(self.data, name)
        else:
            return super().__getattr__(name)

    def __setattr__(self, name, value):
        if name in ["sub_cmd_id", "sender_id", "receiver_id", "data", "packed_buffer"]:
            super().__setattr__(name, value)
        elif hasattr(self, "data") and hasattr(self.data, name):
            setattr(self.data, name, value)
        else:
            super().__setattr__(name, value)

    @classmethod
    def from_bytes(cls, data_bytes: bytes):
        """从交互数据的字节创建消息，data_bytes应该是去掉前7字节(cmd_id + crc)的结构体数据"""
        if cls.STRUCT_CLASS is None:
            raise NotImplementedError("子类必须定义 STRUCT_CLASS")

        if len(data_bytes) < ctypes.sizeof(cls.STRUCT_CLASS):
            raise ValueError(
                f"Data length {len(data_bytes)} is less than struct size {ctypes.sizeof(cls.STRUCT_CLASS)}"
            )

        # 创建实例但不调用__init__
        instance = cls.__new__(cls)
        BaseMsg.__init__(instance)
        instance.sub_cmd_id = cls.SUB_CMD_ID
        instance.sender_id = struct.unpack("<H", data_bytes[2:4])[0]
        instance.receiver_id = struct.unpack("<H", data_bytes[4:6])[0]
        instance.data = cls.STRUCT_CLASS.from_buffer_copy(data_bytes[6:])
        return instance

    def __str__(self):
        text = ""
        if hasattr(self, "data"):
            for field in self.STRUCT_CLASS._fields_:
                name = field[0]
                value = getattr(self.data, name)
                text += f"{field}: {value}\n"
        return text


# 具体的消息类
class RobotStatusMessage(StructureMessage):
    STRUCT_CLASS = RobotStatusData

    def __init__(self, **kwargs):
        super().__init__(MsgID.ROBOT_DATA.value, **kwargs)

    @classmethod
    def _get_msg_id(cls):
        return np.uint16(MsgID.ROBOT_DATA.value)


class RobotHPMessage(StructureMessage):
    STRUCT_CLASS = RobotHPData

    def __init__(self, **kwargs):
        super().__init__(MsgID.ROBOT_HP.value, **kwargs)

    @classmethod
    def _get_msg_id(cls):
        return np.uint16(MsgID.ROBOT_HP.value)


class DartStatusMessage(StructureMessage):
    STRUCT_CLASS = DartStatData

    def __init__(self, **kwargs):
        super().__init__(MsgID.LAUNCHER_DATA.value, **kwargs)

    @classmethod
    def _get_msg_id(cls):
        return np.uint16(MsgID.LAUNCHER_DATA.value)


class RadarMarkMessage(StructureMessage):
    STRUCT_CLASS = RadarMarkProgressData

    def __init__(self, **kwargs):
        super().__init__(MsgID.RADAR_MARK_PROGRESS.value, **kwargs)

    @classmethod
    def _get_msg_id(cls):
        return np.uint16(MsgID.RADAR_MARK_PROGRESS.value)


class RadarInfoMessage(StructureMessage):
    STRUCT_CLASS = RadarInfoData

    def __init__(self, **kwargs):
        super().__init__(MsgID.RADAR_DECISION_SYNC.value, **kwargs)

    @classmethod
    def _get_msg_id(cls):
        return np.uint16(MsgID.RADAR_DECISION_SYNC.value)


class Radar2ClientMessage(StructureMessage):
    STRUCT_CLASS = Radar2ClientData

    def __init__(self, **kwargs):
        super().__init__(MsgID.CLIENT_RADAR_DATA.value, **kwargs)

    @classmethod
    def _get_msg_id(cls):
        return np.uint16(MsgID.CLIENT_RADAR_DATA.value)


class Sentry2RadarMessage(InteractiveStructMessage):
    STRUCT_CLASS = Sentry2RadarData
    SUB_CMD_ID = SubCmdID.SENTRY_2_RADAR.value

    def __init__(self, is_blue=True, **kwargs):
        sender_id = OBJECT_ID.B_SENTRY.value if is_blue else OBJECT_ID.R_SENTRY.value
        receiver_id = OBJECT_ID.B_RADAR.value if is_blue else OBJECT_ID.R_RADAR.value
        super().__init__(sender_id, receiver_id, **kwargs)


class Radar2RobotMessage(InteractiveStructMessage):
    STRUCT_CLASS = Radar2RobotData
    SUB_CMD_ID = SubCmdID.RADAR_2_SENTRY.value

    def __init__(self, is_blue=True, msg_ID=Radar2RobotMsgID.LOCATION, frame=None, receiver_id=None, **kwargs):
        sender_id = OBJECT_ID.B_RADAR.value if is_blue else OBJECT_ID.R_RADAR.value
        if receiver_id is None:
            receiver_id = OBJECT_ID.B_SENTRY.value if is_blue else OBJECT_ID.R_SENTRY.value
        kwargs.setdefault("msg_ID", int(msg_ID))
        kwargs.setdefault("frame_tail", 0xA5)
        if frame is not None:
            kwargs["msg"] = self._pack_frame(frame)
        super().__init__(sender_id, receiver_id, **kwargs)

    @staticmethod
    def _pack_frame(frame):
        frame_bytes = bytes(frame)
        if len(frame_bytes) > 110:
            raise ValueError(f"Radar2Robot frame length {len(frame_bytes)} exceeds 110 bytes")

        msg = (ctypes.c_uint8 * 110)()
        msg[:len(frame_bytes)] = frame_bytes
        return msg

    def set_location_frame(self, frame):
        self.msg_ID = int(Radar2RobotMsgID.LOCATION)
        self.msg = self._pack_frame(frame)

    def set_status_frame(self, frame):
        self.msg_ID = int(Radar2RobotMsgID.STATUS)
        self.msg = self._pack_frame(frame)


Radar2SentryMsgID = Radar2RobotMsgID
Radar2SentryData = Radar2RobotData
Radar2SentryMessage = Radar2RobotMessage


class RadarDecisionMessage(InteractiveStructMessage):
    STRUCT_CLASS = RadarDecisionData
    SUB_CMD_ID = SubCmdID.RADAR_DECISION.value

    def __init__(self, is_blue=True, **kwargs):
        sender_id = OBJECT_ID.B_RADAR.value if is_blue else OBJECT_ID.R_RADAR.value
        receiver_id = OBJECT_ID.SERVER.value
        super().__init__(sender_id, receiver_id, **kwargs)
