#!/bin/bash
# Antenna-reattach 4-way LOSO x the 3 reduced configs (2-5 GHz).
MAT="C:/Program Files/MATLAB/R2025b/bin/matlab.exe"
SCRIPT="C:\Users\peter\Desktop\EM Imaging\CNN vs MLP\cnn_matlab\Imager_CNN_LOSO.m"
RES="C:/Users/peter/Desktop/EM Imaging/CNN vs MLP/results"
export CNN_LOSO_PARENT="C:\Users\peter\Desktop\EM Imaging\BreastPhantom\HunterVNA\DataMeasurements\Sam Antennas\MediumAntenna\Separated\Aug18"
export CNN_LOSO_EPOCHS="100"; export CNN_LOSO_INPUT="raw"; export CNN_LOSO_HIER="0"
export CNN_LOSO_COMPONENT="both"; export CNN_LOSO_PORT_REMAP=""; export CNN_LOSO_NO_MEANSUB=""
export CNN_LOSO_SESSIONS="1258 1509 1631 1703"; export CNN_LOSO_SETLABEL="freshant4"

CF_desc=("all16 @2-5" "refl-all4 @2-5" "pair13 @2-5")
CF_mode=(all all pair)
CF_ports=("1 2 3 4" "1 2 3 4" "1 3")
CF_refl=(0 1 0)
CF_tag=("all_ant1-2-3-4_band2-5" "refl_ant1-2-3-4_band2-5" "pair_ant1-3_band2-5")

for c in 0 1 2; do
  J="$RES/cnn_loso_Aug18_freshant4_raw_${CF_tag[$c]}.json"
  if [ -f "$J" ]; then echo "--- reuse freshant4 ${CF_desc[$c]}"; continue; fi
  export CNN_LOSO_ANT_MODE="${CF_mode[$c]}"; export CNN_LOSO_PORTS="${CF_ports[$c]}"
  export CNN_LOSO_REFL_ONLY="${CF_refl[$c]}"; export CNN_LOSO_BAND="2 5"
  echo "### FRESHANT-REDUCED [${CF_desc[$c]}] ###"
  "$MAT" -batch "run('$SCRIPT')" 2>&1 | grep -E "LOSO position|rror" | head -2
done
echo "======= FRESHANT-REDUCED DONE ======="
