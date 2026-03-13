import numpy as np

from core.pipeline import Pipeline
from config import SIMULATION, CHANNEL, CHANNEL_MODES, BER, BLOCKS, MODULATION

from transmitter.gsm_channel_coding.channel_coder import ChannelCoder
from transmitter.interleaver.base import Interleaver
from receiver.decoder.logic import ChannelDecoder
from channel.gsm_channel import GSMChannel
from transmitter.modulator import Modulation
from receiver.demodulator import Demodulation

from drawber.berruler import BERRuler  
from drawber.plot import plot_ber

#if not BLOCKS["modulator"]["is_working"]:
#    BLOCKS["demodulator"]["is_working"] = False
#if not BLOCKS["coder"]["is_working"]:
#    BLOCKS["decoder"]["is_working"] = False
#if not BLOCKS["coder"]:
#    BLOCKS["interleaver"] = False


def main():


    DEBUG_TRACE = True
    TRACE_FRAME = 0
    frame_counter = 0
    
    channel_type = SIMULATION["channel_type"]
    profile = CHANNEL["profile"]
    
    encoder = ChannelCoder(channel_type, is_working=BLOCKS["coder"]["is_working"])
    interleaver = Interleaver(channel_type, is_working=BLOCKS["interleaver"]["is_working"])
    pipeline = Pipeline([encoder, interleaver])


    params_modulation = MODULATION
    modulator = Modulation(channel_type, params_modulation, is_working=BLOCKS["modulator"]["is_working"])
    demodulator = Demodulation(channel_type, params_modulation, is_working=BLOCKS["demodulator"]["is_working"])

    
    mode_cfg = CHANNEL_MODES[channel_type]
    
    decoder = ChannelDecoder(scheme=mode_cfg["scheme"], is_working=BLOCKS["decoder"]["is_working"])
    frame_bits = CHANNEL_MODES[channel_type]["frame_bits"]
    ber_ruler = BERRuler(**BER)

    while not ber_ruler.isStop:

        snr_db = ber_ruler.h2dB 
        channel = GSMChannel(profile, snr_db, is_working=BLOCKS["channel"]["is_working"])

        while not ber_ruler.is_point_finished():

            bits = np.random.randint(0, 2, frame_bits)
            #print(len(bits))

            bursts = pipeline.run(bits.tolist())

            tx_bursts = [np.array(b[:-8]) for b in bursts]

            signals = [modulator.process(b) for b in tx_bursts]

            rx_signals = [channel.process(s) for s in signals]

            rx_bursts = [demodulator.process(s, params_modulation) for s in rx_signals]

            decoded_bits = decoder.process(rx_bursts)
            
            if DEBUG_TRACE and frame_counter == TRACE_FRAME:
                print("После источника:", bits)
                print("После кодера:", bursts)
                print("После burst mapper", tx_bursts)
                print("После модулятора", signals)
                print("После канала", rx_signals)
                print("После демодулятора:", rx_bursts)
                print("Декодированные:", decoded_bits)

            ber_ruler.update_frame(bits, decoded_bits)
            frame_counter += 1

        ber_ruler.finalize_point()

    snr, ber, fer = ber_ruler.get_results()

    plot_ber(snr, ber, fer)

    return snr, ber, fer

if __name__ == "__main__":
    main()