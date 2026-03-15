import numpy as np


class ViterbiDecoder:

    def __init__(self, constraint_length, polynomials):

        self.K = constraint_length
        self.polynomials = polynomials

        self.n_outputs = len(polynomials)      # rate = 1/n
        self.n_states = 2 ** (constraint_length - 1)

        self.next_state = np.zeros((self.n_states, 2), dtype=int)
        self.output = np.zeros((self.n_states, 2), dtype=int)

        self._build_trellis()


    def _poly_to_bits(self, poly):
        bits = [(poly >> i) & 1 for i in range(self.K)]
        return bits


    def _build_trellis(self):

        poly_bits = [self._poly_to_bits(p) for p in self.polynomials]

        for state in range(self.n_states):

            reg = [(state >> i) & 1 for i in range(self.K - 1)]

            for bit in (0, 1):

                shift_reg = [bit] + reg

                out_bits = []

                for poly in poly_bits:

                    val = 0
                    for i in range(self.K):
                        if poly[i]:
                            val ^= shift_reg[i]

                    out_bits.append(val)

                out = 0
                for b in out_bits:
                    out = (out << 1) | b

                ns = ((state << 1) | bit) & (self.n_states - 1)

                self.next_state[state, bit] = ns
                self.output[state, bit] = out


    def _hamming(self, a, b):
        return (a ^ b).bit_count()


    def decode(self, coded_bits):

        n_steps = len(coded_bits) // self.n_outputs

        path_metric = np.full((n_steps + 1, self.n_states), np.inf)
        path_metric[0, 0] = 0

        prev_state = np.zeros((n_steps, self.n_states), dtype=int)
        prev_bit = np.zeros((n_steps, self.n_states), dtype=int)

        for t in range(n_steps):

            r = 0
            for i in range(self.n_outputs):
                r = (r << 1) | coded_bits[t*self.n_outputs + i]

            for state in range(self.n_states):

                if path_metric[t, state] == np.inf:
                    continue

                for bit in (0, 1):

                    ns = self.next_state[state, bit]

                    expected = self.output[state, bit]

                    metric = path_metric[t, state] + self._hamming(r, expected)

                    if metric < path_metric[t+1, ns]:

                        path_metric[t+1, ns] = metric
                        prev_state[t, ns] = state
                        prev_bit[t, ns] = bit


        state = np.argmin(path_metric[n_steps])

        decoded = []

        for t in reversed(range(n_steps)):

            bit = prev_bit[t, state]
            decoded.append(bit)

            state = prev_state[t, state]

        decoded.reverse()

        return decoded