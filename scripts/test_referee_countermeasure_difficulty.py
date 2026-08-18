#!/usr/bin/env python3
import argparse
import signal
import sys
import time
from pathlib import Path
from types import SimpleNamespace

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


GAME_PROGRESS_ACTIVE = 4


class PrintOnlyCamera:
    def __init__(self):
        self.exposure = None
        self.gain = None

    def set_exposure(self, exposure):
        self.exposure = exposure
        print(f"[camera] set_exposure={exposure}")
        return True

    def set_gain(self, gain):
        self.gain = gain
        print(f"[camera] set_gain={gain}")
        return True

    def close(self):
        return None


class LoggingCamera:
    def __init__(self, camera):
        self.camera = camera

    @property
    def exposure(self):
        return getattr(self.camera, "exposure", None)

    @property
    def gain(self):
        return getattr(self.camera, "gain", None)

    def set_exposure(self, exposure):
        before = self.exposure
        ok = self.camera.set_exposure(exposure)
        print(
            f"[camera] set_exposure requested={exposure} ok={ok} "
            f"before={before} after={self.exposure}"
        )
        return ok

    def set_gain(self, gain):
        before = self.gain
        ok = self.camera.set_gain(gain)
        print(
            f"[camera] set_gain requested={gain} ok={ok} "
            f"before={before} after={self.gain}"
        )
        return ok

    def register_group(self, group_id):
        return self.camera.register_group(group_id)

    def get_image_latest(self, group_id, timeout=1.0):
        return self.camera.get_image_latest(group_id, timeout=timeout)

    def close(self):
        close = getattr(self.camera, "close", None)
        if callable(close):
            close()


class CameraDisplay:
    def __init__(self, camera, enabled, window_name="sub_stage3", width=640, height=480):
        self.enabled = enabled
        self.camera = camera
        self.window_name = window_name
        self.width = width
        self.height = height
        self.group_id = "stage3_display"
        self.cv2 = None
        self.last_frame_time = None
        self.fps = 0.0
        if not self.enabled:
            return

        import cv2

        self.cv2 = cv2
        self.camera.register_group(self.group_id)

    def update(self, status_text):
        if not self.enabled:
            return False

        img_rgb, _ = self.camera.get_image_latest(self.group_id, timeout=0.02)
        if img_rgb is None:
            key = self.cv2.waitKey(1) & 0xFF
            return key == ord("q")

        now = time.monotonic()
        if self.last_frame_time is not None:
            dt = now - self.last_frame_time
            if dt > 0:
                self.fps = 1.0 / dt
        self.last_frame_time = now

        display_bgr = self.cv2.resize(
            img_rgb,
            dsize=(self.width, self.height),
            interpolation=self.cv2.INTER_LINEAR,
        )
        display_bgr = self.cv2.cvtColor(display_bgr, self.cv2.COLOR_RGB2BGR)
        self.cv2.putText(
            display_bgr,
            status_text,
            (20, 38),
            self.cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (0, 255, 0),
            2,
        )
        self.cv2.putText(
            display_bgr,
            f"exp={getattr(self.camera, 'exposure', None)} gain={getattr(self.camera, 'gain', None)} fps={self.fps:.1f}",
            (20, 72),
            self.cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (0, 255, 0),
            2,
        )
        self.cv2.imshow(self.window_name, display_bgr)
        key = self.cv2.waitKey(1) & 0xFF
        return key == ord("q")

    def close(self):
        if self.enabled and self.cv2 is not None:
            self.cv2.destroyWindow(self.window_name)


class EstimatedDifficultyCameraController:
    def __init__(self, camera, sub_camera_config):
        self.camera = camera
        self.default_exposure = float(sub_camera_config.exposure_time)
        self.default_gain = float(sub_camera_config.gain)
        self.stage3_exposure = float(sub_camera_config.stage3.exposure_time)
        self.stage3_gain = float(sub_camera_config.stage3.gain)
        self.applied = None

    def update(self, game_active, difficulty):
        target = (
            (self.stage3_exposure, self.stage3_gain)
            if game_active and difficulty >= 3
            else (self.default_exposure, self.default_gain)
        )
        if target == self.applied:
            return
        exposure, gain = target
        if not self.camera.set_exposure(exposure):
            raise RuntimeError(f"Failed to set sub-camera exposure to {exposure}")
        if not self.camera.set_gain(gain):
            raise RuntimeError(f"Failed to set sub-camera gain to {gain}")
        self.applied = target


