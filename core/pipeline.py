# pipeline.py
from transmitter.gsm_channel_coding.tch_fs import TCHFSBlockCoder
from transmitter.gsm_channel_coding.cs1 import CS1BlockCoder
from transmitter.gsm_channel_coding.msc1 import MSC1Coding as MSC1Coding
from transmitter.gsm_channel_coding.msc5 import MSC5Coding as MSC5Coding

class Pipeline:
    def __init__(self):
        self.tch = TCHFSBlockCoder()
        self.cs1 = CS1BlockCoder()
        self.msc1 = MSC1Coding("MCS1")
        self.msc5 = MSC5Coding("MCS5")

    def run(self, tch_bits, cs1_bits, msc1_bits, msc5_bits):
        return {
            "tch_out": self.tch.process(tch_bits),
            "cs1_out": self.cs1.process(cs1_bits),
            "msc1_out": self.msc1.process(msc1_bits),
            "msc5_out": self.msc5.process(msc5_bits)
        }