from __future__ import annotations

import argparse
import os
import sys
import threading
import time
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from lisar.common.frame_source import (
    build_sub_camera_frame_provider_with_timestamp,
    build_video_frame_provider_with_timestamp,
)
from lisar.common.gimbal_control import (
    SweepSearchConfig,
    SweepSearchController,
)
from lisar.common.laser_reference import (
    CalibratedLaserReference,
    ObservedLaserDotReference,
    draw_laser_reference_roi,
)
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
from lisar.easy.cv_detector import CvModuleTargetDetector, draw_cv_detection, erase_module_bars
from lisar.utils.get_angle import cal_angle
from utils.config import load_cfg_from_cfg_file


SEARCH_YAW_SPEED_DEG_S = 2.0
SEARCH_PITCH_SPEED_DEG_S = 2.0
TARGET_PREDICT_FRAMES = 0.0
ANGLE_LATENCY_MS = 20.0
ANGLE_LATENCY_MODE = "timestamp"


class CvCountermeasureTracker:
    def __init__(
        self,
        config,
        laser_reference,
        visualize=True,
        save_path=None,
        save_fps=20.0,
        save_visualize=False,
        module_hold_frames=MODULE_HOLD_FRAMES,
        target_predict_frames=TARGET_PREDICT_FRAMES,
        angle_latency_ms=ANGLE_LATENCY_MS,
        angle_latency_mode=ANGLE_LATENCY_MODE,
    ):
        self.config = config
        self.show_debug_windows = bool(visualize)
        self.save_path = save_path
        self.save_fps = float(save_fps)
        self.save_visualize = bool(save_visualize)
        self.target_predict_frames = float(target_predict_frames)
        self.angle_latency_s = float(angle_latency_ms) / 1000.0
        if self.angle_latency_s < 0.0:
            raise ValueError("angle_latency_ms must be non-negative")
        if angle_latency_mode not in ("timestamp", "fixed"):
            raise ValueError("angle_latency_mode must be 'timestamp' or 'fixed'")
        self.angle_latency_mode = angle_latency_mode
        self.video_writer = None
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
        self.detector = CvModuleTargetDetector(self.sub_cam_K, self.sub_cam_dist)
        self.laser_reference = laser_reference
        self.search_controller = SweepSearchController(
            SweepSearchConfig(
                yaw_min_deg=MODULE_YAW_MIN_DEG,
                yaw_max_deg=MODULE_YAW_MAX_DEG,
                pitch_min_deg=MODULE_PITCH_MIN_DEG,
                pitch_max_deg=MODULE_PITCH_MAX_DEG,
                yaw_speed_deg_s=SEARCH_YAW_SPEED_DEG_S,
                pitch_speed_deg_s=SEARCH_PITCH_SPEED_DEG_S,
            )
        )
        self.target_stabilizer = TargetAngleStabilizer(
            self.sub_cam_K,
            self.sub_cam_dist,
            yaw_min_deg=MODULE_YAW_MIN_DEG,
            yaw_max_deg=MODULE_YAW_MAX_DEG,
            pitch_min_deg=MODULE_PITCH_MIN_DEG,
            pitch_max_deg=MODULE_PITCH_MAX_DEG,
        )
        self.search_state = CountermeasureSearchState(hold_after_seen_frames=module_hold_frames)

    def run(
        self,
        frame_provider,
        countermeasure_active_provider=None,
        stop_event=None,
        stop_on_empty_frame=False,
        device_timestamp_provider=None,
        device_timestamp_increment=None,
    ):
        try:
            while not self._should_stop(stop_event):
                frame_bgr, frame_metadata = self._read_frame(frame_provider) # 取流时刻
                if frame_bgr is None:
                    if stop_on_empty_frame:
                        break
                    time.sleep(0.005)
                    continue

                start = time.time()
                current_angle = self.gimbal.get_angle() # 取角度时刻
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

                detection = self.detector.detect(frame_bgr, {"current_angle": frame_angle}) # 检测激光检测模块
                detection = self.target_stabilizer.update(detection, frame_angle) # 滤波
                laser_frame = erase_module_bars(frame_bgr, detection) if detection is not None else frame_bgr
                laser_point = self.laser_reference.locate(laser_frame, {"target": detection})
                countermeasure_active = (
                    True
                    if countermeasure_active_provider is None
                    else bool(countermeasure_active_provider())
                )
                state = self._step_absolute_control(
                    detection,
                    laser_point,
                    current_angle,
                    frame_angle,
                    angular_velocity,
                    angle_latency_s,
                    timestamp_source,
                    countermeasure_active,
                    frame_dt,
                )

                display = self._draw(frame_bgr.copy(), detection, laser_point, current_angle, state)
                fps = 1.0 / max(time.time() - start, 1e-6)
                self._draw_status(display, fps)
                self._set_latest_ui_frames(display)
                self._write_frame(display if self.save_visualize else frame_bgr)

                if self.show_debug_windows:
                    cv2.imshow("Easy CV Countermeasure", cv2.resize(display, None, fx=0.4, fy=0.4))
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord("q"):
                        break
                    if key == ord("r"):
                        self.reset()
                        self.gimbal.set_angle(0.0, 0.0)
        finally:
            self.gimbal.set_angle(0.0, 0.0)
            time.sleep(0.1)
            self.gimbal.close()
            if self.video_writer is not None:
                self.video_writer.release()
                print(f"[INFO] CV反制视频已保存: {self.save_path}")
            if self.show_debug_windows:
                cv2.destroyAllWindows()

    def reset(self):
        self.search_controller.reset(reset_target_memory=True)
        self.target_stabilizer.reset()
        self.search_state.reset()
        self.last_frame_time = None
        self.last_angle_sample = None
        self.last_absolute_control = None
        self.last_target_angle_debug = None

    def _read_frame(self, frame_provider):
        frame_item = frame_provider()
        if frame_item is None:
            return None, None
        if isinstance(frame_item, tuple):
            if len(frame_item) != 2:
                raise RuntimeError(f"invalid frame provider tuple length: {len(frame_item)}")
            frame_bgr, frame_metadata = frame_item
            if isinstance(frame_metadata, dict):
                return frame_bgr, frame_metadata
            return frame_bgr, {"time": float(frame_metadata), "timestamp_source": "monotonic"}
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
        state = self.search_state.update(detection is not None)
        if detection is None:
            self.last_absolute_control = None
            if state == CountermeasureState.REACQUIRE:
                self.search_controller.step(self.gimbal, current_angle)
            return state

        self.search_controller.reset()
        target_abs = self._target_absolute_angle(detection, frame_angle)
        if target_abs is not None:
            self.search_controller.remember_target(target_abs, current_angle)
            target_pred_abs = self._predict_target_absolute_angle(target_abs, frame_dt)
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

    def _predict_target_absolute_angle(self, target_abs, frame_dt):
        predict_dt = max(float(frame_dt), 0.0) * self.target_predict_frames
        target_filter = self.target_stabilizer.filter
        if predict_dt <= 0.0 or not target_filter.initialized:
            return target_abs
        return (
            float(target_filter.x[0] + target_filter.x[2] * predict_dt),
            float(target_filter.x[1] + target_filter.x[3] * predict_dt),
        )

    def get_latest_ui_frames(self):
        with self.debug_frame_lock:
            display = None if self.latest_display is None else self.latest_display.copy()
        return display, None

    def _draw(self, display, detection, laser_point, current_angle, state):
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 2.0
        thickness = 3
        label_font_scale = 0.75
        label_thickness = 2
        margin = 20
        line_gap = 16
        (_, text_h), baseline = cv2.getTextSize("Ag", font, font_scale, thickness)
        line_step = text_h + baseline + line_gap
        warning_y = margin + text_h + line_step * 2

        draw_cv_detection(display, detection, font_scale=label_font_scale, thickness=label_thickness)
        draw_laser_reference_roi(display)

        if laser_point is not None:
            color = (0, 255, 255) if laser_point.predicted else (0, 0, 255)
            cv2.circle(display, laser_point.center, 8, color, 2)
            cv2.putText(
                display,
                f"{laser_point.source}=({laser_point.center[0]}, {laser_point.center[1]})",
                (laser_point.center[0] + 10, laser_point.center[1] + 20),
                font,
                label_font_scale,
                color,
                label_thickness,
            )

        if detection is not None and laser_point is not None:
            cv2.line(display, laser_point.center, detection.center, (0, 255, 255), 2)
        elif detection is None:
            cv2.putText(display, "CV TARGET NOT FOUND", (margin, warning_y), font, font_scale, (0, 165, 255), thickness)
        elif laser_point is None:
            cv2.putText(display, "LASER DOT NOT FOUND", (margin, warning_y), font, font_scale, (0, 165, 255), thickness)

        if detection is not None and self.last_target_angle_debug is not None:
            target_abs = self.last_target_angle_debug["target_abs"]
            target_pred_abs = self.last_target_angle_debug["target_pred_abs"]
            label_text = f"abs=({target_abs[0]:.2f}, {target_abs[1]:.2f}) pred=({target_pred_abs[0]:.2f}, {target_pred_abs[1]:.2f})"
            (label_w, _), _ = cv2.getTextSize(label_text, font, label_font_scale, label_thickness)
            label_x = min(max(detection.center[0] + 12, margin), max(margin, display.shape[1] - label_w - margin))
            label_y = min(max(detection.center[1] - 48, margin + 40), display.shape[0] - 24)
            cv2.putText(
                display,
                label_text,
                (label_x, label_y),
                font,
                label_font_scale,
                (0, 0, 255),
                label_thickness,
            )

        yaw, pitch = float(current_angle[0]), float(current_angle[1])
        lines = [
            f"state={state.value} lost={self.search_state.lost_frames}",
            f"yaw={yaw:.2f} pitch={pitch:.2f}",
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

    def _draw_status(self, display, fps):
        cv2.putText(display, f"FPS={fps:.1f}", (2820, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 255), 3)

    def _write_frame(self, frame):
        if self.save_path is None:
            return
        if self.video_writer is None:
            height, width = frame.shape[:2]
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            self.video_writer = cv2.VideoWriter(self.save_path, fourcc, self.save_fps, (width, height))
            if not self.video_writer.isOpened():
                self.video_writer.release()
                self.video_writer = None
                raise RuntimeError(f"无法创建视频文件: {self.save_path}")
            print(f"[INFO] 开始保存CV反制视频: {self.save_path}")
        self.video_writer.write(frame)

    def _set_latest_ui_frames(self, display):
        with self.debug_frame_lock:
            self.latest_display = display.copy()

    def _should_stop(self, stop_event):
        return stop_event is not None and stop_event.is_set()


def _build_laser_reference(args, config):
    if args.laser_reference == "observed":
        return ObservedLaserDotReference(allow_prediction=True)

    center = None
    if args.calibrated_x is not None and args.calibrated_y is not None:
        center = (int(args.calibrated_x), int(args.calibrated_y))
    return CalibratedLaserReference(center=center, config=config)


def parse_args():
    parser = argparse.ArgumentParser(description="easy: 基于CV检测的激光反制测试")
    parser.add_argument("--source", choices=["sub", "video"], default="sub")
    parser.add_argument("--video-path", default="demo/demo.mp4")
    parser.add_argument("--config", default="config/params.yaml")
    parser.add_argument("--laser-reference", choices=["observed", "calibrated"], default="observed")
    parser.add_argument("--calibrated-x", type=int, default=None)
    parser.add_argument("--calibrated-y", type=int, default=None)
    parser.add_argument(
        "--module-hold-frames",
        "--lost-reacquire-frames",
        dest="module_hold_frames",
        type=int,
        default=MODULE_HOLD_FRAMES,
    )
    parser.add_argument("--no-show", action="store_true")
    parser.add_argument("--save", action="store_true")
    parser.add_argument("--save-visualize", action="store_true")
    parser.add_argument("--save-path", default=None)
    parser.add_argument("--target-predict-frames", type=float, default=TARGET_PREDICT_FRAMES)
    parser.add_argument("--angle-latency-mode", choices=["timestamp", "fixed"], default=ANGLE_LATENCY_MODE)
    parser.add_argument("--angle-latency-ms", type=float, default=ANGLE_LATENCY_MS)
    return parser.parse_args()


def main():
    args = parse_args()
    config = load_cfg_from_cfg_file(args.config)

    source_handle = None
    device_timestamp_provider = None
    device_timestamp_increment = None
    if args.source == "video":
        if args.video_path is None:
            raise ValueError("--video-path is required when --source video")
        frame_provider, source_handle, run_fps = build_video_frame_provider_with_timestamp(args.video_path)
    else:
        frame_provider, source_handle, run_fps = build_sub_camera_frame_provider_with_timestamp(config, "easy_cv_countermeasure")
        device_timestamp_provider = source_handle.get_device_timestamp

    save_path = args.save_path
    if args.save and save_path is None:
        save_root = config.sub_camera.recording_save_root_dir
        os.makedirs(save_root, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = os.path.join(save_root, f"easy_cv_countermeasure_{timestamp}.mp4")

    tracker = CvCountermeasureTracker(
        config=config,
        laser_reference=_build_laser_reference(args, config),
        visualize=not args.no_show,
        save_path=save_path if args.save else None,
        save_fps=run_fps,
        save_visualize=args.save_visualize,
        module_hold_frames=args.module_hold_frames,
        target_predict_frames=args.target_predict_frames,
        angle_latency_ms=args.angle_latency_ms,
        angle_latency_mode=args.angle_latency_mode,
    )

    try:
        tracker.run(
            frame_provider,
            stop_on_empty_frame=args.source == "video",
            device_timestamp_provider=device_timestamp_provider,
            device_timestamp_increment=device_timestamp_increment,
        )
    finally:
        if args.source == "video" and source_handle is not None:
            source_handle.release()
        if args.source == "sub" and source_handle is not None:
            source_handle.stop_streaming()
            source_handle.close()


if __name__ == "__main__":
    main()
