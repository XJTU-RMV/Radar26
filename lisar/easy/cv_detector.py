from __future__ import annotations

import cv2
import numpy as np

from lisar.common.types import TargetDetection


class CvModuleTargetDetector:
    def __init__(self, camera_K=None, dist_coeffs=None):
        self.module_detector = None
        if camera_K is not None and dist_coeffs is not None:
            from lisar.easy.lisar_module_detect import LisarModuleDetector

            self.module_detector = LisarModuleDetector(camera_K, dist_coeffs)

    def detect(self, frame_bgr, context=None):
        current_angle = None if context is None else context.get("current_angle")
        if self.module_detector is not None and current_angle is not None:
            raw = self.module_detector.detect(frame_bgr, current_angle)
        else:
            from lisar.easy.lisar_module_detect import detect_lisar_module

            raw = detect_lisar_module(frame_bgr)

        if not raw["found"]:
            return None

        score = raw.get("score")
        confidence = 1.0 if score is None else 1.0 / (1.0 + max(float(score), 0.0))
        return TargetDetection(
            center=tuple(map(int, raw["center"])),
            bbox=_bbox_from_module_result(raw),
            confidence=confidence,
            source="cv_module",
            debug=raw,
        )


def _bbox_from_module_result(result):
    points = []
    for key in ("upper", "lower"):
        bar = result.get(key)
        if bar is None:
            continue
        box = cv2.boxPoints(bar["rect"])
        points.append(box)
    if not points:
        return None
    all_points = np.vstack(points)
    x1, y1 = np.floor(all_points.min(axis=0)).astype(int)
    x2, y2 = np.ceil(all_points.max(axis=0)).astype(int)
    return int(x1), int(y1), int(x2), int(y2)


def draw_cv_detection(display, detection, font_scale=None, thickness=2):
    if detection is None:
        return
    from lisar.easy.lisar_module_detect import draw_lisar_module_result

    draw_lisar_module_result(display, detection.debug, font_scale=font_scale, thickness=thickness)


def erase_module_bars(frame_bgr, detection, padding=5):
    if detection is None:
        return frame_bgr
    result = detection.debug
    erased = frame_bgr.copy()
    for key in ("upper", "lower"):
        bar = result.get(key)
        if bar is None:
            continue
        center, size, angle = bar["rect"]
        w, h = size
        padded_rect = (center, (w + 2 * padding, h + 2 * padding), angle)
        box = cv2.boxPoints(padded_rect)
        cv2.fillConvexPoly(erased, np.round(box).astype(np.int32), (0, 0, 0))
    return erased
