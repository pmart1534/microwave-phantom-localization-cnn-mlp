#!/bin/bash
# Aug18/19 datasets x 3 reduced configs:
#   A) all 16 S-params, 2-5 GHz
#   B) reflection-only, all 4 antennas, full band
#   C) full S of antenna pair 1&3, full band
MAT="C:/Program Files/MATLAB/R2025b/bin/matlab.exe"
SCRIPT="C:\Users\peter\Desktop\EM Imaging\CNN vs MLP\cnn_matlab\Imager_CNN_LOSO.m"
PY="C:/Users/peter/Desktop/EM Imaging/Above 95 Percent/venv/Scripts/python.exe"
RES="C:/Users/peter/Desktop/EM Imaging/CNN vs MLP/results"
export CNN_LOSO_PARENT="C:\Users\peter\Desktop\EM Imaging\BreastPhantom\HunterVNA\DataMeasurements\Sam Antennas\MediumAntenna\Separated\Aug18"
export CNN_LOSO_EPOCHS="100"; export CNN_LOSO_INPUT="raw"; export CNN_LOSO_HIER="0"
export CNN_LOSO_COMPONENT="both"; export CNN_LOSO_PORT_REMAP=""; export CNN_LOSO_NO_MEANSUB=""

DS_label=(metal beet metalday2 freshcal)
DS_sess=("1143 1210 1239" "1334 1444 1512" "0909 0938 1008" "1103 1200 1258")

CF_desc=("all16 @2-5GHz" "refl-all4 @2-5GHz" "pair13 fullS @2-5GHz")
CF_mode=(all all pair)
CF_ports=("1 2 3 4" "1 2 3 4" "1 3")
CF_refl=(0 1 0)
CF_band=("2 5" "2 5" "2 5")
CF_tag=("all_ant1-2-3-4_band2-5" "refl_ant1-2-3-4_band2-5" "pair_ant1-3_band2-5")

for c in 0 1 2; do
  for d in 0 1 2 3; do
    J="$RES/cnn_loso_Aug18_${DS_label[$d]}_raw_${CF_tag[$c]}.json"
    if [ -f "$J" ]; then echo "--- reuse ${DS_label[$d]} ${CF_desc[$c]}"; continue; fi
    export CNN_LOSO_SESSIONS="${DS_sess[$d]}"; export CNN_LOSO_SETLABEL="${DS_label[$d]}"
    export CNN_LOSO_ANT_MODE="${CF_mode[$c]}"; export CNN_LOSO_PORTS="${CF_ports[$c]}"
    export CNN_LOSO_REFL_ONLY="${CF_refl[$c]}"; export CNN_LOSO_BAND="${CF_band[$c]}"
    echo "### REDUCED ${DS_label[$d]} [${CF_desc[$c]}] ###"
    "$MAT" -batch "run('$SCRIPT')" 2>&1 | grep -E "LOSO position|rror" | head -2
  done
done
echo "======= REDUCED LOSO DONE ======="
