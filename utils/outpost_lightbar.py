from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import cv2
import numpy as np

from utils.config import load_cfg_from_cfg_file


@dataclass
class OutpostLightbarResult:
    is_destroyed: bool
    bright_count: int
    bright_ratio: float
    max_value: int
    mean_value: float
    roi: tuple[int, int, int, int]


def parse_roi(text: str | None) -> tuple[int, int, int, int] | None:
    if text is None:
        return None
    values = [int(item.strip()) for item in text.split(",")]
    if len(values) != 4:
        raise ValueError("ROI 格式应为 x,y,w,h")
    x, y, w, h = values
    if w <= 0 or h <= 0:
        raise ValueError("ROI 的 w 和 h 必须大于 0")
    return x, y, w, h


def clamp_roi(roi: tuple[int, int, int, int], image_shape: Iterable[int]) -> tuple[int, int, int, int]:
    height, width = list(image_shape)[:2]
    x, y, w, h = roi
    x1 = max(0, min(width, x))
    y1 = max(0, min(height, y))
    x2 = max(0, min(width, x + w))
    y2 = max(0, min(height, y + h))
    if x2 <= x1 or y2 <= y1:
        raise ValueError(f"ROI {roi} 不在图像范围内")
    return x1, y1, x2 - x1, y2 - y1


def detect_outpost_lightbar(
    image_bgr: np.ndarray,
    roi: tuple[int, int, int, int],
    value_threshold: int = 180,
    min_bright_pixels: int = 1,
) -> OutpostLightbarResult:
    roi = clamp_roi(roi, image_bgr.shape)
    x, y, w, h = roi
    roi_bgr = image_bgr[y : y + h, x : x + w]
    value = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2HSV)[:, :, 2]
    bright_mask = value >= value_threshold
    bright_count = int(np.count_nonzero(bright_mask))
    bright_ratio = bright_count / float(w * h)
    max_value = int(value.max())
    mean_value = float(value.mean())
    is_destroyed = bright_count < min_bright_pixels
    return OutpostLightbarResult(
        is_destroyed=is_destroyed,
        bright_count=bright_count,
        bright_ratio=bright_ratio,
        max_value=max_value,
        mean_value=mean_value,
        roi=roi,
    )


def draw_outpost_lightbar_result(image_bgr: np.ndarray, result: OutpostLightbarResult) -> np.ndarray:
    vis = image_bgr.copy()
    x, y, w, h = result.roi
    color = (0, 0, 255) if result.is_destroyed else (0, 255, 0)
    label = (
        f"destroyed={int(result.is_destroyed)} "
        f"bright={result.bright_count} "
        f"max={result.max_value} "
        f"mean={result.mean_value:.1f}"
    )
    cv2.rectangle(vis, (x, y), (x + w, y + h), color, 2)
    cv2.putText(vis, label, (x, max(20, y - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.65, color, 2)
    return vis


def resize_for_display(image_bgr: np.ndarray, max_width: int, max_height: int) -> tuple[np.ndarray, float]:
    height, width = image_bgr.shape[:2]
    scale = min(max_width / width, max_height / height, 1.0)
    if scale >= 1.0:
        return image_bgr, 1.0
    display_size = (int(round(width * scale)), int(round(height * scale)))
    return cv2.resize(image_bgr, display_size, interpolation=cv2.INTER_AREA), scale


def select_roi(frame_bgr: np.ndarray, max_width: int, max_height: int) -> tuple[int, int, int, int]:
    display_frame, scale = resize_for_display(frame_bgr, max_width, max_height)
    roi = cv2.selectROI("select outpost lightbar roi", display_frame, fromCenter=False, showCrosshair=True)
    cv2.destroyWindow("select outpost lightbar roi")
    x, y, w, h = map(int, roi)
    if w <= 0 or h <= 0:
        raise ValueError("未选择有效 ROI")
    if scale < 1.0:
        x = int(round(x / scale))
        y = int(round(y / scale))
        w = int(round(w / scale))
        h = int(round(h / scale))
    print(f"Selected ROI: {x},{y},{w},{h}")
    return x, y, w, h


def open_video_source(source: str) -> cv2.VideoCapture:
    try:
        source_value = int(source)
    except ValueError:
        source_value = source
    cap = cv2.VideoCapture(source_value)
    if not cap.isOpened():
        raise RuntimeError(f"无法打开视频源: {source}")
    return cap


def run_video_test(args: argparse.Namespace) -> None:
    cap = open_video_source(args.source)
    roi = parse_roi(args.roi)
    window_name = "outpost lightbar"
    frame = None
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    has_progress_bar = frame_count > 0
    state = {"paused": False, "seek_frame": None, "updating_progress": False}

    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    def handle_progress_changed(frame_index: int) -> None:
        if state["updating_progress"]:
            return
        state["seek_frame"] = frame_index
        state["paused"] = True

    if has_progress_bar:
        cv2.createTrackbar("frame", window_name, 0, max(0, frame_count - 1), handle_progress_changed)

    try:
        while True:
            if state["seek_frame"] is not None:
                cap.set(cv2.CAP_PROP_POS_FRAMES, int(state["seek_frame"]))
                state["seek_frame"] = None
                ok, frame = cap.read()
                if not ok:
                    break
            elif not state["paused"]:
                ok, frame = cap.read()
                if not ok:
                    break
            elif frame is None:
                ok, frame = cap.read()
                if not ok:
                    break

            if roi is None:
                roi = select_roi(frame, args.display_width, args.display_height)

            result = detect_outpost_lightbar(
                frame,
                roi,
                value_threshold=args.value_threshold,
                min_bright_pixels=args.min_bright_pixels,
            )
            vis = draw_outpost_lightbar_result(frame, result)
            display_vis, _ = resize_for_display(vis, args.display_width, args.display_height)
            cv2.imshow(window_name, display_vis)

            if has_progress_bar:
                current_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES)) - 1
                current_frame = max(0, min(frame_count - 1, current_frame))
                state["updating_progress"] = True
                cv2.setTrackbarPos("frame", window_name, current_frame)
                state["updating_progress"] = False

            print(
                f"destroyed={int(result.is_destroyed)} "
                f"bright={result.bright_count} "
                f"ratio={result.bright_ratio:.4f} "
                f"max={result.max_value} "
                f"mean={result.mean_value:.1f}",
                end="\r",
            )

            key = cv2.waitKey(30) & 0xFF
            if key == ord("q"):
                break
            if key == ord(" "):
                state["paused"] = not state["paused"]
            if key == ord("r"):
                roi = select_roi(frame, args.display_width, args.display_height)
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print()


