import numpy as np
from core.block import Block


class ZFEqualizer(Block):

    def __init__(self, channel_len=5):
        super().__init__()

        self.L = channel_len

        self.train_start = 61
        self.train_end = 87

    def estimate_channel(self, rx_train, tx_train):

        N = len(tx_train)

        X = np.zeros((N - self.L, self.L), dtype=complex)

        for i in range(N - self.L):
            X[i] = tx_train[i:i + self.L]

        y = rx_train[self.L:]

        h = np.linalg.lstsq(X, y, rcond=None)[0]

        return h

    def equalize(self, rx, h):

        H = np.fft.fft(h, len(rx))
        R = np.fft.fft(rx)

        S = R / (H + 1e-8)

        s = np.fft.ifft(S)

        return s

    def process(self, burst):

        burst = np.array(burst)

        rx_train = burst[self.train_start:self.train_end]

        tx_train = np.ones(len(rx_train))

        h = self.estimate_channel(rx_train, tx_train)

        equalized = self.equalize(burst, h)

        return equalized
    
    print("Equalizer is working")