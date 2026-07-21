"""Deck 2 - leave-one-depth-out error vs depth, edges highlighted.

Shows the CNN predicts an *unseen* depth plane to ~1-3 mm through the interior,
while the two range extremes (extrapolation) blow up. Annotates the key finding:
when the sweep stopped at -5/+30 those planes WERE the bad edges; extending the
range made them interior and they dropped to ~1-3 mm -> usable depth is bounded
by the sampling range, not the model.
"""
import json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

NAVY="#0E2233"; BLUE="#0B5D7A"; TEAL="#1C9AA8"; MINT="#2CC4A3"
CORAL="#D64545"; AMBER="#E0A100"; INK="#1E293B"; MUTE="#5B6B7B"
R = os.path.join(os.path.dirname(__file__), "..", "results")
OUT = os.path.dirname(__file__)

d = json.load(open(os.path.join(R, "cnn_simreg_depthCV_nf256_5mmgrid.json")))
folds = d["folds"]
z   = np.array([int(f["label"].split("=")[1].replace("mm","").strip()) for f in folds])
xy  = np.array([f["xyMedMm"] for f in folds])
zz  = np.array([f["zMedMm"] for f in folds])
edge= np.array([bool(f["isEdge"]) for f in folds])

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.6, 5.2))

for ax, val, lbl, col in [(ax1, xy, "lateral (xy) error", BLUE),
                          (ax2, zz, "depth (z) error", TEAL)]:
    # sampled-range shading (interior span)
    ax.axvspan(z[~edge].min(), z[~edge].max(), color=MINT, alpha=0.06, zorder=0)
    ax.plot(z, val, "-", color=col, lw=2.2, zorder=2)
    ax.plot(z[~edge], val[~edge], "o", color=col, ms=9, zorder=3, label="interior (unseen, interpolated)")
    ax.plot(z[edge], val[edge], "o", color=CORAL, ms=13, mfc="none", mew=2.6, zorder=4,
            label="outer edge depth (extrapolated)")
    for zi, vi in zip(z[edge], val[edge]):
        ax.annotate(f"{vi:.1f}", (zi, vi), textcoords="offset points", xytext=(0, 10),
                    ha="center", color=CORAL, fontsize=10, fontweight="bold")
    ax.set_xlabel("tumor depth z (mm)", fontsize=11)
    ax.set_ylabel(f"{lbl}, median (mm)", fontsize=11)
    ax.grid(True, color="#EAF0F4", lw=0.7)
    ax.set_axisbelow(True)
    ax.legend(loc="upper center", fontsize=9.5, framealpha=0.95)
    ax.set_ylim(0, max(val)*1.18)
    for s in ax.spines.values(): s.set_color("#D8E2EA")

ax1.set_title("Predicting an UNSEEN depth plane (leave-one-depth-out)",
              fontsize=12.5, fontweight="bold", color=INK)
ax2.set_title("Depth resolves to ~1-3 mm through the interior",
              fontsize=12.5, fontweight="bold", color=INK)

# key finding callout across the bottom (wrapped so the plot is not squished)
fig.text(0.5, 0.02,
    "Interior depths are predicted almost as well as trained ones (a continuous learned depth map); the two outer\n"
    "edge depths (-15 / +45 mm) are pure extrapolation. Earlier, when the sweep stopped at -5 / +30 mm, those planes\n"
    "were the bad outer edges (z error 6-8 mm); extending the range made them interior, dropping to ~1-3 mm.\n"
    "Usable depth is bounded by the sampling range, not the model.",
    ha="center", va="bottom", fontsize=10.0, color=MUTE, style="italic")

fig.subplots_adjust(left=0.06, right=0.98, top=0.90, bottom=0.24, wspace=0.16)
p = os.path.join(OUT, "sim_depth_lopo.png")
fig.savefig(p, dpi=160); print("wrote", p)
