from __future__ import annotations

from collections import deque
import argparse
import socket
import threading
import time
from typing import Any
from uuid import uuid4

from .protocol import (
    SIGNAL_CMDS,
    apply_message_to_state,
    copy_state,
    decode_app_packets,
    dict_to_demod_message,
    encode_app_packet,
    format_message_line,
)
from .runtime import normalize_side
from .types import DemodState, ProtocolMessage


def _now_text() -> str:
    return time.strftime("%H:%M:%S")


def _debug(message: str) -> None:
    print(f"[{_now_text()}] [解调控制] {message}", flush=True)


class DemodController:
    def __init__(
        self,
        side: str,
        target_level: int,
        host: str = "0.0.0.0",
        port: int = 9999,
        timeout: float = 30.0,
        line_history: int = 12,
        auto_decode: bool = True,
        auto_advance: bool = True,
        decode_enabled: bool = True,
    ):
        self.side = normalize_side(side)
        self.target_level = int(target_level)
        if self.target_level < 1 or self.target_level > 3:
            raise ValueError("target_level must be 1, 2, or 3")
        self.host = host
        self.port = int(port)
        self.timeout = float(timeout)
        self.auto_decode = bool(auto_decode)
        self.auto_advance = bool(auto_advance)
        self.decode_enabled = bool(decode_enabled)

        self.server_socket: socket.socket | None = None
        self.client_socket: socket.socket | None = None
        self.client_address = None
        self.running = False

        self.lock = threading.RLock()
        self.connected = threading.Event()
        self.ready = threading.Event()
        self.decode_success = threading.Event()
        self.current_level = 1
        self.active_request_id: str | None = None
        self.success_request_id: str | None = None

        self.state = DemodState()
        self.latest_message: ProtocolMessage | None = None
        self.last_message_time = 0.0
        self.lines = deque(maxlen=line_history)
        self.line_records = deque(maxlen=line_history)
        self.buffer = bytearray()
        self.message_count = 0
        self.signal_message_count = 0
        self.signal_message_times = deque()
        self.frequency_window = 1.0
        self.receive_frequency = 0.0
        self.last_frequency_log_time = 0.0
        self.error_count = 0

        self._accept_thread: threading.Thread | None = None
        self._control_thread: threading.Thread | None = None
        self.last_control_status = "未启动"
        self.last_control_log_key: tuple[object, ...] | None = None

    def start(self) -> None:
        _debug(
            f"启动上位机解调控制服务：listen={self.host}:{self.port} "
            f"side={self.side} target_level={self.target_level} "
            f"auto_advance={self.auto_advance} decode_enabled={self.decode_enabled}"
        )
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(1)
        self.running = True

        self._accept_thread = threading.Thread(target=self._accept_client, name="demod_accept", daemon=True)
        self._accept_thread.start()
        if self.auto_decode:
            self._control_thread = threading.Thread(
                target=self.decode_until_target,
                name="demod_control",
                daemon=True,
            )
            self._control_thread.start()

    def _accept_client(self) -> None:
        assert self.server_socket is not None
        while self.running:
            try:
                self.server_socket.settimeout(1.0)
                client_socket, client_address = self.server_socket.accept()
            except socket.timeout:
                continue
            except OSError:
                return

            with self.lock:
                if self.client_socket is not None:
                    self.client_socket.close()
                self.client_socket = client_socket
                self.client_address = client_address
                self.buffer.clear()
                self.signal_message_times.clear()
                self.receive_frequency = 0.0
                self.ready.clear()
                self.connected.set()

            _debug(f"工控机已连接：address={client_address}")
            threading.Thread(
                target=self._receive_loop,
                name="demod_receive",
                daemon=True,
            ).start()
            _debug(f"向工控机发送初始化阵容：side={self.side}")
            self._send({"type": "init", "side": self.side})

    def _receive_loop(self) -> None:
        while self.running:
            with self.lock:
                client_socket = self.client_socket
            if client_socket is None:
                return

            try:
                client_socket.settimeout(1.0)
                data = client_socket.recv(4096)
                if not data:
                    self._drop_client(client_socket)
                    return
                with self.lock:
                    self.buffer.extend(data)
                    packets = decode_app_packets(self.buffer)
                for packet in packets:
                    self._handle_app_message(packet)
            except socket.timeout:
                continue
            except Exception:
                self.error_count += 1
                self._drop_client(client_socket)
                return

    def _drop_client(self, client_socket: socket.socket) -> None:
        with self.lock:
            if self.client_socket is client_socket:
                _debug(f"工控机连接断开：address={self.client_address}")
                self.client_socket.close()
                self.client_socket = None
                self.client_address = None
                self.buffer.clear()
                self.connected.clear()
                self.ready.clear()

    def _handle_app_message(self, packet: dict[str, Any]) -> None:
        msg_type = packet.get("type")
        if msg_type == "ready":
            self.ready.set()
            _debug("收到工控机 ready，信息波解调已启动")
            return
        if msg_type == "data":
            message = dict_to_demod_message(packet["message"])
            self._handle_demod_message(message)
            return
        if msg_type == "decode_success":
            request_id = str(packet["request_id"])
            with self.lock:
                if request_id != self.active_request_id:
                    _debug(
                        f"忽略过期 decode_success：request_id={request_id} "
                        f"active_request_id={self.active_request_id}"
                    )
                    return
                self.success_request_id = request_id
                if self.auto_advance:
                    self.current_level = min(3, self.current_level + 1)
                self.active_request_id = None
            self.decode_success.set()
            _debug(f"收到工控机解调成功回执：request_id={request_id} current_level={self.current_level}")
            return
        if msg_type == "error":
            self.error_count += 1
            _debug(f"收到工控机错误：{packet.get('message', '')}")
            return
        raise ValueError(f"unsupported app message type {msg_type!r}")

    def _handle_demod_message(self, message: ProtocolMessage) -> None:
        frequency_log: tuple[float, int] | None = None
        with self.lock:
            apply_message_to_state(self.state, message)
            self.latest_message = message
            self.last_message_time = message.time_stamp
            line = format_message_line(message)
            self.lines.append(line)
            self.line_records.append((line, message.time_stamp))
            self.message_count += 1
            if message.cmd_id in SIGNAL_CMDS:
                now = time.monotonic()
                self.signal_message_count += 1
                self.signal_message_times.append(now)
                while self.signal_message_times and now - self.signal_message_times[0] > self.frequency_window:
                    self.signal_message_times.popleft()
                self.receive_frequency = len(self.signal_message_times) / self.frequency_window
                if now - self.last_frequency_log_time >= 1.0:
                    self.last_frequency_log_time = now
                    frequency_log = (self.receive_frequency, self.signal_message_count)
        if frequency_log is not None:
            _debug(f"信息波接收频率={frequency_log[0]:.2f} Hz 总数={frequency_log[1]}")

    def _get_receive_frequency_locked(self) -> float:
        now = time.monotonic()
        while self.signal_message_times and now - self.signal_message_times[0] > self.frequency_window:
            self.signal_message_times.popleft()
        self.receive_frequency = len(self.signal_message_times) / self.frequency_window
        return self.receive_frequency

    def _send(self, packet: dict[str, Any]) -> bool:
        data = encode_app_packet(packet)
        with self.lock:
            sock = self.client_socket
        if sock is None:
            return False
        try:
            sock.sendall(data)
            return True
        except OSError:
            _debug(f"向工控机发送失败：type={packet.get('type')}")
            self._drop_client(sock)
            return False

    def try_decode(self) -> bool:
        with self.lock:
            if not self.decode_enabled:
                self.last_control_status = "干扰波请求未启用"
                return False
            if self.current_level >= self.target_level:
                return True
            level = self.current_level
            request_id = uuid4().hex
            self.active_request_id = request_id
            self.success_request_id = None
            self.decode_success.clear()
            self.last_control_status = f"准备请求 level={level}"

        _debug(f"准备请求工控机解调干扰波：level={level} request_id={request_id}")
        if not self.ready.wait(timeout=self.timeout):
            _debug(f"等待工控机 ready 超时，取消本次解调请求：level={level} request_id={request_id}")
            with self.lock:
                if self.active_request_id == request_id:
                    self.active_request_id = None
                self.last_control_status = f"等待 ready 超时 level={level}"
            return False
        if not self._send({"type": "decode_request", "level": level, "request_id": request_id}):
            _debug(f"发送解调请求失败：level={level} request_id={request_id}")
            with self.lock:
                if self.active_request_id == request_id:
                    self.active_request_id = None
                self.last_control_status = f"发送请求失败 level={level}"
            return False
        with self.lock:
            self.last_control_status = f"已发送请求 level={level}"
        _debug(f"已发送解调请求：level={level} request_id={request_id}")

        if self.decode_success.wait(timeout=self.timeout):
            with self.lock:
                confirmed = self.success_request_id == request_id or self.current_level > level
                if confirmed:
                    self.last_control_status = f"收到成功回执 level={level}"
                    return True
                self.last_control_status = f"请求已中止 level={level}"
            return False

        _debug(f"等待解调成功超时：level={level} request_id={request_id}")
        with self.lock:
            if self.active_request_id == request_id:
                self.active_request_id = None
            self.last_control_status = f"等待成功超时 level={level}"
        self._send({"type": "decode_cancel", "request_id": request_id})
        _debug(f"已发送取消解调请求：level={level} request_id={request_id}")
        return False

    def set_decode_enabled(self, enabled: bool) -> None:
        enabled = bool(enabled)
        cancel_request_id = None
        with self.lock:
            if self.decode_enabled == enabled:
                return

            self.decode_enabled = enabled
            if enabled:
                self.decode_success.clear()
                self.last_control_status = "干扰波请求已启用"
            else:
                cancel_request_id = self.active_request_id
                self.active_request_id = None
                self.success_request_id = None
                self.decode_success.set()
                self.last_control_status = "干扰波请求已暂停"

        _debug(f"干扰波自动请求{'启用' if enabled else '暂停'}")
        if cancel_request_id is not None:
            self._send({"type": "decode_cancel", "request_id": cancel_request_id})

    def set_current_level(self, level: int) -> None:
        level = int(level)
        if level < 1 or level > 3:
            raise ValueError("current level must be 1, 2, or 3")
        with self.lock:
            old_level = self.current_level
            self.current_level = level
            self.success_request_id = None
            self.last_control_status = f"裁判确认等级 {old_level}->{level}"
            if old_level != level:
                self.active_request_id = None
                self.decode_success.set()
            if self.current_level >= self.target_level:
                self.active_request_id = None
                self.decode_success.set()
        if old_level != level:
            _debug(f"裁判系统确认当前加密等级：{old_level} -> {level}")

    def reject_pending_decode(self) -> None:
        with self.lock:
            self.success_request_id = None

    def decode_until_target(self) -> None:
        while self.running:
            with self.lock:
                decode_enabled = self.decode_enabled
                done = self.current_level >= self.target_level
                waiting_external_confirmation = (
                    not self.auto_advance and self.success_request_id is not None
                )
                log_key = (
                    self.current_level,
                    self.target_level,
                    self.connected.is_set(),
                    self.ready.is_set(),
                    self.active_request_id,
                    self.success_request_id,
                    decode_enabled,
                    done,
                    waiting_external_confirmation,
                )
            if not decode_enabled:
                self._log_control_wait_once(log_key, "等待比赛开始启用干扰波请求")
                time.sleep(0.1)
                continue
            if done:
                self._log_control_wait_once(log_key, "已达到目标解调等级")
                time.sleep(0.1)
                continue
            if waiting_external_confirmation:
                self._log_control_wait_once(log_key, "等待裁判系统确认上一阶段密钥")
                time.sleep(0.1)
                continue
            self._log_control_wait_once(log_key, "准备进入下一次解调请求")
            self.try_decode()

    def _log_control_wait_once(self, log_key: tuple[object, ...], message: str) -> None:
        with self.lock:
            if self.last_control_log_key == log_key:
                return
            self.last_control_log_key = log_key
            self.last_control_status = message
            current_level = self.current_level
            target_level = self.target_level
            connected = self.connected.is_set()
            ready = self.ready.is_set()
            active_request_id = self.active_request_id
            success_request_id = self.success_request_id
        _debug(
            f"{message}：current={current_level} target={target_level} "
            f"connected={connected} ready={ready} "
            f"active_request_id={active_request_id} success_request_id={success_request_id}"
        )

    def get_snapshot(self) -> dict[str, object]:
        with self.lock:
            return {
                "state": copy_state(self.state),
                "latest_message": self.latest_message,
                "last_message_time": self.last_message_time,
                "lines": list(self.lines),
                "line_records": list(self.line_records),
                "current_level": self.current_level,
                "target_level": self.target_level,
                "connected": self.connected.is_set(),
                "ready": self.ready.is_set(),
                "active_request_id": self.active_request_id,
                "success_request_id": self.success_request_id,
                "decode_enabled": self.decode_enabled,
                "signal_message_count": self.signal_message_count,
                "receive_frequency": self._get_receive_frequency_locked(),
                "control_thread_alive": (
                    self._control_thread is not None and self._control_thread.is_alive()
                ),
                "last_control_status": self.last_control_status,
            }

    def get_stats(self) -> dict[str, float | int]:
        with self.lock:
            return {
                "message_count": self.message_count,
                "signal_message_count": self.signal_message_count,
                "error_count": self.error_count,
                "receive_frequency": self._get_receive_frequency_locked(),
                "success_rate": (self.message_count - self.error_count) / max(1, self.message_count) * 100,
                "last_message_time": self.last_message_time,
                "current_level": self.current_level,
            }

    def stop(self) -> None:
        self.running = False
        self._send({"type": "stop"})
        with self.lock:
            if self.client_socket is not None:
                self.client_socket.close()
                self.client_socket = None
            if self.server_socket is not None:
                self.server_socket.close()
                self.server_socket = None
            self.connected.clear()
            self.ready.clear()
            self.decode_success.set()


