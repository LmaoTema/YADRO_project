import numpy as np

from core.pipeline import Pipeline
from config import SIMULATION, CHANNEL, MODULATION, CHANNEL_MODES, BER, DECODER_CLASSES
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

    channel_type = SIMULATION["channel_type"]
    profile = CHANNEL["profile"]
    
    pipeline = get_pipeline(channel_type)

    params_modulation = MODULATION
    modulator = Modulation(channel_type, params_modulation)
    demodulator = Demodulation(channel_type, params_modulation)
    
    mode_cfg = CHANNEL_MODES[channel_type]
    decoder_class = DECODER_CLASSES[mode_cfg["decoder"]]
    decoder = decoder_class()
    frame_bits = mode_cfg["frame_bits"]
    
    ber_ruler = BERRuler(**BER)

    while not ber_ruler.isStop:

        snr_db = ber_ruler.h2dB 
        channel = GSMChannel(profile, snr_db)

        while not ber_ruler.is_point_finished():

            bits = np.random.randint(0, 2, frame_bits)

            bursts = pipeline.run(bits.tolist())

            tx_bursts = [np.array(b[:-8]) for b in bursts]

            signals = [modulator.process(b) for b in tx_bursts]

            rx_signals = [channel.process(s) for s in signals]

            rx_bursts = [demodulator.process(s, params_modulation) for s in rx_signals]

            decoded_bits = decoder.process(rx_bursts)

            ber_ruler.update_frame(bits, decoded_bits)

        ber_ruler.finalize_point()

    snr, ber, fer = ber_ruler.get_results()

    plot_ber(snr, ber, fer)

    return snr, ber, fer

if __name__ == "__main__":
    main()