from core.pipeline import Pipeline
from transmitter.gsm_channel_coding.tch_fs import TCHFSBlockCoder
from transmitter.gsm_channel_coding.cs1 import CS1BlockCoder
from transmitter.gsm_channel_coding.msc1 import MSC1Coding as MSC1Coding
from transmitter.gsm_channel_coding.msc5 import MSC5Coding as MSC5Coding
from transmitter.gsm_channel_coding.utils import MSC_PARAMS

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

if __name__ == "__main__":
    main()