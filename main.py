from core.pipeline import Pipeline
from transmitter.gsm_channel_coding.tch_fs import TCHFSBlockCoder
from transmitter.gsm_channel_coding.cs1 import CS1BlockCoder
from transmitter.gsm_channel_coding.msc1 import MSC1Coding as MSC1Coding
from transmitter.gsm_channel_coding.msc5 import MSC5Coding as MSC5Coding
from transmitter.gsm_channel_coding.utils import MSC_PARAMS

from channel.gsm_channel import GSMChannel
from channel.pdp_profiles import CHANNEL_PROFILES

from receiver.equalizer import ZFEqualizer


def main():
    # Пример: генерируем случайные биты
    import numpy as np
    tch_bits = np.random.randint(0, 2, 260).tolist()
    cs1_bits = np.random.randint(0, 2, 184).tolist()
    msc1_bits = np.random.randint(0, 2, MSC_PARAMS["MCS1"]["header_bits"] + MSC_PARAMS["MCS1"]["data_bits"]).tolist()
    msc5_bits = np.random.randint(0, 2, MSC_PARAMS["MCS5"]["header_bits"] + MSC_PARAMS["MCS5"]["data_bits"]).tolist()

    # Кодируем
    tch_coder = TCHFSBlockCoder()
    cs1_coder = CS1BlockCoder()
    msc1_coder = MSC1Coding("MCS1")
    msc5_coder = MSC5Coding("MCS5")

    tch_out = tch_coder.process(tch_bits)
    cs1_out = cs1_coder.process(cs1_bits)
    msc1_out = msc1_coder.process(msc1_bits)
    msc5_out = msc5_coder.process(msc5_bits)

    # Вывод размеров
    print(f"TCH/FS output bits: {len(tch_out)}")
    print(f"CS-1 output bits: {len(cs1_out)}")
    print(f"MCS-1 output bits: {len(msc1_out)}")
    print(f"MCS-5 output bits: {len(msc5_out)}")
    
    # Задаем канал
    profile = CHANNEL_PROFILES["TU"] 
    gsm_channel = GSMChannel(profile, fs=10e6, snr_db=20)
    
    equalizer = ZFEqualizer()
    
    # Передаем сигнал через канал (нужно до этого bits -> signal)
    tch_chan = gsm_channel.process(tch_signal)
    cs1_chan = gsm_channel.process(cs1_signal)
    msc1_chan = gsm_channel.process(msc1_signal)
    msc5_chan = gsm_channel.process(msc5_signal)

    print(f"TCH/FS after channel: {len(tch_chan)} samples")
    print(f"CS-1 after channel: {len(cs1_chan)} samples")
    print(f"MCS-1 after channel: {len(msc1_chan)} samples")
    print(f"MCS-5 after channel: {len(msc5_chan)} samples")
    
    # Эквализация
    tch_eq = equalizer.process(tch_chan)
    cs1_eq = equalizer.process(cs1_chan)
    msc1_eq = equalizer.process(msc1_chan)
    msc5_eq = equalizer.process(msc5_chan)
    
    print(f"TCH/FS after equalizer: {len(tch_eq)} samples")
    print(f"CS-1 after equalizer: {len(cs1_eq)} samples")
    print(f"MCS-1 after equalizer: {len(msc1_eq)} samples")
    print(f"MCS-5 after equalizer: {len(msc5_eq)} samples")

if __name__ == "__main__":
    main()