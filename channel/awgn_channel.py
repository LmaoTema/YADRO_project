import numpy as np
class AWGNChannel():


    def __init__(self, snr_db=20):
        
        self.snr_db = snr_db

    def reset(self):
        pass

    def process(self, x):

        x = np.asarray(x)

        # мощность сигнала
        signal_power = np.mean(np.abs(x) ** 2)

        # SNR → линейная шкала
        snr_linear = 10 ** (self.snr_db / 10)   
        R = 1/2
        # мощность шума
        noise_power = signal_power / (snr_linear * R * 50/53)
        #* R * 50/53
        # шум
        noise = np.sqrt(noise_power / 2) * (np.random.randn(*x.shape) + 1j * np.random.randn(*x.shape))

        return x + noise