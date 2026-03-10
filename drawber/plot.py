from core.block import Block
import matplotlib.pyplot as plt
import numpy as np

def plot_ber(h2dBs, BERs, FERs, channel_type="Channel"):
    plt.figure(figsize=(8,5))
    plt.semilogy(h2dBs, BERs, 'o-', label='BER')
    plt.grid(True, which='both', linestyle='--', alpha=0.5)
    plt.xlabel('h2 [dB]')
    plt.ylabel('BER')
    plt.title(f'BER vs h2 for {channel_type}')
    plt.legend()
    plt.tight_layout()
    plt.show()
    
   # plt.figure(figsize=(8,5))
    #plt.semilogy(h2dBs, FERs, 's-', color='orange', label='FER')
    #plt.grid(True, which='both', linestyle='--', alpha=0.5)
    #plt.xlabel('h2 [dB]')
    #plt.ylabel('FER')
    #plt.title(f'FER vs h2 for {channel_type}')
    #plt.legend()
    #plt.tight_layout()
    #plt.show()