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

from channel.gsm_channel import GSMChannel
from channel.pdp_profiles import CHANNEL_PROFILES

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
    profile = CHANNEL_PROFILES["TU"]
    
    pipeline = get_pipeline(channel_type)

    modulator = Modulation(channel_type)
    demodulator = Demodulation(channel_type)
    

    if channel_type == "TCHFS":
        decoder = TCHFSSpeechDecoder()
        frame_bits = 260
    elif channel_type == "CS1":
        decoder = CS1BlockDecoder()
        frame_bits = 184
    elif channel_type == "MCS1":
        decoder = MSC1BlockDecoder()
        frame_bits = MSC_PARAMS["MCS1"]["header_bits"] + MSC_PARAMS["MCS1"]["data_bits"]
    elif channel_type == "MCS5":
        decoder = MSC5BlockDecoder()
        frame_bits = MSC_PARAMS["MCS5"]["header_bits"] + MSC_PARAMS["MCS5"]["data_bits"]
    else:
        raise ValueError("Unknown channel")
    
    ber_ruler = BERRuler(h2dB_init=0, h2dB_max=10)

    print(f"Channel type: {channel_type}")

    for snr_db in range(0, 11):

        print("\n==============================")
        print(f"SNR = {snr_db} dB")
        print("==============================")

        ber_ruler.h2dB = snr_db
        ber_ruler.reset()
        channel = GSMChannel(profile, snr_db)
        
        while ber_ruler.NumTrFrames < 500:

            bits = np.random.randint(0, 2, frame_bits).tolist()

            bursts = pipeline.run(bits)

            tx_bursts = [np.array(b) for b in bursts]

            signals = [modulator.process(b) for b in tx_bursts]

            rx_signals = [channel.process(s) for s in signals]

            rx_bursts = [demodulator.process(s) for s in rx_signals]

            decoded_bits = decoder.process(rx_bursts)

            ber_ruler.update_frame(np.array(bits), np.array(decoded_bits))

        ber_ruler.finalize_point()

    snr, ber, fer = ber_ruler.get_results()

    plot_ber(snr, ber, fer)

    return snr, ber, fer

if __name__ == "__main__":
    main()