class AimedProgressDifficultyEstimator:
    def __init__(self, ignore_game_progress=False):
        self.ignore_game_progress = ignore_game_progress
        self.game_active = False
        self.success_count = 0
        self.difficulty = 1
        self.progress = 0.0
        self.aim_remainder = 0.0
        self.continuous_aim_count = 0
        self.lock_remaining = 0.0
        self.last_update_time = None

    def update(self, game_progress, enemy_aircraft_aimed, now):
        game_active = self.ignore_game_progress or int(game_progress) == GAME_PROGRESS_ACTIVE
        if game_active != self.game_active:
            self.game_active = game_active
            self.reset(now)
            return self.difficulty

        if self.last_update_time is None:
            self.last_update_time = now
            return self.difficulty

        dt = now - self.last_update_time
        self.last_update_time = now
        if dt <= 0:
            return self.difficulty

        if not game_active:
            return self.difficulty

        if self.lock_remaining > 0:
            self.lock_remaining = max(0.0, self.lock_remaining - dt)
            return self.difficulty

        if enemy_aircraft_aimed:
            self.aim_remainder += dt
            while self.aim_remainder >= 0.1 and self.success_count < 5:
                self.aim_remainder -= 0.1
                self.continuous_aim_count += 1
                self.progress += 0.6 * self.continuous_aim_count
                if self.progress >= self._threshold():
                    self.success_count += 1
                    self.difficulty = self._difficulty_from_success_count()
                    self.progress = 0.0
                    self.aim_remainder = 0.0
                    self.continuous_aim_count = 0
                    self.lock_remaining = 45.0
                    break
        else:
            self.progress = max(0.0, self.progress - 0.5 * dt)
            self.aim_remainder = 0.0
            self.continuous_aim_count = 0

        return self.difficulty

    def reset(self, now=None):
        self.success_count = 0
        self.difficulty = 1
        self.progress = 0.0
        self.aim_remainder = 0.0
        self.continuous_aim_count = 0
        self.lock_remaining = 0.0
        self.last_update_time = now

    def _threshold(self):
        if self.difficulty == 1:
            return 50.0
        return 100.0

    def _difficulty_from_success_count(self):
        if self.success_count == 0:
            return 1
        if self.success_count <= 2:
            return 2
        return 3


def parse_args():
    parser = argparse.ArgumentParser(
        description="监听裁判系统并打印激光反制难度状态"
    )
    parser.add_argument("--config", default="config/params.yaml")
    parser.add_argument("--port", default=None, help="裁判系统串口；不填则读取配置或自动扫描")
    parser.add_argument("--baudrate", type=int, default=None, help="裁判系统串口波特率")
    parser.add_argument("--interval", type=float, default=0.02, help="打印刷新间隔，单位秒")
    parser.add_argument("--all", action="store_true", help="每个刷新周期都打印；默认只在状态变化时打印")
    parser.add_argument(
        "--camera",
        choices=["print", "sub"],
        default="sub",
        help="相机测试模式：print 只打印设置请求，sub 打开真实副相机",
    )
    parser.add_argument(
        "--camera-trigger",
        choices=["countered", "aimed-estimate"],
        default="countered",
        help="相机切换触发源：正式 countered 难度或调试 aimed_estimate 难度",
    )
    parser.add_argument(
        "--camera-ready-timeout",
        type=float,
        default=8.0,
        help="打开真实副相机后等待取流进入 WORKING 的最长时间，单位秒",
    )
    parser.add_argument(
        "--self-test-stage3-camera",
        action="store_true",
        help="不监听裁判系统，直接模拟三次反制成功，测试阶段三相机曝光/增益切换",
    )
    parser.add_argument(
        "--show-camera",
        action="store_true",
        help="显示副相机画面，窗口中叠加当前难度、曝光、增益和FPS；按 q 退出",
    )
    parser.add_argument("--display-width", type=int, default=640, help="相机显示窗口宽度")
    parser.add_argument("--display-height", type=int, default=480, help="相机显示窗口高度")
    parser.add_argument(
        "--self-test-observe-seconds",
        type=float,
        default=1.5,
        help="阶段三相机自测中每个状态停留显示的秒数",
    )
    parser.add_argument(
        "--estimate-from-aimed",
        action="store_true",
        help="调试项：按规则手册用 aimed 估算当前难度；默认正式计数仍只使用 countered",
    )
    parser.add_argument(
        "--estimate-without-game-progress",
        action="store_true",
        help="调试项：忽略 game_progress，即使裁判系统未进入比赛中也累计 aimed_estimate",
    )
    return parser.parse_args()


