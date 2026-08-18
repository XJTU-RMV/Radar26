import numpy as np
from gnuradio import gr
import time
import string
from collections import defaultdict, deque
import pmt  # 用于 GNU Radio 消息传递

# ============================================================
# 常量定义
# ============================================================
SOF = 0xA5

# 雷达无线链路空口同步码
ACCESS_CODE_SIGNAL = bytes.fromhex("2F6F4C74B914492E")
ACCESS_CODE_JAMMING = bytes.fromhex("16E8D377151C712D")

# 空口 Header：两份 0x000F
OTA_HEADER = bytes.fromhex("000F000F")

# 注意：
# 这里是空口每个 OTA payload 的分片长度，仍然是 15 字节。
# 不要因为 0x0A05 的协议数据长度变成 41 字节而改这里。
OTA_PAYLOAD_LEN = 15

# 雷达无线链路 cmd_id
CMD_0A01 = 0x0A01
CMD_0A02 = 0x0A02
CMD_0A03 = 0x0A03
CMD_0A04 = 0x0A04
CMD_0A05 = 0x0A05
CMD_0A06 = 0x0A06

# ============================================================
# 新版通信协议 V2.0.0 雷达无线链路数据长度
# 0x0A05 已由旧版 36 字节修改为新版 41 字节
# ============================================================
EXPECTED_LEN = {
    CMD_0A01: 24,  # 对方机器人位置坐标
    CMD_0A02: 12,  # 对方机器人血量
    CMD_0A03: 10,  # 对方机器人剩余发弹量
    CMD_0A04: 8,   # 对方队伍宏观状态
    CMD_0A05: 41,  # 对方各机器人当前增益效果 + 哨兵姿态 + 机器人主要状态
    CMD_0A06: 6,   # 对方干扰波密钥
}


# ============================================================
# 工具函数
# ============================================================
def crc8_rm(data: bytes, init: int = 0xFF) -> int:
    """
    RoboMaster CRC8
    官方多项式：0x31
    这里使用 LSB-first 反射形式：0x8C
    """
    poly = 0x8C
    crc = init & 0xFF

    for b in data:
        crc ^= b
        for _ in range(8):
            if crc & 0x01:
                crc = ((crc >> 1) ^ poly) & 0xFF
            else:
                crc = (crc >> 1) & 0xFF

    return crc & 0xFF


def crc16_rm(data: bytes, init: int = 0xFFFF) -> int:
    """
    RoboMaster CRC16
    LSB-first poly = 0x8408
    """
    poly = 0x8408
    crc = init & 0xFFFF

    for b in data:
        crc ^= b
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ poly
            else:
                crc >>= 1
            crc &= 0xFFFF

    return crc & 0xFFFF


def bytes_to_bits_msb(b: bytes) -> np.ndarray:
    return np.unpackbits(np.frombuffer(b, dtype=np.uint8)).astype(np.uint8)


def bytes_to_bits_lsb(b: bytes) -> np.ndarray:
    arr = np.frombuffer(b, dtype=np.uint8)
    out = np.unpackbits(arr)
    out = out.reshape(-1, 8)[:, ::-1].reshape(-1)
    return out.astype(np.uint8)


def u16_le(b: bytes, off: int) -> int:
    return int.from_bytes(b[off:off + 2], "little", signed=False)


def u32_le(b: bytes, off: int) -> int:
    return int.from_bytes(b[off:off + 4], "little", signed=False)


def is_ascii_alnum_payload(payload: bytes) -> bool:
    allowed = set((string.ascii_letters + string.digits).encode("ascii"))
    return all(x in allowed for x in payload)


