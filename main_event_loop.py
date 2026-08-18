from dataclasses import dataclass
import os
import threading
import time

import cv2
import numpy as np
import yaml
from loguru import logger

from driver.referee.messages import *
from driver.referee.referee_comm import RefereeCommManager
from lisar.countermeasure import (
    ScheduledCountermeasureGate,
    UnifiedCountermeasureTracker,
    load_countermeasure_start_seconds,
)


@dataclass
class RefereeDivision2dPosition:
    x: int
    y: int
    is_valid: bool
    time_stamp: float


@dataclass
class LaserTrackingTarget: # 保存无人机实时位置，用于激光追踪
    x: int
    y: int
    is_valid: bool
    time_stamp: float


@dataclass
class CircleRegion:
    name: str
    center_x_m: float
    center_y_m: float
    radius_m: float


class RegionStayDetector:
    def __init__(
        self,
        robot_name: str,
        region: CircleRegion,
        enter_confirm_seconds: float,
        exit_confirm_seconds: float,
    ):
        self.robot_name = robot_name
        self.region = region
        self.enter_confirm_seconds = float(enter_confirm_seconds)
        self.exit_confirm_seconds = float(exit_confirm_seconds)
        self.inside_since = None
        self.last_inside_time = None
        self.is_active = False

    def update(self, x_m: float | None, y_m: float | None, now: float | None = None) -> bool:
        now = time.monotonic() if now is None else now
        inside = x_m is not None and y_m is not None and self.contains(x_m, y_m) # 是否在区域内

        if inside:
            if self.inside_since is None:
                self.inside_since = now
            self.last_inside_time = now
            if now - self.inside_since >= self.enter_confirm_seconds:
                self.is_active = True
            return self.is_active

        if self.last_inside_time is None or now - self.last_inside_time > self.exit_confirm_seconds:
            self.inside_since = None
            self.last_inside_time = None
            self.is_active = False
        return self.is_active

    def contains(self, x_m: float, y_m: float) -> bool:
        dx = x_m - self.region.center_x_m
        dy = y_m - self.region.center_y_m
        return dx * dx + dy * dy <= self.region.radius_m * self.region.radius_m


