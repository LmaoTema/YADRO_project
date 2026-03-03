import numpy as np
import matplotlib.pyplot as plt
import sys


class Modulation:
    def __init__(self, params):
        self.BT = params.get("BT", 0.3)
        self.T = params.get("T", 1 / 20**6)
        self.sps = params.get("sps", 100)
        self.dt = self.T / self.sps
        self.f_0 = params.get("f_0", 1710.2 * 10**6)
        self.Ec = params.get("Ec", self.T / 2)
        self.phi_0 = params.get("phi_0", 0)

        self.bits = params["bits"]

        return

    def gmsk_modulation(self):
        alpha = self.differential_encoding(self.bits)

        g_t = self.gmsk_filter()

        is_plot_phase = True
        phi = self.calc_phase(alpha, g_t, is_plot_phase)

        is_plot_signal = True
        signal = self.calc_signal(phi, is_plot_signal)

        return

    def psk_modulation(self):
        return

    # help method
    def differential_encoding(self, bits):
        if bits.size % 148 != 0:
            print("Количество модуляционных бит должно быть кратным 148")
            sys.exit()

        d_prev = np.ones(bits.size)
        d_prev[1:] = bits[:-1]

        d_curr = (bits + d_prev) % 2
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

    def calc_phase(self, alpha, g_t, is_plot):
        h = 0.5
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

        if is_plot:
            t = np.arange(alpha_repeat.size) * dt
            wind = sps * 10
            self.plot_2_1(
                "Bits",
                "Phase",
                t[:wind] / self.T,
                t[:wind] / self.T,
                alpha_repeat[:wind],
                phi[:wind],
            )

        return phi

    def calc_signal(self, phi, is_plot):
        dt = self.dt
        Ec = self.Ec
        T = self.T
        f_0 = self.f_0
        phi_0 = self.phi_0

        t = np.arange(phi.size) * dt
        amplitude = np.sqrt(2 * Ec / T)
        x_t = amplitude * np.cos(2 * np.pi * f_0 * t + phi + phi_0)

        if is_plot:
            # take another frequency
            x_plot = amplitude * np.cos(2 * np.pi * 1 / T * t + phi + phi_0)

            wind = 10 * self.sps
            self.plot_1("Signal", t[:wind] / T, x_plot[:wind])

        return x_t

    def plot_1(self, name, range_x, range_y, x="", y=""):
        plt.figure()

        plt.plot(range_x, range_y, lw=3)
        plt.title(name, fontsize=20)
        plt.xlabel(x)
        plt.ylabel(y)
        plt.grid()

        plt.show()

        return

    def plot_2_1(
        self,
        name1,
        name2,
        range_x1,
        range_x2,
        range_y1,
        range_y2,
        x1="",
        x2="",
        y1="",
        y2="",
    ):
        fig = plt.figure()
        ax1 = fig.add_subplot(2, 1, 1)
        ax2 = fig.add_subplot(2, 1, 2)

        ax1.plot(range_x1, range_y1, lw=3)
        ax1.set_title(name1, fontsize=20)
        ax1.set_xlabel(x1)
        ax1.set_ylabel(y1)
        ax1.grid()

        ax2.plot(range_x2, range_y2, c="r", lw=3)
        ax2.set_title(name2, fontsize=20)
        ax2.set_xlabel(x2)
        ax2.set_ylabel(y2)
        ax2.grid()

        fig.subplots_adjust(hspace=0.5)
        plt.show()
        return


bits = np.random.randint(0, 2, 148)
params = {"bits": bits}
mod = Modulation(params)

mod.gmsk_modulation()
