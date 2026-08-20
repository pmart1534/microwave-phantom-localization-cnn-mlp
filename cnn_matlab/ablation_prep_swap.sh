#!/bin/bash
# Preprocessing ablation on the antenna-reattach set (swap4e20: freshCal03
# 1258 + FreshPlaceAnt 1509/1631/1703), all 16 S-params, full band.
# The high-drift counterpart to the ideal-metal ablation: raw between-session
# change here EXCEEDS the position signal, so this is where preprocessing
# should earn its keep. Reference = existing swap4e20 run (100.00).
MAT="C:/Program Files/MATLAB/R2025b/bin/matlab.exe"
SCRIPT="C:\Users\peter\Desktop\EM Imaging\CNN vs MLP\cnn_matlab\Imager_CNN_LOSO.m"
RES="C:/Users/peter/Desktop/EM Imaging/CNN vs MLP/results"
export CNN_LOSO_PARENT="C:\Users\peter\Desktop\EM Imaging\BreastPhantom\HunterVNA\DataMeasurements\Sam Antennas\MediumAntenna\Separated\Aug18\A3_MetalTumor_SwapAntLocation"
export CNN_LOSO_EPOCHS="20"; export CNN_LOSO_CURVES="1"; export CNN_LOSO_INPUT="raw"; export CNN_LOSO_HIER="0"
export CNN_LOSO_ANT_MODE="all"; export CNN_LOSO_PORTS="1 2 3 4"
export CNN_LOSO_REFL_ONLY="0"; export CNN_LOSO_COMPONENT="both"; export CNN_LOSO_BAND=""
export CNN_LOSO_PORT_REMAP=""; export CNN_LOSO_SESSIONS=""

V_desc=("reference" "no-baseline" "no-meansub" "nobase+nomean" "zscore-off" "zscore-row" "zscore-global" "inputnorm-none" "all-off")
V_nb=("" 1 "" 1 "" "" "" "" 1)
V_nm=("" "" 1 1 "" "" "" "" 1)
V_zs=("" "" "" "" off row global "" off)
V_in=("" "" "" "" "" "" "" none none)
V_sfx=(""\n       "-nobase" "-nomean" "-nomean-nobase" "-zsoff" "-zsrow" "-zsglobal" "-innone" "-nomean-nobase-zsoff-innone")

for v in "${!V_desc[@]}"; do
  J="$RES/cnn_loso_A3_MetalTumor_SwapAntLocation_swap4e20${V_sfx[$v]}_raw_all_ant1-2-3-4.json"
  if [ -f "$J" ]; then echo "--- reuse ${V_desc[$v]}"; continue; fi
  export CNN_LOSO_SETLABEL="swap4e20"
  export CNN_LOSO_NO_BASELINE="${V_nb[$v]}"; export CNN_LOSO_NO_MEANSUB="${V_nm[$v]}"
  export CNN_LOSO_ZSCORE="${V_zs[$v]}"; export CNN_LOSO_INPUTNORM="${V_in[$v]}"
  echo "### ABLATION-SWAP [${V_desc[$v]}] ###"
  "$MAT" -batch "run('$SCRIPT')" 2>&1 | grep -E "LOSO position|Session set|rror" | head -3
done
echo "======= ABLATION-SWAP DONE ======="
