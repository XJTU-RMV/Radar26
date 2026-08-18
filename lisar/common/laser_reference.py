from __future__ import annotations

from lisar.common.types import LaserReferencePoint, Point
import cv2

from lisar.detect_lisar_dot import LisarDotDetector, X_MAX, X_MIN, Y_MAX, Y_MIN


class CalibratedLaserReference:
    def __init__(self, center: Point | None = None, config=None):
        if center is None:
            if config is None or not hasattr(config, "laser"):
                raise ValueError("calibrated laser reference needs center or config.laser.center")
            laser_center = config.laser.center
            center = (int(laser_center.pixel_x), int(laser_center.pixel_y))
        self.center = center

    def locate(self, frame_bgr, context=None):
        return LaserReferencePoint(self.center, predicted=False, source="calibrated")


class ObservedLaserDotReference:
    def __init__(self, allow_prediction=False):
        self.detector = LisarDotDetector()
        self.allow_prediction = bool(allow_prediction)

    def locate(self, frame_bgr, context=None):
        if self.allow_prediction:
            center, predicted = self.detector.detect(frame_bgr)
        else:
            center = self.detector._detect_single_frame(frame_bgr)
            predicted = False
        if center is None:
            return None
        return LaserReferencePoint(center, predicted=predicted, source="observed_dot")


def draw_laser_reference_roi(display, color=(0, 255, 255), thickness=2):
    cv2.rectangle(display, (X_MIN, Y_MIN), (X_MAX, Y_MAX), color, thickness)
