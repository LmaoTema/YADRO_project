from core.pipeline import Pipeline
from transmitter.gsm_channel_coding.utils import MSC_PARAMS
from receiver.decoder.dec_tch import TCHFSSpeechDecoder
from channel.pdp_profiles import CHANNEL_PROFILES
#from receiver.decoder.dec_cs import CS1BlockDecoder
#from receiver.decoder.dec_msc import MSC1BlockDecoder, MSC5BlockDecoder


SIMULATION = {
    "channel_type": "TCHFS",
    "snr": {
        "start": 0,
        "max": 10,
        "step": 1
    },
    "frames_per_point": 500,
    "plot": True
}

BER = {
    "h2dB_init": 0,
    "h2dB_init_step": 0.4,
    "h2dB_min_step": 0.1,
    "h2dB_max_step": 1.6,
    "h2dB_max": 15,
    "MinBER": 1e-4,
    "MinFER": 1,
    "MinNumErBits": 500,
    "MinNumErFrames": 100,
    "MinNumTrFrames": 100,
    "MaxNumTrBits": 1e8,
    "MaxNumTrFrames": float("inf"),
    "MaxBERRate": 5,
    "MinBERRate": 2,
    "log_language": "Russian"
}

CHANNEL_MODES = {
    "TCHFS": {
        "decoder": "TCHFSSpeechDecoder",
        "frame_bits": 260
    },
    "CS1": {
        "decoder": "CS1BlockDecoder",
        "frame_bits": 184
    },
    "MCS1": {
        "decoder": "MSC1BlockDecoder",
        "frame_bits": MSC_PARAMS["MCS1"]["header_bits"] + MSC_PARAMS["MCS1"]["data_bits"]
    },
    "MCS5": {
        "decoder": "MSC5BlockDecoder",
        "frame_bits": MSC_PARAMS["MCS5"]["header_bits"] + MSC_PARAMS["MCS5"]["data_bits"]
    }
}

MODULATION = {
    "type": "GMSK",
    "samples_per_symbol": 4,
    "bt": 0.3
}

CHANNEL = {
    "profile": CHANNEL_PROFILES["TU"]
}

DECODER = {
    "use_crc": True,
    "crc_print_errors": False
}

DEBUG = {
    "print_crc_errors": False,
    "log_pipeline": False
}


DECODER_CLASSES = {
    "TCHFSSpeechDecoder": TCHFSSpeechDecoder,
   # "CS1BlockDecoder": CS1BlockDecoder,
   # "MSC1BlockDecoder": MSC1BlockDecoder,
    #"MSC5BlockDecoder": MSC5BlockDecoder,
}