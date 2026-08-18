from __future__ import annotations

import ctypes
from collections import deque
import re
import struct
import sys
import threading
import time
import types
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _install_numpy_stub_if_needed() -> bool:
    try:
        import numpy  # noqa: F401
        return False
    except ModuleNotFoundError:
        fake_numpy = types.SimpleNamespace(
            uint8=int,
            uint16=int,
            uint32=int,
            int8=int,
            int16=int,
            int32=int,
            float32=float,
        )
        sys.modules["numpy"] = fake_numpy
        return True


def _install_optional_dependency_stubs_if_needed() -> list[str]:
    stubbed: list[str] = []

    try:
        import loguru  # noqa: F401
    except ModuleNotFoundError:
        class _Logger:
            def info(self, *args, **kwargs) -> None:
                pass

            def warning(self, *args, **kwargs) -> None:
                pass

            def exception(self, *args, **kwargs) -> None:
                pass

        fake_loguru = types.ModuleType("loguru")
        fake_loguru.logger = _Logger()
        sys.modules["loguru"] = fake_loguru
        stubbed.append("loguru")

    try:
        import serial  # noqa: F401
    except ModuleNotFoundError:
        fake_serial = types.ModuleType("serial")
        fake_tools = types.ModuleType("serial.tools")
        fake_list_ports = types.ModuleType("serial.tools.list_ports")

        class _SerialException(Exception):
            pass

        class _Serial:
            def __init__(self, *args, **kwargs):
                self.is_open = False

            def close(self) -> None:
                self.is_open = False

        def _comports():
            return []

        fake_list_ports.comports = _comports
        fake_tools.list_ports = fake_list_ports
        fake_serial.Serial = _Serial
        fake_serial.SerialException = _SerialException
        fake_serial.tools = fake_tools

        sys.modules["serial"] = fake_serial
        sys.modules["serial.tools"] = fake_tools
        sys.modules["serial.tools.list_ports"] = fake_list_ports
        stubbed.append("serial")

    return stubbed


def verify_rx_protocol() -> None:
    from RX.protocol import (
        CMD_0A01,
        CMD_0A02,
        CMD_0A03,
        CMD_0A04,
        CMD_0A05,
        CMD_0A06,
        RMFrameStreamParser,
        apply_message_to_state,
        build_rm_frame,
        decode_payload,
        decode_rm_frame,
        demod_message_to_dict,
        dict_to_demod_message,
        format_message_line,
    )
    from RX.types import DemodState

    state = DemodState()

    location_payload = struct.pack("<12H", *range(1, 13))
    location = decode_payload(CMD_0A01, location_payload)
    assert location.to_xy_pairs()[0] == (1, 2)
    assert location.to_xy_pairs()[-1] == (11, 12)

    hp = decode_payload(CMD_0A02, struct.pack("<6H", 100, 90, 80, 70, 60, 50))
    assert hp.hero_hp == 100
    assert hp.sentry_hp == 50

    bullets = decode_payload(CMD_0A03, struct.pack("<5H", 1, 2, 3, 4, 5))
    assert bullets.inf4_bullets == 3

    flags = (1 << 0) | (2 << 1) | (1 << 3) | (3 << 4) | (2 << 6)
    enemy_status = decode_payload(CMD_0A04, struct.pack("<HHI", 1000, 2000, flags))
    assert enemy_status.supply_status == 1
    assert enemy_status.central_status == 2
    assert enemy_status.fortress_status == 3
    assert enemy_status.outpost_status == 2

    buff_payload = bytes(range(41))
    buff_frame = build_rm_frame(CMD_0A05, 7, buff_payload)
    buff_message = decode_rm_frame(buff_frame)
    assert buff_message.payload.sentry_pose == 35
    assert buff_message.payload.hero_state == 36
    assert buff_message.payload.enemy_is_invincible.hero == 1
    assert buff_message.payload.engineer_state == 37
    assert buff_message.payload.inf3_state == 38
    assert buff_message.payload.inf4_state == 39
    assert buff_message.payload.sentry_state == 40
    assert dict_to_demod_message(demod_message_to_dict(buff_message)) == buff_message
    assert "sentry_pose=35" in format_message_line(buff_message)
    apply_message_to_state(state, buff_message)
    assert state.buff_status is not None
    assert state.buff_status.value.sentry_state == 40
    buff_payload = bytearray(41)
    buff_payload[36] = 0
    assert decode_payload(CMD_0A05, bytes(buff_payload)).enemy_is_invincible.hero == 0
    buff_payload[36] = 3
    assert decode_payload(CMD_0A05, bytes(buff_payload)).enemy_is_invincible.hero == 1
    buff_payload[37] = 2
    buff_payload[38] = 1
    buff_payload[39] = 3
    buff_payload[40] = 0
    invincible = decode_payload(CMD_0A05, bytes(buff_payload)).enemy_is_invincible
    assert invincible.engineer == 1
    assert invincible.inf3 == 1
    assert invincible.inf4 == 1
    assert invincible.aerial == 0
    assert invincible.sentry == 0

    key_frame = build_rm_frame(CMD_0A06, 8, b"AbC123")
    key_message = decode_rm_frame(key_frame)
    assert key_message.payload.key == "AbC123"
    apply_message_to_state(state, key_message)
    assert state.jamming_key is not None
    assert state.jamming_key.value.key == "AbC123"

    try:
        decode_payload(CMD_0A06, b"ABC12!")
    except ValueError:
        pass
    else:
        raise AssertionError("0x0A06 must reject non-alphanumeric six-byte keys")

    try:
        decode_payload(CMD_0A05, bytes(range(40)))
    except ValueError:
        pass
    else:
        raise AssertionError("0x0A05 must reject 40-byte payloads")

    stream = RMFrameStreamParser()
    parsed = stream.feed(buff_frame[:3])
    assert parsed == []
    parsed = stream.feed(buff_frame[3:] + key_frame)
    assert [message.cmd_id for message in parsed] == [CMD_0A05, CMD_0A06]


