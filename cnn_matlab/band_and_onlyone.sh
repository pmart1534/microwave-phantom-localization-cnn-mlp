#!/bin/bash
# Two sweeps on IDEAL (metal day-1) + SWAP only, @20ep + curves:
#  A) band windows: 1-5, 2-4.5, 1-2, 2-3, 3-4, 4-5 GHz (all16, both components)
#  B) ONLY-ONE-step preprocessing: keep exactly one of {baseline-sub, mean-sub,
#     per-session z-score, input-layer zscore}, remove the other three.
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
  export CNN_LOSO_ZSCORE="" CNN_LOSO_INPUTNORM="" CNN_LOSO_CURVES="1" CNN_LOSO_EPOCHS="20"
  export CNN_LOSO_ANT_MODE="all" CNN_LOSO_PORTS="1 2 3 4"
}

BANDS=("1 5" "2 4.5" "1 2" "2 3" "3 4" "4 5")
BT=("1-5" "2-4.5" "1-2" "2-3" "3-4" "4-5")
for d in 0 1; do
  for b in "${!BANDS[@]}"; do
    J="$RES/cnn_loso_${DS_pre[$d]}_raw_all_ant1-2-3-4_band${BT[$b]}.json"
    if [ -f "$J" ]; then echo "--- reuse ${DS_label[$d]} band ${BT[$b]}"; continue; fi
    base; export CNN_LOSO_PARENT="${DS_parent[$d]}" CNN_LOSO_SESSIONS="${DS_sess[$d]}" CNN_LOSO_SETLABEL="${DS_label[$d]}" CNN_LOSO_BAND="${BANDS[$b]}"
    echo "### BAND ${DS_label[$d]} [${BT[$b]} GHz] ###"
    "$MAT" -batch "run('$SCRIPT')" 2>&1 | grep -E "LOSO position|STILL IMPROVING|rror" | head -4
  done
done

# only-one-step: keep exactly one mechanism
O_desc=("only-baseline" "only-meansub" "only-zscore" "only-innorm")
O_nb=("" 1 1 1); O_nm=(1 "" 1 1); O_zs=(off off "" off); O_in=(none none none "")
for d in 0 1; do
  for v in "${!O_desc[@]}"; do
    base; export CNN_LOSO_PARENT="${DS_parent[$d]}" CNN_LOSO_SESSIONS="${DS_sess[$d]}" CNN_LOSO_SETLABEL="${DS_label[$d]}"
    export CNN_LOSO_NO_BASELINE="${O_nb[$v]}" CNN_LOSO_NO_MEANSUB="${O_nm[$v]}"
    export CNN_LOSO_ZSCORE="${O_zs[$v]}" CNN_LOSO_INPUTNORM="${O_in[$v]}"
    echo "### ONLYONE ${DS_label[$d]} [${O_desc[$v]}] ###"
    "$MAT" -batch "run('$SCRIPT')" 2>&1 | grep -E "LOSO position|Session set|STILL IMPROVING|rror" | head -4
  done
done
echo "======= BAND+ONLYONE DONE ======="
