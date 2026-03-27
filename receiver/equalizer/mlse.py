import numpy as np
from .channel_estimator import ChannelEstimator

class MLSEEqualizer:
    def __init__(self, modulation_params, channel_model):
        self.sps = modulation_params.get("sps", 4)
        self.channel_model = channel_model
        self.estimator = ChannelEstimator(modulation_params)

    def process_eq(self, rx_signal, tx_signal):
        
        samples_per_burst = 156 * self.sps
        num_bursts = len(rx_signal) // samples_per_burst

        rhh_list = []
        if self.channel_model == "awgn":
            h_est = self.estimator.h_awgn()

        eq_signal = []
        for b in range(num_bursts):
            start_idx = b * samples_per_burst
            end_idx = (b + 1) * samples_per_burst
    
            tx_burst = tx_signal[start_idx : end_idx]
            rx_burst = rx_signal[start_idx  : end_idx]

            if self.channel_model != "awgn":
                h_est = self.estimator.h_rayleigh(tx_burst, rx_burst)

            burst_match = np.convolve(rx_burst, np.conj(h_est[::-1]))
            burst_trunc = burst_match[int(h_est.size / 2): - int(h_est.size / 2) + 1]
            eq_signal.append(burst_trunc)

            n = np.arange(h_est.size)
            # h_complex = h_est * (1j**(n / self.sps))
            h_complex = h_est

            rhh_full = np.convolve(h_complex, np.conj(h_complex[::-1]))
            center_idx = h_complex.size - 1
            rhh = rhh_full[center_idx :: self.sps]
            rhh_list.append(rhh)

        return np.concatenate(eq_signal), rhh_list