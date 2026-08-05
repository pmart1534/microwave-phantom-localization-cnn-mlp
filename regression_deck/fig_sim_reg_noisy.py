"""Regression (x,y) on the noise-injected sim, LOSO, across hardware x band reduction.
Single panel; median lateral error (mm); green low -> red high; black box > 20 mm.
Reads results/sim_reg_noisy_grid.json.
"""
import os, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

HERE = os.path.dirname(__file__); RES = os.path.join(HERE, "..", "results")
BROKEN, VMIN, VMAX = 20.0, 3.0, 20.0
CMAP = LinearSegmentedColormap.from_list("err", ["#3E7A3E", "#7BA05B", "#F5E6A3", "#E8A33D", "#BE0000", "#8E1010"])

d = json.load(open(os.path.join(RES, "sim_reg_noisy_grid.json")))
rows = [r["antenna"] for r in d["grid"]]
cols = d["widths"]

def wlab(w):
    if w == "full": return "full\n(2-8)"
    f = float(w); return f"{f:g} GHz" if f >= 0.999 else f"{int(round(f*1000))} MHz"

grid = np.full((len(rows), len(cols)), np.nan); bands = [None]*len(cols)
for i, r in enumerate(d["grid"]):
    for j, c in enumerate(r["cells"]):
        if not c.get("skipped") and c.get("err_mm") is not None:
            grid[i, j] = c["err_mm"]
            if bands[j] is None and c.get("band"): bands[j] = f"{c['band'][0]:g}-{c['band'][1]:g}"

fig, ax = plt.subplots(figsize=(9.5, 5.2))
ax.imshow(np.clip(grid, VMIN, VMAX), cmap=CMAP, vmin=VMIN, vmax=VMAX, aspect="auto")
for i in range(len(rows)):
    for j in range(len(cols)):
        v = grid[i, j]
        if np.isnan(v):
            ax.text(j, i, "--", ha="center", va="center", fontsize=10, color="#B9A6A2")
        else:
            bk = v > BROKEN
            ax.text(j, i, f"{v:.1f}", ha="center", va="center", fontsize=10.5,
                    fontweight="bold" if bk else "normal", color="white" if v >= 12 else "#1A1A1A")
            if bk: ax.add_patch(plt.Rectangle((j-.5, i-.5), 1, 1, fill=False, edgecolor="black", lw=2.4))
ax.set_xticks(range(len(cols)))
ax.set_xticklabels([f"{bands[j]}\n({wlab(cols[j])})" if bands[j] and cols[j] != 'full' else wlab(cols[j]) for j in range(len(cols))],
                   fontsize=8.5, rotation=32, ha="right")
ax.set_yticks(range(len(rows))); ax.set_yticklabels(rows, fontsize=10)
ax.tick_params(length=0)
for s in ax.spines.values(): s.set_visible(False)
ax.set_title(f"Regression (x,y) on the noise-injected sim  (LOSO, ctr {d['center']:g} GHz)", fontsize=13.5, fontweight="bold", color="#1E293B")
fig.text(0.5, -0.02, "Median lateral error (mm); green good -> red bad; black box = >20 mm. Noise-injected sim, leave-one-session-out. "
         "Reflection-only beats all-16 here: the low-SNR transmission channels add more noise than signal once realistic noise is present.",
         ha="center", fontsize=9.3, color="#5B6B7B", style="italic", wrap=True)
fig.tight_layout(rect=[0, 0.03, 1, 1])
fig.savefig(os.path.join(HERE, "sim_reg_noisy_grid.png"), dpi=180, bbox_inches="tight")
print("wrote sim_reg_noisy_grid.png")
