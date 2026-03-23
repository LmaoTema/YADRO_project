
simulation_params = {
    "channel_type": "TCHFS",
    "channel_model": "awgn" # rayleigh_single, rayleigh_multipath, awgn
}

block_params = {

    "encoding": {"is_working": True},
    "interleaver": {"is_working": True},
    "modulation": {"is_working": True},
    "channel": {"is_working": False},
    "equalizer": {"is_working": False},
}

BER = {
    "h2dB_init": 0,
    "h2dB_init_step": 0.4,
    "h2dB_min_step": 0.1,
    "h2dB_max_step": 1.6,
    "h2dB_max": 15,
    "min_BER": 1e-3,
    "min_FER": 1,
    "min_NumErBits": 700,
    "min_NumErFrames": 350,
    "min_NumTrFrames": 700,
    "max_NumTrBits": 1e8,
    "max_NumTrFrames": float("inf"),
    "max_BERRate": 5,
    "min_BERRate": 2,
    "log_language": "Russian"
}

mode_params = {
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

modulation_params = {
    "BT": 0.3,
    "T": 3.69e-6,
    "sps": 4,
    "h": 0.5,
    "gaus_duration": 4,
    "rect_duration": 1,
    "type_demod": "diff_phase" # diff_phase / vit_hard / vit_soft 
}

channel_params = {
    "profile": "TU",        # TU / RA / HT
    "sample_rate": 1e6,
    "doppler": 100
}