import numpy as np
import open3d as o3d
import tkinter as tk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
import cv2
import time
import os
import argparse
import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.append(str(root_dir))

from driver.hik_camera.hik import SimpleHikCamera
from utils.config import load_cfg_from_cfg_file

os.environ['WAYLAND_DISPLAY'] = ''
os.environ['XDG_SESSION_TYPE'] = 'x11'
"""
跑之前要设置环境变量：
export XDG_SESSION_TYPE=x11
"""
class PixelToWorld:
    def __init__(self, camera_matrix, R, T, mesh, dist_coeffs=None, max_octree_depth=8):
        self.camera_matrix = np.array(camera_matrix, dtype=np.float64)
        self.dist_coeffs = (
            np.zeros(5)
            if dist_coeffs is None
            else np.array(dist_coeffs, dtype=np.float64)
        )
        self.R = np.array(R, dtype=np.float64)
        self.T = np.array(T, dtype=np.float64).reshape(3, 1)
        self.mesh = mesh
        self.mesh.paint_uniform_color([1, 1, 0])  # Yellow mesh surface
        # Create LineSet for mesh edges instead of point cloud
        self.edge_lineset = o3d.geometry.LineSet()
        vertices = np.asarray(self.mesh.vertices)
        # Create LineSet for mesh edges
        self.edge_lineset = o3d.geometry.LineSet()
        vertices = np.asarray(self.mesh.vertices)
        triangles = np.asarray(self.mesh.triangles)

        # Manually extract edges from triangles
        # Manually extract edges from triangles
        edges = set()
        for tri in triangles:
            # Each triangle has three edges: (v0,v1), (v1,v2), (v2,v0)
            edges.add(tuple(sorted([tri[0], tri[1]])))  # v0-v1
            edges.add(tuple(sorted([tri[1], tri[2]])))  # v1-v2
            edges.add(tuple(sorted([tri[2], tri[0]])))  # v2-v0
        edges = np.array(list(edges))  # Convert to numpy array

        self.edge_lineset.points = o3d.utility.Vector3dVector(vertices)
        self.edge_lineset.lines = o3d.utility.Vector2iVector(edges)
        self.edge_lineset.paint_uniform_color([1, 0, 1])  # Purple edges

        self.scene = o3d.t.geometry.RaycastingScene()
        self.scene.add_triangles(o3d.t.geometry.TriangleMesh.from_legacy(self.mesh))

    @classmethod
    def build_from_config(self, config):
        camera_cfg = config["main_camera"]
        pixel_world_transform = PixelToWorld(
            camera_matrix=np.array(camera_cfg["K"]).reshape(3, 3),
            R=np.array(camera_cfg["R"]),
            T=np.array(camera_cfg["t"]),
            dist_coeffs=np.array(camera_cfg["dist_coeffs"]),
            mesh=o3d.io.read_triangle_mesh(config["transform"]["mesh_path"]),
        )
        # Store laser camera config if available
        if "laser" in config:
            laser_cfg = config["laser"]
            # pixel_world_transform.laser_R = np.array(laser_cfg["R"])
            # pixel_world_transform.laser_T = np.array(laser_cfg["t"]).reshape(3, 1)
            pixel_world_transform.laser_bias_x = laser_cfg.get("bias_x", 0.0) / 100.0 # cm to m
            pixel_world_transform.laser_bias_y = laser_cfg.get("bias_y", 0.0) / 100.0
            pixel_world_transform.laser_bias_z = laser_cfg.get("bias_z", 0.0) / 100.0
        return pixel_world_transform

    @classmethod
    def build_from_config_and_extrinsics(self, config, R, T):
        camera_cfg = config["main_camera"]
        pixel_world_transform = PixelToWorld(
            camera_matrix=np.array(camera_cfg["K"]).reshape(3, 3),
            R=np.array(R),  # Calibrated R
            T=np.array(T),  # Calibrated T
            dist_coeffs=np.array(camera_cfg["dist_coeffs"]),
            mesh=o3d.io.read_triangle_mesh(config["transform"]["mesh_path"]),
        )
        # Store laser camera config if available
        if "laser" in config:
            laser_cfg = config["laser"]
            # pixel_world_transform.laser_R = np.array(laser_cfg["R"])
            # pixel_world_transform.laser_T = np.array(laser_cfg["t"]).reshape(3, 1)
            pixel_world_transform.laser_bias_x = laser_cfg.get("bias_x", 0.0) / 100.0 # cm to m
            pixel_world_transform.laser_bias_y = laser_cfg.get("bias_y", 0.0) / 100.0
            pixel_world_transform.laser_bias_z = laser_cfg.get("bias_z", 0.0) / 100.0
        return pixel_world_transform

    def get_hit_point(self, pixel):
        """仅获取射线与地图的碰撞点 (3D 坐标)"""
        u, v = pixel
        pixel_hom = np.array([u, v, 1.0], dtype=np.float64)
        if self.dist_coeffs is not None and not np.all(self.dist_coeffs == 0):
            points = np.array([[u, v]], dtype=np.float32).reshape(-1, 1, 2)
            undistorted = cv2.undistortPoints(
                points, self.camera_matrix, self.dist_coeffs, P=self.camera_matrix
            )
            u, v = undistorted[0, 0]
            pixel_hom = np.array([u, v, 1.0], dtype=np.float64)

        cam_dir = np.linalg.inv(self.camera_matrix) @ pixel_hom
        world_dir = self.R.T @ cam_dir
        origin = -self.R.T @ self.T.flatten()
        rays = o3d.core.Tensor([[*origin, *world_dir]], dtype=o3d.core.Dtype.Float32)
        result = self.scene.cast_rays(rays)
        t_hit = result["t_hit"].numpy()[0]
        
        if t_hit < float("inf"):
            return origin + t_hit * world_dir
        return None

    def get_laser_angles(self, pixel, hit_point=None):
        """获取激光发射器的角度。如果提供了 hit_point 则直接计算，否则先进行射线投射"""
        if hit_point is None:
            hit_point = self.get_hit_point(pixel)
        
        if hit_point is not None:
            # 1. 计算击中点在主相机坐标系下的位置
            p_cam = self.R @ hit_point.reshape(3, 1) + self.T.reshape(3, 1)
            
            # 2. 计算击中点在激光发射器坐标系下的位置
            bias_vector = np.array([self.laser_bias_x, self.laser_bias_y, self.laser_bias_z])
            p_laser_emitter = p_cam.flatten() - bias_vector
            
            # 3. 计算相对于激光发射中心的 yaw 和 pitch
            laser_yaw = np.degrees(np.arctan2(p_laser_emitter[0], p_laser_emitter[2]))
            laser_pitch = np.degrees(np.arctan2(-p_laser_emitter[1], np.sqrt(p_laser_emitter[0]**2 + p_laser_emitter[2]**2)))
            return (laser_yaw, laser_pitch)
        
        # 如果没击中，返回基于相机光心的原始角度
        u, v = pixel
        pixel_hom = np.array([u, v, 1.0], dtype=np.float64)
        cam_dir = np.linalg.inv(self.camera_matrix) @ pixel_hom
        yaw = np.degrees(np.arctan2(cam_dir[0], cam_dir[2]))
        pitch = np.degrees(np.arctan2(-cam_dir[1], np.sqrt(cam_dir[0]**2 + cam_dir[2]**2)))
        return (yaw, pitch)

    def pixel_to_world(self, pixel):
        """保持兼容性，同时获取碰撞点和角度"""
        hit_point = self.get_hit_point(pixel)
        angles = self.get_laser_angles(pixel, hit_point)
        return hit_point, angles

    def __call__(self, pixel):
        """
        Args: pixel(u, v) on image
        Returns: 
            hit_point: (x, y, z) in 3d or None
            angles: (yaw, pitch) relative to camera center
        """
        return self.pixel_to_world(pixel)

    def get_ray_geometry(self, pixel, ray_length=50.0):
        u, v = pixel
        pixel_hom = np.array([u, v, 1.0], dtype=np.float64)
        if self.dist_coeffs is not None and not np.all(self.dist_coeffs == 0):
            points = np.array([[u, v]], dtype=np.float32).reshape(-1, 1, 2)
            undistorted = cv2.undistortPoints(
                points, self.camera_matrix, self.dist_coeffs, P=self.camera_matrix
            )
            u, v = undistorted[0, 0]
            pixel_hom = np.array([u, v, 1.0], dtype=np.float64)
        
        cam_dir = np.linalg.inv(self.camera_matrix) @ pixel_hom
        world_dir = self.R.T @ cam_dir
        world_dir = world_dir / np.linalg.norm(world_dir) # 归一化方向
        origin = -self.R.T @ self.T.flatten()

        # 再次进行射线投射以获取准确的碰撞距离
        rays = o3d.core.Tensor([[*origin, *world_dir]], dtype=o3d.core.Dtype.Float32)
        result = self.scene.cast_rays(rays)
        t_hit = result["t_hit"].numpy()[0]

        # 确定射线的终点：击中了就停在击中点，没击中就延伸到指定长度
        display_t = t_hit if (t_hit < float("inf")) else ray_length
        ray_end = origin + display_t * world_dir

        # 创建可视化几何体
        origin_pcd = o3d.geometry.PointCloud()
        origin_pcd.points = o3d.utility.Vector3dVector([origin])
        origin_pcd.paint_uniform_color([0, 1, 0])  # 绿色起点

        ray_line = o3d.geometry.LineSet()
        ray_line.points = o3d.utility.Vector3dVector([origin, ray_end])
        ray_line.lines = o3d.utility.Vector2iVector([[0, 1]])
        ray_line.colors = o3d.utility.Vector3dVector([[1, 0, 0]])  # 红色射线

        geometries = [origin_pcd, ray_line]

        if t_hit < float("inf"):
            hit_point = origin + t_hit * world_dir
            hit_pcd = o3d.geometry.PointCloud()
            hit_pcd.points = o3d.utility.Vector3dVector([hit_point])
            hit_pcd.paint_uniform_color([0, 0, 1])  # 蓝色碰撞点
            geometries.append(hit_pcd)
            
        return geometries


