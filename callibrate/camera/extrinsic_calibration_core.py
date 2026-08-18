from __future__ import annotations

from pathlib import Path
import xml.etree.ElementTree as ET

import cv2
import numpy as np


ROOT_DIR = Path(__file__).resolve().parent.parent


def parse_pp_file(pp_path: str | Path) -> np.ndarray:
    """Parse CloudCompare picked points and keep the name-sorted order."""
    pp_path = Path(pp_path)
    tree = ET.parse(pp_path)
    root = tree.getroot()
    point_elements = sorted(root.findall("point"), key=lambda item: int(item.get("name")))
    points = [
        [float(point.get("x")), float(point.get("y")), float(point.get("z"))]
        for point in point_elements
    ]
    return np.asarray(points, dtype=np.float32)


def resolve_keypoints_path(config_path: str | Path, keypoints_file: str) -> Path:
    config_path = Path(config_path).resolve()
    candidate = Path(keypoints_file)
    if candidate.is_absolute():
        return candidate
    return (config_path.parent.parent / candidate).resolve()


def solve_main_camera_extrinsic(
    world_points: np.ndarray,
    image_points: np.ndarray,
    camera_matrix: np.ndarray,
    dist_coeffs: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, float]:
    if len(world_points) != len(image_points):
        raise ValueError("世界坐标点与图像点数量不一致")
    if len(world_points) < 4:
        raise ValueError("solvePnP 至少需要 4 对点")

    success, rvec, tvec = cv2.solvePnP(
        np.asarray(world_points, dtype=np.float32),
        np.asarray(image_points, dtype=np.float32),
        np.asarray(camera_matrix, dtype=np.float64),
        np.asarray(dist_coeffs, dtype=np.float64),
    )
    if not success:
        raise RuntimeError("solvePnP 计算失败")

    rotation_matrix, _ = cv2.Rodrigues(rvec)
    projected_points, _ = cv2.projectPoints(
        np.asarray(world_points, dtype=np.float32),
        rvec,
        tvec,
        np.asarray(camera_matrix, dtype=np.float64),
        np.asarray(dist_coeffs, dtype=np.float64),
    )
    projected_points = projected_points.reshape(-1, 2)
    image_points = np.asarray(image_points, dtype=np.float32).reshape(-1, 2)
    reprojection_error = float(
        np.sqrt(np.mean(np.sum((image_points - projected_points) ** 2, axis=1)))
    )
    return rotation_matrix, tvec.reshape(3, 1), reprojection_error


def update_main_camera_extrinsic(
    config_path: str | Path,
    rotation_matrix: np.ndarray,
    translation_vector: np.ndarray,
) -> None:
    config_path = Path(config_path)
    lines = config_path.read_text(encoding="utf-8").splitlines(keepends=True)

    def format_inline_matrix(matrix: np.ndarray) -> str:
        rows = []
        for row in np.asarray(matrix).tolist():
            rows.append("[" + ", ".join(f"{float(value):.8f}" for value in row) + "]")
        return "[" + ", ".join(rows) + "]"

    new_r_line = f"  R: {format_inline_matrix(rotation_matrix)}\n"
    new_t_line = f"  t: {format_inline_matrix(np.asarray(translation_vector).reshape(3, 1))}\n"

    new_lines: list[str] = []
    in_main_camera_block = False
    replaced_r = False
    replaced_t = False

    for line in lines:
        stripped = line.strip()
        current_indent = len(line) - len(line.lstrip(" "))

        if stripped.startswith("main_camera:") and current_indent == 0:
            in_main_camera_block = True
            new_lines.append(line)
            continue

        if in_main_camera_block and stripped and current_indent == 0 and not stripped.startswith("#"):
            in_main_camera_block = False

        if in_main_camera_block and stripped.startswith("R:") and current_indent == 2:
            new_lines.append(new_r_line)
            replaced_r = True
            continue

        if in_main_camera_block and stripped.startswith("t:") and current_indent == 2:
            new_lines.append(new_t_line)
            replaced_t = True
            continue

        new_lines.append(line)

    if not replaced_r or not replaced_t:
        raise RuntimeError("未能在 params.yaml 中找到 main_camera.R 或 main_camera.t")

    config_path.write_text("".join(new_lines), encoding="utf-8")
