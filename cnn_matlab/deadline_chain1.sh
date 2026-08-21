#!/bin/bash
# Deadline chain 1: audit-flagged promotions + phase-fingerprint mechanism test.
MAT="C:/Program Files/MATLAB/R2025b/bin/matlab.exe"
LOSO="C:\Users\peter\Desktop\EM Imaging\CNN vs MLP\cnn_matlab\Imager_CNN_LOSO.m"
XDAY="C:\Users\peter\Desktop\EM Imaging\CNN vs MLP\cnn_matlab\Imager_CNN_XDay.m"
SWAP="C:\Users\peter\Desktop\EM Imaging\BreastPhantom\HunterVNA\DataMeasurements\Sam Antennas\MediumAntenna\Separated\Aug18\A3_MetalTumor_SwapAntLocation"
LINKS="C:\Users\peter\AppData\Local\Temp\claude\C--Users-peter-Desktop-EM-Imaging\002574c0-5adc-4320-856a-0ed7b0a683fb\scratchpad\xday_swap_links"
base() {
  export CNN_LOSO_INPUT="raw" CNN_LOSO_HIER="0" CNN_LOSO_REFL_ONLY="0" CNN_LOSO_COMPONENT="both"
  export CNN_LOSO_BAND="" CNN_LOSO_PORT_REMAP="" CNN_LOSO_NO_MEANSUB="" CNN_LOSO_NO_BASELINE=""
  export CNN_LOSO_ZSCORE="" CNN_LOSO_INPUTNORM="" CNN_LOSO_CURVES="1" CNN_LOSO_EPOCHS="100"
  export CNN_LOSO_ANT_MODE="all" CNN_LOSO_PORTS="1 2 3 4"
}

base; export CNN_LOSO_PARENT="$SWAP" CNN_LOSO_SESSIONS="" CNN_LOSO_SETLABEL="swap4"
export CNN_LOSO_ANT_MODE="all" CNN_LOSO_REFL_ONLY="1" CNN_LOSO_BAND="2 5"
echo "### PROMOTE: swap refl4 @2-5 @100ep (was 88.78 @20) ###"
"$MAT" -batch "run('$LOSO')" 2>&1 | grep -E "LOSO position|rror" | head -2

base; export CNN_LOSO_PARENT="$SWAP" CNN_LOSO_SESSIONS="" CNN_LOSO_SETLABEL="swap4"
export CNN_LOSO_ANT_MODE="pair" CNN_LOSO_PORTS="1 3" CNN_LOSO_BAND="2 5"
echo "### PROMOTE: swap pair13 @2-5 @100ep (was 90.82 @20) ###"
"$MAT" -batch "run('$LOSO')" 2>&1 | grep -E "LOSO position|rror" | head -2

base; export CNN_LOSO_PARENT="$LINKS" CNN_LOSO_COMPONENT="mag" CNN_LOSO_CURVES=""
export CNN_XDAY_TRAIN_SESSIONS="0909 0938 1008" CNN_XDAY_TEST_SESSIONS="0856 0922 0954 1020"
export CNN_LOSO_SETLABEL="day2train-swaptest"
echo "### MECHANISM: mag-only day2-pristine -> swapped (mag+phase was 93.37) ###"
"$MAT" -batch "run('$XDAY')" 2>&1 | grep -E "test session|Cross-day|rror" | head -8
echo "======= DEADLINE CHAIN 1 DONE ======="
