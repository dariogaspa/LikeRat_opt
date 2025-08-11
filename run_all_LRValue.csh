#!/bin/csh

# Rimuovo file di output se già esiste
rm -f LR_value_all.txt

# Concateno tutti i file LR_value*.txt ordinati in un unico file
cat `ls LR_value*.txt | sort -V` > LR_value_all.txt

# Eseguo lo script python con LR_value_all.txt e bins=200, output file base "histo_norm_all"
python histo_plot.py LR_value_all.txt 200 histo_norm_all