def verify_referee_protocol() -> None:
    from driver.referee.messages import (
        Radar2ClientData,
        Radar2ClientMessage,
        Radar2RobotData,
        RadarDecisionData,
        RadarDecisionMessage,
        RadarInfoData,
        RadarLocationFrame,
        RadarRobotID,
        RadarStatusFrame,
        RobotHPData,
        RobotHPMessage,
        RobotStatusData,
        Sentry2RadarData,
        Sentry2RadarMessage,
    )
    from driver.referee.protocol import Crc, MsgID, SubCmdID

    expected_sizes = {
        RobotHPData: 20,
        RobotStatusData: 17,
        RadarInfoData: 1,
        Radar2ClientData: 48,
        RadarDecisionData: 8,
        RadarRobotID: 12,
        RadarStatusFrame: 108,
        Radar2RobotData: 112,
        RadarLocationFrame: 54,
        Sentry2RadarData: 41,
    }
    for cls, expected in expected_sizes.items():
        actual = ctypes.sizeof(cls)
        assert actual == expected, f"{cls.__name__}: {actual} != {expected}"

    hp_payload = bytes(range(20))
    hp_msg = RobotHPMessage.from_bytes(hp_payload)
    assert hp_msg.enemy_outpost_hp == 0x1110
    assert hp_msg.enemy_base_hp == 0x1312

    radar_decision = RadarDecisionMessage(
        is_blue=True,
        radar_cmd=1,
        password_cmd=2,
        password_1=ord("A"),
        password_2=ord("B"),
        password_3=ord("C"),
        password_4=ord("1"),
        password_5=ord("2"),
        password_6=ord("3"),
    ).pack()
    assert radar_decision[0] == 0xA5
    assert Crc.verify_crc8_check_sum(bytearray(radar_decision[:5]))
    assert Crc.verify_crc16_check_sum(bytearray(radar_decision))
    assert struct.unpack("<H", radar_decision[1:3])[0] == 14
    assert struct.unpack("<H", radar_decision[5:7])[0] == MsgID.INTERACTIVE_DATA.value
    assert struct.unpack("<H", radar_decision[7:9])[0] == SubCmdID.RADAR_DECISION.value
    assert radar_decision[13:21] == bytes([1, 2]) + b"ABC123"

    radar2client = Radar2ClientMessage().pack()
    assert radar2client[0] == 0xA5
    assert Crc.verify_crc8_check_sum(bytearray(radar2client[:5]))
    assert Crc.verify_crc16_check_sum(bytearray(radar2client))
    assert struct.unpack("<H", radar2client[1:3])[0] == 48
    assert struct.unpack("<H", radar2client[5:7])[0] == MsgID.CLIENT_RADAR_DATA.value

    assert Sentry2RadarMessage.SUB_CMD_ID == SubCmdID.SENTRY_2_RADAR.value


