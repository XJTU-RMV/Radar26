import cv2
import numpy as np
import yaml
import argparse
import os
import sys
import xml.etree.ElementTree as ET
import json
import re
from pathlib import Path

# 将项目根目录添加到路径
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

from driver.hik_camera.hik import SimpleHikCamera
from utils.config import load_cfg_from_cfg_file

def parse_pp_file(pp_path):
    """解析 .pp 文件获取 3D 世界坐标"""
    tree = ET.parse(pp_path)
    root = tree.getroot()
    points = []
    # 按 name 排序确保顺序一致
    point_elements = sorted(root.findall('point'), key=lambda x: int(x.get('name')))
    for pt in point_elements:
        x = float(pt.get('x'))
        y = float(pt.get('y'))
        z = float(pt.get('z'))
        points.append([x, y, z])
    return np.array(points, dtype=np.float32)

class ExtrinsicCalibrator:
    def __init__(self, config, world_points):
        self.config = config
        self.world_points = world_points
        self.image_points = []
        self.img = None
        self.win_name = "Extrinsic Calibration"
        
        # 窗口显示尺寸
        self.win_w = 1600
        self.win_h = 1000
        
        # 缩放与拖拽状态
        self.scale = 1.0
        self.offset = [0, 0]
        self.is_dragging = False
        self.last_mouse = [0, 0]
        
    def set_camera(self, camera_type="camera"):
        """切换当前标定的相机类型"""
        self.camera_type = camera_type
        # 缓存文件路径
        self.cache_path = root_dir / "config" / f"last_marked_points_{camera_type}.json"
        self.image_points = []
        self.load_points() # 尝试加载历史点
        
        # 加载内参
        camera_cfg = self.config[camera_type]
        self.K = np.array(camera_cfg['K']).reshape(3, 3)
        self.D = np.array(camera_cfg['dist_coeffs'])
        
        cv2.setWindowTitle(self.win_name, f"Extrinsic Calibration - {camera_type}")

    def save_points(self):
        """保存标记点到 json"""
        try:
            with open(self.cache_path, 'w') as f:
                json.dump(self.image_points, f)
            print(f"[INFO] {self.camera_type} 标记点已保存至: {self.cache_path}")
        except Exception as e:
            print(f"[ERROR] 保存标记点失败: {e}")

    def load_points(self):
        """加载历史标记点"""
        if self.cache_path.exists():
            try:
                with open(self.cache_path, 'r') as f:
                    self.image_points = json.load(f)
                print(f"[INFO] 已自动加载 {self.camera_type} 上次标记的 {len(self.image_points)} 个点")
            except:
                self.image_points = []

    def get_display_img(self):
        """根据当前缩放和偏移生成显示的图像"""
        M = np.float32([[self.scale, 0, self.offset[0]], [0, self.scale, self.offset[1]]])
        display_img = cv2.warpAffine(self.img, M, (self.win_w, self.win_h))
        
        # 绘制标记
        for idx, pt in enumerate(self.image_points):
            px = int(pt[0] * self.scale + self.offset[0])
            py = int(pt[1] * self.scale + self.offset[1])
            if 0 <= px < self.win_w and 0 <= py < self.win_h:
                cv2.circle(display_img, (px, py), 6, (0, 255, 0), -1)
                cv2.putText(display_img, f"P{idx}", (px + 12, py),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        # 状态栏
        status = f"[{self.camera_type}] Points: {len(self.image_points)}/{len(self.world_points)} | Zoom: {self.scale:.2f}x"
        cv2.putText(display_img, status, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        return display_img

    def mouse_callback(self, event, x, y, flags, param):
        orig_x = (x - self.offset[0]) / self.scale
        orig_y = (y - self.offset[1]) / self.scale

        if event == cv2.EVENT_LBUTTONDOWN:
            if not (flags & cv2.EVENT_FLAG_CTRLKEY):
                if len(self.image_points) < len(self.world_points):
                    self.image_points.append([orig_x, orig_y])
                    self.save_points() # 每次点击都自动保存
            else:
                self.is_dragging = True
                self.last_mouse = [x, y]
        elif event == cv2.EVENT_LBUTTONUP:
            self.is_dragging = False
        elif event == cv2.EVENT_MOUSEMOVE:
            if self.is_dragging:
                self.offset[0] += x - self.last_mouse[0]
                self.offset[1] += y - self.last_mouse[1]
                self.last_mouse = [x, y]
        elif event == cv2.EVENT_MOUSEWHEEL:
            old_scale = self.scale
            self.scale *= 1.15 if flags > 0 else (1/1.15)
            self.scale = max(self.scale, 0.1)
            self.offset[0] = x - (x - self.offset[0]) * (self.scale / old_scale)
            self.offset[1] = y - (y - self.offset[1]) * (self.scale / old_scale)

    def update_config(self, R, t, camera_type="camera"):
        """精准替换 params.yaml 中的 R 和 t，完全保留注释和格式"""
        config_path = root_dir / "config" / "params.yaml"
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # 格式化矩阵为漂亮的 YAML 字符串
            def format_matrix(mat, name, indent=2):
                mat_list = mat.tolist()
                s = f"{name}: [\n"
                rows = []
                indent_str = " " * (indent + 4)
                for row in mat_list:
                    row_str = indent_str + "[" + ", ".join([f"{v:.8f}" for v in row]) + "]"
                    rows.append(row_str)
                s += ",\n".join(rows) + "]"
                return s

            new_r_block = format_matrix(R, "R")
            new_t_block = format_matrix(t, "t")

            new_lines = []
            in_target_block = False
            skip_until_next_key = False
            
            # 根据相机类型确定目标块的起始关键字
            target_key = "camera:" if camera_type == "camera" else "camera_for_laser:"

            for line in lines:
                stripped = line.strip()
                
                # 检测是否进入目标相机块
                if stripped.startswith(target_key):
                    in_target_block = True
                    new_lines.append(line)
                    continue
                
                # 如果在目标块内
                if in_target_block:
                    # 如果遇到顶级 key (非缩进且不是注释)，说明该块结束
                    if line.strip() and not line.startswith(" ") and not line.startswith("#"):
                        in_target_block = False
                    
                    # 匹配 R: 或 t:
                    if stripped.startswith("R:"):
                        new_lines.append(f"  {new_r_block}\n")
                        skip_until_next_key = True
                        continue
                    if stripped.startswith("t:"):
                        new_lines.append(f"  {new_t_block}\n")
                        skip_until_next_key = True
                        continue
                    
                    # 跳过旧矩阵的多行内容
                    if skip_until_next_key:
                        if ":" in stripped and not stripped.startswith("["):
                            skip_until_next_key = False
                        else:
                            continue

                new_lines.append(line)

            with open(config_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            
            print(f"\n[OK] {camera_type} 外参已成功写入: {config_path}")

        except Exception as e:
            print(f"[ERROR] 更新配置文件失败: {e}")

    def run_calibration(self, image, camera_type="camera"):
        self.img = image
        # 先创建窗口，再调用 set_camera (因为 set_camera 会设置窗口标题)
        cv2.namedWindow(self.win_name, cv2.WINDOW_AUTOSIZE)
        self.set_camera(camera_type)
        
        img_h, img_w = image.shape[:2]
        self.scale = min(self.win_w/img_w, self.win_h/img_h)
        self.offset = [(self.win_w - img_w*self.scale)/2, (self.win_h - img_h*self.scale)/2]

        cv2.setMouseCallback(self.win_name, self.mouse_callback)
        
        print(f"\n--- [{camera_type}] 操作提示: 'c'计算, 's'保存点, 'r'重置, 'q'退出 ---")
        
        success_calib = False
        while True:
            cv2.imshow(self.win_name, self.get_display_img())
            key = cv2.waitKey(10) & 0xFF
            if key == ord('c'):
                if len(self.image_points) == len(self.world_points):
                    success, rvec, tvec = cv2.solvePnP(self.world_points, np.array(self.image_points, dtype=np.float32), self.K, self.D)
                    if success:
                        R, _ = cv2.Rodrigues(rvec)
                        
                        # 计算重投影误差
                        points2d_reproj, _ = cv2.projectPoints(
                            self.world_points, rvec, tvec, self.K, self.D
                        )
                        points2d_reproj = points2d_reproj.reshape(-1, 2)
                        img_pts_arr = np.array(self.image_points, dtype=np.float32)
                        error = np.sqrt(np.mean(np.sum((img_pts_arr - points2d_reproj)**2, axis=1)))
                        
                        print("\n" + "="*50)
                        print(f" {camera_type} 标定成功！")
                        print("="*50)
                        print(f"平均重投影误差: {error:.4f} 像素 (建议 < 2.0)")
                        print("-"*50)
                        print("旋转矩阵 R:")
                        print(R)
                        print("\n平移向量 t:")
                        print(tvec)
                        print("="*50)
                        
                        self.update_config(R, tvec, camera_type=camera_type)
                        success_calib = True
                        break
                else:
                    print(f"提示: 还差 {len(self.world_points)-len(self.image_points)} 个点")
            elif key == ord('s'):
                self.save_points()
            elif key == ord('r'):
                self.image_points = []
                # 重置时不退出循环，只是清空点
                print(f"[INFO] {camera_type} 标记点已重置")
            elif key == ord('q'):
                break
        cv2.destroyAllWindows()
        return success_calib

def main():
    parser = argparse.ArgumentParser(description="雷达站相机外参标定工具")
    parser.add_argument("--image", type=str, help="指定本地测试图像路径（若不指定则使用海康相机）")
    parser.add_argument("--pp", type=str, help="CloudCompare 导出的 .pp 文件路径 (默认使用 params.yaml 中的配置)")
    parser.add_argument("--sub", action="store_true", help="是否同时标定副相机")
    args = parser.parse_args()

    # 1. 加载配置
    config_path = root_dir / "config" / "params.yaml"
    config = load_cfg_from_cfg_file(str(config_path))

    # 2. 解析世界坐标
    pp_file = args.pp if args.pp else config.get("transform", {}).get("keypoints_file")
    if not pp_file:
        print("错误: 未指定 .pp 文件，且 params.yaml 中未配置 keypoints_file")
        return

    pp_path = root_dir / pp_file
    if not pp_path.exists():
        print(f"错误: 找不到点文件 {pp_path}")
        return
    world_points = parse_pp_file(pp_path)
    print(f"成功从 {pp_file} 加载了 {len(world_points)} 个参考点")

    # 3. 执行标定
    calibrator = ExtrinsicCalibrator(config, world_points)
    
    # --- 主相机标定 ---
    img_main = None
    if args.image:
        img_main = cv2.imread(args.image)
    else:
        print("\n[STEP 1] 正在获取主相机画面...")
        try:
            camera = SimpleHikCamera(config['camera'], camera_role="main")
            camera.start_streaming()
            camera.register_group("calib")
        
            for _ in range(15):
                camera.set_exposure(50000)
                img_rgb, _ = camera.get_image_latest("calib", timeout=1)
            camera.close()
            if img_rgb is not None:
                img_main = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
        except Exception as e:
            print(f"主相机启动失败: {e}")
            return

    if img_main is not None:
        success = calibrator.run_calibration(img_main, camera_type="camera")
        
        # --- 副相机标定 (如果指定了 --sub 且主相机标定成功) ---
        if success and args.sub:
            print("\n[STEP 2] 准备标定副相机...")
            img_sub = None
            if args.image:
                # 如果是本地图像，副相机可能需要另一个路径，这里简单处理或提示
                print("[WARN] 本地图像模式下暂不支持自动切换副相机图像，请手动指定或使用实时相机。")
            else:
                try:
                    camera_sub = SimpleHikCamera(config['camera_for_laser'], camera_role="sub")
                    camera_sub.start_streaming()
                    camera_sub.register_group("calib")
                    for _ in range(15):
                        camera_sub.set_exposure(90000)
                        img_rgb_sub, _ = camera_sub.get_image_latest("calib", timeout=1)
                    camera_sub.close()
                    if img_rgb_sub is not None:
                        img_sub = cv2.cvtColor(img_rgb_sub, cv2.COLOR_RGB2BGR)
                except Exception as e:
                    print(f"副相机启动失败: {e}")
            
            if img_sub is not None:
                calibrator.run_calibration(img_sub, camera_type="camera_for_laser")
    else:
        print("获取主相机画面失败。")

if __name__ == "__main__":
    main()