def run_hik_test(args: argparse.Namespace) -> None:
    from driver.hik_camera.hik import SimpleHikCamera

    config = load_cfg_from_cfg_file(args.config)
    camera = SimpleHikCamera(config.main_camera, camera_role="main")
    camera.register_group("outpost_lightbar")
    camera.start_streaming()
    roi = parse_roi(args.roi)

    try:
        while True:
            frame_rgb, _ = camera.get_image_latest("outpost_lightbar", timeout=1.0)
            if frame_rgb is None:
                continue
            frame = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

            if roi is None:
                roi = select_roi(frame, args.display_width, args.display_height)

            result = detect_outpost_lightbar(
                frame,
                roi,
                value_threshold=args.value_threshold,
                min_bright_pixels=args.min_bright_pixels,
            )
            vis = draw_outpost_lightbar_result(frame, result)
            display_vis, _ = resize_for_display(vis, args.display_width, args.display_height)
            cv2.imshow("outpost lightbar", display_vis)
            print(
                f"destroyed={int(result.is_destroyed)} "
                f"bright={result.bright_count} "
                f"ratio={result.bright_ratio:.4f} "
                f"max={result.max_value} "
                f"mean={result.mean_value:.1f}",
                end="\r",
            )

            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            if key == ord("r"):
                roi = select_roi(frame, args.display_width, args.display_height)
    finally:
        camera.close()
        cv2.destroyAllWindows()
        print()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="前哨站灯条亮度检测标定工具")
    parser.add_argument("--source", default="/home/wtz/桌面/video_save/camera_20260525_142834.mp4", help="视频路径或摄像头索引；不填且不用 --hik 时读取 params.yaml 的 video_path")
    parser.add_argument("--hik", action="store_true", help="使用海康主相机")
    parser.add_argument("--config", default="config/params.yaml", help="配置文件路径")
    parser.add_argument("--roi", default=None, help="灯条 ROI，格式 x,y,w,h；不填则启动后按当前帧框选")
    parser.add_argument("--value-threshold", type=int, default=180, help="HSV V 通道亮度阈值")
    parser.add_argument("--min-bright-pixels", type=int, default=1, help="判定未摧毁所需的最少亮点数量")
    parser.add_argument("--display-width", type=int, default=1280, help="测试窗口最大显示宽度")
    parser.add_argument("--display-height", type=int, default=720, help="测试窗口最大显示高度")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.hik:
        run_hik_test(args)
        return

    if args.source is None:
        config = load_cfg_from_cfg_file(args.config)
        args.source = str(Path(config.video_path))
    run_video_test(args)


if __name__ == "__main__":
    main()
