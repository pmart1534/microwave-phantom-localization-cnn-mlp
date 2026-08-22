#!/bin/bash
# Where does Aug-F5's information live? Probe the excluded regions + July's band.
MAT="C:/Program Files/MATLAB/R2025b/bin/matlab.exe"
SCRIPT="C:\Users\peter\Desktop\EM Imaging\CNN vs MLP\cnn_matlab\Imager_CNN_LOSO.m"
export CNN_LOSO_PARENT="C:\Users\peter\Desktop\EM Imaging\BreastPhantom\HunterVNA\DataMeasurements\Sam Antennas\MediumAntenna\Separated\Aug18\A3F5"
export CNN_LOSO_INPUT="raw" CNN_LOSO_HIER="0" CNN_LOSO_REFL_ONLY="0" CNN_LOSO_COMPONENT="both"
export CNN_LOSO_PORT_REMAP="" CNN_LOSO_NO_MEANSUB="" CNN_LOSO_NO_BASELINE="" CNN_LOSO_ZSCORE=""
export CNN_LOSO_INPUTNORM="" CNN_LOSO_MAGDB="" CNN_LOSO_CURVES="1" CNN_LOSO_EPOCHS="20"
export CNN_LOSO_ANT_MODE="all" CNN_LOSO_PORTS="1 2 3 4"
export CNN_LOSO_SESSIONS="1317 1341 1409" CNN_LOSO_SETLABEL="f5aug"
for B in "0.1 2" "5 8" "1 5" "0.1 5"; do
  export CNN_LOSO_BAND="$B"
  echo "### F5-PROBE [${B/ /-} GHz] ###"
  "$MAT" -batch "run('$SCRIPT')" 2>&1 | grep -E "LOSO position|rror" | head -2
done
echo "======= F5 PROBE DONE ======="
