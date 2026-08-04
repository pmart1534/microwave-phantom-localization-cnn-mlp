#!/bin/bash
# Component ablation x bandwidth, EMPTY phantom only (scoped first look):
# magnitude-only vs phase-only down the empty band ladder, on the two extreme
# hardware levels. single-S11 runs FIRST (the informative one), full16 second.
# Skip-if-exists; per-(hardware,component) early stop below 50%.
MAT="C:/Program Files/MATLAB/R2025b/bin/matlab.exe"
SCRIPT="C:\\Users\\peter\\Desktop\\EM Imaging\\CNN vs MLP\\cnn_matlab\\Imager_CNN_LOSO.m"
B="C:\\Users\\peter\\Desktop\\EM Imaging\\BreastPhantom\\HunterVNA\\DataMeasurements\\Sam Antennas\\MediumAntenna\\Separated"
PY="C:/Users/peter/Desktop/EM Imaging/Above 95 Percent/venv/Scripts/python.exe"
RES="C:/Users/peter/Desktop/EM Imaging/CNN vs MLP/results"
export CNN_LOSO_EPOCHS="100"; export CNN_LOSO_INPUT="raw"; export CNN_LOSO_HIER="0"
export CNN_LOSO_PARENT="$B\\June18"; export CNN_LOSO_SESSIONS=""
export CNN_LOSO_SETLABEL="remap"; export CNN_LOSO_PORT_REMAP="2 1 4 3"

BANDS=("1 4" "2 4" "1.5 2.5" "1.5 2" "2 2.25" "1.95 2.05" "1.975 2.025")

HW_desc=("single-S11" "full16")
HW_mode=(single all)
HW_ports=("1" "1 2 3 4")
HW_refl=(0 0)
HW_tag=(single_ant1 all_ant1-2-3-4)

for h in 0 1; do
  for comp in mag phase; do
    echo "=================== ${HW_desc[$h]} / ${comp}-only ==================="
    export CNN_LOSO_COMPONENT="$comp"
    broken=0
    for bi in "${!BANDS[@]}"; do
      if [ "$broken" = "1" ]; then
        echo "--- skip [${BANDS[$bi]}] (broken)"
        continue
      fi
      BT="${BANDS[$bi]/ /-}"
      J="$RES/cnn_loso_June18_remap_raw${comp}_${HW_tag[$h]}_band${BT}.json"
      if [ -f "$J" ]; then
        echo "--- reuse ${HW_desc[$h]} ${comp} [$BT]"
      else
        export CNN_LOSO_ANT_MODE="${HW_mode[$h]}"; export CNN_LOSO_PORTS="${HW_ports[$h]}"
        export CNN_LOSO_REFL_ONLY="${HW_refl[$h]}"; export CNN_LOSO_BAND="${BANDS[$bi]}"
        echo "### COMP ${HW_desc[$h]} ${comp} [$BT GHz] ###"
        "$MAT" -batch "run('$SCRIPT')" 2>&1 | grep -E "LOSO position|rror" | head -2
      fi
      ACC=$("$PY" -c "import json;print(json.load(open(r'$J'))['losoPosMean'])" 2>/dev/null)
      if [ -n "$ACC" ]; then
        if [ "$("$PY" -c "print(1 if float('$ACC')<50 else 0)")" = "1" ]; then
          broken=1
          echo ">>> BROKEN: ${HW_desc[$h]} ${comp}-only at $BT GHz (${ACC}%)"
        fi
      else
        echo ">>> WARNING: no result for ${HW_desc[$h]} ${comp} $BT"
      fi
    done
  done
done
echo "======= COMPONENT SWEEP DONE ======="
