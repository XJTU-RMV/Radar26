# -*- coding: utf-8 -*-
"""
Calibrate the Camera with Zhang Zhengyou Method.
Picture File Folder: "./pic/RGB_camera_calib_img/", Without Distortion. 

By You Zhiyuan, 2022.07.04, zhiyuanyou@foxmail.com
"""

import os
import sys
import argparse
from pathlib import Path

# 将项目根目录添加到路径
root_dir = Path(__file__).resolve().parent.parent.parent
print(root_dir)
sys.path.append(str(root_dir))

from callibrate.camera.calibrate_helper import Calibrator


def main():
    parser = argparse.ArgumentParser(description="相机内参标定工具")
    parser.add_argument("--sub", action="store_true", help="是否标定副相机 (camera_for_laser)")
    args = parser.parse_args()

    camera_type = "sub_camera" if args.sub else "main_camera"
    
    # 根据相机类型选择对应的图片文件夹
    if args.sub:
        img_folder = "sub_camera" # 假设副相机图片放在这里
    else:
        img_folder = "main_camera"

    # 路径使用相对于项目根目录的绝对路径，更可靠
    img_dir = str(root_dir / "callibrate" / "camera"/ "pic" / img_folder)
    
    if not os.path.exists(img_dir):
        print(f"[ERROR] 找不到图片目录: {img_dir}")
        return

    shape_inner_corner = (11, 8)
    size_grid = 0.025
    
    print(f"\n--- 正在标定 {'副相机' if args.sub else '主相机'} ({camera_type}) ---")
    print(f"图片目录: {img_dir}")

    # create calibrator
    calibrator = Calibrator(img_dir, shape_inner_corner, size_grid)
    # calibrate the camera
    mat_intri, coff_dis = calibrator.calibrate_camera(camera_type=camera_type)

if __name__ == '__main__':
    main()
