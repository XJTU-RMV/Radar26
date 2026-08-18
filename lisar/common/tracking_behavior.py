from __future__ import annotations

from dataclasses import replace
import time

import cv2
import numpy as np

from lisar.common.search_state import CountermeasureSearchState, CountermeasureState


MAX_STEP_DEG = 0.5
ALIGN_KP_YAW = 0.8
ALIGN_KP_PITCH = 1.0
ALIGN_KD = 0.0
ALIGN_DEADBAND_PX = 0.0
ALIGN_SETTLE_SLEEP_S = 0.02

MODULE_YAW_MIN_DEG = -1.0
MODULE_YAW_MAX_DEG = 17.0

# 比赛用
MODULE_PITCH_MIN_DEG = -7.0
MODULE_PITCH_MAX_DEG = 1.0
# 测试用
# MODULE_PITCH_MIN_DEG = -10.0
# MODULE_PITCH_MAX_DEG = 10.0

MODULE_HOLD_FRAMES = 80
MODULE_FILTER_MEASUREMENT_STD_DEG = 0.08
MODULE_FILTER_ACCEL_STD_DEG_S2 = 1.0
PASSIVE_MODULE_OFFSET_PX = 100


class ModuleAngleFilter:
    def __init__(self, measurement_std_deg, acceleration_std_deg_s2):
        self.x = np.zeros(4, dtype=np.float64)
        self.P = np.eye(4, dtype=np.float64)
        self.measurement_var = measurement_std_deg ** 2
        self.acceleration_var = acceleration_std_deg_s2 ** 2
        self.initialized = False

    def reset(self):
        self.x.fill(0.0)
        self.P = np.eye(4, dtype=np.float64)
        self.initialized = False

    def predict(self, dt):
        if not self.initialized:
            return

        F = np.array(
            [
                [1.0, 0.0, dt, 0.0],
                [0.0, 1.0, 0.0, dt],
                [0.0, 0.0, 1.0, 0.0],
                [0.0, 0.0, 0.0, 1.0],
            ],
            dtype=np.float64,
        )
        dt2 = dt * dt
        dt3 = dt2 * dt
        dt4 = dt2 * dt2
        q = self.acceleration_var
        Q = q * np.array(
            [
                [dt4 / 4.0, 0.0, dt3 / 2.0, 0.0],
                [0.0, dt4 / 4.0, 0.0, dt3 / 2.0],
                [dt3 / 2.0, 0.0, dt2, 0.0],
                [0.0, dt3 / 2.0, 0.0, dt2],
            ],
            dtype=np.float64,
        )
        self.x = F @ self.x
        self.P = F @ self.P @ F.T + Q

    def update(self, world_angle):
        z = np.array(world_angle, dtype=np.float64)
        if not self.initialized:
            self.x[:] = (z[0], z[1], 0.0, 0.0)
            self.P = np.diag([self.measurement_var, self.measurement_var, 1.0, 1.0])
            self.initialized = True
            return

        H = np.array(
            [
                [1.0, 0.0, 0.0, 0.0],
                [0.0, 1.0, 0.0, 0.0],
            ],
            dtype=np.float64,
        )
        R = self.measurement_var * np.eye(2, dtype=np.float64)
        y = z - H @ self.x
        S = H @ self.P @ H.T + R
        K = self.P @ H.T @ np.linalg.inv(S)
        self.x = self.x + K @ y
        self.P = (np.eye(4, dtype=np.float64) - K @ H) @ self.P

    def angle(self):
        if not self.initialized:
            return None
        return float(self.x[0]), float(self.x[1])


