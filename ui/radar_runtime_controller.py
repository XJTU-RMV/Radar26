from __future__ import annotations

import argparse
import threading
import time
from dataclasses import dataclass, field
from typing import Protocol, Sequence
import cv2

from loguru import logger

from utils.config import load_cfg_from_cfg_file, merge_cfg_from_args, resolve_runtime_flags


@dataclass
class RadarRuntimeOptions:
    faction: str | None = None
    use_video: bool | None = None
    enable_vision_localization: bool | None = None
    enable_laser_tracking: bool | None = None
    enable_demod: bool | None = None
    enable_referee: bool | None = None
    config_path: str = "config/params.yaml"


@dataclass
class RadarMapTarget:
    class_id: int
    x_m: float
    y_m: float
    is_guess: bool = False
    source: str = "vision"


@dataclass
class RadarRuntimeStatus:
    # 检测信息
    state: str = "idle"
    message: str = "待机"
    inference_fps: float = 0.0
    map_targets: tuple[RadarMapTarget, ...] = field(default_factory=tuple)
    demod_lines: tuple[str, ...] = field(default_factory=tuple)
    demod_info_lines: tuple[str, ...] = field(default_factory=tuple)
    demod_jam_lines: tuple[str, ...] = field(default_factory=tuple)
    match_log_lines: tuple[str, ...] = field(default_factory=tuple)

    # 状态信息
    faction: str = ""
    encryption_level: int | None = None # 当前爱呢加密等级
    current_key: str = ""
    is_double_vulnerability: bool = False
    used_double_vulnerability_count: int = 0
    total_double_vulnerability_count: int = 0
    countermeasure_success_count: int | None = None
    main_camera_available: bool = False
    sub_camera_available: bool = False
    break_key_pending: bool = False
    break_key_correct: bool | None = None
    pending_break_key: str = ""
    break_key_active_key: str = ""
    break_key_last_key: str = ""
    break_key_cooldown_remaining: float = 0.0


def build_runtime_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Radar Station UI")
    parser.add_argument("--faction", default=None, choices=["red", "blue"], help="team faction")
    parser.add_argument(
        "--use_video",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="use video source from params.yaml",
    )
    parser.add_argument(
        "--enable_laser_tracking",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="enable laser tracking thread",
    )
    parser.add_argument(
        "--enable_vision_localization",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="enable main-camera visual localization",
    )
    parser.add_argument(
        "--enable_referee",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="enable referee communication",
    )
    parser.add_argument(
        "--enable_demod",
        action=argparse.BooleanOptionalAction,
        default=None,
        help="enable information-wave demodulation thread",
    )
    parser.add_argument("--config", default="config/params.yaml", type=str, help="config file")
    return parser


def parse_runtime_options(argv: Sequence[str] | None = None) -> RadarRuntimeOptions:
    parser = build_runtime_arg_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    return RadarRuntimeOptions(
        faction=args.faction,
        use_video=args.use_video,
        enable_vision_localization=args.enable_vision_localization,
        enable_laser_tracking=args.enable_laser_tracking,
        enable_demod=args.enable_demod,
        enable_referee=args.enable_referee,
        config_path=args.config,
    )


def build_runtime_config(options: RadarRuntimeOptions) -> object:
    cfg = load_cfg_from_cfg_file(options.config_path)
    return merge_cfg_from_args(cfg, options)


