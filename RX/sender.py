from __future__ import annotations

import argparse
import os
import socket
import sys
import threading
import time
from pathlib import Path
from typing import Any, Callable

from .protocol import (
    CMD_0A06,
    decode_app_packets,
    demod_message_to_dict,
    encode_app_packet,
)
from .pluto import DEFAULT_JAMMING_SERIAL, DEFAULT_SIGNAL_SERIAL, usb_uri_for_serial
from .runtime import FlowgraphRuntime, normalize_side
from .types import ProtocolMessage


_LOG_LOCK = threading.Lock()
_LOG_PATH: str | None = None
_STDIO_TEE_INSTALLED = False


def _get_log_path() -> str:
    global _LOG_PATH
    if _LOG_PATH is not None:
        return _LOG_PATH

    env_path = os.environ.get("RX_SENDER_LOG_PATH")
    if env_path:
        _LOG_PATH = env_path
        return _LOG_PATH

    log_dir = Path("logs") / "rx_sender"
    log_dir.mkdir(parents=True, exist_ok=True)
    _LOG_PATH = str(log_dir / f"rx_sender_{time.strftime('%Y-%m-%d_%H-%M-%S')}.log")
    os.environ["RX_SENDER_LOG_PATH"] = _LOG_PATH
    return _LOG_PATH


def _append_log_line(line: str) -> None:
    with _LOG_LOCK:
        with open(_get_log_path(), "a", encoding="utf-8") as file:
            file.write(line + "\n")


def _install_stdio_tee() -> None:
    global _STDIO_TEE_INSTALLED
    if _STDIO_TEE_INSTALLED:
        return

    log_path = _get_log_path()
    read_fd, write_fd = os.pipe()
    stdout_fd = os.dup(1)
    stderr_fd = os.dup(2)
    log_fd = os.open(log_path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)

    os.dup2(write_fd, 1)
    os.dup2(write_fd, 2)
    os.close(write_fd)

    sys.stdout = open(1, "w", encoding="utf-8", buffering=1, closefd=False)
    sys.stderr = open(2, "w", encoding="utf-8", buffering=1, closefd=False)

    def tee_loop() -> None:
        while True:
            data = os.read(read_fd, 4096)
            if not data:
                break
            os.write(stdout_fd, data)
            os.write(log_fd, data)

    threading.Thread(target=tee_loop, name="rx_sender_stdio_tee", daemon=True).start()
    _STDIO_TEE_INSTALLED = True


def _now_text() -> str:
    return time.strftime("%H:%M:%S")


def _debug(message: str) -> None:
    line = f"[{_now_text()}] [调试] {message}"
    print(line, flush=True)
    if not _STDIO_TEE_INSTALLED:
        _append_log_line(line)


def _format_bool(value: object) -> str:
    return "是" if value else "否"


def _format_side(side: object) -> str:
    if side == "red":
        return "红方"
    if side == "blue":
        return "蓝方"
    return "未设置"


def _format_level(level: object) -> str:
    if level == "level1":
        return "一级干扰"
    if level == "level2":
        return "二级干扰"
    if level is None:
        return "无"
    return str(level)