class TargetAngleStabilizer:
    def __init__(
        self,
        camera_K,
        dist_coeffs,
        yaw_min_deg=MODULE_YAW_MIN_DEG,
        yaw_max_deg=MODULE_YAW_MAX_DEG,
        pitch_min_deg=MODULE_PITCH_MIN_DEG,
        pitch_max_deg=MODULE_PITCH_MAX_DEG,
        measurement_std_deg=MODULE_FILTER_MEASUREMENT_STD_DEG,
        acceleration_std_deg_s2=MODULE_FILTER_ACCEL_STD_DEG_S2,
    ):
        self.camera_K = np.array(camera_K, dtype=np.float64).reshape(3, 3)
        self.dist_coeffs = np.asarray(dist_coeffs, dtype=np.float64).flatten()
        self.yaw_min_deg = float(yaw_min_deg)
        self.yaw_max_deg = float(yaw_max_deg)
        self.pitch_min_deg = float(pitch_min_deg)
        self.pitch_max_deg = float(pitch_max_deg)
        self.filter = ModuleAngleFilter(measurement_std_deg, acceleration_std_deg_s2)
        self.last_time = None

    def reset(self):
        self.filter.reset()
        self.last_time = None

    def update(self, detection, current_angle):
        now = time.time()
        if self.last_time is None:
            self.last_time = now
        else:
            self.filter.predict(now - self.last_time)
            self.last_time = now

        if detection is None:
            return None

        world_angle = detection.debug.get("world_angle")
        if world_angle is None:
            return detection

        yaw, pitch = float(world_angle[0]), float(world_angle[1])
        if not (
            self.yaw_min_deg <= yaw <= self.yaw_max_deg
            and self.pitch_min_deg <= pitch <= self.pitch_max_deg
        ):
            return None

        self.filter.update((yaw, pitch))
        filtered_world_angle = self.filter.angle()
        filtered_center = self._world_angle_to_pixel(filtered_world_angle, current_angle)
        debug = dict(detection.debug)
        debug["raw_center"] = detection.center
        debug["filtered_world_angle"] = filtered_world_angle
        debug["center"] = filtered_center
        return replace(detection, center=filtered_center, debug=debug)

    def _world_angle_to_pixel(self, world_angle, current_angle):
        rel_yaw = world_angle[0] - float(current_angle[0])
        rel_pitch = world_angle[1] - float(current_angle[1])
        rx = np.tan(np.radians(rel_yaw))
        ry = -np.tan(np.radians(rel_pitch))

        ray_point = np.array([[[rx, ry, 1.0]]], dtype=np.float64)
        rvec = np.zeros((3, 1), dtype=np.float64)
        tvec = np.zeros((3, 1), dtype=np.float64)
        img_pts, _ = cv2.projectPoints(ray_point, rvec, tvec, self.camera_K, self.dist_coeffs)
        return int(round(float(img_pts[0, 0, 0]))), int(round(float(img_pts[0, 0, 1])))


class LisarTrackingBehavior:
    def __init__(
        self,
        hold_frames=MODULE_HOLD_FRAMES,
        passive_offset_px=PASSIVE_MODULE_OFFSET_PX,
    ):
        self.search_state = CountermeasureSearchState(hold_after_seen_frames=hold_frames)
        self.passive_offset_px = int(passive_offset_px)

    def reset(self):
        self.search_state.reset()

    def step(
        self,
        gimbal,
        detection,
        laser_point,
        current_angle,
        countermeasure_active,
        align_controller,
        search_controller,
    ):
        state = self.search_state.update(detection is not None)
        if detection is not None:
            search_controller.reset()
            world_angle = detection.debug.get("world_angle")
            if world_angle is not None:
                search_controller.remember_target(world_angle, current_angle)
            if laser_point is None:
                align_controller.reset()
                return state

            target_center = detection.center
            if not countermeasure_active:
                target_center = (int(target_center[0] - self.passive_offset_px), int(target_center[1]))
            align_controller.step(gimbal, laser_point.center, target_center, current_angle)
            return state

        align_controller.reset()
        if state == CountermeasureState.REACQUIRE:
            search_controller.step(gimbal, current_angle)
        return state
