import numpy as np
import sys
from core.block import Block


class Demodulation(Block):

    def __init__(self, scheme, params, is_working=True):
        super().__init__(is_working)

        if scheme in ["TCHFS", "CS1", "MCS1"]:

            self.demodulator = GMSKDemodulator(params)

        elif scheme == "MCS5":

            self.demodulator = PSKDemodulator(params)

        else:

            raise ValueError("Unknown scheme")

    def _process(self, signal):

        return self.demodulator.process(signal)


class GMSKDemodulator(Block):
    def __init__(self, params):
        self.BT = params.get("BT", 0.3)
        self.T = params.get("T", 1)
        self.sps = params.get("sps", 100)
        self.dt = self.T / self.sps
        self.gaus_duration = params.get("gaus_duration", 4)
        self.rect_duration = params.get("rect_duration", 1)
        self.type_demod = params.get("type_demod", "diff_phase")

    def gmsk_filter(self):
        BT = self.BT
        T = self.T
        dt = self.dt
        gaus_duration = self.gaus_duration
        rect_duration = self.rect_duration

        delta = np.sqrt(np.log(2)) / (2 * np.pi * BT)

        t_h = np.arange(-gaus_duration / 2 * T, gaus_duration / 2 * T, dt)
        t_rect = np.arange(-rect_duration / 2 * T, rect_duration / 2 * T, dt)

        h_t = np.exp(-(t_h**2) / (2 * (delta**2) * (T**2))) / (
            np.sqrt(2 * np.pi) * delta * T
        )
        rect = np.ones(t_rect.size) / T

        g_t = np.convolve(h_t, rect) * dt

        return g_t

    def calc_rhh(self, g_t):
        # In general, rhh should be defined in the TSC
        dt = self.dt
        sps = self.sps
        gaus_duration = self.gaus_duration
        rect_duration = self.rect_duration

        rhh_full = np.convolve(g_t, g_t[::-1]) * dt
        center_idx = int(rhh_full.size / 2)

        rhh = np.zeros(5, dtype=complex)
        for k in range(5):
            rhh[k] = rhh_full[center_idx + k * sps]

        rhh /= rhh[0].real

        return rhh

    def calc_increment(self, rhh):
        # Compute Increment - a table of values which does not change for subsequent input samples.
        # Increment is table of reference levels for computation of branch metrics:
        # branch metric = (+/-)received_sample (+/-) reference_level
        # Should be like rhh[1].imag, rhh[2].real, rhh[3].imag, rhh[4].real
        increment = np.zeros(8)
        increment[0] = -rhh[1] - rhh[2] - rhh[3] + rhh[4]
        increment[1] = rhh[1] - rhh[2] - rhh[3] + rhh[4]
        increment[2] = -rhh[1] + rhh[2] - rhh[3] + rhh[4]
        increment[3] = rhh[1] + rhh[2] - rhh[3] + rhh[4]
        increment[4] = -rhh[1] - rhh[2] + rhh[3] + rhh[4]
        increment[5] = rhh[1] - rhh[2] + rhh[3] + rhh[4]
        increment[6] = -rhh[1] + rhh[2] + rhh[3] + rhh[4]
        increment[7] = rhh[1] + rhh[2] + rhh[3] + rhh[4]

        return increment

    def calc_metric(self, increment, sampled_signal, start_state=0):
        # Computation of path metrics and decisions (Add-Compare-Select).
        # It's composed of two parts: one for odd input samples (imaginary numbers)
        # and one for even samples (real numbers).
        old_path_metrics = np.ones(16) * -1e30
        old_path_metrics[start_state] = 0.0
        new_path_metrics = np.zeros(16)

        samples_num = sampled_signal.size

        trans_table = np.zeros((samples_num, 16))

        sample_nr = 0
        

        while sample_nr < samples_num:
            # imag part
            real_imag = 1
            input_symbol_imag = sampled_signal[sample_nr].imag

            pm_candidate1 = old_path_metrics[0] + input_symbol_imag - increment[2]
            pm_candidate2 = old_path_metrics[8] + input_symbol_imag + increment[5]
            paths_difference = pm_candidate2 - pm_candidate1
            if paths_difference < 0:
                new_path_metrics[0] = pm_candidate1
            else:
                new_path_metrics[0] = pm_candidate2
            trans_table[sample_nr][0] = paths_difference

            pm_candidate1 = old_path_metrics[0] - input_symbol_imag + increment[2]
            pm_candidate2 = old_path_metrics[8] - input_symbol_imag - increment[5]
            paths_difference = pm_candidate2 - pm_candidate1
            if paths_difference < 0:
                new_path_metrics[1] = pm_candidate1
            else:
                new_path_metrics[1] = pm_candidate2
            trans_table[sample_nr][1] = paths_difference

            pm_candidate1 = old_path_metrics[1] + input_symbol_imag - increment[3]
            pm_candidate2 = old_path_metrics[9] + input_symbol_imag + increment[4]
            paths_difference = pm_candidate2 - pm_candidate1
            if paths_difference < 0:
                new_path_metrics[2] = pm_candidate1
            else:
                new_path_metrics[2] = pm_candidate2
            trans_table[sample_nr][2] = paths_difference

            pm_candidate1 = old_path_metrics[1] - input_symbol_imag + increment[3]
            pm_candidate2 = old_path_metrics[9] - input_symbol_imag - increment[4]
            paths_difference = pm_candidate2 - pm_candidate1
            if paths_difference < 0:
                new_path_metrics[3] = pm_candidate1
            else:
                new_path_metrics[3] = pm_candidate2
            trans_table[sample_nr][3] = paths_difference

            pm_candidate1 = old_path_metrics[2] + input_symbol_imag - increment[0]
            pm_candidate2 = old_path_metrics[10] + input_symbol_imag + increment[7]
            paths_difference = pm_candidate2 - pm_candidate1
            if paths_difference < 0:
                new_path_metrics[4] = pm_candidate1
            else:
                new_path_metrics[4] = pm_candidate2
            trans_table[sample_nr][4] = paths_difference

            pm_candidate1 = old_path_metrics[2] - input_symbol_imag + increment[0]
            pm_candidate2 = old_path_metrics[10] - input_symbol_imag - increment[7]
            paths_difference = pm_candidate2 - pm_candidate1
            if paths_difference < 0:
                new_path_metrics[5] = pm_candidate1
            else:
                new_path_metrics[5] = pm_candidate2
            trans_table[sample_nr][5] = paths_difference

            pm_candidate1 = old_path_metrics[3] + input_symbol_imag - increment[1]
            pm_candidate2 = old_path_metrics[11] + input_symbol_imag + increment[6]
            paths_difference = pm_candidate2 - pm_candidate1
            if paths_difference < 0:
                new_path_metrics[6] = pm_candidate1
            else:
                new_path_metrics[6] = pm_candidate2
            trans_table[sample_nr][6] = paths_difference

            pm_candidate1 = old_path_metrics[3] - input_symbol_imag + increment[1]
            pm_candidate2 = old_path_metrics[11] - input_symbol_imag - increment[6]
            paths_difference = pm_candidate2 - pm_candidate1
            if paths_difference < 0:
                new_path_metrics[7] = pm_candidate1
            else:
                new_path_metrics[7] = pm_candidate2
            trans_table[sample_nr][7] = paths_difference

            pm_candidate1 = old_path_metrics[4] + input_symbol_imag - increment[6]
            pm_candidate2 = old_path_metrics[12] + input_symbol_imag + increment[1]
            paths_difference = pm_candidate2 - pm_candidate1
            if paths_difference < 0:
                new_path_metrics[8] = pm_candidate1
            else:
                new_path_metrics[8] = pm_candidate2
            trans_table[sample_nr][8] = paths_difference

            pm_candidate1 = old_path_metrics[4] - input_symbol_imag + increment[6]
            pm_candidate2 = old_path_metrics[12] - input_symbol_imag - increment[1]
            paths_difference = pm_candidate2 - pm_candidate1
            if paths_difference < 0:
                new_path_metrics[9] = pm_candidate1
            else:
                new_path_metrics[9] = pm_candidate2
            trans_table[sample_nr][9] = paths_difference

            pm_candidate1 = old_path_metrics[5] + input_symbol_imag - increment[7]
            pm_candidate2 = old_path_metrics[13] + input_symbol_imag + increment[0]
            paths_difference = pm_candidate2 - pm_candidate1
            if paths_difference < 0:
                new_path_metrics[10] = pm_candidate1
            else:
                new_path_metrics[10] = pm_candidate2
            trans_table[sample_nr][10] = paths_difference

            pm_candidate1 = old_path_metrics[5] - input_symbol_imag + increment[7]
            pm_candidate2 = old_path_metrics[13] - input_symbol_imag - increment[0]
            paths_difference = pm_candidate2 - pm_candidate1
            if paths_difference < 0:
                new_path_metrics[11] = pm_candidate1
            else:
                new_path_metrics[11] = pm_candidate2
            trans_table[sample_nr][11] = paths_difference

            pm_candidate1 = old_path_metrics[6] + input_symbol_imag - increment[4]
            pm_candidate2 = old_path_metrics[14] + input_symbol_imag + increment[3]
            paths_difference = pm_candidate2 - pm_candidate1
            if paths_difference < 0:
                new_path_metrics[12] = pm_candidate1
            else:
                new_path_metrics[12] = pm_candidate2
            trans_table[sample_nr][12] = paths_difference

            pm_candidate1 = old_path_metrics[6] - input_symbol_imag + increment[4]
            pm_candidate2 = old_path_metrics[14] - input_symbol_imag - increment[3]
            paths_difference = pm_candidate2 - pm_candidate1
            if paths_difference < 0:
                new_path_metrics[13] = pm_candidate1
            else:
                new_path_metrics[13] = pm_candidate2
            trans_table[sample_nr][13] = paths_difference

            pm_candidate1 = old_path_metrics[7] + input_symbol_imag - increment[5]
            pm_candidate2 = old_path_metrics[15] + input_symbol_imag + increment[2]
            paths_difference = pm_candidate2 - pm_candidate1
            if paths_difference < 0:
                new_path_metrics[14] = pm_candidate1
            else:
                new_path_metrics[14] = pm_candidate2
            trans_table[sample_nr][14] = paths_difference

            pm_candidate1 = old_path_metrics[7] - input_symbol_imag + increment[5]
            pm_candidate2 = old_path_metrics[15] - input_symbol_imag - increment[2]
            paths_difference = pm_candidate2 - pm_candidate1
            if paths_difference < 0:
                new_path_metrics[15] = pm_candidate1
            else:
                new_path_metrics[15] = pm_candidate2
            trans_table[sample_nr][15] = paths_difference

            tmp = old_path_metrics
            old_path_metrics = new_path_metrics
            new_path_metrics = tmp

            sample_nr += 1
            if sample_nr == samples_num:
                break

            # real part
            real_imag = 0
            input_symbol_real = sampled_signal[sample_nr].real

            pm_candidate1 = old_path_metrics[0] - input_symbol_real - increment[7]
            pm_candidate2 = old_path_metrics[8] - input_symbol_real + increment[0]
            paths_difference = pm_candidate2 - pm_candidate1
            if paths_difference < 0:
                new_path_metrics[0] = pm_candidate1
            else:
                new_path_metrics[0] = pm_candidate2
            trans_table[sample_nr][0] = paths_difference

            pm_candidate1 = old_path_metrics[0] + input_symbol_real + increment[7]
            pm_candidate2 = old_path_metrics[8] + input_symbol_real - increment[0]
            paths_difference = pm_candidate2 - pm_candidate1
            if paths_difference < 0:
                new_path_metrics[1] = pm_candidate1
            else:
                new_path_metrics[1] = pm_candidate2
            trans_table[sample_nr][1] = paths_difference

            pm_candidate1 = old_path_metrics[1] - input_symbol_real - increment[6]
            pm_candidate2 = old_path_metrics[9] - input_symbol_real + increment[1]
            paths_difference = pm_candidate2 - pm_candidate1
            if paths_difference < 0:
                new_path_metrics[2] = pm_candidate1
            else:
                new_path_metrics[2] = pm_candidate2
            trans_table[sample_nr][2] = paths_difference

            pm_candidate1 = old_path_metrics[1] + input_symbol_real + increment[6]
            pm_candidate2 = old_path_metrics[9] + input_symbol_real - increment[1]
            paths_difference = pm_candidate2 - pm_candidate1
            if paths_difference < 0:
                new_path_metrics[3] = pm_candidate1
            else:
                new_path_metrics[3] = pm_candidate2
            trans_table[sample_nr][3] = paths_difference

            pm_candidate1 = old_path_metrics[2] - input_symbol_real - increment[5]
            pm_candidate2 = old_path_metrics[10] - input_symbol_real + increment[2]
            paths_difference = pm_candidate2 - pm_candidate1
            if paths_difference < 0:
                new_path_metrics[4] = pm_candidate1
            else:
                new_path_metrics[4] = pm_candidate2
            trans_table[sample_nr][4] = paths_difference

            pm_candidate1 = old_path_metrics[2] + input_symbol_real + increment[5]
            pm_candidate2 = old_path_metrics[10] + input_symbol_real - increment[2]
            paths_difference = pm_candidate2 - pm_candidate1
            if paths_difference < 0:
                new_path_metrics[5] = pm_candidate1
            else:
                new_path_metrics[5] = pm_candidate2
            trans_table[sample_nr][5] = paths_difference

            pm_candidate1 = old_path_metrics[3] - input_symbol_real - increment[4]
            pm_candidate2 = old_path_metrics[11] - input_symbol_real + increment[3]
            paths_difference = pm_candidate2 - pm_candidate1
            if paths_difference < 0:
                new_path_metrics[6] = pm_candidate1
            else:
                new_path_metrics[6] = pm_candidate2
            trans_table[sample_nr][6] = paths_difference

            pm_candidate1 = old_path_metrics[3] + input_symbol_real + increment[4]
            pm_candidate2 = old_path_metrics[11] + input_symbol_real - increment[3]
            paths_difference = pm_candidate2 - pm_candidate1
            if paths_difference < 0:
                new_path_metrics[7] = pm_candidate1
            else:
                new_path_metrics[7] = pm_candidate2
            trans_table[sample_nr][7] = paths_difference

            pm_candidate1 = old_path_metrics[4] - input_symbol_real - increment[3]
            pm_candidate2 = old_path_metrics[12] - input_symbol_real + increment[4]
            paths_difference = pm_candidate2 - pm_candidate1
            if paths_difference < 0:
                new_path_metrics[8] = pm_candidate1
            else:
                new_path_metrics[8] = pm_candidate2
            trans_table[sample_nr][8] = paths_difference

            pm_candidate1 = old_path_metrics[4] + input_symbol_real + increment[3]
            pm_candidate2 = old_path_metrics[12] + input_symbol_real - increment[4]
            paths_difference = pm_candidate2 - pm_candidate1
            if paths_difference < 0:
                new_path_metrics[9] = pm_candidate1
            else:
                new_path_metrics[9] = pm_candidate2
            trans_table[sample_nr][9] = paths_difference

            pm_candidate1 = old_path_metrics[5] - input_symbol_real - increment[2]
            pm_candidate2 = old_path_metrics[13] - input_symbol_real + increment[5]
            paths_difference = pm_candidate2 - pm_candidate1
            if paths_difference < 0:
                new_path_metrics[10] = pm_candidate1
            else:
                new_path_metrics[10] = pm_candidate2
            trans_table[sample_nr][10] = paths_difference

            pm_candidate1 = old_path_metrics[5] + input_symbol_real + increment[2]
            pm_candidate2 = old_path_metrics[13] + input_symbol_real - increment[5]
            paths_difference = pm_candidate2 - pm_candidate1
            if paths_difference < 0:
                new_path_metrics[11] = pm_candidate1
            else:
                new_path_metrics[11] = pm_candidate2
            trans_table[sample_nr][11] = paths_difference

            pm_candidate1 = old_path_metrics[6] - input_symbol_real - increment[1]
            pm_candidate2 = old_path_metrics[14] - input_symbol_real + increment[6]
            paths_difference = pm_candidate2 - pm_candidate1
            if paths_difference < 0:
                new_path_metrics[12] = pm_candidate1
            else:
                new_path_metrics[12] = pm_candidate2
            trans_table[sample_nr][12] = paths_difference

            pm_candidate1 = old_path_metrics[6] + input_symbol_real + increment[1]
            pm_candidate2 = old_path_metrics[14] + input_symbol_real - increment[6]
            paths_difference = pm_candidate2 - pm_candidate1
            if paths_difference < 0:
                new_path_metrics[13] = pm_candidate1
            else:
                new_path_metrics[13] = pm_candidate2
            trans_table[sample_nr][13] = paths_difference

            pm_candidate1 = old_path_metrics[7] - input_symbol_real - increment[0]
            pm_candidate2 = old_path_metrics[15] - input_symbol_real + increment[7]
            paths_difference = pm_candidate2 - pm_candidate1
            if paths_difference < 0:
                new_path_metrics[14] = pm_candidate1
            else:
                new_path_metrics[14] = pm_candidate2
            trans_table[sample_nr][14] = paths_difference

            pm_candidate1 = old_path_metrics[7] + input_symbol_real + increment[0]
            pm_candidate2 = old_path_metrics[15] + input_symbol_real - increment[7]
            paths_difference = pm_candidate2 - pm_candidate1
            if paths_difference < 0:
                new_path_metrics[15] = pm_candidate1
            else:
                new_path_metrics[15] = pm_candidate2
            trans_table[sample_nr][15] = paths_difference

            tmp = old_path_metrics
            old_path_metrics = new_path_metrics
            new_path_metrics = tmp

        return trans_table, old_path_metrics, real_imag
    
    def find_best_stop_state(self, old_path_metrics, stop_states=[0, 8]):
        best_stop_state = stop_states[0]
        max_stop_state_metric = old_path_metrics[best_stop_state]
        for s in stop_states:
            if old_path_metrics[s] > max_stop_state_metric:
                max_stop_state_metric = old_path_metrics[s]
                best_stop_state = s

        return best_stop_state
    
    def traceback(self, trans_table, best_stop_state, real_imag, type_decision):
        num_samples = trans_table.shape[0]
        
        parity_table = np.array([0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0])
        
        prev_table = np.array([
            [0, 8], [0, 8],
            [1, 9], [1, 9],
            [2, 10], [2, 10],
            [3, 11], [3, 11],
            [4, 12], [4, 12],
            [5, 13], [5, 13],
            [6, 14], [6, 14],
            [7, 15], [7, 15]
        ])

        if type_decision == "vit_soft":
            output_bits = np.zeros(num_samples, dtype=float)
        elif type_decision == "vit_hard":
            output_bits = np.zeros(num_samples, dtype=int)
        else:
            raise ValueError("Неверный тип принятия решения")
        
        sample_nr = num_samples
        state_nr = best_stop_state
        out_bit = 1

        while (sample_nr > 0):
            sample_nr -= 1
            if (trans_table[sample_nr][state_nr] > 0):
                decision = 1
            else:
                decision = 0

            if type_decision == "vit_soft":
                if (decision != out_bit):
                    output_bits[sample_nr] = -trans_table[sample_nr][state_nr]
                else:
                    output_bits[sample_nr] = trans_table[sample_nr][state_nr]
            elif type_decision == "vit_hard":
                if (decision != out_bit):
                    output_bits[sample_nr] = 1
                else:
                    output_bits[sample_nr] = 0
            

            out_bit = out_bit ^ real_imag ^ int(parity_table[state_nr])
            state_nr = prev_table[state_nr][decision]
            real_imag = not real_imag

        return output_bits

    def process(self, complex_signal):

        if not getattr(self, "is_working", True):
            return np.array(complex_signal, copy=True)

        sps = self.sps
        samples_per_burst = 156 * sps
        num_bursts = len(complex_signal) // samples_per_burst
    
        all_bits = []

        if self.type_demod in ["vit_soft", "vit_hard"]:
            g_t = self.gmsk_filter()
            rhh = self.calc_rhh(g_t)
            increment = self.calc_increment(rhh)

        for b in range(num_bursts):

            start_idx = b * samples_per_burst
            burst_samples = complex_signal[start_idx : start_idx + 148 * sps]

            if self.type_demod == "diff_phase":

                y_k = burst_samples[int(self.sps / 2) :: self.sps]

                y_k_prev = np.zeros(y_k.size, dtype=complex)
                y_k_prev[1:] = y_k[:-1]
                y_k_prev[0] = 1 + 0j

                delta_phi = np.angle(y_k * np.conj(y_k_prev))

                alpha = np.ones(delta_phi.size)
                alpha[delta_phi <= 0] = -1

                d_curr = ((1 - alpha) / 2).astype(int)

                burst_bits = np.zeros(d_curr.size, dtype=int)
                d_prev = 1
                for i in range(d_curr.size):
                    burst_bits[i] = d_curr[i] ^ d_prev
                    d_prev = burst_bits[i]

                all_bits.append(burst_bits)

            elif self.type_demod in ["vit_soft", "vit_hard"]:

                sampled_signal = burst_samples[int(self.sps / 2) :: self.sps]
                trans_table, old_path_metrics, real_imag = self.calc_metric(increment, sampled_signal, start_state=0)

                best_stop_state = self.find_best_stop_state(old_path_metrics)

                burst_bits = self.traceback(trans_table, best_stop_state, real_imag, self.type_demod)

                all_bits.append(burst_bits)
                
        bits = np.concatenate(all_bits)
        return bits


class PSKDemodulator(Block):
    def __init__(self, params):
        pass

    def process(self, signal):
        raise ValueError("8-PSK Demodulator еще не реализован")
