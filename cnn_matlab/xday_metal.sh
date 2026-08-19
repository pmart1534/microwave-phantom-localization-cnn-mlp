#!/bin/bash
# Cross-day experiment: train ONLY on day-1 metal (Aug18: 1143 1210 1239),
# validate on day-2 metal (Aug19: 0909 0938 1008). Main CNN defaults.
MAT="C:/Program Files/MATLAB/R2025b/bin/matlab.exe"
SCRIPT="C:\Users\peter\Desktop\EM Imaging\CNN vs MLP\cnn_matlab\Imager_CNN_XDay.m"
export CNN_LOSO_PARENT="C:\Users\peter\Desktop\EM Imaging\BreastPhantom\HunterVNA\DataMeasurements\Sam Antennas\MediumAntenna\Separated\Aug18"
export CNN_LOSO_EPOCHS="100"; export CNN_LOSO_INPUT="raw"; export CNN_LOSO_HIER="0"
export CNN_LOSO_ANT_MODE="all"; export CNN_LOSO_PORTS="1 2 3 4"
export CNN_LOSO_REFL_ONLY="0"; export CNN_LOSO_COMPONENT="both"
export CNN_LOSO_BAND=""; export CNN_LOSO_PORT_REMAP=""; export CNN_LOSO_NO_MEANSUB=""
export CNN_XDAY_TRAIN_SESSIONS="1143 1210 1239"
export CNN_XDAY_TEST_SESSIONS="0909 0938 1008"
export CNN_LOSO_SETLABEL="metal-d1train-d2test"
echo "### CROSS-DAY: train day1 metal, test day2 metal ###"
"$MAT" -batch "run('$SCRIPT')" 2>&1 | grep -E "TRAIN sessions|TEST sessions|trained once|test session|Cross-day|rror" | head -20
echo "======= XDAY DONE ======="
