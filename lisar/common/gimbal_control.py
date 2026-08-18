from __future__ import annotations

from dataclasses import dataclass
import time

import numpy as np


SEARCH_START_BOUND_EPS_DEG = 0.5


@dataclass
class PixelAlignControllerConfig:
    max_step_deg: float = 0.5
    kp_yaw: float = 0.8
    kp_pitch: float = 1.0
    kd: float = 0.0
    deadband_px: float = 0.0
    settle_sleep_s: float = 0.0
    yaw_min_deg: float = -90.0
    yaw_max_deg: float = 90.0
    pitch_min_deg: float = -90.0
    pitch_max_deg: float = 90.0


class PixelAlignController:
    def __init__(self, camera_K, config: PixelAlignControllerConfig | None = None):
        self.camera_K = np.array(camera_K, dtype=np.float64).reshape(3, 3)
        self.config = config or PixelAlignControllerConfig()
        self.last_align_error = None
        self.last_align_time = None

    def reset(self):
        self.last_align_error = None
        self.last_align_time = None

    def step(self, gimbal, laser_center, target_center, current_angle):
        error_px = (
            float(target_center[0] - laser_center[0]),
            float(target_center[1] - laser_center[1]),
        )
        error_dist_px = np.hypot(error_px[0], error_px[1])
        if error_dist_px <= self.config.deadband_px:
            self.reset()
            return None

        fx = float(self.camera_K[0, 0])
        fy = float(self.camera_K[1, 1])
        now = time.time()
        align_error = np.array(
            [
                np.degrees(np.arctan(error_px[0] / fx)),
                -np.degrees(np.arctan(error_px[1] / fy)),
            ],
            dtype=np.float64,
        )
        if self.last_align_error is None:
            align_error_rate = np.zeros(2, dtype=np.float64)
        else:
            dt = now - self.last_align_time
            align_error_rate = (align_error - self.last_align_error) / dt

        align_step = np.array(
            [
                self.config.kp_yaw * align_error[0],
                self.config.kp_pitch * align_error[1],
            ],
            dtype=np.float64,
        ) + self.config.kd * align_error_rate

        yaw_step = np.clip(align_step[0], -self.config.max_step_deg, self.config.max_step_deg)
        pitch_step = np.clip(align_step[1], -self.config.max_step_deg, self.config.max_step_deg)
        target_yaw = np.clip(float(current_angle[0]) + yaw_step, self.config.yaw_min_deg, self.config.yaw_max_deg)
        target_pitch = np.clip(
            float(current_angle[1]) + pitch_step,
            self.config.pitch_min_deg,
            self.config.pitch_max_deg,
        )

        self.last_align_error = align_error
        self.last_align_time = now
        gimbal.set_angle(float(target_yaw), float(target_pitch))
        if self.config.settle_sleep_s > 0.0:
            time.sleep(self.config.settle_sleep_s)
        return float(target_yaw), float(target_pitch)


@dataclass
class SweepSearchConfig:
    yaw_min_deg: float
    yaw_max_deg: float
    pitch_min_deg: float
    pitch_max_deg: float
    yaw_speed_deg_s: float = 1.0
    pitch_speed_deg_s: float = 2.0


@dataclass(frozen=True)
class SweepSearchBounds:
    yaw_min_deg: float
    yaw_max_deg: float
    pitch_min_deg: float
    pitch_max_deg: float


@dataclass
class ObservedAngleBounds:
    yaw_min_deg: float | None = None
    yaw_max_deg: float | None = None
    pitch_min_deg: float | None = None
    pitch_max_deg: float | None = None
    count: int = 0

    def reset(self):
        self.yaw_min_deg = None
        self.yaw_max_deg = None
        self.pitch_min_deg = None
        self.pitch_max_deg = None
        self.count = 0

    def update(self, world_angle):
        yaw, pitch = float(world_angle[0]), float(world_angle[1])
        self.yaw_min_deg = yaw if self.yaw_min_deg is None else min(self.yaw_min_deg, yaw)
        self.yaw_max_deg = yaw if self.yaw_max_deg is None else max(self.yaw_max_deg, yaw)
        self.pitch_min_deg = pitch if self.pitch_min_deg is None else min(self.pitch_min_deg, pitch)
        self.pitch_max_deg = pitch if self.pitch_max_deg is None else max(self.pitch_max_deg, pitch)
        self.count += 1

    def snapshot(self):
        return {
            "count": self.count,
            "yaw_min_deg": self.yaw_min_deg,
            "yaw_max_deg": self.yaw_max_deg,
            "pitch_min_deg": self.pitch_min_deg,
            "pitch_max_deg": self.pitch_max_deg,
        }

    def search_bounds(self):
        if (
            self.yaw_min_deg is None
            or self.yaw_max_deg is None
            or self.pitch_min_deg is None
            or self.pitch_max_deg is None
        ):
            return None
        if self.yaw_min_deg >= self.yaw_max_deg or self.pitch_min_deg > self.pitch_max_deg:
            return None
        return SweepSearchBounds(
            self.yaw_min_deg,
            self.yaw_max_deg,
            self.pitch_min_deg,
            self.pitch_max_deg,
        )


