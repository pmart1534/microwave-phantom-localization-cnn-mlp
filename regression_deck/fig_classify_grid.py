"""Sim-vs-measured CLASSIFICATION reduction grid (LOSO position-classification %).

2x2: Empty, F4, F5 (measured) + Sim (noise-injected). Rows = hardware reduction,
cols = full band then narrowing (each panel at its own best center). Colour = LOSO
accuracy (red low -> green high); black box = BROKEN (<50%); '--' = skipped.
Reads results/classify_grid_*.json.
"""
import os, sys, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

HERE = os.path.dirname(__file__); RES = os.path.join(HERE, "..", "results")
MODEL = sys.argv[1] if len(sys.argv) > 1 else "knn"        # knn | cnn
PFX = "classify_grid_" if MODEL == "knn" else "classify_grid_cnn_"
OUT = "classify_grid.png" if MODEL == "knn" else "classify_grid_cnn.png"
MODEL_LBL = "k-NN" if MODEL == "knn" else "CNN"
COLS = ["full", "3.0", "2.0", "1.0", "0.5", "0.25", "0.1"]
ANT_ROWS = ["16 S-params (full)", "4 ant, refl only", "2 ant (1&3), full S",
            "2 ant (1&3), refl only", "1 ant (S11 only)"]
BROKEN = 50.0; VMIN, VMAX = 20.0, 100.0
CMAP = LinearSegmentedColormap.from_list(
    "acc", ["#8E1010", "#BE0000", "#E8A33D", "#F5E6A3", "#7BA05B", "#3E7A3E"])
PANELS = [("empty", "Empty"), ("F4", "F4"), ("F5", "F5"), ("sim", "Sim (noise-injected)")]


def wlab(w):
    if w == "full": return "full"
    f = float(w); return f"{f:g} GHz" if f >= 0.999 else f"{int(round(f*1000))} MHz"


def load(name):
    d = json.load(open(os.path.join(RES, f"{PFX}{name}.json")))
    grid = np.full((len(ANT_ROWS), len(COLS)), np.nan); hdr = [None]*len(COLS)
    for i, r in enumerate(d["grid"]):
        for j, c in enumerate(r["cells"]):
            if not c.get("skipped") and c.get("acc") is not None:
                grid[i, j] = c["acc"]
                b = c.get("band")
                if hdr[j] is None and b: hdr[j] = f"{b[0]:g}-{b[1]:g}\n({wlab(COLS[j])})"
    for j in range(len(COLS)):
        if hdr[j] is None: hdr[j] = wlab(COLS[j])
    return grid, hdr, d["center"], d["chance"]


fig, axes = plt.subplots(2, 2, figsize=(16, 10.5))
for idx, (ax, (name, disp)) in enumerate(zip(axes.flat, PANELS)):
    col0 = idx % 2
    try:
        grid, hdr, center, chance = load(name)
    except FileNotFoundError:
        ax.text(0.5, 0.5, f"{disp}\n(pending)", ha="center", va="center"); ax.axis("off"); continue
    ax.imshow(np.clip(grid, VMIN, VMAX), cmap=CMAP, vmin=VMIN, vmax=VMAX, aspect="auto")
    for i in range(len(ANT_ROWS)):
        for j in range(len(COLS)):
            v = grid[i, j]
            if np.isnan(v):
                ax.text(j, i, "--", ha="center", va="center", fontsize=10, color="#B9A6A2")
            else:
                bk = v < BROKEN
                ax.text(j, i, f"{v:.0f}", ha="center", va="center", fontsize=10.5,
                        fontweight="bold" if bk else "normal",
                        color="white" if v < 68 else "#1A1A1A")
                if bk:
                    ax.add_patch(plt.Rectangle((j-.5, i-.5), 1, 1, fill=False, edgecolor="black", lw=2.6))
    ax.set_title(f"{disp}  (LOSO, ctr {center:g} GHz, chance {chance:.0f}%)", fontsize=13.5, fontweight="bold", color="#1E293B")
    ax.set_xticks(range(len(COLS))); ax.set_xticklabels(hdr, fontsize=8.3, rotation=32, ha="right")
    ax.set_yticks(range(len(ANT_ROWS)))
    ax.set_yticklabels(ANT_ROWS if col0 == 0 else [""]*len(ANT_ROWS), fontsize=10)
    ax.tick_params(length=0)
    for s in ax.spines.values(): s.set_visible(False)

fig.suptitle(f"LOSO position-classification accuracy (%), {MODEL_LBL}: hardware reduction x band narrowing  —  black box = BROKEN (<50%), -- = skipped",
             fontsize=14, y=0.995, color="#1E293B")
fig.text(0.5, 0.005, f"Measured phantoms + noise-injected sim, same {MODEL_LBL} LOSO classifier; first column = full band, rest each at the panel's best "
         "center. Sim noise calibrated to the bench (per-channel SNR + cross-session drift).",
         ha="center", fontsize=10, color="#5B6B7B", style="italic")
fig.tight_layout(rect=[0, 0.02, 1, 0.965])
fig.savefig(os.path.join(HERE, OUT), dpi=180, bbox_inches="tight")
print("wrote " + OUT)
