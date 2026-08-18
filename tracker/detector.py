import argparse
from typing import List, Optional, Tuple
import numpy as np
import cv2
import time
import os
import sys
import os
from pathlib import Path
from loguru import logger


from utils.config import load_cfg_from_cfg_file
from transform.ray_renderer import PixelToWorld

# 添加 scripts 目录到路径以便导入
sys.path.append(os.path.join(os.path.dirname(__file__), '../driver/motor/scripts'))
try:
    from driver.motor.scripts.controller import GimbalController
except ImportError:
    logger.warning("GimbalController 导入失败，请检查路径")
from pathlib import Path
import sys
try:
    from tracker.type import TrackingState, SingleDetectionResult
except ImportError:
    from type import TrackingState, SingleDetectionResult
from model.yolo26.armor_detector import TwoStepArmorDetectorClassifier
from model.yolo26.predictor_with_tracker import PredictorWithTracker

# 在导入任何 Qt 相关模块之前设置 Qt 插件路径
# 确保 PyQt5 的插件路径优先级高于 OpenCV 的插件路径
# for site_package in sys.path:
#     if 'site-packages' in site_package:
#         pyqt5_plugin_path = Path(site_package) / 'PyQt5' / 'Qt5' / 'plugins'
#         if pyqt5_plugin_path.exists():
#             os.environ["QT_PLUGIN_PATH"] = str(pyqt5_plugin_path)
#             os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = str(pyqt5_plugin_path)
#             break

class_name = ["R1", "R2", "R3", "R4", "R7", "B1", "B2", "B3", "B4", "B7","RA","BA"] # 添加了两个无人机的追踪
class_id = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 15, 16]