def verify_referee_break_key_path() -> None:
    stubbed = _install_optional_dependency_stubs_if_needed()
    from driver.referee.protocol import MsgID, OBJECT_ID, SubCmdID
    from driver.referee.referee_comm import RefereeCommManager

    manager = RefereeCommManager.__new__(RefereeCommManager)
    manager.faction = "red"
    manager.request_count = 5
    manager.encryption_level = 1
    manager.break_key_timeout = 11.0
    manager.break_key_correct = None
    manager.break_key_pending = False
    manager.break_key_start_time = 0.0
    manager.break_key_base_level = 1
    manager.next_break_key_send_time = 0.0
    manager.pending_break_key = None
    manager.interactive_tx_lock = threading.Lock()
    manager.interactive_tx_queue = deque()

    assert RefereeCommManager.break_keys(manager, "AbC123") is True
    assert manager.break_key_pending is True
    assert manager.break_key_base_level == 1
    assert len(manager.interactive_tx_queue) == 1

    frame = manager.interactive_tx_queue[0]
    assert struct.unpack("<H", frame[1:3])[0] == 14
    assert struct.unpack("<H", frame[5:7])[0] == MsgID.INTERACTIVE_DATA.value
    assert struct.unpack("<H", frame[7:9])[0] == SubCmdID.RADAR_DECISION.value
    assert struct.unpack("<H", frame[9:11])[0] == OBJECT_ID.R_RADAR.value
    assert struct.unpack("<H", frame[11:13])[0] == OBJECT_ID.SERVER.value
    assert frame[13:21] == bytes([5, 2]) + b"AbC123"

    assert RefereeCommManager.break_keys(manager, "ZZ9999") is False
    assert manager.pending_break_key == "ZZ9999"
    assert len(manager.interactive_tx_queue) == 1

    radar_info = bytes([(1 << 0) | (2 << 3) | (1 << 5)])
    RefereeCommManager.radar_info_message_decode_func(
        manager,
        MsgID.RADAR_DECISION_SYNC.value,
        radar_info,
    )
    assert manager.double_vulnerability_count == 1
    assert manager.encryption_level == 2
    assert manager.can_modify_password == 1
    assert manager.break_key_correct is True
    assert manager.break_key_pending is False
    assert manager.pending_break_key is None
    if stubbed:
        print(f"optional dependency stubs used for referee logic checks: {', '.join(stubbed)}")


def _eval_generated_expr(expr: str, variables: dict[str, float]) -> float:
    normalized = expr.strip()
    return float(eval(normalized, {"__builtins__": {}}, variables))


def _extract_generated_flowgraph_values(path: Path) -> tuple[object, ...]:
    text = path.read_text(encoding="utf-8")

    sps_match = re.search(r"\bsps\s*=\s*sps\s*=\s*(\d+)", text)
    variables: dict[str, float] = {"samp_rate": 1_000_000.0}
    if sps_match is not None:
        variables["sps"] = float(sps_match.group(1))
    else:
        symbol_sync_match = re.search(
            r"digital\.symbol_sync_ff\(\s*"
            r"digital\.TED_MUELLER_AND_MULLER,\s*"
            r"([^,\n]+)",
            text,
            re.S,
        )
        if symbol_sync_match is None:
            raise AssertionError(f"missing symbol_sync sps in {path}")
        variables["sps"] = _eval_generated_expr(symbol_sync_match.group(1), variables)
    variables["symbol_rate"] = variables["samp_rate"] / variables["sps"]

    for name in ("center_freq", "center_freq_0"):
        match = re.search(rf"\b{name}\s*=\s*{name}\s*=\s*([0-9.eE_]+)", text)
        if match is not None:
            variables[name] = _eval_generated_expr(match.group(1), variables)

    freq_match = re.search(r"\.set_frequency\(([^)]+)\)", text)
    gain_mode_match = re.search(r"\.set_gain_mode\(0,\s*'([^']+)'\)", text)
    gain_match = re.search(r"\.set_gain\(0,\s*([0-9]+)\)", text)
    xlat_match = re.search(
        r"freq_xlating_fir_filter_ccc\(\s*"
        r"([^,]+),\s*"
        r"firdes\.low_pass\(\s*1\.0,\s*([^,]+),\s*([^,]+),\s*([^,)]+)\)",
        text,
    )
    low_pass_match = re.search(
        r"filter_fft_low_pass_filter_0_0\s*=\s*filter\.fft_filter_fff\(\s*"
        r"1,\s*firdes\.low_pass\(\s*1,\s*([^,]+),\s*([^,]+),",
        text,
    )
    quadrature_match = re.search(r"analog\.quadrature_demod_cf\(\(([^)]+)\)\)", text)
    max_data_len_match = re.search(r"\.blk\(.*?max_data_len=([0-9]+)", text, re.S)
    mode_match = re.search(r"\.blk\(mode='([^']+)'", text)

    required = [
        freq_match,
        gain_mode_match,
        gain_match,
        xlat_match,
        low_pass_match,
        quadrature_match,
        max_data_len_match,
        mode_match,
    ]
    if any(match is None for match in required):
        raise AssertionError(f"missing generated flowgraph parameter in {path}")

    return (
        mode_match.group(1),
        int(_eval_generated_expr(freq_match.group(1), variables)),
        gain_mode_match.group(1),
        int(gain_match.group(1)),
        int(_eval_generated_expr(xlat_match.group(1), variables)),
        _eval_generated_expr(xlat_match.group(3), variables),
        _eval_generated_expr(xlat_match.group(4), variables),
        _eval_generated_expr(low_pass_match.group(2), variables),
        _eval_generated_expr(quadrature_match.group(1), variables),
        int(variables["sps"]),
        int(max_data_len_match.group(1)),
    )


