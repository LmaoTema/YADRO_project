import numpy as np
from .base import Interleaver

class MCS5Interleaver(Interleaver):
    def __init__(self):
        self.training_seq = np.array([0,0,1,0,1,1,0,1,1,1,0,1,1,1,1,0,0,0,1,0,1,1,0,1,1,1], dtype=int)
        self.tail_bits = np.zeros(3, dtype=int)
        self.guard_bits = np.zeros(8, dtype=int)

    @staticmethod
    def header_interleave(header_bits):
        hi = np.zeros(136, dtype=int)
        for k in range(136):
            j = 34 * (k % 4) + 2 * ((11 * k) % 17) + ((k % 8) // 4)
            hi[j] = header_bits[k]
        return hi

    @staticmethod
    def insert_flags(block, flags, block_index):
        positions = [25, 82, 139, 424, 426, 427, 428, 429]
        start = block_index * 312
        end = start + 312
        local_positions = [p - start for p in positions if start <= p < end]
        local_flags = [flags[i] for i in range(len(local_positions))]
        for pos, val in zip(local_positions, local_flags):
            block[pos] = val
        return block

    @staticmethod
    def data_interleave(data_bits):
        bursts = [[] for _ in range(4)]
        for k in range(1248):
            B = k % 4
            d = k % 464
            j = 3 * (2 * (25 * d % 58) + ((d % 8) // 4) + 2 * ((-1)**B) * (d // 232)) + (k % 3)
            bursts[B].append((j, data_bits[k]))

        bursts_out = []
        for b in range(4):
            burst_array = np.zeros(312, dtype=int)
            for j, bit in bursts[b]:
                if j < 312:
                    burst_array[j] = bit
            bursts_out.append(burst_array)
        return bursts_out

    def process(self, block):
        header_bits = block["header"]
        data_bits = block["data"]
        flags = block["flags"]

        hi = self.header_interleave(header_bits)
        data_interleaved = self.data_interleave(data_bits)

        for b in range(4):
            data_interleaved[b] = self.insert_flags(data_interleaved[b], flags, b)

        blocks = []
        for b in range(4):
            for i in range(6):
                start = i*58
                end = start+58
                block_slice = data_interleaved[b][start:end]
                if len(block_slice) < 58:
                    block_slice = np.pad(block_slice, (0, 58-len(block_slice)), 'constant')
                blocks.append(block_slice)

        bursts = []
        for i in range(0, 24, 2): 
            burst = np.concatenate([
                self.tail_bits,      # 3
                blocks[i],           # 58
                self.training_seq,   # 26
                blocks[i+1],         # 58
                self.tail_bits,      # 3
                self.guard_bits      # 8
            ])
            bursts.append(burst)

        return np.array(bursts)  