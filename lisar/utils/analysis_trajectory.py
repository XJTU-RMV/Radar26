import argparse
import time
from pathlib import Path

import cv2
import numpy as np

from utils.config import load_cfg_from_cfg_file


WINDOW_NAME = "Trajectory Replay"


def parse_args():
    parser = argparse.ArgumentParser(description="离线动态重现 tracking_direct 导出的轨迹")
    parser.add_argument(
        "--npz",
        default=None,
        help="轨迹数据 npz 文件路径；默认读取 lisar/outputs/trajectory_logs 下最新文件",
    )
    parser.add_argument(
        "--png",
        default=None,
        help="基准底图 png 文件路径；默认与 npz 同名",
    )
    parser.add_argument(
        "--config",
        default="config/params.yaml",
        help="项目配置文件路径，用于读取副相机内参",
    )
    parser.add_argument(
        "--fps",
        type=float,
        default=20.0,
        help="播放帧率，默认 20",
    )
    parser.add_argument(
        "--tail",
        type=int,
        default=0,
        help="仅显示最近多少个点，0 表示显示完整历史",
    )
    parser.add_argument(
        "--export-video",
        action="store_true",
        help="将完整轨迹回放导出为 mp4 视频",
    )
    parser.add_argument(
        "--video-path",
        default=None,
        help="导出视频路径；默认与 npz 同名 mp4",
    )
    return parser.parse_args()


def find_latest_npz(log_dir: Path) -> Path:
    candidates = sorted(log_dir.glob("*.npz"))
    if not candidates:
        raise FileNotFoundError(f"未找到轨迹数据文件: {log_dir}")
    return candidates[-1]


def resolve_paths(args):
    repo_root = Path(__file__).resolve().parent.parent
    log_dir = Path(__file__).resolve().parent / "outputs" / "trajectory_logs"

    npz_path = Path(args.npz) if args.npz else find_latest_npz(log_dir)
    if not npz_path.is_absolute():
        npz_path = (repo_root / npz_path).resolve()

    png_path = Path(args.png) if args.png else npz_path.with_suffix(".png")
    if not png_path.is_absolute():
        png_path = (repo_root / png_path).resolve()

    config_path = Path(args.config)
    if not config_path.is_absolute():
        config_path = (repo_root / config_path).resolve()

    return npz_path, png_path, config_path


def world_angle_to_pixel(world_point, base_angle, camera_matrix, dist_coeffs):
    rel_x = float(world_point[0] - base_angle[0])
    rel_y = float(world_point[1] - base_angle[1])

    rx = np.tan(np.radians(rel_x))
    ry = -np.tan(np.radians(rel_y))

    ray_point = np.array([[[rx, ry, 1.0]]], dtype=np.float64)
    rvec = np.zeros((3, 1), dtype=np.float64)
    tvec = np.zeros((3, 1), dtype=np.float64)
    img_pts, _ = cv2.projectPoints(ray_point, rvec, tvec, camera_matrix, dist_coeffs)
    px = int(round(float(img_pts[0, 0, 0])))
    py = int(round(float(img_pts[0, 0, 1])))
    return px, py


def draw_points(image, pixel_points, color, current_idx, label):
    if not pixel_points:
        return
    for px, py in pixel_points:
        cv2.circle(image, (px, py), 2, color, -1)
    if len(pixel_points) >= 2:
        polyline = np.array(pixel_points, dtype=np.int32).reshape(-1, 1, 2)
        cv2.polylines(image, [polyline], False, color, 2)
    cv2.circle(image, pixel_points[0], 5, color, 2)
    cur_pt = pixel_points[-1]
    cv2.drawMarker(image, cur_pt, color, cv2.MARKER_TILTED_CROSS, 14, 2)
    cv2.putText(
        image,
        f"{label}",
        (cur_pt[0] + 8, cur_pt[1] - 8),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.5,
        color,
        1,
    )


