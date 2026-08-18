from __future__ import annotations

import argparse
import csv
from pathlib import Path
import time

import cv2
import numpy as np


FRAME_GROUP = "lisar_debug_gimbal_axis"
WINDOW_NAME = "Lisar Gimbal Axis Debug"
LOG_FIELDS = (
    "time_s",
    "current_yaw_deg",
    "current_pitch_deg",
    "target_cmd_yaw_deg",
    "target_cmd_pitch_deg",
    "detector",
    "target_found",
    "target_x_px",
    "target_y_px",
    "target_confidence",
    "target_rel_yaw_deg",
    "target_rel_pitch_deg",
    "target_abs_yaw_deg",
    "target_abs_pitch_deg",
    "axis_mode",
    "axis_x_px",
    "axis_y_px",
    "axis_rel_yaw_deg",
    "axis_rel_pitch_deg",
    "axis_abs_yaw_deg",
    "axis_abs_pitch_deg",
    "preset",
    "preset_active",
    "preset_elapsed_s",
    "preset_center_yaw_deg",
    "preset_center_pitch_deg",
    "preset_radius_yaw_deg",
    "preset_radius_pitch_deg",
    "preset_phase_deg",
)


def pixel_to_angle(camera_matrix, dist_coeffs, x, y):
    pts_in = np.array([[[float(x), float(y)]]], dtype=np.float32)
    pts_out = cv2.undistortPoints(pts_in, camera_matrix, dist_coeffs, P=camera_matrix)
    undist_x = float(pts_out[0, 0, 0])
    undist_y = float(pts_out[0, 0, 1])

    fx = float(camera_matrix[0, 0])
    fy = float(camera_matrix[1, 1])
    cx = float(camera_matrix[0, 2])
    cy = float(camera_matrix[1, 2])
    rel_yaw = float(np.degrees(np.arctan((undist_x - cx) / fx)))
    rel_pitch = float(-np.degrees(np.arctan((undist_y - cy) / fy)))
    return rel_yaw, rel_pitch


def draw_crosshair(frame, center, color):
    x, y = int(round(center[0])), int(round(center[1]))
    cv2.line(frame, (x - 28, y), (x + 28, y), color, 2)
    cv2.line(frame, (x, y - 28), (x, y + 28), color, 2)
    cv2.circle(frame, (x, y), 8, color, 2)


def put_text_near_point(frame, text, point, color, font_scale=0.75, thickness=2):
    margin = 8
    font = cv2.FONT_HERSHEY_SIMPLEX
    (text_w, text_h), baseline = cv2.getTextSize(text, font, font_scale, thickness)
    x = int(round(point[0] + 10))
    y = int(round(point[1] - 10))
    x = min(max(x, margin), max(margin, frame.shape[1] - text_w - margin))
    y = min(max(y, text_h + margin), max(text_h + margin, frame.shape[0] - baseline - margin))
    cv2.rectangle(
        frame,
        (x - 3, y - text_h - 3),
        (x + text_w + 3, y + baseline + 3),
        (0, 0, 0),
        -1,
    )
    cv2.putText(frame, text, (x, y), font, font_scale, color, thickness)


def draw_target_detection(frame, detection):
    if detection is None:
        return
    if detection.source == "cv_module":
        for bar in detection.debug.get("bars", ()):
            box = cv2.boxPoints(bar["rect"])
            cv2.polylines(frame, [np.round(box).astype(np.int32)], True, (255, 0, 0), 1)
        for key in ("upper", "lower"):
            bar = detection.debug.get(key)
            if bar is None:
                continue
            box = cv2.boxPoints(bar["rect"])
            cv2.polylines(frame, [np.round(box).astype(np.int32)], True, (0, 255, 0), 2)
    elif detection.bbox is not None:
        x1, y1, x2, y2 = detection.bbox
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

    cv2.circle(frame, detection.center, 8, (0, 0, 255), 2)
    put_text_near_point(
        frame,
        f"target=({detection.center[0]}, {detection.center[1]}) conf={detection.confidence:.2f}",
        detection.center,
        (0, 0, 255),
    )


