import argparse
import tkinter as tk

import cv2


LEFT_KEYS = (ord("a"), 81, 65361, 2424832)
RIGHT_KEYS = (ord("d"), 83, 65363, 2555904)


def parse_args():
    parser = argparse.ArgumentParser(description="按指定倍数慢放视频")
    parser.add_argument("video_path", help="要播放的视频路径")
    parser.add_argument("--slow", type=float, default=16.0, help="慢放倍数，例如 16 表示慢 16 倍")
    parser.add_argument("--window-name", default="slow_video", help="OpenCV 窗口名")
    parser.add_argument("--screen-scale", type=float, default=0.95, help="窗口最大占屏幕比例")
    parser.add_argument("--no-fit-screen", action="store_true", help="使用视频原始尺寸播放")
    parser.add_argument("--loop", action="store_true", help="播放结束后循环")
    return parser.parse_args()


def get_screen_size():
    root = tk.Tk()
    root.withdraw()
    width = root.winfo_screenwidth()
    height = root.winfo_screenheight()
    root.destroy()
    return width, height


def fit_size(frame_width, frame_height, screen_width, screen_height, screen_scale):
    if not 0 < screen_scale <= 1:
        raise ValueError("--screen-scale 必须在 (0, 1] 范围内")

    max_width = int(screen_width * screen_scale)
    max_height = int(screen_height * screen_scale)
    ratio = min(max_width / frame_width, max_height / frame_height)
    return max(1, int(round(frame_width * ratio))), max(1, int(round(frame_height * ratio)))


def main():
    args = parse_args()
    if args.slow <= 0:
        raise ValueError("--slow 必须大于 0")

    cap = cv2.VideoCapture(args.video_path)
    if not cap.isOpened():
        raise RuntimeError(f"无法打开视频: {args.video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        raise RuntimeError(f"视频 FPS 非法: {fps}")

    delay_ms = max(1, int(round(1000.0 / fps * args.slow)))
    paused = True
    display_size = None
    current_frame = None

    def read_frame_at(frame_index):
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ok, frame = cap.read()
        if not ok:
            return None
        return frame

    def show_frame(frame):
        nonlocal display_size

        if display_size is None:
            frame_height, frame_width = frame.shape[:2]
            if args.no_fit_screen:
                display_size = frame_width, frame_height
            else:
                screen_width, screen_height = get_screen_size()
                display_size = fit_size(
                    frame_width,
                    frame_height,
                    screen_width,
                    screen_height,
                    args.screen_scale,
                )
            cv2.namedWindow(args.window_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(args.window_name, display_size[0], display_size[1])

        if display_size != (frame.shape[1], frame.shape[0]):
            frame = cv2.resize(frame, display_size, interpolation=cv2.INTER_AREA)
        cv2.imshow(args.window_name, frame)

    current_frame = read_frame_at(0)
    if current_frame is None:
        raise RuntimeError("视频没有可读取帧")
    show_frame(current_frame)

    while True:
        if not paused:
            ok, frame = cap.read()
            if not ok:
                if args.loop:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                break
            current_frame = frame
            show_frame(current_frame)

        key = cv2.waitKeyEx(delay_ms if not paused else 30)
        if key in (27, ord("q")):
            break
        if key == ord(" "):
            paused = not paused
        if key in RIGHT_KEYS:
            paused = True
            frame = cap.read()[1]
            if frame is not None:
                current_frame = frame
                show_frame(current_frame)
        if key in LEFT_KEYS:
            paused = True
            frame_index = max(0, int(cap.get(cv2.CAP_PROP_POS_FRAMES)) - 2)
            frame = read_frame_at(frame_index)
            if frame is not None:
                current_frame = frame
                show_frame(current_frame)

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
