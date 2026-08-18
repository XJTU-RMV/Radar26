import argparse
import copy
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

from driver.hik_camera.hik import SimpleHikCamera
from driver.motor.scripts.controller import GimbalController
from lisar.detect_lisar_dot import LisarDotDetector, X_MIN, X_MAX, Y_MIN, Y_MAX
from model.yolo26 import Stage3Detector
from utils.config import load_cfg_from_cfg_file


MAX_STEP_DEG = 0.5
ALIGN_KP_YAW = 0.8
ALIGN_KP_PITCH = 1.0
ALIGN_DEADBAND_PX = 0
YAW_MIN_DEG = -90.0
YAW_MAX_DEG = 90.0
PITCH_MIN_DEG = -90.0
PITCH_MAX_DEG = 90.0


class Stage3CountermeasureTracker:
    def __init__(
        self,
        config,
        detector,
        visualize=True,
        save_path=None,
        save_fps=20.0,
        save_visualize=False,
    ):
        self.config = config
        self.detector = detector
        self.show_debug_windows = bool(visualize)
        self.save_path = save_path
        self.save_fps = float(save_fps)
        self.save_visualize = bool(save_visualize)
        self.video_writer = None
        self.debug_frame_lock = threading.Lock()
        self.latest_display = None

        sub_cfg = config.sub_camera
        self.sub_cam_K = np.array(sub_cfg.K, dtype=np.float64).reshape(3, 3)
        self.sub_cam_dist = np.asarray(sub_cfg.dist_coeffs, dtype=np.float64).flatten()

        gimbal_cfg = config.gimbal
        self.gimbal = GimbalController(port=gimbal_cfg.port, baudrate=gimbal_cfg.baudrate)
        self.laser_detector = LisarDotDetector()

        self.last_align_error = None
        self.last_align_time = None
        self.lost_target_frames = 0
        self.lost_laser_frames = 0

    def run(self, frame_provider, stage3_active_provider=None, stop_event=None, stop_on_empty_frame=False):
        try:
            while not self._should_stop(stop_event):
                packet = frame_provider()
                if packet is None:
                    if stop_on_empty_frame:
                        break
                    time.sleep(0.005)
                    continue

                if isinstance(packet, tuple):
                    frame_bgr = packet[0]
                else:
                    frame_bgr = packet
                if frame_bgr is None:
                    continue

                start = time.time()
                cur_angle = self.gimbal.get_angle()
                if cur_angle is None:
                    continue

                detections, _ = self.detector.predict(frame_bgr)
                target = self._select_target(detections)
                laser_center = self.laser_detector._detect_single_frame(frame_bgr)
                stage3_active = True if stage3_active_provider is None else bool(stage3_active_provider())

                if target is not None:
                    self.lost_target_frames = 0
                else:
                    self.lost_target_frames += 1
                    self.last_align_error = None
                    self.last_align_time = None

                if laser_center is not None:
                    self.lost_laser_frames = 0
                else:
                    self.lost_laser_frames += 1
                    self.last_align_error = None
                    self.last_align_time = None

                if stage3_active and target is not None and laser_center is not None:
                    self._step_align(laser_center, target["center"], cur_angle)

                display = self._draw(frame_bgr.copy(), detections, target, laser_center, cur_angle, stage3_active)
                fps = 1.0 / max(time.time() - start, 1e-6)
                self._draw_status(display, fps)
                self._set_latest_ui_frames(display)
                self._write_frame(display if self.save_visualize else frame_bgr)

                if self.show_debug_windows:
                    shown = cv2.resize(display, None, fx=0.4, fy=0.4, interpolation=cv2.INTER_LINEAR)
                    cv2.imshow("Stage3 Countermeasure Tracker", shown)
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord("q"):
                        break
                    if key == ord("r"):
                        self.last_align_error = None
                        self.last_align_time = None
                        self.gimbal.set_angle(0.0, 0.0)
        finally:
            self.gimbal.set_angle(0.0, 0.0)
            time.sleep(0.1)
            self.gimbal.close()
            if self.video_writer is not None:
                self.video_writer.release()
                print(f"[INFO] 阶段三追踪视频已保存: {self.save_path}")
            if self.show_debug_windows:
                cv2.destroyAllWindows()

    def get_latest_ui_frames(self):
        with self.debug_frame_lock:
            display = None if self.latest_display is None else self.latest_display.copy()
        return display, None

    def _select_target(self, detections):
        if not detections:
            return None
        cls, bbox, conf = max(detections, key=lambda item: item[2])
        x1, y1, x2, y2 = map(int, bbox)
        return {
            "cls": int(cls),
            "bbox": (x1, y1, x2, y2),
            "conf": float(conf),
            "center": (int(round((x1 + x2) / 2.0)), int(round((y1 + y2) / 2.0))),
        }

    def _step_align(self, laser_center, target_center, cur_angle):
        error_px = (
            float(target_center[0] - laser_center[0]),
            float(target_center[1] - laser_center[1]),
        )
        error_dist_px = np.hypot(error_px[0], error_px[1])
        if error_dist_px <= ALIGN_DEADBAND_PX:
            self.last_align_error = None
            self.last_align_time = None
            return

        fx = float(self.sub_cam_K[0, 0])
        fy = float(self.sub_cam_K[1, 1])
        align_error = np.array(
            [
                np.degrees(np.arctan(error_px[0] / fx)),
                -np.degrees(np.arctan(error_px[1] / fy)),
            ],
            dtype=np.float64,
        )

        yaw_step = np.clip(ALIGN_KP_YAW * align_error[0], -MAX_STEP_DEG, MAX_STEP_DEG)
        pitch_step = np.clip(ALIGN_KP_PITCH * align_error[1], -MAX_STEP_DEG, MAX_STEP_DEG)
        target_yaw = np.clip(float(cur_angle[0]) + yaw_step, YAW_MIN_DEG, YAW_MAX_DEG)
        target_pitch = np.clip(float(cur_angle[1]) + pitch_step, PITCH_MIN_DEG, PITCH_MAX_DEG)
        self.gimbal.set_angle(target_yaw, target_pitch)

    def _draw(self, display, detections, target, laser_center, cur_angle, stage3_active):
        for cls, bbox, conf in detections:
            x1, y1, x2, y2 = map(int, bbox)
            color = (0, 255, 0)
            cv2.rectangle(display, (x1, y1), (x2, y2), color, 2)
            cv2.putText(
                display,
                f"stage3_target cls={int(cls)} conf={float(conf):.2f}",
                (x1, max(20, y1 - 8)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2,
            )

        if target is not None:
            cv2.circle(display, target["center"], 8, (0, 255, 0), 2)

        cv2.rectangle(display, (X_MIN, Y_MIN), (X_MAX, Y_MAX), (0, 255, 255), 2)
        if laser_center is not None:
            cv2.circle(display, laser_center, 8, (0, 0, 255), 2)
            cv2.putText(
                display,
                f"laser=({laser_center[0]}, {laser_center[1]})",
                (laser_center[0] + 10, laser_center[1] + 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 0, 255),
                2,
            )

        if target is not None and laser_center is not None:
            cv2.line(display, laser_center, target["center"], (0, 255, 255), 2)

        yaw, pitch = float(cur_angle[0]), float(cur_angle[1])
        lines = [
            f"stage3_active={stage3_active}",
            f"yaw={yaw:.2f} pitch={pitch:.2f}",
            f"lost_target={self.lost_target_frames} lost_laser={self.lost_laser_frames}",
        ]
        y = 40
        for text in lines:
            cv2.putText(display, text, (20, y), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 255), 2)
            y += 32
        return display

    def _draw_status(self, display, fps):
        cv2.putText(
            display,
            f"fps={fps:.1f}",
            (20, 136),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            (0, 255, 255),
            2,
        )

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
            print(f"[INFO] 开始保存阶段三追踪视频: {self.save_path}")
        self.video_writer.write(frame)

    def _set_latest_ui_frames(self, display):
        with self.debug_frame_lock:
            self.latest_display = display.copy()

    def _should_stop(self, stop_event):
        return stop_event is not None and stop_event.is_set()


