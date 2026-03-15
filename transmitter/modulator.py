import numpy as np
from core.block import Block


class Modulation(Block):

    def __init__(self, scheme, params, is_working=False):
        super().__init__(is_working)

        if scheme in ["TCHFS", "CS1", "MCS1"]:

            self.modulator = GMSKModulation(params)

        elif scheme == "MCS5":

            self.modulator = PSKModulation(params)

        else:

            raise ValueError("Unknown scheme")

    def _process(self, bits):

        return self.modulator.process(bits)


class GMSKModulation:

    def __init__(self, params):
        self.BT = params.get("BT", 0.3)
        self.T = params.get("T", 1)
        self.sps = params.get("sps", 100)
        self.dt = self.T / self.sps
        self.h = params.get("h", 0.5)
        self.gaus_duration = params.get("gaus_duration", 4)
        self.rect_duration = params.get("rect_duration", 1)

        return

    def differential_encoding(self, bits):
        if bits.size % 148 != 0:
            raise ValueError("Количество модуляционных бит должно быть кратным 148")

        d_prev = np.ones(bits.size, dtype=int)
        d_prev[1:] = bits[:-1]

        d_curr = bits ^ d_prev
        alpha = 1 - 2 * d_curr

        return alpha

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

    def calc_phase(self, alpha, g_t):
        h = self.h
        dt = self.dt
        sps = self.sps
        gaus_duration = self.gaus_duration
        rect_duration = self.rect_duration

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
        # an additional shift of 0.5 need to move to the center of the bit 
        shift = (gaus_duration + rect_duration) / 2 - 0.5
        phi = phi[int(shift * sps) : int(shift * sps) + alpha_repeat.size]

        return phi

    def calc_signal(self, phi):
        dt = self.dt

        t = np.arange(phi.size) * dt
        x_t = np.exp(1j * phi)

        return x_t

    def process(self, bits):
        
        if not getattr(self, "is_working", True):
             return np.array(bits, dtype=complex)
        
        active_size = 148
        num_bursts = len(bits) // active_size
    
        g_t = self.gmsk_filter()
        
        all_signals = []
        guard_period = np.zeros(8 * self.sps, dtype=complex)
        for i in range(num_bursts):
            burst = bits[i*active_size : (i+1)*active_size]
            alpha = self.differential_encoding(burst)
            
            phi = self.calc_phase(alpha, g_t)
            signal = self.calc_signal(phi)
            
            all_signals.append(signal)
            
            all_signals.append(guard_period)

        

<<<<<<< HEAD
        signal = self.calc_signal(phi)
        #bits = np.array(bits)
        #signal = 2*bits - 1
        
        return signal
=======
        return np.concatenate(all_signals)
>>>>>>> c50fdd552be25890ad129d146fcb673215b6d8eb


class PSKModulation:
    def __init__(self, params):
        raise ValueError("Еще не реализован")
