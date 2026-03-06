from transmitter.channel_types import ChannelType

CHANNEL_CONFIG = {

    ChannelType.TCH_FS: {
        "conv_rate": 1/2,
        "constraint": 5,
        "puncturing": None,
        "interleaver": "speech",
        "burst_size": 114
    },

    ChannelType.CS1: {
        "conv_rate": 1/2,
        "constraint": 5,
        "puncturing": None,
        "interleaver": "data",
        "burst_size": 114
    },

    ChannelType.MCS1: {
        "conv_rate": 1/3,
        "constraint": 7,
        "puncturing": None,
        "interleaver": "edge",
        "modulation": "GMSK"
    },

    ChannelType.MCS5: {
        "conv_rate": 1/3,
        "constraint": 7,
        "puncturing": "MCS5",
        "interleaver": "edge",
        "modulation": "8PSK"
    }
}