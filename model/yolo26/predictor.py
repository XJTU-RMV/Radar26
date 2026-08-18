from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Any, Dict, Iterable, List, Optional, Tuple


DetectionTuple = Tuple[int, List[int], float]


def _load_yolo_class():
    package_root = Path(__file__).resolve().parent
    if str(package_root) not in sys.path:
        sys.path.insert(0, str(package_root))
    from ultralytics import YOLO

    return YOLO


@dataclass(frozen=True)
class Stage3Detection:
    cls: int
    bbox: Tuple[int, int, int, int]
    conf: float

    @property
    def center(self) -> Tuple[float, float]:
        x1, y1, x2, y2 = self.bbox
        return (x1 + x2) / 2.0, (y1 + y2) / 2.0

    def as_tuple(self) -> DetectionTuple:
        return self.cls, list(self.bbox), self.conf


class Stage3Detector:
    def __init__(
        self,
        model_path: str = "weights/stage3.engine",
        img_size: int = 640,
        conf_thres: float = 0.25,
        iou_thres: float = 0.45,
        max_det: int = 10,
        device: str = "cuda",
        class_names: Optional[Dict[int, str]] = None,
    ):
        self.model_path = model_path
        self.input_size = img_size
        self.conf_thres = conf_thres
        self.iou_thres = iou_thres
        self.max_det = max_det
        self.device = device
        self.class_names = class_names or {0: "target"}

        if not Path(model_path).exists():
            raise FileNotFoundError(f"YOLO26 stage3 weights not found: {model_path}")

        YOLO = _load_yolo_class()
        self.model = YOLO(model_path, task="detect")
        if Path(model_path).suffix != ".engine":
            self.model = self.model.to(self.device)
            self.model.eval()

    def predict(self, image: Any) -> Tuple[List[DetectionTuple], object]:
        detections, raw_result = self.detect(image)
        return [detection.as_tuple() for detection in detections], raw_result

    def detect(self, image: Any) -> Tuple[List[Stage3Detection], object]:
        if image is None or image.size == 0:
            raise ValueError("image must be a non-empty numpy array")

        results = self.model.predict(
            image,
            imgsz=self.input_size,
            conf=self.conf_thres,
            iou=self.iou_thres,
            max_det=self.max_det,
            verbose=False,
        )
        if not results:
            return [], None

        result = results[0]
        if result.boxes is None or len(result.boxes) == 0:
            return [], result

        detections = []
        for box in result.boxes:
            cls = int(box.cls[0].detach().cpu().item())
            conf = float(box.conf[0].detach().cpu().item())
            x1, y1, x2, y2 = box.xyxy[0].detach().cpu().numpy().tolist()
            detections.append(
                Stage3Detection(
                    cls=cls,
                    bbox=(int(round(x1)), int(round(y1)), int(round(x2)), int(round(y2))),
                    conf=conf,
                )
            )
        return detections, result

    def predict_batch(self, images: Iterable[Any]) -> Tuple[List[List[DetectionTuple]], None]:
        all_detections = []
        for image in images:
            detections, _ = self.predict(image)
            all_detections.append(detections)
        return all_detections, None

    def best_detection(self, image: Any) -> Tuple[Optional[Stage3Detection], object]:
        detections, raw_result = self.detect(image)
        if not detections:
            return None, raw_result
        return max(detections, key=lambda detection: detection.conf), raw_result

    def visualize_results(
        self,
        image: Any,
        detections: Iterable[DetectionTuple],
        class_names: Optional[Dict[int, str]] = None,
    ) -> Any:
        import cv2

        vis_image = image.copy()
        names = class_names or self.class_names
        for cls, bbox, conf in detections:
            x1, y1, x2, y2 = bbox
            label = f"{names.get(cls, f'class_{cls}')} {conf:.2f}"
            cv2.rectangle(vis_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                vis_image,
                label,
                (x1, max(20, y1 - 8)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2,
            )
        return vis_image


Predictor = Stage3Detector


if __name__ == "__main__":
    import argparse
    import cv2

    parser = argparse.ArgumentParser(description="YOLO26 stage3 detector smoke test")
    parser.add_argument("image", help="image path")
    parser.add_argument("--model", default="weights/stage3.engine")
    parser.add_argument("--save", default=None)
    args = parser.parse_args()

    detector = Stage3Detector(model_path=args.model)
    image_bgr = cv2.imread(args.image)
    detections, _ = detector.predict(image_bgr)
    print(detections)
    if args.save:
        cv2.imwrite(args.save, detector.visualize_results(image_bgr, detections))