def compute_error_metrics(target_world_point, pred_world_point, target_pixel, pred_pixel):
    world_error = np.array(pred_world_point, dtype=np.float64) - np.array(
        target_world_point, dtype=np.float64
    )
    pixel_error = np.array(pred_pixel, dtype=np.float64) - np.array(
        target_pixel, dtype=np.float64
    )
    return {
        "world_dx": float(world_error[0]),
        "world_dy": float(world_error[1]),
        "world_norm": float(np.linalg.norm(world_error)),
        "pixel_dx": float(pixel_error[0]),
        "pixel_dy": float(pixel_error[1]),
        "pixel_norm": float(np.linalg.norm(pixel_error)),
    }


def build_frame(
    base_image,
    target_points_world,
    pred_points_world,
    frame_indices,
    upto_idx,
    tail,
    base_angle,
    camera_matrix,
    dist_coeffs,
):
    canvas = base_image.copy()
    if upto_idx < 0:
        return canvas, None

    end = upto_idx + 1
    start = max(0, end - tail) if tail > 0 else 0

    target_pixels = [
        world_angle_to_pixel(point, base_angle, camera_matrix, dist_coeffs)
        for point in target_points_world[start:end]
    ]
    pred_pixels = [
        world_angle_to_pixel(point, base_angle, camera_matrix, dist_coeffs)
        for point in pred_points_world[start:end]
    ]

    draw_points(canvas, target_pixels, (0, 0, 255), int(frame_indices[upto_idx]), "target")
    draw_points(canvas, pred_pixels, (0, 255, 255), int(frame_indices[upto_idx]), "pred")

    current_target_pixel = target_pixels[-1]
    current_pred_pixel = pred_pixels[-1]
    cv2.line(canvas, current_target_pixel, current_pred_pixel, (255, 255, 255), 1)
    error_metrics = compute_error_metrics(
        target_points_world[upto_idx],
        pred_points_world[upto_idx],
        current_target_pixel,
        current_pred_pixel,
    )

    cv2.putText(
        canvas,
        f"sample {upto_idx + 1}/{len(target_points_world)}  frame={int(frame_indices[upto_idx])}",
        (20, 30),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2,
    )
    cv2.putText(
        canvas,
        f"base yaw={base_angle[0]:.2f} pitch={base_angle[1]:.2f}",
        (20, 60),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2,
    )
    cv2.putText(
        canvas,
        (
            f"world err=({error_metrics['world_dx']:+.2f}, {error_metrics['world_dy']:+.2f})deg "
            f"|norm|={error_metrics['world_norm']:.2f}"
        ),
        (20, 90),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2,
    )
    cv2.putText(
        canvas,
        (
            f"pixel err=({error_metrics['pixel_dx']:+.1f}, {error_metrics['pixel_dy']:+.1f})px "
            f"|norm|={error_metrics['pixel_norm']:.1f}"
        ),
        (20, 120),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2,
    )
    cv2.putText(
        canvas,
        "space: play/pause  a/d: step  r: restart  q: quit",
        (20, 150),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2,
    )
    return canvas, error_metrics


def export_video(
    video_path,
    fps,
    base_image,
    target_points_world,
    pred_points_world,
    frame_indices,
    tail,
    base_angle,
    camera_matrix,
    dist_coeffs,
):
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(video_path), fourcc, float(fps), (base_image.shape[1], base_image.shape[0]))
    if not writer.isOpened():
        raise RuntimeError(f"无法创建视频文件: {video_path}")
    try:
        for idx in range(len(target_points_world)):
            frame, _ = build_frame(
                base_image=base_image,
                target_points_world=target_points_world,
                pred_points_world=pred_points_world,
                frame_indices=frame_indices,
                upto_idx=idx,
                tail=tail,
                base_angle=base_angle,
                camera_matrix=camera_matrix,
                dist_coeffs=dist_coeffs,
            )
            writer.write(frame)
    finally:
        writer.release()


