from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, Optional, TypeVar


T = TypeVar("T")


@dataclass(frozen=True)
class Location:
    hero_x: int
    hero_y: int
    eng_x: int
    eng_y: int
    inf3_x: int
    inf3_y: int
    inf4_x: int
    inf4_y: int
    air_x: int
    air_y: int
    sentry_x: int
    sentry_y: int

    def to_line(self) -> str:
        return (
            f"hero=({self.hero_x:4d},{self.hero_y:4d}) "
            f"eng=({self.eng_x:4d},{self.eng_y:4d}) "
            f"inf3=({self.inf3_x:4d},{self.inf3_y:4d}) "
            f"inf4=({self.inf4_x:4d},{self.inf4_y:4d}) "
            f"air=({self.air_x:4d},{self.air_y:4d}) "
            f"sentry=({self.sentry_x:4d},{self.sentry_y:4d})"
        )

    def to_xy_pairs(self) -> tuple[tuple[int, int], ...]:
        return (
            (self.hero_x, self.hero_y),
            (self.eng_x, self.eng_y),
            (self.inf3_x, self.inf3_y),
            (self.inf4_x, self.inf4_y),
            (self.air_x, self.air_y),
            (self.sentry_x, self.sentry_y),
        )


@dataclass(frozen=True)
class HP:
    hero_hp: int
    eng_hp: int
    inf3_hp: int
    inf4_hp: int
    reserve_hp: int
    sentry_hp: int


@dataclass(frozen=True)
class AllowedBullets:
    hero_bullets: int
    inf3_bullets: int
    inf4_bullets: int
    air_bullets: int
    sentry_bullets: int


@dataclass(frozen=True)
class EnemyStatus:
    gold_remain: int
    gold_total: int
    supply_status: int
    central_status: int
    trapezoid_status: int
    fortress_status: int
    outpost_status: int
    raw_flags: int


@dataclass(frozen=True)
class BuffGroup:
    heal_percent: int
    cooldown_reduction: int
    defense_percent: int
    negative_defense_percent: int
    attack_percent: int


@dataclass(frozen=True)
class EnemyInvincibleStatus:
    hero: int
    engineer: int
    inf3: int
    inf4: int
    aerial: int
    sentry: int


@dataclass(frozen=True)
class BuffStatus:
    hero: BuffGroup
    engineer: BuffGroup
    inf3: BuffGroup
    inf4: BuffGroup
    sentry: BuffGroup
    sentry_pose: int
    hero_state: int
    engineer_state: int
    inf3_state: int
    inf4_state: int
    sentry_state: int
    enemy_is_invincible: EnemyInvincibleStatus


@dataclass(frozen=True)
class JammingKey:
    key: str
    key_bytes_hex: str


@dataclass(frozen=True)
class TimedValue(Generic[T]):
    value: T
    seq: int
    time_stamp: float


@dataclass(frozen=True)
class ProtocolMessage:
    cmd_id: int
    seq: int
    payload: object
    time_stamp: float


@dataclass
class DemodState:
    location: Optional[TimedValue[Location]] = None
    hp: Optional[TimedValue[HP]] = None
    allowed_bullets: Optional[TimedValue[AllowedBullets]] = None
    enemy_status: Optional[TimedValue[EnemyStatus]] = None
    buff_status: Optional[TimedValue[BuffStatus]] = None
    jamming_key: Optional[TimedValue[JammingKey]] = None
