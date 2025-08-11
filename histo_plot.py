import sys
import numpy as np
import pylab

def main():
    if len(sys.argv) < 3:
        print("Usage: python histo_plot.py <input_file.txt> <bins_number> [output_prefix]")
        sys.exit(1)

    input_file = sys.argv[1]
    bins_num = int(sys.argv[2])
    output_prefix = sys.argv[3] if len(sys.argv) > 3 else "histo_norm"

    # Leggi dati, converti in float
    with open(input_file, "r") as f:
        lines = f.readlines()

    LR = np.array([float(line.strip()) for line in lines if line.strip() != ''])

    # Filtra valori diversi da zero
    ind_logLR = LR[LR != 0]

    # Crea figura
    fig = pylab.figure(figsize=(10, 10))
    LR_hist = pylab.hist(ind_logLR, bins=bins_num, range=(-40, 20), density=True, histtype='step', color='blue', label='Fermi')

    # Salva istogramma normalizzato in txt
    with open(f"{output_prefix}.txt", 'w') as LRtxt:
        for k in range(bins_num):
            bin_edge = LR_hist[1][k]
            density_val = LR_hist[0][k]
            LRtxt.write(f"{bin_edge}  {density_val}\n")

    # Salva immagine
    pylab.savefig(f"{output_prefix}.png")
    print(f"Saved histogram and data to {output_prefix}.png and {output_prefix}.txt")

if __name__ == "__main__":
    main()

