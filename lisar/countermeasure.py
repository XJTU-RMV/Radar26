from __future__ import annotations

import argparse
import threading
import time

import cv2
import numpy as np
from loguru import logger

from lisar.common.gimbal_control import (
    ObservedAngleBounds,
    SweepSearchConfig,
    SweepSearchController,
)
from lisar.common.laser_reference import ObservedLaserDotReference, draw_laser_reference_roi
from lisar.common.search_state import CountermeasureSearchState, CountermeasureState
from lisar.common.tracking_behavior import (
    MODULE_HOLD_FRAMES,
    PASSIVE_MODULE_OFFSET_PX,
    MODULE_PITCH_MAX_DEG,
    MODULE_PITCH_MIN_DEG,
    MODULE_YAW_MAX_DEG,
    MODULE_YAW_MIN_DEG,
    TargetAngleStabilizer,
)
from lisar.difficulty.model_detector import Yolo26TargetDetector, load_stage3_detector_config
from lisar.easy.cv_detector import CvModuleTargetDetector, draw_cv_detection, erase_module_bars
from lisar.stage3 import CountermeasureDifficultyTracker
from lisar.utils.get_angle import cal_angle


SEARCH_YAW_SPEED_DEG_S = 2.5
SEARCH_PITCH_SPEED_DEG_S = 4.0
TARGET_PREDICT_FRAMES = 0.0
ANGLE_LATENCY_MS = 20.0
ANGLE_LATENCY_MODE = "timestamp"
COUNTERMEASURE_FRAME_GROUP = "lisar_countermeasure"


def load_countermeasure_start_seconds(config):
    values = config.get("countermeasure_start_seconds", None)
    if values is None:
        return ()
    if not isinstance(values, (list, tuple)) or len(values) != 5:
        raise ValueError("countermeasure_start_seconds must contain exactly 5 values")
    return tuple(float(value) for value in values)


class ScheduledCountermeasureGate:
    def __init__(
        self,
        initiative_counter,
        start_seconds,
        match_total_seconds,
        log_callback=None,
        dart_counter_signal_target=2,
        dart_counter_signal_hold_seconds=5.0,
    ):
        self.initiative_counter = bool(initiative_counter)
        self.start_seconds = tuple(start_seconds)
        self.match_total_seconds = float(match_total_seconds)
        self.log_callback = log_callback
        self.dart_counter_signal_target = int(dart_counter_signal_target)
        self.dart_counter_signal_hold_seconds = float(dart_counter_signal_hold_seconds)
        self.active_success_count = None
        self.dart_signal_since = None

    def reset(self):
        self.active_success_count = None
        self.dart_signal_since = None

    def is_active(self, game_start_flag, stage_remain_time, success_count, selected_target):
        if not self.initiative_counter:
            return True
        if not game_start_flag:
            self.reset()
            return False

        success_count = int(success_count)
        if self.active_success_count is not None:
            if success_count <= self.active_success_count:
                return True
            self._log(
                "反制状态",
                f"第 {self.active_success_count + 1}/5 次反制成功，success_count={success_count}，关闭本次反制",
            )
            self.active_success_count = None

        if success_count >= 5:
            self.dart_signal_since = None
            return False

        elapsed = self.match_total_seconds - float(stage_remain_time)
        trigger_time = self.start_seconds[success_count] if success_count < len(self.start_seconds) else None
        if trigger_time is not None and elapsed >= trigger_time:
            return self._start_attempt(
                success_count,
                f"比赛开局经过 {elapsed:.1f}s，达到第 {success_count + 1}/5 次反制计划时间 {trigger_time:.1f}s",
            )

        now = time.monotonic()
        if selected_target != self.dart_counter_signal_target:
            self.dart_signal_since = None
            return False

        if self.dart_signal_since is None:
            self.dart_signal_since = now
            return False

        if now - self.dart_signal_since >= self.dart_counter_signal_hold_seconds:
            return self._start_attempt(
                success_count,
                (
                    f"飞镖 selected_target={self.dart_counter_signal_target} "
                    f"持续 {self.dart_counter_signal_hold_seconds:.1f}s"
                ),
            )
        return False

    def _start_attempt(self, success_count, reason):
        self.active_success_count = int(success_count)
        self.dart_signal_since = None
        self._log("反制状态", f"{reason}，启动第 {self.active_success_count + 1}/5 次无人机反制")
        logger.warning("{}，启动第 {}/5 次无人机反制", reason, self.active_success_count + 1)
        return True

    def _log(self, message_type, content):
        if self.log_callback is not None:
            self.log_callback(message_type, content)


