"""
像素坐标转角度：相机预览 + 鼠标点击计算去畸变后的角度
参考 hik_camera，从 config/params.yaml 或指定 JSON/YAML 配置文件初始化相机和内参。
按 'q' 退出。左键点击图像任意点可计算该点的角度。
"""
import argparse
import json
import os
import random
import sys
import time

import cv2
import numpy as np
import yaml

from utils.config import CfgNode

# 用于随机颜色，与 C++ RNG(12345) 等效
random.seed(12345)


def cal_angle(cam: np.ndarray, dis: np.ndarray, x: float, y: float, verbose: bool = False) -> tuple:
    """
    根据像素坐标计算去畸变后的角度（度）

    Args:
        cam: 3x3 相机内参矩阵
        dis: 畸变系数 (k1, k2, p1, p2)
        x, y: 像素坐标
        verbose: 是否打印调试信息

    Returns:
        (angx_deg, angy_deg): 去畸变后的 x、y 方向角度（度）
    """
    fx = float(cam[0, 0])
    fy = float(cam[1, 1])
    cx = float(cam[0, 2])
    cy = float(cam[1, 2])

    pts_in = np.array([[[x, y]]], dtype=np.float32)
    pts_out = cv2.undistortPoints(pts_in, cam, dis, P=cam)
    pnt_x = float(pts_out[0, 0, 0])
    pnt_y = float(pts_out[0, 0, 1])

    rx = (pnt_x - cx) / fx
    ry = (pnt_y - cy) / fy

    angx_raw = np.degrees(np.arctan((x - cx) / fx))
    angy_raw = - np.degrees(np.arctan((y - cy) / fy))
    angx_new = np.degrees(np.arctan(rx))
    angy_new = - np.degrees(np.arctan(ry)) # pitch反向，符合我们设定的相机坐标系

    if verbose:
        print(f"undistorted point: {pts_out}")
        print(f"xscreen: {x}  xNew: {pnt_x}")
        print(f"yscreen: {y}  yNew: {pnt_y}")
        print(f"angx: {angx_raw:.4f}  angleNew: {angx_new:.4f}")
        print(f"angy: {angy_raw:.4f}  angleNew: {angy_new:.4f}")

    return angx_new, angy_new 


def _load_config(path: str):
    """从 YAML 或 JSON 配置文件加载，返回类 CfgNode 的 dict（支持 attr 访问）"""
    if not os.path.isfile(path):
        raise FileNotFoundError(f"配置文件不存在: {path}")

    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()

    if path.endswith(".json"):
        cfg_dict = json.loads(raw)
    elif path.endswith((".yaml", ".yml")):
        cfg_dict = yaml.safe_load(raw)
    else:
        raise ValueError(f"不支持的配置格式，请使用 .yaml 或 .json: {path}")

    from utils.config import CfgNode
    return CfgNode(cfg_dict)


def _camera_matrix_and_dist_from_config(camera_cfg) -> tuple:
    """从相机配置中提取 K 和 dist_coeffs"""
    K = np.array(camera_cfg.K, dtype=np.float64).reshape(3, 3)
    dist_coeffs = np.asarray(camera_cfg.dist_coeffs, dtype=np.float64).flatten()
    return K, dist_coeffs


def main():
    parser = argparse.ArgumentParser(description="像素坐标转角度，参考 hik_camera 从配置文件初始化")
    parser.add_argument(
        "--config",
        default="/home/wtz/桌面/RM2026/config/params.yaml",
        help="配置文件路径 (YAML 或 JSON)，内含 camera/sub_camera 的 K 和 dist_coeffs",
    )
    parser.add_argument(
        "--camera",
        choices=["main", "sub"],
        default="sub",
        help="使用主相机(main)或副相机(sub)，默认 sub",
    )
    args = parser.parse_args()

    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = args.config if os.path.isabs(args.config) else os.path.join(root, args.config)

    try:
        config = _load_config(config_path)
    except FileNotFoundError as e:
        print(f"错误: {e}")
        return

    # 选择相机配置
    if args.camera == "main":
        camera_cfg = config.main_camera
    else:
        camera_cfg = config.get("sub_camera", config.sub_camera)

    camera_matrix, dist_coeffs = _camera_matrix_and_dist_from_config(camera_cfg)
    print(f"已加载配置: {config_path} (camera={args.camera})")
    print(f"  分辨率: {camera_cfg.width}x{camera_cfg.height}")

    # 使用 SimpleHikCamera 初始化相机
    try:
        from driver.hik_camera.hik import SimpleHikCamera

        cam = SimpleHikCamera(camera_cfg, camera_role=args.camera)
        cam.start_streaming()
        cam.register_group("view")
        time.sleep(2.0)  # 等待流线程完成设备初始化
        cam.set_exposure(camera_cfg.exposure_time)
    except Exception as e:
        print(f"错误: 无法打开海康相机，{e}")
        return

    display_scale = 0.5

    # 鼠标回调用到的全局状态
    state = {
        "draw_rect": False,
        "left_pnt": (-1, -1),
        "mouse_pos": (-1, -1),
        "last_clicked": None,
    }

    def on_mouse(event, x, y, flags, userdata):
        orig_x = int(round(x / display_scale))
        orig_y = int(round(y / display_scale))
        if event == cv2.EVENT_LBUTTONDOWN:
            state["draw_rect"] = True
            state["left_pnt"] = (orig_x, orig_y)
            state["last_clicked"] = (orig_x, orig_y)
            cal_angle(camera_matrix, dist_coeffs, orig_x, orig_y, verbose=True)
        elif event == cv2.EVENT_MOUSEMOVE:
            state["mouse_pos"] = (orig_x, orig_y)
        elif event == cv2.EVENT_LBUTTONUP:
            state["draw_rect"] = False
            state["mouse_pos"] = (orig_x, orig_y)

    cv2.namedWindow("img")
    try:
        while True:
            org, _ = cam.get_image_latest("view", timeout=0.1)
            if org is None:
                continue

            # SimpleHikCamera 返回 RGB，cv2.imshow 期望 BGR
            temp1 = cv2.cvtColor(org, cv2.COLOR_RGB2BGR).copy()
            cv2.setMouseCallback("img", on_mouse)

            if state["last_clicked"] is not None:
                cx, cy = state["last_clicked"]
                cv2.circle(temp1, (cx, cy), 5, (0, 0, 255), -1)
                cv2.putText(temp1, f"({cx},{cy})", (cx + 8, cy), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

            if state["draw_rect"] and state["left_pnt"][0] >= 0:
                color = (
                    random.randint(0, 255),
                    random.randint(0, 255),
                    random.randint(0, 255),
                )
                cv2.rectangle(temp1, state["left_pnt"], state["mouse_pos"], color, 2)

            mx, my = state["mouse_pos"]
            if mx >= 0 and my >= 0:
                cv2.putText(temp1, f"({mx},{my})", (mx, my), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)

            display_img = cv2.resize(temp1, None, fx=display_scale, fy=display_scale)
            cv2.imshow("img", display_img)
            if cv2.waitKey(30) & 0xFF == ord("q"):
                break
    finally:
        cam.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
