
from config import simulation_params, channel_params
from core.block import Block

from channel.awgn_channel import AWGNChannel
from channel.rayleigh_single_path import RayleighSinglePathChannel
from channel.rayleigh_multipath import RayleighMultipathChannel

class ChannelBlock(Block):
    # В channel_manager.py
    def __init__(self, channel_model: str, snr_db: float = 20, profile: str = None, is_working: bool = True):
    
        super().__init__(is_working)
    
        self.channel_model = channel_model
        self.snr_db = snr_db
        self.profile = profile if profile is not None else channel_params["profile"]


        if channel_model == "awgn":
            self.channel = AWGNChannel(
                snr_db = self.snr_db, 
                code_rate = channel_params["code_rate"], 
                bits_per_symbol = channel_params["bits_per_symbol"], 
                burst_eff = channel_params["burst_eff"]
            )

        elif channel_model == "rayleigh_single":
            self.channel = RayleighSinglePathChannel(
                maximum_doppler_shift = channel_params["doppler"],
                sample_rate=channel_params["sample_rate"]
            )

        elif channel_model == "rayleigh_multipath":
            self.channel = RayleighMultipathChannel(
                sample_rate = channel_params["sample_rate"],
                snr_db = self.snr_db,
                profile = self.profile,
                maximum_doppler_shift = channel_params["doppler"]
            )
        else:
            raise ValueError(f"Unknown channel model: {channel_model}")

    def _process(self, tx_signal):
        return self.channel.process(tx_signal)