class PixelToWorldGUI:

    def __init__(self, root, converter, image_path=None, image=None, scale_factor=1.0, depth_scale=0.5):
        self.root = root
        self.root.title("Pixel to World Coordinate Converter")
        self.converter = converter
        self.image_path = image_path
        self.scale_factor = scale_factor
        self.is_drawing = False
        self.pixel_trajectory = []
        self.world_trajectory = []
        self.canvas_lines = []
        self.last_click_point = None  # 用于记录上一次点击的点

        # 加载图像
        if image is not None:
            self.image = image # 预期为 RGB 格式（来自相机）
        elif image_path is not None:
            self.image = cv2.imread(image_path)
            if self.image is None:
                raise FileNotFoundError(f"Image not found: {image_path}")
            self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
        else:
            raise ValueError("Either image or image_path must be provided")
        self.image_scaled = None

        # 按钮框架
        self.button_frame = tk.Frame(root)
        self.button_frame.pack()

        self.zoom_out_button = tk.Button(
            self.button_frame,
            text="Zoom Out",
            command=lambda: self.adjust_scale(1 / 1.25),
        )
        self.zoom_out_button.pack(side=tk.LEFT, padx=5)
        self.zoom_in_button = tk.Button(
            self.button_frame,
            text="Zoom In",
            command=lambda: self.adjust_scale(1.25),
        )
        self.zoom_in_button.pack(side=tk.LEFT, padx=5)
        self.reset_zoom_button = tk.Button(
            self.button_frame,
            text="Reset Zoom",
            command=self.reset_zoom,
        )
        self.reset_zoom_button.pack(side=tk.LEFT, padx=5)
        # Tkinter 画布
        self.canvas = tk.Canvas(root)
        self.canvas.pack()
        self.canvas_image_id = None
        self._update_scaled_image()

        # 坐标标签
        self.coord_label = tk.Label(
            root,
            text="Select the point by left click on the image pixel (Mouse wheel to zoom, Right drag to draw, R to reset)",
            font=("Arial", 12),
        )
        self.coord_label.pack()

        # 重置按钮
        self.reset_button = tk.Button(
            root, text="Reset Trajectory", command=self.reset_trajectory
        )
        self.reset_button.pack()
        self.depth_button = tk.Button(
            self.button_frame,
            text="Generate Depth Map",
            command=self.generate_depth_map,
        )
        self.depth_button.pack(side=tk.LEFT, padx=5)
        self.depth_scale = depth_scale

        # OpenCV 窗口

        # Open3D 可视化
        try:
            self.vis = o3d.visualization.Visualizer()
            # 尝试创建窗口，如果失败则 self.vis 会被设为 None 或后续操作会报错
            if not self.vis.create_window(
                window_name="Ray and Vertex Visualization", width=800, height=600
            ):
                print("[WARN] Open3D 窗口创建失败，将仅运行坐标转换逻辑。")
                self.vis = None
            
            if self.vis:
                self.vis.add_geometry(self.converter.mesh)
                self.vis.add_geometry(self.converter.edge_lineset)
                render_opt = self.vis.get_render_option()
                if render_opt:
                    render_opt.point_size = 3.0
                    render_opt.mesh_show_back_face = True
                    render_opt.background_color = np.array([0.2, 0.2, 0.2])
                    render_opt.line_width = 8.0  # 设置线条宽度
        except Exception as e:
            print(f"[WARN] Open3D 可视化初始化失败: {e}。程序将继续运行转换逻辑。")
            self.vis = None

        # 绑定事件
        self.canvas.bind("<Button-1>", self.on_left_click)
        self.canvas.bind("<Button-3>", self.on_right_click)
        self.canvas.bind("<B3-Motion>", self.on_right_motion)
        self.canvas.bind("<ButtonRelease-3>", self.on_right_release)
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)
        self.canvas.bind("<Button-4>", self.on_mouse_wheel_up)
        self.canvas.bind("<Button-5>", self.on_mouse_wheel_down)
        self.root.bind("r", lambda event: self.reset_trajectory())
        self.root.bind("R", lambda event: self.reset_trajectory())

        # 打印网格范围
        vertices = np.asarray(self.converter.mesh.vertices)
        print(
            f"网格范围: min={np.min(vertices, axis=0)}, max={np.max(vertices, axis=0)}"
        )

        # 启动 Open3D 事件循环
        self.update_visualizer()

    def update_visualizer(self):
        if self.vis:
            self.vis.poll_events()
            self.vis.update_renderer()
        self.root.after(10, self.update_visualizer)

    def reset_trajectory(self):
        self.is_drawing = False
        self.pixel_trajectory = []
        self.world_trajectory = []
        self.canvas.delete("trajectory")
        self.canvas.delete("click_point") # 删除点击的点
        self.last_click_point = None
        self._redraw_canvas_annotations()
        if self.vis:
            self.vis.clear_geometries()
            self.vis.add_geometry(self.converter.mesh)
            self.vis.add_geometry(self.converter.edge_lineset)  # Changed from vertex_pcd
        self.coord_label.config(
            text="Trajectory reset. Left click to select pixel, right drag to draw"
        )

    def adjust_scale(self, factor: float) -> None:
        self.scale_factor = max(0.1, min(self.scale_factor * factor, 8.0))
        self._update_scaled_image()

    def reset_zoom(self) -> None:
        self.scale_factor = 1.0
        self._update_scaled_image()

    def on_mouse_wheel(self, event):
        self.adjust_scale(1.25 if event.delta > 0 else 1 / 1.25)

    def on_mouse_wheel_up(self, event):
        self.adjust_scale(1.25)

    def on_mouse_wheel_down(self, event):
        self.adjust_scale(1 / 1.25)

    def _scaled_canvas_point(self, point):
        return point[0] * self.scale_factor, point[1] * self.scale_factor

    def _update_scaled_image(self):
        new_size = (
            max(1, int(round(self.image.shape[1] * self.scale_factor))),
            max(1, int(round(self.image.shape[0] * self.scale_factor))),
        )
        self.image_scaled = cv2.resize(
            self.image, new_size, interpolation=cv2.INTER_LINEAR
        )
        self.image_pil = Image.fromarray(self.image_scaled)
        self.image_tk = ImageTk.PhotoImage(self.image_pil)
        self.canvas.config(width=new_size[0], height=new_size[1])
        if self.canvas_image_id is None:
            self.canvas_image_id = self.canvas.create_image(0, 0, anchor=tk.NW, image=self.image_tk)
        else:
            self.canvas.itemconfig(self.canvas_image_id, image=self.image_tk)
        self._redraw_canvas_annotations()

    def _redraw_canvas_annotations(self):
        self.canvas.delete("trajectory")
        self.canvas.delete("click_point")

        if self.last_click_point is not None:
            u_scaled, v_scaled = self._scaled_canvas_point(self.last_click_point)
            cross_half = 6
            self.canvas.create_line(
                u_scaled - cross_half,
                v_scaled,
                u_scaled + cross_half,
                v_scaled,
                fill="green",
                width=2,
                tags="click_point",
            )
            self.canvas.create_line(
                u_scaled,
                v_scaled - cross_half,
                u_scaled,
                v_scaled + cross_half,
                fill="green",
                width=2,
                tags="click_point",
            )

        if len(self.pixel_trajectory) > 1:
            for prev_pixel, curr_pixel in zip(self.pixel_trajectory[:-1], self.pixel_trajectory[1:]):
                prev_scaled = self._scaled_canvas_point(prev_pixel)
                curr_scaled = self._scaled_canvas_point(curr_pixel)
                self.canvas.create_line(
                    prev_scaled[0],
                    prev_scaled[1],
                    curr_scaled[0],
                    curr_scaled[1],
                    fill="red",
                    width=2,
                    tags="trajectory",
                )

    def on_left_click(self, event):
        if self.is_drawing:
            self.is_drawing = False
            self.pixel_trajectory = []
            self.world_trajectory = []
            self.canvas.delete("trajectory")
            self.coord_label.config(
                text="Exiting drawing mode. Left Click to select pixel."
            )

            return

        u_scaled, v_scaled = event.x, event.y

        u_orig = u_scaled / self.scale_factor
        v_orig = v_scaled / self.scale_factor
        self.last_click_point = (u_orig, v_orig)
        self._redraw_canvas_annotations()
        pixel = (u_orig, v_orig)
        world_coord, angles = self.converter.pixel_to_world(pixel)
        yaw, pitch = angles
        if world_coord is not None:
            coord_text = f"Pixel ({u_orig:.1f}, {v_orig:.1f}) -> 3D: ({world_coord[0]:.3f}, {world_coord[1]:.3f}, {world_coord[2]:.3f}) | Angles: (Y: {yaw:.2f}°, P: {pitch:.2f}°)"
        else:
            coord_text = f"Pixel ({u_orig:.1f}, {v_orig:.1f}) No 3D | Angles: (Y: {yaw:.2f}°, P: {pitch:.2f}°)"
        self.coord_label.config(text=coord_text)
        if self.vis:
            self.vis.clear_geometries()
            self.vis.add_geometry(self.converter.mesh)
            self.vis.add_geometry(self.converter.edge_lineset)  # Changed from vertex_pcd
            ray_geometries = self.converter.get_ray_geometry(pixel)
            for geom in ray_geometries:
                self.vis.add_geometry(geom)

    def on_right_click(self, event):
        self.is_drawing = True
        self.pixel_trajectory = []
        self.world_trajectory = []
        self.canvas.delete("trajectory")
        u_scaled, v_scaled = event.x, event.y
        u_orig = u_scaled / self.scale_factor
        v_orig = v_scaled / self.scale_factor
        pixel = (u_orig, v_orig)
        world_coord, _ = self.converter.pixel_to_world(pixel)
        if world_coord is not None:
            self.pixel_trajectory.append((u_orig, v_orig))
            self.world_trajectory.append(world_coord)
            print(
                f"Start to draw line: Pixel=({u_orig:.1f}, {v_orig:.1f}), 3D=({world_coord})"
            )
            self._redraw_canvas_annotations()
        self.coord_label.config(
            text="Drawing: Right drag to draw, left click to exit, R to reset"
        )

    def on_right_motion(self, event):
        if not self.is_drawing:
            return
        u_scaled, v_scaled = event.x, event.y
        u_orig = u_scaled / self.scale_factor
        v_orig = v_scaled / self.scale_factor
        pixel = (u_orig, v_orig)
        world_coord, _ = self.converter.pixel_to_world(pixel)
        if world_coord is not None and len(self.pixel_trajectory) > 0:
            self.pixel_trajectory.append((u_orig, v_orig))
            self.world_trajectory.append(world_coord)
            self._redraw_canvas_annotations()
            self.update_3d_trajectory()
            print(
                f"Trajactory points: Pixel=({u_orig:.1f}, {v_orig:.1f}), 3D=({world_coord}), Total points={len(self.world_trajectory)}"
            )

    def on_right_release(self, event):
        if self.is_drawing:
            self.update_3d_trajectory()
            print(f"Trajectory ends: {len(self.world_trajectory)}")

    def update_3d_trajectory(self):
        if not self.vis:
            return
        self.vis.clear_geometries()
        self.vis.add_geometry(self.converter.mesh)
        self.vis.add_geometry(self.converter.edge_lineset)  # Changed from vertex_pcd
        if len(self.world_trajectory) > 1:
            points = np.array(self.world_trajectory)
            lines = [[i, i + 1] for i in range(len(points) - 1)]
            line_set = o3d.geometry.LineSet()
            line_set.points = o3d.utility.Vector3dVector(points)
            line_set.lines = o3d.utility.Vector2iVector(lines)
            line_set.colors = o3d.utility.Vector3dVector(
                [[0, 0, 1]] * len(lines)
            )  # Blue
            self.vis.add_geometry(line_set)
            print(f"3D Trajactory updates: {len(lines)}")

    def generate_depth_map(self):
        start_time = time.time()
        self.coord_label.config(text="Generating depth map, please wait...")
        self.root.update()

        # 获取原图像尺寸
        h_orig, w_orig = self.image.shape[:2]
        # 下采样尺寸
        h_depth = int(h_orig * self.depth_scale)
        w_depth = int(w_orig * self.depth_scale)
        depth_map = np.zeros((h_depth, w_depth), dtype=np.float32)

        # 批量生成像素坐标
        v, u = np.indices((h_depth, w_depth), dtype=np.float32)
        u = u / self.depth_scale  # 还原到原图像坐标
        v = v / self.depth_scale
        pixels = np.stack([u.flatten(), v.flatten()], axis=1)

        # 批量射线投射
        pixel_hom = np.hstack([pixels, np.ones((pixels.shape[0], 1))])
        cam_dirs = np.linalg.inv(self.converter.camera_matrix) @ pixel_hom.T
        world_dirs = self.converter.R.T @ cam_dirs
        origin = -self.converter.R.T @ self.converter.T.flatten()
        origins = np.tile(origin, (pixels.shape[0], 1))
        rays = np.hstack([origins, world_dirs.T])
        rays_tensor = o3d.core.Tensor(rays, dtype=o3d.core.Dtype.Float32)
        result = self.converter.scene.cast_rays(rays_tensor)
        t_hit = result["t_hit"].numpy().reshape(h_depth, w_depth)

        # 填充深度图
        depth_map = t_hit
        depth_map[np.isinf(depth_map)] = 0  # 未命中设为 0

        # 归一化到 [0, 255]
        valid_depths = depth_map[depth_map > 0]
        if valid_depths.size > 0:
            min_depth = valid_depths.min()
            max_depth = valid_depths.max()
            depth_norm = np.zeros_like(depth_map)
            mask = depth_map > 0
            depth_norm[mask] = (
                255 * (depth_map[mask] - min_depth) / (max_depth - min_depth)
            )
            depth_norm = depth_norm.astype(np.uint8)
        else:
            depth_norm = np.zeros_like(depth_map, dtype=np.uint8)

        # 上采样到原尺寸
        depth_norm = cv2.resize(
            depth_norm, (w_orig, h_orig), interpolation=cv2.INTER_LINEAR
        )

        # 显示和保存
        depth_colormap = cv2.applyColorMap(depth_norm, cv2.COLORMAP_JET)
        cv2.imwrite("depth_map.png", depth_colormap)

        elapsed_time = time.time() - start_time
        self.coord_label.config(
            text=f"Depth map generated in {elapsed_time:.2f}s. Min depth: {min_depth:.2f}, Max depth: {max_depth:.2f}"
        )

    def __del__(self):
        if cv2 is not None:
            cv2.destroyAllWindows()
        if hasattr(self, 'vis') and self.vis:
            self.vis.destroy_window()


