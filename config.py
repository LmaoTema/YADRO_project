from core.pipeline import Pipeline
from channel.pdp_profiles import CHANNEL_PROFILES

SIMULATION = {
    "channel_type": "TCHFS",
}

BLOCKS = {

    "encoding": {"is_working": False},
    "interleaver": {"is_working": False},
    "modulation": {"is_working": True},
    "channel": {"is_working": True},
    "equalizer": {"is_working": False},
}

BER = {
    "h2dB_init": 0,
    "h2dB_init_step": 0.4,
    "h2dB_min_step": 0.1,
    "h2dB_max_step": 1.6,
    "h2dB_max": 9,
    "min_BER": 1e-4,
    "min_FER": 1,
    "min_NumErBits": 500,
    "min_NumErFrames": 100,
    "min_NumTrFrames": 100,
    "max_NumTrBits": 1e8,
    "max_NumTrFrames": float("inf"),
    "max_BERRate": 5,
    "min_BERRate": 2,
    "log_language": "Russian"
}

CHANNEL_MODES = {
    "TCHFS": {
        "scheme": "TCHFS",
        "frame_bits": 260
    },
   # "CS1": {
    #    "scheme": "CS1",
    #    "frame_bits": 184
    #},
    #"MCS1": {
    #    "scheme": "MCS1",
     #   "frame_bits": MSC_PARAMS["MCS1"]["header_bits"] + MSC_PARAMS["MCS1"]["data_bits"]
    #},
    #"MCS5": {
     #   "scheme": "MCS5",
     #   "frame_bits": MSC_PARAMS["MCS5"]["header_bits"] + MSC_PARAMS["MCS5"]["data_bits"]
    #}
}
MODULATION = {
    "BT": 0.3,
    "T": 1,
    "sps": 100,
    "h": 0.5,
    "gaus_duration": 4,
    "rect_duration": 1,
    "type_demod": "diff_phase" # vit_soft
}

CHANNEL = {
    "profile": "TU",        # TU / RA / HT
    "sample_rate": 1e6,
    "doppler": 100
}
DEBUG = {
    "print_crc_errors": False,
    "log_pipeline": False
}