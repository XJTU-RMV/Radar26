from __future__ import annotations

import argparse
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from lisar.common.frame_source import build_sub_camera_frame_provider, build_video_frame_provider
from lisar.common.laser_reference import ObservedLaserDotReference, draw_laser_reference_roi
from lisar.common.tracking_behavior import MODULE_HOLD_FRAMES
from lisar.common.search_state import CountermeasureSearchState
from lisar.difficulty.model_detector import Yolo26TargetDetector, load_stage3_detector_config
from utils.config import load_cfg_from_cfg_file

STATIC_CURRENT_ANGLE = (0.0, 0.0)
WINDOW_NAME = "Stage3 YOLO26 Without Gimbal"
TRACKBAR_NAME = "frame"


class Yolo26TrackerWithoutGimbal:
    def __init__(
        self,
        detector,
        visualize=True,
        save_path=None,
        save_fps=20.0,
        save_visualize=False,
        img_size=640,
        module_hold_frames=MODULE_HOLD_FRAMES,
    ):
        self.detector = detector
        self.show_debug_windows = bool(visualize)
        self.save_path = save_path
        self.save_fps = float(save_fps)
        self.save_visualize = bool(save_visualize)
        self.video_writer = None
        self.laser_reference = ObservedLaserDotReference(allow_prediction=True)
        self.search_state = CountermeasureSearchState(hold_after_seen_frames=module_hold_frames)

    def run(self, frame_provider, stage3_active_provider=None, stop_on_empty_frame=False):
        try:
            while True:
                frame_bgr = frame_provider()
                if frame_bgr is None:
                    if stop_on_empty_frame:
                        print("video ended")
                        break
                    time.sleep(0.005)
                    continue

                display = self._process_frame(frame_bgr, stage3_active_provider)
                self._write_frame(display if self.save_visualize else frame_bgr)

                if self.show_debug_windows:
                    cv2.imshow(WINDOW_NAME, cv2.resize(display, None, fx=0.4, fy=0.4))
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord("q"):
                        break
                    if key == ord("r"):
                        self.reset()
        finally:
            if self.video_writer is not None:
                self.video_writer.release()
                print(f"[INFO] YOLO26 without-gimbal video saved: {self.save_path}")
            if self.show_debug_windows:
                cv2.destroyAllWindows()

    def run_video(self, video_capture, stage3_active_provider=None):
        if not self.show_debug_windows:
            self.run(lambda: self._read_next_video_frame(video_capture), stage3_active_provider, stop_on_empty_frame=True)
            return

        frame_count = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
        if frame_count <= 0:
            raise RuntimeError("failed to read video frame count")
        fps = float(video_capture.get(cv2.CAP_PROP_FPS))
        delay_ms = max(1, int(round(1000.0 / fps))) if fps > 0.0 else 33
        state = {
            "frame_idx": 0,
            "paused": True,
            "trackbar_update": False,
            "user_seek": False,
        }

        def on_trackbar(value):
            if state["trackbar_update"]:
                return
            state["frame_idx"] = int(value)
            state["user_seek"] = True

        cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
        cv2.createTrackbar(TRACKBAR_NAME, WINDOW_NAME, 0, max(frame_count - 1, 0), on_trackbar)

        try:
            while True:
                if state["user_seek"]:
                    self.reset()
                    state["user_seek"] = False

                frame_idx = min(max(state["frame_idx"], 0), frame_count - 1)
                frame_bgr = self._read_video_frame(video_capture, frame_idx)
                display = self._process_frame(frame_bgr, stage3_active_provider)
                self._draw_frame_index(display, frame_idx, frame_count)
                if not state["paused"]:
                    self._write_frame(display if self.save_visualize else frame_bgr)
                cv2.imshow(WINDOW_NAME, cv2.resize(display, None, fx=0.4, fy=0.4))

                state["trackbar_update"] = True
                cv2.setTrackbarPos(TRACKBAR_NAME, WINDOW_NAME, frame_idx)
                state["trackbar_update"] = False

                key = cv2.waitKey(30 if state["paused"] else delay_ms) & 0xFF
                if key in (27, ord("q")):
                    break
                if key == ord(" "):
                    state["paused"] = not state["paused"]
                    continue
                if key == ord("r"):
                    self.reset()
                    continue
                if key == ord("a"):
                    state["frame_idx"] = max(0, frame_idx - 1)
                    state["paused"] = True
                    self.reset()
                    continue
                if key == ord("d"):
                    state["frame_idx"] = min(frame_count - 1, frame_idx + 1)
                    state["paused"] = True
                    self.reset()
                    continue
                if not state["paused"]:
                    state["frame_idx"] = 0 if frame_idx + 1 >= frame_count else frame_idx + 1
        finally:
            if self.video_writer is not None:
                self.video_writer.release()
                print(f"[INFO] YOLO26 without-gimbal video saved: {self.save_path}")
            cv2.destroyAllWindows()

    def reset(self):
        self.search_state.reset()

    def _process_frame(self, frame_bgr, stage3_active_provider=None):
        start = time.time()
        current_angle = STATIC_CURRENT_ANGLE
        detection = self.detector.detect(frame_bgr, {"current_angle": current_angle})
        laser_point = self.laser_reference.locate(frame_bgr)
        stage3_active = True if stage3_active_provider is None else bool(stage3_active_provider())
        state = self.search_state.update(detection is not None)

        display = self._draw(frame_bgr.copy(), detection, laser_point, stage3_active, state)
        fps = 1.0 / max(time.time() - start, 1e-6)
        self._draw_status(display, fps)
        return display

    def _read_next_video_frame(self, video_capture):
        ok, frame_bgr = video_capture.read()
        return frame_bgr if ok else None

    def _read_video_frame(self, video_capture, frame_idx):
        video_capture.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ok, frame_bgr = video_capture.read()
        if not ok:
            raise RuntimeError(f"failed to read video frame: {frame_idx}")
        return frame_bgr

    def _draw(self, display, detection, laser_point, stage3_active, state):
        if detection is not None:
            for cls, bbox, conf in detection.debug["detections"]:
                x1, y1, x2, y2 = map(int, bbox)
                cv2.rectangle(display, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(
                    display,
                    f"stage3_target cls={int(cls)} conf={float(conf):.2f}",
                    (x1, max(20, y1 - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2,
                )
            cv2.circle(display, detection.center, 8, (0, 255, 0), 2)

        draw_laser_reference_roi(display)
        if laser_point is not None:
            cv2.circle(display, laser_point.center, 8, (0, 0, 255), 2)
            cv2.putText(
                display,
                f"laser=({laser_point.center[0]}, {laser_point.center[1]})",
                (laser_point.center[0] + 10, laser_point.center[1] + 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 0, 255),
                2,
            )

        if detection is not None and laser_point is not None:
            cv2.line(display, laser_point.center, detection.center, (0, 255, 255), 2)
            error = (
                detection.center[0] - laser_point.center[0],
                detection.center[1] - laser_point.center[1],
            )
            distance = float(np.hypot(error[0], error[1]))
            cv2.putText(
                display,
                f"error=({error[0]}, {error[1]}) dist={distance:.1f}px",
                (20, 170),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 255, 255),
                2,
            )
        elif detection is None:
            cv2.putText(display, "YOLO26 TARGET NOT FOUND", (20, 170), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 165, 255), 2)
        elif laser_point is None:
            cv2.putText(display, "LASER DOT NOT FOUND", (20, 170), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 165, 255), 2)

        lines = [
            f"stage3_active={stage3_active}",
            f"state={state.value} lost={self.search_state.lost_frames}",
            "gimbal=disabled",
        ]
        y = 40
        for text in lines:
            cv2.putText(display, text, (20, y), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 255), 2)
            y += 32
        return display

    def _draw_status(self, display, fps):
        cv2.putText(display, f"fps={fps:.1f}", (20, 136), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 255), 2)

    def _draw_frame_index(self, display, frame_idx, frame_count):
        text = f"frame={frame_idx + 1}/{frame_count}"
        cv2.putText(display, text, (20, display.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 255), 2)

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
                raise RuntimeError(f"failed to create video file: {self.save_path}")
            print(f"[INFO] start saving YOLO26 without-gimbal video: {self.save_path}")
        self.video_writer.write(frame)


