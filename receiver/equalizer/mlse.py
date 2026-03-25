import numpy as np
from .channel_estimator import ChannelEstimator

class MLSEEqualizer:
    def __init__(self, modulation_params):
        self.sps = modulation_params.get("sps", 4)
        self.estimator = ChannelEstimator(modulation_params)

    def procces_eq(self, rx_signal, tx_signal):
       # Оценка канала + согласованный фильтр
       # на выходе нужна еще и полученная импульсная характеристика
       return 0, 0