class DataReceiver(DemodController):
    def __init__(
        self,
        host: str = "0.0.0.0",
        port: int = 9999,
        line_history: int = 12,
        output_format: str = "text",
        side: str = "blue",
        target_level: int = 1,
        timeout: float = 30.0,
        auto_decode: bool = False,
        auto_advance: bool = True,
    ):
        super().__init__(
            side=side,
            target_level=target_level,
            host=host,
            port=port,
            timeout=timeout,
            line_history=line_history,
            auto_decode=auto_decode,
            auto_advance=auto_advance,
        )
        self.output_format = output_format


def main() -> None:
    parser = argparse.ArgumentParser(description="RX controller server")
    parser.add_argument("--side", choices=("red", "blue"), required=True)
    parser.add_argument("--target-level", type=int, default=3, choices=(1, 2, 3))
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=9999)
    parser.add_argument("--timeout", type=float, default=30.0)
    args = parser.parse_args()

    controller = DemodController(
        side=args.side,
        target_level=args.target_level,
        host=args.host,
        port=args.port,
        timeout=args.timeout,
    )
    controller.start()
    printed_messages = 0
    try:
        while True:
            time.sleep(1.0)
            stats = controller.get_stats()
            snapshot = controller.get_snapshot()
            lines = snapshot["lines"]
            new_message_count = stats["message_count"] - printed_messages
            if new_message_count > 0:
                for line in lines[-new_message_count:]:
                    print(line)
                printed_messages = stats["message_count"]
            print(
                # f"rx messages={stats['message_count']} errors={stats['error_count']} "
                # f"signal_messages={stats['signal_message_count']} "
                f"signal_freq={stats['receive_frequency']:.2f}Hz "
                f"level={stats['current_level']}/{args.target_level}"
            )
    except KeyboardInterrupt:
        pass
    finally:
        controller.stop()


if __name__ == "__main__":
    main()
