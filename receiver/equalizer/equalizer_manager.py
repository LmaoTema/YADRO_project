import numpy as np
from core.block import Block
from .zero_force import ZFEqualizer
from .mlse import MLSEEqualizer

class Equalizer(Block):

    def __init__(self, equalizer_params, modulation_params, is_working=True):
        super().__init__(is_working)

        eq_type = equalizer_params.get("equalizer_type", "ZF")
        channel_model = equalizer_params.get("channel_model", "awgn")

        if eq_type == "ZF":
            self.equalizer = ZFEqualizer(modulation_params, channel_model)
        elif eq_type == "DFE":
            self.equalizer = DFEEqualizer(modulation_params, channel_model)
        elif eq_type == "MLSE":
            self.equalizer = MLSEEqualizer(modulation_params, channel_model)
    
    def _process(self, rx_signal, tx_signal):

        return self.equalizer.process_eq(rx_signal, tx_signal)