def verify_rx_new_sources() -> None:
    expected_source_paths = {
        ("red", "base"): ROOT / "RX/RX_new/red-base/REDBASEDATA.py",
        ("red", "level1"): ROOT / "RX/RX_new/red-level1/REDLEVEL1NEW.py",
        ("red", "level2"): ROOT / "RX/RX_new/red-level2/REDLEVEL2NEW.py",
        ("blue", "base"): ROOT / "RX/RX_new/blue-base/RX_BLUE_BASE.py",
        ("blue", "level1"): ROOT / "RX/RX_new/blue-level1/BLUELEVEL1NEW.py",
        ("blue", "level2"): ROOT / "RX/RX_new/blue-level2/BLUELEVEL2NEW.py",
    }
    expected_modes = {
        ("red", "base"): "signal",
        ("red", "level1"): "jamming",
        ("red", "level2"): "jamming",
        ("blue", "base"): "signal",
        ("blue", "level1"): "jamming",
        ("blue", "level2"): "jamming",
    }
    expected_generated_runtime_constraints = {
        ("red", "base"): (False, True, ("RX_RED_BASE",)),
        ("red", "level1"): (True, False, ()),
        ("red", "level2"): (True, False, ("02",)),
        ("blue", "base"): (True, False, ()),
        ("blue", "level1"): (True, False, ()),
        ("blue", "level2"): (True, False, ()),
    }

    from RX.runtime import FLOWGRAPH_SPECS, get_flowgraph_spec

    assert set(FLOWGRAPH_SPECS) == set(expected_source_paths)
    for key, expected_path in expected_source_paths.items():
        spec = get_flowgraph_spec(*key)
        path = ROOT / spec.source_path
        assert path == expected_path, f"{key}: {path} != {expected_path}"
        assert path.exists(), path
        generated = _extract_generated_flowgraph_values(path)
        project = (
            spec.mode,
            spec.center_freq,
            spec.gain_mode,
            spec.gain,
            spec.xlating_decimation,
            spec.filter_cutoff,
            spec.filter_transition,
            spec.low_pass_cutoff,
            spec.quadrature_gain,
            spec.sps,
            spec.max_data_len,
        )
        assert spec.mode == expected_modes[key]
        assert project == generated, f"{key}: {project} != {generated}"

        text = path.read_text(encoding="utf-8")
        init_match = re.search(
            r"class\s+\w+\(gr\.top_block,\s*Qt\.QWidget\):\n\n\s+def __init__\(([^)]*)\):",
            text,
        )
        assert init_match is not None, path
        has_uri_param, has_fixed_uri_literal, expected_file_sinks = expected_generated_runtime_constraints[key]
        assert "Qt.QWidget.__init__(self)" in text, path
        assert "Qt.QApplication" in text, path
        assert ("uri=" in init_match.group(1)) is has_uri_param, path
        assert ("'ip:192.168.2.1' if 'ip:192.168.2.1'" in text) is has_fixed_uri_literal, path
        file_sinks = tuple(re.findall(r"blocks\.file_sink\([^,]+,\s*'([^']+)'", text))
        assert file_sinks == expected_file_sinks, f"{key}: {file_sinks} != {expected_file_sinks}"

    for path in sorted((ROOT / "RX/RX_new").glob("*/*epy_block*.py")):
        text = path.read_text(encoding="utf-8")
        assert re.search(r"OTA_PAYLOAD_LEN\s*=\s*15\b", text), path
        assert re.search(r"CMD_0A05:\s*41\b", text), path
        assert "def _emit_log(self, text: str):" in text, path
        assert "message_port_pub(self.out_port, pmt.intern(text))" in text, path
        assert "pmt.to_pmt" not in text, path
        assert "pmt.make_dict" not in text, path
        assert "pmt.init_u8vector" not in text, path


