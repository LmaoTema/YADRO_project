import numpy as np
from datetime import datetime

class BERRuler:

    def __init__(self, h2dB_init=0, h2dB_max=20, log_language="Russian"):

        self.h2dB = h2dB_init
        self.h2dB_max = h2dB_max
        self.log_language = log_language

        self.NumTrBits = 0
        self.NumErBits = 0
        self.NumTrFrames = 0
        self.NumErFrames = 0

        self.SNR_points = []
        self.BER_points = []
        self.FER_points = []

    def update_frame(self, tx_bits, rx_bits):

        n_bits = len(tx_bits)
        n_errors = np.sum(tx_bits != rx_bits)

        self.NumTrBits += n_bits
        self.NumTrFrames += 1
        self.NumErBits += n_errors

        if n_errors > 0:
            self.NumErFrames += 1

        ber = self.NumErBits / max(1, self.NumTrBits)
        fer = self.NumErFrames / max(1, self.NumTrFrames)

        self.print_log(ber, fer, n_errors, n_bits)

    def finalize_point(self):
        ber = self.NumErBits / max(1, self.NumTrBits)
        fer = self.NumErFrames / max(1, self.NumTrFrames)

        self.SNR_points.append(self.h2dB)
        self.BER_points.append(ber)
        self.FER_points.append(fer)

        print(f"\nPoint finished: SNR={self.h2dB} dB | BER={ber:.3e} | FER={fer:.3e}\n")

    def print_log(self, ber, fer, n_errors, n_bits):

        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if self.log_language.lower() == "Russian":
            log_str = (
                f"{ts} | h2 = {self.h2dB:.2f} дБ | "
                f"BER = {ber:.3e} ({self.NumErBits}/{self.NumTrBits}) | "
                f"FER = {fer:.3e} ({self.NumErFrames}/{self.NumTrFrames}) | "
                f"Ошибок = {n_errors}/{n_bits}"
            )
        else:
            log_str = (
                f"{ts} | h2 = {self.h2dB:.2f} dB | "
                f"BER = {ber:.3e} ({self.NumErBits}/{self.NumTrBits}) | "
                f"FER = {fer:.3e} ({self.NumErFrames}/{self.NumTrFrames}) | "
                f"Errors in frame = {n_errors}/{n_bits}"
            )

        print(log_str)

    def reset(self):
        self.NumTrBits = 0
        self.NumErBits = 0
        self.NumTrFrames = 0
        self.NumErFrames = 0

    def get_results(self):

        return (
            np.array(self.SNR_points),
            np.array(self.BER_points),
            np.array(self.FER_points),
        )