def build_video_provider(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"无法打开视频文件: {video_path}")
    video_fps = float(cap.get(cv2.CAP_PROP_FPS))
    if video_fps <= 0:
        raise RuntimeError(f"无法读取视频 FPS: {video_path}")

    def frame_provider():
        ret, frame_bgr = cap.read()
        if not ret:
            return None
        return frame_bgr

    return frame_provider, cap, video_fps


def build_sub_camera_provider(config, group_id):
    sub_cfg = copy.deepcopy(config.sub_camera)
    sub_cfg.exposure_time = sub_cfg.stage3.exposure_time
    sub_cfg.gain = sub_cfg.stage3.gain
    if "gamma_enable" in sub_cfg.stage3:
        sub_cfg.gamma_enable = bool(sub_cfg.stage3.gamma_enable)
    if getattr(sub_cfg, "gamma_enable", False):
        sub_cfg.gamma = sub_cfg.stage3.gamma
    cam_sub = SimpleHikCamera(sub_cfg, camera_role="sub")
    cam_sub.start_streaming()
    cam_sub.register_group(group_id)
    time.sleep(1.0)

    def frame_provider():
        frame_rgb, _ = cam_sub.get_image_latest(group_id, timeout=0.05)
        if frame_rgb is None:
            return None
        return cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

    return frame_provider, cam_sub, float(getattr(config.sub_camera, "acquisition_rate", 20.0))


