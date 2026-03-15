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

    def calc_metric(
        self, increment, sampled_signal, start_state=0, stop_states=0, stops_num=0
    ):
        # Computation of path metrics and decisions (Add-Compare-Select).
        # It's composed of two parts: one for odd input samples (imaginary numbers)
        # and one for even samples (real numbers).
        path_metrics = np.ones(16) * -1e30
        path_metrics[start_state] = 0.0
        old_path_metrics = path_metrics
        new_path_metrics = np.zeros(16)

        trans_table = np.zeros((148, 16))

        sample_nr = 0
        samples_num = sampled_signal.size

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

    def process(self, complex_signal):

        if not getattr(self, "is_working", True):
            return np.array(complex_signal, copy=True)

        signal = np.array(complex_signal)

        # decision
        bits = (signal > 0).astype(int)
        
       # bursts = bits.reshape(-1, 156)   # 4 bursts × 156
       # bursts = bursts[:, :148]         # убираем 8 guard bits
       # bits = bursts.reshape(-1)        # обратно в поток

        return bits


class PSKDemodulator(Block):
    def __init__(self, params):
        pass

    def process(self, signal):
        raise ValueError("8-PSK Demodulator еще не реализован")
