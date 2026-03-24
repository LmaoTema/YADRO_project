import numpy as np
class AWGNChannel():


    def __init__(self, snr_db = 20, code_rate = 1.0, bits_per_symbol = 1, burst_eff = 1.0):
        
        self.snr_db = snr_db
        self.code_rate = code_rate
        self.bits_per_symbol = bits_per_symbol
        self.burst_eff = burst_eff

    def process(self, x):
        x = np.asarray(x, dtype = complex)

        # Средняя мощность сигнала
        Ps = np.mean(np.abs(x)**2)
        Pb = Ps / self.bits_per_symbol                  # мощность на бит
        eff_rate = self.code_rate * self.burst_eff      # мощность на декодируемый бит
        Pbd = Pb / eff_rate
        
        # SNR → линейная шкала
        snr_linear = 10 ** (self.snr_db / 10)   
        # Дисперсия шума
        noise_var = Pbd / snr_linear
        
        # Шум
        noise = np.sqrt(noise_var / 2) * (np.random.randn(*x.shape) + 1j * np.random.randn(*x.shape))

        return x + noise