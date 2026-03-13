import numpy as np
from datetime import datetime


class BERRuler:

    def __init__(
        self,
        h2dB_init=0,
        h2dB_init_step=0.4,
        h2dB_min_step=0.1,
        h2dB_max_step=1.6,
        h2dB_max=15,
        min_BER=1e-4,
        min_FER=1,
        min_NumErBits=500,
        min_NumErFrames=100,
        min_NumTrFrames=100,
        max_NumTrBits=1e8,
        max_NumTrFrames=np.inf,
        max_BERRate=5,
        min_BERRate=2,
        log_language="Russian",
    ):

        # параметры
        self.h2dB = h2dB_init
        self.h2dBStep = h2dB_init_step
        self.h2dBInitStep = h2dB_init_step
        self.h2dBMinStep = h2dB_min_step
        self.h2dBMaxStep = h2dB_max_step
        self.h2dBMax = h2dB_max

        self.MinBER = min_BER
        self.MinFER = min_FER

        self.MinNumErBits = min_NumErBits
        self.MinNumErFrames = min_NumErFrames
        self.MinNumTrFrames = min_NumTrFrames

        self.MaxNumTrBits = max_NumTrBits
        self.MaxNumTrFrames = max_NumTrFrames

        self.MaxBERRate = max_BERRate
        self.MinBERRate = min_BERRate

        self.log_language = log_language

        # статистика текущей точки
        self.reset()

        # массивы результатов
        self.h2dBs = []
        self.BER_points = []
        self.FER_points = []

        # служебные
        self.AdditionalSNR = []
        self.isMainCalcFinished = False
        self.isStop = False

    def update_frame(self, tx_bits, rx_bits):

        tx_bits = np.asarray(tx_bits)
        rx_bits = np.asarray(rx_bits)

        n_bits = len(tx_bits)
        n_errors = np.sum(tx_bits != rx_bits)

        self.NumTrBits += n_bits
        self.NumTrFrames += 1
        self.NumErBits += n_errors

        if n_errors > 0:
            self.NumErFrames += 1

    def is_point_finished(self):

        enough_statistics = (
            self.NumErBits >= self.MinNumErBits
            and self.NumErFrames >= self.MinNumErFrames
            and self.NumTrFrames >= self.MinNumTrFrames
        )

        complexity_exceeded = (
            self.NumTrBits >= self.MaxNumTrBits
            or self.NumTrFrames >= self.MaxNumTrFrames
        )

        return enough_statistics or complexity_exceeded

    def finalize_point(self):

        ber = self.NumErBits / max(1, self.NumTrBits)
        fer = self.NumErFrames / max(1, self.NumTrFrames)

        self.h2dBs.append(self.h2dB)
        self.BER_points.append(ber)
        self.FER_points.append(fer)

        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if self.log_language.lower() == "Russian":
            print(
                f"{ts} | Точка завершена: h2 = {self.h2dB:.2f} дБ | "
                f"BER = {ber:.3e} | FER = {fer:.3e} | "
                f"Frames = {self.NumTrFrames}"
            )
        else:
            print(
                f"{ts} | Point finished: h2 = {self.h2dB:.2f} dB | "
                f"BER = {ber:.3e} | FER = {fer:.3e} | "
                f"Frames = {self.NumTrFrames}"
            )

        self._update_snr_step()

        self.reset()

    def _update_snr_step(self):

        if len(self.BER_points) < 2:
            self.h2dB += self.h2dBStep
            return

        ber_prev = self.BER_points[-2]
        ber_curr = self.BER_points[-1]

        if ber_curr == 0:
            rate = np.inf
        else:
            rate = ber_prev / ber_curr

        # уменьшение шага
        if rate > self.MaxBERRate:

            RRate = rate / self.MaxBERRate

            if RRate < 4:
                dec = 0.5
            elif RRate < 16:
                dec = 0.25
            elif RRate < 64:
                dec = 0.125
            else:
                dec = 0.0625

            self.h2dBStep = max(self.h2dBStep * dec, self.h2dBMinStep)

        # увеличение шага
        elif rate < self.MinBERRate:

            self.h2dBStep = min(self.h2dBStep * 2, self.h2dBMaxStep)

        self.h2dB += self.h2dBStep

        if self.h2dB > self.h2dBMax:
            self.isStop = True

    def reset(self):

        self.NumTrBits = 0
        self.NumErBits = 0
        self.NumTrFrames = 0
        self.NumErFrames = 0
        
    def get_results(self):

        return (
            np.array(self.h2dBs),
            np.array(self.BER_points),
            np.array(self.FER_points),
        )