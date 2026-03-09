import numpy as np
from .base import Interleaver

class MCS1Interleaver(Interleaver):
    def __init__(self, bursts=4):
        self.bursts = bursts
        if bursts != 4:
            raise ValueError("MCS1Interleaver expects 4 bursts per block")
        
        self.tail_bits = np.zeros(3, dtype=int)
        self.guard_bits = np.zeros(8, dtype=int)
        self.st_flag = np.zeros(1, dtype=int)
        self.training_seq = np.array([0,0,1,0,1,1,0,1,1,1,0,1,1,1,1,0,0,0,1,0,1,1,0,1,1,1], dtype=int)

    @staticmethod
    def interleave_57(subblock):
        out = np.zeros(57, dtype=int)
        for k in range(57):
            j = (49 * k) % 57
            out[j] = subblock[k]
        return out

    def process(self, block):
        if len(block) != 456:
            raise ValueError("Input block must have 456 bits (80 header + 372 data + 4 tail)")

        subblocks = [block[i*57:(i+1)*57] for i in range(8)]

        bursts_out = []

        for b in range(self.bursts):
            first_data = self.interleave_57(subblocks[b])
            second_data = self.interleave_57(subblocks[b+4])
            
            burst = np.concatenate([
                self.tail_bits,     
                first_data,                    
                self.st_flag,        
                self.training_seq,            
                second_data,                   
                self.st_flag,        
                self.tail_bits,
                self.guard_bits      
            ])
            bursts_out.append(burst)

        return np.array(bursts_out) 