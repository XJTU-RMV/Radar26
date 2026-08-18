from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
import threading
import time
from typing import Callable

import numpy as np

from .protocol import (
    ALL_CMDS,
    CMD_0A06,
    EXPECTED_PAYLOAD_LEN,
    JAMMING_CMDS,
    SIGNAL_CMDS,
    crc8_rm,
    crc16_rm,
    decode_payload,
)
from .types import ProtocolMessage


ACCESS_CODE_SIGNAL = bytes.fromhex("2F6F4C74B914492E")
ACCESS_CODE_JAMMING = bytes.fromhex("16E8D377151C712D")
OTA_HEADER = bytes.fromhex("000F000F")
OTA_PAYLOAD_LEN = 15


@dataclass(frozen=True)
class FlowgraphSpec:
    side: str
    level: str
    mode: str
    source_path: str
    center_freq: int
    gain_mode: str
    gain: int
    xlating_decimation: int
    filter_cutoff: float
    filter_transition: float
    low_pass_cutoff: float
    quadrature_gain: float
    sps: int
    max_data_len: int

    @property
    def allowed_cmds(self) -> set[int]:
        if self.mode == "signal":
            return set(SIGNAL_CMDS)
        if self.mode == "jamming":
            return set(JAMMING_CMDS)
        return set(ALL_CMDS)


FLOWGRAPH_SPECS: dict[tuple[str, str], FlowgraphSpec] = {
    ("red", "base"): FlowgraphSpec("red", "base", "signal", "RX/RX_new/red-base/REDBASEDATA.py", 433_200_000, "fast_attack", 30, 1, 260e3, 20e3, 1_000_000 / 47, 1 / 1.5628, 47, 80),
    ("red", "level1"): FlowgraphSpec("red", "level1", "jamming", "RX/RX_new/red-level1/REDLEVEL1NEW.py", 432_200_000, "fast_attack", 30, 1, 470e3, 20e3, 1_000_000 / 47, 1 / 2.8194, 47, 16),
    ("red", "level2"): FlowgraphSpec("red", "level2", "jamming", "RX/RX_new/red-level2/REDLEVEL2NEW.py", 432_500_000, "fast_attack", 30, 1, 430e3, 30e3, 21276.6, 1 / 2.5681, 47, 16),
    ("blue", "base"): FlowgraphSpec("blue", "base", "signal", "RX/RX_new/blue-base/RX_BLUE_BASE.py", 433_920_000, "fast_attack", 30, 1, 260e3, 20e3, 21276.6, 1 / 1.5628, 47, 80),
    ("blue", "level1"): FlowgraphSpec("blue", "level1", "jamming", "RX/RX_new/blue-level1/BLUELEVEL1NEW.py", 434_920_000, "fast_attack", 30, 1, 470e3, 20e3, 21276.6, 1 / 2.8194, 47, 16),
    ("blue", "level2"): FlowgraphSpec("blue", "level2", "jamming", "RX/RX_new/blue-level2/BLUELEVEL2NEW.py", 434_620_000, "fast_attack", 30, 1, 430e3, 30e3, 21276.6, 1 / 2.5681, 47, 16),
}


def normalize_side(side: str) -> str:
    normalized = str(side).strip().lower()
    if normalized not in {"red", "blue"}:
        raise ValueError(f"side must be 'red' or 'blue', got {side!r}")
    return normalized


def level_name(level: int | str) -> str:
    if isinstance(level, int):
        if level == 0:
            return "base"
        if level in (1, 2):
            return f"level{level}"
        raise ValueError(f"unsupported demod level {level!r}")
    normalized = str(level).strip().lower()
    if normalized in {"base", "level1", "level2"}:
        return normalized
    raise ValueError(f"unsupported demod level {level!r}")


def get_flowgraph_spec(side: str, level: int | str) -> FlowgraphSpec:
    return FLOWGRAPH_SPECS[(normalize_side(side), level_name(level))]


def bytes_to_bits_msb(data: bytes) -> np.ndarray:
    return np.unpackbits(np.frombuffer(data, dtype=np.uint8))


def bytes_to_bits_lsb(data: bytes) -> np.ndarray:
    bits = np.unpackbits(np.frombuffer(data, dtype=np.uint8))
    return bits.reshape(-1, 8)[:, ::-1].reshape(-1).astype(np.uint8)


