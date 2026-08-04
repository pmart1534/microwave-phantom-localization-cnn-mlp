"""Sim-only: lateral (x,y) vs depth (z) error across hardware x bandwidth reduction.

Measured is single-depth so there's no z to compare; this shows how the SAME
reductions affect the sim CNN's lateral and depth resolution side by side.
Reads results/cnn_simreg_*_grid.json (lateral_medianMm, depth_medianMm).
Break-descent style: continuous colormap, black box on broken cells, '--' missing.
"""
import os, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

HERE = os.path.dirname(__file__); RES = os.path.join(HERE, "..", "results")
COL_KEYS = ["full", 3.0, 2.0, 1.0, 0.5, 0.25, 0.1, 0.05]
ANT_ROWS = ["16 S-params (full)", "4 ant, refl only", "2 ant (1&3), full S",
            "2 ant (1&3), refl only", "1 ant (S11 only)"]
CMAP = LinearSegmentedColormap.from_list(
    "err", ["#3E7A3E", "#7BA05B", "#F5E6A3", "#E8A33D", "#BE0000", "#8E1010"])
SIM_ANT_SUF = {"16 S-params (full)": "", "4 ant, refl only": "_refl",
               "2 ant (1&3), full S": "_pair13", "2 ant (1&3), refl only": "_refl2",
               "1 ant (S11 only)": "_refl1"}
SIM_COL_SUF = {"full": "", 3.0: "_b2-5", 2.0: "_b2.25-4.25", 1.0: "_b2.75-3.75",
               0.5: "_b3-3.5", 0.25: "_b3.125-3.375", 0.1: "_b3.2-3.3", 0.05: "_b3.225-3.275"}
SIM_COL_LBL = {"full": "2-8", 3.0: "2-5", 2.0: "2.25-4.25", 1.0: "2.75-3.75",
               0.5: "3-3.5", 0.25: "3.13-3.38", 0.1: "3.2-3.3", 0.05: "3.23-3.28"}

def cell(ant, ck, field):
    fp = os.path.join(RES, f"cnn_simreg_8fold_nf256_5mmgrid{SIM_COL_SUF[ck]}{SIM_ANT_SUF[ant]}_grid.json")
    return json.load(open(fp))[field] if os.path.exists(fp) else None

def wlab(w): return f"{w:g} GHz" if w >= 0.999 else f"{int(round(w*1000))} MHz"
def hdr(ck):
    lbl = SIM_COL_LBL[ck]
    return f"{lbl} GHz\n(full)" if ck == "full" else f"{lbl} GHz\n({wlab(ck)})"

# (field, title, vmin, vmax, broken, chance)
PANELS = [("lateral_medianMm", "Sim lateral (x,y) error", 3.0, 20.0, 20.0, 33.9),
          ("depth_medianMm",   "Sim depth (z) error",     2.0, 10.0, 10.0, 16.3)]

fig, axes = plt.subplots(1, 2, figsize=(13, 4.8))
for ax, (field, title, vmin, vmax, broken, chance) in zip(axes, PANELS):
    grid = np.full((len(ANT_ROWS), len(COL_KEYS)), np.nan)
    for i, a in enumerate(ANT_ROWS):
        for j, ck in enumerate(COL_KEYS):
            v = cell(a, ck, field)
            if v is not None: grid[i, j] = v
    ax.imshow(np.clip(grid, vmin, vmax), cmap=CMAP, vmin=vmin, vmax=vmax, aspect="auto")
    for i in range(len(ANT_ROWS)):
        for j in range(len(COL_KEYS)):
            v = grid[i, j]
            if np.isnan(v):
                ax.text(j, i, "--", ha="center", va="center", fontsize=10, color="#B9A6A2")
            else:
                bk = v > broken
                ax.text(j, i, f"{v:.1f}", ha="center", va="center", fontsize=9.0,
                        fontweight="bold" if bk else "normal",
                        color="white" if v >= (vmin + 0.55*(vmax-vmin)) else "#1A1A1A")
                if bk:
                    ax.add_patch(plt.Rectangle((j-.5, i-.5), 1, 1, fill=False, edgecolor="black", lw=2.4))
    ax.set_title(f"{title}   (chance {chance:.0f} mm, broken >{broken:.0f})", fontsize=12, fontweight="bold", color="#1E293B")
    ax.set_xticks(range(len(COL_KEYS))); ax.set_xticklabels([hdr(c) for c in COL_KEYS], fontsize=7.0, rotation=32, ha="right")
    ax.set_yticks(range(len(ANT_ROWS)))
    ax.set_yticklabels(ANT_ROWS if ax is axes[0] else [""]*len(ANT_ROWS), fontsize=9)
    ax.tick_params(length=0)
    for s in ax.spines.values(): s.set_visible(False)

fig.suptitle("Simulated CNN: lateral vs depth resolution across hardware reduction x band narrowing  (tuned 8-fold, ctr ~3.25 GHz)",
             fontsize=12.5, y=1.0, color="#1E293B")
fig.text(0.5, -0.04, "Sim only (measured is single-depth). Depth (z) is resolved BETTER than lateral and degrades more gently. "
         "Same cells as the lateral grid, so cells skipped there (lateral >20) are '--' here too. (3 GHz = 2-5 GHz sub-band pending.)",
         ha="center", fontsize=9.3, color="#5B6B7B", style="italic")
fig.tight_layout(rect=[0, 0, 1, 0.94])
fig.savefig(os.path.join(HERE, "sim_depth_grid.png"), dpi=180, bbox_inches="tight")
print("wrote sim_depth_grid.png")
