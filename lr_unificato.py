import os
import sys
import argparse
import numpy as np
from astropy.io import fits
from astropy.coordinates import SkyCoord
from matplotlib import pylab as plt
from math import sqrt, exp, log10, pow, pi

# --------------------------
# Parse argomenti
# --------------------------
parser = argparse.ArgumentParser(description="Calcolo LR per RASS / Fake")
parser.add_argument("--mode", choices=["true", "fake"], required=True, help="Modalità: true o fake")
parser.add_argument("--num", type=int, help="Numero del file fake (richiesto se mode=fake)")
args = parser.parse_args()

if args.mode == "fake" and args.num is None:
    parser.error("--num è richiesto in modalità fake")

# --------------------------
# File input/output
# --------------------------
if args.mode == "true":
    input_file = "rass_5FGL.fits"
    output_table = "table_RASS_4FHL.fits"
    num_str = "true"
else:
    input_file = f"prova_{args.num}.fits"
    output_table = f"table_RASS_fake{args.num}.fits"
    num_str = str(args.num)

LRtxt = open(f"LR_norm{num_str}.txt", 'w')
LRvalue = open(f"LR_value{num_str}.txt", 'w')

# --------------------------
# Lettura dati
# --------------------------
hdulist = fits.open(input_file)
tbdata = hdulist[1].data
print(input_file)
n = len(tbdata)
logLR = np.zeros(n, float)
LR = np.zeros(n, float)
rg_match = np.zeros(n, float)
dist = np.zeros(n, float)
area = np.zeros(n, float)
error_radius_planck = np.zeros(n, float)

if args.mode == "true":
    rel = np.zeros(n, float)

# --------------------------
# Colonne base (nomi cambiano in true/fake)
# --------------------------
if args.mode == "true":
    ra_nvss = tbdata.field('RA')
    dec_nvss = tbdata.field('DEC')
    ra_planck = tbdata.field('RAJ2000')
    dec_planck = tbdata.field('DEJ2000')
    flux_nvss = tbdata.field('FX')
    error_radius_nvss = tbdata.field('POS_ERR')
    name_planck = tbdata.field('Source_name')
    name_nvss = tbdata.field('NAME')
else:
    ra_nvss = tbdata.field('RA_nvss')
    dec_nvss = tbdata.field('DEC_nvss')
    ra_planck = tbdata.field('RA_fermi')
    dec_planck = tbdata.field('DEC_fermi')
    flux_nvss = tbdata.field('FX')
    error_radius_nvss = tbdata.field('POS_ERR')
    # nomi dummy
    name_planck = np.array(["fake"] * n)
    name_nvss = np.array(["fake"] * n)

# --------------------------
# Raggi di errore
# --------------------------
error_radius_fermi_sma2s = tbdata.field('Conf_95_SemiMajor') / 2.4477
error_radius_fermi_smi2s = tbdata.field('Conf_95_SemiMinor') / 2.4477

# --------------------------
# Calcolo LR
# --------------------------
c = SkyCoord(ra_nvss, dec_nvss, unit="deg")
c1 = SkyCoord(ra_planck, dec_planck, unit="deg")

lognlogs = np.zeros(n, float)
lognlos_slope = np.zeros(n, float)
expected = np.zeros(n, float)
norm = 82.91875

for k in range(n):
    error_radius_planck[k] = sqrt(error_radius_fermi_sma2s[k] * error_radius_fermi_smi2s[k])
    dist[k] = c[k].separation(c1[k]).arcmin
    rg_match[k] = dist[k] / sqrt(pow(error_radius_planck[k] * 60.0, 2) + pow(error_radius_nvss[k] / 60.0, 2))
    if rg_match[k] > 12.0:
        rg_match[k] = 12.0
    area[k] = pi * error_radius_fermi_sma2s[k] * error_radius_fermi_smi2s[k]
    lognlos_slope[k] = -1.37411
    lognlogs[k] = norm * pow((flux_nvss[k] / 1.38e-14), lognlos_slope[k])

    expected[k] = lognlogs[k] * area[k]
    LR[k] = exp(-pow(rg_match[k], 2.) / 2.) / expected[k]
    logLR[k] = log10(LR[k])

    if args.mode == "true":
	 # Parametri hardcoded
        p0 = 9.28532386198732
        p1 = 1.237937226702223
        rel[k] = (1 - p0 * (1 / exp(logLR[k] * p1)))

# --------------------------
# Istogramma LR
# --------------------------
logLR_nz = logLR != 0
ind_logLR = logLR[logLR_nz]
fig1 = plt.figure(figsize=(10, 10))
LR_hist = plt.hist(ind_logLR, bins=200, range=(-30, 10), density=True, histtype='step')

for k in range(200):
    LRtxt.write(f"{LR_hist[1][k]}  {LR_hist[0][k]}\n")

for k in range(n):
    LRvalue.write(f"{logLR[k]}\n")

plt.savefig(f"LR{num_str}.png")

# --------------------------
# Salvataggio FITS di output
# --------------------------
cols = [
    fits.Column(name='Fermi_name', format='20A', array=name_planck),
    fits.Column(name='RA_Xradio', format='E', array=ra_nvss),
    fits.Column(name='DEC_Xradio', format='E', array=dec_nvss),
    fits.Column(name='Pos_err_X', format='E', array=error_radius_nvss),
    fits.Column(name='Flux_X', format='E', array=flux_nvss),
    fits.Column(name='LR', format='E', array=logLR),
    fits.Column(name='rg_match', format='E', array=rg_match),
    fits.Column(name='area', format='E', array=area),
    fits.Column(name='dista', format='E', array=dist)
]

if args.mode == "true":
    cols.append(fits.Column(name='rel', format='E', array=rel))

cols.append(fits.Column(name='RASS_Name', format='20A', array=name_nvss))

tbhdu = fits.BinTableHDU.from_columns(fits.ColDefs(cols))
tbhdu.writeto(output_table, overwrite=True)

print(f"✅ Elaborazione completata. File salvato: {output_table}")
