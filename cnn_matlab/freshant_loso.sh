#!/bin/bash
# Antenna-reattach LOSO, 4-way: the 3 fresh-placement sessions (1509 1631 1703)
# + the last fresh-cal session (1258) as the pre-reattach reference fold.
# Main CNN defaults: all 16 S-params, full band.
MAT="C:/Program Files/MATLAB/R2025b/bin/matlab.exe"
SCRIPT="C:\Users\peter\Desktop\EM Imaging\CNN vs MLP\cnn_matlab\Imager_CNN_LOSO.m"
export CNN_LOSO_PARENT="C:\Users\peter\Desktop\EM Imaging\BreastPhantom\HunterVNA\DataMeasurements\Sam Antennas\MediumAntenna\Separated\Aug18"
export CNN_LOSO_EPOCHS="100"; export CNN_LOSO_INPUT="raw"; export CNN_LOSO_HIER="0"
export CNN_LOSO_ANT_MODE="all"; export CNN_LOSO_PORTS="1 2 3 4"
export CNN_LOSO_REFL_ONLY="0"; export CNN_LOSO_COMPONENT="both"
export CNN_LOSO_BAND=""; export CNN_LOSO_PORT_REMAP=""; export CNN_LOSO_NO_MEANSUB=""
export CNN_LOSO_SESSIONS="1258 1509 1631 1703"; export CNN_LOSO_SETLABEL="freshant4"
echo "### ANTENNA-REATTACH 4-WAY LOSO (1258 + 1509 1631 1703) ###"
"$MAT" -batch "run('$SCRIPT')" 2>&1 | grep -E "LOSO position|fold test|rror" | head -10
echo "======= FRESHANT DONE ======="
