from __future__ import annotations

import copy
import time

import cv2


def build_video_frame_provider(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"无法打开视频文件: {video_path}")
    video_fps = float(cap.get(cv2.CAP_PROP_FPS))
    if video_fps <= 0:
        raise RuntimeError(f"无法读取视频 FPS: {video_path}")

    def frame_provider():
        ret, frame_bgr = cap.read()
        if not ret:
            return None
        return frame_bgr

    return frame_provider, cap, video_fps


def build_video_frame_provider_with_timestamp(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"无法打开视频文件: {video_path}")
    video_fps = float(cap.get(cv2.CAP_PROP_FPS))
    if video_fps <= 0:
        raise RuntimeError(f"无法读取视频 FPS: {video_path}")

    def frame_provider():
        ret, frame_bgr = cap.read()
        if not ret:
            return None
        return frame_bgr, {"time": time.monotonic(), "timestamp_source": "monotonic"}

    return frame_provider, cap, video_fps


def _open_sub_camera(config, group_id, use_stage3_profile=False):
    from driver.hik_camera.hik import SimpleHikCamera

    sub_cfg = copy.deepcopy(config.sub_camera)
    if use_stage3_profile:
        sub_cfg.exposure_time = sub_cfg.stage3.exposure_time
        sub_cfg.gain = sub_cfg.stage3.gain
        if "gamma_enable" in sub_cfg.stage3:
            sub_cfg.gamma_enable = bool(sub_cfg.stage3.gamma_enable)
        if getattr(sub_cfg, "gamma_enable", False):
            sub_cfg.gamma = sub_cfg.stage3.gamma

    cam_sub = SimpleHikCamera(sub_cfg, camera_role="sub")
    cam_sub.start_streaming()
    cam_sub.register_group(group_id)
    time.sleep(1.0)
    return cam_sub, sub_cfg


def build_sub_camera_frame_provider(config, group_id, use_stage3_profile=False):
    cam_sub, sub_cfg = _open_sub_camera(config, group_id, use_stage3_profile)

    def frame_provider():
        frame_rgb, _ = cam_sub.get_image_latest(group_id, timeout=0.1)
        if frame_rgb is None:
            return None
        return cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

    return frame_provider, cam_sub, float(getattr(sub_cfg, "acquisition_rate", 20.0))


def build_sub_camera_frame_provider_with_timestamp(config, group_id, use_stage3_profile=False):
    cam_sub, sub_cfg = _open_sub_camera(config, group_id, use_stage3_profile)

    def frame_provider():
        frame_rgb, _, metadata = cam_sub.get_image_latest_with_metadata(group_id, timeout=0.1)
        if frame_rgb is None:
            return None
        if metadata is None or metadata.get("device_timestamp") is None:
            raise RuntimeError("sub camera frame device timestamp is missing")
        timestamp_increment = float(metadata["device_timestamp_increment"])
        frame_device_timestamp = int(metadata["device_timestamp"])
        return cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR), {
            "time": frame_device_timestamp / timestamp_increment,
            "timestamp_source": "device",
            "device_timestamp": frame_device_timestamp,
            "device_timestamp_increment": timestamp_increment,
            "host_timestamp": metadata.get("host_timestamp"),
            "wall_timestamp": metadata.get("wall_timestamp"),
        }

    return frame_provider, cam_sub, float(getattr(sub_cfg, "acquisition_rate", 20.0))
