import numpy as np
from core.block import Block


class Modulation(Block):
    def __init__(self, scheme):

        if scheme in ["TCHFS", "CS1", "MCS1"]:

            self.modulator = GMSKModulation()

        elif scheme == "MCS5":

            self.modulator = PSKModulation()

        else:

            raise ValueError("Unknown scheme")

    def process(self, bits):

        return self.modulator.process(bits)


class GMSKModulation:

    def __init__(self):
        self.BT = 0.3
        self.T = 1
        self.sps = 100
        self.dt = self.T / self.sps
        self.h = 1 / 2

        return

    def differential_encoding(self, bits):
        # if bits.size % 148 != 0:
        #     raise ValueError("Количество модуляционных бит должно быть кратным 148")

        d_prev = np.ones(bits.size, dtype=int)
        d_prev[1:] = bits[:-1]

        d_curr = bits ^ d_prev
        alpha = 1 - 2 * d_curr

        return alpha

    def gmsk_filter(self):
        BT = self.BT
        T = self.T
        dt = self.dt

        delta = np.sqrt(np.log(2)) / (2 * np.pi * BT)

        t_h = np.arange(-1.5 * T, 1.5 * T, dt)
        t_rect = np.arange(-0.5 * T, 0.5 * T, dt)

        h_t = np.exp(-(t_h**2) / (2 * (delta**2) * (T**2))) / (
            np.sqrt(2 * np.pi) * delta * T
        )
        rect = t_rect * 0 + 1 / T

        g_t = np.convolve(h_t, rect) * dt

        return g_t

    def calc_phase(self, alpha, g_t):
        h = self.h
        dt = self.dt
        sps = self.sps

        alpha_repeat = np.repeat(alpha, sps)

        q_gmsk = np.cumsum(g_t) * dt

        num_bits = alpha.size
        phi = np.zeros(num_bits * sps + q_gmsk.size)

        #  phase accumulation
        for i in range(num_bits):
            alpha_i = alpha[i]
            start_idx = i * sps

            phi[start_idx : start_idx + q_gmsk.size] += alpha_i * np.pi * h * q_gmsk

            phase_step = alpha_i * np.pi * h
            phi[start_idx + q_gmsk.size :] += phase_step

        # shift to synchronization with the modulation symbol changes
        phi = phi[int(1.5 * sps) : int(1.5 * sps) + alpha_repeat.size]

        return phi

    def calc_signal(self, phi):
        dt = self.dt

        t = np.arange(phi.size) * dt
        x_t = np.exp(1j * phi)

        return x_t

    def process(self, bits):

        alpha = self.differential_encoding(bits)

        g_t = self.gmsk_filter()

        phi = self.calc_phase(alpha, g_t)

        signal = self.calc_signal(phi)

        return signal


class PSKModulation:
    def __init__(self):
        raise ValueError("Еще не реализован")