class UnifiedCountermeasureTracker:
    """Unified lisar countermeasure tracker selected by referee success count."""

    def __init__(
        self,
        config,
        referee,
        camera,
        visualize=True,
        module_hold_frames=MODULE_HOLD_FRAMES,
        target_predict_frames=TARGET_PREDICT_FRAMES,
        angle_latency_ms=ANGLE_LATENCY_MS,
        angle_latency_mode=ANGLE_LATENCY_MODE,
        event_callback=None,
    ):
        self.config = config
        self.referee = referee
        self.camera = camera
        self.show_debug_windows = bool(visualize)
        self.event_callback = event_callback
        self.target_predict_frames = float(target_predict_frames)
        self.angle_latency_s = float(angle_latency_ms) / 1000.0
        if self.angle_latency_s < 0.0:
            raise ValueError("angle_latency_ms must be non-negative")
        if angle_latency_mode not in ("timestamp", "fixed"):
            raise ValueError("angle_latency_mode must be 'timestamp' or 'fixed'")
        self.angle_latency_mode = angle_latency_mode
        self.debug_frame_lock = threading.Lock()
        self.latest_display = None
        self.last_frame_time = None
        self.last_angle_sample = None
        self.last_absolute_control = None
        self.last_target_angle_debug = None

        sub_cfg = config.sub_camera
        self.sub_cam_K = np.array(sub_cfg.K, dtype=np.float64).reshape(3, 3)
        self.sub_cam_dist = np.asarray(sub_cfg.dist_coeffs, dtype=np.float64).flatten()

        from driver.motor.scripts.controller import GimbalController

        gimbal_cfg = config.gimbal
        self.gimbal = GimbalController(port=gimbal_cfg.port, baudrate=gimbal_cfg.baudrate)

        self.cv_detector = CvModuleTargetDetector(self.sub_cam_K, self.sub_cam_dist)
        stage3_cfg = load_stage3_detector_config(config)
        self.yolo_detector = Yolo26TargetDetector(
            **stage3_cfg,
            camera_K=self.sub_cam_K,
            dist_coeffs=self.sub_cam_dist,
        )
        self.laser_reference = ObservedLaserDotReference(allow_prediction=True)
        self.difficulty_tracker = CountermeasureDifficultyTracker(camera, sub_cfg)

        self.cv_search_controller = SweepSearchController(
            SweepSearchConfig(
                yaw_min_deg=MODULE_YAW_MIN_DEG,
                yaw_max_deg=MODULE_YAW_MAX_DEG,
                pitch_min_deg=MODULE_PITCH_MIN_DEG,
                pitch_max_deg=MODULE_PITCH_MAX_DEG,
                yaw_speed_deg_s=SEARCH_YAW_SPEED_DEG_S,
                pitch_speed_deg_s=SEARCH_PITCH_SPEED_DEG_S,
            )
        )
        self.yolo_search_controller = SweepSearchController(
            SweepSearchConfig(
                yaw_min_deg=MODULE_YAW_MIN_DEG,
                yaw_max_deg=MODULE_YAW_MAX_DEG,
                pitch_min_deg=MODULE_PITCH_MIN_DEG,
                pitch_max_deg=MODULE_PITCH_MAX_DEG,
                yaw_speed_deg_s=SEARCH_YAW_SPEED_DEG_S,
                pitch_speed_deg_s=SEARCH_PITCH_SPEED_DEG_S,
            )
        )
        self.cv_target_stabilizer = TargetAngleStabilizer(
            self.sub_cam_K,
            self.sub_cam_dist,
            yaw_min_deg=MODULE_YAW_MIN_DEG,
            yaw_max_deg=MODULE_YAW_MAX_DEG,
            pitch_min_deg=MODULE_PITCH_MIN_DEG,
            pitch_max_deg=MODULE_PITCH_MAX_DEG,
        )
        self.yolo_target_stabilizer = TargetAngleStabilizer(
            self.sub_cam_K,
            self.sub_cam_dist,
            yaw_min_deg=MODULE_YAW_MIN_DEG,
            yaw_max_deg=MODULE_YAW_MAX_DEG,
            pitch_min_deg=MODULE_PITCH_MIN_DEG,
            pitch_max_deg=MODULE_PITCH_MAX_DEG,
        )
        self.search_state = CountermeasureSearchState(hold_after_seen_frames=module_hold_frames)
        self.observed_module_bounds = ObservedAngleBounds()
        self.observed_module_bounds_lock = threading.Lock()
        self.last_search_bounds_log_key = "unset"
        self.last_strategy = None
        self.last_difficulty = self.difficulty_tracker.difficulty
        self.last_success_count = self.difficulty_tracker.success_count

    def run(
        self,
        sub_frame_provider,
        countermeasure_active_provider=None,
        match_countdown_provider=None,
        stop_event=None,
        device_timestamp_provider=None,
        device_timestamp_increment=None,
    ):
        try:
            while not self._should_stop(stop_event):
                #########################################
                ##########       1. 取流           #######
                #########################################
                img_rgb, frame_metadata = self._read_frame(sub_frame_provider)
                if img_rgb is None:
                    time.sleep(0.005)
                    continue

                start = time.time()
                frame_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
                current_angle = self.gimbal.get_angle()
                if current_angle is None:
                    continue
                angle_time = time.monotonic()
                current_device_timestamp = None
                if device_timestamp_provider is not None:
                    current_device_timestamp = int(device_timestamp_provider())
                if frame_metadata is None:
                    if self.angle_latency_mode == "timestamp":
                        raise RuntimeError("timestamp latency mode requires frame metadata")
                    frame_metadata = {"time": angle_time, "timestamp_source": "monotonic"}
                frame_time = self._frame_time(frame_metadata)
                frame_dt = 0.0 if self.last_frame_time is None else float(frame_time) - self.last_frame_time
                self.last_frame_time = float(frame_time)
                frame_angle, angular_velocity, angle_latency_s, timestamp_source = self._compensated_frame_angle(
                    current_angle,
                    angle_time,
                    frame_metadata,
                    current_device_timestamp,
                    device_timestamp_increment,
                )
                
                #########################################
                ##########  2. 判断当前反制等级      #######
                #########################################

                difficulty = self._update_referee_difficulty()
                strategy = "yolo26" if difficulty == 3 else "cv"
                if strategy != self.last_strategy:
                    self._reset_tracking_state(reset_angle_timing=False)
                    self.last_strategy = strategy
                    logger.info("Lisar countermeasure strategy switched to {}", strategy)
                    self._emit_event("反制状态", f"反制策略切换为 {strategy}，当前难度={difficulty}")

                active = True if countermeasure_active_provider is None else bool(countermeasure_active_provider())
                detection = self._detect_target(strategy, frame_bgr, frame_angle)
                detection = self._target_stabilizer(strategy).update(detection, frame_angle)
                if detection is not None and self.difficulty_tracker.success_count < 3:
                    self._record_module_bounds(detection)
                laser_frame = erase_module_bars(frame_bgr, detection) if strategy == "cv" and detection is not None else frame_bgr
                laser_point = self.laser_reference.locate(laser_frame, {"target": detection})
                search_controller = self._search_controller(strategy)
                active_search_bounds = self._active_search_bounds()
                self._log_search_bounds_if_needed(active_search_bounds)
                search_controller.set_search_bounds(active_search_bounds)
                state = self._step_absolute_control(
                    strategy,
                    detection,
                    laser_point,
                    current_angle,
                    frame_angle,
                    angular_velocity,
                    angle_latency_s,
                    timestamp_source,
                    active,
                    frame_dt,
                )

                display = self._draw(
                    frame_bgr.copy(),
                    strategy,
                    difficulty,
                    active,
                    detection,
                    laser_point,
                    current_angle,
                    state,
                    match_countdown_provider,
                )
                self._draw_status(display, start)
                self._set_latest_ui_frames(display)

                if self.show_debug_windows:
                    cv2.imshow("Unified Lisar Countermeasure", cv2.resize(display, None, fx=0.4, fy=0.4))
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord("q"):
                        break
                    if key == ord("r"):
                        self.reset_countermeasure_state()
                        self.gimbal.set_angle(0.0, 0.0)
        finally:
            self.gimbal.set_angle(0.0, 0.0)
            time.sleep(0.1)
            self.gimbal.close()
            if self.show_debug_windows:
                cv2.destroyAllWindows()

    def reset_countermeasure_state(self):
        self.difficulty_tracker.reset()
        with self.observed_module_bounds_lock:
            self.observed_module_bounds.reset()
        self.last_search_bounds_log_key = "unset"
        self.cv_search_controller.set_search_bounds(None)
        self.yolo_search_controller.set_search_bounds(None)
        if self.referee is not None:
            self.difficulty_tracker.game_active = int(self.referee.game_progress) == 4
        self.last_difficulty = self.difficulty_tracker.difficulty
        self.last_success_count = self.difficulty_tracker.success_count
        self.last_strategy = None
        self._reset_tracking_state()

    def get_latest_ui_frames(self):
        with self.debug_frame_lock:
            display = None if self.latest_display is None else self.latest_display.copy()
        return display, None

    def _read_frame(self, frame_provider):
        frame_item = frame_provider()
        if frame_item is None:
            return None, None
        if isinstance(frame_item, tuple):
            if len(frame_item) != 2:
                raise RuntimeError(f"invalid frame provider tuple length: {len(frame_item)}")
            frame_rgb, frame_metadata = frame_item
            if isinstance(frame_metadata, dict):
                return frame_rgb, frame_metadata
            return frame_rgb, {"time": float(frame_metadata), "timestamp_source": "monotonic"}
        return frame_item, None

    def _frame_time(self, frame_metadata):
        if "time" not in frame_metadata:
            raise RuntimeError("frame metadata missing time")
        return float(frame_metadata["time"])

    def _compensated_frame_angle(
        self,
        current_angle,
        angle_time,
        frame_metadata,
        current_device_timestamp=None,
        device_timestamp_increment=None,
    ):
        current_yaw = float(current_angle[0])
        current_pitch = float(current_angle[1])
        if self.last_angle_sample is None:
            angular_velocity = (0.0, 0.0)
        else:
            last_time, last_yaw, last_pitch = self.last_angle_sample
            dt = float(angle_time) - last_time
            if dt <= 0.0:
                raise RuntimeError(f"invalid gimbal angle sample dt={dt}")
            angular_velocity = ((current_yaw - last_yaw) / dt, (current_pitch - last_pitch) / dt)
        self.last_angle_sample = (float(angle_time), current_yaw, current_pitch)
        angle_latency_s = self.angle_latency_s
        timestamp_source = "fixed"
        if self.angle_latency_mode == "timestamp":
            timestamp_source = frame_metadata.get("timestamp_source")
            if timestamp_source == "device":
                if current_device_timestamp is None:
                    raise RuntimeError("device timestamp compensation requires current device timestamp")
                frame_device_timestamp = int(frame_metadata["device_timestamp"])
                increment = float(device_timestamp_increment or frame_metadata["device_timestamp_increment"])
                angle_latency_s = (current_device_timestamp - frame_device_timestamp) / increment
            elif timestamp_source == "monotonic":
                angle_latency_s = float(angle_time) - self._frame_time(frame_metadata)
            else:
                raise RuntimeError(f"unsupported frame timestamp source: {timestamp_source}")
            if angle_latency_s < 0.0:
                raise RuntimeError(f"frame timestamp is newer than gimbal angle sample: latency={angle_latency_s}")
        frame_angle = (
            current_yaw - angular_velocity[0] * angle_latency_s,
            current_pitch - angular_velocity[1] * angle_latency_s,
        )
        return frame_angle, angular_velocity, angle_latency_s, timestamp_source

    def _step_absolute_control(
        self,
        strategy,
        detection,
        laser_point,
        current_angle,
        frame_angle,
        angular_velocity,
        angle_latency_s,
        timestamp_source,
        countermeasure_active,
        frame_dt,
    ):
        search_controller = self._search_controller(strategy)
        state = self.search_state.update(detection is not None)
        if detection is None:
            self.last_absolute_control = None
            if state == CountermeasureState.REACQUIRE:
                search_controller.step(self.gimbal, current_angle)
            return state

        search_controller.reset()
        target_abs = self._target_absolute_angle(detection, frame_angle)
        if target_abs is not None:
            search_controller.remember_target(target_abs, current_angle)
            target_pred_abs = self._predict_target_absolute_angle(strategy, target_abs, frame_dt)
            self.last_target_angle_debug = {"target_abs": target_abs, "target_pred_abs": target_pred_abs}
        else:
            target_pred_abs = None
            self.last_target_angle_debug = None
        if target_abs is None or laser_point is None:
            self.last_absolute_control = None
            return state

        target_rel = self._pixel_to_relative_angle(detection.center)
        laser_rel = self._pixel_to_relative_angle(laser_point.center)
        laser_abs = (float(frame_angle[0]) + laser_rel[0], float(frame_angle[1]) + laser_rel[1])

        if not countermeasure_active:
            offset_center = (int(detection.center[0] - PASSIVE_MODULE_OFFSET_PX), int(detection.center[1]))
            offset_rel = self._pixel_to_relative_angle(offset_center)
            target_pred_abs = (
                target_pred_abs[0] + offset_rel[0] - target_rel[0],
                target_pred_abs[1] + offset_rel[1] - target_rel[1],
            )

        angle_error = (target_pred_abs[0] - laser_abs[0], target_pred_abs[1] - laser_abs[1])
        command = (
            float(np.clip(target_pred_abs[0] - laser_rel[0], MODULE_YAW_MIN_DEG, MODULE_YAW_MAX_DEG)),
            float(np.clip(target_pred_abs[1] - laser_rel[1], MODULE_PITCH_MIN_DEG, MODULE_PITCH_MAX_DEG)),
        )
        self.gimbal.set_angle(command[0], command[1])
        self.last_absolute_control = {
            "active": bool(countermeasure_active),
            "target_rel": target_rel,
            "target_abs": target_abs,
            "target_pred_abs": target_pred_abs,
            "laser_rel": laser_rel,
            "laser_abs": laser_abs,
            "current_angle": (float(current_angle[0]), float(current_angle[1])),
            "frame_angle": (float(frame_angle[0]), float(frame_angle[1])),
            "angular_velocity": angular_velocity,
            "angle_latency_s": float(angle_latency_s),
            "angle_latency_mode": self.angle_latency_mode,
            "timestamp_source": timestamp_source,
            "angle_error": angle_error,
            "command": command,
            "predict_dt": max(float(frame_dt), 0.0) * self.target_predict_frames,
        }
        return state

    def _pixel_to_relative_angle(self, center):
        return tuple(
            float(value)
            for value in cal_angle(
                self.sub_cam_K,
                self.sub_cam_dist,
                float(center[0]),
                float(center[1]),
                verbose=False,
            )
        )

    def _target_absolute_angle(self, detection, current_angle):
        world_angle = detection.debug.get("filtered_world_angle")
        if world_angle is None:
            world_angle = detection.debug.get("world_angle")
        if world_angle is not None:
            return float(world_angle[0]), float(world_angle[1])

        target_rel = self._pixel_to_relative_angle(detection.center)
        return float(current_angle[0]) + target_rel[0], float(current_angle[1]) + target_rel[1]

    def _predict_target_absolute_angle(self, strategy, target_abs, frame_dt):
        predict_dt = max(float(frame_dt), 0.0) * self.target_predict_frames
        target_filter = self._target_stabilizer(strategy).filter
        if predict_dt <= 0.0 or not target_filter.initialized:
            return target_abs
        return (
            float(target_filter.x[0] + target_filter.x[2] * predict_dt),
            float(target_filter.x[1] + target_filter.x[3] * predict_dt),
        )

    def _update_referee_difficulty(self):
        if self.referee is None:
            return self.difficulty_tracker.difficulty

        radar_mark = self.referee.radar_mark_progress_msg
        countered = bool(getattr(radar_mark, "enemy_aircraft_countered", 0))
        difficulty = self.difficulty_tracker.update(self.referee.game_progress, countered)
        if self.difficulty_tracker.success_count != self.last_success_count:
            logger.info(
                "Lisar official countermeasure success edge: {} -> {}",
                self.last_success_count,
                self.difficulty_tracker.success_count,
            )
            self._emit_event(
                "反制状态",
                f"裁判系统反制成功次数 {self.last_success_count} -> {self.difficulty_tracker.success_count}",
            )
            self.last_success_count = self.difficulty_tracker.success_count
        if difficulty != self.last_difficulty:
            logger.info(
                "Lisar countermeasure difficulty changed: {} -> {}, success_count={}",
                self.last_difficulty,
                difficulty,
                self.difficulty_tracker.success_count,
            )
            self._emit_event(
                "反制状态",
                f"反制难度 {self.last_difficulty} -> {difficulty}，success_count={self.difficulty_tracker.success_count}",
            )
            self.last_difficulty = difficulty
        return difficulty

    def _detect_target(self, strategy, frame_bgr, current_angle):
        if strategy == "yolo26":
            return self.yolo_detector.detect(frame_bgr, {"current_angle": current_angle})
        return self.cv_detector.detect(frame_bgr, {"current_angle": current_angle})

    def _search_controller(self, strategy):
        if strategy == "yolo26":
            return self.yolo_search_controller
        return self.cv_search_controller

    def _target_stabilizer(self, strategy):
        if strategy == "yolo26":
            return self.yolo_target_stabilizer
        return self.cv_target_stabilizer

    def _record_module_bounds(self, detection):
        world_angle = detection.debug.get("world_angle")
        if world_angle is not None:
            with self.observed_module_bounds_lock:
                self.observed_module_bounds.update(world_angle)

    def _active_search_bounds(self):
        if self.difficulty_tracker.success_count < 3:
            return None
        with self.observed_module_bounds_lock:
            return self.observed_module_bounds.search_bounds()

    def _observed_bounds_snapshot(self):
        with self.observed_module_bounds_lock:
            snapshot = self.observed_module_bounds.snapshot()
            search_bounds = self.observed_module_bounds.search_bounds()
        snapshot["search_bounds"] = search_bounds
        return snapshot

    def _format_observed_bounds(self, snapshot):
        count = int(snapshot["count"])
        if count == 0:
            return "本局未记录到有效检测模块世界角，搜索范围=全范围保底"
        text = (
            f"本局检测模块观测={count}次 "
            f"yaw=[{snapshot['yaw_min_deg']:.2f}, {snapshot['yaw_max_deg']:.2f}] "
            f"pitch=[{snapshot['pitch_min_deg']:.2f}, {snapshot['pitch_max_deg']:.2f}]"
        )
        bounds = snapshot["search_bounds"]
        if bounds is None:
            return text + "；未形成有效窄搜索范围，搜索范围=全范围保底"
        return (
            text
            + f"；4/5阶段搜索范围 yaw=[{bounds.yaw_min_deg:.2f}, {bounds.yaw_max_deg:.2f}] "
            + f"pitch=[{bounds.pitch_min_deg:.2f}, {bounds.pitch_max_deg:.2f}]"
        )

    def get_observed_module_bounds_summary(self):
        return self._format_observed_bounds(self._observed_bounds_snapshot())

    def _log_search_bounds_if_needed(self, bounds):
        if self.difficulty_tracker.success_count < 3:
            return
        key = None if bounds is None else (
            round(bounds.yaw_min_deg, 4),
            round(bounds.yaw_max_deg, 4),
            round(bounds.pitch_min_deg, 4),
            round(bounds.pitch_max_deg, 4),
        )
        if key == self.last_search_bounds_log_key:
            return
        self.last_search_bounds_log_key = key
        self._emit_event("反制搜索范围", self.get_observed_module_bounds_summary())

    def _reset_tracking_state(self, reset_angle_timing=True):
        self.search_state.reset()
        self.cv_target_stabilizer.reset()
        self.yolo_target_stabilizer.reset()
        self._reset_control_state()
        if reset_angle_timing:
            self.last_frame_time = None
            self.last_angle_sample = None
        self.last_absolute_control = None
        self.last_target_angle_debug = None

    def _reset_control_state(self):
        self.cv_search_controller.reset(reset_target_memory=True)
        self.yolo_search_controller.reset(reset_target_memory=True)

    def _emit_event(self, message_type, content):
        if self.event_callback is not None:
            self.event_callback(message_type, content)

    def _draw(self, display, strategy, difficulty, active, detection, laser_point, current_angle, state, match_countdown_provider):
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 2.0
        thickness = 3
        label_font_scale = 0.75
        label_thickness = 2
        margin = 20
        line_gap = 16
        (_, text_h), baseline = cv2.getTextSize("Ag", font, font_scale, thickness)
        line_step = text_h + baseline + line_gap
        warning_y = margin + text_h + line_step * 3

        if strategy == "cv":
            draw_cv_detection(display, detection, font_scale=label_font_scale, thickness=label_thickness)
        elif detection is not None:
            for cls, bbox, conf in detection.debug["detections"]:
                x1, y1, x2, y2 = map(int, bbox)
                cv2.rectangle(display, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(
                    display,
                    f"stage3_target cls={int(cls)} conf={float(conf):.2f}",
                    (x1, max(text_h + margin, y1 - 8)),
                    font,
                    font_scale,
                    (0, 255, 0),
                    thickness,
                )
            cv2.circle(display, detection.center, 8, (0, 255, 0), 2)

        draw_laser_reference_roi(display)
        if laser_point is not None:
            cv2.circle(display, laser_point.center, 8, (0, 0, 255), 2)
            cv2.putText(
                display,
                f"laser=({laser_point.center[0]}, {laser_point.center[1]})",
                (laser_point.center[0] + 10, laser_point.center[1] + 20),
                font,
                label_font_scale,
                (0, 0, 255),
                thickness,
            )

        if detection is not None and laser_point is not None:
            cv2.line(display, laser_point.center, detection.center, (0, 255, 255), 2)
        elif detection is None:
            cv2.putText(display, "TARGET NOT FOUND", (margin, warning_y), font, font_scale, (0, 165, 255), thickness)
        elif laser_point is None:
            cv2.putText(display, "LASER DOT NOT FOUND", (margin, warning_y), font, font_scale, (0, 165, 255), thickness)

        if detection is not None and self.last_target_angle_debug is not None:
            target_abs = self.last_target_angle_debug["target_abs"]
            target_pred_abs = self.last_target_angle_debug["target_pred_abs"]
            label_text = f"abs=({target_abs[0]:.2f}, {target_abs[1]:.2f}) pred=({target_pred_abs[0]:.2f}, {target_pred_abs[1]:.2f})"
            (label_w, _), _ = cv2.getTextSize(label_text, font, label_font_scale, label_thickness)
            label_x = min(max(detection.center[0] + 12, margin), max(margin, display.shape[1] - label_w - margin))
            label_y = min(max(detection.center[1] - 48, margin + 40), display.shape[0] - 24)
            cv2.putText(display, label_text, (label_x, label_y), font, label_font_scale, (0, 0, 255), label_thickness)

        countdown = None if match_countdown_provider is None else match_countdown_provider()
        yaw, pitch = float(current_angle[0]), float(current_angle[1])
        lines = [
            f"difficulty={difficulty} success={self.difficulty_tracker.success_count}",
            f"active={active} state={state.value} lost={self.search_state.lost_frames}",
            f"yaw={yaw:.2f} pitch={pitch:.2f} remain={countdown}",
        ]
        if self.last_absolute_control is not None:
            control = self.last_absolute_control
            target_abs = control["target_abs"]
            target_pred_abs = control["target_pred_abs"]
            laser_abs = control["laser_abs"]
            frame_angle = control["frame_angle"]
            angular_velocity = control["angular_velocity"]
            angle_error = control["angle_error"]
            command = control["command"]
            lines.extend(
                [
                    f"frame_angle=({frame_angle[0]:.2f}, {frame_angle[1]:.2f}) vel=({angular_velocity[0]:.2f}, {angular_velocity[1]:.2f})",
                    f"target_abs=({target_abs[0]:.2f}, {target_abs[1]:.2f}) pred=({target_pred_abs[0]:.2f}, {target_pred_abs[1]:.2f})",
                    f"laser_abs=({laser_abs[0]:.2f}, {laser_abs[1]:.2f}) err=({angle_error[0]:.2f}, {angle_error[1]:.2f})",
                    f"cmd=({command[0]:.2f}, {command[1]:.2f}) latency[{control['timestamp_source']}]={control['angle_latency_s'] * 1000.0:.1f}ms predict_dt={control['predict_dt']:.3f}s",
                ]
            )
        y = margin + text_h
        for text in lines:
            cv2.putText(display, text, (margin, y), font, font_scale, (0, 255, 255), thickness)
            y += line_step
        return display

    def _draw_status(self, display, start):
        fps = 1.0 / max(time.time() - start, 1e-6)
        cv2.putText(display, f"FPS={fps:.1f}", (2820, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 255), 3)

    def _set_latest_ui_frames(self, display):
        with self.debug_frame_lock:
            self.latest_display = display.copy()

    def _should_stop(self, stop_event):
        return stop_event is not None and stop_event.is_set()


def _build_arg_parser():
    parser = argparse.ArgumentParser(description="Run adaptive lisar countermeasure with referee-system difficulty tracking.")
    parser.add_argument("--config", default="config/params.yaml", type=str, help="runtime config yaml")
    parser.add_argument("--faction", default=None, choices=["red", "blue"], help="override team faction")
    parser.add_argument("--referee-port", default=None, type=str, help="override referee serial port")
    parser.add_argument("--referee-baudrate", default=None, type=int, help="override referee serial baudrate")
    parser.add_argument(
        "--visualize",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="show countermeasure debug window",
    )
    parser.add_argument(
        "--initiative-counter",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="override initiative_counter from config",
    )
    parser.add_argument(
        "--countermeasure-start-seconds",
        default=None,
        type=str,
        help="override five countermeasure start times after match start, comma-separated",
    )
    parser.add_argument("--target-predict-frames", type=float, default=TARGET_PREDICT_FRAMES)
    parser.add_argument("--angle-latency-mode", choices=["timestamp", "fixed"], default=ANGLE_LATENCY_MODE)
    parser.add_argument("--angle-latency-ms", type=float, default=ANGLE_LATENCY_MS)
    return parser


def _apply_cli_overrides(config, args):
    if args.faction is not None:
        config.faction = args.faction
    if args.initiative_counter is not None:
        config.initiative_counter = args.initiative_counter
    if args.countermeasure_start_seconds is not None:
        config.countermeasure_start_seconds = [
            float(value.strip()) for value in args.countermeasure_start_seconds.split(",") if value.strip()
        ]

    referee_cfg = config.get("referee", {})
    if args.referee_port is not None:
        referee_cfg.port = args.referee_port
    if args.referee_baudrate is not None:
        referee_cfg.baudrate = args.referee_baudrate


def _build_sub_frame_provider(sub_camera):
    def sub_frame_provider():
        frame_rgb, _, metadata = sub_camera.get_image_latest_with_metadata(COUNTERMEASURE_FRAME_GROUP, timeout=0.02)
        if frame_rgb is None:
            return None
        if metadata is None or metadata.get("device_timestamp") is None:
            raise RuntimeError("sub camera frame device timestamp is missing")
        timestamp_increment = float(metadata["device_timestamp_increment"])
        frame_device_timestamp = int(metadata["device_timestamp"])
        return frame_rgb, {
            "time": frame_device_timestamp / timestamp_increment,
            "timestamp_source": "device",
            "device_timestamp": frame_device_timestamp,
            "device_timestamp_increment": timestamp_increment,
            "host_timestamp": metadata.get("host_timestamp"),
            "wall_timestamp": metadata.get("wall_timestamp"),
        }

    return sub_frame_provider


def _build_match_countdown_provider(referee):
    def match_countdown_provider():
        if not referee.game_start_flag:
            return None
        return referee.stage_remain_time

    return match_countdown_provider


def _build_countermeasure_active_provider(config, referee, success_count_provider):
    gate = ScheduledCountermeasureGate(
        initiative_counter=bool(config.get("initiative_counter", False)),
        start_seconds=load_countermeasure_start_seconds(config),
        match_total_seconds=float(config.get("match_total_seconds", 420.0)),
        log_callback=lambda message_type, content: logger.info("[{}] {}", message_type, content),
    )

    def countermeasure_active_provider():
        return gate.is_active(
            game_start_flag=bool(referee.game_start_flag),
            stage_remain_time=referee.stage_remain_time,
            success_count=success_count_provider(),
            selected_target=referee.target,
        )

    return countermeasure_active_provider


def _log_countermeasure_event(message_type, content):
    logger.info("[{}] {}", message_type, content)


def main(argv=None):
    from driver.hik_camera.hik import SimpleHikCamera
    from driver.referee.referee_comm import RefereeCommManager
    from utils.config import load_cfg_from_cfg_file

    args = _build_arg_parser().parse_args(argv)
    config = load_cfg_from_cfg_file(args.config)
    _apply_cli_overrides(config, args)

    sub_camera = None
    referee = None
    referee_started = False
    try:
        sub_camera = SimpleHikCamera(config.sub_camera, camera_role="sub")
        sub_camera.register_group(COUNTERMEASURE_FRAME_GROUP)
        sub_camera.start_streaming()

        referee_cfg = config.get("referee", {})
        referee = RefereeCommManager(
            port=referee_cfg.get("port"),
            baudrate=referee_cfg.get("baudrate", 115200),
            args=config,
        )
        referee_started = referee.start()
        if not referee_started:
            raise RuntimeError("裁判系统通信线程启动失败")

        tracker = UnifiedCountermeasureTracker(
            config=config,
            referee=referee,
            camera=sub_camera,
            visualize=args.visualize,
            target_predict_frames=args.target_predict_frames,
            angle_latency_ms=args.angle_latency_ms,
            angle_latency_mode=args.angle_latency_mode,
            event_callback=_log_countermeasure_event,
        )
        tracker.run(
            sub_frame_provider=_build_sub_frame_provider(sub_camera),
            device_timestamp_provider=sub_camera.get_device_timestamp,
            countermeasure_active_provider=_build_countermeasure_active_provider(
                config,
                referee,
                lambda: tracker.difficulty_tracker.success_count,
            ),
            match_countdown_provider=_build_match_countdown_provider(referee),
        )
        return 0
    finally:
        if referee_started:
            referee.close()
        if sub_camera is not None:
            sub_camera.close()


if __name__ == "__main__":
    raise SystemExit(main())
