import argparse
import sys
import time
from pathlib import Path

import cv2
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from lisar.utils.get_angle import cal_angle


MIN_BAR_AREA = 100
MAX_BAR_AREA = 2500
MIN_BAR_ASPECT = 1.8
MAX_BAR_ANGLE_DEG = 15 # bar最大倾斜角度
MAX_PAIR_SCORE = 1.0

BRIGHT_THRESHOLD = 20 # 场馆用
# BRIGHT_THRESHOLD = 35 比赛用
OPEN_KERNEL = (15, 3)
CLOSE_KERNEL = (25, 3)

def detect_lisar_module(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, BRIGHT_THRESHOLD, 255, cv2.THRESH_BINARY)

    open_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, OPEN_KERNEL)
    opened = cv2.morphologyEx(binary, cv2.MORPH_OPEN, open_kernel)

    close_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, CLOSE_KERNEL)
    closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, close_kernel)

    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    bars = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < MIN_BAR_AREA or area > MAX_BAR_AREA:
            continue

        rect = cv2.minAreaRect(contour)
        (cx, cy), (w, h), angle = rect
        if w <= 0 or h <= 0:
            continue

        length = max(w, h)
        width = min(w, h)
        if length / width < MIN_BAR_ASPECT:
            continue

        if w < h:
            angle += 90
        if angle < -45:
            angle += 180
        if angle > 135:
            angle -= 180
        if abs(angle) > MAX_BAR_ANGLE_DEG:
            continue

        bars.append(
            {
                "center": (float(cx), float(cy)),
                "length": float(length),
                "width": float(width),
                "area": float(area),
                "angle": float(angle),
                "rect": rect,
            }
        )

    best = None
    for index_a in range(len(bars)):
        for index_b in range(index_a + 1, len(bars)):
            upper, lower = sorted((bars[index_a], bars[index_b]), key=lambda item: item["center"][1])
            mean_length = (upper["length"] + lower["length"]) / 2
            mean_width = (upper["width"] + lower["width"]) / 2
            if mean_length <= 0 or mean_width <= 0:
                continue

            dx = abs(upper["center"][0] - lower["center"][0])
            dy = lower["center"][1] - upper["center"][1]
            if dy <= 0:
                continue

            angle_error = abs(upper["angle"] - lower["angle"])
            angle_error = min(angle_error, 180 - angle_error) / 30
            x_align_error = dx / mean_length
            length_error = abs(np.log(upper["length"] / lower["length"]))
            width_error = abs(np.log(upper["width"] / lower["width"]))
            gap_ratio = dy / mean_length
            gap_error = abs(np.log(gap_ratio / 0.55))

            score = angle_error + x_align_error + length_error + width_error + 0.5 * gap_error
            if best is None or score < best["score"]:
                points = np.array(
                    [
                        upper["center"],
                        lower["center"],
                    ],
                    dtype=np.float32,
                )
                best = {
                    "center": tuple(np.round(points.mean(axis=0)).astype(int)),
                    "upper": upper,
                    "lower": lower,
                    "score": float(score),
                }

    if best is None or best["score"] > MAX_PAIR_SCORE:
        best = {
            "found": False,
            "center": None,
            "upper": None,
            "lower": None,
            "score": None,
        }
    else:
        best["found"] = True

    best["mask"] = closed
    best["bars"] = bars
    return best


class LisarModuleDetector:
    def __init__(self, K, dist_coeffs):
        self.K = np.array(K, dtype=np.float64).reshape(3, 3)
        self.dist_coeffs = np.asarray(dist_coeffs, dtype=np.float64).flatten()

    def detect(self, img_bgr, current_angle):
        raw = detect_lisar_module(img_bgr)
        if raw["found"]:
            raw["world_angle"] = self._pixel_to_world_angle(raw["center"], current_angle)
        else:
            raw["world_angle"] = None
        raw["predicted"] = False
        raw["state"] = "DETECTED" if raw["found"] else "NOT_FOUND"
        return raw

    def _pixel_to_world_angle(self, center, current_angle):
        yaw_relate_cam, pitch_relate_cam = cal_angle(
            self.K,
            self.dist_coeffs,
            float(center[0]),
            float(center[1]),
            verbose=False,
        )
        return float(current_angle[0] + yaw_relate_cam), float(current_angle[1] + pitch_relate_cam)


def draw_lisar_module_result(img, result, font_scale=None, thickness=2):
    if result is None:
        return
    bars_font_scale = 0.8 if font_scale is None else font_scale
    module_font_scale = 0.65 if font_scale is None else font_scale

    for bar in result["bars"]:
        box = cv2.boxPoints(bar["rect"])
        cv2.polylines(img, [np.round(box).astype(np.int32)], True, (255, 0, 0), 1)

    if not result["found"]:
        cv2.putText(
            img,
            f"bars={len(result['bars'])}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            bars_font_scale,
            (255, 0, 0),
            thickness,
        )
        return

    if not result.get("predicted", False):
        for bar in (result["upper"], result["lower"]):
            box = cv2.boxPoints(bar["rect"])
            cv2.polylines(img, [np.round(box).astype(np.int32)], True, (0, 255, 0), 2)

    center = result["center"]
    cv2.circle(img, center, 8, (0, 0, 255), 2)
    score_text = "pred" if result.get("predicted", False) else f"score={result['score']:.3f}"
    cv2.putText(
        img,
        f"module=({center[0]}, {center[1]}) {score_text}",
        (center[0] + 10, center[1] - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        module_font_scale,
        (0, 0, 255),
        thickness,
    )


def main():
    parser = argparse.ArgumentParser(description="lisar detect module detect")
    parser.add_argument("--source", choices=["video", "sub"], default="video")
    parser.add_argument("--video-path", default="archive/camera.mp4")
    parser.add_argument("--config", default="config/params.yaml")
    args = parser.parse_args()

    cap = None
    cam_sub = None
    group_id = "lisar_module_detect"

    if args.source == "video":
        cap = cv2.VideoCapture(args.video_path)
        window_name = args.video_path
        if not cap.isOpened():
            print("Error: 无法打开视频文件")
            raise SystemExit(1)
    else:
        from driver.hik_camera.hik import SimpleHikCamera
        from utils.config import load_cfg_from_cfg_file

        config = load_cfg_from_cfg_file(args.config)
        cam_sub = SimpleHikCamera(config.sub_camera, camera_role="sub")
        cam_sub.start_streaming()
        cam_sub.register_group(group_id)
        time.sleep(1.0)
        window_name = "sub-camera"

    try:
        while True:
            start = time.time()

            if args.source == "video":
                ret, frame = cap.read()
                if not ret:
                    print("视频读取结束")
                    break
            else:
                frame_rgb, _ = cam_sub.get_image_latest(group_id, timeout=0.1)
                if frame_rgb is None:
                    continue
                frame = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

            result = detect_lisar_module(frame)
            display = frame.copy()
            draw_lisar_module_result(display, result)

            cv2.imshow(window_name, cv2.resize(display, None, fx=0.5, fy=0.5))
            cv2.imshow("module_mask", cv2.resize(result["mask"], None, fx=0.5, fy=0.5))

            key = cv2.waitKey(30) & 0xFF
            if key == ord(" "):
                print("已暂停")
                while True:
                    key = cv2.waitKey(100) & 0xFF
                    if key == ord(" "):
                        print("继续播放")
                        break
            if key == ord("q"):
                break

            gap = time.time() - start
            print(f"FPS: {1 / gap}")
    finally:
        if cap is not None:
            cap.release()
        if cam_sub is not None:
            cam_sub.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
