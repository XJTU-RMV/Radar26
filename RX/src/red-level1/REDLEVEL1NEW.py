#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Not titled yet
# GNU Radio version: 3.10.12.0

from PyQt5 import Qt
from gnuradio import qtgui
from gnuradio import analog
import math
from gnuradio import blocks
from gnuradio import digital
from gnuradio import filter
from gnuradio.filter import firdes
from gnuradio import gr
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import iio
import REDLEVEL1NEW_epy_block_1_0 as epy_block_1_0  # embedded python block
import threading



class REDLEVEL1NEW(gr.top_block, Qt.QWidget):

    def __init__(self, uri='ip:192.168.2.1'):
        gr.top_block.__init__(self, "Not titled yet", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Not titled yet")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except BaseException as exc:
            print(f"Qt GUI: Could not set Icon: {str(exc)}", file=sys.stderr)
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("gnuradio/flowgraphs", "REDLEVEL1NEW")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)
        self.flowgraph_started = threading.Event()

        ##################################################
        # Parameters
        ##################################################
        self.uri = uri

        ##################################################
        # Variables
        ##################################################
        self.sps = sps = 47
        self.samp_rate = samp_rate = 1000000
        self.symbol_rate = symbol_rate =  samp_rate / sps
        self.span = span = 11
        self.nfilts = nfilts = 32
        self.center_freq_0 = center_freq_0 = 433200000
        self.binary_const = binary_const = digital.constellation_calcdist([-1+0j, 1+0j], [ 0,1],
        2, 1, digital.constellation.AMPLITUDE_NORMALIZATION).base()
        self.binary_const.set_npwr(1.0)
        self.baud_rate = baud_rate = symbol_rate
        self.alpha = alpha = 0.25
        self.Length = Length = 8000

        ##################################################
        # Blocks
        ##################################################

        self.iio_pluto_source_0_0 = iio.fmcomms2_source_fc32(uri if uri else iio.get_pluto_uri(), [True, True], 32768)
        self.iio_pluto_source_0_0.set_len_tag_key('packet_len')
        self.iio_pluto_source_0_0.set_frequency(432200000)
        self.iio_pluto_source_0_0.set_samplerate(samp_rate)
        self.iio_pluto_source_0_0.set_gain_mode(0, 'fast_attack')
        self.iio_pluto_source_0_0.set_gain(0, 30)
        self.iio_pluto_source_0_0.set_quadrature(True)
        self.iio_pluto_source_0_0.set_rfdc(True)
        self.iio_pluto_source_0_0.set_bbdc(True)
        self.iio_pluto_source_0_0.set_filter_params('Auto', '', 0, 0)
        self.freq_xlating_fir_filter_xxx_1 = filter.freq_xlating_fir_filter_ccc(1, firdes.low_pass(1.0, 1000000, 470e3, 20e3), 0, samp_rate)
        self.filter_fft_low_pass_filter_0_0 = filter.fft_filter_fff(1, firdes.low_pass(1, samp_rate, symbol_rate, 2000, window.WIN_BLACKMAN, 6.76), 1)
        self.epy_block_1_0 = epy_block_1_0.blk(mode='jamming', input_format='packed', bit_order='msb', show_soft=True, allow_soft_crc8=True, soft_repeat=3, ac_min_match_bits=60, hdr_max_bit_errors=2, max_data_len=16, stats_interval=1.0, rate_window=1.0, only_stats=False, dedup_ttl=5.0, min_sep_bits=216, require_0a06_ascii=True, enable_console_print=True)
        self.digital_symbol_sync_xx_0 = digital.symbol_sync_ff(
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
            firdes.root_raised_cosine(32, 32, 1.0, 0.25, 11*8*32))
        self.digital_binary_slicer_fb_0 = digital.binary_slicer_fb()
        self.blocks_unpacked_to_packed_xx_0_0 = blocks.unpacked_to_packed_bb(1, gr.GR_MSB_FIRST)
        self.analog_quadrature_demod_cf_0 = analog.quadrature_demod_cf((1/2.8194))


        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_quadrature_demod_cf_0, 0), (self.filter_fft_low_pass_filter_0_0, 0))
        self.connect((self.blocks_unpacked_to_packed_xx_0_0, 0), (self.epy_block_1_0, 0))
        self.connect((self.digital_binary_slicer_fb_0, 0), (self.blocks_unpacked_to_packed_xx_0_0, 0))
        self.connect((self.digital_symbol_sync_xx_0, 0), (self.digital_binary_slicer_fb_0, 0))
        self.connect((self.filter_fft_low_pass_filter_0_0, 0), (self.digital_symbol_sync_xx_0, 0))
        self.connect((self.freq_xlating_fir_filter_xxx_1, 0), (self.analog_quadrature_demod_cf_0, 0))
        self.connect((self.iio_pluto_source_0_0, 0), (self.freq_xlating_fir_filter_xxx_1, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("gnuradio/flowgraphs", "REDLEVEL1NEW")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_uri(self):
        return self.uri

    def set_uri(self, uri):
        self.uri = uri

    def get_sps(self):
        return self.sps

    def set_sps(self, sps):
        self.sps = sps
        self.set_symbol_rate( self.samp_rate / self.sps)
        self.digital_symbol_sync_xx_0.set_sps(self.sps)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_symbol_rate( self.samp_rate / self.sps)
        self.filter_fft_low_pass_filter_0_0.set_taps(firdes.low_pass(1, self.samp_rate, self.symbol_rate, 2000, window.WIN_BLACKMAN, 6.76))
        self.iio_pluto_source_0_0.set_samplerate(self.samp_rate)

    def get_symbol_rate(self):
        return self.symbol_rate

    def set_symbol_rate(self, symbol_rate):
        self.symbol_rate = symbol_rate
        self.set_baud_rate(self.symbol_rate)
        self.filter_fft_low_pass_filter_0_0.set_taps(firdes.low_pass(1, self.samp_rate, self.symbol_rate, 2000, window.WIN_BLACKMAN, 6.76))

    def get_span(self):
        return self.span

    def set_span(self, span):
        self.span = span

    def get_nfilts(self):
        return self.nfilts

    def set_nfilts(self, nfilts):
        self.nfilts = nfilts

    def get_center_freq_0(self):
        return self.center_freq_0

    def set_center_freq_0(self, center_freq_0):
        self.center_freq_0 = center_freq_0

    def get_binary_const(self):
        return self.binary_const

    def set_binary_const(self, binary_const):
        self.binary_const = binary_const

    def get_baud_rate(self):
        return self.baud_rate

    def set_baud_rate(self, baud_rate):
        self.baud_rate = baud_rate

    def get_alpha(self):
        return self.alpha

    def set_alpha(self, alpha):
        self.alpha = alpha

    def get_Length(self):
        return self.Length

    def set_Length(self, Length):
        self.Length = Length



def argument_parser():
    parser = ArgumentParser()
    parser.add_argument(
        "--uri", dest="uri", type=str, default='ip:192.168.2.1',
        help="Set URI [default=%(default)r]")
    return parser


def main(top_block_cls=REDLEVEL1NEW, options=None):
    if options is None:
        options = argument_parser().parse_args()

    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls(uri=options.uri)

    tb.start()
    tb.flowgraph_started.set()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
