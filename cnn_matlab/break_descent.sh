#!/bin/bash
# Phase 3 adaptive break-descent: hardware reduction x band narrowing.
# Per hardware level, bands descend in width; once a phantom scores <50%
# (BROKEN) it stops descending at that level; unbroken phantoms continue.
MAT="C:/Program Files/MATLAB/R2025b/bin/matlab.exe"
SCRIPT="C:\\Users\\peter\\Desktop\\EM Imaging\\CNN vs MLP\\cnn_matlab\\Imager_CNN_LOSO.m"
B="C:\\Users\\peter\\Desktop\\EM Imaging\\BreastPhantom\\HunterVNA\\DataMeasurements\\Sam Antennas\\MediumAntenna\\Separated"
PY="C:/Users/peter/Desktop/EM Imaging/Above 95 Percent/venv/Scripts/python.exe"
RES="C:/Users/peter/Desktop/EM Imaging/CNN vs MLP/results"
export CNN_LOSO_EPOCHS="100"; export CNN_LOSO_INPUT="raw"; export CNN_LOSO_HIER="0"

# phantom table: name | setup-json-prefix | parent | sessions | setlabel | remap
PH_names=(empty F4 F5)
PH_json=(June18_remap A3_F4_SamMed_all4 A3_F5_SamMed_last3)
PH_parent=("$B\\June18" "$B\\July03\\A3_F4_SamMed" "$B\\July03\\A3_F5_SamMed")
PH_sess=("" "1623 1642 1707 1726" "1432 1454 1516")
PH_label=(remap all4 last3)
PH_remap=("2 1 4 3" "" "")

# hardware ladder: mode | ports | refl | json-mode-tag
HW_desc=("refl-all4" "pair13-fullS" "refl-pair13" "single-S11")
HW_mode=(all pair pair single)
HW_ports=("1 2 3 4" "1 3" "1 3" "1")
HW_refl=(1 0 1 0)
HW_tag=("refl_ant1-2-3-4" "pair_ant1-3" "refl_ant1-3" "single_ant1")

# band ladder (descending width; best placement per width from the full-array study)
BANDS=("1 4" "2 4" "1.5 2.5" "1.5 2" "2 2.25" "1.825 1.925" "1.85 1.9")
BTAG=("1-4" "2-4" "1.5-2.5" "1.5-2" "2-2.25" "1.825-1.925" "1.85-1.9")

for h in 0 1 2 3; do
  echo "=================== HARDWARE: ${HW_desc[$h]} ==================="
  broken=(0 0 0)   # per-phantom broken flag, reset per hardware level
  for bi in "${!BANDS[@]}"; do
    for p in 0 1 2; do
      if [ "${broken[$p]}" = "1" ]; then
        echo "--- skip ${PH_names[$p]} @ ${BTAG[$bi]} (already broken at this hardware level)"
        continue
      fi
      export CNN_LOSO_PARENT="${PH_parent[$p]}"; export CNN_LOSO_SESSIONS="${PH_sess[$p]}"
      export CNN_LOSO_SETLABEL="${PH_label[$p]}"; export CNN_LOSO_PORT_REMAP="${PH_remap[$p]}"
      export CNN_LOSO_ANT_MODE="${HW_mode[$h]}"; export CNN_LOSO_PORTS="${HW_ports[$h]}"
      export CNN_LOSO_REFL_ONLY="${HW_refl[$h]}"; export CNN_LOSO_BAND="${BANDS[$bi]}"
      echo "### DESCENT ${HW_desc[$h]} ${PH_names[$p]} [${BTAG[$bi]} GHz] ###"
      "$MAT" -batch "run('$SCRIPT')" 2>&1 | grep -E "LOSO position|rror" | head -2
      J="$RES/cnn_loso_${PH_json[$p]}_raw_${HW_tag[$h]}_band${BTAG[$bi]}.json"
      ACC=$("$PY" -c "import json;print(json.load(open(r'$J'))['losoPosMean'])" 2>/dev/null)
      if [ -n "$ACC" ]; then
        below=$("$PY" -c "print(1 if float('$ACC')<50 else 0)")
        if [ "$below" = "1" ]; then
          broken[$p]=1
          echo ">>> ${PH_names[$p]} BROKEN at ${HW_desc[$h]} / ${BTAG[$bi]} GHz (${ACC}%)"
        fi
      else
        echo ">>> WARNING: no result JSON for ${PH_names[$p]} ${BTAG[$bi]} (looked for $J)"
      fi
    done
  done
done
echo "======= BREAK DESCENT DONE ======="
