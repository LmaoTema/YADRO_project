import numpy as np
from core.block import Block

from .viterbi_uni import ViterbiDecoder

class SpeechDeinterleaver(Block):

    def __init__(self):
        pass

    def deinterleave_57(self, data):

        out = np.zeros(57, dtype=int)

        for j in range(57):
            k = (7 * j) % 57
            out[k] = data[j]

        return out

    def extract_data(self, burst):

        first = burst[3:60]
        second = burst[87:144]

        return first, second

    def process(self, bursts):

        if len(bursts) != 4:
            raise ValueError("Expected 4 bursts")

        subblocks = [None]*8

        for b in range(4):

            first, second = self.extract_data(bursts[b])

            subblocks[b] = self.deinterleave_57(first)
            subblocks[b+4] = self.deinterleave_57(second)

        bits = np.concatenate(subblocks)

        return bits

def reverse_reordering(u):

    class1a_crc = [0]*53

    for k in range(91):

        if 2*k < 50:
            class1a_crc[2*k] = u[k]

        if 2*k+1 < 50:
            class1a_crc[2*k+1] = u[184-k]

    for k in range(3):
        class1a_crc[50+k] = u[91+k]

    class1b = u[53:185]

    return class1a_crc, class1b

class CRC5350Decoder:

    def __init__(self):
        self.poly = [1,0,1,1]

    def check(self, bits):

        reg = bits.copy()

        for i in range(50):

            if reg[i] == 1:
                for j in range(len(self.poly)):
                    reg[i+j] ^= self.poly[j]

        return reg[-3:] == [0,0,0]

    def decode(self, bits):

        data = bits[:50]

        if not self.check(bits):
            print("CRC error")

        return data
    
class TCHFSSpeechDecoder(Block):

    def __init__(self):

        self.deint = SpeechDeinterleaver()
        self.viterbi = self.viterbi = ViterbiDecoder(constraint_length=5,polynomials=[0x19, 0x1D])
        self.crc = CRC5350Decoder()

    def reverse_reordering(self, u):

        class1a_crc = [0]*53

        for k in range(91):

            if 2*k < 50:
                class1a_crc[2*k] = u[k]

            if 2*k+1 < 50:
                class1a_crc[2*k+1] = u[184-k]

        for k in range(3):
            class1a_crc[50+k] = u[91+k]

        class1b = u[53:185]

        return class1a_crc, class1b


    def process(self, bursts):

        bits456 = self.deint.process(bursts)

        coded = bits456[:378]
        class2 = bits456[378:]

        u = self.viterbi.decode(coded)

        class1a_crc, class1b = self.reverse_reordering(u)

        class1a = self.crc.decode(class1a_crc)

        class1b = class1b[:132]

        frame = np.array(class1a + class1b + list(class2))

        return frame