from __future__ import annotations

from dataclasses import asdict
import json
import string
import struct
import time
from typing import Any

from .types import (
    AllowedBullets,
    BuffGroup,
    BuffStatus,
    DemodState,
    EnemyInvincibleStatus,
    EnemyStatus,
    HP,
    JammingKey,
    Location,
    ProtocolMessage,
    TimedValue,
)


SOF = 0xA5
CMD_0A01 = 0x0A01
CMD_0A02 = 0x0A02
CMD_0A03 = 0x0A03
CMD_0A04 = 0x0A04
CMD_0A05 = 0x0A05
CMD_0A06 = 0x0A06

SIGNAL_CMDS = {CMD_0A01, CMD_0A02, CMD_0A03, CMD_0A04, CMD_0A05}
JAMMING_CMDS = {CMD_0A06}
ALL_CMDS = SIGNAL_CMDS | JAMMING_CMDS

EXPECTED_PAYLOAD_LEN = {
    CMD_0A01: 24,
    CMD_0A02: 12,
    CMD_0A03: 10,
    CMD_0A04: 8,
    CMD_0A05: 41,
    CMD_0A06: 6,
}


def crc8_rm(data: bytes, init: int = 0xFF) -> int:
    poly = 0x8C
    crc = init & 0xFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = ((crc >> 1) ^ poly) & 0xFF if (crc & 0x01) else ((crc >> 1) & 0xFF)
    return crc & 0xFF


def crc16_rm(data: bytes, init: int = 0xFFFF) -> int:
    poly = 0x8408
    crc = init & 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            crc = ((crc >> 1) ^ poly) if (crc & 0x0001) else (crc >> 1)
            crc &= 0xFFFF
    return crc & 0xFFFF


def is_ascii_alnum6(payload: bytes) -> bool:
    allowed = set((string.ascii_letters + string.digits).encode("ascii"))
    return len(payload) == 6 and all(value in allowed for value in payload)


def _require_payload_len(cmd_id: int, payload: bytes) -> None:
    expected = EXPECTED_PAYLOAD_LEN.get(cmd_id)
    if expected is None:
        raise ValueError(f"unsupported cmd_id=0x{cmd_id:04X}")
    if len(payload) != expected:
        raise ValueError(
            f"cmd_id=0x{cmd_id:04X} payload length {len(payload)} != {expected}"
        )


def _u16le(payload: bytes, offset: int) -> int:
    return payload[offset] | (payload[offset + 1] << 8)


def decode_payload(cmd_id: int, payload: bytes) -> object:
    _require_payload_len(cmd_id, payload)
    if cmd_id == CMD_0A01:
        values = struct.unpack("<12H", payload)
        return Location(
            hero_x=values[0],
            hero_y=values[1],
            eng_x=values[2],
            eng_y=values[3],
            inf3_x=values[4],
            inf3_y=values[5],
            inf4_x=values[6],
            inf4_y=values[7],
            air_x=values[8],
            air_y=values[9],
            sentry_x=values[10],
            sentry_y=values[11],
        )
    if cmd_id == CMD_0A02:
        values = struct.unpack("<6H", payload)
        return HP(
            hero_hp=values[0],
            eng_hp=values[1],
            inf3_hp=values[2],
            inf4_hp=values[3],
            reserve_hp=values[4],
            sentry_hp=values[5],
        )
    if cmd_id == CMD_0A03:
        values = struct.unpack("<5H", payload)
        return AllowedBullets(
            hero_bullets=values[0],
            inf3_bullets=values[1],
            inf4_bullets=values[2],
            air_bullets=values[3],
            sentry_bullets=values[4],
        )
    if cmd_id == CMD_0A04:
        gold_remain, gold_total, raw_flags = struct.unpack("<HHI", payload)
        return EnemyStatus(
            gold_remain=gold_remain,
            gold_total=gold_total,
            supply_status=(raw_flags >> 0) & 0x1,
            central_status=(raw_flags >> 1) & 0x3,
            trapezoid_status=(raw_flags >> 3) & 0x1,
            fortress_status=(raw_flags >> 4) & 0x3,
            outpost_status=(raw_flags >> 6) & 0x3,
            raw_flags=raw_flags,
        )
    if cmd_id == CMD_0A05:
        def group(offset: int) -> BuffGroup:
            return BuffGroup(
                heal_percent=payload[offset],
                cooldown_reduction=_u16le(payload, offset + 1),
                defense_percent=payload[offset + 3],
                negative_defense_percent=payload[offset + 4],
                attack_percent=_u16le(payload, offset + 5),
            )

        def is_invincible(state: int) -> int:
            return int(state != 0)

        hero_state = payload[36]
        engineer_state = payload[37]
        inf3_state = payload[38]
        inf4_state = payload[39]
        sentry_state = payload[40]
        return BuffStatus(
            hero=group(0),
            engineer=group(7),
            inf3=group(14),
            inf4=group(21),
            sentry=group(28),
            sentry_pose=payload[35],
            hero_state=hero_state,
            engineer_state=engineer_state,
            inf3_state=inf3_state,
            inf4_state=inf4_state,
            sentry_state=sentry_state,
            enemy_is_invincible=EnemyInvincibleStatus(
                hero=is_invincible(hero_state),
                engineer=is_invincible(engineer_state),
                inf3=is_invincible(inf3_state),
                inf4=is_invincible(inf4_state),
                aerial=0,
                sentry=is_invincible(sentry_state),
            ),
        )
    if cmd_id == CMD_0A06:
        if not is_ascii_alnum6(payload):
            raise ValueError("0x0A06 payload must be 6 ASCII alphanumeric bytes")
        return JammingKey(
            key=payload.decode("ascii"),
            key_bytes_hex=" ".join(f"{value:02X}" for value in payload),
        )
    raise ValueError(f"unsupported cmd_id=0x{cmd_id:04X}")


