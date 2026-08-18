from __future__ import annotations

import argparse
import csv
import os
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from driver.hik_camera.MvImport.MvCameraControl_class import MVCC_FLOATVALUE, MVCC_INTVALUE_EX
from driver.hik_camera.hik import SimpleHikCamera
from utils.config import load_cfg_from_cfg_file


def _get_int_ex(cam, name):
    value = MVCC_INTVALUE_EX()
    ret = cam.cam.MV_CC_GetIntValueEx(name, value)
    if ret != 0:
        return ret, None
    return ret, int(value.nCurValue)


def _get_float(cam, name):
    value = MVCC_FLOATVALUE()
    ret = cam.cam.MV_CC_GetFloatValue(name, value)
    if ret != 0:
        return ret, None
    return ret, float(value.fCurValue)


def _try_set_bool(cam, name, value):
    ret = cam.cam.MV_CC_SetBoolValue(name, bool(value))
    print(f"set {name}={bool(value)} ret=0x{ret:x}")
    return ret


def _try_set_enum_string(cam, name, value):
    ret = cam.cam.MV_CC_SetEnumValueByString(name, value)
    print(f"set {name}={value} ret=0x{ret:x}")
    return ret


def _enable_chunk(cam):
    _try_set_bool(cam, "ChunkModeActive", True)
    for selector in ("Exposure", "Timestamp"):
        if _try_set_enum_string(cam, "ChunkSelector", selector) == 0:
            _try_set_bool(cam, "ChunkEnable", True)


def _dev_timestamp(info):
    return (int(info.nDevTimeStampHigh) << 32) | int(info.nDevTimeStampLow)


def _print_node(cam, name, kind="int"):
    if kind == "float":
        ret, value = _get_float(cam, name)
    else:
        ret, value = _get_int_ex(cam, name)
    print(f"node {name}: ret=0x{ret:x} value={value}")
    return value


def main():
    parser = argparse.ArgumentParser(description="Probe Hik camera frame/exposure timestamp fields")
    parser.add_argument("--config", default="config/params.yaml")
    parser.add_argument("--role", choices=["sub", "main"], default="sub")
    parser.add_argument("--frames", type=int, default=80)
    parser.add_argument("--output", default=None)
    parser.add_argument("--no-chunk", action="store_true")
    args = parser.parse_args()

    cfg = load_cfg_from_cfg_file(args.config)
    cam_cfg = cfg.sub_camera if args.role == "sub" else cfg.main_camera
    cam = None
    rows = []
    try:
        cam = SimpleHikCamera(cam_cfg, camera_role=args.role)
        for step in ("_init_device", "_configure_basic"):
            ret = getattr(cam, step)()
            print(f"{step} ret=0x{ret:x}")
            if ret != 0:
                raise RuntimeError(f"{step} failed: 0x{ret:x}")
        if not args.no_chunk:
            _enable_chunk(cam)
        ret = cam._start_grabbing()
        print(f"_start_grabbing ret=0x{ret:x}")
        if ret != 0:
            raise RuntimeError(f"_start_grabbing failed: 0x{ret:x}")

        print("camera nodes before grabbing:")
        timestamp_increment = _print_node(cam, "DeviceTimestampIncrement")
        _print_node(cam, "DeviceTimestamp")
        _print_node(cam, "ChunkTimestamp")
        _print_node(cam, "ChunkExposure")
        _print_node(cam, "ExposureTime", kind="float")

        last = None
        print(
            "idx,py_after_mono,py_dt_ms,host_ts,host_dt,dev_ts,dev_dt,device_now,device_latency_ms,"
            "second,cycle,offset,chunk_ts,chunk_dt,chunk_exposure,frame_num,frame_counter,exposure_us"
        )
        for idx in range(args.frames):
            py_before_mono = time.monotonic()
            py_before_wall = time.time()
            ret = cam.cam.MV_CC_GetOneFrameTimeout(cam.data_buf, cam.nPayloadSize, cam.stFrameInfo, 1000)
            py_after_mono = time.monotonic()
            py_after_wall = time.time()
            if ret != 0:
                raise RuntimeError(f"MV_CC_GetOneFrameTimeout failed at frame {idx}: 0x{ret:x}")

            info = cam.stFrameInfo
            frame_dev_ts = _dev_timestamp(info)
            device_now = cam.get_device_timestamp()
            chunk_ts_ret, chunk_ts = _get_int_ex(cam, "ChunkTimestamp")
            chunk_exp_ret, chunk_exposure = _get_int_ex(cam, "ChunkExposure")
            row = {
                "idx": idx,
                "py_before_mono": py_before_mono,
                "py_after_mono": py_after_mono,
                "py_before_wall": py_before_wall,
                "py_after_wall": py_after_wall,
                "host_ts": int(info.nHostTimeStamp),
                "dev_ts": frame_dev_ts,
                "device_now": device_now,
                "device_latency_ms": (device_now - frame_dev_ts) / float(timestamp_increment) * 1000.0,
                "second": int(info.nSecondCount),
                "cycle": int(info.nCycleCount),
                "offset": int(info.nCycleOffset),
                "frame_num": int(info.nFrameNum),
                "frame_counter": int(info.nFrameCounter),
                "exposure_us": float(info.fExposureTime),
                "chunk_ts_ret": chunk_ts_ret,
                "chunk_ts": chunk_ts,
                "chunk_exposure_ret": chunk_exp_ret,
                "chunk_exposure": chunk_exposure,
                "timestamp_increment": timestamp_increment,
            }
            if last is None:
                py_dt_ms = None
                host_dt = None
                dev_dt = None
                chunk_dt = None
            else:
                py_dt_ms = (row["py_after_mono"] - last["py_after_mono"]) * 1000.0
                host_dt = row["host_ts"] - last["host_ts"]
                dev_dt = row["dev_ts"] - last["dev_ts"]
                chunk_dt = None if row["chunk_ts"] is None or last["chunk_ts"] is None else row["chunk_ts"] - last["chunk_ts"]
            row.update({"py_dt_ms": py_dt_ms, "host_dt": host_dt, "dev_dt": dev_dt, "chunk_dt": chunk_dt})
            rows.append(row)
            print(
                f"{idx},{py_after_mono:.9f},{'' if py_dt_ms is None else f'{py_dt_ms:.3f}'},"
                f"{row['host_ts']},{'' if host_dt is None else host_dt},"
                f"{row['dev_ts']},{'' if dev_dt is None else dev_dt},"
                f"{row['device_now']},{row['device_latency_ms']:.3f},"
                f"{row['second']},{row['cycle']},{row['offset']},"
                f"{'' if chunk_ts is None else chunk_ts},{'' if chunk_dt is None else chunk_dt},"
                f"{'' if chunk_exposure is None else chunk_exposure},"
                f"{row['frame_num']},{row['frame_counter']},{row['exposure_us']:.1f}"
            )
            last = row
    finally:
        if cam is not None:
            cam._stop_grabbing()
            cam._close_device()
            cam._finalize_sdk()

    output = args.output
    if output is None:
        os.makedirs("logs", exist_ok=True)
        output = f"logs/camera_timestamps_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    if rows:
        with open(output, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        print(f"saved {output}")


if __name__ == "__main__":
    main()
