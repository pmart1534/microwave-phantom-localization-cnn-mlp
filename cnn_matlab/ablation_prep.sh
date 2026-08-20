#!/bin/bash
# Preprocessing ablation on the ideal 3-session LOSO (day-1 metal, all 16
# S-params, full band). Reference = existing 99.32 run. Each variant removes
# or coarsens ONE step (plus one everything-off run).
MAT="C:/Program Files/MATLAB/R2025b/bin/matlab.exe"
SCRIPT="C:\Users\peter\Desktop\EM Imaging\CNN vs MLP\cnn_matlab\Imager_CNN_LOSO.m"
RES="C:/Users/peter/Desktop/EM Imaging/CNN vs MLP/results"
export CNN_LOSO_PARENT="C:\Users\peter\Desktop\EM Imaging\BreastPhantom\HunterVNA\DataMeasurements\Sam Antennas\MediumAntenna\Separated\Aug18"
export CNN_LOSO_EPOCHS="100"; export CNN_LOSO_INPUT="raw"; export CNN_LOSO_HIER="0"
export CNN_LOSO_ANT_MODE="all"; export CNN_LOSO_PORTS="1 2 3 4"
export CNN_LOSO_REFL_ONLY="0"; export CNN_LOSO_COMPONENT="both"; export CNN_LOSO_BAND=""
export CNN_LOSO_PORT_REMAP=""; export CNN_LOSO_SESSIONS="1143 1210 1239"

# name | NO_BASELINE | NO_MEANSUB | ZSCORE | INPUTNORM | expected label suffix
V_desc=("no-baseline" "no-meansub" "zscore-off" "zscore-row" "zscore-global" "inputnorm-none" "all-off")
V_nb=(1 "" "" "" "" "" 1)
V_nm=("" 1 "" "" "" "" 1)
V_zs=("" "" off row global "" off)
V_in=("" "" "" "" "" none none)
V_sfx=("-nobase" "-nomean" "-zsoff" "-zsrow" "-zsglobal" "-innone" "-nomean-nobase-zsoff-innone")

for v in "${!V_desc[@]}"; do
  J="$RES/cnn_loso_Aug18_metal${V_sfx[$v]}_raw_all_ant1-2-3-4.json"
  if [ -f "$J" ]; then echo "--- reuse ${V_desc[$v]}"; continue; fi
  export CNN_LOSO_SETLABEL="metal"
  export CNN_LOSO_NO_BASELINE="${V_nb[$v]}"; export CNN_LOSO_NO_MEANSUB="${V_nm[$v]}"
  export CNN_LOSO_ZSCORE="${V_zs[$v]}"; export CNN_LOSO_INPUTNORM="${V_in[$v]}"
  echo "### ABLATION [${V_desc[$v]}] ###"
  "$MAT" -batch "run('$SCRIPT')" 2>&1 | grep -E "LOSO position|Session set|rror" | head -3
done
echo "======= ABLATION DONE ======="