def parse_args():
    parser = argparse.ArgumentParser(description="difficulty: YOLO26 detection without gimbal control")
    parser.add_argument("--source", choices=["sub", "video"], default="sub")
    parser.add_argument("--video-path", default="demo/demo.mp4")
    parser.add_argument("--config", default="config/params.yaml")
    parser.add_argument("--model", default=None)
    parser.add_argument("--img-size", type=int, default=None)
    parser.add_argument("--conf", type=float, default=None)
    parser.add_argument("--iou", type=float, default=None)
    parser.add_argument("--max-det", type=int, default=None)
    parser.add_argument("--device", default=None)
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
    return parser.parse_args()


def main():
    args = parse_args()
    config = load_cfg_from_cfg_file(args.config)
    stage3_cfg = load_stage3_detector_config(config)
    if args.model is not None:
        stage3_cfg["model_path"] = args.model
    if args.img_size is not None:
        stage3_cfg["img_size"] = args.img_size
    if args.conf is not None:
        stage3_cfg["conf_thres"] = args.conf
    if args.iou is not None:
        stage3_cfg["iou_thres"] = args.iou
    if args.max_det is not None:
        stage3_cfg["max_det"] = args.max_det
    if args.device is not None:
        stage3_cfg["device"] = args.device
    detector = Yolo26TargetDetector(
        **stage3_cfg,
    )

    source_handle = None
    if args.source == "video":
        if args.video_path is None:
            raise ValueError("--video-path is required when --source video")
        frame_provider, source_handle, run_fps = build_video_frame_provider(args.video_path)
    else:
        frame_provider, source_handle, run_fps = build_sub_camera_frame_provider(
            config,
            "difficulty_yolo26_without_gimbal",
            use_stage3_profile=True,
        )

    save_path = args.save_path
    if args.save and save_path is None:
        save_root = config.sub_camera.recording_save_root_dir
        os.makedirs(save_root, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = os.path.join(save_root, f"difficulty_yolo26_without_gimbal_{timestamp}.mp4")

    tracker = Yolo26TrackerWithoutGimbal(
        detector=detector,
        visualize=not args.no_show,
        save_path=save_path if args.save else None,
        save_fps=run_fps,
        save_visualize=args.save_visualize,
        img_size=stage3_cfg["img_size"],
        module_hold_frames=args.module_hold_frames,
    )

    try:
        if args.source == "video" and source_handle is not None:
            tracker.run_video(source_handle)
        else:
            tracker.run(frame_provider, stop_on_empty_frame=False)
    finally:
        if args.source == "video" and source_handle is not None:
            source_handle.release()
        if args.source == "sub" and source_handle is not None:
            source_handle.stop_streaming()
            source_handle.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
