"""Classification reduction grid, measured panels taken DIRECTLY from the existing
classification-CNN results (cnn_loso_*, per-position LOSO vote, per-phantom best-
center ladders = analyze_break_descent_best), so Empty/F4/F5 match the prior
figure exactly. Sim panel = the noise-injected sim (classify_grid_cnn_sim).

2x2: Empty, F4 / F5, Sim. Accuracy %, red->green, black box <50% (broken), '--' skip.
"""
import os, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

HERE = os.path.dirname(__file__); RES = os.path.join(HERE, "..", "results")
CMAP = LinearSegmentedColormap.from_list("acc", ["#8E1010", "#BE0000", "#E8A33D", "#F5E6A3", "#7BA05B", "#3E7A3E"])
VMIN, VMAX, BROKEN = 20.0, 100.0, 50.0
BAND_W = ["3", "2", "1", "0.5", "0.25", "0.1", "0.05"]
HW = [("16 S-params (full)", "all_ant1-2-3-4"), ("4 ant, refl only", "refl_ant1-2-3-4"),
      ("2 ant (1&3), full S", "pair_ant1-3"), ("2 ant (1&3), refl only", "refl_ant1-3"),
      ("1 ant (S11 only)", "single_ant1")]
ANT_ROWS = [h[0] for h in HW]
# measured: (display, json prefix, best-center band ladder) -- from analyze_break_descent_best
MEAS = {
    "Empty  (LOSO, ctr ~1.875 GHz)": ("June18_remap",
        ["1-4", "2-4", "1.5-2.5", "1.5-2", "2-2.25", "1.825-1.925", "1.85-1.9"]),
    "F4  (LOSO, ctr ~3.0 GHz)": ("A3_F4_SamMed_all4",
        ["1-4", "2-4", "2.5-3.5", "2.5-3", "3-3.25", "2.95-3.05", "2.975-3.025"]),
    "F5  (LOSO, ctr ~2.25 GHz)": ("A3_F5_SamMed_last3",
        ["1-4", "2-4", "2-3", "2-2.5", "2-2.25", "2.2-2.3", "2.225-2.275"]),
}


def meas_panel(pre, bands):
    grid = np.full((len(HW), len(bands)), np.nan)
    for i, (_, tag) in enumerate(HW):
        broke = False
        for j, b in enumerate(bands):
            if broke: continue
            f = os.path.join(RES, f"cnn_loso_{pre}_raw_{tag}_band{b}.json")
            if not os.path.exists(f): continue
            v = json.load(open(f))["losoPosMean"]; grid[i, j] = v
            if v < BROKEN: broke = True
    hdr = [f"{b}\n({w} GHz)" for b, w in zip(bands, BAND_W)]
    return grid, hdr


def sim_panel():
    d = json.load(open(os.path.join(RES, "classify_grid_cnn_sim.json")))
    cols = d["widths"]; grid = np.full((len(HW), len(cols)), np.nan); hdr = [None]*len(cols)
    def wl(w):
        if w == "full": return "full"
        f = float(w); return f"{f:g} GHz" if f >= 0.999 else f"{int(round(f*1000))} MHz"
    for i, r in enumerate(d["grid"]):
        for j, c in enumerate(r["cells"]):
            if not c.get("skipped") and c.get("acc") is not None:
                grid[i, j] = c["acc"]
                if hdr[j] is None and c.get("band"): hdr[j] = f"{c['band'][0]:g}-{c['band'][1]:g}\n({wl(cols[j])})"
    for j in range(len(cols)):
        if hdr[j] is None: hdr[j] = wl(cols[j])
    return grid, hdr


PANELS = [(name,) + meas_panel(pre, bands) for name, (pre, bands) in MEAS.items()]
PANELS.append(("Sim (noise-injected, LOSO)",) + sim_panel())

fig, axes = plt.subplots(2, 2, figsize=(16, 10.5))
for idx, (ax, (title, grid, hdr)) in enumerate(zip(axes.flat, PANELS)):
    col0 = idx % 2
    ax.imshow(np.clip(grid, VMIN, VMAX), cmap=CMAP, vmin=VMIN, vmax=VMAX, aspect="auto")
    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            v = grid[i, j]
            if np.isnan(v):
                ax.text(j, i, "--", ha="center", va="center", fontsize=10, color="#B9A6A2")
            else:
                bk = v < BROKEN
                ax.text(j, i, f"{v:.0f}", ha="center", va="center", fontsize=10.5,
                        fontweight="bold" if bk else "normal", color="white" if v < 68 else "#1A1A1A")
                if bk:
                    ax.add_patch(plt.Rectangle((j-.5, i-.5), 1, 1, fill=False, edgecolor="black", lw=2.6))
    ax.set_title(title, fontsize=13.5, fontweight="bold", color="#1E293B")
    ax.set_xticks(range(len(hdr))); ax.set_xticklabels(hdr, fontsize=8.3, rotation=32, ha="right")
    ax.set_yticks(range(len(ANT_ROWS)))
    ax.set_yticklabels(ANT_ROWS if col0 == 0 else [""]*len(ANT_ROWS), fontsize=10)
    ax.tick_params(length=0)
    for s in ax.spines.values(): s.set_visible(False)

fig.suptitle("LOSO position-classification accuracy (%): hardware reduction x band narrowing  —  black box = BROKEN (<50%), -- = skipped",
             fontsize=14, y=0.995, color="#1E293B")
fig.text(0.5, 0.005, "Measured (Empty/F4/F5) = the classification-CNN track (cnn_loso, per-position LOSO vote), each at its own best center - matches the prior figure. "
         "Sim = noise-injected sim, calibrated to the bench (per-channel SNR + drift).",
         ha="center", fontsize=10, color="#5B6B7B", style="italic")
fig.tight_layout(rect=[0, 0.02, 1, 0.965])
fig.savefig(os.path.join(HERE, "classify_grid_matched.png"), dpi=180, bbox_inches="tight")
print("wrote classify_grid_matched.png")