class RadarAirParser:
    def __init__(
        self,
        mode: str,
        *,
        input_format: str = "packed",
        bit_order: str = "msb",
        allow_soft_crc8: bool = True,
        ac_min_match_bits: int = 60,
        hdr_max_bit_errors: int = 2,
        max_data_len: int = 80,
        dedup_ttl: float = 5.0,
        min_sep_bits: int = 216,
    ):
        self.mode = mode.strip().lower()
        self.input_format = input_format.strip().lower()
        self.bit_order = bit_order.strip().lower()
        self.allow_soft_crc8 = bool(allow_soft_crc8)
        self.max_data_len = int(max_data_len)
        self.dedup_ttl = float(dedup_ttl)
        self.min_sep_bits = int(min_sep_bits)

        if self.mode == "signal":
            self.allowed_cmds = set(SIGNAL_CMDS)
            access_code = ACCESS_CODE_SIGNAL
        elif self.mode == "jamming":
            self.allowed_cmds = set(JAMMING_CMDS)
            access_code = ACCESS_CODE_JAMMING
            self.max_data_len = min(self.max_data_len, 16)
        else:
            self.allowed_cmds = set(ALL_CMDS)
            access_code = ACCESS_CODE_SIGNAL

        if self.bit_order == "msb":
            self.access_bits = bytes_to_bits_msb(access_code)
            self.header_bits = bytes_to_bits_msb(OTA_HEADER)
            self.pack_bitorder = "big"
        elif self.bit_order == "lsb":
            self.access_bits = bytes_to_bits_lsb(access_code)
            self.header_bits = bytes_to_bits_lsb(OTA_HEADER)
            self.pack_bitorder = "little"
        else:
            raise ValueError("bit_order must be 'msb' or 'lsb'")

        self.access_pm = (self.access_bits.astype(np.int16) * 2) - 1
        self.access_threshold = 2 * int(ac_min_match_bits) - len(self.access_bits)
        self.header_max_errors = int(hdr_max_bit_errors)
        self.ota_frame_bits = len(self.access_bits) + len(self.header_bits) + OTA_PAYLOAD_LEN * 8

        self.hist_bits = np.array([], dtype=np.uint8)
        self.payload_buf = bytearray()
        self.recent_cmd_seq: dict[tuple[int, int], float] = {}
        self.stats = defaultdict(int)

    def feed_air_bytes(self, data: bytes) -> list[ProtocolMessage]:
        self._process_air_bytes(data)
        return self._process_protocol()

    def feed_rm_payload_bytes(self, data: bytes) -> list[ProtocolMessage]:
        self.payload_buf.extend(data)
        return self._process_protocol()

    def _message_to_bits(self, data: bytes) -> np.ndarray:
        if self.input_format == "packed":
            return bytes_to_bits_msb(data) if self.bit_order == "msb" else bytes_to_bits_lsb(data)
        return (np.frombuffer(data, dtype=np.uint8) & 1).astype(np.uint8)

    def _process_air_bytes(self, data: bytes) -> None:
        inp_bits = self._message_to_bits(data)
        if len(inp_bits) == 0:
            return

        old_hist_len = len(self.hist_bits)
        bits = np.concatenate([self.hist_bits, inp_bits])
        if len(bits) < self.ota_frame_bits:
            self.hist_bits = bits[-(self.ota_frame_bits - 1) :].copy()
            return

        bits_pm = (bits.astype(np.int16) * 2) - 1
        corr = np.correlate(bits_pm, self.access_pm, "valid")
        candidates = np.flatnonzero(corr >= self.access_threshold)
        self.stats["ota_candidates"] += len(candidates)

        payloads: list[bytes] = []
        last_accept_start = -10**9
        access_len = len(self.access_bits)
        header_len = len(self.header_bits)
        for start in candidates:
            header_start = start + access_len
            payload_start = header_start + header_len
            payload_end = payload_start + OTA_PAYLOAD_LEN * 8

            if payload_end > len(bits):
                break
            if payload_end <= old_hist_len:
                continue
            if start - last_accept_start < self.min_sep_bits:
                continue
            header_errors = int(np.count_nonzero(bits[header_start:payload_start] ^ self.header_bits))
            if header_errors > self.header_max_errors:
                continue

            payloads.append(np.packbits(bits[payload_start:payload_end], bitorder=self.pack_bitorder).tobytes())
            last_accept_start = start
            self.stats["ota_accept"] += 1

        if payloads:
            self.payload_buf.extend(b"".join(payloads))
        self.hist_bits = bits[-(self.ota_frame_bits - 1) :].copy()

    def _process_protocol(self) -> list[ProtocolMessage]:
        buf = self.payload_buf
        messages: list[ProtocolMessage] = []
        scan = 0
        keep_from = len(buf)

        while True:
            sof = buf.find(b"\xA5", scan)
            if sof < 0 or len(buf) - sof < 5:
                keep_from = len(buf) if sof < 0 else sof
                break

            data_len = buf[sof + 1] | (buf[sof + 2] << 8)
            if data_len > self.max_data_len:
                scan = sof + 1
                self.stats["len_fail"] += 1
                continue

            frame_len = 5 + 2 + data_len + 2
            if len(buf) - sof < frame_len:
                keep_from = sof
                break

            frame = bytes(buf[sof : sof + frame_len])
            crc8_ok = frame[4] == crc8_rm(frame[:4])
            if not crc8_ok:
                self.stats["crc8_fail"] += 1

            if crc16_rm(frame[:-2]) != (frame[-2] | (frame[-1] << 8)):
                scan = sof + 1
                self.stats["frame_drop"] += 1
                continue

            cmd_id = frame[5] | (frame[6] << 8)
            payload = frame[7:-2]
            if (
                cmd_id not in EXPECTED_PAYLOAD_LEN
                or len(payload) != EXPECTED_PAYLOAD_LEN[cmd_id]
                or cmd_id not in self.allowed_cmds
            ):
                scan = sof + 1 if cmd_id not in EXPECTED_PAYLOAD_LEN else sof + frame_len
                self.stats["cmd_drop"] += 1
                continue

            if not crc8_ok and not self.allow_soft_crc8:
                scan = sof + frame_len
                self.stats["crc8_drop"] += 1
                continue

            try:
                message = ProtocolMessage(
                    cmd_id=cmd_id,
                    seq=frame[3],
                    payload=decode_payload(cmd_id, payload),
                    time_stamp=time.time(),
                )
            except ValueError:
                scan = sof + 1
                self.stats["frame_drop"] += 1
                continue

            if crc8_ok:
                self.stats["hard_ok"] += 1
            else:
                self.stats["soft_ok"] += 1

            if self._is_unique(message.cmd_id, message.seq):
                messages.append(message)
            else:
                self.stats["dup_drop"] += 1
            scan = sof + frame_len

        if keep_from >= len(buf):
            del buf[:]
        elif keep_from > 0:
            del buf[:keep_from]
        return messages

    def _is_unique(self, cmd_id: int, seq: int) -> bool:
        now = time.time()
        stale = [key for key, timestamp in self.recent_cmd_seq.items() if now - timestamp > self.dedup_ttl]
        for key in stale:
            self.recent_cmd_seq.pop(key, None)
        key = (cmd_id, seq)
        if key in self.recent_cmd_seq:
            return False
        self.recent_cmd_seq[key] = now
        return True