class RadarRuntimeController:
    def __init__(self, options: RadarRuntimeOptions | None = None) -> None:
        self.options = options or RadarRuntimeOptions()
        self._lock = threading.Lock()
        self._stop_requested = threading.Event()
        self._status = RadarRuntimeStatus()
        self._startup_thread: threading.Thread | None = None
        
        self._event_loop = None
        self._camera = None
        self._camera_sub = None
        self._referee = None

    def start(self) -> bool:
        # 这里很快返回True，把真正启动线程分给_launch_radar
        with self._lock:
            if self._status.state in {"starting", "running"}:
                return False
            self._stop_requested.clear()
            self._status = RadarRuntimeStatus(state="starting", message="正在启动")
            self._startup_thread = threading.Thread(
                target=self._launch_radar,
                name="RadarLaunchThread",
                daemon=True,
            )
            self._startup_thread.start()
        return True

    def stop(self) -> None:
        self._stop_requested.set()
        self._cleanup_attached_runtime(set_idle=True)

    def get_status(self) -> RadarRuntimeStatus:
        with self._lock:
            status = RadarRuntimeStatus(
                state=self._status.state,
                message=self._status.message,
                inference_fps=self._status.inference_fps,
                map_targets=self._status.map_targets,
                demod_lines=self._status.demod_lines,
                demod_info_lines=self._status.demod_info_lines,
                demod_jam_lines=self._status.demod_jam_lines,
                match_log_lines=self._status.match_log_lines,

                encryption_level=self._status.encryption_level,
                current_key=self._status.current_key,
                faction=self._status.faction,
                is_double_vulnerability=self._status.is_double_vulnerability,
                used_double_vulnerability_count=self._status.used_double_vulnerability_count,
                total_double_vulnerability_count=self._status.total_double_vulnerability_count,
                countermeasure_success_count=self._status.countermeasure_success_count,
                main_camera_available=self._status.main_camera_available,
                sub_camera_available=self._status.sub_camera_available,
                break_key_pending=self._status.break_key_pending,
                break_key_correct=self._status.break_key_correct,
                pending_break_key=self._status.pending_break_key,
                break_key_active_key=self._status.break_key_active_key,
                break_key_last_key=self._status.break_key_last_key,
                break_key_cooldown_remaining=self._status.break_key_cooldown_remaining,
            )
            event_loop = self._event_loop
            referee = self._referee

        if status.state != "running" or event_loop is None:
            return status

        snapshot = event_loop.get_ui_snapshot()
        status.inference_fps = snapshot["inference_fps"]
        status.map_targets = tuple(
            RadarMapTarget(
                class_id=int(target.get("class_id", -1)),
                x_m=float(target.get("x_m", 0.0)),
                y_m=float(target.get("y_m", 0.0)),
                is_guess=bool(target.get("is_guess", False)),
                source=str(target.get("source", "vision") or "vision"),
            )
            for target in snapshot.get("map_targets", [])
        )
        status.demod_lines = tuple(snapshot.get("demod_lines", ()))
        status.demod_info_lines = tuple(snapshot.get("demod_info_lines", ()))
        status.demod_jam_lines = tuple(snapshot.get("demod_jam_lines", ()))
        status.match_log_lines = tuple(snapshot.get("match_log_lines", ()))
        status.countermeasure_success_count = snapshot.get("countermeasure_success_count")

        if referee is not None:
            used_count = int(getattr(referee, "request_count", 0))
            remaining_count = int(getattr(referee, "double_vulnerability_count", 0))
            status.encryption_level = int(getattr(referee, "encryption_level", 0))
            status.current_key = getattr(referee, "keys", "") or ""
            status.faction = getattr(referee, "faction", "") or ""
            status.is_double_vulnerability = bool(
                getattr(referee, "is_double_vulnerability", 0)
            )
            status.used_double_vulnerability_count = used_count
            status.total_double_vulnerability_count = used_count + remaining_count
            status.break_key_pending = bool(getattr(referee, "break_key_pending", False))
            status.break_key_correct = getattr(referee, "break_key_correct", None)
            status.pending_break_key = getattr(referee, "pending_break_key", None) or ""
            status.break_key_active_key = getattr(referee, "break_key_active_key", None) or ""
            status.break_key_last_key = getattr(referee, "break_key_last_key", None) or ""
            next_send_time = float(getattr(referee, "next_break_key_send_time", 0.0))
            status.break_key_cooldown_remaining = max(0.0, next_send_time - time.monotonic())
        else:
            status.faction = getattr(event_loop, "faction", "") or ""
        return status

    def send_break_key(self, key: str) -> dict[str, object]:
        with self._lock:
            status_state = self._status.state
            referee = self._referee

        if status_state != "running":
            raise RuntimeError("雷达站未运行")
        if referee is None:
            raise RuntimeError("裁判系统通信未启用")

        sent_now = bool(referee.break_keys(key))
        cooldown_remaining = max(
            0.0,
            float(getattr(referee, "next_break_key_send_time", 0.0)) - time.monotonic(),
        )
        return {
            "sent_now": sent_now,
            "cooldown_remaining": cooldown_remaining,
            "encryption_level": int(getattr(referee, "encryption_level", 0)),
        }

    def get_latest_track_frame(self):
        with self._lock:
            event_loop = self._event_loop
        if event_loop is None:
            return None
        return event_loop.get_latest_track_vis_img()

    def get_latest_sub_vis_frame(self):
        with self._lock:
            event_loop = self._event_loop
            camera_sub = self._camera_sub

        if event_loop is not None:
            frame = event_loop.get_latest_laser_sub_vis_img()
            if frame is not None:
                return frame

        if camera_sub is None:
            return None

        frame, _ = camera_sub.get_image_latest("laser_sub", timeout=0.1)
        if frame is None:
            return None
        return cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    def get_latest_laser_offset_frame(self):
        with self._lock:
            event_loop = self._event_loop
        if event_loop is None:
            return None
        return event_loop.get_latest_laser_offset_vis_img()

    def set_main_exposure(self, exposure: float) -> bool:
        with self._lock:
            camera = self._camera
        if camera is None:
            raise RuntimeError("主相机未启动")
        return bool(camera.set_exposure(exposure))

    def set_sub_exposure(self, exposure: float) -> bool:
        with self._lock:
            camera_sub = self._camera_sub
        if camera_sub is None:
            raise RuntimeError("副相机未启动")
        return bool(camera_sub.set_exposure(exposure))

    def _build_runtime_config(self):
        return build_runtime_config(self.options)

    def _launch_radar(self) -> None:
        # 后台启动线程
        camera = None
        camera_sub = None
        referee = None
        event_loop = None

        try:
            cfg = self._build_runtime_config()
            use_sub_camera, enable_laser_tracking = resolve_runtime_flags(cfg)

            logger.info("我方阵容为{}", "红方" if cfg.faction == "red" else "蓝方")
            logger.info("视觉定位{}", "开启" if cfg.enable_vision_localization else "关闭")
            logger.info("副相机{}", "开启" if use_sub_camera else "关闭")
            logger.info("激光追踪模式{}", "开启" if enable_laser_tracking else "关闭")
            logger.info("信息波解调{}", "开启" if cfg.enable_demod else "关闭")
            logger.info("串口通信{}", "开启" if cfg.enable_referee else "关闭")

            startup_warnings = []
            need_main_camera = bool(cfg.enable_vision_localization or cfg.get("record_main", False))
            if cfg.use_video:
                from driver.hik_camera.mock_hik import SimpleHikCamera

                if need_main_camera:
                    try:
                        camera = SimpleHikCamera(video_source=cfg.video_path)
                        camera.start_streaming()
                    except Exception as exc:
                        logger.exception("Failed to start video source.")
                        startup_warnings.append(f"视频源启动失败: {exc}")
                        camera = None
                camera_sub = None
            else:
                from driver.hik_camera.hik import SimpleHikCamera

                if need_main_camera:
                    try:
                        camera = SimpleHikCamera(cfg.main_camera, camera_role="main")
                        camera.start_streaming()
                    except Exception as exc:
                        logger.exception("Failed to start main camera.")
                        startup_warnings.append(f"主相机启动失败: {exc}")
                        camera = None

                if use_sub_camera:
                    try:
                        camera_sub = SimpleHikCamera(cfg.sub_camera, camera_role="sub")
                        camera_sub.start_streaming()
                    except Exception as exc:
                        logger.exception("Failed to start sub camera.")
                        startup_warnings.append(f"副相机启动失败: {exc}")
                        camera_sub = None
                else:
                    camera_sub = None

            if cfg.enable_referee:
                from driver.referee.referee_comm import RefereeCommManager

                referee_cfg = cfg.get("referee", {})
                referee = RefereeCommManager(
                    port=referee_cfg.get("port"),
                    baudrate=referee_cfg.get("baudrate", 115200),
                    args=cfg,
                )
                referee.start()

            from main_event_loop import MainEventLoop

            event_loop = MainEventLoop(
                config=cfg,
                main_camera=camera,
                sub_camera=camera_sub,
                referee=referee,
            )

            if self._stop_requested.is_set():
                self._cleanup_resources(event_loop, referee, camera_sub, camera)
                self._set_status(RadarRuntimeStatus())
                return

            event_loop.run()

            if self._stop_requested.is_set():
                self._cleanup_resources(event_loop, referee, camera_sub, camera)
                self._set_status(RadarRuntimeStatus())
                return

            with self._lock:
                self._event_loop = event_loop
                self._camera = camera
                self._camera_sub = camera_sub
                self._referee = referee
                message = "运行中"
                if startup_warnings:
                    message = "运行中，" + "；".join(startup_warnings)
                self._status = RadarRuntimeStatus(
                    state="running",
                    message=message,
                    main_camera_available=camera is not None,
                    sub_camera_available=camera_sub is not None,
                )

        except Exception as exc:
            logger.exception("Failed to launch radar runtime from UI.")
            self._cleanup_resources(event_loop, referee, camera_sub, camera)
            self._set_status(
                RadarRuntimeStatus(
                    state="error",
                    message=str(exc) or exc.__class__.__name__,
                )
            )

    def _set_status(self, status: RadarRuntimeStatus) -> None:
        with self._lock:
            self._status = status

    def _cleanup_attached_runtime(self, set_idle: bool) -> None:
        with self._lock:
            event_loop = self._event_loop
            referee = self._referee
            camera_sub = self._camera_sub
            camera = self._camera
            self._event_loop = None
            self._referee = None
            self._camera_sub = None
            self._camera = None
            if set_idle:
                self._status = RadarRuntimeStatus()

        self._cleanup_resources(event_loop, referee, camera_sub, camera)

    def _cleanup_resources(self, event_loop, referee, camera_sub, camera) -> None:
        if event_loop is not None:
            try:
                event_loop.stop()
            except Exception:
                logger.exception("Failed to stop MainEventLoop cleanly.")

        if referee is not None:
            try:
                referee.close()
            except Exception:
                logger.exception("Failed to close referee communication cleanly.")

        self._close_camera(camera_sub)
        self._close_camera(camera)

    @staticmethod
    def _close_camera(camera) -> None:
        if camera is None:
            return

        for method_name in ("stop_streaming", "close"):
            method = getattr(camera, method_name, None)
            if callable(method):
                try:
                    method()
                except Exception:
                    logger.exception("Failed to call {} on camera.", method_name)
