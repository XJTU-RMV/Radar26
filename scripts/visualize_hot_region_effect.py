from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import cv2

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from ui.radar_monitor_window import (
    DEFAULT_MAP_CLASS_NAMES,
    FIELD_MAP_DISPLAY_SIZE,
    draw_region_grid_on_map,
    draw_targets_on_map,
    load_image_bgr,
    resolve_hot_region_cells,
)
from ui.radar_runtime_controller import RadarMapTarget


CELL_CENTERS_M = {
    "top_left": (4.6, 11.3),
    "top_mid": (14.0, 11.3),
    "top_right": (23.4, 11.3),
    "bottom_left": (4.6, 3.7),
    "bottom_mid": (14.0, 3.7),
    "bottom_right": (23.4, 3.7),
}
CELL_NAMES = tuple(CELL_CENTERS_M)


def build_hot_region_demo_targets(faction: str, hot_cell_name: str) -> list[RadarMapTarget]:
    cx, cy = CELL_CENTERS_M[hot_cell_name]
    if faction == "red":
        ally_ids = (0, 1)
        enemy_ids = (5, 6)
        drone_id = 11
    else:
        ally_ids = (5, 6)
        enemy_ids = (0, 1)
        drone_id = 10

    return [
        RadarMapTarget(enemy_ids[0], cx - 0.9, cy + 0.45, source="demod"),
        RadarMapTarget(enemy_ids[1], cx - 0.35, cy - 0.35, source="vision"),
        RadarMapTarget(ally_ids[0], cx + 0.35, cy + 0.35, source="vision"),
        RadarMapTarget(ally_ids[1], cx + 0.9, cy - 0.45, source="demod"),
        RadarMapTarget(drone_id, cx, cy + 0.9, source="demod"),
        RadarMapTarget(enemy_ids[0], 23.0, 3.0, source="vision"),
    ]


def load_demo_base_map(map_path: Path, faction: str):
    map_image = load_image_bgr(map_path)
    if map_image is None:
        raise RuntimeError(f"failed to read map image: {map_path}")
    resized_map = cv2.resize(
        map_image,
        (FIELD_MAP_DISPLAY_SIZE.width(), FIELD_MAP_DISPLAY_SIZE.height()),
        interpolation=cv2.INTER_AREA,
    )
    return draw_region_grid_on_map(resized_map, faction)


def make_demo_frame(base_map, faction: str, hot_cell_name: str):
    targets = build_hot_region_demo_targets(faction, hot_cell_name)
    hot_cells = resolve_hot_region_cells(targets, faction)
    frame = draw_targets_on_map(base_map, targets, DEFAULT_MAP_CLASS_NAMES, faction)
    return frame, hot_cells


def resolve_dynamic_hot_cell(start_cell_name: str, elapsed_seconds: float, switch_seconds: float) -> str:
    start_index = CELL_NAMES.index(start_cell_name)
    offset = int(elapsed_seconds / switch_seconds)
    return CELL_NAMES[(start_index + offset) % len(CELL_NAMES)]


def run_dynamic_demo(args, base_map) -> None:
    if args.fps <= 0.0:
        raise ValueError("--fps must be positive")
    if args.switch_seconds <= 0.0:
        raise ValueError("--switch-seconds must be positive")
    if args.duration <= 0.0:
        raise ValueError("--duration must be positive")

    delay_ms = max(1, int(round(1000.0 / args.fps)))
    frame_size = (FIELD_MAP_DISPLAY_SIZE.width(), FIELD_MAP_DISPLAY_SIZE.height())
    writer = None
    if args.video_output:
        output_path = Path(args.video_output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        writer = cv2.VideoWriter(
            str(output_path),
            cv2.VideoWriter_fourcc(*"mp4v"),
            args.fps,
            frame_size,
        )
        if not writer.isOpened():
            writer.release()
            raise RuntimeError(f"failed to create video file: {output_path}")

    start_time = time.monotonic()
    frame_idx = 0
    total_frames = int(round(args.duration * args.fps))
    try:
        while args.show or frame_idx < total_frames:
            elapsed = time.monotonic() - start_time if args.show else frame_idx / args.fps
            hot_cell = resolve_dynamic_hot_cell(args.hot_cell, elapsed, args.switch_seconds)
            frame, hot_cells = make_demo_frame(base_map, args.faction, hot_cell)
            if writer is not None and frame_idx < total_frames:
                writer.write(frame)
            if args.show:
                cv2.imshow("hot region dynamic effect", frame)
                key = cv2.waitKey(delay_ms) & 0xFF
                if key in (27, ord("q")):
                    break
            frame_idx += 1
    finally:
        if writer is not None:
            writer.release()
            print(f"video_saved={args.video_output}")
        if args.show:
            cv2.destroyAllWindows()


def parse_args():
    parser = argparse.ArgumentParser(description="visualize radar map hot-region effect")
    parser.add_argument("--faction", choices=("red", "blue"), default="red")
    parser.add_argument("--hot-cell", choices=CELL_NAMES, default="top_left")
    parser.add_argument("--map", default="config/field/RM2026Map.png", help="field map image path")
    parser.add_argument("--output", default="/tmp/hot_region_effect.png", help="output image path")
    parser.add_argument("--show", action="store_true", help="show OpenCV preview window")
    parser.add_argument("--dynamic", action="store_true", help="animate the hot region across all six cells")
    parser.add_argument("--fps", type=float, default=20.0, help="dynamic preview/video FPS")
    parser.add_argument("--duration", type=float, default=16.0, help="dynamic video duration in seconds")
    parser.add_argument("--switch-seconds", type=float, default=2.4, help="seconds before moving to next hot cell")
    parser.add_argument("--video-output", default=None, help="optional dynamic mp4 output path")
    return parser.parse_args()


def main():
    args = parse_args()
    base_map = load_demo_base_map(Path(args.map), args.faction)

    if args.dynamic:
        if args.video_output is None and not args.show:
            args.video_output = "/tmp/hot_region_effect_dynamic.mp4"
        run_dynamic_demo(args, base_map)
        return

    frame, hot_cells = make_demo_frame(base_map, args.faction, args.hot_cell)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(output_path), frame):
        raise RuntimeError(f"failed to write output image: {output_path}")

    print(f"hot_cells={sorted(hot_cells)}")
    print(f"saved={output_path}")

    if args.show:
        cv2.imshow("hot region effect", frame)
        while True:
            key = cv2.waitKey(0) & 0xFF
            if key in (27, ord("q")):
                break
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
