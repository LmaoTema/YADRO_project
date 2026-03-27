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
        min_NumErBits=200,
        min_NumErFrames=500,
        min_NumTrFrames=500,
        max_NumTrBits=1e8,
        max_NumTrFrames=np.inf,
        max_BERRate=5,
        min_BERRate=2,
        log_language="Russian",
        enable_log=True,
        channel_type="TCH/FS",
        **kwargs
    ):
        self.h2dB = h2dB_init
        self.h2dBStep = h2dB_init_step
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

        self.enable_log = enable_log
        self.log_language = log_language
        self.channel_type = channel_type

  
        tmp_blocks = self._slice_blocks(np.zeros(1))  
        self.stats = {name: {"NumTrBits":0, "NumErBits":0, "NumTrFrames":0, "NumErFrames":0} for name in tmp_blocks}
        self.results = {name: {"BER":[], "FER":[]} for name in tmp_blocks}

        self.h2dBs = []

        self.isStop = False


    def _slice_blocks(self, bits):
        if self.channel_type == "TCHFS":
            return {
                "class1": bits[0:182],
                "class2": bits[182:260]
            }
        elif self.channel_type == "CS1":
            return {"full": bits[:]}
        elif self.channel_type == "MCS1":
            return {
                "header": bits[0:80],
                "data": bits[80:456]
            }
        elif self.channel_type == "MCS5":
            return {
                "header": bits[0:136],
                "data": bits[136:1384]
            }
        else:
            return {"full": bits[:]}


    def update_frame(self, tx_bits, rx_bits):
        tx_blocks = self._slice_blocks(tx_bits)
        rx_blocks = self._slice_blocks(rx_bits)

        for name, tx_blk in tx_blocks.items():
            rx_blk = rx_blocks[name]
            n_bits = len(tx_blk)
            n_errors = np.sum(np.array(tx_blk) != np.array(rx_blk))

            self.stats[name]["NumTrBits"] += n_bits
            self.stats[name]["NumTrFrames"] += 1
            self.stats[name]["NumErBits"] += n_errors
            if n_errors > 0:
                self.stats[name]["NumErFrames"] += 1


    def is_point_finished(self):
        total_tr_bits = sum(s["NumTrBits"] for s in self.stats.values())
        total_er_bits = sum(s["NumErBits"] for s in self.stats.values())
        total_tr_frames = sum(s["NumTrFrames"] for s in self.stats.values())
        total_er_frames = sum(s["NumErFrames"] for s in self.stats.values())

        enough_statistics = (
            total_er_bits >= self.MinNumErBits and
            total_er_frames >= self.MinNumErFrames and
            total_tr_frames >= self.MinNumTrFrames
        )
        complexity_exceeded = (
            total_tr_bits >= self.MaxNumTrBits or
            total_tr_frames >= self.MaxNumTrFrames
        )
        return enough_statistics or complexity_exceeded

    def finalize_point(self):
        self.h2dBs.append(self.h2dB)
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for name, stat in self.stats.items():
            ber = stat["NumErBits"] / max(1, stat["NumTrBits"])
            fer = stat["NumErFrames"] / max(1, stat["NumTrFrames"])
            self.results[name]["BER"].append(ber)
            self.results[name]["FER"].append(fer)

            if self.enable_log:
                print(f"{ts} | h2={self.h2dB:.2f} dB | {name} BER={ber:.3e} | FER={fer:.3e} | Frames={stat['NumTrFrames']}")

        main_ber = list(self.results.values())[0]["BER"][-1]
        if main_ber < self.MinBER:
            self.isStop = True

        self._update_snr_step()
        self.reset()

    def _update_snr_step(self):
        if len(self.h2dBs) < 2:
            self.h2dB += self.h2dBStep
            return

        ber_prev = list(self.results.values())[0]["BER"][-2]
        ber_curr = list(self.results.values())[0]["BER"][-1]

        rate = np.inf if ber_curr == 0 else ber_prev / ber_curr

        if rate > self.MaxBERRate:
            dec = 0.5 if rate/self.MaxBERRate < 4 else 0.25 if rate/self.MaxBERRate < 16 else 0.125 if rate/self.MaxBERRate < 64 else 0.0625
            self.h2dBStep = max(self.h2dBStep * dec, self.h2dBMinStep)
        elif rate < self.MinBERRate:
            self.h2dBStep = min(self.h2dBStep * 2, self.h2dBMaxStep)

        self.h2dB += self.h2dBStep
        if self.h2dB > self.h2dBMax:
            self.isStop = True

    def reset(self):
        for stat in self.stats.values():
            stat["NumTrBits"] = 0
            stat["NumErBits"] = 0
            stat["NumTrFrames"] = 0
            stat["NumErFrames"] = 0

    # 🔹 Получение результатов в виде словаря для графиков
    def get_results(self):
        return {
            "h2dB": np.array(self.h2dBs),
            "results": self.results
        }