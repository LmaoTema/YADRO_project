import numpy as np
from datetime import datetime
from core.block import Block

class BERRuler:
    def __init__(self, h2dB_init=0, h2dB_max=20, log_language="Russia"):
        self.h2dB = h2dB_init
        self.h2dB_max = h2dB_max
        self.log_language = log_language

        # Статистика
        self.NumTrBits = 0
        self.NumErBits = 0
        self.NumTrFrames = 0
        self.NumErFrames = 0
        self.h2dBs = [self.h2dB]
        self.BERs = []
        self.FERs = []

    def update_frame(self, tx_bits, rx_bits, frame_energy=None):
        n_bits = len(tx_bits)
        n_errors = np.sum(tx_bits != rx_bits)

        self.NumTrBits += n_bits
        self.NumTrFrames += 1
        self.NumErBits += n_errors
        if n_errors > 0:
            self.NumErFrames += 1

        ber = self.NumErBits / max(1, self.NumTrBits)
        fer = self.NumErFrames / max(1, self.NumTrFrames)
        self.BERs.append(ber)
        self.FERs.append(fer)

        # Лог
        self.print_log(ber, fer, n_errors, n_bits)

    def print_log(self, ber, fer, n_errors, n_bits):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if self.log_language.lower() == "russian":
            log_str = (f"{ts} | h2 = {self.h2dB:.2f} дБ | "
                       f"BER = {ber:.3e} ({self.NumErBits}/{self.NumTrBits}) | "
                       f"FER = {fer:.3e} ({self.NumErFrames}/{self.NumTrFrames}) | "
                       f"Ошибок = {n_errors}/{n_bits}")
        else:
            log_str = (f"{ts} | h2 = {self.h2dB:.2f} dB | "
                       f"BER = {ber:.3e} ({self.NumErBits}/{self.NumTrBits}) | "
                       f"FER = {fer:.3e} ({self.NumErFrames}/{self.NumTrFrames}) | "
                       f"Errors in frame = {n_errors}/{n_bits}")

        print(log_str)

    def reset(self):
        self.NumTrBits = 0
        self.NumErBits = 0
        self.NumTrFrames = 0
        self.NumErFrames = 0

        self.h2dBs = [self.h2dB]
        self.BERs = []
        self.FERs = []

    def get_results(self):
        return np.array(self.h2dBs), np.array(self.BERs), np.array(self.FERs)