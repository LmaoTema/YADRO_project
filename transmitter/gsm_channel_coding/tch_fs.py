
from core.block import Block
from .encoder import ConvolutionalEncoder

class CRC5350:
    def __init__(self):
        self.poly = [1,0,1,1]  # x^3 + x + 1

    def encode(self, bits):
        reg = bits + [0,0,0]
        poly = self.poly
        for i in range(len(bits)):
            if reg[i] == 1:
                for j in range(len(poly)):
                    reg[i+j] ^= poly[j]
        parity = reg[-3:]
        return bits + parity  # 50 bits + 3 parity bits


class TCHFSBlockCoder:
    def __init__(self):
        self.crc = CRC5350()

        G = [
            [1,0,0,1,1],  # G0
            [1,1,0,1,1]   # G1
        ]
        self.conv = ConvolutionalEncoder(G, 5)  

    def process(self, bits):
        if not getattr(self, "is_working", True):
            return bits.copy()
        if len(bits) != 260:
            raise ValueError("TCH/FS frame must be 260 bits")

        class1a = bits[0:50]
        class1b = bits[50:182]
        class2  = bits[182:260]

        class1a_crc = self.crc.encode(class1a)  # 53 bits
        # Reordering 
        u = [0]*189  # class1: 189 bits including parity + tail

        for k in range(91):
            if 2*k < 50:
                u[k] = class1a_crc[2*k]       # even bits
            if 2*k+1 < 50:
                u[184-k] = class1a_crc[2*k+1] # odd bits

        for k in range(3):
            u[91+k] = class1a_crc[50+k]

        for k in range(185,189):
            u[k] = 0

        coded = []
        for k in range(189):
            u_k   = u[k]
            u_k1  = u[k-1] if k-1 >= 0 else 0
            u_k3  = u[k-3] if k-3 >= 0 else 0
            u_k4  = u[k-4] if k-4 >= 0 else 0

            c0 = u_k ^ u_k3 ^ u_k4
            c1 = u_k ^ u_k1 ^ u_k3 ^ u_k4
            coded.append(c0)
            coded.append(c1)
            
        frame = coded + class2  # 378 + 78 = 456 bits class1+class2

        return frame