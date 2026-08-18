import ctypes
import logging
import os
import queue
import threading
import time
from ctypes import *
from datetime import datetime, timezone, timedelta
from enum import Enum
from pathlib import Path
from queue import Queue
from threading import Condition, Event, Lock, Thread
from typing import Tuple

os.environ["MVCAM_COMMON_RUNENV"] = "/opt/MVS/lib"

import cv2
import numpy as np

from .MvImport.MvCameraControl_class import *
from utils.config import load_cfg_from_cfg_file

tz = timezone(timedelta(hours=8))

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

class HikState(Enum):
    DISABLED = 0
    WORKING = 1
    RECONNECTING = 2


class FrameData:
    def __init__(self, img_w, img_h):
        self.time_stamp = -1
        self.metadata = None
        self.frame_buffer = np.zeros((img_h, img_w, 3), dtype=np.uint8)


class RingBuffer:
    def __init__(self, num, img_w, img_h):
        self.num = num
        self.frames = [FrameData(img_w, img_h) for _ in range(num)]
        self.write_pos = -1
        self.lock = Lock()
        self.group_conditions = {}
        self.group_last_read = {}

    def register_group(self, group_id):
        with self.lock:
            if group_id not in self.group_conditions:
                self.group_conditions[group_id] = Condition(self.lock)
                self.group_last_read[group_id] = -1

    def put(self, data, time_stamp, metadata=None):
        with self.lock:
            self.write_pos = (self.write_pos + 1) % self.num
            self.frames[self.write_pos].frame_buffer = data
            self.frames[self.write_pos].time_stamp = time_stamp
            self.frames[self.write_pos].metadata = metadata
            for group_id, condition in self.group_conditions.items():
                condition.notify(n=1)

    def get_latest(self, group_id, timeout=1.0):
        with self.lock:
            if group_id not in self.group_conditions:
                raise ValueError(f"Group {group_id} not registered")
            condition = self.group_conditions[group_id]
            start_time = time.time()
            while True:
                if self.write_pos > self.group_last_read[group_id] or (
                    self.write_pos < self.group_last_read[group_id]
                    and self.write_pos + self.num > self.group_last_read[group_id]
                ):
                    self.group_last_read[group_id] = self.write_pos
                    return self.frames[self.write_pos]

                elapsed = time.time() - start_time
                if elapsed >= timeout:
                    return None

                remaining_timeout = timeout - elapsed
                condition.wait(remaining_timeout)

    def get_buffer(self, index):
        return self.frames[index]


