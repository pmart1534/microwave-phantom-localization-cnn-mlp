#!/bin/bash
# Ideal (metal day-1) + swap, @20ep + curves:
#  A) 2-GHz windows: 1-3, 2-4, 3-5
#  B) ORIGINAL-PAPER pipeline: baseline sub + mag/phase + input-layer zscore
#     only (no session stats); linear-mag and dB-mag variants
#  C) feature reduction: {pair13 fullS, refl-pair13, single-S11} x {full, 2-5}
MAT="C:/Program Files/MATLAB/R2025b/bin/matlab.exe"
SCRIPT="C:\Users\peter\Desktop\EM Imaging\CNN vs MLP\cnn_matlab\Imager_CNN_LOSO.m"
RES="C:/Users/peter/Desktop/EM Imaging/CNN vs MLP/results"
A18="C:\Users\peter\Desktop\EM Imaging\BreastPhantom\HunterVNA\DataMeasurements\Sam Antennas\MediumAntenna\Separated\Aug18"
DS_parent=("$A18" "$A18\A3_MetalTumor_SwapAntLocation")
DS_sess=("1143 1210 1239" "")
DS_label=(metal-e20 swap4e20)
DS_pre=(Aug18_metal-e20 A3_MetalTumor_SwapAntLocation_swap4e20)
base() {
  export CNN_LOSO_INPUT="raw" CNN_LOSO_HIER="0" CNN_LOSO_REFL_ONLY="0" CNN_LOSO_COMPONENT="both"
  export CNN_LOSO_BAND="" CNN_LOSO_PORT_REMAP="" CNN_LOSO_NO_MEANSUB="" CNN_LOSO_NO_BASELINE=""
  export CNN_LOSO_ZSCORE="" CNN_LOSO_INPUTNORM="" CNN_LOSO_MAGDB="" CNN_LOSO_CURVES="1" CNN_LOSO_EPOCHS="20"
  export CNN_LOSO_ANT_MODE="all" CNN_LOSO_PORTS="1 2 3 4"
}

for d in 0 1; do
  for B in "1 3" "2 4" "3 5"; do
    BT="${B/ /-}"
    J="$RES/cnn_loso_${DS_pre[$d]}_raw_all_ant1-2-3-4_band${BT}.json"
    if [ -f "$J" ]; then echo "--- reuse ${DS_label[$d]} band $BT"; continue; fi
    base; export CNN_LOSO_PARENT="${DS_parent[$d]}" CNN_LOSO_SESSIONS="${DS_sess[$d]}" CNN_LOSO_SETLABEL="${DS_label[$d]}" CNN_LOSO_BAND="$B"
    echo "### BAND ${DS_label[$d]} [$BT GHz] ###"
    "$MAT" -batch "run('$SCRIPT')" 2>&1 | grep -E "LOSO position|STILL IMPROVING|rror" | head -4
  done
done

for d in 0 1; do
  for mdb in "" 1; do
    base; export CNN_LOSO_PARENT="${DS_parent[$d]}" CNN_LOSO_SESSIONS="${DS_sess[$d]}" CNN_LOSO_SETLABEL="${DS_label[$d]}"
    export CNN_LOSO_NO_MEANSUB="1" CNN_LOSO_ZSCORE="off" CNN_LOSO_MAGDB="$mdb"
    tag="linear-mag"; [ -n "$mdb" ] && tag="dB-mag"
    echo "### ORIGPIPE ${DS_label[$d]} [baseline+innorm only, $tag] ###"
    "$MAT" -batch "run('$SCRIPT')" 2>&1 | grep -E "LOSO position|Session set|STILL IMPROVING|rror" | head -4
  done
done

HW_desc=("pair13-fullS" "refl-pair13" "single-S11")
HW_mode=(pair pair single); HW_ports=("1 3" "1 3" "1"); HW_refl=(0 1 0)
HW_tag=(pair_ant1-3 refl_ant1-3 single_ant1)
for d in 0 1; do
  for h in 0 1 2; do
    for B in "" "2 5"; do
      sfx=""; [ -n "$B" ] && sfx="_band2-5"
      J="$RES/cnn_loso_${DS_pre[$d]}_raw_${HW_tag[$h]}${sfx}.json"
      if [ -f "$J" ]; then echo "--- reuse ${DS_label[$d]} ${HW_desc[$h]} ${B:-full}"; continue; fi
      base; export CNN_LOSO_PARENT="${DS_parent[$d]}" CNN_LOSO_SESSIONS="${DS_sess[$d]}" CNN_LOSO_SETLABEL="${DS_label[$d]}"
      export CNN_LOSO_ANT_MODE="${HW_mode[$h]}" CNN_LOSO_PORTS="${HW_ports[$h]}" CNN_LOSO_REFL_ONLY="${HW_refl[$h]}" CNN_LOSO_BAND="$B"
      echo "### FEAT ${DS_label[$d]} [${HW_desc[$h]} ${B:-full}] ###"
      "$MAT" -batch "run('$SCRIPT')" 2>&1 | grep -E "LOSO position|STILL IMPROVING|rror" | head -4
    done
  done
done
echo "======= BANDS+ORIG+FEAT DONE ======="
