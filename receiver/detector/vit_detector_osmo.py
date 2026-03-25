import numpy as np

def calc_increment_osmo(rhh):
    # Compute Increment - a table of values which does not change for subsequent input samples.
    # Increment is table of reference levels for computation of branch metrics:
    # branch metric = (+/-)received_sample (+/-) reference_level
    # Should be like rhh[1].imag, rhh[2].real, rhh[3].imag, rhh[4].real
    increment = np.zeros(8)
    increment[0] = -rhh[1].imag - rhh[2].real - rhh[3].imag + rhh[4].real
    increment[1] = rhh[1].imag - rhh[2].real - rhh[3].imag + rhh[4].real
    increment[2] = -rhh[1].imag + rhh[2].real - rhh[3].imag + rhh[4].real
    increment[3] = rhh[1].imag + rhh[2].real - rhh[3].imag + rhh[4].real
    increment[4] = -rhh[1].imag - rhh[2].real + rhh[3].imag + rhh[4].real
    increment[5] = rhh[1].imag - rhh[2].real + rhh[3].imag + rhh[4].real
    increment[6] = -rhh[1].imag + rhh[2].real + rhh[3].imag + rhh[4].real
    increment[7] = rhh[1].imag + rhh[2].real + rhh[3].imag + rhh[4].real

    return increment

def calc_metric_osmo(increment, sampled_signal, start_state=0):
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

        sample_nr += 1

    return trans_table, old_path_metrics, real_imag

def find_best_stop_state_osmo(old_path_metrics, stop_states=[0, 8]):
    best_stop_state = stop_states[0]
    max_stop_state_metric = old_path_metrics[best_stop_state]
    for s in stop_states:
        if old_path_metrics[s] > max_stop_state_metric:
            max_stop_state_metric = old_path_metrics[s]
            best_stop_state = s

    return best_stop_state

def traceback_osmo(trans_table, best_stop_state, real_imag, type_decision):
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
        state_nr = int(prev_table[state_nr][decision])
        real_imag = 1 - real_imag

    return output_bits