def parse_args():
    parser = argparse.ArgumentParser(description="阶段三不发光模块反制追踪")
    parser.add_argument("--source", choices=["sub", "video"], default="sub")
    parser.add_argument("--video-path", default=None)
    parser.add_argument("--config", default="config/params.yaml")
    parser.add_argument("--model", default="weights/stage3.engine")
    parser.add_argument("--img-size", type=int, default=640)
    parser.add_argument("--conf", type=float, default=0.25)
    parser.add_argument("--iou", type=float, default=0.45)
    parser.add_argument("--max-det", type=int, default=1)
    parser.add_argument("--device", default="cuda")
    parser.add_argument("--no-show", action="store_true")
    parser.add_argument("--save", action="store_true")
    parser.add_argument("--save-visualize", action="store_true")
    parser.add_argument("--save-path", default=None)
    return parser.parse_args()


def main():
    args = parse_args()
    config = load_cfg_from_cfg_file(args.config)
    detector = Stage3Detector(
        model_path=args.model,
        img_size=args.img_size,
        conf_thres=args.conf,
        iou_thres=args.iou,
        max_det=args.max_det,
        device=args.device,
    )

    source_handle = None
    group_id = "stage3_lisar_tracker"
    if args.source == "video":
        if args.video_path is None:
            raise ValueError("--video-path is required when --source video")
        frame_provider, source_handle, run_fps = build_video_provider(args.video_path)
    else:
        frame_provider, source_handle, run_fps = build_sub_camera_provider(config, group_id)

    save_path = args.save_path
    if args.save and save_path is None:
        save_root = config.sub_camera.recording_save_root_dir
        os.makedirs(save_root, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = os.path.join(save_root, f"stage3_lisar_tracker_{timestamp}.mp4")

    tracker = Stage3CountermeasureTracker(
        config=config,
        detector=detector,
        visualize=not args.no_show,
        save_path=save_path if args.save else None,
        save_fps=run_fps,
        save_visualize=args.save_visualize,
    )

    try:
        tracker.run(frame_provider, stop_on_empty_frame=args.source == "video")
    finally:
        if args.source == "video" and source_handle is not None:
            source_handle.release()
        if args.source == "sub" and source_handle is not None:
            source_handle.stop_streaming()
            source_handle.close()


if __name__ == "__main__":
    main()
