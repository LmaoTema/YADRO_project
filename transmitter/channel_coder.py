import numpy as np
from core.block import Block

class ConvolutionalEncoder(Block):

    def __init__(self, G, K):
        
       # G - generator polynomials
       # K - constraint length
        
        self.G = G
        self.K = K
        self.state = [0]*(K-1)

    def encode_bit(self, bit):

        reg = [bit] + self.state

        out = []
        for g in self.G:

            val = 0
            for r, g_bit in zip(reg, g):
                if g_bit:
                    val ^= r

            out.append(val)

        self.state = reg[:-1]

        return out

    def process(self, bits):

        output = []

        for b in bits:
            output.extend(self.encode_bit(b))

        return np.array(output)
    
class Puncturer:

    def __init__(self, pattern):
        self.pattern = pattern

    def process(self, bits):

        out = []

        for i,b in enumerate(bits):

            if self.pattern[i % len(self.pattern)]:
                out.append(b)

        return np.array(out)
    
    
class ChannelCoder(Block):

    def __init__(self, scheme):

        if scheme == "TCH_FS":

            G = [
                [1,1,1,0,1],
                [1,0,1,1,1]
            ]
            K = 5
            puncture = None


        elif scheme == "CS1":

            G = [
                [1,1,1,0,1],
                [1,0,1,1,1]
            ]
            K = 5
            puncture = None


        elif scheme == "MCS1":

            G = [
                [1,1,1,1,0,1,1],
                [1,0,1,1,0,0,1],
                [1,1,0,1,1,0,1]
            ]
            K = 7
            puncture = None


        elif scheme == "MCS5":

            G = [
                [1,1,1,1,0,1,1],
                [1,0,1,1,0,0,1],
                [1,1,0,1,1,0,1]
            ]
            K = 7

            puncture = [
                1,1,0,
                1,0,1
            ]


        self.encoder = ConvolutionalEncoder(G,K)

        if puncture:
            self.puncturer = Puncturer(puncture)
        else:
            self.puncturer = None


    def process(self, bits):

        bits = self.encoder.process(bits)

        if self.puncturer:
            bits = self.puncturer.process(bits)

        return bits