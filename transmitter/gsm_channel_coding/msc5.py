import numpy as np
from .encoder import ConvolutionalEncoder
from .utils import MSC_PARAMS, prepend_last_bits


class MSC5CRC:
    def __init__(self, parity_bits):
        self.parity_bits = parity_bits

    def encode(self, bits):
        # TODO: zaglushka
        parity = [0]*self.parity_bits
        return bits + parity


class MSC5HeaderCoder:
    def __init__(self, params):
        self.crc = MSC5CRC(params["header_crc"])
        G = [
            [1,1,1,1,0,1,1],
            [1,0,1,1,0,0,1],
            [1,1,0,1,1,0,1]
        ]
        self.conv = ConvolutionalEncoder(G,7)
        self.use_puncture = params["header_puncture"]

    def process(self, bits):
        bits = self.crc.encode(bits)
        bits = prepend_last_bits(bits,6)
        coded = self.conv.process(bits[:len(bits)-6])
        return coded

class MCS5DataPuncturer:
    def __init__(self, mode="P1"):
        self.mode = mode
        self.exceptions1 = {47,371,695,1019}
        self.exceptions2 = {136,460,784,1108}

    def process(self, bits):
        out = []
        for i, b in enumerate(bits):
            if self.mode == "P1":
                # стандарт P1
                if (i % 9 == 2) and (i not in self.exceptions1):
                    continue
                if 1388 <= i <= 1403 and (i not in self.exceptions1):
                    continue
            else:
                # стандарт P2
                if (i % 9 == 1) and (i not in self.exceptions2):
                    continue
                if 1387 <= i <= 1402 and (i not in self.exceptions2):
                    continue
            out.append(b)
        return out

class MSC5DataCoder:
    def __init__(self, params, cps="P1"):
        self.crc = MSC5CRC(params["data_crc"])
        G = [
            [1,1,1,1,0,1,1],
            [1,0,1,1,0,0,1],
            [1,1,0,1,1,0,1]
        ]
        self.conv = ConvolutionalEncoder(G,7)
        self.punct = MCS5DataPuncturer(cps)

    def process(self, bits):
        bits = self.crc.encode(bits)
        bits = bits + [0]*6  # tail bits
        coded = self.conv.process(bits)
        coded = self.punct.process(coded)
        return coded

class MSC5Coding:
    def __init__(self, scheme, cps="P1"):
        if scheme != "MCS5":
            raise ValueError("MSC-5 coder only")
        params = MSC_PARAMS[scheme]
        self.header_bits = params["header_bits"]
        self.data_bits = params["data_bits"]
        self.header = MSC5HeaderCoder(params)
        self.data = MSC5DataCoder(params, cps)
        self.scheme = scheme

    def process(self, bits):
        header = bits[:self.header_bits]
        data = bits[self.header_bits:self.header_bits + self.data_bits]
        h = self.header.process(header)
        d = self.data.process(data)

        mcs_flag = [0]*8
        return np.concatenate([h, d, np.array(mcs_flag)])