class FlowgraphRuntime:
    def __init__(
        self,
        side: str,
        level: int | str,
        uri: str = "ip:192.168.2.1",
        record_path: str | None = None,
        message_callback: Callable[[ProtocolMessage], None] | None = None,
    ):
        self.spec = get_flowgraph_spec(side, level)
        self.uri = uri
        self.record_path = record_path
        self.message_callback = message_callback
        self._flowgraph = _HeadlessFlowgraph(self.spec, uri, record_path, self._handle_message)

    def start(self) -> None:
        self._flowgraph.start()

    def stop(self) -> None:
        self._flowgraph.stop()
        self._flowgraph.wait()

    def wait(self) -> None:
        self._flowgraph.wait()

    def get_debug_stats(self) -> dict[str, object]:
        return self._flowgraph.get_debug_stats()

    def _handle_message(self, message: ProtocolMessage) -> None:
        if self.message_callback is not None:
            self.message_callback(message)


class _HeadlessFlowgraph:
    def __init__(
        self,
        spec: FlowgraphSpec,
        uri: str,
        record_path: str | None,
        callback: Callable[[ProtocolMessage], None],
    ):
        try:
            from gnuradio import analog, blocks, digital, filter, gr, iio
            from gnuradio.fft import window
            from gnuradio.filter import firdes
        except ImportError as exc:
            raise RuntimeError("GNU Radio is required to run RX flowgraphs") from exc

        class DecoderBlock(gr.basic_block):
            def __init__(self, parser: RadarAirParser):
                gr.basic_block.__init__(self, name="rx_structured_decoder", in_sig=[np.uint8], out_sig=[])
                self.parser = parser

            def general_work(self, input_items, output_items):
                inp = input_items[0]
                for message in self.parser.feed_air_bytes(inp.tobytes()):
                    callback(message)
                self.consume(0, len(inp))
                return 0

        self._gr = gr
        self._tb = gr.top_block(f"RX {spec.side} {spec.level}", catch_exceptions=True)

        samp_rate = 1_000_000
        sps = spec.sps
        binary_const = digital.constellation_calcdist(
            [-1 + 0j, 1 + 0j],
            [0, 1],
            2,
            1,
            digital.constellation.AMPLITUDE_NORMALIZATION,
        ).base()
        binary_const.set_npwr(1.0)

        source = iio.fmcomms2_source_fc32(uri if uri else iio.get_pluto_uri(), [True, True], 32768)
        source.set_len_tag_key("packet_len")
        source.set_frequency(spec.center_freq)
        source.set_samplerate(samp_rate)
        source.set_gain_mode(0, spec.gain_mode)
        source.set_gain(0, spec.gain)
        source.set_quadrature(True)
        source.set_rfdc(True)
        source.set_bbdc(True)
        source.set_filter_params("Auto", "", 0, 0)
        record_sink = None
        if record_path is not None:
            record_sink = blocks.file_sink(gr.sizeof_gr_complex, record_path, False)
            record_sink.set_unbuffered(False)

        translating_filter = filter.freq_xlating_fir_filter_ccc(
            spec.xlating_decimation,
            firdes.low_pass(1.0, samp_rate, spec.filter_cutoff, spec.filter_transition),
            0,
            samp_rate,
        )
        quadrature_demod = analog.quadrature_demod_cf(spec.quadrature_gain)
        low_pass = filter.fft_filter_fff(
            1,
            firdes.low_pass(1, samp_rate, spec.low_pass_cutoff, 2000, window.WIN_BLACKMAN, 6.76),
            1,
        )
        symbol_sync = digital.symbol_sync_ff(
            digital.TED_MUELLER_AND_MULLER,
            sps,
            0.05,
            1.0,
            1.0,
            1.5,
            1,
            binary_const,
            digital.IR_MMSE_8TAP,
            32,
            firdes.root_raised_cosine(32, 32, 1.0, 0.25, 11 * 8 * 32),
        )
        slicer = digital.binary_slicer_fb()
        packer = blocks.unpacked_to_packed_bb(1, gr.GR_MSB_FIRST)
        parser = RadarAirParser(spec.mode, max_data_len=spec.max_data_len)
        decoder = DecoderBlock(parser)
        self.parser = parser

        self._tb.connect((source, 0), (translating_filter, 0))
        if record_sink is not None:
            self._tb.connect((source, 0), (record_sink, 0))
        self._tb.connect((translating_filter, 0), (quadrature_demod, 0))
        self._tb.connect((quadrature_demod, 0), (low_pass, 0))
        self._tb.connect((low_pass, 0), (symbol_sync, 0))
        self._tb.connect((symbol_sync, 0), (slicer, 0))
        self._tb.connect((slicer, 0), (packer, 0))
        self._tb.connect((packer, 0), (decoder, 0))

        self.blocks = {
            "source": source,
            "decoder": decoder,
            "record_sink": record_sink,
        }

    def start(self) -> None:
        self._tb.start()

    def stop(self) -> None:
        self._tb.stop()

    def wait(self) -> None:
        self._tb.wait()

    def get_debug_stats(self) -> dict[str, object]:
        return {
            "mode": self.parser.mode,
            "parser_stats": dict(self.parser.stats),
        }


class FakeFlowgraphRuntime:
    def __init__(self, side: str, level: int | str, uri: str = "", record_path: str | None = None, message_callback=None):
        self.spec = get_flowgraph_spec(side, level)
        self.uri = uri
        self.record_path = record_path
        self.message_callback = message_callback
        self.started = False
        self.stopped = False
        self._stop_event = threading.Event()

    def start(self) -> None:
        self._stop_event.clear()
        self.started = True
        self.stopped = False

    def stop(self) -> None:
        self.stopped = True
        self.started = False
        self._stop_event.set()

    def wait(self) -> None:
        self._stop_event.wait()

    def get_debug_stats(self) -> dict[str, object]:
        return {"parser_stats": {}}

    def emit(self, message: ProtocolMessage) -> None:
        if self.message_callback is not None:
            self.message_callback(message)
