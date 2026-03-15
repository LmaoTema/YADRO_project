
import numpy as np
from core.block import Block


class RayleighSinglePathChannel(Block):
    
    def __init__(self, maximum_doppler_shift=0, sample_rate=1e6):

        self.fd = maximum_doppler_shift
        self.fs = sample_rate

    def reset(self):

        self.t = 0

    def _generate_fading(self, N):

        # Rayleigh fading
        h = (np.random.randn(N) + 1j * np.random.randn(N)) / np.sqrt(2)

        # Доплер эффект
        if self.fd > 0:

            t = (np.arange(N) + self.t) / self.fs

            doppler = np.exp(1j * 2 * np.pi * self.fd * t)

            h *= doppler

        self.t += N

        return h

    def process(self, x):

        x = np.asarray(x)

        N = len(x)

        h = self._generate_fading(N)

        y = h * x

        return y