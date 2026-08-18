# -*- coding: utf-8 -*-
"""
Calibrate the Camera with Zhang Zhengyou Method.

By You Zhiyuan, 2022.07.04, zhiyuanyou@foxmail.com
"""

import os
import glob
from pathlib import Path

import cv2
import numpy as np
import yaml


class Calibrator(object):
    def __init__(self, img_dir, shape_inner_corner, size_grid, visualization=True):
        """
        --parameters--
        img_dir: the directory that save images for calibration, str
        shape_inner_corner: the shape of inner corner, Array of int, (h, w)
        size_grid: the real size of a grid in calibrator, float
        visualization: whether visualization, bool
        """
        self.img_dir = img_dir
        self.shape_inner_corner = shape_inner_corner
        self.size_grid = size_grid
        self.visualization = visualization
        self.mat_intri = None # intrinsic matrix
        self.coff_dis = None # cofficients of distortion

        # create the conner in world space
        w, h = shape_inner_corner
        # cp_int: corner point in int form, save the coordinate of corner points in world sapce in 'int' form
        # like (0,0,0), (1,0,0), (2,0,0) ...., (10,7,0)
        cp_int = np.zeros((w * h, 3), np.float32)
        cp_int[:,:2] = np.mgrid[0:w,0:h].T.reshape(-1,2)
        # cp_world: corner point in world space, save the coordinate of corner points in world space
        self.cp_world = cp_int * size_grid

        # images
        self.img_paths = []
        for extension in ["jpg", "png", "jpeg"]:
            self.img_paths += glob.glob(os.path.join(img_dir, "*.{}".format(extension)))
        assert len(self.img_paths), "No images for calibration found!"


    def update_config(self, mat_intri, coff_dis, camera_type="camera"):
        """精准替换 params.yaml 中的 K 和 dist_coeffs，完全保留注释 and 格式"""
        try:
            # 文件在 callibrate/ 下，向上二级到达项目根目录
            config_path = Path(__file__).resolve().parent.parent.parent / "config" / "params.yaml"
            if not config_path.exists():
                print(f"\n[WARNING] 未找到配置文件: {config_path}，跳过自动更新。")
                return

            with open(config_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # 格式化 K (3x3 矩阵)
            k_list = mat_intri.flatten().tolist()
            k_str = "K: [" + ", ".join([f"{v:.8f}" for v in k_list]) + "]"
            
            # 格式化 dist_coeffs (1x5 向量)
            d_list = coff_dis.flatten().tolist()
            d_str = "dist_coeffs: [" + ", ".join([f"{v:.8f}" for v in d_list]) + "]"

            new_lines = []
            in_target_block = False
            skip_until_next_key = False
            
            # 根据相机类型确定目标块的起始关键字 (与 params.yaml 中 section 名一致)
            target_key = f"{camera_type}:"

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
                    
                    # 匹配 K: 或 dist_coeffs:
                    if stripped.startswith("K:"):
                        new_lines.append(f"  {k_str}\n")
                        skip_until_next_key = True
                        continue
                    if stripped.startswith("dist_coeffs:"):
                        new_lines.append(f"  {d_str}\n")
                        skip_until_next_key = True
                        continue
                    
                    # 跳过旧矩阵的多行内容 (如果有的话)
                    if skip_until_next_key:
                        if ":" in stripped and not stripped.startswith("["):
                            skip_until_next_key = False
                        else:
                            continue

                new_lines.append(line)

            with open(config_path, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            
            print(f"\n[OK] {camera_type} 内参已成功更新至: {config_path}")
            print("K 和 dist_coeffs 已更新，原始注释已全部保留。")

        except Exception as e:
            print(f"\n[ERROR] 更新配置文件失败: {e}")
            import traceback
            traceback.print_exc()

    def calibrate_camera(self, camera_type="camera"):
        w, h = self.shape_inner_corner
        points_world = [] # the points in world space
        points_pixel = [] # the points in pixel space (relevant to points_world)
        
        # 为了获取图像尺寸
        gray_img = None
        
        for img_path in self.img_paths:
            img = cv2.imread(img_path)
            if img is None:
                continue
            gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # find the corners, cp_img: corner points in pixel space
            ret, cp_img = cv2.findChessboardCorners(gray_img, (w, h), None)
            # if ret is True, save
            if ret:
                points_world.append(self.cp_world)
                points_pixel.append(cp_img)
                # view the corners
                if self.visualization:
                    cv2.drawChessboardCorners(img, (w, h), cp_img, ret)
                    display_img = cv2.resize(img, None, fx=0.2, fy=0.2, interpolation=cv2.INTER_AREA)
                    cv2.imshow('FoundCorners', display_img)
                    # cv2.imshow('FoundCorners', img)
                    cv2.imwrite(os.path.join(self.img_dir, "FoundCorners.png"), img)
                    cv2.waitKey(500)

        if not points_world:
            print("Error: No corners found in any image!")
            return None, None

        # calibrate the camera
        ret, mat_intri, coff_dis, v_rot, v_trans = cv2.calibrateCamera(points_world, points_pixel, gray_img.shape[::-1], None, None)
        print ("ret: {}".format(ret))
        print ("intrinsic matrix: \n {}".format(mat_intri))
        print ("distortion cofficients: \n {}".format(coff_dis))

        # calculate the error of reproject
        total_error = 0
        for i in range(len(points_world)):
            points_pixel_repro, _ = cv2.projectPoints(points_world[i], v_rot[i], v_trans[i], mat_intri, coff_dis)
            error = cv2.norm(points_pixel[i], points_pixel_repro, cv2.NORM_L2) / len(points_pixel_repro)
            total_error += error
        print("Average error of reproject: {}".format(total_error / len(points_world)))

        self.mat_intri = mat_intri
        self.coff_dis = coff_dis

        # 调用精准更新函数
        self.update_config(mat_intri, coff_dis, camera_type=camera_type)

        return mat_intri, coff_dis


    def dedistortion(self, save_dir):
        # if not calibrated, calibrate first
        if self.mat_intri is None:
            assert self.coff_dis is None
            self.calibrate_camera()

        w, h = self.shape_inner_corner
        for img_path in self.img_paths:
            _, img_name = os.path.split(img_path)
            img = cv2.imread(img_path)
            newcameramtx, roi = cv2.getOptimalNewCameraMatrix(self.mat_intri, self.coff_dis, (w,h), 0, (w,h))
            dst = cv2.undistort(img, self.mat_intri, self.coff_dis, None, newcameramtx)
            cv2.imwrite(os.path.join(save_dir, img_name), dst)
        print("Dedistorted images have been saved to: {}".format(save_dir))
