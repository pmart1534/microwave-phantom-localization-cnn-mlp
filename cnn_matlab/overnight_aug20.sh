#!/bin/bash
# Overnight chain (Aug20): new-data LOSO + remaining ablation gaps.
#   S1: oil-change LOSO (100 ep, canonical) - sessions 1120 1154 1225
#   S2: A3F4 LOSO (100 ep, canonical) - sessions 1655 1804 1820
#   S3: reduced trio (all16/refl/pair13 @2-5 GHz) x {swap4, oil3, f4aug} @20ep
#   S4: preprocessing ablation (9 variants) x {oil3, f4aug} @20ep
#   S5: magnitude-only full-band x {swap4, oil3, f4aug} @20ep
# All runs record loss curves + convergence audit (CNN_LOSO_CURVES=1).
MAT="C:/Program Files/MATLAB/R2025b/bin/matlab.exe"
SCRIPT="C:\Users\peter\Desktop\EM Imaging\CNN vs MLP\cnn_matlab\Imager_CNN_LOSO.m"
RES="C:/Users/peter/Desktop/EM Imaging/CNN vs MLP/results"
OIL="C:\Users\peter\Desktop\EM Imaging\BreastPhantom\HunterVNA\DataMeasurements\Sam Antennas\MediumAntenna\Separated\Aug18\OilChangeandA3F4"
SWAP="C:\Users\peter\Desktop\EM Imaging\BreastPhantom\HunterVNA\DataMeasurements\Sam Antennas\MediumAntenna\Separated\Aug18\A3_MetalTumor_SwapAntLocation"
base_env() {
  export CNN_LOSO_INPUT="raw" CNN_LOSO_HIER="0" CNN_LOSO_REFL_ONLY="0"
  export CNN_LOSO_COMPONENT="both" CNN_LOSO_BAND="" CNN_LOSO_PORT_REMAP=""
  export CNN_LOSO_NO_MEANSUB="" CNN_LOSO_NO_BASELINE="" CNN_LOSO_ZSCORE=""
  export CNN_LOSO_INPUTNORM="" CNN_LOSO_ANT_MODE="all" CNN_LOSO_PORTS="1 2 3 4"
  export CNN_LOSO_CURVES="1"
}
run() { echo "### $1 ###"; "$MAT" -batch "run('$SCRIPT')" 2>&1 | grep -E "LOSO position|STILL IMPROVING|rror" | head -6; }

# ---- S1/S2: canonical LOSO, 100 epochs ----
base_env; export CNN_LOSO_EPOCHS="100"
export CNN_LOSO_PARENT="$OIL" CNN_LOSO_SESSIONS="1120 1154 1225" CNN_LOSO_SETLABEL="oil3"
run "S1 OIL-CHANGE LOSO @100ep"
export CNN_LOSO_SESSIONS="1655 1804 1820" CNN_LOSO_SETLABEL="f4aug"
run "S2 A3F4 LOSO @100ep"

# ---- S3: reduced trio @20ep ----
base_env; export CNN_LOSO_EPOCHS="20"
DS_parent=("$SWAP" "$OIL" "$OIL")
DS_sess=("" "1120 1154 1225" "1655 1804 1820")
DS_label=(swap4e20 oil3e20 f4auge20)
CF_mode=(all all pair); CF_ports=("1 2 3 4" "1 2 3 4" "1 3"); CF_refl=(0 1 0)
CF_name=("all16@2-5" "refl4@2-5" "pair13@2-5")
for d in 0 1 2; do
  for c in 0 1 2; do
    base_env; export CNN_LOSO_EPOCHS="20"
    export CNN_LOSO_PARENT="${DS_parent[$d]}" CNN_LOSO_SESSIONS="${DS_sess[$d]}" CNN_LOSO_SETLABEL="${DS_label[$d]}"
    export CNN_LOSO_ANT_MODE="${CF_mode[$c]}" CNN_LOSO_PORTS="${CF_ports[$c]}" CNN_LOSO_REFL_ONLY="${CF_refl[$c]}" CNN_LOSO_BAND="2 5"
    run "S3 ${DS_label[$d]} [${CF_name[$c]}]"
  done
done

# ---- S4: preprocessing ablation x {oil3, f4aug} @20ep ----
V_desc=(no-baseline no-meansub zscore-off zscore-global all-off)
V_nb=(1 "" "" "" 1); V_nm=("" 1 "" "" 1); V_zs=("" "" off global off); V_in=("" "" "" "" none)
for d in 1 2; do
  for v in "${!V_desc[@]}"; do
    base_env; export CNN_LOSO_EPOCHS="20"
    export CNN_LOSO_PARENT="${DS_parent[$d]}" CNN_LOSO_SESSIONS="${DS_sess[$d]}" CNN_LOSO_SETLABEL="${DS_label[$d]}"
    export CNN_LOSO_NO_BASELINE="${V_nb[$v]}" CNN_LOSO_NO_MEANSUB="${V_nm[$v]}"
    export CNN_LOSO_ZSCORE="${V_zs[$v]}" CNN_LOSO_INPUTNORM="${V_in[$v]}"
    run "S4 ${DS_label[$d]} [${V_desc[$v]}]"
  done
done

# ---- S5: magnitude-only full band @20ep ----
for d in 0 1 2; do
  base_env; export CNN_LOSO_EPOCHS="20"
  export CNN_LOSO_PARENT="${DS_parent[$d]}" CNN_LOSO_SESSIONS="${DS_sess[$d]}" CNN_LOSO_SETLABEL="${DS_label[$d]}"
  export CNN_LOSO_COMPONENT="mag"
  run "S5 ${DS_label[$d]} [mag-only]"
done
echo "======= OVERNIGHT DONE ======="
