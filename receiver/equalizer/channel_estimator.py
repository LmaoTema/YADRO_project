import numpy as np


class ChannelEstimator:

    def __init__(self, train_start=61, train_end=87, channel_len=5):
        self.train_start = train_start
        self.train_end = train_end
        self.L = channel_len
        self.tx_train = np.array([0,0,1,0,1,1,0,1,1,1,0,1,1,1,1,0,0,0,1,0,1,1,0,1,1,1])
    def estimate(self, burst):

        rx_train = burst[self.train_start:self.train_end]

        tx_train = self.tx_train

        N = len(tx_train)

        X = np.zeros((N - self.L, self.L), dtype=complex)

        for i in range(N - self.L):
            X[i] = tx_train[i:i + self.L]
        #print(X)
        y = rx_train[self.L:]

        h = np.linalg.lstsq(X, y, rcond=None)[0]

        return h