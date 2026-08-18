from __future__ import annotations

import argparse
from pathlib import Path

import cv2


WINDOW_NAME = "stage3 enhance compare"
TRACKBAR_NAME = "frame"
IMAGE_SUFFIXES = {".bmp", ".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp"}
VIDEO_SUFFIXES = {".avi", ".mkv", ".mov", ".mp4", ".mpeg", ".mpg", ".wmv"}
CLAHE = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))


def enhance_frame(frame_bgr, img_size):
    model_bgr = cv2.resize(frame_bgr, (img_size, img_size), interpolation=cv2.INTER_AREA)
    lab = cv2.cvtColor(model_bgr, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    l_enhanced = CLAHE.apply(l)
    enhanced_lab = cv2.merge((l_enhanced, a, b))
    return model_bgr, cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)


def draw_label(frame, text):
    display = frame.copy()
    cv2.rectangle(display, (0, 0), (260, 42), (0, 0, 0), -1)
    cv2.putText(display, text, (12, 29), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
    return display


def make_compare_frame(frame_bgr, img_size, frame_idx=None, frame_count=None):
    original, enhanced = enhance_frame(frame_bgr, img_size)
    left = draw_label(original, "before")
    right = draw_label(enhanced, "after CLAHE")
    compare = cv2.hconcat([left, right])
    if frame_idx is not None and frame_count is not None:
        text = f"frame {frame_idx + 1}/{frame_count}"
        cv2.putText(compare, text, (20, compare.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 255), 2)
    return compare


def show_image(path, img_size):
    frame = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if frame is None:
        raise RuntimeError(f"failed to read image: {path}")

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.imshow(WINDOW_NAME, make_compare_frame(frame, img_size))
    while True:
        key = cv2.waitKey(0) & 0xFF
        if key in (27, ord("q")):
            break
    cv2.destroyAllWindows()


def read_video_frame(cap, frame_idx):
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
    ok, frame = cap.read()
    if not ok:
        raise RuntimeError(f"failed to read video frame: {frame_idx}")
    return frame


def show_video(path, img_size, playback_fps=None):
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise RuntimeError(f"failed to open video: {path}")

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = float(playback_fps) if playback_fps is not None else float(cap.get(cv2.CAP_PROP_FPS))
    delay_ms = max(1, int(round(1000.0 / fps))) if fps > 0.0 else 33
    state = {"frame_idx": 0, "paused": True, "seeking": False}

    def on_trackbar(value):
        state["frame_idx"] = int(value)
        state["seeking"] = True

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.createTrackbar(TRACKBAR_NAME, WINDOW_NAME, 0, max(frame_count - 1, 0), on_trackbar)

    try:
        while True:
            frame_idx = min(max(state["frame_idx"], 0), frame_count - 1)
            frame = read_video_frame(cap, frame_idx)
            compare = make_compare_frame(frame, img_size, frame_idx, frame_count)
            cv2.imshow(WINDOW_NAME, compare)
            cv2.setTrackbarPos(TRACKBAR_NAME, WINDOW_NAME, frame_idx)
            state["seeking"] = False

            key = cv2.waitKey(30 if state["paused"] else delay_ms) & 0xFF
            if key in (27, ord("q")):
                break
            if key == ord(" "):
                state["paused"] = not state["paused"]
                continue
            if key == ord("a"):
                state["frame_idx"] = max(0, frame_idx - 1)
                state["paused"] = True
                continue
            if key == ord("d"):
                state["frame_idx"] = min(frame_count - 1, frame_idx + 1)
                state["paused"] = True
                continue
            if not state["paused"] and not state["seeking"]:
                state["frame_idx"] = 0 if frame_idx + 1 >= frame_count else frame_idx + 1
    finally:
        cap.release()
        cv2.destroyAllWindows()


def parse_args():
    parser = argparse.ArgumentParser(description="compare stage3 image enhancement before and after CLAHE")
    parser.add_argument("--input", required=True, help="image or video path")
    parser.add_argument("--img-size", type=int, default=640, help="resize size used before enhancement")
    parser.add_argument("--fps", type=float, default=None, help="video playback FPS; defaults to source video FPS")
    return parser.parse_args()


def main():
    args = parse_args()
    input_path = Path(args.input)
    suffix = input_path.suffix.lower()
    if args.fps is not None and args.fps <= 0.0:
        raise ValueError("--fps must be positive")

    if suffix in IMAGE_SUFFIXES:
        show_image(input_path, args.img_size)
    elif suffix in VIDEO_SUFFIXES:
        show_video(input_path, args.img_size, args.fps)
    else:
        raise ValueError(f"unsupported input suffix: {suffix}")


if __name__ == "__main__":
    main()
