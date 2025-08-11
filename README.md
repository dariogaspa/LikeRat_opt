# LikeRat_opt
This repo contains the LikeRatio method scripts for association between Fermi and low energy counterparts
# Pipeline Likelihood & Reliability – RASS/Fermi
## 1️⃣ Creazione dei Fake
Lancia lo script Python di creazione fake in modalità multi–process.
Alla fine, controlla che i file .fits fake siano stati generati.

## 2️⃣ Cross–correlazione
Modifica i path nei file script.csh per puntare a:
file RASS
file Fermi vero o fake
Esegui:
```bash
./script.csh true               # Per il VERO cielo
./script.csh fake <inizio> <fine>  # Per i cieli finti
```
Lo script crea: 
prova.fits
Immagini .png
File LR_valueXX.txt
Tabelle .fits (table_RASS_fakeXX.fits)
## 3️⃣ Organizzazione file Fake
Sposta le tabelle e i file prova nella cartella fake/:
```bash 
mv table_RASS_fake*.* fake/
mv prova*.* fake/
```
Mantieni nella dir corrente solo i LR_valueXX.txt e i .png.
## 4️⃣ Creazione istogrammi normalizzati
Il file importante qui è lr_unificato.py che calcola likelihood e reliability.
Per i fake:
Esegui run_all_LRValue.csh (chiama histo_plot.py per ogni LR_valueXX.txt)
Ottieni histo_norm_all.txt (falsi).
Per il vero:
```bash
python histo_plot.py LR_value_true.txt 200 histo_norm_true
```
Ottieni histo_norm_true.txt (veri).
## 5️⃣ Calcolo Reliability
In passato con reliability_new.cxx, ora usiamo fit_mio_migliorato.py per poter gestire manualmente lo starting point del fit.
Modifica i path in fit_mio_migliorato.py per puntare a reliability.txt generato dai due histo_norm_*.txt.

Lancia:
```bash
python fit_mio_migliorato.py
```
Osserva il plot e annota i valori di p0 e p1.
6️⃣ Aggiornamento lr_unificato.py
Apri lr_unificato.py e, nella sezione:
```python
if args.mode == "true":
    p0 = ...
    p1 = ...
```
Inserisci i nuovi valori dal fit.
7️⃣ Esecuzione finale
Lancia:
python lr_unificato.py --mode true
Verranno calcolate la likelihood e la reliability definitive con i nuovi parametri.


## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[GNU GPLv3](https://choosealicense.com/licenses/gpl-3.0/)
