from __future__ import annotations

import argparse
from pathlib import Path
import signal
import sys
import threading

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from RX.protocol import format_message_line
from RX.pluto import DEFAULT_JAMMING_SERIAL, DEFAULT_SIGNAL_SERIAL, usb_uri_for_serial
from RX.runtime import FlowgraphRuntime
from RX.types import ProtocolMessage


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="直接启动实时解调并打印结果，不连接上位机。")
    parser.add_argument("--side", choices=("red", "blue"), default="red", help="己方阵容")
    parser.add_argument("--level", choices=("base", "level1", "level2"), default="base", help="解调类型")
    parser.add_argument("--uri", type=str, default=None, help="兼容旧用法：当前解调显式使用的 PlutoSDR URI")
    parser.add_argument("--signal-uri", type=str, default=None, help="信息波 PlutoSDR URI")
    parser.add_argument("--jamming-uri", type=str, default=None, help="干扰波 PlutoSDR URI")
    parser.add_argument("--signal-serial", type=str, default=DEFAULT_SIGNAL_SERIAL, help="信息波 PlutoSDR USB 序列号")
    parser.add_argument("--jamming-serial", type=str, default=DEFAULT_JAMMING_SERIAL, help="干扰波 PlutoSDR USB 序列号")
    return parser.parse_args()


def resolve_demod_uri(args: argparse.Namespace) -> str:
    if args.signal_uri is not None and args.jamming_uri is not None and args.signal_uri == args.jamming_uri:
        raise RuntimeError(f"信息波和干扰波 PlutoSDR 不能是同一台设备，当前都设置为：{args.signal_uri}")
    if args.signal_serial == args.jamming_serial:
        raise RuntimeError(f"信息波和干扰波 PlutoSDR USB 序列号不能相同：{args.signal_serial}")

    if args.uri is not None:
        return args.uri
    if args.level == "base":
        if args.signal_uri is not None:
            return args.signal_uri
        return usb_uri_for_serial(args.signal_serial)
    if args.jamming_uri is not None:
        return args.jamming_uri
    return usb_uri_for_serial(args.jamming_serial)


def main() -> None:
    args = parse_args()
    uri = resolve_demod_uri(args)
    stop_event = threading.Event()
    count = 0

    def on_message(message: ProtocolMessage) -> None:
        nonlocal count
        count += 1
        print(format_message_line(message), flush=True)

    runtime = FlowgraphRuntime(
        args.side,
        args.level,
        uri=uri,
        message_callback=on_message,
    )

    def stop_handler(signum, frame):
        stop_event.set()
        runtime.stop()

    signal.signal(signal.SIGINT, stop_handler)
    signal.signal(signal.SIGTERM, stop_handler)

    print(f"启动实时解调：阵容={args.side} 类型={args.level} uri={uri}", flush=True)
    runtime.start()
    try:
        while not stop_event.wait(1.0):
            print(f"已解调消息数={count}", flush=True)
    finally:
        if not stop_event.is_set():
            runtime.stop()


if __name__ == "__main__":
    main()
