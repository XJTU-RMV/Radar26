import time
import argparse
from collections import deque

import cv2
import numpy as np

# 大ROI
REJECT_X_MIN = 0
REJECT_Y_MIN = 0
REJECT_X_MAX = None
REJECT_Y_MAX = None
MAX_REJECT_RED_AREA = 300

# 小ROI
X_MIN = 1100
Y_MIN = 880
X_MAX = 1200
Y_MAX = 950
default_point = (1036, 967)

# 重理内录参数
# X_MIN = 630
# Y_MIN = 520
# X_MAX = 730
# Y_MAX = 600
# default_point = (690, 580)

MIN_RED_AREA = 5
MAX_RED_AREA = 300

RED_HSV_LOWER1 = (0, 80, 80)
RED_HSV_UPPER1 = (10, 255, 255)
RED_HSV_LOWER2 = (170, 80, 80)
RED_HSV_UPPER2 = (180, 255, 255)

HISTORY_LEN = 10
MAX_JUMP_PX = 50
OUTLIER_CONFIRM_FRAMES = 5
OUTLIER_STABLE_RADIUS_PX = 8
MAX_HORIZONTAL_Y_DIFF_PX = 50


class LisarDotDetector:
    def __init__(
        self,
        history_len=HISTORY_LEN,
        max_jump_px=MAX_JUMP_PX,
        initial_point=default_point,
        outlier_confirm_frames=OUTLIER_CONFIRM_FRAMES,
        outlier_stable_radius_px=OUTLIER_STABLE_RADIUS_PX,
        max_horizontal_y_diff_px=MAX_HORIZONTAL_Y_DIFF_PX,
    ):
        self.history = deque(maxlen=history_len)
        self.outlier_history = deque(maxlen=outlier_confirm_frames)
        self.max_jump_px = max_jump_px
        self.initial_point = initial_point
        self.outlier_confirm_frames = outlier_confirm_frames
        self.outlier_stable_radius_px = outlier_stable_radius_px
        self.max_horizontal_y_diff_px = max_horizontal_y_diff_px

    def detect(self, img):
        center = self._detect_single_frame(img)
        if center is None:
            self.outlier_history.clear()
            predicted = self._predict()
            return predicted if predicted is not None else self.initial_point, True

        predicted = self._predict()
        if predicted is not None:
            jump = np.hypot(center[0] - predicted[0], center[1] - predicted[1])
            if jump > self.max_jump_px:
                if abs(center[1] - predicted[1]) > self.max_horizontal_y_diff_px:
                    self.outlier_history.clear()
                    return predicted, True

                self.outlier_history.append(center)
                outlier_points = np.array(self.outlier_history)
                outlier_center = np.median(outlier_points, axis=0)
                outlier_dist = np.hypot(
                    outlier_points[:, 0] - outlier_center[0],
                    outlier_points[:, 1] - outlier_center[1],
                )
                outlier_spread = np.max(outlier_dist)
                if (
                    len(self.outlier_history) >= self.outlier_confirm_frames
                    and outlier_spread <= self.outlier_stable_radius_px
                ):
                    self.history.clear()
                    self.history.extend(self.outlier_history)
                    self.outlier_history.clear()
                    return center, False

                return predicted, True

        self.outlier_history.clear()
        self.history.append(center)
        return center, False

    def _predict(self):
        if not self.history:
            return None
        points = np.array(self.history)
        return int(round(np.median(points[:, 0]))), int(round(np.median(points[:, 1])))

    def _detect_single_frame(self, img):
        height, width = img.shape[:2]
        reject_x_max = width if REJECT_X_MAX is None else REJECT_X_MAX
        reject_y_max = height if REJECT_Y_MAX is None else REJECT_Y_MAX
        reject_roi = img[REJECT_Y_MIN:reject_y_max, REJECT_X_MIN:reject_x_max]
        hsv = cv2.cvtColor(reject_roi, cv2.COLOR_BGR2HSV)
        red_mask1 = cv2.inRange(hsv, RED_HSV_LOWER1, RED_HSV_UPPER1)
        red_mask2 = cv2.inRange(hsv, RED_HSV_LOWER2, RED_HSV_UPPER2)
        red_mask = cv2.bitwise_or(red_mask1, red_mask2)

        contours, _ = cv2.findContours(red_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            if cv2.contourArea(contour) > MAX_REJECT_RED_AREA:
                cv2.drawContours(red_mask, [contour], -1, 0, -1)

        roi_x_min = X_MIN - REJECT_X_MIN
        roi_y_min = Y_MIN - REJECT_Y_MIN
        roi_x_max = X_MAX - REJECT_X_MIN
        roi_y_max = Y_MAX - REJECT_Y_MIN
        if roi_x_min < 0 or roi_y_min < 0 or roi_x_max > red_mask.shape[1] or roi_y_max > red_mask.shape[0]:
            raise ValueError("laser dot ROI must be inside reject ROI")
        roi_mask = red_mask[roi_y_min:roi_y_max, roi_x_min:roi_x_max]

        contours, _ = cv2.findContours(roi_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        candidates = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if MIN_RED_AREA <= area <= MAX_RED_AREA:
                candidates.append(contour)

        if not candidates:
            return None

        contour = max(candidates, key=cv2.contourArea)
        (x, y), radius = cv2.minEnclosingCircle(contour)
        if radius <= 0:
            return None

        return int(round(X_MIN + x)), int(round(Y_MIN + y))

def main():
    parser = argparse.ArgumentParser(description="激光点检测调试")
    parser.add_argument("--source", choices=["video", "sub"], default="video")
    parser.add_argument("--video-path", default="demo/demo.mp4")
    parser.add_argument("--config", default="config/params.yaml")
    args = parser.parse_args()

    cap = None
    cam_sub = None
    group_id = "detect_lisar"
    detector = LisarDotDetector()

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

            center, is_predicted = detector.detect(frame)
            display = frame.copy()
            cv2.rectangle(display, (X_MIN, Y_MIN), (X_MAX, Y_MAX), (0, 255, 255), 2)
            if center is not None:
                color = (0, 255, 255) if is_predicted else (0, 255, 0)
                label = "pred" if is_predicted else "laser"
                cv2.circle(display, center, 8, color, 2)
                cv2.putText(
                    display,
                    f"{label}=({center[0]}, {center[1]})",
                    (center[0] + 10, center[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    color,
                    2,
                )

            display = cv2.resize(display, None, fx=0.5, fy=0.5)
            cv2.imshow(window_name, display)

            key = cv2.waitKey(10) & 0xFF # 理论最大10帧
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