class SweepSearchController:
    def __init__(self, config: SweepSearchConfig):
        self.config = config
        self.search_yaw = None
        self.search_yaw_dir = None
        self.search_yaw_travel = None
        self.search_pitch = None
        self.search_pitch_dir = None
        self.search_last_time = None
        self.last_target_yaw_dir = None
        self.search_bounds = None

    def reset(self, reset_target_memory=False):
        self.search_yaw = None
        self.search_yaw_dir = None
        self.search_yaw_travel = None
        self.search_pitch = None
        self.search_pitch_dir = None
        self.search_last_time = None
        if reset_target_memory:
            self.last_target_yaw_dir = None

    def remember_target(self, target_world_angle, current_angle):
        yaw_error = float(target_world_angle[0] - current_angle[0])
        if yaw_error > 0.0:
            self.last_target_yaw_dir = 1.0
        elif yaw_error < 0.0:
            self.last_target_yaw_dir = -1.0

    def set_search_bounds(self, bounds):
        if bounds is None:
            next_bounds = None
        else:
            next_bounds = SweepSearchBounds(
                float(bounds.yaw_min_deg),
                float(bounds.yaw_max_deg),
                float(bounds.pitch_min_deg),
                float(bounds.pitch_max_deg),
            )
        if next_bounds != self.search_bounds:
            self.reset()
            self.search_bounds = next_bounds

    def step(self, gimbal, current_angle):
        now = time.time()
        bounds = self.search_bounds
        yaw_min = self.config.yaw_min_deg if bounds is None else bounds.yaw_min_deg
        yaw_max = self.config.yaw_max_deg if bounds is None else bounds.yaw_max_deg
        pitch_min = self.config.pitch_min_deg if bounds is None else bounds.pitch_min_deg
        pitch_max = self.config.pitch_max_deg if bounds is None else bounds.pitch_max_deg
        pitch_center = (pitch_min + pitch_max) / 2.0
        pitch_amp = (pitch_max - pitch_min) / 2.0

        if self.search_yaw is None:
            start_yaw = float(current_angle[0])
            start_pitch = float(current_angle[1])
            if bounds is None and not yaw_min - SEARCH_START_BOUND_EPS_DEG <= start_yaw <= yaw_max + SEARCH_START_BOUND_EPS_DEG:
                raise ValueError(f"search start yaw {start_yaw:.2f} is outside [{yaw_min:.2f}, {yaw_max:.2f}]")
            if bounds is None and not pitch_min - SEARCH_START_BOUND_EPS_DEG <= start_pitch <= pitch_max + SEARCH_START_BOUND_EPS_DEG:
                raise ValueError(
                    f"search start pitch {start_pitch:.2f} is outside [{pitch_min:.2f}, {pitch_max:.2f}]"
                )
            start_yaw = float(np.clip(start_yaw, yaw_min, yaw_max))
            start_pitch = float(np.clip(start_pitch, pitch_min, pitch_max))

            self.search_yaw = start_yaw
            if self.last_target_yaw_dir is None:
                self.search_yaw_dir = 1.0 if yaw_max - start_yaw >= start_yaw - yaw_min else -1.0
            else:
                self.search_yaw_dir = self.last_target_yaw_dir
            self.search_yaw_travel = 0.0
            self.search_pitch = start_pitch
            self.search_pitch_dir = 1.0 if pitch_max - start_pitch >= start_pitch - pitch_min else -1.0
            self.search_last_time = now

        dt = now - self.search_last_time
        self.search_last_time = now
        remaining = self.config.yaw_speed_deg_s * dt
        while remaining > 0.0:
            boundary = yaw_max if self.search_yaw_dir > 0.0 else yaw_min
            distance_to_boundary = abs(boundary - self.search_yaw)
            step = min(remaining, distance_to_boundary)
            self.search_yaw += self.search_yaw_dir * step
            self.search_yaw_travel += step
            remaining -= step
            if self.search_yaw == boundary:
                self.search_yaw_dir = -self.search_yaw_dir

        if pitch_amp > 0.0:
            remaining = self.config.pitch_speed_deg_s * dt
            while remaining > 0.0:
                boundary = pitch_max if self.search_pitch_dir > 0.0 else pitch_min
                distance_to_boundary = abs(boundary - self.search_pitch)
                step = min(remaining, distance_to_boundary)
                self.search_pitch += self.search_pitch_dir * step
                remaining -= step
                if self.search_pitch == boundary:
                    self.search_pitch_dir = -self.search_pitch_dir
            target_pitch = self.search_pitch
        else:
            target_pitch = pitch_center
        gimbal.set_angle(float(self.search_yaw), float(target_pitch))
        return float(self.search_yaw), float(target_pitch)
