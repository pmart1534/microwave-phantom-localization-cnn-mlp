#!/bin/bash
# All-night chain, priority-ordered. @20ep+curves except noted promotions.
MAT="C:/Program Files/MATLAB/R2025b/bin/matlab.exe"
LOSO="C:\Users\peter\Desktop\EM Imaging\CNN vs MLP\cnn_matlab\Imager_CNN_LOSO.m"
LOPO="C:\Users\peter\Desktop\EM Imaging\CNN vs MLP\cnn_matlab\Imager_CNN_LOPO.m"
RES="C:/Users/peter/Desktop/EM Imaging/CNN vs MLP/results"
A18="C:\Users\peter\Desktop\EM Imaging\BreastPhantom\HunterVNA\DataMeasurements\Sam Antennas\MediumAntenna\Separated\Aug18"
F4P="$A18\OilChangeandA3F4"; F5P="$A18\A3F5"; SWP="$A18\A3_MetalTumor_SwapAntLocation"
base() {
  export CNN_LOSO_INPUT="raw" CNN_LOSO_HIER="0" CNN_LOSO_REFL_ONLY="0" CNN_LOSO_COMPONENT="both"
  export CNN_LOSO_BAND="" CNN_LOSO_PORT_REMAP="" CNN_LOSO_NO_MEANSUB="" CNN_LOSO_NO_BASELINE=""
  export CNN_LOSO_ZSCORE="" CNN_LOSO_INPUTNORM="" CNN_LOSO_MAGDB="" CNN_LOSO_CURVES="1" CNN_LOSO_EPOCHS="20"
  export CNN_LOSO_ANT_MODE="all" CNN_LOSO_PORTS="1 2 3 4"
}
f4() { export CNN_LOSO_PARENT="$F4P" CNN_LOSO_SESSIONS="1655 1804 1820" CNN_LOSO_SETLABEL="f4auge20"; }
f5() { export CNN_LOSO_PARENT="$F5P" CNN_LOSO_SESSIONS="1317 1341 1409" CNN_LOSO_SETLABEL="f5aug"; }
run() { echo "### $1 ###"; "$MAT" -batch "run('$LOSO')" 2>&1 | grep -E "LOSO position|STILL IMPROVING|rror" | head -4; }

# ---- P1: band windows on F4 + F5 ----
F4PRE="OilChangeandA3F4_f4auge20"; F5PRE="A3F5_f5aug"
for B in "0.1 2" "5 8" "1 5" "0.1 5" "1 3" "2 4" "3 5"; do
  BT="${B/ /-}"
  if [ ! -f "$RES/cnn_loso_${F4PRE}_raw_all_ant1-2-3-4_band${BT}.json" ]; then
    base; f4; export CNN_LOSO_BAND="$B"; run "P1 F4 band $BT"
  else echo "--- reuse F4 $BT"; fi
  if [ ! -f "$RES/cnn_loso_${F5PRE}_raw_all_ant1-2-3-4_band${BT}.json" ]; then
    base; f5; export CNN_LOSO_BAND="$B"; run "P1 F5 band $BT"
  else echo "--- reuse F5 $BT"; fi
done

# ---- P2: cheap-device factorial cells on F4 + F5 ----
CP=(both mag phase); CP_tag=(raw rawmag rawphase)
for d in f4 f5; do
  [ "$d" = "f4" ] && PRE="$F4PRE" || PRE="$F5PRE"
  for c in 0 1 2; do
    for h in 0 1; do
      for b in 0 1; do
        [ $h -eq 0 ] && HT="all_ant1-2-3-4" || HT="refl_ant1-2-3-4"
        [ $b -eq 0 ] && SFX="" BV="" || SFX="_band2-5" BV="2 5"
        J="$RES/cnn_loso_${PRE}_${CP_tag[$c]}_${HT}${SFX}.json"
        if [ -f "$J" ]; then echo "--- reuse $d ${CP[$c]} $HT $SFX"; continue; fi
        base; $d; export CNN_LOSO_COMPONENT="${CP[$c]}" CNN_LOSO_BAND="$BV"
        [ $h -eq 1 ] && export CNN_LOSO_REFL_ONLY="1"
        run "P2 $d [${CP[$c]} hw$h band$b]"
      done
    done
  done
done

# ---- P3: only-one preprocessing on F4 + F5 ----
O_nb=("" 1 1 1); O_nm=(1 "" 1 1); O_zs=(off off "" off); O_in=(none none none "")
O_d=("only-baseline" "only-meansub" "only-zscore" "only-innorm")
for d in f4 f5; do
  for v in 0 1 2 3; do
    base; $d
    export CNN_LOSO_NO_BASELINE="${O_nb[$v]}" CNN_LOSO_NO_MEANSUB="${O_nm[$v]}"
    export CNN_LOSO_ZSCORE="${O_zs[$v]}" CNN_LOSO_INPUTNORM="${O_in[$v]}"
    run "P3 $d [${O_d[$v]}]"
  done
done

# ---- P4: LOPO regression on F4, F5, swap ----
lopo() { echo "### P4 LOPO $3 ###"; export CNN_LOSO_PARENT="$1" CNN_LOSO_SESSIONS="$2" CNN_LOSO_SETLABEL="$3" CNN_LOSO_EPOCHS="20"
  "$MAT" -batch "run('$LOPO')" 2>&1 | grep -E "LOPO REGRESSION|per-trial|per-hold|Saved|rror" | head -5; }
lopo "$F4P" "1655 1804 1820" "f4aug"
lopo "$F5P" "1317 1341 1409" "f5aug"
lopo "$SWP" "" "swap4"

# ---- P5: audit-flagged swap promotions @100ep ----
base; export CNN_LOSO_PARENT="$SWP" CNN_LOSO_SESSIONS="" CNN_LOSO_SETLABEL="swap4-p100" CNN_LOSO_EPOCHS="100"
export CNN_LOSO_REFL_ONLY="1" CNN_LOSO_BAND="2 5"; run "P5 swap refl4 @2-5 @100"
base; export CNN_LOSO_PARENT="$SWP" CNN_LOSO_SESSIONS="" CNN_LOSO_SETLABEL="swap4-p100" CNN_LOSO_EPOCHS="100"
export CNN_LOSO_ANT_MODE="pair" CNN_LOSO_PORTS="1 3" CNN_LOSO_BAND="2 5"; run "P5 swap pair13 @2-5 @100"
echo "======= OVERNIGHT AUG21 DONE ======="
