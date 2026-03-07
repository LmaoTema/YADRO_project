import numpy as np
from .encoder import ConvolutionalEncoder
from core.block import Block

class FIRECode:
    def __init__(self):
        self.parity_bits = 40

    def encode(self, bits):
        if len(bits) != 184:
            raise ValueError("CS-1 block must be 184 bits")
        parity = [0]*self.parity_bits
        return bits + parity  


class CS1BlockCoder:
    def __init__(self):
        self.fire = FIRECode()

        G = [
            [1,0,0,1,1], 
            [1,1,0,1,1]   
        ]
        
        self.conv = ConvolutionalEncoder(G,5)

    def process(self, bits):
        if len(bits) != 184:
            raise ValueError("CS-1 frame must be 184 bits")

        block224 = self.fire.encode(bits)  

        tail = [0,0,0,0]
        u = block224 + tail  # 228 bits

        coded = []
        for k in range(228):
            u_k   = u[k]
            u_k1  = u[k-1] if k-1 >= 0 else 0
            u_k3  = u[k-3] if k-3 >= 0 else 0
            u_k4  = u[k-4] if k-4 >= 0 else 0

            c0 = u_k ^ u_k3 ^ u_k4
            c1 = u_k ^ u_k1 ^ u_k3 ^ u_k4
            coded.append(c0)
            coded.append(c1)

        return coded