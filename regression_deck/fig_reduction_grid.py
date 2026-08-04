"""4-panel hardware x bandwidth error grid (regression), break-descent style.

Columns: FULL band first, then 3/2/1/0.5/0.25/0.1/0.05 GHz (each at the panel's
best center). Continuous red->green imshow (low error green, high red), black-box
outline on BROKEN (>20 mm) cells, '--' for skipped / not-computed.

Panels: Empty, F4, F5 (measured session-LOSO CNN) + Sim (tuned 8-fold CNN).
Measured full = bw_grid_measured_full_{ds}.json; measured widths =
bw_grid_measured_{ds}.json; sim = cnn_simreg_*_grid.json.
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
BROKEN = 20.0; VMIN, VMAX = 3.0, 20.0
CMAP = LinearSegmentedColormap.from_list(
    "err", ["#3E7A3E", "#7BA05B", "#F5E6A3", "#E8A33D", "#BE0000", "#8E1010"])

# ---- sim ----
SIM_ANT_SUF = {"16 S-params (full)": "", "4 ant, refl only": "_refl",
               "2 ant (1&3), full S": "_pair13", "2 ant (1&3), refl only": "_refl2",
               "1 ant (S11 only)": "_refl1"}
SIM_COL_SUF = {"full": "", 3.0: "_b2-5", 2.0: "_b2.25-4.25", 1.0: "_b2.75-3.75",
               0.5: "_b3-3.5", 0.25: "_b3.125-3.375", 0.1: "_b3.2-3.3", 0.05: "_b3.225-3.275"}
SIM_COL_LBL = {"full": "2-8", 3.0: "2-5", 2.0: "2.25-4.25", 1.0: "2.75-3.75",
               0.5: "3-3.5", 0.25: "3.13-3.38", 0.1: "3.2-3.3", 0.05: "3.23-3.28"}

def _read(fp):
    return json.load(open(fp))["lateral_medianMm"] if os.path.exists(fp) else None

def sim_panel():
    out = {a: {} for a in ANT_ROWS}
    for a in ANT_ROWS:
        for ck in COL_KEYS:
            fp = os.path.join(RES, f"cnn_simreg_8fold_nf256_5mmgrid{SIM_COL_SUF[ck]}{SIM_ANT_SUF[a]}_grid.json")
            v = _read(fp)
            out[a][ck] = (v, SIM_COL_LBL[ck] if v is not None else None)
    return out, "~3.25"

def meas_panel(ds):
    out = {a: {} for a in ANT_ROWS}
    try:
        full = json.load(open(os.path.join(RES, f"bw_grid_measured_full_{ds}.json")))
        for r in full["rows"]:
            out[r["antenna"]]["full"] = (r["err_mm"], "1-8")
    except FileNotFoundError:
        for a in ANT_ROWS: out[a]["full"] = (None, None)
    d = json.load(open(os.path.join(RES, f"bw_grid_measured_{ds}.json")))
    for r in d["grid"]:
        for c in r["cells"]:
            w = c["width"]
            if not c.get("skipped") and c.get("err_mm") is not None:
                b = c.get("band"); out[r["antenna"]][w] = (c["err_mm"], f"{b[0]:g}-{b[1]:g}" if b else "")
            else:
                out[r["antenna"]][w] = (None, None)
    return out, f"{d['center']:g}"

PANELS = []
for ds, disp in [("empty", "Empty"), ("F4", "F4"), ("F5", "F5")]:
    p, c = meas_panel(ds); PANELS.append((f"{disp}  (LOSO, ctr {c} GHz)", p))
p, c = sim_panel(); PANELS.append((f"Sim  (8-fold, ctr {c} GHz)", p))

def wlab(w):
    return f"{w:g} GHz" if w >= 0.999 else f"{int(round(w*1000))} MHz"
def band_w(lbl):
    try: lo, hi = [float(x) for x in lbl.split("-")]; return hi - lo
    except Exception: return None
def col_hdr(ck, lbl):
    if lbl is None: return ("full" if ck == "full" else wlab(ck))
    if ck == "full": return f"{lbl} GHz\n(full)"
    return f"{lbl} GHz\n({wlab(ck)})"

fig, axes = plt.subplots(2, 2, figsize=(16, 10.5))
for idx, (ax, (title, panel)) in enumerate(zip(axes.flat, PANELS)):
    col = idx % 2
    grid = np.full((len(ANT_ROWS), len(COL_KEYS)), np.nan)
    hdrs = [None] * len(COL_KEYS)
    for i, a in enumerate(ANT_ROWS):
        for j, ck in enumerate(COL_KEYS):
            v, lbl = panel[a].get(ck, (None, None))
            if v is not None: grid[i, j] = v
            if lbl is not None and hdrs[j] is None: hdrs[j] = col_hdr(ck, lbl)
    for j, ck in enumerate(COL_KEYS):
        if hdrs[j] is None: hdrs[j] = ("full" if ck == "full" else wlab(ck))
    ax.imshow(np.clip(grid, VMIN, VMAX), cmap=CMAP, vmin=VMIN, vmax=VMAX, aspect="auto")
    for i in range(len(ANT_ROWS)):
        for j in range(len(COL_KEYS)):
            v = grid[i, j]
            if np.isnan(v):
                ax.text(j, i, "--", ha="center", va="center", fontsize=10, color="#B9A6A2")
            else:
                broken = v > BROKEN
                ax.text(j, i, f"{v:.1f}", ha="center", va="center", fontsize=10.5,
                        fontweight="bold" if broken else "normal",
                        color="white" if v >= 12 else "#1A1A1A")
                if broken:
                    ax.add_patch(plt.Rectangle((j-.5, i-.5), 1, 1, fill=False, edgecolor="black", lw=2.6))
    ax.set_title(title, fontsize=14, fontweight="bold", color="#1E293B")
    ax.set_xticks(range(len(COL_KEYS))); ax.set_xticklabels(hdrs, fontsize=8.5, rotation=32, ha="right")
    ax.set_yticks(range(len(ANT_ROWS)))
    ax.set_yticklabels(ANT_ROWS if col == 0 else [""]*len(ANT_ROWS), fontsize=10)
    ax.tick_params(length=0)
    for s in ax.spines.values(): s.set_visible(False)

fig.suptitle("Localization error (mm): full band -> narrowing x hardware reduction  —  black box = BROKEN (>20 mm), -- = skipped / not computed",
             fontsize=14, y=0.995, color="#1E293B")
fig.text(0.5, 0.005, "First column = FULL band (measured 1-8, sim 2-8 GHz); the rest each at the panel's best center. Colour = median lateral error "
         "(green good -> red bad). Measured = session-LOSO CNN; sim = tuned 8-fold CNN. (sim 3 GHz sub-band pending.)",
         ha="center", fontsize=10, color="#5B6B7B", style="italic")
fig.tight_layout(rect=[0, 0.02, 1, 0.965])
fig.savefig(os.path.join(HERE, "reduction_grid.png"), dpi=180, bbox_inches="tight")
print("wrote reduction_grid.png")