class DemodProcessManager:
    def __init__(
        self,
        server_ip: str = "192.168.1.10",
        port: int = 9999,
        uri: str | None = None,
        signal_uri: str | None = None,
        jamming_uri: str | None = None,
        signal_serial: str = DEFAULT_SIGNAL_SERIAL,
        jamming_serial: str = DEFAULT_JAMMING_SERIAL,
        reconnect_interval: float = 2.0,
        record_signal: bool = True,
        record_jamming: bool = False,
        record_dir: str | Path = "record",
        flowgraph_factory: Callable[..., Any] = FlowgraphRuntime,
    ):
        self.server_ip = server_ip
        self.port = int(port)
        self.uri = uri
        self.signal_uri = signal_uri
        self.jamming_uri = jamming_uri
        self.signal_serial = signal_serial
        self.jamming_serial = jamming_serial
        self.reconnect_interval = float(reconnect_interval)
        self.record_signal = bool(record_signal)
        self.record_jamming = bool(record_jamming)
        self.record_dir = Path(record_dir)
        self.flowgraph_factory = flowgraph_factory

        self.socket: socket.socket | None = None
        self.running = False
        self.lock = threading.RLock()
        self.buffer = bytearray()
        self.side: str | None = None
        self.ready_sent = False
        self.signal_runtime = None
        self.jamming_runtime = None
        self.signal_runtime_generation = 0
        self.jamming_runtime_generation = 0
        self.signal_stop_in_progress = 0
        self.jamming_stop_in_progress = 0
        self.jamming_level_name: str | None = None
        self.pending_jamming_level_name: str | None = None
        self.active_request_id: str | None = None
        self.message_count = 0
        self.signal_message_count = 0
        self.jamming_message_count = 0
        self.cmd_counts: dict[int, int] = {}
        self.signal_cmd_counts: dict[int, int] = {}
        self.jamming_cmd_counts: dict[int, int] = {}
        self.error_count = 0
        self.last_error: str | None = None
        self.jamming_request_start_time: float | None = None
        self.stats_log_interval = 5.0
        self.last_stats_log_time = 0.0
        self._receive_thread: threading.Thread | None = None
        self._runtime_thread: threading.Thread | None = None

    def start(self) -> None:
        self.running = True
        self._receive_thread = threading.Thread(target=self._connection_loop, name="demod_client_connection", daemon=True)
        self._receive_thread.start()
        self._runtime_thread = threading.Thread(target=self._runtime_loop, name="demod_runtime_reconnect", daemon=True)
        self._runtime_thread.start()

    def connect(self) -> bool:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.settimeout(3.0)
            _debug(f"正在连接上位机 {self.server_ip}:{self.port}")
            sock.connect((self.server_ip, self.port))
        except OSError as exc:
            sock.close()
            self._record_error(f"连接上位机 {self.server_ip}:{self.port} 失败：{exc}")
            return False
        sock.settimeout(1.0)
        with self.lock:
            self._close_socket_locked()
            self.socket = sock
            self.buffer.clear()
        _debug(f"已连接上位机 {self.server_ip}:{self.port}")
        return True

    def _connection_loop(self) -> None:
        while self.running:
            if not self.connect():
                self._sleep_reconnect_interval()
                continue
            self._receive_loop()
            signal_runtime = None
            jamming_runtime = None
            jamming_level_name = None
            with self.lock:
                _debug("上位机连接断开，停止当前解调并等待重连")
                self._close_socket_locked()
                jamming_runtime, jamming_level_name = self._detach_jamming_runtime_locked()
                signal_runtime = self._detach_signal_runtime_locked()
                self.side = None
                self.ready_sent = False
                self.active_request_id = None
                self.pending_jamming_level_name = None
                self.buffer.clear()
            self._stop_detached_jamming_runtime(jamming_runtime, jamming_level_name)
            self._stop_detached_signal_runtime(signal_runtime)
            self._sleep_reconnect_interval()

    def _receive_loop(self) -> None:
        while self.running:
            with self.lock:
                sock = self.socket
            if sock is None:
                return
            try:
                data = sock.recv(4096)
                if not data:
                    return
                with self.lock:
                    self.buffer.extend(data)
                    packets = decode_app_packets(self.buffer)
                for packet in packets:
                    self.handle_app_message(packet)
            except socket.timeout:
                continue
            except Exception as exc:
                self._record_error(str(exc))
                self._send({"type": "error", "message": str(exc)})
                return

    def handle_app_message(self, packet: dict[str, Any]) -> None:
        msg_type = packet.get("type")
        if msg_type == "init":
            side = normalize_side(packet["side"])
            _debug(f"收到上位机阵容配置：{_format_side(side)}")
            signal_runtime = None
            jamming_runtime = None
            jamming_level_name = None
            with self.lock:
                self.side = side
                self.ready_sent = False
                self.active_request_id = None
                self.jamming_request_start_time = None
                self.pending_jamming_level_name = None
                signal_runtime = self._detach_signal_runtime_locked()
                jamming_runtime, jamming_level_name = self._detach_jamming_runtime_locked()
            self._stop_detached_jamming_runtime(jamming_runtime, jamming_level_name)
            self._stop_detached_signal_runtime(signal_runtime)
            with self.lock:
                self._try_start_signal_locked()
                self._publish_ready_if_needed_locked()
            return

        if msg_type == "decode_request":
            level = int(packet["level"])
            if level not in (1, 2):
                raise ValueError(f"解调等级必须是 1 或 2，实际收到：{level!r}")
            request_id = str(packet["request_id"])
            _debug(f"收到干扰波解调请求：等级={level} request_id={request_id}")
            jamming_runtime = None
            jamming_level_name = None
            with self.lock:
                self._require_initialized_locked()
                self.active_request_id = request_id
                self.jamming_request_start_time = time.monotonic()
                self.pending_jamming_level_name = f"level{level}"
                jamming_runtime, jamming_level_name = self._detach_jamming_runtime_locked()
                self._try_start_jamming_locked()
            self._stop_detached_jamming_runtime(jamming_runtime, jamming_level_name)
            with self.lock:
                self._try_start_jamming_locked()
            return

        if msg_type == "decode_cancel":
            request_id = str(packet["request_id"])
            _debug(f"收到取消解调请求：request_id={request_id}")
            jamming_runtime = None
            jamming_level_name = None
            with self.lock:
                if request_id == self.active_request_id:
                    duration = self._active_jamming_duration_locked()
                    _debug(f"取消干扰波解调：request_id={request_id} 已运行={duration:.1f}s")
                    self.active_request_id = None
                    self.jamming_request_start_time = None
                    self.pending_jamming_level_name = None
                    jamming_runtime, jamming_level_name = self._detach_jamming_runtime_locked()
                else:
                    _debug(
                        f"忽略非当前取消请求：request_id={request_id} "
                        f"active_request_id={self.active_request_id}"
                    )
            self._stop_detached_jamming_runtime(jamming_runtime, jamming_level_name)
            return

        if msg_type == "stop":
            _debug("收到上位机停止指令")
            self.stop()
            return

        raise ValueError(f"不支持的上位机消息类型：{msg_type!r}")

    def _require_initialized_locked(self) -> None:
        if self.side is None:
            raise RuntimeError("工控机尚未收到上位机阵容初始化消息")

    def _start_signal_locked(self) -> None:
        assert self.side is not None
        signal_uri = self._resolve_signal_uri()
        record_path = self._make_record_path_locked("signal", "base", None) if self.record_signal else None
        _debug(
            f"启动信息波解调：阵容={_format_side(self.side)} uri={signal_uri} "
            f"record={record_path or '关闭'}"
        )
        runtime = self.flowgraph_factory(
            self.side,
            "base",
            uri=signal_uri,
            record_path=str(record_path) if record_path is not None else None,
            message_callback=lambda message: self._handle_demod_message(message, None),
        )
        runtime.start()
        self.signal_runtime = runtime
        self.signal_runtime_generation += 1
        generation = self.signal_runtime_generation
        threading.Thread(
            target=self._watch_signal_runtime,
            args=(runtime, generation),
            name="demod_signal_runtime_watch",
            daemon=True,
        ).start()
        _debug("信息波解调启动成功")

    def _try_start_signal_locked(self) -> bool:
        if self.side is None or self.signal_runtime is not None or self.signal_stop_in_progress > 0:
            return True
        try:
            self._start_signal_locked()
            return True
        except Exception as exc:
            self._record_error(f"启动信息波解调失败：{exc}")
            return False

    def _start_jamming_locked(self, level_name: str, request_id: str) -> None:
        assert self.side is not None
        jamming_uri = self._resolve_jamming_uri()
        record_path = self._make_record_path_locked("jamming", level_name, request_id) if self.record_jamming else None
        _debug(
            f"启动干扰波解调：阵容={_format_side(self.side)} "
            f"等级={_format_level(level_name)} uri={jamming_uri} "
            f"request_id={request_id} record={record_path or '关闭'}"
        )
        runtime = self.flowgraph_factory(
            self.side,
            level_name,
            uri=jamming_uri,
            record_path=str(record_path) if record_path is not None else None,
            message_callback=lambda message: self._handle_demod_message(message, request_id),
        )
        runtime.start()
        self.jamming_runtime = runtime
        self.jamming_level_name = level_name
        self.jamming_runtime_generation += 1
        generation = self.jamming_runtime_generation
        threading.Thread(
            target=self._watch_jamming_runtime,
            args=(runtime, generation, level_name),
            name="demod_jamming_runtime_watch",
            daemon=True,
        ).start()
        _debug(f"干扰波解调启动成功：{_format_level(level_name)}")

    def _watch_signal_runtime(self, runtime, generation: int) -> None:
        try:
            runtime.wait()
        except Exception as exc:
            self._record_error(f"信息波解调运行异常退出：{exc}")
        with self.lock:
            if self.signal_runtime is not runtime or self.signal_runtime_generation != generation:
                return
            self.signal_runtime = None
            self.ready_sent = False
        _debug("信息波解调已退出，等待自动重启")

    def _watch_jamming_runtime(self, runtime, generation: int, level_name: str) -> None:
        try:
            runtime.wait()
        except Exception as exc:
            self._record_error(f"干扰波解调运行异常退出：{exc}")
        with self.lock:
            if self.jamming_runtime is not runtime or self.jamming_runtime_generation != generation:
                return
            self.jamming_runtime = None
            self.jamming_level_name = None
        _debug(f"干扰波解调已退出，等待自动重启：{_format_level(level_name)}")

    def _try_start_jamming_locked(self) -> bool:
        if self.side is None or self.active_request_id is None or self.pending_jamming_level_name is None:
            return True
        if self.jamming_runtime is not None or self.jamming_stop_in_progress > 0:
            return True
        try:
            self._start_jamming_locked(self.pending_jamming_level_name, self.active_request_id)
            return True
        except Exception as exc:
            self._record_error(f"启动干扰波解调失败：{exc}")
            return False

    def _detach_signal_runtime_locked(self):
        runtime = self.signal_runtime
        self.signal_runtime = None
        self.signal_runtime_generation += 1
        if runtime is not None:
            self.signal_stop_in_progress += 1
        return runtime

    def _detach_jamming_runtime_locked(self):
        runtime = self.jamming_runtime
        level_name = self.jamming_level_name
        self.jamming_runtime = None
        self.jamming_level_name = None
        self.jamming_runtime_generation += 1
        if runtime is not None:
            self.jamming_stop_in_progress += 1
        return runtime, level_name

    def _stop_detached_signal_runtime(self, runtime) -> None:
        if runtime is None:
            return
        _debug("停止信息波解调")
        try:
            runtime.stop()
            _debug("信息波解调停止完成")
        except Exception as exc:
            self._record_error(f"停止信息波解调失败：{exc}")
        finally:
            with self.lock:
                self.signal_stop_in_progress -= 1
                if self.running:
                    self._try_start_signal_locked()
                    self._publish_ready_if_needed_locked()

    def _stop_detached_jamming_runtime(self, runtime, level_name: str | None) -> None:
        if runtime is None:
            return
        _debug(f"停止干扰波解调：{_format_level(level_name)}")
        try:
            runtime.stop()
            _debug(f"干扰波解调停止完成：{_format_level(level_name)}")
        except Exception as exc:
            self._record_error(f"停止干扰波解调失败：{exc}")
        finally:
            with self.lock:
                self.jamming_stop_in_progress -= 1
                if self.running:
                    self._try_start_jamming_locked()

    def _handle_demod_message(self, message: ProtocolMessage, request_id: str | None) -> None:
        with self.lock:
            self.message_count += 1
            self.cmd_counts[message.cmd_id] = self.cmd_counts.get(message.cmd_id, 0) + 1
            if request_id is None:
                self.signal_message_count += 1
                self.signal_cmd_counts[message.cmd_id] = self.signal_cmd_counts.get(message.cmd_id, 0) + 1
            else:
                self.jamming_message_count += 1
                self.jamming_cmd_counts[message.cmd_id] = self.jamming_cmd_counts.get(message.cmd_id, 0) + 1
        self._send({"type": "data", "message": demod_message_to_dict(message)})
        if message.cmd_id == CMD_0A06 and request_id is not None:
            _debug(f"收到干扰波密钥帧 0x0A06：seq={message.seq} request_id={request_id}")
            threading.Thread(
                target=self._finish_decode_success,
                args=(request_id,),
                name="demod_finish_success",
                daemon=True,
            ).start()

    def _finish_decode_success(self, request_id: str) -> None:
        jamming_runtime = None
        jamming_level_name = None
        with self.lock:
            if request_id == self.active_request_id:
                duration = self._active_jamming_duration_locked()
                self.active_request_id = None
                self.jamming_request_start_time = None
                self.pending_jamming_level_name = None
                jamming_runtime, jamming_level_name = self._detach_jamming_runtime_locked()
            else:
                return
        _debug(f"向上位机上报解调成功：request_id={request_id} 已运行={duration:.1f}s")
        self._send({"type": "decode_success", "request_id": request_id})
        self._stop_detached_jamming_runtime(jamming_runtime, jamming_level_name)

    def _send(self, packet: dict[str, Any]) -> bool:
        data = encode_app_packet(packet)
        with self.lock:
            sock = self.socket
        if sock is None:
            return False
        try:
            sock.sendall(data)
            return True
        except OSError:
            with self.lock:
                if self.socket is sock:
                    self._close_socket_locked()
            return False

    def get_stats(self) -> dict[str, float | int | str | None]:
        with self.lock:
            return {
                "message_count": self.message_count,
                "signal_message_count": self.signal_message_count,
                "jamming_message_count": self.jamming_message_count,
                "error_count": self.error_count,
                "signal_running": self.signal_runtime is not None,
                "jamming_level": self.jamming_level_name,
                "pending_jamming_level": self.pending_jamming_level_name,
                "signal_stop_in_progress": self.signal_stop_in_progress,
                "jamming_stop_in_progress": self.jamming_stop_in_progress,
                "connected": self.socket is not None,
                "ready": self.ready_sent,
                "side": self.side,
                "last_error": self.last_error,
            }

    def _runtime_loop(self) -> None:
        while self.running:
            with self.lock:
                self._try_start_signal_locked()
                self._publish_ready_if_needed_locked()
                self._try_start_jamming_locked()
                self._log_periodic_stats_locked()
            self._sleep_reconnect_interval()

    def _active_jamming_duration_locked(self) -> float:
        if self.jamming_request_start_time is None:
            return 0.0
        return time.monotonic() - self.jamming_request_start_time

    def _format_cmd_counts(self, counts: dict[int, int]) -> str:
        if not counts:
            return "无"
        return " ".join(f"0x{cmd_id:04X}={counts[cmd_id]}" for cmd_id in sorted(counts))

    def _runtime_debug_stats(self, runtime) -> dict[str, object]:
        if runtime is None or not hasattr(runtime, "get_debug_stats"):
            return {}
        try:
            return runtime.get_debug_stats()
        except Exception as exc:
            return {"error": str(exc)}

    def _log_periodic_stats_locked(self) -> None:
        now = time.monotonic()
        if now - self.last_stats_log_time < self.stats_log_interval:
            return
        self.last_stats_log_time = now
        signal_debug = self._runtime_debug_stats(self.signal_runtime)
        jamming_debug = self._runtime_debug_stats(self.jamming_runtime)
        _debug(
            "统计："
            f"total={self.message_count} signal={self.signal_message_count} "
            f"jamming={self.jamming_message_count} "
            f"signal_running={_format_bool(self.signal_runtime is not None)} "
            f"jamming_running={_format_bool(self.jamming_runtime is not None)} "
            f"signal_stopping={_format_bool(self.signal_stop_in_progress > 0)} "
            f"jamming_stopping={_format_bool(self.jamming_stop_in_progress > 0)} "
            f"jamming_level={_format_level(self.jamming_level_name or self.pending_jamming_level_name)} "
            f"active_request_id={self.active_request_id} "
            f"active_duration={self._active_jamming_duration_locked():.1f}s "
            f"cmd_total=({self._format_cmd_counts(self.cmd_counts)}) "
            f"cmd_signal=({self._format_cmd_counts(self.signal_cmd_counts)}) "
            f"cmd_jamming=({self._format_cmd_counts(self.jamming_cmd_counts)}) "
            f"signal_parser={signal_debug.get('parser_stats', {})} "
            f"jamming_parser={jamming_debug.get('parser_stats', {})}"
        )

    def _resolve_signal_uri(self) -> str:
        if self.signal_uri is not None:
            return self.signal_uri
        if self.uri is not None:
            return self.uri
        return usb_uri_for_serial(self.signal_serial)

    def _resolve_jamming_uri(self) -> str:
        if self.jamming_uri is not None:
            return self.jamming_uri
        if self.uri is not None:
            return self.uri
        return usb_uri_for_serial(self.jamming_serial)

    def _make_record_path_locked(self, kind: str, level_name: str, request_id: str | None) -> Path:
        assert self.side is not None
        self.record_dir.mkdir(parents=True, exist_ok=True)
        now = time.time()
        timestamp = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime(now)) + f"_{int((now % 1) * 1000):03d}"
        suffix = f"_{request_id}" if request_id is not None else ""
        stem = f"{timestamp}_{kind}_{self.side}_{level_name}{suffix}"
        path = self.record_dir / f"{stem}.c64"
        index = 1
        while path.exists():
            path = self.record_dir / f"{stem}_{index:02d}.c64"
            index += 1
        return path

    def _record_error(self, message: str) -> None:
        with self.lock:
            self.error_count += 1
            self.last_error = message
        _debug(f"错误：{message}")

    def _close_socket_locked(self) -> None:
        if self.socket is not None:
            try:
                self.socket.close()
            finally:
                self.socket = None
        self.ready_sent = False

    def _publish_ready_if_needed_locked(self) -> None:
        if self.side is None or self.signal_runtime is None or self.ready_sent:
            return
        if self._send({"type": "ready", "side": self.side}):
            self.ready_sent = True
            _debug(f"已向上位机发送 ready：阵容={_format_side(self.side)}")

    def _sleep_reconnect_interval(self) -> None:
        deadline = time.time() + self.reconnect_interval
        while self.running and time.time() < deadline:
            time.sleep(0.1)

    def stop(self) -> None:
        self.running = False
        signal_runtime = None
        jamming_runtime = None
        jamming_level_name = None
        with self.lock:
            self.active_request_id = None
            self.jamming_request_start_time = None
            self.pending_jamming_level_name = None
            jamming_runtime, jamming_level_name = self._detach_jamming_runtime_locked()
            signal_runtime = self._detach_signal_runtime_locked()
            self._close_socket_locked()
        self._stop_detached_jamming_runtime(jamming_runtime, jamming_level_name)
        self._stop_detached_signal_runtime(signal_runtime)


