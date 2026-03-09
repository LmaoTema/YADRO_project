import numpy as np

from core.pipeline import Pipeline
from transmitter.gsm_channel_coding.utils import MSC_PARAMS
from transmitter.gsm_channel_coding.tch_fs import TCHFSBlockCoder
from transmitter.interleaver.cstch import SpeechInterleaver

from transmitter.gsm_channel_coding.cs1 import CS1BlockCoder
from transmitter.interleaver.cstch import SpeechInterleaver as CS1Interleaver

from transmitter.gsm_channel_coding.msc1 import MSC1Coding
from transmitter.interleaver.msc_1 import MCS1Interleaver

from transmitter.gsm_channel_coding.msc5 import MSC5Coding
from transmitter.interleaver.msc_5 import MCS5Interleaver

from transmitter.modulator import Modulation
from receiver.demodulator import Demodulation

from receiver.decoder.dec_tch import TCHFSSpeechDecoder

from drawber.berruler import BERRuler  
from drawber.plot import plot_ber


def get_pipeline(channel_type):
    if channel_type == "TCHFS":
        return Pipeline([TCHFSBlockCoder(), SpeechInterleaver()])
    elif channel_type == "CS1":
        return Pipeline([CS1BlockCoder(), CS1Interleaver()])
    elif channel_type == "MCS1":
        return Pipeline([MSC1Coding("MCS1"), MCS1Interleaver()])
    elif channel_type == "MCS5":
        return Pipeline([MSC5Coding("MCS5"), MCS5Interleaver()])
    else:
        raise ValueError(f"Unknown channel type: {channel_type}")


def main():

    channel_type = "TCHFS"

    # Создание случайного кадра
    if channel_type == "TCHFS":
        bits = np.random.randint(0, 2, 260).tolist()
    elif channel_type == "CS1":
        bits = np.random.randint(0, 2, 184).tolist()
    elif channel_type == "MCS1":
        bits = np.random.randint(0, 2,
                                 MSC_PARAMS["MCS1"]["header_bits"] +
                                 MSC_PARAMS["MCS1"]["data_bits"]).tolist()
    elif channel_type == "MCS5":
        bits = np.random.randint(0, 2,
                                 MSC_PARAMS["MCS5"]["header_bits"] +
                                 MSC_PARAMS["MCS5"]["data_bits"]).tolist()


    if channel_type == "TCHFS":
        decoder = TCHFSSpeechDecoder()
    elif channel_type == "CS1":
        decoder = CS1BlockDecoder()
    elif channel_type == "MCS1":
        decoder = MSC1BlockDecoder()
    elif channel_type == "MCS5":
        decoder = MSC5BlockDecoder()
    else:
        raise ValueError(f"Unknown channel type: {channel_type}")

    pipeline = get_pipeline(channel_type)
    bursts = pipeline.run(bits)

    modulator = Modulation(channel_type)
    demodulator = Demodulation(channel_type)

    # Создаём объект для подсчёта BER
    ber_ruler = BERRuler(h2dB_init=0, log_language="English")

    print(f"Channel type: {channel_type}")
    print("Number of bursts:", len(bursts))
    print("Burst length:", len(bursts[0]))

    all_rx_bits = []

    for i, burst in enumerate(bursts, 1):
        tx_bits_burst = np.array(burst)

        signal = modulator.process(tx_bits_burst)

        # Канал + демодуляция
        rx_bits_burst = demodulator.process(signal)
        
        decoded_bits = decoder.process(rx_bits_burst)
        
        # Добавляем для BER
        ber_ruler.update_frame(tx_bits_burst, decoded_bits)

        all_rx_bits.append(decoded_bits)

    print("\nFinal BER:", ber_ruler.BERs[-1])
    print("Final FER:", ber_ruler.FERs[-1])

  
    return ber_ruler.h2dBs, ber_ruler.BERs, ber_ruler.FERs


if __name__ == "__main__":
    main()