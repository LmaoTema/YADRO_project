import numpy as np
from core.block import Block


class GSMChannel(Block):

    def __init__(self, profile, snr_db, fs=270833, ):


        self.delays = profile["delays"]
        self.powers_db = profile["powers_db"]

        self.fs = fs
        self.snr_db = snr_db

        # перевод в отсчеты
        self.delay_samples = (self.delays * fs).astype(int)

        # перевод из дБ
        self.powers = 10 ** (self.powers_db / 20)

    def _generate_impulse_response(self):

        # Кол-во лучей
        taps = len(self.powers)

        # Случайные коэффициенты затухания для каждого "пути"
        fading = (np.random.randn(taps) + 1j * np.random.randn(taps)) / np.sqrt(2)

        fading = fading * self.powers

        # Импульсная характеристика канала
        h = np.zeros(self.delay_samples.max() + 1, dtype=complex)

        for gain, delay in zip(fading, self.delay_samples):
            h[delay] += gain

        return h

    def _add_awgn(self, signal):

        signal_power = np.mean(np.abs(signal) ** 2)

        snr_linear = 10 ** (self.snr_db / 10)

        noise_power = signal_power / snr_linear

        noise = np.sqrt(noise_power / 2) * (np.random.randn(len(signal)) +1j * np.random.randn(len(signal)))

        return signal + noise

    def process(self, signal):


        # Генерируем импульсную характеристику канала
       # h = self._generate_impulse_response()

        # Суммируем все отраженные лучи (используем свертку)
        #output = np.convolve(signal, h, mode='same')

        # Добавляем шум
        #output = self._add_awgn(output)
        
        # AWGN
        output = self._add_awgn(signal) 
        
        return output