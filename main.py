import numpy as np

from core.pipeline import Pipeline
from transmitter.gsm_channel_coding.utils import MSC_PARAMS
from transmitter.gsm_channel_coding.tch_fs import TCHFSBlockCoder
from transmitter.interleaver.cstch import SpeechInterleaver

from transmitter.gsm_channel_coding.cs1 import CS1BlockCoder
from transmitter.interleaver.cstch import SpeechInterleaver as CS1Interleaver

from transmitter.gsm_channel_coding.msc1 import MSC1Coding
from transmitter.interleaver.msc_1 import MCS1Interleaver

from transmitter.gsm_channel_coding.msc5 import MSC5Coding
from transmitter.interleaver.msc_5 import MCS5Interleaver


def get_pipeline(channel_type):
    """
    channel_type: 'TCHFS', 'CS1', 'MCS1', 'MCS5'
    """
    if channel_type == 'TCHFS':
        return Pipeline([
            TCHFSBlockCoder(),
            SpeechInterleaver()
        ])
    elif channel_type == 'CS1':
        return Pipeline([
            CS1BlockCoder(),
            CS1Interleaver()
        ])
    elif channel_type == 'MCS1':
        return Pipeline([
            MSC1Coding("MCS1"),
            MCS1Interleaver()
        ])
    elif channel_type == 'MCS5':
        return Pipeline([
            MSC5Coding("MCS5"),
            MCS5Interleaver()
        ])
    else:
        raise ValueError(f"Unknown channel type: {channel_type}")


def main():

   
    channel_type = "MCS5"  #  'CS1', 'MCS1', 'MCS5'

    if channel_type == "TCHFS":
        bits = np.random.randint(0, 2, 260).tolist()
    elif channel_type == "CS1":
        bits = np.random.randint(0, 2, 184).tolist()
    elif channel_type == "MCS1":
        # например MSC1_PARAMS['header_bits'] + MSC1_PARAMS['data_bits']
        bits = np.random.randint(0, 2, MSC_PARAMS["MCS1"]["header_bits"] + MSC_PARAMS["MCS1"]["data_bits"]).tolist()
    elif channel_type == "MCS5":
        bits = np.random.randint(0, 2, MSC_PARAMS["MCS5"]["header_bits"] + MSC_PARAMS["MCS5"]["data_bits"]).tolist()


    pipeline = get_pipeline(channel_type)

    bursts = pipeline.run(bits)

    print(f"Channel type: {channel_type}")
    print("Number of bursts:", len(bursts))
    print("Burst length:", len(bursts[0]))

    for i, burst in enumerate(bursts, 1):
        print(f"\nBurst {i}:")
        print(burst)


if __name__ == "__main__":
    main()