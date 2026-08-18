from model.mobilenet.predictor import DigitClassifier
import PIL


class_names = [
    "R1", "R2", "R3", "R4", "R7",
    "B1", "B2", "B3", "B4", "B7",
    "G1", "G2", "G3", "G4", "G7",
]


class TwoStepArmorDetectorClassifier:
    def __init__(self, armor_detector_model, digit_classifier_model):
        self.armor_detector_model = armor_detector_model
        self.digit_classifier = digit_classifier_model

    @classmethod
    def from_config(cls, config):
        from model.yolo26.predictor import Predictor

        original_armor_detector = Predictor(
            model_path=config["armor_detector"]["weights_path"],
            img_size=config["armor_detector"]["img_size"],
            max_det=config["armor_detector"]["max_det"],
            conf_thres=config["armor_detector"]["conf_thres"],
            iou_thres=config["armor_detector"]["iou_thres"],
        )
        digit_classifier = DigitClassifier(
            model_type=config["armor_detector"]["digit_model_type"],
            weights_path=config["armor_detector"]["digit_weights_path"],
        )

        return TwoStepArmorDetectorClassifier(
            armor_detector_model=original_armor_detector,
            digit_classifier_model=digit_classifier,
        )

    def predict_batch(self, imgs):
        raw_detections_list, annotated_images_list = self.armor_detector_model.predict_batch(imgs)

        all_armor_crops = []
        all_detection_info = []
        for img_idx, (img, raw_detections) in enumerate(zip(imgs, raw_detections_list)):
            if not raw_detections:
                continue

            for detection in raw_detections:
                color_id, xyxy, confidence = detection
                x1, y1, x2, y2 = map(int, xyxy)
                crop = img[y1:y2, x1:x2]
                if crop.size > 0:
                    all_armor_crops.append(crop)
                    all_detection_info.append((img_idx, xyxy, confidence, color_id))

        enhanced_detections_list = [[] for _ in imgs]
        if all_armor_crops:
            pattern_indexes, digit_confs = self.digit_classifier.predict_batch(
                [PIL.Image.fromarray(img).convert("RGB") for img in all_armor_crops],
                return_names=False,
            )
            for (img_idx, xyxy, yolo_conf, color_id), pattern_id, digit_conf in zip(
                all_detection_info, pattern_indexes, digit_confs
            ):
                if pattern_id == 5:
                    continue
                if color_id == 0:
                    armor_id = pattern_id + 10
                elif color_id == 1:
                    armor_id = pattern_id
                else:
                    armor_id = pattern_id + 5

                enhanced_detections_list[img_idx].append((armor_id, xyxy, max(digit_conf)))

        return enhanced_detections_list, annotated_images_list

    def predict(self, img):
        detections_list, annotated_images_list = self.predict_batch([img])
        return detections_list[0], annotated_images_list[0]