class BaseDetector:
    @staticmethod
    def _make_scoped_bot_id(source: str, track_id) -> str:
        """Avoid bot ID collisions across independent detector trackers."""
        return f"{source}:{track_id}"

    def __init__(self, config, pixel_world_transform, visualize=False):
        super().__init__()
        self.device = config["device"]
        self.class_names = config["class_names"]
        self.config = config
        self.faction = config.get("faction", "red")

        # 一阶段先检测车
        self.car_detector = PredictorWithTracker(
            model_path=config["car_detector"]["weights_path"],
            img_size=config["car_detector"]["img_size"],
            max_det=config["car_detector"]["max_det"],
            conf_thres=config["car_detector"]["conf_thres"],
            iou_thres=config["car_detector"]["iou_thres"],
            tracker_config_path=config["car_detector"]["tracker_config_path"],
        )

        # 二阶段检测装甲板，分两步
        self.armor_detector = TwoStepArmorDetectorClassifier.from_config(config)

        # 无人机检测器
        # self.aircraft_detector = PredictorWithTracker(
        #     model_path=config["aircraft_detector"]["weights_path"],
        #     img_size=config["aircraft_detector"]["img_size"],
        #     max_det=config["aircraft_detector"]["max_det"],
        #     conf_thres=config["aircraft_detector"]["conf_thres"],
        #     iou_thres=config["aircraft_detector"]["iou_thres"],
        #     tracker_config_path=config["aircraft_detector"]["tracker_config_path"],
        # )

        self.pixel_world_transform = pixel_world_transform
        self.visualize = visualize

        # 初始化激光补偿参数 (从 params.yaml 的 laser 部分加载)
        laser_cfg = config.get("laser", {})
        self.laser_bias_yaw = laser_cfg.get("bias_yaw", 0.0)
        self.laser_bias_pitch = laser_cfg.get("bias_pitch", 0.0)
        
    
    def get_pos3d_only(self, pixel):
        """仅获取 3D 坐标"""
        pos = self.pixel_world_transform.get_hit_point(pixel)
        return pos.tolist() if pos is not None else [0.0, 0.0, 0.0]

    def xyxy2pos3d(self, xyxy):
        x1, y1, x2, y2 = xyxy
        # 默认使用底边中点（用于车辆定位）
        xo, yo = (x1 + x2) * 0.5, y2
        return self.get_pos3d_only([xo, yo])

    def aircraftpos3d(self, xyxy, is_enemy):
        """解耦后的无人机定位与瞄准逻辑"""
        x1, y1, x2, y2 = xyxy
        
        # 敌方偏右 (x2+10)，己方偏左 (x1-10)
        pos_pixel = [x2 + 10, (y1 + y2) / 2] if is_enemy else [x1 - 10, (y1 + y2) / 2]
        position_3d = self.get_pos3d_only(pos_pixel)
        
        return position_3d

    def _get_aircraft_class_id(self, xyxy, img_width, img_height):
        """
        根据己方阵容(self.faction)和无人机的敌我关系判断。
        红方无人机 RA: class_id = 15
        蓝方无人机 BA: class_id = 16
        
        逻辑：
        - 如果我方是红方("red"):
            - 敌方无人机 -> 蓝方无人机 (16)
            - 己方无人机 -> 红方无人机 (15)
        - 如果我方是蓝方("blue"):
            - 敌方无人机 -> 红方无人机 (15)
            - 己方无人机 -> 蓝方无人机 (16)
        """
        x1, y1, x2, y2 = xyxy
        center_x, center_y = (x1 + x2) / 2, (y1 + y2) / 2
        
        # 根据目标在左上角还是右上角判断是敌方还是己方
        dist_enemy = np.sqrt((center_x - img_width)**2 + (center_y - 0)**2)
        dist_our = np.sqrt((center_x - 0)**2 + (center_y - img_height)**2)
        is_enemy = dist_enemy < dist_our
        
        if self.faction == "red":
            return 16 if is_enemy else 15, is_enemy
        else: # blue
            return 15 if is_enemy else 16, is_enemy

    def detect(self, img) -> Tuple[List[SingleDetectionResult], Optional[np.ndarray]]:
        """
        Preform full detection pipeline on the input image.
        Args:
            img: Input image in BGR format.
        Returns:
            A tuple containing a list of detection results and an optional image with visualizations.
        """
        detections = []
        img_copy = img
        start_time = time.time() 
        
        # 1. 检测无人机
        # enermy_aircraft_count = 0
        # our_aircraft_count = 0
        # aircraft_results, _ = self.aircraft_detector.predict(img_copy) # [(cls, [x1, y1, x2, y2], conf, track_id)...], None
        # img_h, img_w = img_copy.shape[:2]
        # if(len(aircraft_results) != 0): # 如果没有检测到，应该继续检测车
        #     # 如果检测到了，要返回无人机的3D坐标，并且进一步检测激光检测模块
        #     for aircraft_result in aircraft_results:
        #         _, xyxy, conf, track_id = aircraft_result
        #         scoped_bot_id = self._make_scoped_bot_id("aircraft", track_id)
        #         # 判断是己方还是敌方
        #         class_id, is_enemy = self._get_aircraft_class_id(xyxy, img_w, img_h)
        #         if is_enemy:
        #             enermy_aircraft_count += 1
        #         else:
        #             our_aircraft_count += 1
        #
        #         # 根据无人机阵容选择对应的投影方式
        #         position_3d = self.aircraftpos3d(xyxy, is_enemy)
        #
        #         detections.append(SingleDetectionResult(
        #             class_id=class_id,  # 15: 红方无人机， 16: 蓝方无人机
        #             class_conf=conf,
        #             bot_id=scoped_bot_id,
        #             car_box=list(map(int, xyxy)),
        #             car_conf=conf,
        #             armor_box=[0.0, 0.0, 0.0, 0.0],
        #             pos_3d=position_3d,
        #             time_stamp=time.time(),
        #         ))

        # 2. 检测地面车辆
        car_detections, _ = self.car_detector.predict(img_copy) # [(cls, [x1, y1, x2, y2], conf, track_id)...], None
        if len(car_detections) == 0:
            # 如果没有地面车，返回原图缩放结果
            vis_img = None
            if self.visualize and len(detections) > 0:
                vis_img = self._get_visualized_img(img_copy, detections)
            return detections, vis_img if vis_img is not None else cv2.resize(img_copy,(1024, 768), interpolation=cv2.INTER_LINEAR)

        # logger.info(f"检测到{len(car_detections)}辆车, 我方无人机:{our_aircraft_count}, 敌方无人机:{enermy_aircraft_count}, 耗时{(time.time() - start_time):.4f}秒")

        crop_imgs = []
        for car_detection in car_detections:
            _, xyxy, conf, _ = car_detection
            x1, y1, x2, y2 = map(int, xyxy)
            # 边界检查
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(img_copy.shape[1], x2), min(img_copy.shape[0], y2)
            crop_img = img_copy[y1:y2, x1:x2]
            crop_imgs.append(crop_img)
            # cv2.imshow("crop_imgs", crop_img)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()
        
        # 3. 检测装甲板， TODO: 这里两辆车叠在一起容易误识别
        armor_detections, _ = self.armor_detector.predict_batch(crop_imgs) # 每辆车有一个列表 [ [(armor_id, bbox, conf), (armor_id, bbox, conf), ...], ... ]

        for armor_list, car_detection in zip(armor_detections, car_detections):
            _, car_box, car_conf, track_id = car_detection
            scoped_bot_id = self._make_scoped_bot_id("car", track_id)
            car_box = list(map(int, car_box))
            
            # 1. 默认先计算车辆底部的 3D 坐标（用于地图定位）
            position_3d_car = self.xyxy2pos3d(car_box)

            if len(armor_list) == 0:    # 未检测到装甲板，回退到车辆底边中点坐标
                detection_result = SingleDetectionResult(
                    class_id=-1,
                    class_conf=0.0,
                    bot_id=scoped_bot_id,
                    car_box=car_box,
                    armor_box=[0.0, 0.0, 0.0, 0.0],
                    car_conf=car_conf,
                    pos_3d=position_3d_car, # 相对世界坐标系
                    time_stamp=time.time(),
                )
                detections.append(detection_result)
                continue

            # 2. 检测到装甲板，使用最高置信度装甲板确定类别
            max_armor = max(armor_list, key=lambda x: x[2]) # 如果有多个，取置信度最高的一个
            class_id, armor_box, armor_conf = max_armor

            detection_result = SingleDetectionResult(
                class_id=class_id,
                class_conf=armor_conf,
                bot_id=scoped_bot_id,
                car_box=car_box,
                armor_box=list(map(int, armor_box)),
                car_conf=car_conf,
                pos_3d=position_3d_car, # 地图位置依然使用车辆底部的解算结果
                time_stamp=time.time(),
            )
            detections.append(detection_result)

        vis_img = None
        if self.visualize:
            vis_img = self._get_visualized_img(img_copy, detections)
        return detections, vis_img

    def _get_visualized_img(self, img, detections):
        vis_img = cv2.resize(img, (1024, 768), interpolation=cv2.INTER_LINEAR)
    
        # 计算缩放比例，用于调整边界框坐标
        original_height, original_width = img.shape[:2]
        scale_x = 1024 / original_width
        scale_y = 768 / original_height
        
        # 后续代码保持不变，但需要调整边界框坐标
        height, width = vis_img.shape[:2]  # 现在是768, 1024

        for detection in detections:
            # 1. 处理无人机显示 (class_id == 15 或 16)
            if detection.class_id in [15, 16]:
                x1, y1, x2, y2 = map(int, detection.car_box)
                x1, y1, x2, y2 = int(x1*scale_x), int(y1*scale_y), int(x2*scale_x), int(y2*scale_y)
                
                label = f"Aircraft: {detection.car_conf:.2f} "  # ID: {detection.bot_id}
                color = (255, 0, 255) # 紫色
                
                cv2.rectangle(vis_img, (x1, y1), (x2, y2), color, 2)
                cv2.putText(vis_img, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                
                # 如果开启了 3D 坐标显示 (无人机)
                # if self.show_3d and detection.pos_3d is not None:
                #     x, y, z = detection.pos_3d
                #     pos_label = f"({x:.1f}, {y:.1f}, {z:.1f})"
                #     angle_label = f"Y:{detection.yaw:.1f} P:{detection.pitch:.1f}"
                #     cv2.putText(
                #         vis_img,
                #         pos_label,
                #         (x1, y2 + 20),
                #         cv2.FONT_HERSHEY_SIMPLEX,
                #         0.5,
                #         (255, 255, 0), # 青色
                #         2,
                #     )
                #     cv2.putText(
                #         vis_img,
                #         angle_label,
                #         (x1, y2 + 40),
                #         cv2.FONT_HERSHEY_SIMPLEX,
                #         0.5,
                #         (0, 255, 255), # 黄色
                #         2,
                #     )
                continue

            # 2. 处理地面车辆显示
            x1_car, y1_car, x2_car, y2_car = map(int, detection.car_box)
            x1_car = int(x1_car * scale_x)
            y1_car = int(y1_car * scale_y)
            x2_car = int(x2_car * scale_x)
            y2_car = int(y2_car * scale_y)
            
            # 根据 class_id 确定车辆颜色
            class_id = detection.class_id
            if class_id >= 0:
                if class_id < 5:      # red (R1-R7)
                    color = (0, 0, 255)  # BGR 红色
                elif class_id < 10:   # blue (B1-B7)
                    color = (255, 0, 0)  # BGR 蓝色
                else:                 # grey (G1-G5)
                    color = (128, 128, 128)
            else:
                color = (0, 255, 0)   # 未识别到装甲板时，车辆用绿色

            label = f"Car: {detection.car_conf:.2f} "   # ID: {detection.bot_id}
            cv2.rectangle(vis_img, (x1_car, y1_car), (x2_car, y2_car), color, 2)
            cv2.putText(
                vis_img,
                label,
                (x1_car, y1_car - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                color,
                2,
            )

            # 如果开启了 3D 坐标显示
            # if self.show_3d and detection.pos_3d is not None:
            #     x, y, z = detection.pos_3d
            #     pos_label = f"({x:.1f}, {y:.1f}, {z:.1f})"
            #     angle_label = f"Y:{detection.yaw:.1f} P:{detection.pitch:.1f}"
            #     cv2.putText(
            #         vis_img,
            #         pos_label,
            #         (x1_car, y2_car + 20),
            #         cv2.FONT_HERSHEY_SIMPLEX,
            #         0.5,
            #         (255, 255, 0), # 青色
            #         2,
            #     )
            #     cv2.putText(
            #         vis_img,
            #         angle_label,
            #         (x1_car, y2_car + 40),
            #         cv2.FONT_HERSHEY_SIMPLEX,
            #         0.5,
            #         (0, 255, 255), # 黄色
            #         2,
            #     )

            # 装甲板
            if detection.class_id >= 0:
                x1_armor, y1_armor, x2_armor, y2_armor = map(int, detection.armor_box)
                x1_armor = int((x1_armor + detection.car_box[0]) * scale_x)
                y1_armor = int((y1_armor + detection.car_box[1]) * scale_y)
                x2_armor = int((x2_armor + detection.car_box[0]) * scale_x)
                y2_armor = int((y2_armor + detection.car_box[1]) * scale_y)

                if class_id < len(self.class_names):
                    label = f"{self.class_names[detection.class_id]}: {detection.class_conf:.2f}"
                else:
                    label = f"ID_{class_id}: {detection.class_conf:.2f}"

                cv2.rectangle(
                    vis_img, (x1_armor, y1_armor), (x2_armor, y2_armor), color, 2
                )
                cv2.putText(
                    vis_img,
                    label,
                    (x1_armor, y1_armor - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    color,
                    2,
                )
        return vis_img



def prepare_directory():
    current_file = Path(__file__).resolve()
    root_dir = current_file.parent.parent.parent
    
    # 打印调试信息，确认路径是否正确
    print(f"Current file: {current_file}")
    print(f"Root directory: {root_dir}")
    
    # 将根目录插入到 sys.path 的最前面，确保优先匹配根目录下的包
    if str(root_dir) not in sys.path:
        sys.path.insert(0, str(root_dir))
    
def process_frame(detector, gimbal, frame):
    # --- 指定追踪配置 ---
    # 你可以在这里修改想要追踪的 class_id
    # 例如: 0-4(红方车), 5-9(蓝方车), 15(红方无人机), 16(蓝方无人机)
    TRACK_TARGET_ID = 0  # <--- 修改这里来指定追踪的目标 ID
    # ------------------

    start_time = time.time()
    detections, vis_img = detector.detect(frame)
    
    # 筛选指定 ID 的目标
    target_to_track = None
    for d in detections:
        if d.class_id != -1:
            target_to_track = d
            break
    
    # 发送指令给云台 (如果串口已打开)
    if target_to_track is not None and gimbal is not None:
        print("追踪到")
        bias_yaw = detector.laser_bias_yaw
        bias_pitch = detector.laser_bias_pitch
        gimbal.set_angle(-target_to_track.yaw + bias_yaw, -target_to_track.pitch + bias_pitch)

    end_time = time.time()
    fps = 1.0 / (end_time - start_time)
    if vis_img is not None:
        # 在图像上绘制 FPS
        cv2.putText(vis_img, f"FPS: {fps:.2f}", (10, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow("Detector Test", vis_img)

def get_parser():
    parser = argparse.ArgumentParser(description="无追踪模式测试")
    parser.add_argument("--mode", default="video", choices=["camera", "video", "image"], help="detect mode for detector")
    parser.add_argument("--source", default="/home/wtz/桌面/video_save/哈工深-cliped.mp4", help="source video or image")
    parser.add_argument("--serial", action="store_true", help="是否打开串口进行云台控制")
    args = parser.parse_args()
    return args
    
if __name__ == "__main__":
    args = get_parser()
    prepare_directory()

    config = load_cfg_from_cfg_file( "config/params.yaml")
    pixel_world_transform = PixelToWorld.build_from_config(config)
    detector = BaseDetector(config, pixel_world_transform, visualize=True)
    
    # 根据参数决定是否初始化串口
    gimbal = None
    if args.serial:
        try:
            gimbal = GimbalController('/dev/ttyACM0', 115200)
            print("[INFO] Serial port opened successfully.")
        except Exception as e:
            print(f"[ERROR] Failed to open serial port: {e}")

    if args.mode == "camera":
        try:
            from driver.hik_camera.hik import SimpleHikCamera
            camera = SimpleHikCamera(config.main_camera, "main")
            camera.register_group("detector")
            camera.start_streaming()
            exposure = 80000
            time.sleep(1)
            camera.set_exposure(exposure)
            while(1):
                img_rgb, _ = camera.get_image_latest("detector", timeout=1)
                if img_rgb is None:
                    continue
                img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
                process_frame(detector, gimbal, img_bgr)
                
                key = cv2.waitKey(1) & 0xFF
                if key==ord('q'):
                    break
                elif key == ord('s'):
                    print("Paused. Press 'r' to resume.")
                    while True:
                        if cv2.waitKey(1) & 0xFF == ord('r'):
                            print("Resumed.")
                            break
        finally:
            camera.close()

    elif args.mode == "video":
        cap = cv2.VideoCapture(int(args.source) if args.source.isdigit() else args.source)
        if not cap.isOpened():
            print(f"Error: Could not open video: {args.source}")
        try:
            while True:
                ret, frame = cap.read()
                if not ret: break
                process_frame(detector, gimbal, frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'): 
                    break
                elif key == ord('s'):
                    print("Paused. Press 'r' to resume.")
                    while True:
                        if cv2.waitKey(1) & 0xFF == ord('r'):
                            print("Resumed.")
                            break
        finally:
            cap.release()
    
    else:

        img_path = str("demo/demo1.jpg")
        img = cv2.imread(img_path)
        if img is None:
            print(f"Error: Could not read image at {img_path}")
        else:
            # 注意：BaseDetector.detect 期望的是 BGR 还是 RGB？
            # 根据代码中的 cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 来看，通常期望 BGR
            result, vis_img = detector.detect(img)
            if vis_img is not None:
                cv2.imshow("Detection Result", vis_img)
                cv2.waitKey(0)
            else:
                print("No visualization returned.")
