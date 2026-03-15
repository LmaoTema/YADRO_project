import numpy as np
from core.block import Block
from receiver.equalizer.channel_estimator import ChannelEstimator


class ZFEqualizer(Block):

    def __init__(self, channel_type, is_working=True):

        super().__init__(is_working)

        self.channel_type = channel_type

        self.estimator = ChannelEstimator()

    def equalize(self, rx, h):

        H = np.fft.fft(h, len(rx))
        R = np.fft.fft(rx)
        
        S = R / (H + 1e-8)

        s = np.fft.ifft(S)

        return s

    def _process(self, burst):

        if not self.is_working:
            return burst

        # если AWGN → эквализация не нужна
        if self.channel_type == "awgn":
            return burst

        burst = np.array(burst)

        # оценка канала
        h_est = self.estimator.estimate(burst)

        # эквализация
        burst_eq = self.equalize(burst, h_est)

        return burst_eq