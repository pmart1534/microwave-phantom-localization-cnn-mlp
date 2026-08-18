#!/bin/bash
# Aug18 A3 metal-tumor and beet-1cm: main CNN LOSO, settled defaults
# (raw mag+phase, all 16 S-params, full band, single-stage, 100 epochs).
MAT="C:/Program Files/MATLAB/R2025b/bin/matlab.exe"
SCRIPT="C:\Users\peter\Desktop\EM Imaging\CNN vs MLP\cnn_matlab\Imager_CNN_LOSO.m"
export CNN_LOSO_PARENT="C:\Users\peter\Desktop\EM Imaging\BreastPhantom\HunterVNA\DataMeasurements\Sam Antennas\MediumAntenna\Separated\Aug18"
export CNN_LOSO_EPOCHS="100"; export CNN_LOSO_INPUT="raw"; export CNN_LOSO_HIER="0"
export CNN_LOSO_ANT_MODE="all"; export CNN_LOSO_PORTS="1 2 3 4"
export CNN_LOSO_REFL_ONLY="0"; export CNN_LOSO_COMPONENT="both"
export CNN_LOSO_BAND=""; export CNN_LOSO_PORT_REMAP=""; export CNN_LOSO_NO_MEANSUB=""

echo "### AUG18 METAL (sessions 1143 1210 1239) ###"
export CNN_LOSO_SESSIONS="1143 1210 1239"; export CNN_LOSO_SETLABEL="metal"
"$MAT" -batch "run('$SCRIPT')" 2>&1 | grep -E "LOSO position|fold|rror" | head -8

echo "### AUG18 BEET (sessions 1334 1444 1512) ###"
export CNN_LOSO_SESSIONS="1334 1444 1512"; export CNN_LOSO_SETLABEL="beet"
"$MAT" -batch "run('$SCRIPT')" 2>&1 | grep -E "LOSO position|fold|rror" | head -8
echo "======= AUG18 LOSO DONE ======="