def verify_config() -> None:
    config_text = (ROOT / "config" / "params.yaml").read_text(encoding="utf-8")
    assert "decode_timeout: 30.0" in config_text
    assert "tx_interval: 0.2" in config_text


def _wait_until(predicate, timeout: float, message: str) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return
        time.sleep(0.02)
    raise AssertionError(message)


def verify_demod_control_loop() -> None:
    from RX.protocol import CMD_0A01, CMD_0A06, build_rm_frame, decode_rm_frame
    from RX.receiver import DemodController
    from RX.runtime import FakeFlowgraphRuntime
    from RX.sender import DemodProcessManager

    controller = DemodController(
        side="red",
        target_level=2,
        host="127.0.0.1",
        port=9999,
        timeout=1.0,
        auto_decode=False,
        auto_advance=True,
    )
    manager = DemodProcessManager(
        server_ip="127.0.0.1",
        port=9999,
        signal_uri="fake-signal",
        jamming_uri="fake-jamming",
        reconnect_interval=0.05,
        record_signal=False,
        record_jamming=False,
        flowgraph_factory=FakeFlowgraphRuntime,
    )

    def send_to_manager(packet: dict) -> bool:
        manager.handle_app_message(packet)
        return True

    def send_to_controller(packet: dict) -> bool:
        controller._handle_app_message(packet)
        return True

    controller._send = send_to_manager
    manager._send = send_to_controller
    controller.running = True
    manager.running = True

    try:
        controller._send({"type": "init", "side": controller.side})

        _wait_until(lambda: controller.get_snapshot()["ready"], 2.0, "demod controller did not become ready")

        signal_message = decode_rm_frame(
            build_rm_frame(CMD_0A01, 1, struct.pack("<12H", *range(10, 22)))
        )
        with manager.lock:
            assert manager.signal_runtime is not None
            manager.signal_runtime.emit(signal_message)

        _wait_until(
            lambda: controller.get_snapshot()["state"].location is not None,
            1.0,
            "signal message did not reach controller state",
        )

        decode_results: list[bool] = []
        decode_thread = threading.Thread(
            target=lambda: decode_results.append(controller.try_decode()),
            name="verify_demod_try_decode",
        )
        decode_thread.start()

        _wait_until(
            lambda: manager.get_stats()["pending_jamming_level"] == "level1"
            or manager.get_stats()["jamming_level"] == "level1",
            2.0,
            "level1 jamming runtime was not requested",
        )

        key_message = decode_rm_frame(build_rm_frame(CMD_0A06, 2, b"AbC123"))
        with manager.lock:
            assert manager.jamming_runtime is not None
            manager.jamming_runtime.emit(key_message)

        decode_thread.join(timeout=2.0)
        assert not decode_thread.is_alive(), "try_decode did not finish after 0x0A06"
        assert decode_results == [True]
        _wait_until(
            lambda: controller.get_snapshot()["current_level"] == 2,
            2.0,
            "0x0A06 decode success did not advance current_level",
        )
        snapshot = controller.get_snapshot()
        assert snapshot["state"].jamming_key is not None
        assert snapshot["state"].jamming_key.value.key == "AbC123"
        assert snapshot["success_request_id"] is not None
        assert snapshot["active_request_id"] is None
    finally:
        manager.stop()
        controller.running = False


def main() -> None:
    verify_rx_protocol()
    verify_referee_protocol()
    verify_referee_break_key_path()
    numpy_stubbed = _install_numpy_stub_if_needed()
    verify_rx_new_sources()
    verify_config()
    verify_demod_control_loop()
    if numpy_stubbed:
        print("numpy is not installed; RX runtime checks used a minimal numpy type stub.")
    print("protocol update verification passed")


if __name__ == "__main__":
    main()
