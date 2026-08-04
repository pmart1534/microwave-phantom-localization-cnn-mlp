#!/bin/bash
# Minimal-chip sweep, PRIORITY-ORDERED so the most important results land first:
#   G1 single-S11 empty: tone descent 4->3->2->1 freq points (mag+phase "both")
#   G2 single-S11 empty: magnitude-only, band ladder + tone descent
#   G3 single-S11 F4:    tone descent (both)
#   G4 single-S11 F4:    magnitude-only ladder
#   G5 refl-pair13 empty: tone descent (both)
#   G6 refl-pair13 F4:    tone descent (both)
#   G7 refl-pair13 empty: magnitude-only ladder
#   G8 refl-pair13 F4:    magnitude-only ladder
# Each group early-stops below 50%. Skip-if-exists reuse. 10 MHz native grid:
# "2 2" = a single frequency point (1-tone CW chip).
MAT="C:/Program Files/MATLAB/R2025b/bin/matlab.exe"
SCRIPT="C:\\Users\\peter\\Desktop\\EM Imaging\\CNN vs MLP\\cnn_matlab\\Imager_CNN_LOSO.m"
B="C:\\Users\\peter\\Desktop\\EM Imaging\\BreastPhantom\\HunterVNA\\DataMeasurements\\Sam Antennas\\MediumAntenna\\Separated"
PY="C:/Users/peter/Desktop/EM Imaging/Above 95 Percent/venv/Scripts/python.exe"
RES="C:/Users/peter/Desktop/EM Imaging/CNN vs MLP/results"
export CNN_LOSO_EPOCHS="100"; export CNN_LOSO_INPUT="raw"; export CNN_LOSO_HIER="0"

run_group() {  # $1 desc  $2 comp  $3 ant_mode  $4 ports  $5 refl  $6 hwtag
               # $7 phantom(empty|F4)  $8... bands
  local desc="$1" comp="$2" mode="$3" ports="$4" refl="$5" hwtag="$6" ph="$7"
  shift 7
  local bands=("$@")
  echo "=================== $desc ==================="
  if [ "$ph" = "empty" ]; then
    export CNN_LOSO_PARENT="$B\\June18"; export CNN_LOSO_SESSIONS=""
    export CNN_LOSO_SETLABEL="remap"; export CNN_LOSO_PORT_REMAP="2 1 4 3"
    local pre="June18_remap"
  else
    export CNN_LOSO_PARENT="$B\\July03\\A3_F4_SamMed"; export CNN_LOSO_SESSIONS="1623 1642 1707 1726"
    export CNN_LOSO_SETLABEL="all4"; export CNN_LOSO_PORT_REMAP=""
    local pre="A3_F4_SamMed_all4"
  fi
  local itag="raw"; if [ "$comp" != "both" ]; then itag="raw${comp}"; fi
  local broken=0
  for band in "${bands[@]}"; do
    if [ "$broken" = "1" ]; then echo "--- skip [$band] (broken)"; continue; fi
    local BT="${band/ /-}"
    local J="$RES/cnn_loso_${pre}_${itag}_${hwtag}_band${BT}.json"
    if [ -f "$J" ]; then
      echo "--- reuse $desc [$BT]"
    else
      export CNN_LOSO_COMPONENT="$comp"; export CNN_LOSO_ANT_MODE="$mode"
      export CNN_LOSO_PORTS="$ports"; export CNN_LOSO_REFL_ONLY="$refl"
      export CNN_LOSO_BAND="$band"
      echo "### MINCHIP $desc [$BT GHz] ###"
      "$MAT" -batch "run('$SCRIPT')" 2>&1 | grep -E "LOSO position|rror" | head -2
    fi
    local ACC=$("$PY" -c "import json;print(json.load(open(r'$J'))['losoPosMean'])" 2>/dev/null)
    if [ -n "$ACC" ]; then
      if [ "$("$PY" -c "print(1 if float('$ACC')<50 else 0)")" = "1" ]; then
        broken=1; echo ">>> BROKEN: $desc at $BT GHz (${ACC}%)"
      fi
    else
      echo ">>> WARNING: no result for $desc $BT"
    fi
  done
}

# tone descents (component = both): 4 -> 3 -> 2 -> 1 frequency points.
# EMPTY uses the ORIGINAL ~1.875 GHz center (its full-array "optimized" 2.0
# center was chosen on a saturated metric and is worse at reduced hardware).
E_TONES=("1.86 1.89" "1.86 1.88" "1.87 1.88" "1.87 1.87")
F4_TONES=("2.98 3.01" "2.99 3.01" "2.99 3" "3 3")
# magnitude-only ladders: coarse band ladder, then the tones
E_MAG=("1 4" "2 2.25" "1.85 1.9" "1.86 1.89" "1.86 1.88" "1.87 1.88" "1.87 1.87")
F4_MAG=("1 4" "3 3.25" "2.975 3.025" "2.98 3.01" "2.99 3.01" "2.99 3" "3 3")

run_group "G1 single-S11 empty tones"   both single "1" 0 single_ant1 empty "${E_TONES[@]}"
run_group "G2 single-S11 empty MAGonly" mag  single "1" 0 single_ant1 empty "${E_MAG[@]}"
run_group "G3 single-S11 F4 tones"      both single "1" 0 single_ant1 F4    "${F4_TONES[@]}"
run_group "G4 single-S11 F4 MAGonly"    mag  single "1" 0 single_ant1 F4    "${F4_MAG[@]}"
run_group "G5 refl-pair13 empty tones"  both pair "1 3" 1 refl_ant1-3 empty "${E_TONES[@]}"
run_group "G6 refl-pair13 F4 tones"     both pair "1 3" 1 refl_ant1-3 F4    "${F4_TONES[@]}"
run_group "G7 refl-pair13 empty MAGonly" mag pair "1 3" 1 refl_ant1-3 empty "${E_MAG[@]}"
run_group "G8 refl-pair13 F4 MAGonly"   mag pair "1 3" 1 refl_ant1-3 F4    "${F4_MAG[@]}"
echo "======= MINIMAL-CHIP SWEEP DONE ======="
