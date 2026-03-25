import numpy as np
from .vit_detector_osmo import calc_increment_osmo, calc_metric_osmo, find_best_stop_state_osmo, traceback_osmo

class GMSKDetector:
    def __init__(self, params):
        self.BT = params.get("BT", 0.3)
        self.T = params.get("T", 1)
        self.sps = params.get("sps", 100)
        self.dt = self.T / self.sps
        self.gaus_duration = params.get("gaus_duration", 4)
        self.rect_duration = params.get("rect_duration", 1)
        self.type_demod = params.get("type_demod", "diff_phase")

    def gmsk_filter(self):
        BT = self.BT
        T = self.T
        dt = self.dt
        gaus_duration = self.gaus_duration
        rect_duration = self.rect_duration

        delta = np.sqrt(np.log(2)) / (2 * np.pi * BT)

        t_h = np.arange(-gaus_duration / 2 * T, gaus_duration / 2 * T, dt)
        t_rect = np.arange(-rect_duration / 2 * T, rect_duration / 2 * T, dt)

        h_t = np.exp(-(t_h**2) / (2 * (delta**2) * (T**2))) / (
            np.sqrt(2 * np.pi) * delta * T
        )
        rect = np.ones(t_rect.size) / T

        g_t = np.convolve(h_t, rect) * dt

        return g_t

    def calc_rhh(self, g_t):
        # In general, rhh should be defined in the TSC
        dt = self.dt
        sps = self.sps
        gaus_duration = self.gaus_duration
        rect_duration = self.rect_duration

        rhh_full = np.convolve(g_t, g_t[::-1]) * dt
        center_idx = int(rhh_full.size / 2)

        rhh = np.zeros(5, dtype=complex)
        for k in range(5):
            rhh[k] = rhh_full[center_idx + k * sps]

        rhh /= rhh[0].real

        return rhh

    def diff_phase(self, burst_samples):
        y_k = burst_samples[self.sps - 1 :: self.sps]

        y_k_prev = np.zeros(y_k.size, dtype=complex)
        y_k_prev[1:] = y_k[:-1]
        y_k_prev[0] = 1 + 0j

        delta_phi = np.angle(y_k * np.conj(y_k_prev))

        alpha = np.ones(delta_phi.size)
        alpha[delta_phi <= 0] = -1

        d_curr = ((1 - alpha) / 2).astype(int)

        burst_bits = np.zeros(d_curr.size, dtype=int)
        d_prev = 1
        for i in range(d_curr.size):
            burst_bits[i] = d_curr[i] ^ d_prev
            d_prev = burst_bits[i]

        return burst_bits

    def process_detect(self, complex_signal):

        sps = self.sps
        samples_per_burst = 156 * sps
        num_bursts = len(complex_signal) // samples_per_burst
    
        all_bits = []

        if self.type_demod in ["vit_soft", "vit_hard"]:
            g_t = self.gmsk_filter()
            rhh = self.calc_rhh(g_t)
            increment = calc_increment_osmo(rhh)

        for b in range(num_bursts):
            start_idx = b * samples_per_burst
            burst_samples = complex_signal[start_idx : start_idx + 148 * sps]

            if self.type_demod == "diff_phase":
                burst_bits = self.diff_phase(burst_samples)
                all_bits.append(burst_bits)

            elif self.type_demod in ["vit_soft", "vit_hard"]:
                sampled_signal = burst_samples[self.sps - 1 :: self.sps]
                trans_table, old_path_metrics, real_imag = calc_metric_osmo(increment, sampled_signal, start_state=0)

                best_stop_state = find_best_stop_state_osmo(old_path_metrics)

                burst_bits = traceback_osmo(trans_table, best_stop_state, real_imag, self.type_demod)

                all_bits.append(burst_bits)
                
        bits = np.concatenate(all_bits)

        return bits