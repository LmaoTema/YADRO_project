import numpy as np
from core.block import Block


class Interleaver(Block):

    def __init__(self):

        self.permutation = self._build_table()


    def _build_table(self):

        table = []

        for k in range(456):

            B = (k % 4)
            j = (2*((49*k) % 57) + ((k % 8)//4))

            table.append((B,j))

        return table


    def process(self, bits):

        bursts = [[0]*114 for _ in range(4)]

        for k,b in enumerate(bits):

            B,j = self.permutation[k]
            bursts[B][j] = b

        return bursts