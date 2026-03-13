import numpy as np
import sys
from core.block import Block


class Demodulation(Block):

    def __init__(self, scheme, params, is_working=True):
        super().__init__(is_working)

        if scheme in ["TCHFS", "CS1", "MCS1"]:

            self.demodulator = GMSKDemodulator(params)

        elif scheme == "MCS5":

            self.demodulator = PSKDemodulator(params)

        else:

            raise ValueError("Unknown scheme")

    def _process(self, signal):

        return self.demodulator.process(signal)


class GMSKDemodulator(Block):
    def __init__(self, params):
        self.BT = params.get("BT", 0.3)
        self.T = params.get("T", 1)
        self.sps = params.get("sps", 100)
        self.dt = self.T / self.sps
        self.gaus_duration = params.get("gaus_duration", 4)
        self.rect_duration = params.get("rect_duration", 1)
        self.type_demod = params.get("type_demod", "diff_phase")


    def process(self, complex_signal, params):
        
        if not getattr(self, "is_working", True):
            return np.array(complex_signal, copy=True)
        
        type_demod = self.type_demod
        
        if type_demod == "diff_phase":

            sample_indices = np.arange(148) * self.sps + int(self.sps / 2)
            y_k = complex_signal[sample_indices]

            y_k_prev = np.zeros(y_k.size, dtype=complex)
            y_k_prev[1:] = y_k[:-1]
            y_k_prev[0] = 1 + 0j

            delta_phi = np.angle(y_k * np.conj(y_k_prev))

            alpha = np.ones(delta_phi.size)
            alpha[delta_phi <= 0] = -1

            d_curr = ((1 - alpha) / 2).astype(int)

            bits = np.zeros(148, dtype=int)
            d_prev = 1
            for i in range(148):
                bits[i] = d_curr[i] ^ d_prev
                d_prev = bits[i]

        elif type_demod == "vit_soft":

            T = self.T
            BT = self.BT
            dt = self.dt
            sps = self.sps
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

            rhh_full = np.convolve(g_t, g_t[::-1]) * dt
            center_idx = int(rhh_full.size/2)

            rhh = np.zeros(5, dtype=complex)
            for k in range(5):
                rhh[k] = rhh_full[center_idx + k * sps]

            rhh /= rhh[0].real

            increment = np.zeros(8)
            increment[0] = -rhh[1].imag() - rhh[2].real() - rhh[3].imag() + rhh[4].real()
            increment[1] = rhh[1].imag() - rhh[2].real() - rhh[3].imag() + rhh[4].real()
            increment[2] = -rhh[1].imag() + rhh[2].real() - rhh[3].imag() + rhh[4].real()
            increment[3] = rhh[1].imag() + rhh[2].real() - rhh[3].imag() + rhh[4].real()
            increment[4] = -rhh[1].imag() - rhh[2].real() + rhh[3].imag() + rhh[4].real()
            increment[5] = rhh[1].imag() - rhh[2].real() + rhh[3].imag() + rhh[4].real()
            increment[6] = -rhh[1].imag() + rhh[2].real() + rhh[3].imag() + rhh[4].real()
            increment[7] = rhh[1].imag() + rhh[2].real() + rhh[3].imag() + rhh[4].real()

            path_metrics = np.ones(16) * -1e30
            path_metrics[0] = 0.0
            trans_table = np.zeros((148, 16))

            sample_nr = 0
            old_path_metrics = path_metrics1
            new_path_metrics = path_metrics2

            bits = 0

        return bits




class PSKDemodulator(Block):
    def __init__(self, params):
        pass

    def process(self, signal):
        raise ValueError("8-PSK Demodulator еще не реализован")