def decode_rm_frame(frame: bytes, allowed_cmds: set[int] | None = None) -> ProtocolMessage:
    if len(frame) < 9:
        raise ValueError("frame too short")
    if frame[0] != SOF:
        raise ValueError("invalid SOF")
    data_len = frame[1] | (frame[2] << 8)
    frame_len = 5 + 2 + data_len + 2
    if len(frame) != frame_len:
        raise ValueError(f"frame length {len(frame)} != {frame_len}")
    if crc8_rm(frame[:4]) != frame[4]:
        raise ValueError("CRC8 check failed")
    if crc16_rm(frame[:-2]) != (frame[-2] | (frame[-1] << 8)):
        raise ValueError("CRC16 check failed")

    cmd_id = frame[5] | (frame[6] << 8)
    if allowed_cmds is not None and cmd_id not in allowed_cmds:
        raise ValueError(f"cmd_id=0x{cmd_id:04X} is not allowed in this mode")
    payload = frame[7:-2]
    return ProtocolMessage(
        cmd_id=cmd_id,
        seq=frame[3],
        payload=decode_payload(cmd_id, payload),
        time_stamp=time.time(),
    )


class RMFrameStreamParser:
    def __init__(self, allowed_cmds: set[int] | None = None, max_data_len: int = 80):
        self.allowed_cmds = allowed_cmds
        self.max_data_len = int(max_data_len)
        self.buffer = bytearray()

    def feed(self, data: bytes) -> list[ProtocolMessage]:
        self.buffer.extend(data)
        messages: list[ProtocolMessage] = []
        while True:
            sof = self.buffer.find(bytes([SOF]))
            if sof < 0:
                self.buffer.clear()
                return messages
            if sof > 0:
                del self.buffer[:sof]
            if len(self.buffer) < 7:
                return messages

            data_len = self.buffer[1] | (self.buffer[2] << 8)
            if data_len > self.max_data_len:
                del self.buffer[0]
                continue
            frame_len = 5 + 2 + data_len + 2
            if len(self.buffer) < frame_len:
                return messages
            frame = bytes(self.buffer[:frame_len])
            del self.buffer[:frame_len]
            try:
                messages.append(decode_rm_frame(frame, self.allowed_cmds))
            except ValueError:
                continue


def build_rm_frame(cmd_id: int, seq: int, payload: bytes) -> bytes:
    _require_payload_len(cmd_id, payload)
    header_without_crc = struct.pack("<BHB", SOF, len(payload), seq & 0xFF)
    header = header_without_crc + bytes([crc8_rm(header_without_crc)])
    frame_without_tail = header + struct.pack("<H", cmd_id) + payload
    return frame_without_tail + struct.pack("<H", crc16_rm(frame_without_tail))


def apply_message_to_state(state: DemodState, message: ProtocolMessage) -> None:
    timed_payload = TimedValue(
        value=message.payload,
        seq=message.seq,
        time_stamp=message.time_stamp,
    )
    if message.cmd_id == CMD_0A01:
        state.location = timed_payload
    elif message.cmd_id == CMD_0A02:
        state.hp = timed_payload
    elif message.cmd_id == CMD_0A03:
        state.allowed_bullets = timed_payload
    elif message.cmd_id == CMD_0A04:
        state.enemy_status = timed_payload
    elif message.cmd_id == CMD_0A05:
        state.buff_status = timed_payload
    elif message.cmd_id == CMD_0A06:
        state.jamming_key = timed_payload
    else:
        raise ValueError(f"unsupported cmd_id=0x{message.cmd_id:04X}")


def copy_state(state: DemodState) -> DemodState:
    return DemodState(
        location=state.location,
        hp=state.hp,
        allowed_bullets=state.allowed_bullets,
        enemy_status=state.enemy_status,
        buff_status=state.buff_status,
        jamming_key=state.jamming_key,
    )


