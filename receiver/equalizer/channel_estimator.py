import numpy as np

class ChannelEstimator:

    def __init__(self, modulation_params, train_start=61, train_end=87):
        self.BT = modulation_params.get("BT", 0.3)
        self.T = modulation_params.get("T", 3.69e-6)
        self.sps = modulation_params.get("sps", 4)
        self.train_start = train_start * self.sps
        self.train_end = train_end * self.sps

        self.gaus_duration = modulation_params.get("gaus_duration", 4)
        self.rect_duration = modulation_params.get("rect_duration", 1)
        self.L = (self.gaus_duration + self.rect_duration)

    # h(t) композитного фильтра (передатчик + канал)
    def h_awgn(self):
        BT = self.BT
        T = self.T
        gaus_duration = self.gaus_duration
        rect_duration = self.rect_duration
        L = self.L

        oversampling = 100
        sps_oversampling = self.sps * oversampling
        dt_oversampling = T/sps_oversampling

        delta = np.sqrt(np.log(2)) / (2 * np.pi * BT)

        t_h = np.arange(-gaus_duration / 2 * T, gaus_duration / 2 * T, dt_oversampling)
        t_rect = np.arange(-rect_duration / 2 * T, rect_duration / 2 * T, dt_oversampling)

        h_t = np.exp(-(t_h**2) / (2 * (delta**2) * (T**2))) / (
            np.sqrt(2 * np.pi) * delta * T
        )
        rect = np.ones(t_rect.size) / T

        g_t = np.convolve(h_t, rect) * dt_oversampling

        q_gmsk_oversampling = np.cumsum(g_t) * dt_oversampling

        s_increas = np.sin(np.pi / 2 * q_gmsk_oversampling)
        s_decreas = np.sin(np.pi / 2 - np.pi / 2 * (- q_gmsk_oversampling))
        s = np.concatenate([s_increas, s_decreas, np.zeros(2)])

        c_0 = np.ones((L + 1) * sps_oversampling)
        for i in range((L + 1) * sps_oversampling):
            for j in range(L):
                c_0[i] *= s[i + j * sps_oversampling]

        # Для АБГШ c_0 - импульсная характеристика
        h = c_0[::oversampling]

        return h

    def h_rayleigh(self, tx_burst, rx_burst):
        L_sps = self.L * self.sps

        tx_train = tx_burst[self.train_start : self.train_end]
        rx_train = rx_burst[self.train_start : self.train_end]

        N = len(tx_train)
        X = np.zeros((N - L_sps, L_sps), dtype=complex)

        for i in range(N - L_sps):
            X[i] = tx_train[i:i + L_sps]

        y = rx_train[L_sps:]

        h = np.linalg.lstsq(X, y, rcond=None)[0]

        return h