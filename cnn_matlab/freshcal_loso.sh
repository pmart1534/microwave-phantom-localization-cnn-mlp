#!/bin/bash
# Fresh-calibration metal sessions (VNA recalibrated before each session):
# main CNN LOSO, settled defaults.
MAT="C:/Program Files/MATLAB/R2025b/bin/matlab.exe"
SCRIPT="C:\Users\peter\Desktop\EM Imaging\CNN vs MLP\cnn_matlab\Imager_CNN_LOSO.m"
export CNN_LOSO_PARENT="C:\Users\peter\Desktop\EM Imaging\BreastPhantom\HunterVNA\DataMeasurements\Sam Antennas\MediumAntenna\Separated\Aug18"
export CNN_LOSO_EPOCHS="100"; export CNN_LOSO_INPUT="raw"; export CNN_LOSO_HIER="0"
export CNN_LOSO_ANT_MODE="all"; export CNN_LOSO_PORTS="1 2 3 4"
export CNN_LOSO_REFL_ONLY="0"; export CNN_LOSO_COMPONENT="both"
export CNN_LOSO_BAND=""; export CNN_LOSO_PORT_REMAP=""; export CNN_LOSO_NO_MEANSUB=""
export CNN_LOSO_SESSIONS="1103 1200 1258"; export CNN_LOSO_SETLABEL="freshcal"
echo "### FRESH-CAL METAL LOSO (sessions 1103 1200 1258) ###"
"$MAT" -batch "run('$SCRIPT')" 2>&1 | grep -E "LOSO position|fold test|rror" | head -8
echo "======= FRESHCAL DONE ======="
