from __future__ import annotations

import cv2
import numpy as np

from lisar.common.types import TargetDetection
from lisar.utils.get_angle import cal_angle
from model.yolo26 import Stage3Detector


def load_stage3_detector_config(config):
    cfg = config.get("stage3_detector", {})
    return {
        "model_path": cfg.get("model_path", "weights/stage3.engine"),
        "img_size": int(cfg.get("img_size", 640)),
        "conf_thres": float(cfg.get("conf_thres", 0.25)),
        "iou_thres": float(cfg.get("iou_thres", 0.45)),
        "max_det": int(cfg.get("max_det", 1)),
        "device": cfg.get("device", config.get("device", "cuda")),
    }


class Yolo26TargetDetector:
    def __init__(
        self,
        model_path="weights/stage3.engine",
        img_size=640,
        conf_thres=0.25,
        iou_thres=0.45,
        max_det=1,
        device="cuda",
        detector=None,
        camera_K=None,
        dist_coeffs=None,
    ):
        self.img_size = int(img_size)
        self.clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        self.detector = detector or Stage3Detector(
            model_path=model_path,
            img_size=img_size,
            conf_thres=conf_thres,
            iou_thres=iou_thres,
            max_det=max_det,
            device=device,
        )
        self.camera_K = None if camera_K is None else np.array(camera_K, dtype=np.float64).reshape(3, 3)
        self.dist_coeffs = None if dist_coeffs is None else np.asarray(dist_coeffs, dtype=np.float64).flatten()

    def detect(self, frame_bgr, context=None):
        model_bgr = cv2.resize(frame_bgr, (self.img_size, self.img_size), interpolation=cv2.INTER_AREA)
        enhanced_bgr = self._enhance_frame(model_bgr)
        detections, raw_result = self.detector.predict(enhanced_bgr)
        if not detections:
            return None

        frame_shape = frame_bgr.shape[:2]
        model_shape = enhanced_bgr.shape[:2]
        cls, bbox, conf = max(detections, key=lambda item: item[2])
        x1, y1, x2, y2 = self._scale_bbox(bbox, frame_shape, model_shape)
        center = (int(round((x1 + x2) / 2.0)), int(round((y1 + y2) / 2.0)))
        world_angle = self._pixel_to_world_angle(center, context)
        return TargetDetection(
            center=center,
            bbox=(x1, y1, x2, y2),
            confidence=float(conf),
            source="yolo26_stage3",
            debug={
                "cls": int(cls),
                "detections": [
                    (raw_cls, list(self._scale_bbox(raw_bbox, frame_shape, model_shape)), raw_conf)
                    for raw_cls, raw_bbox, raw_conf in detections
                ],
                "model_center": self._bbox_center(bbox),
                "model_bbox": bbox,
                "model_detections": detections,
                "raw_result": raw_result,
                "world_angle": world_angle,
            },
        )

    def _enhance_frame(self, frame_bgr):
        lab = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        l_enhanced = self.clahe.apply(l)
        enhanced_lab = cv2.merge((l_enhanced, a, b))
        return cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)

    def _scale_bbox(self, bbox, frame_shape, model_shape):
        frame_h, frame_w = frame_shape
        model_h, model_w = model_shape
        sx = frame_w / model_w
        sy = frame_h / model_h
        x1, y1, x2, y2 = bbox
        return (
            int(round(x1 * sx)),
            int(round(y1 * sy)),
            int(round(x2 * sx)),
            int(round(y2 * sy)),
        )

    def _bbox_center(self, bbox):
        x1, y1, x2, y2 = bbox
        return int(round((x1 + x2) / 2.0)), int(round((y1 + y2) / 2.0))

    def _pixel_to_world_angle(self, center, context):
        if self.camera_K is None or self.dist_coeffs is None or context is None:
            return None
        current_angle = context.get("current_angle")
        if current_angle is None:
            return None

        yaw_relate_cam, pitch_relate_cam = cal_angle(
            self.camera_K,
            self.dist_coeffs,
            float(center[0]),
            float(center[1]),
            verbose=False,
        )
        return float(current_angle[0] + yaw_relate_cam), float(current_angle[1] + pitch_relate_cam)