def main():
    args = parse_args()
    npz_path, png_path, config_path = resolve_paths(args)
    video_path = Path(args.video_path) if args.video_path else npz_path.with_suffix(".mp4")
    if not video_path.is_absolute():
        video_path = (Path(__file__).resolve().parent.parent / video_path).resolve()

    data = np.load(npz_path)
    base_angle = data["base_angle"].astype(np.float64)
    target_points_world = data["target_world_points"].astype(np.float64)
    pred_points_world = data["pred_world_points"].astype(np.float64)
    frame_indices = data["frame_indices"].astype(np.int32)

    if len(target_points_world) == 0:
        raise ValueError(f"轨迹数据为空: {npz_path}")
    if len(target_points_world) != len(pred_points_world):
        raise ValueError("target_world_points 与 pred_world_points 长度不一致")

    base_image = cv2.imread(str(png_path), cv2.IMREAD_COLOR)
    if base_image is None:
        raise FileNotFoundError(f"无法读取基准图像: {png_path}")

    config = load_cfg_from_cfg_file(str(config_path))
    sub_cfg = config.sub_camera
    camera_matrix = np.array(sub_cfg.K, dtype=np.float64).reshape(3, 3)
    dist_coeffs = np.asarray(sub_cfg.dist_coeffs, dtype=np.float64).flatten()

    if args.export_video:
        export_video(
            video_path=video_path,
            fps=args.fps,
            base_image=base_image,
            target_points_world=target_points_world,
            pred_points_world=pred_points_world,
            frame_indices=frame_indices,
            tail=args.tail,
            base_angle=base_angle,
            camera_matrix=camera_matrix,
            dist_coeffs=dist_coeffs,
        )
        print(f"已导出视频: {video_path}")

    total = len(target_points_world)
    state = {
        "index": 0,
        "playing": False,
        "dragging": False,
        "last_tick": time.time(),
    }

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(WINDOW_NAME, min(base_image.shape[1], 1280), min(base_image.shape[0], 960))

    def on_trackbar(pos):
        state["index"] = max(0, min(pos, total - 1))
        state["dragging"] = True

    cv2.createTrackbar("progress", WINDOW_NAME, 0, max(total - 1, 1), on_trackbar)

    while True:
        if state["playing"]:
            now = time.time()
            interval = 1.0 / max(args.fps, 1e-6)
            if now - state["last_tick"] >= interval:
                next_index = state["index"] + 1
                if next_index >= total:
                    next_index = total - 1
                    state["playing"] = False
                state["index"] = next_index
                cv2.setTrackbarPos("progress", WINDOW_NAME, state["index"])
                state["last_tick"] = now
        elif state["dragging"]:
            state["last_tick"] = time.time()
            state["dragging"] = False

        frame, _ = build_frame(
            base_image=base_image,
            target_points_world=target_points_world,
            pred_points_world=pred_points_world,
            frame_indices=frame_indices,
            upto_idx=state["index"],
            tail=args.tail,
            base_angle=base_angle,
            camera_matrix=camera_matrix,
            dist_coeffs=dist_coeffs,
        )
        cv2.imshow(WINDOW_NAME, frame)

        key = cv2.waitKey(15) & 0xFF
        if key == ord("q"):
            break
        if key == ord(" "):
            state["playing"] = not state["playing"]
            state["last_tick"] = time.time()
        elif key == ord("a"):
            state["playing"] = False
            state["index"] = max(0, state["index"] - 1)
            cv2.setTrackbarPos("progress", WINDOW_NAME, state["index"])
        elif key == ord("d"):
            state["playing"] = False
            state["index"] = min(total - 1, state["index"] + 1)
            cv2.setTrackbarPos("progress", WINDOW_NAME, state["index"])
        elif key == ord("r"):
            state["playing"] = False
            state["index"] = 0
            cv2.setTrackbarPos("progress", WINDOW_NAME, 0)

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