def load_first_video_frame(video_path):
    capture = cv2.VideoCapture(str(video_path))
    if not capture.isOpened():
        return None
    try:
        ok, frame = capture.read()
        if not ok:
            return None
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    finally:
        capture.release()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pixel to World Coordinate Converter")
    parser.add_argument("--image", type=str, help="指定本地测试图像路径（可选）")
    parser.add_argument(
        "--video_path",
        nargs="?",
        const="",
        default=None,
        help="指定视频路径；若只传 --video_path，则默认使用配置中的 video_path，并读取第一帧",
    )
    parser.add_argument("--serial", action="store_true", help="是否启用串口通信")
    args = parser.parse_args()

    config_path = "config/params.yaml"
    config = load_cfg_from_cfg_file(str(config_path))
    converter = PixelToWorld.build_from_config(config)
    default_demo_image = config["main_camera"].get("demo_img_path", "demo/test.jpg")

    # 2. 初始化串口 (可选，用于点击控制云台)
    if args.serial:
        from driver.motor.scripts.controller import GimbalController
        PORT_NAME = '/dev/ttyACM0' 
        gimbal = None
        try:
            gimbal = GimbalController(PORT_NAME, 115200)
            print("[INFO] 串口打开成功，点击画面可控制云台。")
        except Exception as e:
            print(f"[WARN] 串口打开失败: {e}，将仅运行坐标转换和可视化。")

    img_rgb = None
    if args.video_path is not None:
        video_path = args.video_path or config.get("video_path")
        if not video_path:
            raise ValueError("未指定 --video_path，且配置文件中也未设置 video_path")
        img_rgb = load_first_video_frame(video_path)
        if img_rgb is None:
            raise RuntimeError(f"无法从视频读取第一帧: {video_path}")
        print(f"[INFO] 已从视频首帧加载图像: {video_path}")
    elif not args.image:
        print("正在连接海康相机获取实时画面...")
        try:
            camera = SimpleHikCamera(config['main_camera'], camera_role="main")
            camera.start_streaming()
            camera.register_group("gui")
            exposure = 50000
            
            # 等待画面稳定并获取最新帧
            for _ in range(15):
                img_rgb, _ = camera.get_image_latest("gui", timeout=1)
                camera.set_exposure(exposure)
            camera.close()
            
            if img_rgb is None:
                print("[ERROR] 无法从相机获取图像，将使用默认 demo 图像。")
                args.image = default_demo_image
        except Exception as e:
            print(f"[ERROR] 相机启动或抓图失败: {e}。将回退到 demo 图像。")
            args.image = default_demo_image

    root = tk.Tk()
    
    # 包装一下点击事件，增加云台控制逻辑
    if img_rgb is not None:
        app = PixelToWorldGUI(root, converter, image=img_rgb, scale_factor=0.5)
    else:
        app = PixelToWorldGUI(root, converter, image_path=args.image, scale_factor=0.5)

    # 重写 GUI 的点击处理逻辑以支持云台
    if args.serial:
        original_on_left_click = app.on_left_click
        def on_left_click_with_gimbal(event):
            # 先执行原有的坐标转换和可视化逻辑
            original_on_left_click(event)
            
            # 如果串口可用，发送角度
            if gimbal:
                u_orig = event.x / app.scale_factor
                v_orig = event.y / app.scale_factor
                _, angles = converter.pixel_to_world((u_orig, v_orig))
                if angles:
                    yaw, pitch = angles
                    print(f"[GIMBAL] Sending Yaw: {-yaw:.2f}, Pitch: {-pitch:.2f}")
                    bias_yaw = 1.2
                    bias_pitch = 2.75
                    gimbal.set_angle(-yaw + bias_yaw, -pitch + bias_pitch)

        app.canvas.bind("<Button-1>", on_left_click_with_gimbal)
        
    plt.ion()  # 开启Matplotlib交互模式
    try:
        root.mainloop()
    finally:
        if args.serial:
            if gimbal:
                gimbal.close()
