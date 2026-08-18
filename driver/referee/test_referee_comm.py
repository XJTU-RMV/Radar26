import argparse
import time

from .serial_comm import RefereeSerialManager
from .messages import (
    EnemyRobotCoo,
    Radar2RobotMessage,
    Radar2RobotMsgID,
    RadarLocationFrame,
    RadarStatusFrame,
    RobotStatusMessage,
    Sentry2RadarMessage,
)
from .protocol import MsgID, SubCmdID, OBJECT_ID


def status_message_decode_func(cmd_id, data):

    if cmd_id == MsgID.ROBOT_DATA.value:
        message = RobotStatusMessage.from_bytes(data)
        print(f"[STATUS] Robot Status: {message}")


def sentry2radar_message_decode_func(cmd_id, data):
    if cmd_id == MsgID.INTERACTIVE_DATA.value:
        import struct

        sub_cmd_id = struct.unpack("<H", data[0:2])[0]
        if sub_cmd_id != SubCmdID.SENTRY_2_RADAR.value:
            print(f"[INTERACTIVE] Ignore sub_cmd_id: 0x{sub_cmd_id:04x}")
            return
        message = Sentry2RadarMessage.from_bytes(data)
        print(f"[SENTRY2RADAR] Sentry to Radar Message: {message}")


def get_receiver_ids(faction):
    if faction == "blue":
        return [
            OBJECT_ID.B_HERO.value,
            OBJECT_ID.B_ENGINEER.value,
            OBJECT_ID.B_INFANTRY_3.value,
            OBJECT_ID.B_INFANTRY_4.value,
            OBJECT_ID.B_DRONE.value,
            OBJECT_ID.B_SENTRY.value,
        ]
    print("红方")
    return [
        OBJECT_ID.R_HERO.value,
        OBJECT_ID.R_ENGINEER.value,
        OBJECT_ID.R_INFANTRY_3.value,
        OBJECT_ID.R_INFANTRY_4.value,
        OBJECT_ID.R_DRONE.value,
        OBJECT_ID.R_SENTRY.value,
    ]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--faction", choices=["red", "blue"], default="red")
    args = parser.parse_args()
    is_blue = args.faction == "blue"

    serial_manager = RefereeSerialManager(port="/dev/ttyUSB0", baudrate=115200)
    print(serial_manager.initial_port)
    serial_manager.bind(MsgID.ROBOT_DATA.value, status_message_decode_func)
    serial_manager.bind(MsgID.INTERACTIVE_DATA.value, sentry2radar_message_decode_func)
    serial_manager.start()

    location_frame = RadarLocationFrame(
        hero=EnemyRobotCoo(1, 1.0, 2.0),
        engineer=EnemyRobotCoo(1, 3.0, 4.0),
        infantry_3=EnemyRobotCoo(1, 5.0, 6.0),
        infantry_4=EnemyRobotCoo(1, 7.0, 8.0),
        aerial=EnemyRobotCoo(0, -8888.0, -8888.0),
        sentry=EnemyRobotCoo(1, 52.0, 53.0),
    )

    status_frame = RadarStatusFrame()
    status_frame.msg_is_reliable = 1
    status_frame.enemy_hp.enemy_engineer = 10
    status_frame.enemy_hp.enemy_infantry_3 = 20
    status_frame.enemy_hp.enemy_infantry_4 = 30
    status_frame.enemy_hp.enemy_aerial = 40
    status_frame.enemy_hp.enemy_sentry = 50

    status_frame.ammunition_allowed.enemy_hero = 60
    status_frame.ammunition_allowed.enemy_infantry_3 = 70
    status_frame.ammunition_allowed.enemy_infantry_4 = 80
    status_frame.ammunition_allowed.enemy_aerial = 90
    status_frame.ammunition_allowed.enemy_sentry = 100

    status_frame.enemy_economy_remaining = 1000
    
    status_frame.enemy_economy_total = 0
    status_frame.enemy_outpost_is_destroyed = 1
    status_frame.base_armor_enabled = 1
    status_frame.is_hero_strike = 0
    status_frame.is_engineer_redeem = 0

    status_frame.is_enemy_constrained_defense = 0
    status_frame.is_enemy_invade_fortress = 0
    status_frame.is_enemy_revive_outpost = 0

    invincible_fields = (
        "enemy_hero",
        "enemy_engineer",
        "enemy_infantry_3",
        "enemy_infantry_4",
        "enemy_aerial",
        "enemy_sentry",
    )
    for field in invincible_fields:
        setattr(status_frame.enemy_is_invincible, field, 0)
    send_location = False
    receiver_ids = get_receiver_ids(args.faction)

    location_msg = Radar2RobotMessage(
        is_blue=is_blue,
        msg_ID=Radar2RobotMsgID.LOCATION,
        frame=location_frame,
    )
    status_msg = Radar2RobotMessage(
        is_blue=is_blue,
        msg_ID=Radar2RobotMsgID.STATUS,
        frame=status_frame,
    )

    while True:
        for field in invincible_fields:
            current = getattr(status_frame.enemy_is_invincible, field)
            setattr(status_frame.enemy_is_invincible, field, 1 - current)
        invincible_state = {
            field: getattr(status_frame.enemy_is_invincible, field)
            for field in invincible_fields
        }
       
        status_frame.msg_is_reliable += 1
        status_frame.enemy_hp.enemy_engineer += 1
        status_frame.enemy_hp.enemy_infantry_3 += 1
        status_frame.enemy_hp.enemy_infantry_4 += 1
        status_frame.enemy_hp.enemy_aerial += 1
        status_frame.enemy_hp.enemy_sentry += 1

        status_frame.ammunition_allowed.enemy_hero += 1
        status_frame.ammunition_allowed.enemy_infantry_3 += 1
        status_frame.ammunition_allowed.enemy_infantry_4 += 1
        status_frame.ammunition_allowed.enemy_aerial += 1
        status_frame.ammunition_allowed.enemy_sentry += 1

        status_frame.enemy_economy_remaining += 1

        # if send_location:
        #     location_msg.set_location_frame(location_frame)
        #     robot_msg = location_msg
        #     msg_id = Radar2RobotMsgID.LOCATION
        # else:
        status_msg.set_status_frame(status_frame)
        robot_msg = status_msg
        msg_id = Radar2RobotMsgID.STATUS

        serial_manager.summarize()
        print(f"[RADAR2ROBOT] Send {msg_id.name} to {args.faction}")
        print(f"剩余金币数:{status_frame.enemy_economy_remaining}")
        for receiver_id in receiver_ids:
            robot_msg.receiver_id = receiver_id
            serial_manager.tx(robot_msg.pack())
            time.sleep(0.2)
        send_location = not send_location
        # time.sleep(1)
