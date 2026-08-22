#!/bin/bash
# A3F5 (Aug21: 1317 1341 1409; aborted 1307 excluded) - full parity suite
# matching A3F4-Aug's coverage. All @20ep + curves.
MAT="C:/Program Files/MATLAB/R2025b/bin/matlab.exe"
SCRIPT="C:\Users\peter\Desktop\EM Imaging\CNN vs MLP\cnn_matlab\Imager_CNN_LOSO.m"
export CNN_LOSO_PARENT="C:\Users\peter\Desktop\EM Imaging\BreastPhantom\HunterVNA\DataMeasurements\Sam Antennas\MediumAntenna\Separated\Aug18\A3F5"
base() {
  export CNN_LOSO_INPUT="raw" CNN_LOSO_HIER="0" CNN_LOSO_REFL_ONLY="0" CNN_LOSO_COMPONENT="both"
  export CNN_LOSO_BAND="" CNN_LOSO_PORT_REMAP="" CNN_LOSO_NO_MEANSUB="" CNN_LOSO_NO_BASELINE=""
  export CNN_LOSO_ZSCORE="" CNN_LOSO_INPUTNORM="" CNN_LOSO_MAGDB="" CNN_LOSO_CURVES="1" CNN_LOSO_EPOCHS="20"
  export CNN_LOSO_ANT_MODE="all" CNN_LOSO_PORTS="1 2 3 4"
  export CNN_LOSO_SESSIONS="1317 1341 1409" CNN_LOSO_SETLABEL="f5aug"
}
run() { echo "### F5 $1 ###"; "$MAT" -batch "run('$SCRIPT')" 2>&1 | grep -E "LOSO position|STILL IMPROVING|rror" | head -4; }

base; run "LOSO headline (all16, full band)"
base; export CNN_LOSO_BAND="2 5"; run "all16 @2-5"
base; export CNN_LOSO_REFL_ONLY="1" CNN_LOSO_BAND="2 5"; run "refl4 @2-5"
base; export CNN_LOSO_ANT_MODE="pair" CNN_LOSO_PORTS="1 3" CNN_LOSO_BAND="2 5"; run "pair13 @2-5"
base; export CNN_LOSO_NO_BASELINE="1"; run "abl no-baseline"
base; export CNN_LOSO_NO_MEANSUB="1"; run "abl no-meansub"
base; export CNN_LOSO_ZSCORE="off"; run "abl zscore-off"
base; export CNN_LOSO_ZSCORE="global"; run "abl zscore-global"
base; export CNN_LOSO_NO_BASELINE="1" CNN_LOSO_NO_MEANSUB="1" CNN_LOSO_ZSCORE="off" CNN_LOSO_INPUTNORM="none"; run "abl ALL-OFF"
base; export CNN_LOSO_COMPONENT="mag"; run "mag-only full band"
echo "======= F5 PARITY DONE ======="
