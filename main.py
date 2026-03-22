import numpy as np

from core.pipeline import Pipeline
from config import SIMULATION, CHANNEL, CHANNEL_MODES, BER, BLOCKS, MODULATION

from transmitter.channel_coder.coder_manager import ChannelCoder
from transmitter.interleaver.inter_manager import Interleaver
from receiver.decoder.dec_manager import ChannelDecoder
from receiver.deinterleaver.deinter_manager import Deinterleaver

from channel.channel_manager import ChannelBlock

from receiver.equalizer.zero_force import ZFEqualizer

from transmitter.modulator import Modulation
from receiver.demodulator import Demodulation

from drawber.berruler import BERRuler
from drawber.plot import plot_ber
    
def main():


    DEBUG_TRACE = True
    TRACE_FRAME = 0
    frame_counter = 0
    
    channel_type = SIMULATION["channel_type"]
    channel_model = SIMULATION["channel_model"]
    profile = CHANNEL["profile"]
    
    encoder = ChannelCoder(channel_type, is_working=BLOCKS["encoding"]["is_working"])
    interleaver = Interleaver(channel_type, is_working=BLOCKS["interleaver"]["is_working"])
    pipeline_Tx = Pipeline([encoder, interleaver])
    
    mode_cfg = CHANNEL_MODES[channel_type]
    
    deinterv = Deinterleaver(channel_type, is_working=BLOCKS["interleaver"]["is_working"])
    decoder = ChannelDecoder(scheme=mode_cfg["scheme"], is_working=BLOCKS["encoding"]["is_working"])
    pipeline_Rx = Pipeline([deinterv, decoder])
    
    
    params_modulation = MODULATION
    modulator = Modulation(channel_type, params_modulation, is_working=BLOCKS["modulation"]["is_working"])
    demodulator = Demodulation(channel_type, params_modulation, is_working=BLOCKS["modulation"]["is_working"])

    
    
    equalizer = ZFEqualizer(channel_type,is_working=BLOCKS["equalizer"]["is_working"])
    
  #  if SIMULATION["channel_model"] == "awgn":
  #      equalizer.is_working = False
    
    frame_bits = CHANNEL_MODES[channel_type]["frame_bits"]
    ber_ruler = BERRuler(**BER)

    while not ber_ruler.isStop:

        snr_db = ber_ruler.h2dB 
        channel = ChannelBlock(channel_model, snr_db, profile, is_working=BLOCKS["channel"]["is_working"])

        while not ber_ruler.is_point_finished():

            bits = np.random.randint(0, 2, frame_bits)

            tx_stream = pipeline_Tx.run(bits.tolist())
            #print(len(tx_stream))
            tx_stream = np.array(tx_stream)
            #print(len(tx_stream))
            signal = modulator.process(tx_stream)
            #print(len(signal))
            rx_signal = channel.process(signal, code_rate = 1/2, bits_per_symbol = 1, burst_eff = 50/53)
            #print(len(rx_signal))
            rx_signal = equalizer.process(rx_signal)
            rx_bits = demodulator.process(rx_signal)
            #rint(len(rx_bits))
            decoded_bits = pipeline_Rx.run(rx_bits)

            if DEBUG_TRACE and frame_counter == TRACE_FRAME:
                print("После источника:", bits)
                #print("После кодера:", tx_stream)
                # print("После burst mapper", tx_stream)
                # print("После модулятора", signal)
                # print("После канала", rx_signal)
                # print("После демодулятора:", rx_bits)
                print("Декодированные:", decoded_bits)

            ber_ruler.update_frame(bits, decoded_bits)
            frame_counter += 1

        ber_ruler.finalize_point()

    snr, ber, fer = ber_ruler.get_results()

    plot_ber(snr, ber, fer)

    return snr, ber, fer

if __name__ == "__main__":
    main()