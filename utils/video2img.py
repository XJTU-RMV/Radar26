import argparse
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="Extract images from a video every N frames.")
    parser.add_argument("--video-path", type=Path, help="Path to input video.")
    parser.add_argument("--dataset-path", type=Path, default="/home/wtz/桌面/data/stage3/", help="Directory to save extracted images.")
    parser.add_argument("-n", "--interval", type=int, default=20, help="Extract one image every N frames.")
    parser.add_argument("--prefix", type=str, default=None, help="Output filename prefix. Defaults to video stem.")
    parser.add_argument("--ext", type=str, default="png", choices=["jpg", "jpeg", "png"], help="Output image format.")
    return parser.parse_args()


def main():
    args = parse_args()

    try:
        import cv2
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError("OpenCV is required. Install it with: pip install opencv-python") from exc

    if args.interval <= 0:
        raise ValueError("interval must be greater than 0")

    if not args.video_path.is_file():
        raise FileNotFoundError(f"video not found: {args.video_path}")

    args.dataset_path.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(str(args.video_path))
    if not cap.isOpened():
        raise RuntimeError(f"failed to open video: {args.video_path}")

    prefix = args.prefix or args.video_path.stem
    frame_idx = 0
    saved_count = 0

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        if frame_idx % args.interval == 0:
            image_path = args.dataset_path / f"{prefix}_frame_{frame_idx:06d}.{args.ext}"
            if not cv2.imwrite(str(image_path), frame):
                cap.release()
                raise RuntimeError(f"failed to write image: {image_path}")
            saved_count += 1

        frame_idx += 1

    cap.release()
    print(f"saved {saved_count} images to {args.dataset_path}")


if __name__ == "__main__":
    main()
