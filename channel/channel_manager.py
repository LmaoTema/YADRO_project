from config import simulation_params, channel_params
from core.block import Block
from channel.awgn_channel import AWGNChannel
from channel.rayleigh_single_path import RayleighSinglePathChannel
from channel.rayleigh_multipath import RayleighMultipathChannel

class ChannelBlock(Block):
    def __init__(self, channel_model, snr_db=20, profile="TU", is_working=True):
        super().__init__(is_working)
        
        self.snr_db = snr_db
        self.profile = profile
        self.channel = channel_model
        
        if channel_model == "awgn":
            self.channel = AWGNChannel(snr_db=self.snr_db)

        elif channel_model == "rayleigh_single":
            self.channel = RayleighSinglePathChannel(
                maximum_doppler_shift=channel_params["doppler"],
                sample_rate=channel_params["sample_rate"]
            )

        elif channel_model == "rayleigh_multipath":
            self.channel = RayleighMultipathChannel(
                sample_rate=channel_params["sample_rate"],
                snr_db=self.snr_db,
                profile=self.profile,
                maximum_doppler_shift=channel_params["doppler"]
            )
        else:
            raise ValueError(f"Unknown channel model: {channel_model}")

    def _process(self, signal):
        return self.channel.process(signal)