def put_line(frame, text, line_idx, color=(0, 255, 255)):
    y = 42 + line_idx * 36
    cv2.putText(frame, text, (20, y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 2)


def get_screen_size():
    try:
        import tkinter as tk

        root = tk.Tk()
        root.withdraw()
        width = int(root.winfo_screenwidth())
        height = int(root.winfo_screenheight())
        root.destroy()
        return width, height
    except Exception:
        return None


def fit_frame_to_screen(frame, screen_size, margin, max_scale):
    if max_scale <= 0.0:
        raise ValueError("display scale must be positive")
    img_h, img_w = frame.shape[:2]
    if screen_size is None:
        scale = max_scale
    else:
        screen_w, screen_h = screen_size
        max_w = max(screen_w - margin, 1)
        max_h = max(screen_h - margin, 1)
        scale = min(max_w / img_w, max_h / img_h, max_scale)

    if scale == 1.0:
        return frame
    return cv2.resize(
        frame,
        (max(1, int(round(img_w * scale))), max(1, int(round(img_h * scale)))),
        interpolation=cv2.INTER_AREA,
    )


def open_log_writer(log_path):
    if log_path is None:
        return None, None
    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    log_file = path.open("w", newline="")
    writer = csv.DictWriter(log_file, fieldnames=LOG_FIELDS)
    writer.writeheader()
    return log_file, writer


def write_log_row(
    writer,
    start_time,
    current_angle,
    target_angle,
    detector_name,
    detection,
    target_rel,
    target_abs,
    axis_mode,
    axis_pixel,
    axis_rel,
    axis_abs,
    preset_state,
):
    if writer is None:
        return
    preset_elapsed = ""
    preset_phase = ""
    if preset_state["active"]:
        preset_elapsed = time.monotonic() - preset_state["start_time"]
        preset_phase = preset_state["phase_deg"]
    row = {
        "time_s": time.monotonic() - start_time,
        "current_yaw_deg": "" if current_angle is None else float(current_angle[0]),
        "current_pitch_deg": "" if current_angle is None else float(current_angle[1]),
        "target_cmd_yaw_deg": "" if target_angle is None else float(target_angle[0]),
        "target_cmd_pitch_deg": "" if target_angle is None else float(target_angle[1]),
        "detector": detector_name,
        "target_found": detection is not None,
        "target_x_px": "" if detection is None else int(detection.center[0]),
        "target_y_px": "" if detection is None else int(detection.center[1]),
        "target_confidence": "" if detection is None else float(detection.confidence),
        "target_rel_yaw_deg": "" if target_rel is None else float(target_rel[0]),
        "target_rel_pitch_deg": "" if target_rel is None else float(target_rel[1]),
        "target_abs_yaw_deg": "" if target_abs is None else float(target_abs[0]),
        "target_abs_pitch_deg": "" if target_abs is None else float(target_abs[1]),
        "axis_mode": axis_mode,
        "axis_x_px": float(axis_pixel[0]),
        "axis_y_px": float(axis_pixel[1]),
        "axis_rel_yaw_deg": float(axis_rel[0]),
        "axis_rel_pitch_deg": float(axis_rel[1]),
        "axis_abs_yaw_deg": "" if axis_abs is None else float(axis_abs[0]),
        "axis_abs_pitch_deg": "" if axis_abs is None else float(axis_abs[1]),
        "preset": preset_state["name"],
        "preset_active": preset_state["active"],
        "preset_elapsed_s": preset_elapsed,
        "preset_center_yaw_deg": "" if preset_state["center"] is None else preset_state["center"][0],
        "preset_center_pitch_deg": "" if preset_state["center"] is None else preset_state["center"][1],
        "preset_radius_yaw_deg": preset_state["radius_yaw_deg"],
        "preset_radius_pitch_deg": preset_state["radius_pitch_deg"],
        "preset_phase_deg": preset_phase,
    }
    writer.writerow(row)


def build_arg_parser():
    parser = argparse.ArgumentParser(description="Debug gimbal yaw/pitch axis with keyboard control.")
    parser.add_argument("--config", default="config/params.yaml", help="runtime config yaml")
    parser.add_argument("--step", default=0.2, type=float, help="angle step in degrees")
    parser.add_argument("--scale", default=0.4, type=float, help="maximum display scale")
    parser.add_argument("--screen-margin", default=120, type=int, help="auto-fit margin in pixels")
    parser.add_argument("--log", default=None, help="write per-frame target angle log to CSV")
    parser.add_argument(
        "--auto-fit",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="fit display window to screen size",
    )
    parser.add_argument(
        "--detector",
        choices=("cv", "yolo26"),
        default="cv",
        help="target detector reused from countermeasure.py",
    )
    parser.add_argument(
        "--axis",
        choices=("principal-point", "image-center"),
        default="image-center",
        help="pixel used as the camera/gimbal axis marker",
    )
    parser.add_argument(
        "--preset",
        choices=("none", "circle"),
        default="circle",
        help="optional keyboard-started motion preset; press P to start or stop circle",
    )
    parser.add_argument("--circle-radius-yaw", default=3, type=float, help="circle preset yaw radius in degrees")
    parser.add_argument("--circle-radius-pitch", default=3, type=float, help="circle preset pitch radius in degrees")
    parser.add_argument("--circle-period", default=8.0, type=float, help="circle preset period in seconds")
    parser.add_argument("--circle-duration", default=30.0, type=float, help="circle preset duration in seconds")
    return parser


def run_debug_gimbal_axis(
    config,
    step_deg=0.2,
    display_scale=0.4,
    axis_mode="principal-point",
    detector_name="cv",
    auto_fit=True,
    screen_margin=120,
    log_path=None,
    preset_name="circle",
    circle_radius_yaw_deg=1.5,
    circle_radius_pitch_deg=1.0,
    circle_period_s=8.0,
    circle_duration_s=30.0,
):
    from driver.hik_camera.hik import SimpleHikCamera
    from driver.motor.scripts.controller import GimbalController
    from lisar.easy.cv_detector import CvModuleTargetDetector

    sub_cfg = config.sub_camera
    camera_matrix = np.array(sub_cfg.K, dtype=np.float64).reshape(3, 3)
    dist_coeffs = np.asarray(sub_cfg.dist_coeffs, dtype=np.float64).flatten()
    if detector_name == "yolo26":
        from lisar.difficulty.model_detector import Yolo26TargetDetector, load_stage3_detector_config

        detector = Yolo26TargetDetector(
            **load_stage3_detector_config(config),
            camera_K=camera_matrix,
            dist_coeffs=dist_coeffs,
        )
    else:
        detector = CvModuleTargetDetector(camera_matrix, dist_coeffs)

    cam = None
    gimbal = None
    target_angle = None
    step_deg = float(step_deg)
    circle_period_s = float(circle_period_s)
    circle_duration_s = float(circle_duration_s)
    if preset_name == "circle" and circle_period_s <= 0.0:
        raise ValueError("circle_period_s must be positive")
    if preset_name == "circle" and circle_duration_s <= 0.0:
        raise ValueError("circle_duration_s must be positive")
    preset_state = {
        "name": preset_name,
        "active": False,
        "start_time": None,
        "center": None,
        "radius_yaw_deg": float(circle_radius_yaw_deg),
        "radius_pitch_deg": float(circle_radius_pitch_deg),
        "phase_deg": "",
    }
    screen_size = get_screen_size() if auto_fit else None
    last_display_size = None
    log_file = None
    log_writer = None
    start_time = time.monotonic()
    try:
        log_file, log_writer = open_log_writer(log_path)
        cam = SimpleHikCamera(sub_cfg, camera_role="sub")
        cam.register_group(FRAME_GROUP)
        cam.start_streaming()
        time.sleep(1.0)

        gimbal_cfg = config.gimbal
        gimbal = GimbalController(port=gimbal_cfg.port, baudrate=gimbal_cfg.baudrate)

        cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
        while True:
            frame_rgb, _ = cam.get_image_latest(FRAME_GROUP, timeout=0.1)
            current_angle = gimbal.get_angle()
            if current_angle is not None and target_angle is None:
                target_angle = [float(current_angle[0]), float(current_angle[1])]

            if frame_rgb is None:
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break
                continue

            frame = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
            height, width = frame.shape[:2]
            if axis_mode == "image-center":
                axis_pixel = ((width - 1) / 2.0, (height - 1) / 2.0)
            else:
                axis_pixel = (float(camera_matrix[0, 2]), float(camera_matrix[1, 2]))

            axis_rel = pixel_to_angle(camera_matrix, dist_coeffs, axis_pixel[0], axis_pixel[1])
            if current_angle is None:
                axis_abs = None
            else:
                axis_abs = (float(current_angle[0]) + axis_rel[0], float(current_angle[1]) + axis_rel[1])

            detection = detector.detect(frame, {"current_angle": current_angle})
            target_rel = None
            target_abs = None
            if detection is not None:
                target_rel = pixel_to_angle(camera_matrix, dist_coeffs, detection.center[0], detection.center[1])
                if current_angle is not None:
                    target_abs = (float(current_angle[0]) + target_rel[0], float(current_angle[1]) + target_rel[1])

            if preset_state["active"]:
                elapsed = time.monotonic() - preset_state["start_time"]
                if elapsed > circle_duration_s:
                    preset_state["active"] = False
                    preset_state["phase_deg"] = ""
                else:
                    phase = 2.0 * np.pi * elapsed / circle_period_s
                    preset_state["phase_deg"] = float(np.degrees(phase) % 360.0)
                    center_yaw, center_pitch = preset_state["center"]
                    target_angle = [
                        center_yaw + preset_state["radius_yaw_deg"] * float(np.cos(phase)),
                        center_pitch + preset_state["radius_pitch_deg"] * float(np.sin(phase)),
                    ]
                    gimbal.set_angle(float(target_angle[0]), float(target_angle[1]))

            write_log_row(
                log_writer,
                start_time,
                current_angle,
                target_angle,
                detector_name,
                detection,
                target_rel,
                target_abs,
                axis_mode,
                axis_pixel,
                axis_rel,
                axis_abs,
                preset_state,
            )

            draw_crosshair(frame, axis_pixel, (0, 255, 255))
            draw_target_detection(frame, detection)
            key_hint = "W/S pitch  A/D yaw  R zero  P circle  [/]: step  Q quit"
            if preset_state["name"] == "none":
                key_hint = "W/S pitch  A/D yaw  R zero  [/]: step  Q quit"
            put_line(frame, key_hint, 0)
            put_line(frame, f"step={step_deg:.3f} deg axis={axis_mode} detector={detector_name}", 1)
            if current_angle is None:
                put_line(frame, "current angle: None", 2, (0, 0, 255))
            else:
                put_line(frame, f"current yaw={current_angle[0]:.3f} pitch={current_angle[1]:.3f}", 2)
            if target_angle is not None:
                put_line(frame, f"target  yaw={target_angle[0]:.3f} pitch={target_angle[1]:.3f}", 3)
            if axis_abs is not None:
                put_line(frame, f"axis abs yaw={axis_abs[0]:.3f} pitch={axis_abs[1]:.3f}", 4, (0, 255, 0))
            put_line(frame, f"axis pixel=({axis_pixel[0]:.1f}, {axis_pixel[1]:.1f})", 5, (0, 255, 0))
            if detection is None:
                put_line(frame, "target: NOT FOUND", 6, (0, 165, 255))
            else:
                put_line(frame, f"target pixel=({detection.center[0]}, {detection.center[1]})", 6, (0, 0, 255))
                put_line(frame, f"target rel yaw={target_rel[0]:.3f} pitch={target_rel[1]:.3f}", 7, (0, 0, 255))
            if target_abs is not None:
                put_line(frame, f"target abs yaw={target_abs[0]:.3f} pitch={target_abs[1]:.3f}", 8, (0, 0, 255))
            if preset_state["name"] == "circle":
                if preset_state["active"]:
                    put_line(
                        frame,
                        (
                            f"preset circle ON center=({preset_state['center'][0]:.3f}, "
                            f"{preset_state['center'][1]:.3f}) phase={preset_state['phase_deg']:.1f}"
                        ),
                        9,
                        (255, 255, 255),
                    )
                else:
                    put_line(frame, "preset circle OFF; press P when target found", 9, (255, 255, 255))
            if log_path is not None:
                put_line(frame, f"log={log_path}", 10, (255, 255, 255))

            display = fit_frame_to_screen(frame, screen_size, int(screen_margin), float(display_scale))
            display_size = (display.shape[1], display.shape[0])
            if display_size != last_display_size:
                cv2.resizeWindow(WINDOW_NAME, display_size[0], display_size[1])
                last_display_size = display_size
            cv2.imshow(WINDOW_NAME, display)
            key = cv2.waitKey(1) & 0xFF
            if key == ord("q"):
                break
            if key == ord("["):
                step_deg = max(0.01, step_deg / 2.0)
                continue
            if key == ord("]"):
                step_deg *= 2.0
                continue
            if key == ord("r"):
                preset_state["active"] = False
                preset_state["phase_deg"] = ""
                target_angle = [0.0, 0.0]
            elif key in (ord("p"), ord("P")):
                if preset_state["name"] != "circle":
                    continue
                if preset_state["active"]:
                    preset_state["active"] = False
                    preset_state["phase_deg"] = ""
                    continue
                if target_abs is None:
                    continue
                preset_state["center"] = (float(target_abs[0]), float(target_abs[1]))
                preset_state["start_time"] = time.monotonic()
                preset_state["active"] = True
                preset_state["phase_deg"] = 0.0
                target_angle = [
                    preset_state["center"][0] + preset_state["radius_yaw_deg"],
                    preset_state["center"][1],
                ]
            elif key in (ord("a"), ord("d"), ord("w"), ord("s")):
                if target_angle is None:
                    continue
                preset_state["active"] = False
                preset_state["phase_deg"] = ""
                if key == ord("a"):
                    target_angle[0] -= step_deg
                elif key == ord("d"):
                    target_angle[0] += step_deg
                elif key == ord("w"):
                    target_angle[1] += step_deg
                elif key == ord("s"):
                    target_angle[1] -= step_deg
            else:
                continue

            gimbal.set_angle(float(target_angle[0]), float(target_angle[1]))
    finally:
        if gimbal is not None:
            gimbal.close()
        if cam is not None:
            cam.close()
        if log_file is not None:
            log_file.close()
        cv2.destroyAllWindows()


def main(argv=None):
    from utils.config import load_cfg_from_cfg_file

    args = build_arg_parser().parse_args(argv)
    config = load_cfg_from_cfg_file(args.config)
    run_debug_gimbal_axis(
        config,
        step_deg=args.step,
        display_scale=args.scale,
        axis_mode=args.axis,
        detector_name=args.detector,
        auto_fit=args.auto_fit,
        screen_margin=args.screen_margin,
        log_path=args.log,
        preset_name=args.preset,
        circle_radius_yaw_deg=args.circle_radius_yaw,
        circle_radius_pitch_deg=args.circle_radius_pitch,
        circle_period_s=args.circle_period,
        circle_duration_s=args.circle_duration,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
