#!/bin/csh

if ($#argv < 1) then
    echo "Uso: $0 true"
    echo "     $0 fake <inizio> <fine>"
    exit 1
endif

set mode = $1

if ($mode == "true") then
    /Applications/TOPCAT.app/Contents/Resources/app/stilts -memgui tmatch2 \
    #./dario_stilts -memgui tmatch2 \
        /Users/dariogasparrini/Documents/Likelihood_GPT/TEST_RASS_5FGL/nvrasstest.fits \
        /Users/dariogasparrini/Documents/Likelihood_GPT/TEST_RASS_5FGL/gll_pscP305uw1617_v1_assoc_v9r0_classes.fits \
        out=/Users/dariogasparrini/Documents/Likelihood_GPT/TEST_RASS_5FGL/rass_5FGL.fits \
        matcher=sky values1="ra dec" values2="RAJ2000 DEJ2000" \
        params="2700" find=all suffix1=_nvss suffix2=_fermi

    #python Likelihood_ratio_rasstrue_new.py true   #file diversi
    python lr_unificato.py --mode true

else if ($mode == "fake") then
    if ($#argv != 3) then
        echo "Uso per fake: $0 fake <inizio> <fine>"
        exit 1
    endif
    set start = $2
    set end = $3

    @ n = $start
    while ($n <= $end)
       /Applications/TOPCAT.app/Contents/Resources/app/stilts -memgui tmatch2 \
        #./dario_stilts -memgui tmatch2 \
            /Users/dariogasparrini/Documents/Likelihood_GPT/TEST_RASS_5FGL/nvrasstest.fits \
            /Users/dariogasparrini/Documents/Likelihood_GPT/TEST_RASS_5FGL/fake/LACfake_fake$n.fits \
            out=/Users/dariogasparrini/Documents/Likelihood_GPT/TEST_RASS_5FGL/prova_$n.fits \
            matcher=sky values1="ra dec" values2="ra dec" \
            params="2700" find=all suffix1=_nvss suffix2=_fermi

        #python Likelihood_ratio_rassfake.py $n #file diversi
        python lr_unificato.py --mode fake --num $n
        @ n++
    end
else
    echo "Modalità non riconosciuta: $mode"
    exit 1
endif
