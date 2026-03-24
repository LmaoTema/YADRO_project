import numpy as np

from core.pipeline import Pipeline
from config import simulation_params, channel_params, mode_params, BER, block_params, modulation_params

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
    
    channel_type = simulation_params["channel_type"]
    channel_model = simulation_params["channel_model"]
    profile = channel_params["profile"]
    mode_cfg = mode_params[channel_type]
    frame_bits = mode_params[channel_type]["frame_bits"]
    
    encoder = ChannelCoder(channel_type, is_working=block_params["encoding"]["is_working"])
    interleaver = Interleaver(channel_type, is_working=block_params["interleaver"]["is_working"])
    pipeline_Tx = Pipeline([encoder, interleaver])
    
    deinterv = Deinterleaver(channel_type, is_working=block_params["interleaver"]["is_working"])
    decoder = ChannelDecoder(scheme=mode_cfg["scheme"], is_working=block_params["encoding"]["is_working"])
    pipeline_Rx = Pipeline([deinterv, decoder])
    
    modulator = Modulation(channel_type, modulation_params, is_working=block_params["modulation"]["is_working"])
    demodulator = Demodulation(channel_type, modulation_params, is_working=block_params["modulation"]["is_working"])

    equalizer = ZFEqualizer(modulation_params, is_working=block_params["equalizer"]["is_working"])
    
    ber_ruler = BERRuler(**BER)

    while not ber_ruler.isStop:

        snr_db = ber_ruler.h2dB 
        channel = ChannelBlock(channel_model, snr_db, 
                code_rate = 1/2, 
                bits_per_symbol = 1, 
                burst_eff = 50/53, 
                profile = "TU", 
                is_working=block_params["channel"]["is_working"])

        while not ber_ruler.is_point_finished():

            bits = np.random.randint(0, 2, frame_bits)

            tx_stream = pipeline_Tx.run(bits.tolist())

            tx_signal = modulator.process(np.array(tx_stream))

            rx_signal = channel.process(tx_signal)

            eq_signal = equalizer.process(tx_signal, rx_signal)

            rx_bits = demodulator.process(eq_signal)

            decoded_bits = pipeline_Rx.run(rx_bits)

            if DEBUG_TRACE and frame_counter == TRACE_FRAME:
                print("После источника:", bits)
                # print("После кодера:", tx_stream)
                # print("После модулятора", tx_signal)
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