class MainEventLoop:
    _instance = None

    def __init__(
        self,
        config,
        main_camera,
        sub_camera=None,
        referee: RefereeCommManager = None,
    ):
        # 1. 配置
        self.config = config
        self.faction = self.config.faction
        self.enable_vision_localization = bool(
            self.config.get("enable_vision_localization", True)
        )
        self.enable_laser_tracking = self.config.enable_laser_tracking
        self.initiative_counter = bool(self.config.get("initiative_counter", False))
        self.countermeasure_start_seconds = load_countermeasure_start_seconds(self.config)
        self.match_total_seconds = float(self.config.get("match_total_seconds", 420.0))
        self.demod = self.config.enable_demod
        self.referee_summary_period = 0.01
        self.demod_timeout = float(self.config.demod.get("demod_timeout", 1.0))
        self.map_points = self._load_map_points()

        # 录制配置
        self.record_main = bool(self.config.get("record_main", False))
        self.record_sub = bool(self.config.get("record_sub", False))
        self.record_session_stamp = time.strftime("%Y%m%d_%H%M%S")
        self.match_log_path = None
        self.match_log_index = 0
        self.match_log_match_active = False
        self.match_log_finalized = False

        # 2. 设备
        self.main_camera = main_camera
        self.sub_camera = sub_camera
        if self.sub_camera is not None:
            self.sub_camera.register_group("laser_sub")
        self.referee = referee

        # 3. 模块
        self.dummy_pixel_world_transform = None
        self.tracker = None
        if self.enable_vision_localization:
            if self.main_camera is None:
                logger.warning("主相机不可用，视觉定位不启动。")
                self.enable_vision_localization = False
            else:
                from tracker.tracker import CascadeMatchTracker
                from transform.ray_renderer import PixelToWorld

                self.main_camera.register_group("tracker")
                self.dummy_pixel_world_transform = PixelToWorld.build_from_config(self.config)
                self.tracker = CascadeMatchTracker(
                    self.config,
                    pixel_world_transform=self.dummy_pixel_world_transform,
                    visualize=True,
                )

        self.laser_tracker = None
        if self.enable_laser_tracking:
            if self.sub_camera is None:
                logger.warning("副相机不可用，激光检测模块不启动。")
                self.enable_laser_tracking = False
            else:
                self.laser_tracker = UnifiedCountermeasureTracker(
                    config=self.config,
                    referee=self.referee,
                    camera=self.sub_camera,
                    visualize=False,
                    event_callback=self._append_match_log,
                )

        # 4. 线程
        self.runtime_state_lock = threading.Lock()
        self.vision_state_lock = threading.Lock()
        self.demod_state_lock = threading.Lock()
        self.divisions_lock = threading.Lock()
        self.laser_target_lock = threading.Lock()
        self.record_lock = threading.Lock()
        self.match_log_lock = threading.Lock()
        self.countermeasure_gate = ScheduledCountermeasureGate(
            initiative_counter=self.initiative_counter,
            start_seconds=self.countermeasure_start_seconds,
            match_total_seconds=self.match_total_seconds,
            log_callback=self._append_match_log,
        )

        self.inference_fps = 0.0
        self.imgsize = self.config["car_detector"]["img_size"]
        self.tracks = []
        self.detect_vis_img = None
        self.track_vis_img = None
        self.main_writer = None
        self.sub_writer = None

        # 共享坐标
        self.enemy_aircraft_target = LaserTrackingTarget(
            x=-1,
            y=-1,
            is_valid=False,
            time_stamp=0.0,
        )

        self.vision_positions = self._make_invalid_positions()
        self.demod_positions = self._make_invalid_positions()
        self.divisions_pos = self._make_invalid_positions()
        self.divisions_source = ["none" for _ in range(12)]
        self.latest_demod_state = None
        self.demod_lines = [] # 输出信息
        self.demod_info_lines = []
        self.demod_jam_lines = []
        self.match_log_lines = []
        self.last_jamming_key_id = None
        self.region_stay_detectors = self._build_region_stay_detectors()
        self.last_region_status_snapshot = None
        self.last_enemy_status_log = None

        self.stop_event = None
        self.worker_threads = []
        self.summary_update_event = threading.Event()

        if self.tracker is not None:
            self.tracker.warmup(warmup_num=20)
        self.__class__._instance = self

    def _make_invalid_positions(self):
        return [RefereeDivision2dPosition(-1, -1, False, 0.0) for _ in range(12)]

    def _copy_positions(self, positions):
        return [
            RefereeDivision2dPosition(pos.x, pos.y, pos.is_valid, pos.time_stamp)
            for pos in positions
        ]

    def _load_map_points(self):
        map_point_path = self.config.get("map_point_config_path", "config/map_point.yaml")
        with open(map_point_path, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file) or {}

        point_items = data.get("points") or []
        if not isinstance(point_items, list):
            raise ValueError(f"{map_point_path} 中的 points 必须是列表")

        regions = {}
        for item in point_items:
            center = item["center"]
            regions[item["name"]] = CircleRegion(
                name=item["name"],
                center_x_m=float(center[0]),
                center_y_m=float(center[1]),
                radius_m=float(item["radius_m"]),
            )
        return regions

    def _build_region_stay_detectors(self):
        enemy_prefix = "B" if self.faction == "red" else "R"
        ally_prefix = "R" if self.faction == "red" else "B"
        enemy_hero_name = f"{enemy_prefix}1"
        enemy_engineer_name = f"{enemy_prefix}2"
        enemy_ground_names = [
            f"{enemy_prefix}1",
            f"{enemy_prefix}2",
            f"{enemy_prefix}3",
            f"{enemy_prefix}4",
            f"{enemy_prefix}7",
        ]
        strike_region_name = f"{enemy_prefix}1_strike_region"
        redeem_region_name = f"{enemy_prefix}2_redeem_region"
        enemy_defense_region_name = f"{enemy_prefix}_defense_region"
        ally_defense_region_name = f"{ally_prefix}_defense_region"
        enemy_outpost_region_name = f"{enemy_prefix}_outpost_region"
        strike_region = self.map_points[strike_region_name]
        redeem_region = self.map_points[redeem_region_name]
        enemy_defense_region = self.map_points[enemy_defense_region_name]
        ally_defense_region = self.map_points[ally_defense_region_name]
        enemy_outpost_region = self.map_points[enemy_outpost_region_name]
        single_robot_enter_seconds = 3.0
        single_robot_exit_seconds = 1.0
        fortress_enter_seconds = 1.0
        fortress_exit_seconds = 2.0
        return {
            "hero_strike": RegionStayDetector(
                robot_name=enemy_hero_name,
                region=strike_region,
                enter_confirm_seconds=single_robot_enter_seconds,
                exit_confirm_seconds=single_robot_exit_seconds,
            ),
            "engineer_redeem": RegionStayDetector(
                robot_name=enemy_engineer_name,
                region=redeem_region,
                enter_confirm_seconds=single_robot_enter_seconds,
                exit_confirm_seconds=single_robot_exit_seconds,
            ),
            "enemy_constrained_defense": [
                RegionStayDetector(
                    robot_name=robot_name,
                    region=enemy_defense_region,
                    enter_confirm_seconds=fortress_enter_seconds,
                    exit_confirm_seconds=fortress_exit_seconds,
                )
                for robot_name in enemy_ground_names
            ],
            "enemy_invade_fortress": [
                RegionStayDetector(
                    robot_name=robot_name,
                    region=ally_defense_region,
                    enter_confirm_seconds=fortress_enter_seconds,
                    exit_confirm_seconds=fortress_exit_seconds,
                )
                for robot_name in enemy_ground_names
            ],
            "enemy_revive_outpost": [ # 敌方是否在前哨站
                RegionStayDetector(
                    robot_name=robot_name,
                    region=enemy_outpost_region,
                    enter_confirm_seconds=fortress_enter_seconds,
                    exit_confirm_seconds=fortress_exit_seconds,
                )
                for robot_name in enemy_ground_names
            ],
        }

    def run(self):
        if self.stop_event is not None and not self.stop_event.is_set():
            logger.warning("Main event loop is already running.")
            return

        self._stop_camera_recorders()
        self._release_recorders()
        self.record_session_stamp = time.strftime("%Y%m%d_%H%M%S")
        self._init_match_log("session")
        self.stop_event = threading.Event()
        self.summary_update_event.clear()
        self._start_camera_recorders()
        self.worker_threads = [
            threading.Thread(
                target=self.summary_and_send_loop_thread,
                name="summary_and_send",
                daemon=False,
            ),
        ]

        if self.enable_vision_localization and self.main_camera is not None:
            self.worker_threads.insert(
                0,
                threading.Thread(
                    target=self.detection_loop_thread,
                    name="tracker_detection",
                    daemon=False,
                ),
            )
        else:
            logger.info("视觉定位关闭或主相机不可用，视觉检测线程不启动。")

        if self.laser_tracker is not None:
            self.worker_threads.append(
                threading.Thread(
                    target=self.laser_loop_thread,
                    name="laser_tracking",
                    daemon=False,
                )
            )

        if self.demod:
            self.worker_threads.append(
                threading.Thread(
                    target=self.demod_loop_thread,
                    name="enemy_demod",
                    daemon=False,
                )
            )

        for thread in self.worker_threads:
            thread.start()

    def stop(self):
        if self.stop_event is None:
            logger.warning("Main event loop is not running, nothing to stop.")
            return

        self.stop_event.set()
        self.summary_update_event.set()
        for thread in self.worker_threads:
            thread.join()
        self._stop_camera_recorders()
        self._release_recorders()
        self._finalize_current_match_log("程序停止")
        self.worker_threads = []
        self.stop_event = None

    def _start_camera_recorders(self):
        if self.record_main and self.main_camera is not None and hasattr(self.main_camera, "start_saving_threads"):
            self.main_camera.start_saving_threads()
        if self.record_sub and self.sub_camera is not None and hasattr(self.sub_camera, "start_saving_threads"):
            self.sub_camera.start_saving_threads()

    def _stop_camera_recorders(self):
        if self.record_main and self.main_camera is not None and hasattr(self.main_camera, "stop_saving_images"):
            self.main_camera.stop_saving_images()
        if self.record_sub and self.sub_camera is not None and hasattr(self.sub_camera, "stop_saving_images"):
            self.sub_camera.stop_saving_images()

    def _init_video_writer(self, kind, frame_bgr):
        if kind == "main":
            if not self.record_main or self.main_writer is not None:
                return
            camera_cfg = self.config.main_camera
            record_dir = str(camera_cfg.recording_save_root_dir)
            output_path = os.path.join(
                record_dir,
                f"{self.record_session_stamp}_main.mp4",
            )
        elif kind == "sub":
            if not self.record_sub or self.sub_writer is not None:
                return
            camera_cfg = self.config.sub_camera
            record_dir = str(camera_cfg.recording_save_root_dir)
            output_path = os.path.join(
                record_dir,
                f"{self.record_session_stamp}_sub.mp4",
            )
        else:
            raise ValueError(f"unknown recorder kind: {kind}")

        height, width = frame_bgr.shape[:2]
        fps = float(getattr(camera_cfg, "acquisition_rate", 20.0))
        os.makedirs(record_dir, exist_ok=True)
        writer = cv2.VideoWriter(
            output_path,
            cv2.VideoWriter_fourcc(*"mp4v"),
            fps,
            (width, height),
        )
        if not writer.isOpened():
            raise RuntimeError(f"failed to open video writer: {output_path}")

        if kind == "main":
            self.main_writer = writer
        else:
            self.sub_writer = writer

    def _write_record_frame(self, kind, frame_bgr):
        with self.record_lock:
            self._init_video_writer(kind, frame_bgr)
            if kind == "main" and self.main_writer is not None:
                self.main_writer.write(frame_bgr)
            if kind == "sub" and self.sub_writer is not None:
                self.sub_writer.write(frame_bgr)

    def _release_recorders(self):
        with self.record_lock:
            if self.main_writer is not None:
                self.main_writer.release()
                self.main_writer = None
            if self.sub_writer is not None:
                self.sub_writer.release()
                self.sub_writer = None

    def _init_match_log(self, label="match"):
        os.makedirs("logs", exist_ok=True)
        if label == "match":
            self.match_log_index += 1
            filename = f"{time.strftime('%Y-%m-%d-%H-%M-%S')}-match-{self.match_log_index:02d}.log"
        else:
            filename = f"{time.strftime('%Y-%m-%d-%H-%M-%S')}-{label}.log"
        self.match_log_path = os.path.join("logs", filename)
        with open(self.match_log_path, "w", encoding="utf-8"):
            pass
        with self.match_log_lock:
            self.match_log_lines = []
        self.match_log_finalized = False

    def _update_match_log_lifecycle(self):
        if self.referee is None:
            return

        is_game_active = bool(self.referee.game_start_flag)
        if is_game_active and not self.match_log_match_active:
            self._init_match_log("match")
            reset_stats = getattr(self.referee, "reset_radar2client_stats", None)
            if callable(reset_stats):
                reset_stats()
            reset_countermeasure_state = getattr(self.laser_tracker, "reset_countermeasure_state", None)
            if callable(reset_countermeasure_state):
                reset_countermeasure_state()
            self.countermeasure_gate.reset()
            self.match_log_match_active = True
            self._append_match_log(
                "比赛状态",
                f"比赛开始，阶段剩余 {int(self.referee.stage_remain_time)}s，日志文件={self.match_log_path}",
            )
            logger.info("[MatchLog] New match log started: {}", self.match_log_path)
            return

        if not is_game_active and self.match_log_match_active:
            self._finalize_current_match_log(
                f"比赛结束/离开比赛阶段 progress={self.referee.game_progress} remain={self.referee.stage_remain_time}s"
            )
            self.match_log_match_active = False

    def _append_referee_client_final_log(self):
        if self.referee is None:
            return
        stats = self.referee.get_radar2client_stats()
        valid_coord_count = stats["vision_coord_count"] + stats["demod_coord_count"]
        vision_percent = (
            stats["vision_coord_count"] * 100.0 / valid_coord_count
            if valid_coord_count > 0
            else 0.0
        )
        demod_percent = (
            stats["demod_coord_count"] * 100.0 / valid_coord_count
            if valid_coord_count > 0
            else 0.0
        )
        self._append_match_log_final(
            "裁判客户端",
            (
                f"坐标发送次数={stats['tx_count']} "
                f"平均频率={stats['avg_freq']:.2f}/s "
                f"敌方视觉坐标={stats['vision_coord_count']}({vision_percent:.1f}%) "
                f"敌方解调坐标={stats['demod_coord_count']}({demod_percent:.1f}%) "
                f"敌方无效坐标={stats['unknown_coord_count']}"
            ),
        )

    def _append_lisar_bounds_final_log(self):
        if self.laser_tracker is None:
            return
        get_summary = getattr(self.laser_tracker, "get_observed_module_bounds_summary", None)
        if not callable(get_summary):
            return
        try:
            summary = get_summary()
        except Exception:
            logger.exception("Failed to collect lisar observed module bounds.")
            return
        self._append_match_log_final("反制搜索范围", summary)

    def _finalize_current_match_log(self, reason: str):
        if self.match_log_path is None or self.match_log_finalized:
            return
        self._append_match_log_final("比赛状态", reason)
        self._append_lisar_bounds_final_log()
        self._append_referee_client_final_log()
        self.match_log_finalized = True
        logger.info("[MatchLog] Match log finalized: {}", self.match_log_path)

    def _format_match_countdown(self):
        if self.referee is None or not self.referee.game_start_flag:
            return None
        remain = int(self.referee.stage_remain_time)
        if remain < 0:
            remain = 0
        return f"{remain // 60}:{remain % 60:02d}"

    def _append_match_log(self, message_type: str, content: str):
        countdown = self._format_match_countdown()
        if countdown is None:
            return

        line = f"[{countdown}] [{message_type}] {content}"
        with self.match_log_lock:
            self.match_log_lines.append(line)
            self.match_log_lines = self.match_log_lines[-12:]
            with open(self.match_log_path, "a", encoding="utf-8") as file:
                file.write(line + "\n")

    def _append_match_log_final(self, message_type: str, content: str):
        if self.match_log_path is None:
            return
        line = f"[结束] [{message_type}] {content}"
        with self.match_log_lock:
            self.match_log_lines.append(line)
            self.match_log_lines = self.match_log_lines[-12:]
            with open(self.match_log_path, "a", encoding="utf-8") as file:
                file.write(line + "\n")

    def _update_enemy_aircraft_target(self, tracks=None):
        target = LaserTrackingTarget(
            x=-1,
            y=-1,
            is_valid=False,
            time_stamp=time.time(),
        )
        enemy_aircraft_class_id = 11 if self.faction == "red" else 10

        for track in tracks:
            if track.class_id != enemy_aircraft_class_id or not track.is_active:
                continue

            x1, y1, x2, y2 = map(int, track.car_box)
            target = LaserTrackingTarget(   # 粗调用无人机检测框中心
                x=int((x1 + x2) * 0.5),
                y=int((y1 + y2) * 0.5),
                is_valid=True,
                time_stamp=time.time(),
            )
            break

        with self.laser_target_lock:
            self.enemy_aircraft_target = target

    def get_enemy_aircraft_target(self) -> LaserTrackingTarget:
        with self.laser_target_lock:
            target = self.enemy_aircraft_target
            return LaserTrackingTarget(
                x=target.x,
                y=target.y,
                is_valid=target.is_valid,
                time_stamp=target.time_stamp,
            )

    def _tracks_to_positions(self, tracks):
        now = time.time()
        positions = self._make_invalid_positions()
        for track in tracks:
            class_id = getattr(track, "class_id", None)
            if class_id is None or class_id < 0 or class_id >= len(positions):
                continue

            if getattr(track, "is_active", False):
                positions[class_id] = RefereeDivision2dPosition(
                    x=int(track.pos_2d_uwb[0] * 100),
                    y=int(track.pos_2d_uwb[1] * 100),
                    is_valid=True,
                    time_stamp=now,
                )

            if getattr(track, "is_start_guess", False):
                positions[class_id] = RefereeDivision2dPosition(
                    x=int(track.guess_point[0] * 100),
                    y=int(track.guess_point[1] * 100),
                    is_valid=True,
                    time_stamp=now,
                )
        return positions

    def _fuse_positions(self, vision_positions, demod_positions):
        """
        融合检测和解调信息波结果
        """
        fused_positions = self._copy_positions(vision_positions)
        fused_sources = ["vision" if pos.is_valid else "none" for pos in vision_positions]
        now = time.time()
        enemy_class_id = [5, 6, 7, 8, 9, 11] if self.faction == "red" else [0, 1, 2, 3, 4, 10]
        for class_id in enemy_class_id:
            demod_pos = demod_positions[class_id]
            is_demod_fresh = (
                demod_pos.is_valid
                and (now - demod_pos.time_stamp) <= self.demod_timeout
            )
            if is_demod_fresh:
                fused_positions[class_id] = RefereeDivision2dPosition(
                    x=demod_pos.x,
                    y=demod_pos.y,
                    is_valid=True,
                    time_stamp=demod_pos.time_stamp,
                )
                fused_sources[class_id] = "demod"
        return fused_positions, fused_sources

    def _count_radar2client_sources(self, sources):
        class_ids = [5, 6, 7, 8, 11, 9] if self.faction == "red" else [0, 1, 2, 3, 10, 4]
        vision = 0
        demod = 0
        unknown = 0
        for class_id in class_ids:
            source = sources[class_id]
            if source == "vision":
                vision += 1
            elif source == "demod":
                demod += 1
            else:
                unknown += 1
        return vision, demod, unknown

    def _get_divisions_snapshot(self):
        with self.divisions_lock:
            return self._copy_positions(self.divisions_pos)

    def _build_demod_positions(self, frame, time_stamp):
        positions = self._make_invalid_positions()
        enemy_class_ids = [5, 6, 7, 8, 11, 9] if self.faction == "red" else [0, 1, 2, 3, 10, 4]
        for class_id, (x_pos, y_pos) in zip(enemy_class_ids, frame.to_xy_pairs()):
            positions[class_id] = RefereeDivision2dPosition(
                x=int(x_pos),
                y=int(y_pos),
                is_valid=True,
                time_stamp=time_stamp,
            )
        return positions

    def detection_loop_thread(self):
        """
        检测线程：更新self.vision_positions和无人机坐标bbox
        """
        logger.info("Tracker initialized and the model weights are loaded, starting detection loop.")
        time.sleep(2)

        while not self.stop_event.is_set():
            loop_start = time.time()

            try:
                frame, _ = self.main_camera.get_image_latest("tracker", timeout=0.1)
                if frame is None:
                    continue

                frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                tracks, detect_vis_img, track_vis_img = self.tracker.track(frame_bgr)

                with self.runtime_state_lock:
                    self.tracks = list(tracks)
                    self.detect_vis_img = (
                        None if detect_vis_img is None else detect_vis_img.copy()
                    )
                    self.track_vis_img = (
                        None if track_vis_img is None else track_vis_img.copy()
                    )
                    
                # 更新本地坐标
                vision_positions = self._tracks_to_positions(tracks)
                with self.vision_state_lock:
                    self.vision_positions = vision_positions
                self.summary_update_event.set()

                # self._update_enemy_aircraft_target(tracks)

            except Exception:
                logger.exception("Error in detection loop.")
            finally:
                elapsed = time.time() - loop_start
                inference_fps = 1 / elapsed if elapsed > 0 else 0.0
                with self.runtime_state_lock:
                    self.inference_fps = inference_fps

    def demod_loop_thread(self):
        """
        信息波/干扰波接收线程
        """
        logger.info("Demod thread started.")
        receiver = None
        last_seq = None
        last_break_key_correct = None
        last_prestart_jamming_key_id = None
        last_demod_control_log_key = None
        submitted_jamming_request_id = None
        failed_jamming_key_ids = set()
        rejected_duplicate_success_request_ids = set()
        seen_demod_ui_lines = set()
        info_demod_count = 0
        info_demod_first_time = None
        info_demod_last_time = None
        info_demod_first_wall_time = None
        info_demod_last_wall_time = None
        info_demod_first_countdown = None
        info_demod_last_countdown = None
        game_start_wall_time = None

        try:
            from RX.receiver import DemodController

            demod_cfg = self.config.get("demod", {})
            last_wait_log_time = 0.0

            receiver = DemodController(
                side=self.faction,
                target_level=int(demod_cfg.get("target_level", 3)),
                host=demod_cfg.get("listen_host", "0.0.0.0"),
                port=int(demod_cfg.get("listen_port", 9999)),
                timeout=float(demod_cfg.get("decode_timeout", 30.0)),
                auto_advance=self.referee is None,
                decode_enabled=self.referee is None,
            )

            logger.info("正在启动解调")
            receiver.start()
            logger.info("启动解调成功")

            while not self.stop_event.is_set():
                if self.referee is not None:
                    if not self.referee.game_start_flag:
                        receiver.set_decode_enabled(False)
                        game_start_wall_time = None
                        now = time.monotonic()
                        if now - last_wait_log_time >= 1.0:
                            logger.info(
                                "Waiting for game start before jamming demodulation: progress={} remain={}s",
                                getattr(self.referee, "game_progress", -1),
                                getattr(self.referee, "stage_remain_time", -1),
                            )
                            last_wait_log_time = now
                    elif game_start_wall_time is None:
                        game_start_wall_time = time.time()
                        with self.demod_state_lock:
                            self.demod_positions = self._make_invalid_positions()
                        last_seq = None
                        receiver.set_decode_enabled(True)

                snapshot = receiver.get_snapshot()
                lines = snapshot["lines"]
                line_records = snapshot.get("line_records", [])
                if not line_records:
                    line_records = [(line, time.time()) for line in lines]
                demod_state = snapshot["state"]
                if game_start_wall_time is not None: # 清空消息缓存
                    for attr in (
                        "location",
                        "hp",
                        "allowed_bullets",
                        "enemy_status",
                        "buff_status",
                        "jamming_key",
                    ):
                        value = getattr(demod_state, attr)
                        if value is not None and value.time_stamp < game_start_wall_time:
                            setattr(demod_state, attr, None)
                latest_location = demod_state.location
                latest_jamming_key = demod_state.jamming_key
                control_log_key = (
                    snapshot["current_level"],
                    snapshot["target_level"],
                    snapshot["connected"],
                    snapshot["ready"],
                    snapshot["active_request_id"],
                    snapshot["success_request_id"],
                    snapshot["decode_enabled"],
                    snapshot["control_thread_alive"],
                    snapshot["last_control_status"],
                )
                if control_log_key != last_demod_control_log_key:
                    self._append_match_log(
                        "解调控制",
                        (
                            f"level={snapshot['current_level']}/{snapshot['target_level']} "
                            f"连接工控机={int(snapshot['connected'])} "
                            f"ready={int(snapshot['ready'])} "
                            f"decode={int(snapshot['decode_enabled'])} "
                            f"控制线程={int(snapshot['control_thread_alive'])} "
                            f"active={snapshot['active_request_id']} "
                            f"success={snapshot['success_request_id']} "
                            f"状态={snapshot['last_control_status']}"
                        ),
                    )
                    last_demod_control_log_key = control_log_key

                with self.demod_state_lock:
                    self.latest_demod_state = demod_state
                    self.demod_lines = list(lines)
                    for line, message_time in line_records:
                        if game_start_wall_time is not None and message_time < game_start_wall_time:
                            continue
                        if line in seen_demod_ui_lines:
                            continue
                        seen_demod_ui_lines.add(line)
                        if "cmd=0x0A06" in line:
                            self.demod_jam_lines.append(line)
                            self.demod_jam_lines = self.demod_jam_lines[-12:]
                        elif "cmd=0x0A0" in line:
                            self.demod_info_lines.append(line)
                            self.demod_info_lines = self.demod_info_lines[-12:]
                            info_demod_count += 1
                            now = time.monotonic()
                            countdown = (
                                getattr(self.referee, "stage_remain_time", None)
                                if self.referee is not None
                                else None
                            )
                            if info_demod_first_time is None:
                                info_demod_first_time = now
                                info_demod_first_wall_time = message_time
                                info_demod_first_countdown = countdown
                            info_demod_last_time = now
                            info_demod_last_wall_time = message_time
                            info_demod_last_countdown = countdown
                    if latest_location is not None and latest_location.seq != last_seq:
                        self.demod_positions = self._build_demod_positions(
                            latest_location.value,
                            latest_location.time_stamp,
                        )
                        last_seq = latest_location.seq
                        self.summary_update_event.set()

                referee_level = None
                if self.referee is not None:
                    referee_level = int(getattr(self.referee, "encryption_level", 1))
                    if referee_level != snapshot["current_level"]:
                        self._append_match_log(
                            "解调",
                            f"同步裁判加密等级 {snapshot['current_level']} -> {referee_level}",
                        )
                        receiver.set_current_level(referee_level)
                        updated_snapshot = receiver.get_snapshot()
                        self._append_match_log(
                            "解调控制",
                            (
                                f"同步后 level={updated_snapshot['current_level']}/"
                                f"{updated_snapshot['target_level']} "
                                f"decode={int(updated_snapshot['decode_enabled'])} "
                                f"active={updated_snapshot['active_request_id']} "
                                f"success={updated_snapshot['success_request_id']} "
                                f"状态={updated_snapshot['last_control_status']}"
                            ),
                        )
                    break_key_correct = getattr(self.referee, "break_key_correct", None)
                    if break_key_correct is not last_break_key_correct:
                        if break_key_correct is False:
                            if self.last_jamming_key_id is not None:
                                failed_jamming_key_ids.add(self.last_jamming_key_id)
                            submitted_jamming_request_id = None
                            receiver.reject_pending_decode()
                            self._append_match_log("解调", "密钥验证失败")
                        elif break_key_correct is True:
                            if self.last_jamming_key_id is not None:
                                failed_jamming_key_ids.discard(self.last_jamming_key_id)
                            submitted_jamming_request_id = None
                            self._append_match_log(
                                "解调",
                                f"密钥验证成功，加密等级提升至 {referee_level}",
                            )
                        last_break_key_correct = break_key_correct

                if (
                    self.referee is not None
                    and latest_jamming_key is not None
                ):
                    key = latest_jamming_key.value.key
                    jamming_key_id = (latest_jamming_key.seq, key)
                    if jamming_key_id != self.last_jamming_key_id:
                        if not self.referee.game_start_flag:
                            now = time.monotonic()
                            if (
                                jamming_key_id != last_prestart_jamming_key_id
                                or now - last_wait_log_time >= 1.0
                            ):
                                logger.info(
                                    "Demod key decoded before game start, not sending to referee: "
                                    "progress={} remain={}s key={}",
                                    getattr(self.referee, "game_progress", -1),
                                    getattr(self.referee, "stage_remain_time", -1),
                                    key,
                                )
                                last_wait_log_time = now
                                last_prestart_jamming_key_id = jamming_key_id
                        else:
                            sent = self.referee.break_keys(key)
                            self.last_jamming_key_id = jamming_key_id
                            submitted_jamming_request_id = snapshot["success_request_id"]
                            if sent:
                                self._append_match_log("解调", f"发送破解密钥 key={key}")
                                logger.info(
                                    "Sent demodulated jamming key to referee system: seq={} key={} level={}",
                                    latest_jamming_key.seq,
                                    key,
                                    int(snapshot["current_level"]),
                                )
                            else:
                                self._append_match_log("解调", f"冷却中，缓存最新密钥 key={key}")
                    elif (
                        self.referee.game_start_flag
                        and snapshot["success_request_id"] is not None
                        and jamming_key_id in failed_jamming_key_ids
                        and snapshot["success_request_id"] != submitted_jamming_request_id
                        and snapshot["success_request_id"] not in rejected_duplicate_success_request_ids
                    ):
                        rejected_duplicate_success_request_ids.add(snapshot["success_request_id"])
                        receiver.reject_pending_decode()
                        self._append_match_log(
                            "解调",
                            f"重复失败密钥 key={key}，跳过提交并继续请求",
                        )

                time.sleep(0.05)
        except Exception:
            logger.exception("Error in demod loop.")
        finally:
            if info_demod_count > 0 and self.match_log_path is not None:
                elapsed = 0.0
                if info_demod_first_time is not None and info_demod_last_time is not None:
                    elapsed = info_demod_last_time - info_demod_first_time
                avg_freq = info_demod_count / elapsed if elapsed > 0 else 0.0
                first_text = "无"
                last_text = "无"
                if info_demod_first_wall_time is not None:
                    first_text = (
                        time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(info_demod_first_wall_time))
                        + f".{int((info_demod_first_wall_time % 1) * 1000):03d}"
                        + f" 倒计时={info_demod_first_countdown}s"
                    )
                if info_demod_last_wall_time is not None:
                    last_text = (
                        time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(info_demod_last_wall_time))
                        + f".{int((info_demod_last_wall_time % 1) * 1000):03d}"
                        + f" 倒计时={info_demod_last_countdown}s"
                    )
                self._append_match_log_final(
                    "解调统计",
                    (
                        f"本局信息波解调条数={info_demod_count} 平均频率={avg_freq:.2f}/s "
                        f"首条={first_text} 末条={last_text}"
                    ),
                )
            if receiver is not None:
                try:
                    receiver.stop()
                except Exception:
                    logger.exception("Failed to stop demod receiver cleanly.")

    def laser_loop_thread(self):
        """
        激光追踪线程
        """
        if self.laser_tracker is None:
            return

        try:
            self.laser_tracker.run(
                sub_frame_provider=self._get_laser_sub_frame,
                countermeasure_active_provider=self.is_laser_countermeasure_active,
                match_countdown_provider=self._get_match_countdown,
                stop_event=self.stop_event,
            )
        except Exception:
            logger.exception("激光追踪线程异常退出。")

    def _get_match_countdown(self):
        if self.referee is None or not self.referee.game_start_flag:
            return None
        return self.referee.stage_remain_time

    def is_laser_countermeasure_active(self):
        if self.referee is None:
            return not self.initiative_counter
        return self.countermeasure_gate.is_active(
            game_start_flag=bool(self.referee.game_start_flag),
            stage_remain_time=self.referee.stage_remain_time,
            success_count=self._get_countermeasure_success_count(),
            selected_target=self.referee.target,
        )

    def _get_countermeasure_success_count(self):
        if self.laser_tracker is None:
            return 0
        difficulty_tracker = getattr(self.laser_tracker, "difficulty_tracker", None)
        if difficulty_tracker is None:
            return 0
        return int(getattr(difficulty_tracker, "success_count", 0))


    def summary_and_send_loop_thread(self):
        """
        融合检测与解调结果
        """
        logger.info("Summary/send thread started in event-driven mode.")
        time.sleep(2)
        next_match_status_log_time = time.monotonic()

        while not self.stop_event.is_set():
            now = time.monotonic()
            self._update_match_log_lifecycle()
            if now >= next_match_status_log_time:
                self._append_enemy_status_log()
                next_match_status_log_time = now + 1.0

            triggered = self.summary_update_event.wait(timeout=0.1)
            if self.stop_event.is_set():
                break
            if not triggered: # 等待最新坐标更新后才触发
                if self.referee is not None:
                    self.referee.radar2robot_status_msg = self.pack_radar2robot_status_msg()
                else:
                    self._log_region_status_if_changed()
                continue

            self.summary_update_event.clear()

            with self.vision_state_lock:
                vision_positions = self._copy_positions(self.vision_positions)
            with self.demod_state_lock:
                demod_positions = self._copy_positions(self.demod_positions)

            fused_positions, fused_sources = self._fuse_positions(vision_positions, demod_positions)

            with self.divisions_lock:
                self.divisions_pos = fused_positions
                self.divisions_source = fused_sources

            if self.referee is not None:
                self.referee.set_radar2client_source_counts(
                    *self._count_radar2client_sources(fused_sources)
                )
                self.referee.radar2robot_status_msg = self.pack_radar2robot_status_msg()
                self.referee.radar2robot_location_msg = self.pack_radar2robot_location_msg()
                self.referee.radar2client_msg = self.pack_radar2clientmsg()
            else:
                self._log_region_status_if_changed()

    def pack_radar2robot_location_msg(self) -> Radar2RobotMessage:
        positions = self._get_divisions_snapshot()

        if self.faction == "red":
            is_blue = False
            enemy_class_ids = [5, 6, 7, 8, 11, 9]
        else:
            is_blue = True
            enemy_class_ids = [0, 1, 2, 3, 10, 4]

        def coo(class_id):
            pos = positions[class_id]
            if not pos.is_valid:
                return EnemyRobotCoo(0, -8888.0, -8888.0)
            return EnemyRobotCoo(1, pos.x / 100.0, pos.y / 100.0)

        frame = RadarLocationFrame(
            hero=coo(enemy_class_ids[0]),
            engineer=coo(enemy_class_ids[1]),
            infantry_3=coo(enemy_class_ids[2]),
            infantry_4=coo(enemy_class_ids[3]),
            aerial=coo(enemy_class_ids[4]),
            sentry=coo(enemy_class_ids[5]),
        )

        return Radar2RobotMessage(
            is_blue=is_blue,
            msg_ID=Radar2RobotMsgID.LOCATION,
            frame=frame,
        )

    def pack_radar2robot_status_msg(self) -> Radar2RobotMessage:
        status_frame = RadarStatusFrame()
        region_status = self._update_region_status_snapshot()
        referee_hp_received = (
            self.referee is not None
            and getattr(self.referee, "robot_hp_msg_received", False)
        )
        status_frame.enemy_outpost_is_destroyed = self._get_enemy_outpost_destroyed()
        status_frame.msg_is_reliable = int(referee_hp_received)
        status_frame.is_hero_strike = region_status["hero_strike"]
        status_frame.is_engineer_redeem = region_status["engineer_redeem"]
        status_frame.is_enemy_constrained_defense = region_status["enemy_constrained_defense"]
        status_frame.is_enemy_invade_fortress = region_status["enemy_invade_fortress"]
        status_frame.is_enemy_revive_outpost = region_status["enemy_revive_outpost"]
        with self.demod_state_lock:
            demod_state = self.latest_demod_state

        if demod_state is not None:
            hp = demod_state.hp.value if demod_state.hp is not None else None
            allowed_bullets = (
                demod_state.allowed_bullets.value
                if demod_state.allowed_bullets is not None
                else None
            )
            enemy_status = (
                demod_state.enemy_status.value
                if demod_state.enemy_status is not None
                else None
            )
            buff_status = (
                demod_state.buff_status.value
                if demod_state.buff_status is not None
                else None
            )
            status_frame.msg_is_reliable = int(
                referee_hp_received or any((hp, allowed_bullets, enemy_status, buff_status))
            )

            if hp is not None:
                status_frame.enemy_hp.enemy_hero = hp.hero_hp
                status_frame.enemy_hp.enemy_engineer = hp.eng_hp
                status_frame.enemy_hp.enemy_infantry_3 = hp.inf3_hp
                status_frame.enemy_hp.enemy_infantry_4 = hp.inf4_hp
                status_frame.enemy_hp.enemy_sentry = hp.sentry_hp

            if allowed_bullets is not None:
                status_frame.ammunition_allowed.enemy_hero = allowed_bullets.hero_bullets
                status_frame.ammunition_allowed.enemy_infantry_3 = allowed_bullets.inf3_bullets
                status_frame.ammunition_allowed.enemy_infantry_4 = allowed_bullets.inf4_bullets
                status_frame.ammunition_allowed.enemy_aerial = allowed_bullets.air_bullets
                status_frame.ammunition_allowed.enemy_sentry = allowed_bullets.sentry_bullets

            if buff_status is not None:
                status_frame.defense_buff.enemy_hero = buff_status.hero.defense_percent
                status_frame.defense_buff.enemy_engineer = buff_status.engineer.defense_percent
                status_frame.defense_buff.enemy_infantry_3 = buff_status.inf3.defense_percent
                status_frame.defense_buff.enemy_infantry_4 = buff_status.inf4.defense_percent
                status_frame.defense_buff.enemy_sentry = buff_status.sentry.defense_percent

                status_frame.defense_defense_reduction.enemy_hero = buff_status.hero.negative_defense_percent
                status_frame.defense_defense_reduction.enemy_engineer = buff_status.engineer.negative_defense_percent
                status_frame.defense_defense_reduction.enemy_infantry_3 = buff_status.inf3.negative_defense_percent
                status_frame.defense_defense_reduction.enemy_infantry_4 = buff_status.inf4.negative_defense_percent
                status_frame.defense_defense_reduction.enemy_sentry = buff_status.sentry.negative_defense_percent

                status_frame.hp_regen_buff.enemy_hero = buff_status.hero.heal_percent
                status_frame.hp_regen_buff.enemy_engineer = buff_status.engineer.heal_percent
                status_frame.hp_regen_buff.enemy_infantry_3 = buff_status.inf3.heal_percent
                status_frame.hp_regen_buff.enemy_infantry_4 = buff_status.inf4.heal_percent
                status_frame.hp_regen_buff.enemy_sentry = buff_status.sentry.heal_percent

                status_frame.heat_cooling_buff.enemy_hero = buff_status.hero.cooldown_reduction
                status_frame.heat_cooling_buff.enemy_engineer = buff_status.engineer.cooldown_reduction
                status_frame.heat_cooling_buff.enemy_infantry_3 = buff_status.inf3.cooldown_reduction
                status_frame.heat_cooling_buff.enemy_infantry_4 = buff_status.inf4.cooldown_reduction
                status_frame.heat_cooling_buff.enemy_sentry = buff_status.sentry.cooldown_reduction

                status_frame.attack_buff.enemy_hero = buff_status.hero.attack_percent
                status_frame.attack_buff.enemy_engineer = buff_status.engineer.attack_percent
                status_frame.attack_buff.enemy_infantry_3 = buff_status.inf3.attack_percent
                status_frame.attack_buff.enemy_infantry_4 = buff_status.inf4.attack_percent
                status_frame.attack_buff.enemy_sentry = buff_status.sentry.attack_percent
                status_frame.enemy_is_invincible.enemy_hero = buff_status.enemy_is_invincible.hero
                status_frame.enemy_is_invincible.enemy_engineer = buff_status.enemy_is_invincible.engineer
                status_frame.enemy_is_invincible.enemy_infantry_3 = buff_status.enemy_is_invincible.inf3
                status_frame.enemy_is_invincible.enemy_infantry_4 = buff_status.enemy_is_invincible.inf4
                status_frame.enemy_is_invincible.enemy_aerial = buff_status.enemy_is_invincible.aerial
                status_frame.enemy_is_invincible.enemy_sentry = buff_status.enemy_is_invincible.sentry

            if enemy_status is not None:
                status_frame.enemy_economy_remaining = enemy_status.gold_remain
                status_frame.enemy_economy_total = enemy_status.gold_total

        return Radar2RobotMessage(
            is_blue=self.faction == "blue",
            msg_ID=Radar2RobotMsgID.STATUS,
            frame=status_frame,
        )

    def _get_enemy_outpost_destroyed(self) -> int:
        if self.referee is None:
            return 0
        if not getattr(self.referee, "robot_hp_msg_received", False):
            return 0
        return int(int(getattr(self.referee, "enemy_outpost_hp", 0)) == 0)

    def _get_enemy_status_snapshot(self) -> dict[str, int]:
        region_status = self._update_region_status_snapshot()
        return {
            "enemy_outpost_is_destroyed": self._get_enemy_outpost_destroyed(),
            "is_hero_strike": region_status["hero_strike"],
            "is_engineer_redeem": region_status["engineer_redeem"],
            "is_enemy_constrained_defense": region_status["enemy_constrained_defense"],
            "is_enemy_invade_fortress": region_status["enemy_invade_fortress"],
            "is_enemy_revive_outpost": region_status["enemy_revive_outpost"],
        }

    def _append_enemy_status_log(self) -> None:
        snapshot = self._get_enemy_status_snapshot()
        self.last_enemy_status_log = snapshot
        content = (
            f"前哨摧毁={snapshot['enemy_outpost_is_destroyed']} "
            f"英雄吊射={snapshot['is_hero_strike']} "
            f"工程兑换={snapshot['is_engineer_redeem']} "
            f"登上地面堡垒={snapshot['is_enemy_constrained_defense']} "
            f"站上我方堡垒={snapshot['is_enemy_invade_fortress']} "
            f"位于前哨站={snapshot['is_enemy_revive_outpost']}"
        )
        self._append_match_log("敌方状态", content)

    def _update_region_status_snapshot(self) -> dict[str, int]:
        return {
            "hero_strike": int(self._update_region_status("hero_strike")),
            "engineer_redeem": int(self._update_region_status("engineer_redeem")),
            "enemy_constrained_defense": int(
                self._update_region_status("enemy_constrained_defense")
            ),
            "enemy_invade_fortress": int(
                self._update_region_status("enemy_invade_fortress")
            ),
            "enemy_revive_outpost": int(
                self._update_region_status("enemy_revive_outpost")
            ),
        }

    def _log_region_status_if_changed(self) -> None:
        snapshot = self._update_region_status_snapshot()
        if snapshot == self.last_region_status_snapshot:
            return
        self.last_region_status_snapshot = snapshot
        logger.info(
            "Region status: hero_strike={} engineer_redeem={} "
            "enemy_constrained_defense={} enemy_invade_fortress={} enemy_revive_outpost={}",
            snapshot["hero_strike"],
            snapshot["engineer_redeem"],
            snapshot["enemy_constrained_defense"],
            snapshot["enemy_invade_fortress"],
            snapshot["enemy_revive_outpost"],
        )

    def _update_region_status(self, detector_name: str) -> bool:
        detectors = self.region_stay_detectors[detector_name]
        if isinstance(detectors, RegionStayDetector):
            detectors = [detectors]
        positions = self._get_divisions_snapshot()
        is_any_active = False
        for detector in detectors:
            enemy_class_id = self._enemy_robot_class_id(detector.robot_name)
            pos = positions[enemy_class_id]
            if not pos.is_valid:
                is_active = detector.update(None, None)
            else:
                is_active = detector.update(pos.x / 100.0, pos.y / 100.0)
            is_any_active = is_any_active or is_active
        return is_any_active

    @staticmethod
    def _enemy_robot_class_id(robot_name: str) -> int:
        class_ids = {
            "R1": 0,
            "R2": 1,
            "R3": 2,
            "R4": 3,
            "R7": 4,
            "B1": 5,
            "B2": 6,
            "B3": 7,
            "B4": 8,
            "B7": 9,
        }
        return class_ids[robot_name]

    def pack_radar2clientmsg(self) -> Radar2ClientMessage:
        positions = self._get_divisions_snapshot()

        def get_xy(class_id):
            pos = positions[class_id]
            if not pos.is_valid:
                return 0, 0
            return int(pos.x), int(pos.y)

        if self.faction == "red":
            opponent_hero_x, opponent_hero_y = get_xy(5)
            opponent_engineer_x, opponent_engineer_y = get_xy(6)
            opponent_standard_3_x, opponent_standard_3_y = get_xy(7)
            opponent_standard_4_x, opponent_standard_4_y = get_xy(8)
            opponent_aircraft_x, opponent_aircraft_y = get_xy(11)
            opponent_sentry_x, opponent_sentry_y = get_xy(9)

            ally_hero_x, ally_hero_y = get_xy(0)
            ally_engineer_x, ally_engineer_y = get_xy(1)
            ally_standard_3_x, ally_standard_3_y = get_xy(2)
            ally_standard_4_x, ally_standard_4_y = get_xy(3)
            ally_aircraft_x, ally_aircraft_y = get_xy(10)
            ally_sentry_x, ally_sentry_y = get_xy(4)
        else:
            opponent_hero_x, opponent_hero_y = get_xy(0)
            opponent_engineer_x, opponent_engineer_y = get_xy(1)
            opponent_standard_3_x, opponent_standard_3_y = get_xy(2)
            opponent_standard_4_x, opponent_standard_4_y = get_xy(3)
            opponent_aircraft_x, opponent_aircraft_y = get_xy(10)
            opponent_sentry_x, opponent_sentry_y = get_xy(4)

            ally_hero_x, ally_hero_y = get_xy(5)
            ally_engineer_x, ally_engineer_y = get_xy(6)
            ally_standard_3_x, ally_standard_3_y = get_xy(7)
            ally_standard_4_x, ally_standard_4_y = get_xy(8)
            ally_aircraft_x, ally_aircraft_y = get_xy(11)
            ally_sentry_x, ally_sentry_y = get_xy(9)

        return Radar2ClientMessage(
            opponent_hero_x=opponent_hero_x,
            opponent_hero_y=opponent_hero_y,
            opponent_engineer_x=opponent_engineer_x,
            opponent_engineer_y=opponent_engineer_y,
            opponent_standard_3_x=opponent_standard_3_x,
            opponent_standard_3_y=opponent_standard_3_y,
            opponent_standard_4_x=opponent_standard_4_x,
            opponent_standard_4_y=opponent_standard_4_y,
            opponent_aircraft_x=opponent_aircraft_x,
            opponent_aircraft_y=opponent_aircraft_y,
            opponent_sentry_x=opponent_sentry_x,
            opponent_sentry_y=opponent_sentry_y,
            ally_hero_x=ally_hero_x,
            ally_hero_y=ally_hero_y,
            ally_engineer_x=ally_engineer_x,
            ally_engineer_y=ally_engineer_y,
            ally_standard_3_x=ally_standard_3_x,
            ally_standard_3_y=ally_standard_3_y,
            ally_standard_4_x=ally_standard_4_x,
            ally_standard_4_y=ally_standard_4_y,
            ally_aircraft_x=ally_aircraft_x,
            ally_aircraft_y=ally_aircraft_y,
            ally_sentry_x=ally_sentry_x,
            ally_sentry_y=ally_sentry_y,
        )

    """以下为给ui的可视化接口"""
    def get_ui_snapshot(self):
        with self.runtime_state_lock:
            inference_fps = self.inference_fps

        now = time.time()
        map_targets = []
        with self.divisions_lock:
            positions = self._copy_positions(self.divisions_pos)
            sources = list(self.divisions_source)
        for class_id, pos in enumerate(positions):
            if not pos.is_valid:
                continue
            source = sources[class_id] if class_id < len(sources) else "none"
            if source == "none":
                source = "vision"
            if source == "demod" and now - pos.time_stamp > self.demod_timeout:
                continue
            map_targets.append(
                {
                    "class_id": int(class_id),
                    "x_m": float(pos.x) / 100.0,
                    "y_m": float(pos.y) / 100.0,
                    "is_guess": False,
                    "source": source,
                }
            )

        with self.demod_state_lock:
            demod_lines = list(self.demod_lines)
            demod_info_lines = list(self.demod_info_lines)
            demod_jam_lines = list(self.demod_jam_lines)
        with self.match_log_lock:
            match_log_lines = list(self.match_log_lines)
        countermeasure_success_count = None if self.laser_tracker is None else self._get_countermeasure_success_count()

        return {
            "inference_fps": inference_fps,
            "map_targets": map_targets,
            "demod_lines": demod_lines,
            "demod_info_lines": demod_info_lines,
            "demod_jam_lines": demod_jam_lines,
            "match_log_lines": match_log_lines,
            "countermeasure_success_count": countermeasure_success_count,
        }

    def get_latest_track_vis_img(self):
        with self.runtime_state_lock:
            if self.track_vis_img is None:
                return None
            return self.track_vis_img.copy()

    def get_latest_laser_sub_vis_img(self):
        if self.laser_tracker is None:
            return None

        sub_vis_img, _ = self.laser_tracker.get_latest_ui_frames()
        return sub_vis_img

    def get_latest_laser_offset_vis_img(self):
        if self.laser_tracker is None:
            return None

        _, laser_offset_img = self.laser_tracker.get_latest_ui_frames()
        return laser_offset_img

    def _get_laser_sub_frame(self):
        if self.sub_camera is None:
            return None
        img_sub, _ = self.sub_camera.get_image_latest("laser_sub", timeout=0.02)
        return img_sub
