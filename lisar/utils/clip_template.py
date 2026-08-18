import argparse
from pathlib import Path

import cv2


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_PATH = PROJECT_ROOT / "config" / "template" / "template.png"
WINDOW_NAME = "clip_template"
DISPLAY_WIDTH = 960


frame = None
display_scale = 1.0
playing = True
cropping = False
crop_start = None
crop_end = None
requested_frame = None


def make_display_frame(src):
    global display_scale

    h, w = src.shape[:2]
    display_scale = min(1.0, DISPLAY_WIDTH / w)
    if display_scale == 1.0:
        return src.copy()
    return cv2.resize(src, (int(round(w * display_scale)), int(round(h * display_scale))))


def display_to_frame_point(x, y):
    return int(round(x / display_scale)), int(round(y / display_scale))


def draw_status(img, text):
    cv2.putText(img, text, (20, 36), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)


def refresh_window():
    if frame is None:
        return

    shown = make_display_frame(frame)
    if cropping:
        if crop_start is not None:
            x1, y1 = crop_start
            x2, y2 = crop_end
            p1 = (int(round(x1 * display_scale)), int(round(y1 * display_scale)))
            p2 = (int(round(x2 * display_scale)), int(round(y2 * display_scale)))
            cv2.rectangle(shown, p1, p2, (0, 255, 0), 2)
        draw_status(shown, "crop: click start, drag, click end | Esc cancel")
    else:
        draw_status(shown, "space pause/play | trackbar seek | s crop | q quit")
    cv2.imshow(WINDOW_NAME, shown)


def save_crop():
    x1, y1 = crop_start
    x2, y2 = crop_end
    left, right = sorted((x1, x2))
    top, bottom = sorted((y1, y2))

    if left == right or top == bottom:
        print("裁剪失败：矩形宽高不能为 0")
        return False

    cropped = frame[top:bottom, left:right]
    TEMPLATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(TEMPLATE_PATH), cropped):
        raise OSError(f"failed to save template: {TEMPLATE_PATH}")
    print(f"已保存模板: {TEMPLATE_PATH}")
    return True


def on_mouse(event, x, y, flags, param):
    global cropping, crop_start, crop_end

    if not cropping or frame is None:
        return

    frame_h, frame_w = frame.shape[:2]
    px, py = display_to_frame_point(x, y)
    px = min(max(px, 0), frame_w - 1)
    py = min(max(py, 0), frame_h - 1)

    if event == cv2.EVENT_LBUTTONDOWN:
        if crop_start is None:
            crop_start = (px, py)
            crop_end = (px, py)
        else:
            crop_end = (px, py)
            if save_crop():
                cropping = False
                crop_start = None
                crop_end = None
    elif event == cv2.EVENT_MOUSEMOVE and crop_start is not None:
        crop_end = (px, py)

    refresh_window()


def read_frame(cap, index):
    global frame

    cap.set(cv2.CAP_PROP_POS_FRAMES, index)
    ret, new_frame = cap.read()
    if not ret:
        raise RuntimeError(f"failed to read frame: {index}")
    frame = new_frame


def on_trackbar(pos):
    global requested_frame

    requested_frame = pos


def main():
    global playing, cropping, crop_start, crop_end, requested_frame

    parser = argparse.ArgumentParser(description="Crop a template image from a video.")
    parser.add_argument("--video_path", default="/home/wtz/record_4-9/sub1.mp4", help="input video path")
    args = parser.parse_args()

    cap = cv2.VideoCapture(args.video_path)
    if not cap.isOpened():
        raise FileNotFoundError(f"failed to open video: {args.video_path}")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total_frames <= 0:
        raise ValueError("failed to get video frame count")

    cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
    cv2.createTrackbar("frame", WINDOW_NAME, 0, total_frames - 1, on_trackbar)
    cv2.setMouseCallback(WINDOW_NAME, on_mouse)

    current_index = 0
    read_frame(cap, current_index)
    requested_frame = 0

    while True:
        if requested_frame is not None and requested_frame != current_index:
            current_index = requested_frame
            read_frame(cap, current_index)
            requested_frame = None
        elif playing and not cropping:
            next_index = min(current_index + 1, total_frames - 1)
            if next_index != current_index:
                current_index = next_index
                read_frame(cap, current_index)
                cv2.setTrackbarPos("frame", WINDOW_NAME, current_index)
            else:
                playing = False
        refresh_window()
        key = cv2.waitKey(30) & 0xFF

        if key == ord("q"):
            break
        if key == ord(" "):
            playing = not playing
        elif key == ord("s"):
            playing = False
            cropping = True
            crop_start = None
            crop_end = None
            print("进入裁剪模式")
        elif key == 27:
            cropping = False
            crop_start = None
            crop_end = None
            print("已取消裁剪")
        elif key == ord("a"):
            current_index = max(current_index - 1, 0)
            read_frame(cap, current_index)
            cv2.setTrackbarPos("frame", WINDOW_NAME, current_index)
        elif key == ord("d"):
            current_index = min(current_index + 1, total_frames - 1)
            read_frame(cap, current_index)
            cv2.setTrackbarPos("frame", WINDOW_NAME, current_index)

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
