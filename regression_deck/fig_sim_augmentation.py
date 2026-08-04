"""Why the sim is augmented, shown on the tumor DIFFERENTIAL dS (where the nuisances
are visible). Three panels (S11 dS, linear x1e3):
  A) measured signal vs take-to-take noise floor -> additive noise, SNR ~6.6x
  B) measured session-mean dS across 3 sessions -> cross-session drift (~12%)
  C) sim: deterministic vs augmented takes -> reproduces A + B
"""
import os, sys, glob, re
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "mlp_python"))
import sim_noise as SN

TEAL="#2C5F7C"; GREEN="#2E7D5B"; CRIMSON="#BE0000"; GOLD="#C8890B"; INK="#1E293B"; MUTE="#5B6B7B"
CH = 0  # S11

def stems_of(s):
    return {re.match(r"(R\d+C\d+P\d+)_T", os.path.basename(x)).group(1)
            for x in glob.glob(os.path.join(s, "R*C*P*_T*.csv"))}

sess = [s for s in sorted(glob.glob(os.path.join(SN.MEAS, "BreastPhantom_A3_*")))
        if glob.glob(os.path.join(s, "baseline_T*.csv")) and glob.glob(os.path.join(s, "R*C*P*_T*.csv"))]
common = sorted(set.intersection(*[stems_of(s) for s in sess]))
st = common[len(common)//2]                              # a representative position
F = SN._read_meas(sorted(glob.glob(os.path.join(sess[0], "baseline_T*.csv")))[0]).shape[0]
fghz = np.linspace(0.1, 8, F)

sess_take_ds = []                                        # per session: (takes,F) dS for channel CH
for s in sess:
    base = np.mean([SN._read_meas(b) for b in sorted(glob.glob(os.path.join(s, "baseline_T*.csv")))], axis=0)
    tks = np.array([SN._read_meas(x) - base for x in sorted(glob.glob(os.path.join(s, st + "_T*.csv")))])
    sess_take_ds.append(tks[:, :, CH])

d0 = sess_take_ds[0]                                     # (takes,F)
sig = np.abs(d0.mean(0)) * 1e3                           # |mean dS| (mV-ish)
noise = np.abs(d0).std(0) * 1e3                          # take-to-take std
snr = np.median(np.abs(d0.mean(0)) / (np.abs(d0).std(0) + 1e-12))

# sim clean + augmented, S11 dS
dS, tgt = SN.load_sim_ds(); snr_c, drift = SN.measured_calibration()
d = SN.synth(dS, tgt, snr_c, drift * SN.DRIFT_GAIN, noise=True, drift=True)
simf = SN.FG / 1e9; p = 20
clean = np.abs(dS[p, CH, :]) * 1e3
aug = np.abs(d["Yc"][(d["pos"] == p) & (d["sess"] == 0)][:, CH, :]) * 1e3

fig, ax = plt.subplots(1, 3, figsize=(15.5, 4.6))
# A: signal vs noise floor
ax[0].plot(fghz, sig, color=CRIMSON, lw=1.8, label="signal  |mean dS|")
ax[0].plot(fghz, noise, color=TEAL, lw=1.6, label="take-to-take noise (std)")
ax[0].fill_between(fghz, 0, noise, color=TEAL, alpha=0.15)
ax[0].set_title("A) Measured: signal vs take-to-take noise floor", fontsize=12, fontweight="bold", color=INK)
ax[0].set_xlabel("GHz"); ax[0].set_ylabel("|S11 dS|  (x1e-3)"); ax[0].legend(fontsize=8.5)
ax[0].text(0.97, 0.95, "-> additive per-take noise, calibrated\n   per channel (median SNR 6.6x;\n   S11 shown here is higher)",
           transform=ax[0].transAxes, fontsize=9, color=TEAL, ha="right", va="top")
# B: cross-session drift
for i, td in enumerate(sess_take_ds):
    ax[1].plot(fghz, np.abs(td.mean(0)) * 1e3, lw=1.5, label=f"session {i+1}")
ax[1].set_title("B) Measured: session-mean dS (drift ~12%)", fontsize=12, fontweight="bold", color=INK)
ax[1].set_xlabel("GHz"); ax[1].set_ylabel("|S11 dS|  (x1e-3)"); ax[1].legend(fontsize=8.5)
ax[1].text(0.97, 0.95, "-> per-session common-mode drift\n   (survives z-score -> real LOSO)",
           transform=ax[1].transAxes, fontsize=9, color=GOLD, ha="right", va="top")
# C: sim clean vs augmented
for a in aug: ax[2].plot(simf, a, color=GREEN, lw=0.5, alpha=0.35)
ax[2].plot(simf, clean, color=INK, lw=1.9, label="sim (deterministic)")
ax[2].plot([], [], color=GREEN, lw=1.5, label="augmented takes")
ax[2].set_title("C) Sim: clean -> augmented", fontsize=12, fontweight="bold", color=INK)
ax[2].set_xlabel("GHz"); ax[2].set_ylabel("|S11 dS|  (x1e-3)"); ax[2].legend(fontsize=8.5)
ax[2].text(0.97, 0.95, "noise + drift injected\nto match A + B", transform=ax[2].transAxes,
           fontsize=9, color=GREEN, ha="right", va="top")
for a in ax:
    a.grid(True, color="#EAF0F4", lw=0.7); a.set_axisbelow(True)
    for s in a.spines.values(): s.set_color("#D8E2EA")

fig.suptitle("Augmenting the simulation: reproduce the bench's measurement noise (A) and session drift (B) in the clean sim (C)",
             fontsize=13, fontweight="bold", color=INK, y=1.0)
fig.tight_layout(rect=[0, 0, 1, 0.95])
fig.savefig(os.path.join(os.path.dirname(__file__), "sim_augmentation.png"), dpi=170, bbox_inches="tight")
print("wrote sim_augmentation.png")
