from config import SIMULATION, CHANNEL
from core.block import Block
from channel.awgn_channel import AWGNChannel
from channel.rayleigh_single_path import RayleighSinglePathChannel
from channel.rayleigh_multipath import RayleighMultipathChannel

class ChannelBlock(Block):
    def __init__(self, channel_model, snr_db, code_rate, bits_per_symbol, burst_eff, profile, is_working=True):
        super().__init__(is_working)
        
        self.channel = channel_model
        self.snr_db = snr_db
        self.code_rate = code_rate
        self.bits_per_symbol = bits_per_symbol
        self.burst_eff = burst_eff
        self.profile = profile
        self.channel = channel_model
        
        if channel_model == "awgn":
            self.channel = AWGNChannel(snr_db=self.snr_db,
                code_rate = self.code_rate, 
                bits_per_symbol = self.bits_per_symbol, 
                burst_eff = self.burst_eff)

        elif channel_model == "rayleigh_single":
            self.channel = RayleighSinglePathChannel(
                maximum_doppler_shift=CHANNEL["doppler"],
                sample_rate=CHANNEL["sample_rate"]
            )

        elif channel_model == "rayleigh_multipath":
            self.channel = RayleighMultipathChannel(
                sample_rate=CHANNEL["sample_rate"],
                snr_db=self.snr_db,
                profile=self.profile,
                maximum_doppler_shift=CHANNEL["doppler"]
            )
        else:
            raise ValueError(f"Unknown channel model: {channel_model}")

    def _process(self, signal):
        return self.channel.process(signal)