def wait_camera_working(camera, timeout):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        status = getattr(camera, "status", None)
        status_name = getattr(status, "name", str(status))
        if status_name == "WORKING":
            return
        time.sleep(0.1)
    raise RuntimeError(f"Sub-camera did not enter WORKING within {timeout}s")


def build_camera(args, config):
    if args.camera == "print":
        return PrintOnlyCamera()

    from driver.hik_camera.hik import SimpleHikCamera

    camera = SimpleHikCamera(config.sub_camera, camera_role="sub")
    try:
        camera.start_streaming()
        wait_camera_working(camera, args.camera_ready_timeout)
        print(
            "[camera] sub camera ready "
            f"exposure={camera.exposure} gain={camera.gain}"
        )
        return LoggingCamera(camera)
    except Exception:
        camera.close()
        raise


def update_display_until(display, seconds, status_text):
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        if display.update(status_text):
            return True
        time.sleep(0.01)
    return False


def run_stage3_camera_self_test(args, config, countermeasure_tracker_class):
    camera = build_camera(args, config)
    display = CameraDisplay(
        camera,
        args.show_camera,
        width=args.display_width,
        height=args.display_height,
    )
    try:
        tracker = countermeasure_tracker_class(camera, config.sub_camera)
        print(
            "[self-test] start "
            f"default_exposure={config.sub_camera.exposure_time} "
            f"default_gain={config.sub_camera.gain} "
            f"stage3_exposure={config.sub_camera.stage3.exposure_time} "
            f"stage3_gain={config.sub_camera.stage3.gain}"
        )
        tracker.update(GAME_PROGRESS_ACTIVE, False)
        if update_display_until(
            display,
            args.self_test_observe_seconds,
            f"self-test d={tracker.difficulty} sc={tracker.success_count}",
        ):
            return
        for index in range(3):
            tracker.update(GAME_PROGRESS_ACTIVE, True)
            tracker.update(GAME_PROGRESS_ACTIVE, False)
            print(
                "[self-test] countered_rising_edge="
                f"{index + 1} difficulty={tracker.difficulty} "
                f"success_count={tracker.success_count} "
                f"camera_exposure={getattr(camera, 'exposure', None)} "
                f"camera_gain={getattr(camera, 'gain', None)}"
            )
            if update_display_until(
                display,
                args.self_test_observe_seconds,
                f"self-test d={tracker.difficulty} sc={tracker.success_count}",
            ):
                return
        ok = (
            tracker.difficulty == 3
            and float(getattr(camera, "exposure", -1)) == float(config.sub_camera.stage3.exposure_time)
            and float(getattr(camera, "gain", -1)) == float(config.sub_camera.stage3.gain)
        )
        print(f"[self-test] result={'PASS' if ok else 'FAIL'}")
        if not ok:
            raise RuntimeError("Stage3 camera setting self-test failed")
    finally:
        display.close()
        close = getattr(camera, "close", None)
        if callable(close):
            close()


