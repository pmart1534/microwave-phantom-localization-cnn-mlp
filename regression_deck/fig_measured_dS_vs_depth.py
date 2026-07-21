"""Measured analog to sim_dS_vs_depth: how much the tumor perturbs the MEASURED
signal at each of the 4 July10 tumor heights.

For each depth session: dS(position) = mean_takes S(position) - mean_takes
baseline; reduce to mean |dS| over frequency and all 16 S-parameters; summarize
per depth (median + IQR across the ~51 positions). Depths are port-relative
(z=0 at the antenna port); the 1227 session's README "2.5 cm below" is actually
+25 mm ABOVE (per Peter).
"""
import os, glob, re
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BLUE="#0B5D7A"; TEAL="#1C9AA8"; CORAL="#D64545"; AMBER="#E0A100"; INK="#1E293B"; MUTE="#5B6B7B"
OUT = os.path.dirname(__file__)
ROOT = (r"C:\Users\peter\Desktop\EM Imaging\BreastPhantom\HunterVNA\DataMeasurements"
        r"\Sam Antennas\MediumAntenna\Separated\July10\A3TumorDepthTesting_JULY10")
# session -> port-relative depth (mm); 1227 corrected to +25 (above)
SESS = {"BreastPhantom_A3_FishingWeight_20260710_1145": -20,
        "BreastPhantom_A3_FishingWeight_20260710_1122":  -7,
        "BreastPhantom_A3_FishingWeight_20260710_1207": +15,
        "BreastPhantom_A3_FishingWeight_20260710_1227": +25}

def read_meas_csv(path):
    a = np.genfromtxt(path, delimiter=",", skip_header=1)
    a = a[:, ~np.all(np.isnan(a), axis=0)]        # drop trailing empty col
    body = a[:, 1:].reshape(a.shape[0], 16, 2)
    return body[:, :, 0] * np.exp(1j*np.deg2rad(body[:, :, 1]))   # (nf,16)

def mean_over_takes(folder, stem):
    files = sorted(glob.glob(os.path.join(folder, f"{stem}_T*.csv")))
    if not files: return None
    S = [read_meas_csv(f) for f in files]
    return np.mean(S, axis=0)

per_depth = {}
for sess, z in SESS.items():
    folder = os.path.join(ROOT, sess)
    base = mean_over_takes(folder, "baseline")
    if base is None: print("no baseline", sess); continue
    stems = sorted({re.match(r"(R\d+C\d+P\d+)_T", os.path.basename(f)).group(1)
                    for f in glob.glob(os.path.join(folder, "R*C*P*_T*.csv"))})
    vals = []
    for st in stems:
        Sp = mean_over_takes(folder, st)
        if Sp is None or Sp.shape != base.shape: continue
        vals.append(np.mean(np.abs(Sp - base)))    # mean |dS| over freq & 16 params
    per_depth[z] = np.array(vals)
    print(f"z={z:+3d} mm : {len(vals)} positions, median |dS| = {np.median(vals):.4g}")

zs = np.array(sorted(per_depth))
med = np.array([np.median(per_depth[z]) for z in zs])
q1  = np.array([np.percentile(per_depth[z], 25) for z in zs])
q3  = np.array([np.percentile(per_depth[z], 75) for z in zs])

fig, ax = plt.subplots(figsize=(9.2, 5.4))
ax.fill_between(zs, q1, q3, color=TEAL, alpha=0.15, label="inter-quartile range")
ax.plot(zs, med, "-o", color=BLUE, lw=2.4, ms=10, zorder=3, label="median over positions")
ymax = max(q3)*1.16
# antenna port (z=0, definitional) and approximate radiating-patch region
ax.axvline(0, color=CORAL, lw=1.8, ls="--", zorder=2)
ax.annotate("antenna port / feed\n(z = 0, reference)", (0, ymax),
            textcoords="offset points", xytext=(-8, -2), ha="right", va="top",
            fontsize=9.5, color=CORAL, fontweight="bold")
ax.axvspan(12, 18, color=AMBER, alpha=0.18, zorder=1)
ax.annotate("radiating patch\n(~+15 mm from feed)", (15, ymax),
            textcoords="offset points", xytext=(6, -2), ha="left", va="top",
            fontsize=9.5, color="#9A6D00", fontweight="bold")
for zi, mi in zip(zs, med):
    ax.annotate(f"{zi:+d} mm", (zi, mi), textcoords="offset points", xytext=(0, 11),
                ha="center", fontsize=9.5, color=INK, fontweight="bold")
ax.set_ylim(top=ymax)
ax.set_xlabel("tumor depth z relative to antenna port (mm)", fontsize=12)
ax.set_ylabel("mean |dS|  (tumor minus empty, over freq & all 16 S-params)", fontsize=11.5)
ax.set_title("How much the tumor perturbs the MEASURED signal, by depth",
             fontsize=13.5, fontweight="bold", color=INK)
ax.grid(True, color="#EAF0F4", lw=0.7); ax.set_axisbelow(True)
for s in ax.spines.values(): s.set_color("#D8E2EA")
ax.legend(fontsize=10.5, framealpha=0.95, loc="lower center")
fig.text(0.5, 0.015,
    "4 measured tumor heights (bench VNA, empty-baseline differential). The perturbation is strongest near the\n"
    "radiating patch and falls off with distance, the same shape the simulation shows.",
    ha="center", va="bottom", fontsize=10.0, color=MUTE, style="italic")
fig.subplots_adjust(left=0.12, right=0.97, top=0.90, bottom=0.22)
p = os.path.join(OUT, "measured_dS_vs_depth.png")
fig.savefig(p, dpi=160); print("wrote", p)
