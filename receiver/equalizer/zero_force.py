import numpy as np
from core.block import Block
from receiver.equalizer.channel_estimator import ChannelEstimator


class ZFEqualizer(Block):

    def __init__(self, modulation_params, is_working=True):
        self.sps = modulation_params.get("sps", 4)
        self.estimator = ChannelEstimator(modulation_params)

    def equalize(self, rx, h):

        H = np.fft.fft(h, len(rx))
        R = np.fft.fft(rx)
        
        S = R / (H + 1e-8)

        s = np.fft.ifft(S)

        return s

    def process_eq(self, rx_signal, tx_signal):
        
        samples_per_burst = 156 * self.sps
        num_bursts = len(rx_signal) // samples_per_burst

        eq_signal = []
        for b in range(num_bursts):
            start_idx = b * samples_per_burst
            end_idx = (b + 1) * samples_per_burst
    
            tx_burst = tx_signal[start_idx : end_idx]
            rx_burst = rx_signal[start_idx  : end_idx]

            h_est = self.estimator.estimate(tx_burst, rx_burst)

            eq_burst= self.equalize(rx_burst, h_est)
            eq_signal.append(eq_burst)

        return np.concatenate(eq_signal)