# ============================================================
# GNU Radio 自定义 Python 模块
# ============================================================
class blk(gr.basic_block):
    """
    Radar Terminal Decoder Block

    输入：
        GNU Radio 流输入，uint8。
        默认 input_format="packed"，即前级 Unpacked to Packed 输出的字节流。

    输出：
        通过 GNU Radio 消息端口 decoded_out 输出解码结果。
    """

    def __init__(
        self,
        mode="signal",
        input_format="packed",
        bit_order="msb",
        show_soft=False,
        allow_soft_crc8=True,
        soft_repeat=3,
        ac_min_match_bits=60,
        hdr_max_bit_errors=2,
        max_data_len=80,
        stats_interval=1.0,
        rate_window=1.0,
        only_stats=False,
        dedup_ttl=5.0,
        min_sep_bits=216,
        require_0a06_ascii=True,
        enable_console_print=False
    ):
        gr.basic_block.__init__(
            self,
            name="Radar Terminal Decoder",
            in_sig=[np.uint8],
            out_sig=[]
        )

        self.mode = str(mode).strip().lower()
        self.input_format = str(input_format).strip().lower()
        self.bit_order = str(bit_order).strip().lower()
        self.show_soft = bool(show_soft)
        self.allow_soft_crc8 = bool(allow_soft_crc8)
        self.soft_repeat = int(soft_repeat)
        self.ac_min_match_bits = int(ac_min_match_bits)
        self.hdr_max_bit_errors = int(hdr_max_bit_errors)
        self.max_data_len = int(max_data_len)
        self.stats_interval = float(stats_interval)
        self.rate_window = float(rate_window)
        self.only_stats = bool(only_stats)
        self.dedup_ttl = float(dedup_ttl)
        self.require_0a06_ascii = bool(require_0a06_ascii)
        self.min_sep_bits = int(min_sep_bits)
        self.enable_console_print = bool(enable_console_print)

        # 注册 GNU Radio 异步消息输出端口
        self.out_port = pmt.intern("decoded_out")
        self.message_port_register_out(self.out_port)

        # ----------------------------
        # Access Code 选择
        # ----------------------------
        if self.mode == "jamming":
            access_code = ACCESS_CODE_JAMMING
            self.max_data_len = min(self.max_data_len, 16)
        else:
            access_code = ACCESS_CODE_SIGNAL

        if self.mode == "signal":
            self.allowed_cmds = {
                CMD_0A01,
                CMD_0A02,
                CMD_0A03,
                CMD_0A04,
                CMD_0A05,
            }
        elif self.mode == "jamming":
            self.allowed_cmds = {CMD_0A06}
        else:
            self.allowed_cmds = {
                CMD_0A01,
                CMD_0A02,
                CMD_0A03,
                CMD_0A04,
                CMD_0A05,
                CMD_0A06,
            }

        # ----------------------------
        # 比特序设置
        # ----------------------------
        if self.bit_order == "msb":
            self.ac_bits = bytes_to_bits_msb(access_code)
            self.hdr_bits = bytes_to_bits_msb(OTA_HEADER)
            self.pack_bitorder = "big"
        else:
            self.ac_bits = bytes_to_bits_lsb(access_code)
            self.hdr_bits = bytes_to_bits_lsb(OTA_HEADER)
            self.pack_bitorder = "little"

        self.ac_pm = (self.ac_bits.astype(np.int16) * 2) - 1

        # Access Code 共有 64 bit
        # ac_min_match_bits=60 时，允许最多 4 bit 错误
        self.ac_corr_threshold = 2 * self.ac_min_match_bits - 64

        # 空口一包长度：
        # Access Code 8B = 64 bit
        # Header 4B = 32 bit
        # Payload 15B = 120 bit
        # 总计 216 bit
        self.ota_frame_bits = 64 + 32 + OTA_PAYLOAD_LEN * 8

        self.hist_bits = np.array([], dtype=np.uint8)
        self.payload_buf = bytearray()

        self.last_seq_global = None
        self.last_seq_by_cmd = {}

        self.stats = defaultdict(int)

        self.cmd_events_raw = {cmd: deque() for cmd in EXPECTED_LEN.keys()}
        self.cmd_events_uniq = {cmd: deque() for cmd in EXPECTED_LEN.keys()}

        self.kind_events_raw = {
            "hard": deque(),
            "soft": deque(),
            "soft_stable": deque(),
        }
        self.kind_events_uniq = {
            "hard": deque(),
            "soft": deque(),
            "soft_stable": deque(),
        }

        self.recent_cmd_seq = {}
        self.last_stat_time = time.time()

        self.soft_sig_count = defaultdict(int)
        self.soft_sig_last_ts = {}

        self._emit_log(
            f"[INIT] Radar Decoder Started. "
            f"Mode={self.mode}, bit_order={self.bit_order}, "
            f"0x0A05_len={EXPECTED_LEN[CMD_0A05]}, "
            f"console_print={self.enable_console_print}"
        )

    # ========================================================
    # 消息输出
    # ========================================================
    def _emit_log(self, text: str):
        """
        将日志输出到 GNU Radio 的消息端口。
        enable_console_print=True 时，同时输出到终端。
        """
        self.message_port_pub(self.out_port, pmt.intern(text))

        if self.enable_console_print:
            print(text, flush=True)

    # ========================================================
    # 解码逻辑
    # ========================================================
    def _decode_0a01(self, payload: bytes) -> str:
        vals = [u16_le(payload, 2 * i) for i in range(12)]
        names = ["hero", "engineer", "inf3", "inf4", "air", "sentry"]

        parts = []
        for i, name in enumerate(names):
            x = vals[2 * i]
            y = vals[2 * i + 1]
            parts.append(f"{name}=({x},{y})cm")

        return "0x0A01 POS  " + ", ".join(parts)

    def _decode_0a02(self, payload: bytes) -> str:
        h, e, i3, i4, r, s = [u16_le(payload, 2 * i) for i in range(6)]
        return (
            f"0x0A02 HP   "
            f"hero={h}, engineer={e}, inf3={i3}, inf4={i4}, "
            f"reserved={r}, sentry={s}"
        )

    def _decode_0a03(self, payload: bytes) -> str:
        h, i3, i4, a, s = [u16_le(payload, 2 * i) for i in range(5)]
        return (
            f"0x0A03 AMMO "
            f"hero={h}, inf3={i3}, inf4={i4}, air={a}, sentry={s}"
        )

    def _decode_0a04(self, payload: bytes) -> str:
        coins_remain = u16_le(payload, 0)
        coins_total = u16_le(payload, 2)
        flags = u32_le(payload, 4)

        return (
            f"0x0A04 MACRO "
            f"coins_remain={coins_remain}, "
            f"coins_total={coins_total}, "
            f"flags=0x{flags:08X}"
        )

    def _decode_buff_group(self, payload: bytes, off: int, name: str) -> str:
        """
        每个机器人 buff 组 7 字节：
        offset +0: 回血增益，uint8，百分比
        offset +1: 射击热量冷却增益，uint16
        offset +3: 防御增益，uint8，百分比
        offset +4: 负防御增益，uint8，百分比
        offset +5: 攻击增益，uint16，百分比
        """
        return (
            f"{name}["
            f"heal={payload[off]}%, "
            f"cool={u16_le(payload, off + 1)}, "
            f"def={payload[off + 3]}%, "
            f"neg_def={payload[off + 4]}%, "
            f"atk={u16_le(payload, off + 5)}%"
            f"]"
        )

    def _robot_main_state_text(self, v: int) -> str:
        """
        新版 0x0A05 中机器人主要状态：
        0：存活
        1：战亡
        2：无敌但不虚弱
        3：无敌且虚弱
        """
        names = {
            0: "alive",
            1: "dead",
            2: "invincible",
            3: "invincible_weak",
        }
        return names.get(v, f"unknown({v})")

    def _sentry_posture_text(self, v: int) -> str:
        """
        新版 0x0A05 中对方哨兵机器人当前姿态：
        1：进攻姿态
        2：防御姿态
        3：移动姿态
        4：强化进攻姿态
        5：强化防御姿态
        6：强化移动姿态
        """
        names = {
            1: "attack",
            2: "defense",
            3: "move",
            4: "power_attack",
            5: "power_defense",
            6: "power_move",
        }
        return names.get(v, f"unknown({v})")

    def _decode_0a05(self, payload: bytes) -> str:
        """
        新版 0x0A05，41 字节：

        0~6    英雄机器人 buff
        7~13   工程机器人 buff
        14~20  3 号步兵机器人 buff
        21~27  4 号步兵机器人 buff
        28~34  哨兵机器人 buff
        35     哨兵当前姿态
        36     英雄机器人主要状态
        37     工程机器人主要状态
        38     3 号步兵机器人主要状态
        39     4 号步兵机器人主要状态
        40     哨兵机器人主要状态
        """
        if len(payload) < 41:
            return f"0x0A05 BUFF invalid_len={len(payload)}, raw={payload.hex(' ')}"

        posture = payload[35]

        hero_state = self._robot_main_state_text(payload[36])
        eng_state = self._robot_main_state_text(payload[37])
        inf3_state = self._robot_main_state_text(payload[38])
        inf4_state = self._robot_main_state_text(payload[39])
        sentry_state = self._robot_main_state_text(payload[40])

        return (
            f"0x0A05 BUFF "
            f"{self._decode_buff_group(payload, 0, 'hero')}, "
            f"{self._decode_buff_group(payload, 7, 'eng')}, "
            f"{self._decode_buff_group(payload, 14, 'inf3')}, "
            f"{self._decode_buff_group(payload, 21, 'inf4')}, "
            f"{self._decode_buff_group(payload, 28, 'sentry')}, "
            f"posture={self._sentry_posture_text(posture)}, "
            f"state["
            f"hero={hero_state}, "
            f"eng={eng_state}, "
            f"inf3={inf3_state}, "
            f"inf4={inf4_state}, "
            f"sentry={sentry_state}"
            f"]"
        )

    def _decode_0a06(self, payload: bytes) -> str:
        try:
            key = payload.decode("ascii", errors="replace")
        except Exception:
            key = "".join(chr(x) if 32 <= x < 127 else "." for x in payload)

        return f"0x0A06 KEY  {key}"

    def _decode_payload_text(self, cmd_id: int, payload: bytes) -> str:
        if cmd_id == CMD_0A01:
            return self._decode_0a01(payload)
        if cmd_id == CMD_0A02:
            return self._decode_0a02(payload)
        if cmd_id == CMD_0A03:
            return self._decode_0a03(payload)
        if cmd_id == CMD_0A04:
            return self._decode_0a04(payload)
        if cmd_id == CMD_0A05:
            return self._decode_0a05(payload)
        if cmd_id == CMD_0A06:
            return self._decode_0a06(payload)

        return f"cmd=0x{cmd_id:04X}, payload={payload.hex(' ')}"

    # ========================================================
    # 统计与追踪机制
    # ========================================================
    def _prune_deque(self, dq: deque, now_ts: float):
        while dq and (now_ts - dq[0]) > self.rate_window:
            dq.popleft()

    def _prune_recent_cmd_seq(self, now_ts: float):
        stale = [
            k for k, ts in self.recent_cmd_seq.items()
            if (now_ts - ts) > self.dedup_ttl
        ]
        for k in stale:
            self.recent_cmd_seq.pop(k, None)

    def _is_unique_cmd_seq(self, cmd_id: int, seq: int) -> bool:
        now = time.time()
        self._prune_recent_cmd_seq(now)

        key = (cmd_id, seq)
        if key in self.recent_cmd_seq:
            return False

        self.recent_cmd_seq[key] = now
        return True

    def _record_event(self, cmd_id: int, kind: str, unique: bool):
        now = time.time()

        if cmd_id in self.cmd_events_raw:
            self.cmd_events_raw[cmd_id].append(now)

        if kind in self.kind_events_raw:
            self.kind_events_raw[kind].append(now)

        if unique:
            if cmd_id in self.cmd_events_uniq:
                self.cmd_events_uniq[cmd_id].append(now)

            if kind in self.kind_events_uniq:
                self.kind_events_uniq[kind].append(now)

    def _cmd_rate(self, cmd_id: int, unique: bool) -> float:
        dq = self.cmd_events_uniq[cmd_id] if unique else self.cmd_events_raw[cmd_id]
        self._prune_deque(dq, time.time())
        return len(dq) / self.rate_window

    def _kind_rate(self, kind: str, unique: bool) -> float:
        dq = self.kind_events_uniq[kind] if unique else self.kind_events_raw[kind]
        self._prune_deque(dq, time.time())
        return len(dq) / self.rate_window

    def _print_stats(self):
        now = time.time()
        if now - self.last_stat_time < self.stats_interval:
            return

        self.last_stat_time = now

        if self.mode == "signal":
            cmds = [CMD_0A01, CMD_0A02, CMD_0A03, CMD_0A04, CMD_0A05]
        elif self.mode == "jamming":
            cmds = [CMD_0A06]
        else:
            cmds = [CMD_0A01, CMD_0A02, CMD_0A03, CMD_0A04, CMD_0A05, CMD_0A06]

        rates = "  ".join(
            f"0x{cmd:04X}={self._cmd_rate(cmd, True):.1f}/s"
            for cmd in cmds
        )

        self._emit_log(
            "--- STATS ---\n"
            f"[FREQ] {rates}\n"
            f"[TOTAL] "
            f"HARD={self.stats['hard_ok']} "
            f"SOFT={self.stats['soft_ok']} "
            f"SOFT_STABLE={self.stats['soft_stable_ok']} "
            f"DUP={self.stats['dup_drop']} "
            f"CRC8_FAIL={self.stats['crc8_fail']} "
            f"CRC16_FAIL={self.stats['crc16_fail']} "
            f"CMD_DROP={self.stats['cmd_drop']}"
        )

    def _soft_is_stable(self, cmd_id: int, payload: bytes) -> bool:
        sig = f"{cmd_id:04X}:{payload.hex()}"
        now = time.time()

        stale = [
            k for k, ts in self.soft_sig_last_ts.items()
            if now - ts > 1.0
        ]
        for k in stale:
            self.soft_sig_last_ts.pop(k, None)
            self.soft_sig_count.pop(k, None)

        self.soft_sig_last_ts[sig] = now
        self.soft_sig_count[sig] += 1

        return self.soft_sig_count[sig] >= self.soft_repeat

    # ========================================================
    # 核心数据处理流程
    # ========================================================
    def _message_to_bits(self, msg: bytes) -> np.ndarray:
        if self.input_format == "packed":
            if self.bit_order == "msb":
                return bytes_to_bits_msb(msg)
            return bytes_to_bits_lsb(msg)

        # unpacked 模式：每个输入 byte 的最低 bit 作为一个 bit
        return (np.frombuffer(msg, dtype=np.uint8) & 1).astype(np.uint8)

    def _process_air_bytes(self, msg: bytes):
        """
        处理 GNU Radio 输入流中的 packed bytes：
        1. 转为 bit 流
        2. 查找 Access Code
        3. 检查 OTA Header
        4. 提取 15 字节 OTA Payload
        5. 拼接到 payload_buf
        """
        inp_bits = self._message_to_bits(msg)
        if len(inp_bits) == 0:
            return

        old_hist_len = len(self.hist_bits)
        bits = np.concatenate([self.hist_bits, inp_bits])

        if len(bits) < self.ota_frame_bits:
            keep = self.ota_frame_bits - 1
            self.hist_bits = bits[-keep:].copy() if len(bits) > keep else bits.copy()
            return

        bits_pm = (bits.astype(np.int16) * 2) - 1

        # 与 Access Code 相关
        corr = np.correlate(bits_pm, self.ac_pm, "valid")
        cand = np.flatnonzero(corr >= self.ac_corr_threshold)
        self.stats["ota_cand_hit"] += len(cand)

        payload_list = []
        last_accept_start = -10**9

        for start in cand:
            hdr_start = start + 64
            payload_start = start + 96
            payload_end = payload_start + OTA_PAYLOAD_LEN * 8

            if payload_end > len(bits):
                break

            # 防止历史缓存中的旧包重复处理
            if payload_end <= old_hist_len:
                continue

            # 防止同一包附近重复触发
            if start - last_accept_start < self.min_sep_bits:
                continue

            hdr_err = int(np.count_nonzero(bits[hdr_start:hdr_start + 32] ^ self.hdr_bits))
            if hdr_err > self.hdr_max_bit_errors:
                continue

            self.stats["header_hit"] += 1

            payload_bits = bits[payload_start:payload_end]
            payload_bytes = np.packbits(
                payload_bits,
                bitorder=self.pack_bitorder
            ).tobytes()

            payload_list.append(payload_bytes)
            self.stats["ota_accept"] += 1
            last_accept_start = start

        if payload_list:
            self.payload_buf.extend(b"".join(payload_list))

        keep = self.ota_frame_bits - 1
        self.hist_bits = bits[-keep:].copy() if len(bits) > keep else bits.copy()

    def _process_protocol(self):
        """
        在 payload_buf 中寻找 RoboMaster 串口协议帧：

        frame_header:
            SOF: 1B, 固定 0xA5
            data_length: 2B, little endian
            seq: 1B
            CRC8: 1B

        cmd_id:
            2B, little endian

        data:
            data_length bytes

        frame_tail:
            CRC16, 2B, little endian
        """
        buf = self.payload_buf
        n = len(buf)

        if n == 0:
            return

        scan = 0
        keep_from = n

        while True:
            sof = buf.find(bytes([SOF]), scan)

            if sof < 0 or n - sof < 5:
                keep_from = n if sof < 0 else sof
                break

            data_len = buf[sof + 1] | (buf[sof + 2] << 8)

            if data_len > self.max_data_len:
                self.stats["len_fail"] += 1
                scan = sof + 1
                continue

            total_len = 5 + 2 + data_len + 2

            if n - sof < total_len:
                keep_from = sof
                break

            frame = bytes(buf[sof: sof + total_len])

            # 帧头 CRC8
            crc8_ok = (frame[4] == crc8_rm(frame[:4]))
            if not crc8_ok:
                self.stats["crc8_fail"] += 1

            # 整包 CRC16
            recv_crc16 = frame[-2] | (frame[-1] << 8)
            calc_crc16 = crc16_rm(frame[:-2])

            if recv_crc16 != calc_crc16:
                self.stats["crc16_fail"] += 1
                scan = sof + 1
                continue

            cmd_id = frame[5] | (frame[6] << 8)
            payload = frame[7:-2]

            # cmd_id、长度、模式过滤
            if (
                cmd_id not in EXPECTED_LEN
                or len(payload) != EXPECTED_LEN[cmd_id]
                or cmd_id not in self.allowed_cmds
            ):
                self.stats["cmd_drop"] += 1

                if cmd_id not in EXPECTED_LEN:
                    scan = sof + 1
                else:
                    scan = sof + total_len

                continue

            # 干扰波密钥要求 ASCII 字母或数字
            if (
                cmd_id == CMD_0A06
                and self.require_0a06_ascii
                and not is_ascii_alnum_payload(payload)
            ):
                self.stats["key_ascii_fail"] += 1
                scan = sof + 1
                continue

            # CRC8 不通过时是否允许软通过
            if not crc8_ok and not self.allow_soft_crc8:
                self.stats["crc8_drop"] += 1
                scan = sof + total_len
                continue

            seq = frame[3]

            if self.last_seq_global is None:
                dseq_global = 0
            else:
                dseq_global = (seq - self.last_seq_global) & 0xFF

            if cmd_id not in self.last_seq_by_cmd:
                dseq_cmd = 0
            else:
                dseq_cmd = (seq - self.last_seq_by_cmd[cmd_id]) & 0xFF

            self.last_seq_global = seq
            self.last_seq_by_cmd[cmd_id] = seq

            unique = self._is_unique_cmd_seq(cmd_id, seq)
            if not unique:
                self.stats["dup_drop"] += 1

            text = self._decode_payload_text(cmd_id, payload)

            if crc8_ok:
                kind = "hard"
                tag = "HARD"
                self.stats["hard_ok"] += 1
            else:
                if self._soft_is_stable(cmd_id, payload):
                    kind = "soft_stable"
                    tag = "SOFT_STABLE"
                    self.stats["soft_stable_ok"] += 1
                else:
                    kind = "soft"
                    tag = "SOFT"
                    self.stats["soft_ok"] += 1

            self._record_event(cmd_id, kind, unique)

            if not self.only_stats and unique:
                if kind != "soft" or self.show_soft:
                    self._emit_log(
                        f"[RX OK {tag}] "
                        f"seq={seq:03d} "
                        f"cmd=0x{cmd_id:04X} "
                        f"dseq_global={dseq_global} "
                        f"dseq_cmd={dseq_cmd} "
                        f"| {text}"
                    )

            scan = sof + total_len

        if keep_from >= n:
            del buf[:]
        elif keep_from > 0:
            del buf[:keep_from]

    # ========================================================
    # GNU Radio 数据流处理入口
    # ========================================================
    def general_work(self, input_items, output_items):
        inp = input_items[0]
        n_input = len(inp)

        if n_input > 0:
            msg_bytes = inp.tobytes()

            self._process_air_bytes(msg_bytes)
            self._process_protocol()
            self._print_stats()

        self.consume(0, n_input)
        return 0