def _payload_from_dict(cmd_id: int, payload: dict[str, Any]) -> object:
    if cmd_id == CMD_0A01:
        return Location(**payload)
    if cmd_id == CMD_0A02:
        return HP(**payload)
    if cmd_id == CMD_0A03:
        return AllowedBullets(**payload)
    if cmd_id == CMD_0A04:
        return EnemyStatus(**payload)
    if cmd_id == CMD_0A05:
        return BuffStatus(
            hero=BuffGroup(**payload["hero"]),
            engineer=BuffGroup(**payload["engineer"]),
            inf3=BuffGroup(**payload["inf3"]),
            inf4=BuffGroup(**payload["inf4"]),
            sentry=BuffGroup(**payload["sentry"]),
            sentry_pose=payload["sentry_pose"],
            hero_state=payload["hero_state"],
            engineer_state=payload["engineer_state"],
            inf3_state=payload["inf3_state"],
            inf4_state=payload["inf4_state"],
            sentry_state=payload["sentry_state"],
            enemy_is_invincible=EnemyInvincibleStatus(**payload["enemy_is_invincible"]),
        )
    if cmd_id == CMD_0A06:
        return JammingKey(**payload)
    raise ValueError(f"unsupported cmd_id=0x{cmd_id:04X}")


def demod_message_to_dict(message: ProtocolMessage) -> dict[str, Any]:
    return {
        "cmd_id": message.cmd_id,
        "seq": message.seq,
        "time_stamp": message.time_stamp,
        "payload": asdict(message.payload),
    }


def dict_to_demod_message(data: dict[str, Any]) -> ProtocolMessage:
    cmd_id = int(data["cmd_id"])
    return ProtocolMessage(
        cmd_id=cmd_id,
        seq=int(data["seq"]),
        time_stamp=float(data["time_stamp"]),
        payload=_payload_from_dict(cmd_id, data["payload"]),
    )


message_to_dict = demod_message_to_dict
dict_to_message = dict_to_demod_message


def encode_message_packet(message: ProtocolMessage) -> bytes:
    payload = json.dumps(demod_message_to_dict(message), separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return struct.pack(">I", len(payload)) + payload


def try_decode_packet(buffer: bytearray) -> ProtocolMessage | None:
    if len(buffer) < 4:
        return None
    payload_len = struct.unpack(">I", buffer[:4])[0]
    if payload_len <= 0:
        raise ValueError(f"invalid payload_len={payload_len}")
    if len(buffer) < 4 + payload_len:
        return None
    payload = bytes(buffer[4 : 4 + payload_len])
    del buffer[: 4 + payload_len]
    return dict_to_demod_message(json.loads(payload.decode("utf-8")))


def format_message_line(message: ProtocolMessage) -> str:
    payload = message.payload
    prefix = f"seq={message.seq:3d} cmd=0x{message.cmd_id:04X} "
    if isinstance(payload, Location):
        return prefix + payload.to_line()
    if isinstance(payload, HP):
        return (
            prefix
            + f"hp hero={payload.hero_hp} eng={payload.eng_hp} inf3={payload.inf3_hp} "
            + f"inf4={payload.inf4_hp} reserve={payload.reserve_hp} sentry={payload.sentry_hp}"
        )
    if isinstance(payload, AllowedBullets):
        return (
            prefix
            + f"ammo hero={payload.hero_bullets} inf3={payload.inf3_bullets} "
            + f"inf4={payload.inf4_bullets} air={payload.air_bullets} sentry={payload.sentry_bullets}"
        )
    if isinstance(payload, EnemyStatus):
        return (
            prefix
            + f"macro gold=({payload.gold_remain}/{payload.gold_total}) supply={payload.supply_status} "
            + f"central={payload.central_status} trapezoid={payload.trapezoid_status} "
            + f"fortress={payload.fortress_status} outpost={payload.outpost_status} "
            + f"flags=0x{payload.raw_flags:08X}"
        )
    if isinstance(payload, BuffStatus):
        return (
            prefix
            + f"buff sentry_pose={payload.sentry_pose} "
            + f"state hero={payload.hero_state} eng={payload.engineer_state} "
            + f"inf3={payload.inf3_state} inf4={payload.inf4_state} sentry={payload.sentry_state}"
            + " invincible="
            + f"hero:{payload.enemy_is_invincible.hero} "
            + f"eng:{payload.enemy_is_invincible.engineer} "
            + f"inf3:{payload.enemy_is_invincible.inf3} "
            + f"inf4:{payload.enemy_is_invincible.inf4} "
            + f"air:{payload.enemy_is_invincible.aerial} "
            + f"sentry:{payload.enemy_is_invincible.sentry}"
        )
    if isinstance(payload, JammingKey):
        return prefix + f"key={payload.key} hex={payload.key_bytes_hex}"
    return prefix + repr(payload)


def encode_app_packet(message: dict[str, Any]) -> bytes:
    payload = json.dumps(message, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return struct.pack(">I", len(payload)) + payload


def decode_app_packets(buffer: bytearray) -> list[dict[str, Any]]:
    messages: list[dict[str, Any]] = []
    while True:
        if len(buffer) < 4:
            return messages
        payload_len = struct.unpack(">I", buffer[:4])[0]
        if payload_len <= 0:
            raise ValueError(f"invalid payload_len={payload_len}")
        if len(buffer) < 4 + payload_len:
            return messages
        payload = bytes(buffer[4 : 4 + payload_len])
        del buffer[: 4 + payload_len]
        messages.append(json.loads(payload.decode("utf-8")))
