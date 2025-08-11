#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from astropy.io import ascii
import matplotlib.pyplot as plt
from scipy import optimize

# === CONFIG ===
input_file = '/Users/dariogasparrini/Documents/Likelihood_GPT/TEST_RASS_5FGL/reliability.txt'
startpoint = 21  # indice da cui partire per il fit
params_output = "fit_params.txt"
plot_output = "fit_plot.png"

# === LETTURA FILE ===
f = ascii.read(input_file)
x_values = f.columns[0]
y_values = f.columns[1]

# === FUNZIONE OBIETTIVO ===
def objective(x, p0, p1):
    return (1 - p0 * (1 / np.exp(x * p1)))

# === SELEZIONE DATI PER IL FIT ===
xfit = x_values[startpoint:]
yfit = y_values[startpoint:]
print(f"Fit a partire da bin x = {x_values[startpoint]:.3f}")

# === FIT ===
popt, pcov = optimize.curve_fit(objective, xfit, yfit)
p0, p1 = popt

# === CALCOLO QUALITÀ DEL FIT ===
y_pred = objective(xfit, p0, p1)
residuals = yfit - y_pred
ss_res = np.sum(residuals**2)
ss_tot = np.sum((yfit - np.mean(yfit))**2)
r2 = 1 - (ss_res / ss_tot)
std_resid = np.std(residuals)

print(f"\n=== Risultati Fit ===")
print(f"p0 = {p0:.6f}")
print(f"p1 = {p1:.6f}")
print(f"R² = {r2:.6f}")
print(f"Deviazione standard residui = {std_resid:.6e}")

# === SALVA PARAMETRI ===
with open(params_output, "w") as f_out:
    f_out.write(f"p0 = {p0:.6f}\n")
    f_out.write(f"p1 = {p1:.6f}\n")
    f_out.write(f"R2 = {r2:.6f}\n")
    f_out.write(f"Std_resid = {std_resid:.6e}\n")

# === PLOT ===
plt.figure(figsize=(8, 6))
plt.scatter(x_values, y_values, label="Dati originali", alpha=0.7)
plt.scatter(xfit, yfit, color='orange', label="Dati usati per il fit", alpha=0.8)

x_line = np.linspace(min(xfit)-0.5, max(xfit)+0.5, 300)
y_line = objective(x_line, p0, p1)
plt.plot(x_line, y_line, '--', color='red',
         label=f'Fit: p0={p0:.3f}, p1={p1:.3f}, R²={r2:.3f}')

plt.xlabel("Bin")
plt.ylabel("Reliability")
plt.legend()
plt.grid(True)

# Salva e mostra grafico
plt.savefig(plot_output, dpi=300)
plt.show()

print(f"\nGrafico salvato in '{plot_output}'")
print(f"Parametri salvati in '{params_output}'")

