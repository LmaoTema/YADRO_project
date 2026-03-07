import numpy as np
import pytest
from gsm_channel_coding.tch_fs import TCHFSBlockCoder

def test_tchfs_output_length():
    coder = TCHFSBlockCoder()
    input_bits = np.random.randint(0, 2, size=260).tolist()  # TCH/FS frame 260 бит
    output_bits = coder.process(input_bits)
    
    # проверяем размерность выхода
    assert len(output_bits) == 456, f"Ожидалось 456, получили {len(output_bits)}"
    