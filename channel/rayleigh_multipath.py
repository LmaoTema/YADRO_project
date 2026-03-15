
import numpy as np
from core.block import Block
from channel.pdp_profiles import CHANNEL_PROFILES


class RayleighMultipathChannel(Block):

    def __init__(
        self,
        sample_rate,
        snr_db,
        profile="TU",
        maximum_doppler_shift=100,
        filter_length=21
    ):

        self.fs = sample_rate
        self.snr_db = snr_db
        self.fd = maximum_doppler_shift
        self.L = filter_length

        pdp = CHANNEL_PROFILES[profile]

        self.delays = pdp["delays"]
        self.powers_db = pdp["powers_db"]

        powers = 10 ** (self.powers_db / 10)

        self.powers = powers / np.sum(powers)

        self.num_paths = len(self.delays)

        self._prepare_delays()

        self.reset()

    def _prepare_delays(self):

        delays_samples = self.delays * self.fs

        self.int_delays = np.floor(delays_samples).astype(int)

        self.frac_delays = delays_samples - self.int_delays

    def reset(self):
        self.t = 0

    def _fractional_delay_filter(self, mu):

        n = np.arange(-self.L//2, self.L//2 + 1)

        h = np.sinc(n - mu)

        window = np.hamming(len(h))

        h *= window

        h /= np.sum(h)

        return h

    def _apply_fractional_delay(self, x, mu):

        h = self._fractional_delay_filter(mu)

        return np.convolve(x, h, mode="full")

    def _generate_fading(self, N, power):

        sigma = np.sqrt(power / 2)

        h = sigma * (np.random.randn(N) + 1j * np.random.randn(N))

        return h

    def _add_awgn(self, x):

        signal_power = np.mean(np.abs(x)**2)

        snr_linear = 10 ** (self.snr_db / 10)

        noise_power = signal_power / snr_linear

        noise = np.sqrt(noise_power/2) * (np.random.randn(*x.shape) + 1j*np.random.randn(*x.shape))

        return x + noise

    def process(self, x):

        x = np.asarray(x)

        N = len(x)

        max_delay = np.max(self.int_delays) + self.L

        y = np.zeros(N + max_delay, dtype=np.complex128)

        for k in range(self.num_paths):

            int_delay = self.int_delays[k]

            frac_delay = self.frac_delays[k]

            delayed = self._apply_fractional_delay(x, frac_delay)

            fading = self._generate_fading(len(delayed), self.powers[k])

            faded = fading * delayed

            y[int_delay:int_delay + len(faded)] += faded

        y = y[:N]

        # добавление AWGN
        y = self._add_awgn(y)

        return y