def main():
    args = parse_args()
    if args.show_camera and args.camera != "sub":
        raise SystemExit("--show-camera requires --camera sub")
    if args.camera_trigger == "aimed-estimate":
        args.estimate_from_aimed = True

    from lisar.stage3 import CountermeasureDifficultyTracker
    from utils.config import load_cfg_from_cfg_file

    config = load_cfg_from_cfg_file(args.config)
    if args.self_test_stage3_camera:
        run_stage3_camera_self_test(args, config, CountermeasureDifficultyTracker)
        return

    from driver.referee.messages import RadarMarkMessage
    from driver.referee.protocol import MsgID
    from driver.referee.serial_comm import RefereeSerialManager

    referee_cfg = config.get("referee", {})
    port = args.port if args.port is not None else referee_cfg.get("port")
    baudrate = args.baudrate if args.baudrate is not None else referee_cfg.get("baudrate", 115200)

    state = SimpleNamespace(
        game_progress=0,
        stage_remain_time=0,
        enemy_aircraft_countered=0,
        enemy_aircraft_aimed=0,
        last_game_status_time=None,
        last_mark_progress_time=None,
    )

    def on_game_status(cmd_id, data):
        if cmd_id != MsgID.GAME_STATUS.value or len(data) < 3:
            return
        stage = data[0]
        state.game_progress = (stage >> 4) & 0x0F
        state.stage_remain_time = int.from_bytes(data[1:3], "little")
        state.last_game_status_time = time.monotonic()

    def on_radar_mark_progress(cmd_id, data):
        if cmd_id != MsgID.RADAR_MARK_PROGRESS.value:
            return
        message = RadarMarkMessage.from_bytes(data)
        state.enemy_aircraft_countered = int(message.enemy_aircraft_countered)
        state.enemy_aircraft_aimed = int(message.enemy_aircraft_aimed)
        state.last_mark_progress_time = time.monotonic()

    serial_manager = RefereeSerialManager(port=port, baudrate=baudrate, auto_scan=True)
    serial_manager.bind(MsgID.GAME_STATUS, on_game_status)
    serial_manager.bind(MsgID.RADAR_MARK_PROGRESS, on_radar_mark_progress)

    camera = build_camera(args, config)
    display = CameraDisplay(
        camera,
        args.show_camera,
        width=args.display_width,
        height=args.display_height,
    )
    tracker_camera = camera if args.camera_trigger == "countered" else PrintOnlyCamera()
    tracker = CountermeasureDifficultyTracker(tracker_camera, config.sub_camera)
    aimed_estimator = AimedProgressDifficultyEstimator(args.estimate_without_game_progress)
    estimated_camera_controller = None
    if args.camera_trigger == "aimed-estimate":
        estimated_camera_controller = EstimatedDifficultyCameraController(camera, config.sub_camera)
    stop = False

    def handle_stop(signum, frame):
        nonlocal stop
        stop = True

    signal.signal(signal.SIGINT, handle_stop)
    signal.signal(signal.SIGTERM, handle_stop)

    print(
        "Listening referee system: "
        f"port={port or 'auto'} baudrate={baudrate}. Press Ctrl+C to stop."
    )
    serial_manager.start()

    last_printed = None
    try:
        while not stop:
            now = time.monotonic()
            difficulty = tracker.update(
                state.game_progress,
                state.enemy_aircraft_countered,
            )
            estimated_difficulty = aimed_estimator.update(
                state.game_progress,
                state.enemy_aircraft_aimed,
                now,
            )
            estimated_game_active = (
                args.estimate_without_game_progress
                or state.game_progress == GAME_PROGRESS_ACTIVE
            )
            if estimated_camera_controller is not None:
                estimated_camera_controller.update(
                    estimated_game_active,
                    estimated_difficulty,
                )
            snapshot = (
                difficulty,
                tracker.success_count,
                state.game_progress,
                state.stage_remain_time,
                state.enemy_aircraft_countered,
                state.enemy_aircraft_aimed,
                serial_manager.current_port,
                serial_manager.state.name,
                getattr(camera, "exposure", None),
                getattr(camera, "gain", None),
            )
            if args.estimate_from_aimed:
                snapshot += (
                    estimated_difficulty,
                    aimed_estimator.success_count,
                    round(aimed_estimator.progress, 1),
                    round(aimed_estimator.lock_remaining, 1),
                    aimed_estimator.continuous_aim_count,
                )
            if args.all or snapshot != last_printed:
                output = (
                    "[difficulty] "
                    f"current={difficulty} success_count={tracker.success_count} "
                    f"game_progress={state.game_progress} remain={state.stage_remain_time}s "
                    f"countered={state.enemy_aircraft_countered} aimed={state.enemy_aircraft_aimed} "
                    f"port={serial_manager.current_port or '-'} serial={serial_manager.state.name}"
                )
                output += (
                    f" | camera mode={args.camera} trigger={args.camera_trigger} "
                    f"exposure={getattr(camera, 'exposure', None)} "
                    f"gain={getattr(camera, 'gain', None)}"
                )
                if args.estimate_from_aimed:
                    output += (
                        " | aimed_estimate "
                        f"current={estimated_difficulty} "
                        f"success_count={aimed_estimator.success_count} "
                        f"P={aimed_estimator.progress:.1f} "
                        f"n={aimed_estimator.continuous_aim_count} "
                        f"lock_remaining={aimed_estimator.lock_remaining:.1f}s"
                    )
                print(output)
                last_printed = snapshot
            display_text = (
                f"d={difficulty} sc={tracker.success_count} "
                f"gp={state.game_progress} c={state.enemy_aircraft_countered} "
                f"a={state.enemy_aircraft_aimed}"
            )
            if args.estimate_from_aimed:
                display_text += (
                    f" est_d={estimated_difficulty} "
                    f"P={aimed_estimator.progress:.1f}"
                )
            if display.update(display_text):
                stop = True
            time.sleep(args.interval)
    finally:
        serial_manager.close()
        display.close()
        close = getattr(camera, "close", None)
        if callable(close):
            close()


if __name__ == "__main__":
    main()