def main() -> None:
    parser = argparse.ArgumentParser(description="工控机端解调进程管理器")
    parser.add_argument("--server-ip", type=str, default="192.168.1.10", help="上位机 IP 地址")
    parser.add_argument("--port", type=int, default=9999, help="上位机监听端口")
    parser.add_argument("--uri", type=str, default=None, help="兼容旧用法：信息波和干扰波共用同一个 PlutoSDR URI")
    parser.add_argument("--signal-uri", type=str, default=None, help="信息波 PlutoSDR URI")
    parser.add_argument("--jamming-uri", type=str, default=None, help="干扰波 PlutoSDR URI")
    parser.add_argument("--signal-serial", type=str, default=DEFAULT_SIGNAL_SERIAL, help="信息波 PlutoSDR USB 序列号")
    parser.add_argument("--jamming-serial", type=str, default=DEFAULT_JAMMING_SERIAL, help="干扰波 PlutoSDR USB 序列号")
    parser.add_argument("--reconnect-interval", type=float, default=2.0, help="重连间隔，单位秒")
    parser.add_argument("--record-signal", action=argparse.BooleanOptionalAction, default=True, help="录制信息波原始 IQ")
    parser.add_argument("--record-jamming", action=argparse.BooleanOptionalAction, default=False, help="录制干扰波原始 IQ")
    parser.add_argument("--record-dir", type=Path, default=Path("record"), help="原始 IQ 录制目录")
    args = parser.parse_args()

    _install_stdio_tee()
    _debug(f"工控机解调日志文件：{_get_log_path()}")

    if args.signal_uri is not None and args.signal_uri == args.jamming_uri:
        raise RuntimeError(f"信息波和干扰波 PlutoSDR 不能是同一台设备，当前都设置为：{args.signal_uri}")

    manager = DemodProcessManager(
        server_ip=args.server_ip,
        port=args.port,
        uri=args.uri,
        signal_uri=args.signal_uri,
        jamming_uri=args.jamming_uri,
        signal_serial=args.signal_serial,
        jamming_serial=args.jamming_serial,
        reconnect_interval=args.reconnect_interval,
        record_signal=args.record_signal,
        record_jamming=args.record_jamming,
        record_dir=args.record_dir,
    )
    manager.start()
    try:
        while True:
            time.sleep(1.0)
            stats = manager.get_stats()
            # print(
            #     f"工控机状态：上位机连接={_format_bool(stats['connected'])} "
            #     f"阵容={_format_side(stats['side'])} "
            #     f"信息波解调={_format_bool(stats['signal_running'])} "
            #     f"已就绪={_format_bool(stats['ready'])} "
            #     f"干扰波解调={_format_level(stats['jamming_level'] or stats['pending_jamming_level'])} "
            #     f"消息数={stats['message_count']} "
            #     f"错误数={stats['error_count']} "
            #     f"最近错误={stats['last_error'] or '无'}"
            # )
    except KeyboardInterrupt:
        pass
    finally:
        manager.stop()


if __name__ == "__main__":
    main()
