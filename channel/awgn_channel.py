import numpy as np
from core.block import Block


class AWGNChannel(Block):


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

        # мощность шума
        noise_power = signal_power / snr_linear

        # шум
        noise = np.sqrt(noise_power / 2) * (np.random.randn(*x.shape) + 1j * np.random.randn(*x.shape))

        return x + noise