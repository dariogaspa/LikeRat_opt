#!/usr/bin/env python3
import math
import random
import numpy as np
if not hasattr(np, "mat"):  # patch per compatibilità con NumPy 2.x
    np.mat = np.asmatrix
from astropy.io import fits
import ctx
from multiprocessing import Pool, cpu_count
from tqdm import tqdm

# Costanti
DEG2RAD = math.pi / 180.0
RAD2DEG = 180.0 / math.pi
DEC_LIMIT = 89.9
TWOPI = 2 * math.pi

FGL_FILE = "/Users/dariogasparrini/Documents/Likelihood_GPT/TEST_RASS_5FGL/gll_pscP305uw1617_v1_assoc_v9r0_classes.fits"

def sech2(x):
    sech = 2 / (math.exp(x) + math.exp(-x))
    return sech**2

def adjust_ra_dec(ra, dec):
    """Mantiene RA e DEC nei limiti ammessi."""
    if dec > DEC_LIMIT:
        dec = DEC_LIMIT
    elif dec < -DEC_LIMIT:
        dec = -DEC_LIMIT

    if ra < 0.0:
        ra += 360.0
    elif ra > 360.0:
        ra -= 360.0

    return ra, dec

def process_source(RA, DEC, LII, BII, b0, rmax):
    """Genera coordinate finte per una sorgente."""
    if abs(BII) >= 10:  # Alto galattico
        rad = random.uniform(1.0, 5.0)  # gradi
        theta = random.uniform(0, 359.999)
        theta_rad = theta * DEG2RAD

        RAfake = RA + rad * math.cos(theta_rad)
        DECfake = DEC + rad * math.sin(theta_rad)
        RAfake, DECfake = adjust_ra_dec(RAfake, DECfake)

        LIIfake, BIIfake = ctx.j20002gal(RAfake, DECfake)

    else:  # Basso galattico
        lii = LII * DEG2RAD
        bii = BII * DEG2RAD
        lii_fake = random.uniform(lii - 10*DEG2RAD, lii + 10*DEG2RAD)

        bmax = rmax * (1 - sech2(bii / b0))
        if bmax < 0.2 * DEG2RAD:
            bmax = 0.2 * DEG2RAD

        bii_fake = random.uniform(bii - bmax, bii + bmax)

        if lii_fake < 0.0:
            lii_fake += TWOPI
        elif lii_fake > TWOPI:
            lii_fake -= TWOPI

        RAfake, DECfake = ctx.gal2j2000(lii_fake * RAD2DEG, bii_fake * RAD2DEG)
        RAfake, DECfake = adjust_ra_dec(RAfake, DECfake)

        LIIfake, BIIfake = lii_fake * RAD2DEG, bii_fake * RAD2DEG

    return RAfake, DECfake, LIIfake, BIIfake

def generate_fake_file(run, tbdata, name, RA, DEC, LII, BII, c95sma, c95smi,c95posa, ts):
    """Genera un singolo file FITS con coordinate finte."""
    b0 = 5.0 * DEG2RAD
    rmax = 10.0 * DEG2RAD

    RAfake_arr = np.zeros(len(tbdata), dtype=float)
    DECfake_arr = np.zeros(len(tbdata), dtype=float)
    LIIfake_arr = np.zeros(len(tbdata), dtype=float)
    BIIfake_arr = np.zeros(len(tbdata), dtype=float)

    for j in range(len(tbdata)):
        RAfake, DECfake, LIIfake, BIIfake = process_source(
            RA[j], DEC[j], LII[j], BII[j], b0, rmax
        )
        RAfake_arr[j] = RAfake
        DECfake_arr[j] = DECfake
        LIIfake_arr[j] = LIIfake
        BIIfake_arr[j] = BIIfake

    cols = fits.ColDefs([
        fits.Column(name='SourceName', format='20A', array=name),
        fits.Column(name='NickName', format='20A', array=name),
        fits.Column(name='RA', format='E', array=RAfake_arr),
        fits.Column(name='DEC', format='E', array=DECfake_arr),
        fits.Column(name='GLON', format='E', array=LIIfake_arr),
        fits.Column(name='GLAT', format='E', array=BIIfake_arr),
        fits.Column(name='Conf_95_SemiMajor', format='E', array=c95sma),
        fits.Column(name='Conf_95_SemiMinor', format='E', array=c95smi),
	fits.Column(name='Conf_95_PosAng', format='E', array=c95posa),
        fits.Column(name='Signif_Avg', format='E', array=ts),
    ])

    tbhdu = fits.BinTableHDU.from_columns(cols)
    output_file = f"LACfake_fake{run}.fits"
    tbhdu.writeto(output_file, overwrite=True)
    return output_file

def main():
    # Leggi FITS una sola volta
    hdulist = fits.open(FGL_FILE)
    tbdata = hdulist[1].data

    name = tbdata["Source_Name"]
    RA = tbdata["RAJ2000"]
    DEC = tbdata["DEJ2000"]
    LII = tbdata["GLON"]
    BII = tbdata["GLAT"]
    c95sma = tbdata["Conf_95_SemiMajor"]
    c95smi = tbdata["Conf_95_SemiMinor"]
    c95posa = tbdata["Conf_95_PosAng"]
    ts = tbdata["Test_Statistic"]
    #pivotene = tbdata["Pivot_Energy"]

    common_args = (tbdata, name, RA, DEC, LII, BII, c95sma, c95smi, c95posa, ts)

    runs = range(1, 101)
    with Pool(cpu_count()) as pool:
        for _ in tqdm(
            pool.starmap(generate_fake_file, [(run, *common_args) for run in runs]),
            total=len(runs),
            desc="Generazione file FITS",
            unit="file"
        ):
            pass

if __name__ == "__main__":
    main()

