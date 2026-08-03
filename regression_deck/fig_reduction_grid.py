"""4-panel hardware x bandwidth error grid (regression).

Panels: Empty, F4, F5 (measured session-LOSO CNN) + Sim (tuned 8-fold CNN),
each optimized to its OWN best center. Rows = antenna/feature reduction,
cols = band width. Cell = lateral error (mm), 3-tier:
  <10 good (green) | 10-20 degraded (yellow->orange) | >20 BROKEN (black box).
Skipped-after-break cells show '--'.

Measured grids: results/bw_grid_measured_{ds}.json (structured).
Sim grid: per-cell results/cnn_simreg_*_grid.json (reconstructed + skip rule).
"""
import os, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Rectangle

HERE = os.path.dirname(__file__); RES = os.path.join(HERE, "..", "results")
INK = "#1E293B"; MUTE = "#5B6B7B"
WIDTHS = [3.0, 2.0, 1.0, 0.5, 0.25, 0.1, 0.05]
ANT_ROWS = ["16 S-params (full)", "4 ant, refl only", "2 ant (1&3), full S",
            "2 ant (1&3), refl only", "1 ant (S11 only)"]
BROKEN = 20.0
# green -> yellow -> orange over [0,20]; >20 handled separately (black)
CMAP = LinearSegmentedColormap.from_list("gyo", ["#2E7D5B", "#7DBb6a", "#E8D34e", "#E8973a", "#D8563a"])

# ---- sim: reconstruct grid from per-cell JSONs + skip-after-break ----
SIM_ANT_SUF = {"16 S-params (full)": "", "4 ant, refl only": "_refl",
               "2 ant (1&3), full S": "_pair13", "2 ant (1&3), refl only": "_refl2",
               "1 ant (S11 only)": "_refl1"}
SIM_BAND_SUF = {3.0: None, 2.0: "_b2.25-4.25", 1.0: "_b2.75-3.75", 0.5: "_b3-3.5",
                0.25: "_b3.125-3.375", 0.1: "_b3.2-3.3", 0.05: "_b3.225-3.275"}
SIM_BANDLBL = {3.0: "2-8", 2.0: "2.25-4.25", 1.0: "2.75-3.75", 0.5: "3-3.5",
               0.25: "3.13-3.38", 0.1: "3.2-3.3", 0.05: "3.23-3.28"}

def sim_cell(ant, w):
    suf = SIM_BAND_SUF[w]; band = "" if suf is None else suf
    fp = os.path.join(RES, f"cnn_simreg_8fold_nf256_5mmgrid{band}{SIM_ANT_SUF[ant]}_grid.json")
    if not os.path.exists(fp): return None
    return json.load(open(fp))["lateral_medianMm"]

def sim_grid():
    rows = []
    for ant in ANT_ROWS:
        cells = []; broke = False
        for w in WIDTHS:
            if broke: cells.append((None, True, None)); continue
            v = sim_cell(ant, w)
            if v is None: cells.append((None, True, None)); continue
            broke = v > BROKEN
            cells.append((v, False, SIM_BANDLBL[w]))
        rows.append(cells)
    # widest labels for the x axis come from SIM_BANDLBL
    return rows, {w: SIM_BANDLBL[w] for w in WIDTHS}

def meas_grid(ds):
    d = json.load(open(os.path.join(RES, f"bw_grid_measured_{ds}.json")))
    lbl = {}
    rows = []
    for r in d["grid"]:
        cells = []
        for c in r["cells"]:
            if c.get("skipped"): cells.append((None, True, None))
            else:
                b = c.get("band"); ll = f"{b[0]:g}-{b[1]:g}" if b else ""
                lbl[c["width"]] = ll
                cells.append((c["err_mm"], False, ll))
        rows.append(cells)
    return rows, lbl, d["center"], d["chanceIn"]

PANELS = []
for ds in ["empty", "F4", "F5"]:
    try:
        rows, lbl, c0, ch = meas_grid(ds)
        PANELS.append((f"{ds}  (LOSO, ctr {c0:g} GHz)", rows, lbl))
    except FileNotFoundError:
        PANELS.append((f"{ds} (pending)", None, None))
srows, slbl = sim_grid()
PANELS.append(("Sim  (8-fold, ctr ~3.25 GHz)", srows, slbl))

fig, axs = plt.subplots(1, 4, figsize=(20, 5.2))
for ax, (title, rows, lbl) in zip(axs, PANELS):
    ax.set_title(title, fontsize=12.5, fontweight="bold", color=INK)
    ax.set_xlim(0, len(WIDTHS)); ax.set_ylim(0, len(ANT_ROWS)); ax.invert_yaxis()
    if rows is None:
        ax.text(len(WIDTHS)/2, len(ANT_ROWS)/2, "pending", ha="center", va="center", color=MUTE); continue
    for ri, cells in enumerate(rows):
        for ci, (v, skipped, _) in enumerate(cells):
            x, y = ci, ri
            if skipped:
                ax.add_patch(Rectangle((x, y), 1, 1, facecolor="white", edgecolor="#E7D6D1"))
                ax.text(x+0.5, y+0.5, "--", ha="center", va="center", color="#B9A6A2", fontsize=11)
            elif v > BROKEN:
                ax.add_patch(Rectangle((x, y), 1, 1, facecolor="#1A1A1A", edgecolor="k", linewidth=1.5))
                ax.text(x+0.5, y+0.5, f"{v:.0f}", ha="center", va="center", color="white", fontsize=10, fontweight="bold")
            else:
                col = CMAP(min(v, BROKEN)/BROKEN)
                ax.add_patch(Rectangle((x, y), 1, 1, facecolor=col, edgecolor="white", linewidth=1))
                ax.text(x+0.5, y+0.5, f"{v:.1f}", ha="center", va="center", color=INK, fontsize=9.5)
    ax.set_xticks(np.arange(len(WIDTHS))+0.5)
    ax.set_xticklabels([f"{lbl.get(w,'')}\n({w:g} GHz)" for w in WIDTHS], fontsize=8)
    ax.set_yticks(np.arange(len(ANT_ROWS))+0.5); ax.set_yticklabels(ANT_ROWS, fontsize=9)
    ax.tick_params(length=0)
    for s in ax.spines.values(): s.set_visible(False)

fig.suptitle("Localization error (mm) across hardware reduction x band narrowing  —  black = BROKEN (>20 mm), -- = skipped after break",
             fontsize=13.5, fontweight="bold", color=INK, y=1.02)
fig.text(0.5, -0.02, "Each panel optimized to its own best center (measured empty ~2.1, F4 ~2.9, F5 ~3.4, sim ~3.25 GHz). Cell = median lateral error; "
         "green <10 mm, yellow/orange 10-20, black >20 (broken). Measured = session-LOSO CNN; sim = tuned 8-fold CNN.",
         ha="center", fontsize=9.5, color=MUTE, style="italic")
fig.tight_layout(rect=[0, 0, 1, 1])
fig.savefig(os.path.join(HERE, "reduction_grid.png"), dpi=160, bbox_inches="tight"); print("wrote reduction_grid.png")
