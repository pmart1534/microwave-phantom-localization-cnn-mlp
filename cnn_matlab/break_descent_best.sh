#!/bin/bash
# Break descent v2: each phantom's band ladder converges on ITS OWN best
# frequency (from the 0.25/0.1 GHz placement scans):
#   empty -> 2.0 GHz, F4 -> 3.0 GHz, F5 -> 2.25 GHz
# Same adaptive rule: per hardware level, a phantom that scores <50% (BROKEN)
# stops descending. Skip-if-exists: reuses any window already run (still reads
# its accuracy so the break flag is set correctly).
MAT="C:/Program Files/MATLAB/R2025b/bin/matlab.exe"
SCRIPT="C:\\Users\\peter\\Desktop\\EM Imaging\\CNN vs MLP\\cnn_matlab\\Imager_CNN_LOSO.m"
B="C:\\Users\\peter\\Desktop\\EM Imaging\\BreastPhantom\\HunterVNA\\DataMeasurements\\Sam Antennas\\MediumAntenna\\Separated"
PY="C:/Users/peter/Desktop/EM Imaging/Above 95 Percent/venv/Scripts/python.exe"
RES="C:/Users/peter/Desktop/EM Imaging/CNN vs MLP/results"
export CNN_LOSO_EPOCHS="100"; export CNN_LOSO_INPUT="raw"; export CNN_LOSO_HIER="0"

PH_names=(empty F4 F5)
PH_json=(June18_remap A3_F4_SamMed_all4 A3_F5_SamMed_last3)
PH_parent=("$B\\June18" "$B\\July03\\A3_F4_SamMed" "$B\\July03\\A3_F5_SamMed")
PH_sess=("" "1623 1642 1707 1726" "1432 1454 1516")
PH_label=(remap all4 last3)
PH_remap=("2 1 4 3" "" "")

# per-phantom band ladders (widths 3,2,1,0.5,0.25,0.1,0.05 GHz), converging on
# each phantom's best center; every window except the 0.05s was placement-tested
E_BANDS=("1 4" "2 4" "1.5 2.5" "1.5 2" "2 2.25" "1.95 2.05" "1.975 2.025")
F4_BANDS=("1 4" "2 4" "2.5 3.5" "2.5 3" "3 3.25" "2.95 3.05" "2.975 3.025")
F5_BANDS=("1 4" "2 4" "2 3" "2 2.5" "2 2.25" "2.2 2.3" "2.225 2.275")

# hardware ladder, full array first
HW_desc=("full16" "refl-all4" "pair13-fullS" "refl-pair13" "single-S11")
HW_mode=(all all pair pair single)
HW_ports=("1 2 3 4" "1 2 3 4" "1 3" "1 3" "1")
HW_refl=(0 1 0 1 0)
HW_tag=(all_ant1-2-3-4 refl_ant1-2-3-4 pair_ant1-3 refl_ant1-3 single_ant1)

get_band() {  # $1=phantom idx, $2=width idx
  case $1 in
    0) echo "${E_BANDS[$2]}" ;;
    1) echo "${F4_BANDS[$2]}" ;;
    2) echo "${F5_BANDS[$2]}" ;;
  esac
}

for h in 0 1 2 3 4; do
  echo "=================== HARDWARE: ${HW_desc[$h]} ==================="
  broken=(0 0 0)
  for bi in 0 1 2 3 4 5 6; do
    for p in 0 1 2; do
      if [ "${broken[$p]}" = "1" ]; then
        echo "--- skip ${PH_names[$p]} width-idx $bi (broken at this hardware level)"
        continue
      fi
      BAND=$(get_band $p $bi)
      BT="${BAND/ /-}"
      J="$RES/cnn_loso_${PH_json[$p]}_raw_${HW_tag[$h]}_band${BT}.json"
      if [ -f "$J" ]; then
        echo "--- reuse ${PH_names[$p]} ${HW_desc[$h]} [$BT]"
      else
        export CNN_LOSO_PARENT="${PH_parent[$p]}"; export CNN_LOSO_SESSIONS="${PH_sess[$p]}"
        export CNN_LOSO_SETLABEL="${PH_label[$p]}"; export CNN_LOSO_PORT_REMAP="${PH_remap[$p]}"
        export CNN_LOSO_ANT_MODE="${HW_mode[$h]}"; export CNN_LOSO_PORTS="${HW_ports[$h]}"
        export CNN_LOSO_REFL_ONLY="${HW_refl[$h]}"; export CNN_LOSO_BAND="$BAND"
        echo "### BEST-DESCENT ${HW_desc[$h]} ${PH_names[$p]} [$BT GHz] ###"
        "$MAT" -batch "run('$SCRIPT')" 2>&1 | grep -E "LOSO position|rror" | head -2
      fi
      ACC=$("$PY" -c "import json;print(json.load(open(r'$J'))['losoPosMean'])" 2>/dev/null)
      if [ -n "$ACC" ]; then
        below=$("$PY" -c "print(1 if float('$ACC')<50 else 0)")
        if [ "$below" = "1" ]; then
          broken[$p]=1
          echo ">>> ${PH_names[$p]} BROKEN at ${HW_desc[$h]} / $BT GHz (${ACC}%)"
        fi
      else
        echo ">>> WARNING: no result for ${PH_names[$p]} $BT (looked for $J)"
      fi
    done
  done
done
echo "======= BEST-DESCENT DONE ======="
