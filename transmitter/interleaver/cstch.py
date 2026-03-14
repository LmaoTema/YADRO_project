import numpy as np

class SpeechInterleaver:
    def __init__(self, bursts=8):
        if bursts != 8:
            raise ValueError("SpeechInterleaver expects 4 bursts per block")
        self.bursts = bursts
        self.tail_bits = np.zeros(3, dtype=int)
        self.guard_bits = np.zeros(8, dtype=int)
        self.st_flag = np.zeros(1, dtype=int)
        self.training_seq = np.array([0,0,1,0,1,1,0,1,1,1,0,1,1,1,1,0,0,0,1,0,1,1,0,1,1,1])

    def interleave_57(self, subblock):
        out = np.zeros(57, dtype=int)
        for k in range(57):
            j = (49 * k) % 57
            out[j] = subblock[k]
        return out
    
    
    def process(self, bits):
        
        if not getattr(self, "is_working", True):
            return np.array.bits
        
        if len(bits) != 456:
            raise ValueError("Expected 456 bits")
        #print("Input bits:", len(bits))
        subblocks = [bits[i*57:(i+1)*57] for i in range(8)]

        if len(subblocks) != 8:
            raise ValueError("Interleaver expects 456 bits -> 8 subblocks")

        bursts_out = []

        for b in range(4):
            first_data = self.interleave_57(subblocks[b])
            second_data = self.interleave_57(subblocks[b+4])

            burst = np.concatenate([
                self.tail_bits,         # tb
                first_data,             # 57 data 
                self.st_flag,           # sb
                self.training_seq,      # ts
                second_data,            # 57 data
                self.st_flag,           # sb
                self.tail_bits,         # tb
                self.guard_bits         # gp
            ])
            bursts_out.append(burst)

        return np.concatenate(bursts_out)