# -*- coding: utf-8 -*-
"""
python main.py --faction red --enable_laser_tracking --enable_referee
"""
import os
import sys
import time
import argparse
from loguru import logger
from pathlib import Path

# 在导入任何 Qt 相关模块之前设置 Qt 插件路径
# 确保 PyQt5 的插件路径优先级高于 OpenCV 的插件路径
for site_package in sys.path:
    if 'site-packages' in site_package:
        pyqt5_plugin_path = Path(site_package) / 'PyQt5' / 'Qt5' / 'plugins'
        if pyqt5_plugin_path.exists():
            os.environ["QT_PLUGIN_PATH"] = str(pyqt5_plugin_path)
            os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = str(pyqt5_plugin_path)
            break

from driver.referee.referee_comm import RefereeCommManager
from utils.config import (
    load_cfg_from_cfg_file,
    merge_cfg_from_args,
    resolve_runtime_flags,
)

from main_event_loop import MainEventLoop


def get_parser():
    parser = argparse.ArgumentParser(description="Pytorch Referring Expression Segmentation")
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

    args = parser.parse_args()

    cfg = load_cfg_from_cfg_file(args.config)
    cfg = merge_cfg_from_args(cfg, args)

    return cfg


def close_camera(main_camera):
    if main_camera is None:
        return

    for method_name in ("stop_streaming", "stop_saving_images", "close"):
        method = getattr(main_camera, method_name, None)
        if callable(method):
            method()

if __name__ == "__main__":
    args = get_parser()
    use_sub_camera, enable_laser_tracking = resolve_runtime_flags(args)

    logger.info("我方阵容为" "红方" if args.faction=='red' else "蓝方")
    logger.info("视觉定位{}", "开启" if args.enable_vision_localization else "关闭")
    logger.info("副相机{}", "开启" if use_sub_camera else "关闭")
    logger.info("激光追踪模式{}", "开启" if enable_laser_tracking else "关闭")
    logger.info("信息波解调{}", "开启" if args.enable_demod else "关闭")
    logger.info("串口通信{}", "开启" if args.enable_referee else "关闭")

    # 打开相机
    need_main_camera = bool(args.enable_vision_localization or args.record_main)
    main_camera = None
    sub_camera = None
    if args.use_video:
        if need_main_camera:
            from driver.hik_camera.mock_hik import SimpleHikCamera
            main_camera = SimpleHikCamera(video_source=args.video_path)
    else:
        from driver.hik_camera.hik import SimpleHikCamera
        if need_main_camera:
            main_camera = SimpleHikCamera(args.main_camera, camera_role="main")
        if use_sub_camera:
            logger.info("启用副相机")
            sub_camera = SimpleHikCamera(args.sub_camera, camera_role="sub")
    if main_camera:
        main_camera.start_streaming()
    if sub_camera:
        sub_camera.start_streaming()

    # 打开串口通信
    referee = None
    if args.enable_referee:
        referee_cfg = args.get("referee", {})
        referee = RefereeCommManager(
            port=referee_cfg.get("port"),
            baudrate=referee_cfg.get("baudrate", 115200),
            args=args,
        )
        referee.start()
    
    event_loop = MainEventLoop(
        config=args,
        main_camera=main_camera,
        sub_camera=sub_camera,
        referee=referee
    )
    
    event_loop.run()
    
    ## do not terminate the main eventloop
    try:
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("KeyboardInterrupt received, stopping...")
    finally:
        event_loop.stop()
        if referee is not None:
            referee.close()
        close_camera(sub_camera)
        close_camera(main_camera)
        
        
