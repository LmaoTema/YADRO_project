import matplotlib.pyplot as plt

def plot_ber(h2dBs, results, uncoded_results=None, channel_type="Channel"):

    plt.figure(figsize=(8,5))

    # 🔹 Кодированные (по блокам)
    for name, data in results.items():
        plt.semilogy(h2dBs, data["BER"], marker='o', label=f"{name} BER")

    # 🔹 Uncoded — одна линия
    if uncoded_results is not None:
        # берём первый (и по сути единственный) блок
        first_key = list(uncoded_results.keys())[0]
        uncoded_BER = uncoded_results[first_key]["BER"]

        plt.semilogy(h2dBs, uncoded_BER, 'k--', linewidth=2, label="Uncoded BER")

    plt.grid(True, which='both', linestyle='--', alpha=0.5)
    plt.xlabel('h2 [dB]')
    plt.ylabel('BER')
    plt.title(f'BER vs h2 for {channel_type}')
    plt.legend()
    plt.tight_layout()
    plt.show()