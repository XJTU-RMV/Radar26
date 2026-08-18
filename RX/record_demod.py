from __future__ import annotations

import argparse
from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from RX.protocol import format_message_line
from RX.runtime import RadarAirParser, get_flowgraph_spec


DEFAULT_RECORD_PATH = Path(__file__).resolve().parent / "record" / "01"


class RecordedFlowgraph:
    def __init__(
        self,
        record_path: Path,
        side: str,
        level: int | str,
    ):
        try:
            from gnuradio import analog, blocks, digital, filter, gr
            from gnuradio.fft import window
            from gnuradio.filter import firdes
            import pmt
        except ImportError as exc:
            raise RuntimeError("GNU Radio is required to demodulate recorded IQ files") from exc

        spec = get_flowgraph_spec(side, level)

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

        self.tb = gr.top_block(f"Recorded RX {spec.side} {spec.level}", catch_exceptions=True)
        source = blocks.file_source(gr.sizeof_gr_complex, str(record_path), False, 0, 0)
        source.set_begin_tag(pmt.PMT_NIL)
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
        self.parser = RadarAirParser(spec.mode, max_data_len=spec.max_data_len)
        self.sink = blocks.vector_sink_b()

        self.tb.connect((source, 0), (translating_filter, 0))
        self.tb.connect((translating_filter, 0), (quadrature_demod, 0))
        self.tb.connect((quadrature_demod, 0), (low_pass, 0))
        self.tb.connect((low_pass, 0), (symbol_sync, 0))
        self.tb.connect((symbol_sync, 0), (slicer, 0))
        self.tb.connect((slicer, 0), (packer, 0))
        self.tb.connect((packer, 0), (self.sink, 0))

    def run(self):
        self.tb.run()
        return self.parser.feed_air_bytes(bytes(self.sink.data()))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Demodulate a recorded GNU Radio complex64 IQ file.")
    parser.add_argument("--record", type=Path, default=DEFAULT_RECORD_PATH, help="recorded gr_complex IQ file")
    parser.add_argument("--side", choices=["red", "blue"], default="red")
    parser.add_argument("--level", choices=["base", "level1", "level2"], default="base")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    record_path = args.record.expanduser().resolve()
    if not record_path.is_file():
        raise FileNotFoundError(record_path)

    flowgraph = RecordedFlowgraph(
        record_path,
        args.side,
        args.level,
    )
    messages = flowgraph.run()
    for message in messages:
        print(format_message_line(message))
    print(f"decoded_messages={len(messages)}")


if __name__ == "__main__":
    main()
