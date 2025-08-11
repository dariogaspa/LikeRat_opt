import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# ---------------------
# Parametri input/output
# ---------------------
true_file = "histo_norm_true.txt"
all_file = "histo_norm_all.txt"
out_file = "reliability.txt"

# ---------------------
# Funzione per il fit (come in lr_unificato.py)
# ---------------------
def reliability_func(x, p0, p1):
    return 1 - p0 * np.exp(-p1 * x)

# ---------------------
# Carica i dati
# ---------------------
true_data = np.loadtxt(true_file, usecols=(0, 1))
all_data = np.loadtxt(all_file, usecols=(0, 1))

if len(true_data) != len(all_data):
    raise ValueError("I file non hanno lo stesso numero di bin!")

bins = true_data[:, 0]
true_vals = true_data[:, 1]
all_vals = all_data[:, 1]

# ---------------------
# Calcolo reliability
# ---------------------
with np.errstate(divide='ignore', invalid='ignore'):
    reliability = np.where(true_vals != 0, 1 - (all_vals / true_vals), 0)

# Salva il file
np.savetxt(out_file, np.column_stack((bins, reliability)),
           fmt="%.6f", header="bin reliability")

print(f"File salvato: {out_file}")

# ---------------------
# Fit
# ---------------------
# Considera solo i punti con reliability valida (0 < rel < 1)
mask = (reliability > 0) & (reliability < 1)
x_fit = bins[mask]
y_fit = reliability[mask]

popt, pcov = curve_fit(reliability_func, x_fit, y_fit, p0=[1, 1])
p0, p1 = popt
print(f"Fit results: p0 = {p0:.6f}, p1 = {p1:.6f}")

# ---------------------
# Plot
# ---------------------
plt.figure(figsize=(10, 6))
plt.scatter(bins, reliability, label="Dati", color='blue', s=10)
plt.plot(bins, reliability_func(bins, p0, p1), label=f"Fit: 1 - {p0:.3f} * exp(-{p1:.3f} * x)",
         color='red', linewidth=2)
plt.xlabel("Bin")
plt.ylabel("Reliability")
plt.title("Reliability e Fit")
plt.grid(True, linestyle=':')
plt.legend()
plt.tight_layout()
plt.savefig("reliability_fit.png", dpi=150)
plt.show()

