from __future__ import annotations

from pathlib import Path
from typing import Any, List, Tuple

import cv2

from model.yolo26.predictor import _load_yolo_class


TrackingDetectionTuple = Tuple[int, List[int], float, int]


class PredictorWithTracker:
    def __init__(
        self,
        model_path: str,
        img_size=1280,
        conf_thres=0.05,
        iou_thres=0.5,
        device="cuda",
        max_det=10,
        tracker_config_path: str = "config/bytetrack.yaml",
        visualize=False,
    ):
        self.model_path = model_path
        self.input_size = img_size
        self.conf_thres = conf_thres
        self.iou_thres = iou_thres
        self.device = device
        self.visualize = visualize
        self.max_det = max_det
        self.tracker_config_path = tracker_config_path

        if not Path(model_path).exists():
            raise FileNotFoundError(f"YOLO26 tracker weights not found: {model_path}")

        YOLO = _load_yolo_class()
        self.model = YOLO(model_path, task="detect")
        if Path(model_path).suffix != ".engine":
            self.model = self.model.to(self.device)
            self.model.eval()

    def predict(self, image: Any) -> Tuple[List[TrackingDetectionTuple], None]:
        if image is None or image.shape[0] == 0 or image.shape[1] == 0:
            raise ValueError("image must be a non-empty numpy array")

        results = self.model.track(
            image,
            imgsz=self.input_size,
            stream=False,
            persist=True,
            tracker=self.tracker_config_path,
            conf=self.conf_thres,
            iou=self.iou_thres,
            max_det=self.max_det,
            verbose=False,
        )[0]

        if results.boxes is None or len(results.boxes) == 0:
            return [], None

        detections = []
        img_area = image.shape[0] * image.shape[1]
        for box in results.boxes:
            if box.id is None:
                continue

            cls = int(box.cls[0].detach().cpu().item())
            conf = float(box.conf[0].detach().cpu().item())
            track_id = int(box.id[0].detach().cpu().item())
            x1, y1, x2, y2 = box.xyxy[0].detach().cpu().numpy().tolist()
            bbox = [int(round(x1)), int(round(y1)), int(round(x2)), int(round(y2))]

            box_area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
            if box_area > img_area / 7:
                continue
            if box_area < 10000:
                continue

            detections.append((cls, bbox, conf, track_id))

        return detections, None

    def visualize_results(self, image: Any, detections, class_names=None):
        vis_image = image.copy()
        names = class_names or {0: "car"}
        colors = [
            (255, 0, 0),
            (0, 255, 0),
            (0, 0, 255),
            (255, 255, 0),
            (255, 0, 255),
            (0, 255, 255),
        ]

        for cls_id, bbox, conf, track_id in detections:
            x1, y1, x2, y2 = bbox
            color = colors[cls_id % len(colors)]
            cv2.rectangle(vis_image, (x1, y1), (x2, y2), color, 2)
            label = f"{names.get(cls_id, f'Class_{cls_id}')}:{track_id} {conf:.2f}"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            cv2.rectangle(
                vis_image,
                (x1, y1 - label_size[1] - 10),
                (x1 + label_size[0], y1),
                color,
                -1,
            )
            cv2.putText(
                vis_image,
                label,
                (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                2,
            )

        return vis_image
