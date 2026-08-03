#!/bin/bash
# 0.1 GHz placement scan: nine 100 MHz windows across the span, all 16 S-params,
# to verify (or refute) that the ~1.85-1.925 GHz slot really is the best
# placement at ultra-narrow width for each phantom.
MAT="C:/Program Files/MATLAB/R2025b/bin/matlab.exe"
SCRIPT="C:\\Users\\peter\\Desktop\\EM Imaging\\CNN vs MLP\\cnn_matlab\\Imager_CNN_LOSO.m"
B="C:\\Users\\peter\\Desktop\\EM Imaging\\BreastPhantom\\HunterVNA\\DataMeasurements\\Sam Antennas\\MediumAntenna\\Separated"
export CNN_LOSO_EPOCHS="100"; export CNN_LOSO_INPUT="raw"; export CNN_LOSO_HIER="0"
export CNN_LOSO_ANT_MODE="all"; export CNN_LOSO_PORTS="1 2 3 4"; export CNN_LOSO_REFL_ONLY="0"

PH_names=(empty F4 F5)
PH_parent=("$B\\June18" "$B\\July03\\A3_F4_SamMed" "$B\\July03\\A3_F5_SamMed")
PH_sess=("" "1623 1642 1707 1726" "1432 1454 1516")
PH_label=(remap all4 last3)
PH_remap=("2 1 4 3" "" "")

BANDS=("0.95 1.05" "1.2 1.3" "1.45 1.55" "1.7 1.8" "1.95 2.05" "2.2 2.3" "2.45 2.55" "2.95 3.05" "3.45 3.55")

for bi in "${!BANDS[@]}"; do
  for p in 0 1 2; do
    export CNN_LOSO_PARENT="${PH_parent[$p]}"; export CNN_LOSO_SESSIONS="${PH_sess[$p]}"
    export CNN_LOSO_SETLABEL="${PH_label[$p]}"; export CNN_LOSO_PORT_REMAP="${PH_remap[$p]}"
    export CNN_LOSO_BAND="${BANDS[$bi]}"
    echo "### SCAN100 ${PH_names[$p]} [${BANDS[$bi]} GHz] ###"
    "$MAT" -batch "run('$SCRIPT')" 2>&1 | grep -E "LOSO position|rror" | head -2
  done
done
echo "======= 100MHZ SCAN DONE ======="
