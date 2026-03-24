import numpy as np
from transmitter.modulator import Modulation


class ChannelEstimator:

    def __init__(self, modulation_params, train_start=61, train_end=87):
        self.sps = modulation_params.get("sps", 4)
        self.train_start = train_start * self.sps
        self.train_end = train_end * self.sps

        gaus_duration = modulation_params.get("gaus_duration", 4)
        rect_duration = modulation_params.get("rect_duration", 1)
        self.L = (gaus_duration + rect_duration) * self.sps

    def estimate(self, tx_burst, rx_burst):

        tx_train = tx_burst[self.train_start : self.train_end]
        rx_train = rx_burst[self.train_start : self.train_end]

        N = len(tx_train)
        X = np.zeros((N - self.L, self.L), dtype=complex)

        for i in range(N - self.L):
            X[i] = tx_train[i:i + self.L]

        y = rx_train[self.L:]

        h = np.linalg.lstsq(X, y, rcond=None)[0]

        return h