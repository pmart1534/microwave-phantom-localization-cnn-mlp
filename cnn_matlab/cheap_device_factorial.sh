#!/bin/bash
# Cheap-device factorial @20ep: component {both,mag,phase} x hardware
# {all16, refl-only-4ant} x band {full, 2-5 GHz} on metal / swap / oil.
# Shows what a cheaper front end (power detector, no transmission paths,
# narrow band) costs, separately and combined. Skip-if-exists.
MAT="C:/Program Files/MATLAB/R2025b/bin/matlab.exe"
SCRIPT="C:\Users\peter\Desktop\EM Imaging\CNN vs MLP\cnn_matlab\Imager_CNN_LOSO.m"
RES="C:/Users/peter/Desktop/EM Imaging/CNN vs MLP/results"
A18="C:\Users\peter\Desktop\EM Imaging\BreastPhantom\HunterVNA\DataMeasurements\Sam Antennas\MediumAntenna\Separated\Aug18"

DS_parent=("$A18" "$A18\A3_MetalTumor_SwapAntLocation" "$A18\OilChangeandA3F4")
DS_sess=("1143 1210 1239" "" "1120 1154 1225")
DS_label=(metal-e20 swap4e20 oil3e20)
DS_pre=(Aug18_metal-e20 A3_MetalTumor_SwapAntLocation_swap4e20 OilChangeandA3F4_oil3e20)

CP=(both mag phase); CP_tag=(raw rawmag rawphase)
HW_mode=(all all); HW_refl=(0 1); HW_tag=(all_ant1-2-3-4 refl_ant1-2-3-4); HW_name=(all16 refl4)
BD=("" "2 5"); BD_sfx=("" "_band2-5"); BD_name=(full "2-5GHz")

for d in 0 1 2; do
  for c in 0 1 2; do
    for h in 0 1; do
      for b in 0 1; do
        J="$RES/cnn_loso_${DS_pre[$d]}_${CP_tag[$c]}_${HW_tag[$h]}${BD_sfx[$b]}.json"
        if [ -f "$J" ]; then echo "--- reuse ${DS_label[$d]} ${CP[$c]} ${HW_name[$h]} ${BD_name[$b]}"; continue; fi
        export CNN_LOSO_INPUT="raw" CNN_LOSO_HIER="0" CNN_LOSO_PORT_REMAP=""
        export CNN_LOSO_NO_MEANSUB="" CNN_LOSO_NO_BASELINE="" CNN_LOSO_ZSCORE="" CNN_LOSO_INPUTNORM=""
        export CNN_LOSO_CURVES="1" CNN_LOSO_EPOCHS="20"
        export CNN_LOSO_PARENT="${DS_parent[$d]}" CNN_LOSO_SESSIONS="${DS_sess[$d]}" CNN_LOSO_SETLABEL="${DS_label[$d]}"
        export CNN_LOSO_COMPONENT="${CP[$c]}" CNN_LOSO_ANT_MODE="${HW_mode[$h]}" CNN_LOSO_PORTS="1 2 3 4"
        export CNN_LOSO_REFL_ONLY="${HW_refl[$h]}" CNN_LOSO_BAND="${BD[$b]}"
        echo "### CHEAP ${DS_label[$d]} [${CP[$c]} ${HW_name[$h]} ${BD_name[$b]}] ###"
        "$MAT" -batch "run('$SCRIPT')" 2>&1 | grep -E "LOSO position|STILL IMPROVING|rror" | head -4
      done
    done
  done
done
echo "======= CHEAP FACTORIAL DONE ======="
