import cv2
import numpy as np
import time
from pathlib import Path

from ruamel.yaml import YAML
from driver.hik_camera.hik import SimpleHikCamera
from utils.config import load_cfg_from_cfg_file

# 用于存储点击的坐标
clicked_point = None
display_size = None
raw_image_size = None


def get_screen_size():
    import tkinter as tk

    root = tk.Tk()
    root.withdraw()
    width = int(root.winfo_screenwidth())
    height = int(root.winfo_screenheight())
    root.destroy()
    return width, height


def fit_image_to_screen(image, screen_size, margin=120):
    screen_w, screen_h = screen_size
    img_h, img_w = image.shape[:2]
    max_w = max(screen_w - margin, 1)
    max_h = max(screen_h - margin, 1)
    scale = min(max_w / img_w, max_h / img_h, 1.0)

    if scale >= 1.0:
        return image, 1.0

    resized = cv2.resize(
        image,
        (int(round(img_w * scale)), int(round(img_h * scale))),
        interpolation=cv2.INTER_AREA,
    )
    return resized, scale

def mouse_callback(event, x, y, flags, param):
    global clicked_point, display_size, raw_image_size
    if event == cv2.EVENT_LBUTTONDOWN:
        if display_size is None or raw_image_size is None:
            return

        display_w, display_h = display_size
        raw_w, raw_h = raw_image_size
        if display_w <= 0 or display_h <= 0:
            return

        scale_x = raw_w / display_w
        scale_y = raw_h / display_h
        orig_x = int(round(x * scale_x))
        orig_y = int(round(y * scale_y))
        orig_x = max(0, min(orig_x, raw_w - 1))
        orig_y = max(0, min(orig_y, raw_h - 1))
        clicked_point = (orig_x, orig_y)
        print(f"已记录标定点: x={orig_x}, y={orig_y}")


def save_laser_center_to_params(clicked_point):
    config_path = Path(__file__).resolve().parent.parent / "config" / "params.yaml"
    if not config_path.exists():
        raise FileNotFoundError(f"未找到配置文件: {config_path}")

    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.width = 4096

    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.load(f)

    if data is None:
        data = {}
    if "laser" not in data or data["laser"] is None:
        data["laser"] = {}

    data["laser"]["center"] = {
        "pixel_x": int(clicked_point[0]),
        "pixel_y": int(clicked_point[1]),
    }

    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f)

    return config_path

def main():
    global clicked_point, display_size, raw_image_size
    
    # 1. 加载配置
    try:
        config = load_cfg_from_cfg_file("config/params.yaml")
        sub_cfg = config.get("sub_camera", config.sub_camera)
    except Exception as e:
        print(f"加载配置失败: {e}")
        return

    # 2. 初始化副相机
    print("正在启动副相机...")
    cam = SimpleHikCamera(sub_cfg, camera_role="sub")
    
    cam.start_streaming()
    cam.register_group("calibrate")

    time.sleep(2)
    cam.set_exposure(50000)
    print("\n--- 激光位置标定程序 ---")
    print("1. 请确保激光已打开并照射在某个物体上。")
    print("2. 在弹出的窗口中，用鼠标左键点击激光点的中心。")
    print("3. 点击后按 's' 保存并退出，按 'q' 直接退出。")

    screen_size = get_screen_size()
    cv2.namedWindow("Calibrate Laser Position", cv2.WINDOW_AUTOSIZE)
    cv2.setMouseCallback("Calibrate Laser Position", mouse_callback)

    try:
        while True:
            # 获取最新图像
            img_rgb, _ = cam.get_image_latest("calibrate", timeout=1.0)
            if img_rgb is None:
                continue

            # 转换为 BGR 用于 OpenCV 显示
            display_img = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
            raw_h, raw_w = display_img.shape[:2]
            raw_image_size = (raw_w, raw_h)

            # 如果已经点击了，画一个十字准星
            if clicked_point:
                x, y = clicked_point
                cv2.drawMarker(display_img, (x, y), (0, 0, 255), cv2.MARKER_CROSS, 20, 2)
                cv2.putText(display_img, f"Selected: ({x}, {y})", (x + 10, y - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1)

            display_img, _ = fit_image_to_screen(display_img, screen_size)
            display_h, display_w = display_img.shape[:2]
            display_size = (display_w, display_h)
            cv2.imshow("Calibrate Laser Position", display_img)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                print("用户取消标定。")
                break
            elif key == ord('s'):
                if clicked_point:
                    save_path = save_laser_center_to_params(clicked_point)
                    print(f"\n标定成功！结果已保存至: {save_path}")
                    break
                else:
                    print("请先点击图像中的激光点再保存！")

    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        cam.close()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
