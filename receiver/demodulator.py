import numpy as np
import sys
from core.block import Block


class Demodulation(Block):
    def __init__(self, scheme):

        if scheme in ["TCHFS", "CS1", "MCS1"]:

            self.demodulator = GMSKDemodulator()

        elif scheme == "MCS5":

            self.demodulator = PSKDemodulator()

        else:

            raise ValueError("Unknown scheme")

    def process(self, signal):

        return self.demodulator.process(signal)


class GMSKDemodulator(Block):
    def __init__(self):
        self.sps = 100

    def process(self, complex_signal):

        sample_indices = np.arange(148) * self.sps + int(self.sps / 2)
        y_k = complex_signal[sample_indices]

        y_k_prev = np.zeros(y_k.size, dtype=complex)
        y_k_prev[1:] = y_k[:-1]
        y_k_prev[0] = 1 + 0j

        delta_phi = np.angle(y_k * np.conj(y_k_prev))

        alpha = np.ones(delta_phi.size)
        alpha[delta_phi <= 0] = -1

        d_curr = (1 - alpha) / 2

        bits = np.zeros(148, dtype=int)
        d_prev = 1
        for i in range(148):
            bits[i] = d_curr[i] ^ d_prev
            d_prev = bits[i]

        return bits


class PSKDemodulator(Block):
    def __init__(self):
        pass

    def process(self, signal):
        raise ValueError("8-PSK Demodulator еще не реализован")
