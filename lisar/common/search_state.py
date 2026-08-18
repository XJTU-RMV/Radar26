from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class CountermeasureState(str, Enum):
    ACQUIRE = "ACQUIRE"
    TRACK = "TRACK"
    LOST = "LOST"
    REACQUIRE = "REACQUIRE"


@dataclass
class CountermeasureSearchState:
    reacquire_after_lost_frames: int = 3
    hold_after_seen_frames: int | None = None
    state: CountermeasureState = CountermeasureState.ACQUIRE
    lost_frames: int = 0
    has_seen_target: bool = False

    def reset(self):
        self.state = CountermeasureState.ACQUIRE
        self.lost_frames = 0
        self.has_seen_target = False

    def update(self, target_found):
        if target_found:
            self.state = CountermeasureState.TRACK
            self.lost_frames = 0
            self.has_seen_target = True
            return self.state

        self.lost_frames += 1
        if self.hold_after_seen_frames is not None:
            should_reacquire = not self.has_seen_target or self.lost_frames > self.hold_after_seen_frames
        else:
            should_reacquire = self.lost_frames >= self.reacquire_after_lost_frames

        if should_reacquire:
            self.state = CountermeasureState.REACQUIRE
        else:
            self.state = CountermeasureState.LOST
        return self.state