class SimpleHikCamera:
    _enum_lock = threading.Lock()
    _sdk_lock = threading.Lock()
    _sdk_ref_count = 0
    
    # 定义主副相机的序列号
    MAIN_CAMERA_SERIAL = "DA7643021"  # 5472x3648
    SUB_CAMERA_SERIAL = "00L34964883"   # 1440x1080
    PIXEL_FORMATS = {
        "BayerRG8": (PixelType_Gvsp_BayerRG8, cv2.COLOR_BAYER_RG2BGR),
        "BayerGB8": (PixelType_Gvsp_BayerGB8, cv2.COLOR_BAYER_GB2BGR),
        "BayerBG8": (PixelType_Gvsp_BayerBG8, cv2.COLOR_BAYER_BG2BGR),
        "BayerGR8": (PixelType_Gvsp_BayerGR8, cv2.COLOR_BAYER_GR2BGR),
    }

    def __init__(self, args, camera_role="main"):
        self.logger = logging.getLogger(f"camera_driver_{camera_role}")
        self.cam = MvCamera()
        self.camera_role = camera_role
        self.stop_streaming_signal = None
        self.streaming_thread = None
        self.save_thread = None
        self.stop_save_signal = None
        self.enable_save = False
        self.video_writer = None
        self.video_path = None
        self.device_opened = False
        self.grabbing = False
        self.handle_created = False
        self.sdk_initialized = False
        self.device_timestamp_increment = None
        self.status = HikState.DISABLED
        self.error_counter = 0

        if self._init_sdk() != 0:
            raise RuntimeError("HikRobot SDK initialize failed")
        
        # 自动根据序列号选择设备索引
        devices = self.enum_devices()
        if not devices:
            raise RuntimeError("No HikRobot cameras found!")
        
        target_serial = self.MAIN_CAMERA_SERIAL if camera_role == "main" else self.SUB_CAMERA_SERIAL
        
        # 在枚举列表中寻找匹配序列号的设备
        self.device_info = next((d for d in devices if d['serial'] == target_serial), None)
        
        if self.device_info is None:
            self.logger.warning(f"Target serial {target_serial} for {camera_role} not found! Falling back to resolution-based selection.")
            # 如果序列号没找着，回退到分辨率排序逻辑
            sorted_devices = sorted(devices, key=lambda x: x['width'] * x['height'], reverse=True)
            if camera_role == "main":
                self.device_info = sorted_devices[0]
            else:
                self.device_info = sorted_devices[1] if len(sorted_devices) > 1 else sorted_devices[0]
            
        self.device_index = self.device_info['index']
        self.logger.info(f"Selected {camera_role} camera by serial {self.device_info['serial']}: {self.device_info['name']} "
                         f"(Index: {self.device_index}, Res: {self.device_info['width']}x{self.device_info['height']})")

        # save thread variables
        self.save_queue = Queue(maxsize=100)  # 限制队列大小防止内存溢出
        self.save_directory = "saved_videos"
        self.frame_counter = 0
        # fps calculation
        self.now = time.time()
        self.last = time.time()
        self.fps = 0.0

        self.width = args.width
        self.height = args.height
        self.args = args
        self.exposure = args.exposure_time
        self.gain = args.gain
        self.pixel_format_name = args.format
        if self.pixel_format_name not in self.PIXEL_FORMATS:
            supported_formats = ", ".join(self.PIXEL_FORMATS)
            raise ValueError(
                f"Unsupported camera format {self.pixel_format_name}. "
                f"Supported formats: {supported_formats}"
            )
        self.pixel_format, self.cv_bayer_code = self.PIXEL_FORMATS[self.pixel_format_name]
        self._init_buffer()
        # self.__class__._instance = self
        
        self.recording_workers_num = args.recording_workers_num
        self.recording_save_root_dir = args.recording_save_root_dir
    def _init_sdk(self):
        with self.__class__._sdk_lock:
            if self.sdk_initialized:
                return 0
            if self.__class__._sdk_ref_count == 0:
                ret = MvCamera.MV_CC_Initialize()
                if ret != 0:
                    self.logger.error(f"SDK initialize failed! Error code: {hex(ret)}")
                    return ret
            self.__class__._sdk_ref_count += 1
            self.sdk_initialized = True
            return 0

    def _finalize_sdk(self):
        with self.__class__._sdk_lock:
            if not self.sdk_initialized:
                return
            self.__class__._sdk_ref_count = max(0, self.__class__._sdk_ref_count - 1)
            self.sdk_initialized = False
            if self.__class__._sdk_ref_count == 0:
                ret = MvCamera.MV_CC_Finalize()
                if ret != 0:
                    self.logger.warning(f"Finalize SDK failed! Error code: {hex(ret)}")

    def _init_device(self):
        device_list = MV_CC_DEVICE_INFO_LIST()
        ret = self.cam.MV_CC_EnumDevices(MV_USB_DEVICE, device_list)
        if ret != 0:
            self.logger.error(f"Enum devices failed! Error code: {hex(ret)}")
            return ret

        if device_list.nDeviceNum <= self.device_index:
            self.logger.error(f"Device index {self.device_index} out of range (total {device_list.nDeviceNum} devices)")
            ret = 0xFF
            return ret

        self._print_device_info(device_list)
        stDeviceInfo = cast(
            device_list.pDeviceInfo[self.device_index], POINTER(MV_CC_DEVICE_INFO)
        ).contents
        ret = self.cam.MV_CC_CreateHandle(stDeviceInfo)
        if ret != 0:
            self.logger.error(f"Create handle failed! Error code: {hex(ret)}")
            return ret
        self.handle_created = True
        ret = self.cam.MV_CC_OpenDevice()
        if ret != 0:
            self.logger.error(f"Open device failed! Error code: {hex(ret)}")
            self._close_device()
            return ret
        self.device_opened = True
        return ret

    def _init_buffer(self):

        self.stFrameInfo = MV_FRAME_OUT_INFO_EX()
        self.ring_buffer = RingBuffer(num=6, img_h=self.height, img_w=self.width)
        self.nPayloadSize = self.width * self.height
        self.data_buf = (ctypes.c_ubyte * (self.width * self.height))()
        # self.__class__._instance = self # Removed singleton assignment

    def _print_device_info(self, device_list):
        self.logger.info(f"Found {device_list.nDeviceNum} devices:")
        for i in range(device_list.nDeviceNum):
            dev_info = cast(
                device_list.pDeviceInfo[i], POINTER(MV_CC_DEVICE_INFO)
            ).contents
            if dev_info.nTLayerType == MV_USB_DEVICE:
                usb_info = dev_info.SpecialInfo.stUsb3VInfo

                # Device name
                name_bytes = bytearray(usb_info.chUserDefinedName)
                device_name = name_bytes.split(b"\x00")[0].decode(
                    "ascii", errors="ignore"
                )

                # Serial Number
                serial_bytes = bytearray(usb_info.chSerialNumber)
                serial_num = serial_bytes.split(b"\x00")[0].decode(
                    "ascii", errors="ignore"
                )

                self.logger.info(f"Device {i}: {device_name}")
                self.logger.info(f"Serial: {serial_num}")

    def _get_int_value(self, name):
        stInt = MVCC_INTVALUE()
        ret = self.cam.MV_CC_GetIntValue(name, stInt)
        if ret != 0:
            self.logger.error(f"Get {name} failed! Error code: {hex(ret)}")
        return stInt.nCurValue

    def _get_int_value_ex(self, name):
        stInt = MVCC_INTVALUE_EX()
        ret = self.cam.MV_CC_GetIntValueEx(name, stInt)
        if ret != 0:
            raise RuntimeError(f"Get {name} failed! Error code: {hex(ret)}")
        return int(stInt.nCurValue)

    def _set_command_value(self, name):
        ret = self.cam.MV_CC_SetCommandValue(name)
        if ret != 0:
            raise RuntimeError(f"Set command {name} failed! Error code: {hex(ret)}")

    def _get_enum_value(self, name):
        stEnum = MVCC_ENUMVALUE()
        ret = self.cam.MV_CC_GetEnumValue(name, stEnum)
        if ret != 0:
            self.logger.error(f"Get {name} failed! Error code: {hex(ret)}")
        return stEnum.nCurValue

    def _get_float_value(self, name):
        stFloat = MVCC_FLOATVALUE()
        ret = self.cam.MV_CC_GetFloatValue(name, stFloat)
        if ret != 0:
            self.logger.error(f"Get {name} failed! Error code: {hex(ret)}")
        return stFloat.fCurValue

    def _configure_basic(self):
        params = [
            ("PixelFormat", self.pixel_format, "enum"),
            ("AcquisitionMode", MV_ACQ_MODE_CONTINUOUS, "enum"),
            ("TriggerMode", MV_TRIGGER_MODE_OFF, "enum"),
            ("ExposureAuto", MV_EXPOSURE_AUTO_MODE_OFF, "enum"),
            ("GainAuto", MV_GAIN_MODE_OFF, "enum"),
            ("BalanceWhiteAuto", MV_BALANCEWHITE_AUTO_CONTINUOUS, "enum"),
            ("GammaSelector", MV_GAMMA_SELECTOR_USER, "enum"),
            ("AcquisitionFrameRate", self.args.acquisition_rate, "float"),
            ("ExposureTime", self.args.exposure_time, "float"),
            ("Gain", self.args.gain, "float"),
            ("Width", self.args.width, "int"),
            ("Height", self.args.height, "int"),
        ]

        for name, value, value_type in params:
            if value_type == "float":
                self.cam.MV_CC_SetFloatValue(name, value)
            elif value_type == "enum":
                self.cam.MV_CC_SetEnumValue(name, value)
            elif value_type == "int":
                self.cam.MV_CC_SetIntValue(name, value)
            elif value_type == "bool":
                self.cam.MV_CC_SetBoolValue(name, value)

        has_gamma_enable = (
            "gamma_enable" in self.args
            if hasattr(self.args, "__contains__")
            else hasattr(self.args, "gamma_enable")
        )
        if has_gamma_enable:
            gamma_enable = bool(self.args.gamma_enable)
            gamma = float(self.args.gamma) if gamma_enable else 1.0
            if not self.set_gamma(gamma, enable=gamma_enable):
                return 1

        time.sleep(0.05)
        ## Check params
        width = self._get_int_value("Width")
        if width != self.width:
            self.logger.error(
                f"Camera width {width} does not match the configuration width {self.width}"
            )
            return 1

        height = self._get_int_value("Height")
        if height != self.height:
            self.logger.error(
                f"Camera height {height} does not match the configuration width {self.height}"
            )
            return 1

        pixel_format = self._get_enum_value("PixelFormat")

        if pixel_format != self.pixel_format:
            self.logger.error(
                f"Camera pixel format {pixel_format} does not match configured {self.pixel_format_name}"
            )
            return 1

        self.device_timestamp_increment = self._get_int_value_ex("DeviceTimestampIncrement")

        return 0

    def get_device_timestamp(self):
        self._set_command_value("DeviceTimestampLatch")
        return self._get_int_value_ex("DeviceTimestamp")

    def get_device_timestamp_increment(self):
        if self.device_timestamp_increment is None:
            self.device_timestamp_increment = self._get_int_value_ex("DeviceTimestampIncrement")
        return self.device_timestamp_increment

    @staticmethod
    def _frame_device_timestamp(frame_info):
        return (int(frame_info.nDevTimeStampHigh) << 32) | int(frame_info.nDevTimeStampLow)

    def set_exposure(self, exposure: float):
        """
        Set the exposure time of the camera.
        Args:
            exposure (float): Exposure time in microseconds.
        """
        ret = self.cam.MV_CC_SetFloatValue("ExposureTime", exposure)
        if ret != 0:
            self.logger.error(f"Set exposure failed! Error code: {hex(ret)}")
            return False
        else:
            self.logger.info(f"Exposure set to {exposure} seconds")
        self.exposure = exposure
        return True 
    
    def set_gain(self, gain: float):
        """
        Set the gain of the camera
        Args:
            exposure (float): Gain value.
        """
        ret = self.cam.MV_CC_SetFloatValue("Gain", gain)
        if ret != 0:
            self.logger.error(f"Set gain failed! Error code: {hex(ret)}")
            return False
        else:
            self.logger.info(f"Gain set to {gain}")
        self.gain = gain
        return True

    def set_gamma(self, gamma: float, enable: bool = True):
        if enable and not 0.1 <= gamma <= 4.0:
            raise ValueError("Gamma must be in [0.1, 4.0]")

        if enable:
            ret = self.cam.MV_CC_SetEnumValue("GammaSelector", MV_GAMMA_SELECTOR_USER)
            if ret != 0:
                self.logger.error(f"Set GammaSelector failed! Error code: {hex(ret)}")
                return False
            ret = self.cam.MV_CC_SetBoolValue("GammaEnable", True)
            if ret != 0:
                self.logger.error(f"Set GammaEnable failed! Error code: {hex(ret)}")
                return False
            ret = self.cam.MV_CC_SetFloatValue("Gamma", gamma)
            if ret != 0:
                self.logger.error(f"Set Gamma failed! Error code: {hex(ret)}")
                return False
        else:
            ret = self.cam.MV_CC_SetBoolValue("GammaEnable", False)
            if ret != 0:
                self.logger.error(f"Set GammaEnable failed! Error code: {hex(ret)}")
                return False

        self.gamma_enable = bool(enable)
        self.gamma = gamma
        return True

    def get_gamma_state(self):
        gamma_enable = c_bool(False)
        ret = self.cam.MV_CC_GetBoolValue("GammaEnable", gamma_enable)
        if ret != 0:
            raise RuntimeError(f"Get GammaEnable failed: {hex(ret)}")

        gamma = MVCC_FLOATVALUE()
        if not gamma_enable.value:
            return False, None

        ret = self.cam.MV_CC_GetFloatValue("Gamma", gamma)
        if ret != 0:
            raise RuntimeError(f"Get Gamma failed: {hex(ret)}")

        return gamma_enable.value, gamma.fCurValue
    
    def _get_formatted_time(self):
        return datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

    def get_exposure(self):
        """
        Get the current exposure time of the camera.
        Returns:
            float: Current exposure time in microseconds.
        """
        return self.exposure

    def get_gain(self):
        return self.gain

    def is_connected(self):
        return self.status == HikState.WORKING

    def capture_one_frame(self):
        ret = self.cam.MV_CC_GetOneFrameTimeout(
            self.data_buf, self.nPayloadSize, self.stFrameInfo, 1000
        )
        # self.cam.MV_CC_StopGrabbing()

        if ret != 0:
            self.logger.error(f"Get frame failed! Error code: {hex(ret)}")

        else:
            self.logger.info("Get one frame success")

        width = self.stFrameInfo.nWidth
        height = self.stFrameInfo.nHeight
        pixel_format = self.stFrameInfo.enPixelType
        buf_view = memoryview(self.data_buf).cast("B")

        # if pixel_format != PixelType_Gvsp_BayerGB8:
        if pixel_format != PixelType_Gvsp_BayerRG8:
            self.logger.error(f"Unsupported format: {pixel_format}")

        return {
            "data": buf_view,
            "width": width,
            "height": height,
            "pixel_format": pixel_format,
            "frame_info": self.stFrameInfo,
        }

    def start_streaming(self):
        if self.streaming_thread is not None and self.streaming_thread.is_alive():
            self.logger.warning("Streaming thread is already running")
            return
        self.stop_streaming_signal = Event()
        self.streaming_thread = Thread(target=self.streaming_thread_impl)
        self.status = HikState.RECONNECTING
        self.streaming_thread.start()
        self.logger.info("Started streaming")

    def stop_streaming(self):
        if self.stop_streaming_signal is None or self.streaming_thread is None:
            self.logger.warning(
                "Need to start streaming before calling stopping, exiting"
            )
            return
        self.stop_streaming_signal.set()
        if self.streaming_thread.is_alive():
            self.streaming_thread.join(timeout=3.0)
            if self.streaming_thread.is_alive():
                self.logger.warning("Streaming thread did not stop within timeout")
        self.streaming_thread = None
        self.stop_streaming_signal = None
        self._stop_grabbing()
        self.logger.info("Stopped streaming")

    def _create_save_directory(self):
        """创建保存视频的目录"""
        timestamp = self._get_formatted_time()
        timestamp = timestamp.replace(" ", "_").replace(":", "-")
        self.save_directory = f"{self.recording_save_root_dir}/saved_videos_{timestamp}"
        Path(self.save_directory).mkdir(parents=True, exist_ok=True)
        self.logger.info(f"Created save directory: {self.save_directory}")
        
    def _open_video_writer(self, frame_shape):
        height, width = frame_shape[:2]
        timestamp = self._get_formatted_time().replace(" ", "_").replace(":", "-")
        filename = f"{self.camera_role}_{timestamp}.mp4"
        self.video_path = os.path.join(self.save_directory, filename)

        fps = float(getattr(self.args, "acquisition_rate", 19.0))
        fps = max(fps, 1.0)
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        self.video_writer = cv2.VideoWriter(self.video_path, fourcc, fps, (width, height))

        if not self.video_writer.isOpened():
            self.logger.error(f"Failed to open video writer: {self.video_path}")
            self.video_writer.release()
            self.video_writer = None
            self.video_path = None
            return False

        self.logger.info(f"Started recording video to: {self.video_path}")
        return True

    def save_thread_impl(self):
        """按采集顺序将帧写入 mp4 视频文件。"""
        self.logger.info("Video recording thread started")

        try:
            while not self.stop_save_signal.is_set() or not self.save_queue.empty():
                try:
                    _, rgb_image = self.save_queue.get(timeout=0.1)
                except queue.Empty:
                    continue

                try:
                    bgr_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)

                    if self.video_writer is None and not self._open_video_writer(bgr_image.shape):
                        self.enable_save = False
                        continue

                    self.video_writer.write(bgr_image)

                    with self.lock:
                        self.frame_counter += 1
                        if self.frame_counter % 100 == 0:
                            self.logger.info(f"Recorded {self.frame_counter} frames")
                finally:
                    self.save_queue.task_done()
        except Exception as e:
            self.logger.error(f"Error in recording thread: {str(e)}")
        finally:
            if self.video_writer is not None:
                self.video_writer.release()
                self.video_writer = None
                self.logger.info(f"Recording saved to: {self.video_path}")

    # def save_thread_impl(self):
    #     """保存图像的线程实现"""
    #     self.get_logger().info("Image save thread started")
    #     last = time.time()
    #     while not self.stop_save_signal.is_set():
    #         try:
    #             # 从队列中获取图像数据，超时时间1秒
    #             if not self.save_queue.empty():
    #                 image_data = self.save_queue.get(timeout=1.0)
    #                 timestamp, rgb_image = image_data
                    
    #                 # 生成文件名
    #                 filename = f"frame_{self.frame_counter:06d}_{timestamp}.jpg"
    #                 filepath = os.path.join(self.save_directory, filename)
                    
    #                 # 转换为BGR格式保存
    #                 bgr_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2BGR)
                    
    #                 # 保存图像
    #                 success = cv2.imwrite(filepath, bgr_image)
    #                 if success:
    #                     self.frame_counter += 1
    #                     if self.frame_counter % 100 == 0:  # 每100帧打印一次日志
    #                         self.get_logger().info(f"Saved {self.frame_counter} frames")
    #                 else:
    #                     self.get_logger().error(f"Failed to save image: {filepath}")
                        
    #                 self.save_queue.task_done()
    #             else:
    #                 time.sleep(0.01)  # 队列为空时短暂休眠
                
    #             self.get_logger().info(
    #                 f"Image save fps: {1.0 / (time.time() - last):.2f}"
    #             )
    #             last = time.time()
                
                    
    #         except Exception as e:
    #             self.get_logger().error(f"Error in save thread: {str(e)}")
    #             time.sleep(0.1)
        
    #     self.get_logger().info("Image save thread stopped")

    # def start_saving_images(self):
    #     """开始保存图像"""
    #     if self.save_thread is not None and self.save_thread.is_alive():
    #         self.get_logger().warning("Save thread is already running")
    #         return
        
    #     self._create_save_directory()
    #     self.enable_save = True
    #     self.frame_counter = 0
    #     self.stop_save_signal = Event()
    #     self.save_thread = Thread(target=self.save_thread_impl)
    #     self.save_thread.start()
    #     self.get_logger().info("Started saving images")
    def start_saving_threads(self):
        """启动后台线程，将采集画面录制为 mp4。"""
        if self.save_thread is not None and self.save_thread.is_alive():
            self.logger.warning("Save thread is already running")
            return
        self._create_save_directory()
        self.enable_save = True
        self.frame_counter = 0
        self.video_path = None
        self.video_writer = None
        self.save_queue = queue.Queue(maxsize=100)
        self.stop_save_signal = threading.Event()
        self.lock = threading.Lock()  # 用于线程安全计数
        self.save_thread = Thread(target=self.save_thread_impl, daemon=False)
        self.save_thread.start()
    

    def stop_saving_images(self):
        """停止录制并关闭 mp4 文件。"""
        if self.save_thread is None or not self.save_thread.is_alive():
            self.logger.warning("Save thread is not running")
            return
        
        self.enable_save = False
        self.stop_save_signal.set()
        self.save_thread.join()
        self.save_thread = None
        self.stop_save_signal = None
        self.logger.info(f"Stopped recording. Total saved: {self.frame_counter} frames")

    def streaming_thread_impl(self):
        time.sleep(0.1)
        while not self.stop_streaming_signal.is_set():
            if self.status == HikState.WORKING:
                if self.error_counter > 5:
                    self.status = HikState.RECONNECTING
                    self._close_device()
                    self.cam = MvCamera()
                    self.fps = 0.0
                    time.sleep(0.1)

            elif self.status == HikState.RECONNECTING:
                init_ok = self._init_sdk() == 0 and self._init_device() == 0
                if init_ok and self._configure_basic() != 0:
                    self._close_device()
                    self.cam = MvCamera()
                    time.sleep(0.2)
                    continue
                if init_ok and self._start_grabbing() != 0:
                    self._close_device()
                    self.cam = MvCamera()
                    time.sleep(0.2)
                    continue
                if init_ok:
                    self.error_counter = 0
                    self.status = HikState.WORKING
                    time.sleep(1)
            else:
                raise ValueError("The hik camera should not be disabled when running")

            if self.status == HikState.WORKING:
                ret = self.cam.MV_CC_GetOneFrameTimeout(
                    self.data_buf,
                    self.nPayloadSize,
                    self.stFrameInfo,
                    1000,
                )
                if ret != 0:
                    self.logger.error(f"Get frame failed! Error code: {hex(ret)}")
                    self.error_counter += 1
                    time.sleep(0.05)
                    continue
                else:
                    self.error_counter = 0
                time_stamp = time.time()
                frame_device_timestamp = self._frame_device_timestamp(self.stFrameInfo)
                recorded_time_stamp = self._get_formatted_time()
                np_data_buf = np.frombuffer(
                    self.data_buf,
                    dtype=np.uint8,
                ).reshape(self.height, self.width)
                
                rgb = cv2.cvtColor(np_data_buf, self.cv_bayer_code)
                rgb.flags.writeable = False
                self.ring_buffer.put(
                    rgb,
                    time_stamp,
                    metadata={
                        "device_timestamp": frame_device_timestamp,
                        "device_timestamp_increment": self.get_device_timestamp_increment(),
                        "host_timestamp": int(self.stFrameInfo.nHostTimeStamp),
                        "wall_timestamp": time_stamp,
                    },
                )

                # sace the frames
                if self.enable_save and not self.save_queue.full():
                    try:
                        self.save_queue.put(
                            (recorded_time_stamp, rgb), block=False
                        )
                    except:
                        pass

                self.now = time.time()
                self.fps = 0.8 * self.fps + 0.2 / (self.now - self.last + 1e-8)

                if self.args.display_fps:
                    self.logger.info("FPS {}".format(self.fps))
                self.last = self.now
                time.sleep(0.01)

                # self.cam.MV_CC_ClearImageBuffer()

                # self.get_logger().info(
                #     "Capture 1 frame. Timestamp: {:.4f}".format(
                #         self.get_clock().now().nanoseconds / 1e9,
                #     )
                # )
            elif self.status == HikState.RECONNECTING:
                time.sleep(0.2)

        self._stop_grabbing()
        print("Streaming thread stop by signal")

    def register_group(self, group_id: str):
        self.ring_buffer.register_group(group_id)

    def get_image_latest(
        self, group_id: str = "ptda", timeout: float = 1.0
    ) -> Tuple[np.ndarray, float]:
        """
        Args:
            timeout: float, maximum time to wait for an image in seconds
        Returns:
            tuple: (image: np.ndarray, time_stamp: float)
        Raises:
            TimeoutError: not raised explicitly, but logs error on timeout
        """

        frame_data = self.ring_buffer.get_latest(group_id=group_id, timeout=timeout)
        if frame_data is None:
            return None, None

        img_data = frame_data.frame_buffer
        img_data.flags.writeable = False
        time_stamp = frame_data.time_stamp
        return img_data, time_stamp

    def get_image_latest_with_metadata(
        self, group_id: str = "ptda", timeout: float = 1.0
    ) -> Tuple[np.ndarray, float, dict]:
        frame_data = self.ring_buffer.get_latest(group_id=group_id, timeout=timeout)
        if frame_data is None:
            return None, None, None

        img_data = frame_data.frame_buffer
        img_data.flags.writeable = False
        return img_data, frame_data.time_stamp, frame_data.metadata

    def get_time(self):
        return time.time()

    def get_fps(self):
        return self.fps

    def _close_device(self):
        self._stop_grabbing()
        if self.device_opened:
            ret = self.cam.MV_CC_CloseDevice()
            if ret != 0:
                self.logger.warning(f"Close device failed! Error code: {hex(ret)}")
            self.device_opened = False
        if self.handle_created:
            ret = self.cam.MV_CC_DestroyHandle()
            if ret != 0:
                self.logger.warning(f"Destroy handle failed! Error code: {hex(ret)}")
            self.handle_created = False
        self._finalize_sdk()

    def _start_grabbing(self):
        ret = self.cam.MV_CC_StartGrabbing()
        if ret == 0:
            self.grabbing = True
        return ret

    def _stop_grabbing(self):
        if not self.grabbing:
            return
        ret = self.cam.MV_CC_StopGrabbing()
        if ret != 0:
            self.logger.warning(f"Stop grabbing failed! Error code: {hex(ret)}")
        self.grabbing = False

    def close(self):
        if getattr(self, "status", HikState.DISABLED) == HikState.DISABLED:
            if getattr(self, "sdk_initialized", False):
                self._finalize_sdk()
            return
        if self.save_thread and self.save_thread.is_alive():
            self.stop_saving_images()
            self.logger.info("Save thread killed")
        if self.streaming_thread is not None:
            self.stop_streaming()
            self.logger.info("Streaming thread killed")
        if self.cam:
            self._close_device()

        self.logger.info("Camera is closed gracefully")
        self.status = HikState.DISABLED

    @staticmethod
    def enum_devices():
        """
        获取所有连接的海康相机设备信息，包括分辨率
        Returns:
            list: 包含设备信息的字典列表
        """
        # 1. 枚举设备列表
        device_list = MV_CC_DEVICE_INFO_LIST()
        ret = MvCamera.MV_CC_EnumDevices(MV_USB_DEVICE, device_list)
        if ret != 0:
            return []

        devices = []
        for i in range(device_list.nDeviceNum):
            dev_info = cast(device_list.pDeviceInfo[i], POINTER(MV_CC_DEVICE_INFO)).contents
            if dev_info.nTLayerType == MV_USB_DEVICE:
                usb_info = dev_info.SpecialInfo.stUsb3VInfo
                
                # 解析基本信息
                name_bytes = bytearray(usb_info.chUserDefinedName)
                device_name = name_bytes.split(b"\x00")[0].decode("ascii", errors="ignore")
                if not device_name:
                    model_bytes = bytearray(usb_info.chModelName)
                    device_name = model_bytes.split(b"\x00")[0].decode("ascii", errors="ignore")

                serial_bytes = bytearray(usb_info.chSerialNumber)
                serial_num = serial_bytes.split(b"\x00")[0].decode("ascii", errors="ignore")

                # 2. 获取分辨率（需要临时创建句柄并打开设备）
                width, height = 0, 0
                temp_cam = MvCamera()
                try:
                    if temp_cam.MV_CC_CreateHandle(dev_info) == 0:
                        if temp_cam.MV_CC_OpenDevice() == 0:
                            stIntWidth = MVCC_INTVALUE()
                            stIntHeight = MVCC_INTVALUE()
                            if temp_cam.MV_CC_GetIntValue("Width", stIntWidth) == 0:
                                width = stIntWidth.nCurValue
                            if temp_cam.MV_CC_GetIntValue("Height", stIntHeight) == 0:
                                height = stIntHeight.nCurValue
                            temp_cam.MV_CC_CloseDevice()
                        temp_cam.MV_CC_DestroyHandle()
                except Exception as e:
                    logging.error(f"Error probing device {i}: {e}")

                devices.append({
                    "index": i,
                    "name": device_name,
                    "serial": serial_num,
                    "width": width,
                    "height": height
                })
        return devices

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="海康相机测试程序")
    parser.add_argument("--mode", type=str, choices=["main", "sub", "both"], default="main", 
                        help="选择打开的相机: main(主相机), sub(副相机), both(两个都打开)")
    parser.add_argument("--gamma", type=float, default=None,
                        help="设置相机 Gamma，范围 [0.1, 4.0]；不传则保持相机当前配置")
    args_cli = parser.parse_args()

    config = load_cfg_from_cfg_file("config/params.yaml")
    
    cameras = []
    
    try:

        configs_to_open = []
        if args_cli.mode in ["main", "both"]:
            configs_to_open.append((config.main_camera, "main", "Main_Camera"))
        if args_cli.mode in ["sub", "both"]:
            sub_cfg = config.get("sub_camera", config.sub_camera)
            configs_to_open.append((sub_cfg, "sub", "Sub_Camera"))

        # 初始化并启动所有选中的相机
        for cfg, role, name in configs_to_open:
            print(f"\n[INFO] 正在启动 {name} (Role: {role})...")
            if args_cli.gamma is not None:
                if not 0.1 <= args_cli.gamma <= 4.0:
                    raise ValueError("Gamma must be in [0.1, 4.0]")
                cfg.gamma = args_cli.gamma
                cfg.gamma_enable = True
            cam = SimpleHikCamera(cfg, camera_role=role)
            cam.start_streaming()
            if args_cli.gamma is not None:
                for _ in range(100):
                    if cam.status == HikState.WORKING:
                        break
                    time.sleep(0.05)
                if cam.status != HikState.WORKING:
                    raise RuntimeError(f"{name} failed to start after Gamma config")
                gamma_enabled, current_gamma = cam.get_gamma_state()
                if abs(current_gamma - args_cli.gamma) > 1e-3:
                    raise RuntimeError(f"{name} Gamma mismatch: expected {args_cli.gamma}, got {current_gamma}")
                if not gamma_enabled:
                    raise RuntimeError(f"{name} GammaEnable is false")
                print(f"[INFO] {name} Gamma set to {current_gamma}")
            cam.register_group("test")
            cameras.append((cam, name))

            print(f"已初始化{name}")

        print("\n[INFO] 所有相机已启动。按 'q' 退出，按 's' 保存当前帧。")

        while True:
            for cam, name in cameras:
                img_rgb, timestamp = cam.get_image_latest("test", timeout=0.1) # 驱动返回的是RGB图像
                
                if img_rgb is not None:
                    # 缩放显示
                    display_rgb = cv2.resize(img_rgb, dsize=(640, 480), interpolation=cv2.INTER_LINEAR)
                    display_bgr = cv2.cvtColor(display_rgb, code=cv2.COLOR_RGB2BGR)
                    
                    # 在画面上标注相机名称
                    cv2.putText(display_bgr, name, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    cv2.imshow(name, display_bgr)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                os.makedirs("demo", exist_ok=True)
                for cam, name in cameras:
                    img_rgb, _ = cam.get_image_latest("test", timeout=0.5)
                    if img_rgb is not None:
                        save_path = f"demo/test_{name}.jpg"
                        save_img = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
                        cv2.imwrite(save_path, save_img)
                        print(f"--- [INFO] 已保存 {name} 帧至 {save_path} ---")

    except KeyboardInterrupt:
        print("\n[INFO] 用户停止推流")
    except Exception as e:
        import traceback
        print(f"\n[ERROR] 发生错误: {traceback.format_exc()}")
    finally:
        for cam, name in cameras:
            print(f"[INFO] 正在关闭 {name}...")
            cam.close()
        cv2.destroyAllWindows()
