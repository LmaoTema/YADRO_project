from core.block import Block
import matplotlib.pyplot as plt
import numpy as np

def plot_ber(h2dBs, BERs, FERs, channel_type="Channel"):
    plt.figure(figsize=(8,5))
    plt.semilogy(h2dBs, BERs, 'o-', label='BER')
    plt.semilogy(h2dBs, FERs, 's-', label='FER')
    plt.grid(True, which='both', linestyle='--', alpha=0.5)
    plt.xlabel('h2 [dB]')
    plt.ylabel('Error Rate')
    plt.title(f'Error Rate vs h2 for {channel_type}')
    plt.legend()
    plt.tight_layout()
    plt.show()