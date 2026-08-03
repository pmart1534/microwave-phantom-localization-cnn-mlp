r"""Measured hardware x bandwidth error GRID (regression, session-LOSO CNN).

For each measured phantom (empty/F4/F5): 5 antenna configs x 7 band widths, at
that phantom's OWN best center (read from its bw_meas_narrow sweep). 3-tier /
skip-after-break: once a cell exceeds BROKEN mm, the rest of that (narrower) row
is skipped. Writes results/bw_grid_measured_{ds}.json.

Companion to the sim MATLAB grid (run_sim_grid.ps1 -> cnn_simreg_*_grid.json).
"""
from __future__ import annotations
import os, json, time
import numpy as np
import bandwidth_sweep_reg as B
import bandwidth_cnn as C

R = lambda p: (p - 1) * 4 + (p - 1)
ANT = [                                    # (label, channel indices), Deck-1 order
    ("16 S-params (full)",      list(range(16))),
    ("4 ant, refl only",        [R(1), R(2), R(3), R(4)]),
    ("2 ant (1&3), full S",     [0, 2, 8, 10]),         # S11,S13,S31,S33
    ("2 ant (1&3), refl only",  [R(1), R(3)]),
    ("1 ant (S11 only)",        [R(1)]),
]
WIDTHS = [3.0, 2.0, 1.0, 0.5, 0.25, 0.1, 0.05]
BROKEN = 20.0
LO, HI = 1.0, 8.0                          # measured cache band
EPOCHS, SEEDS = 35, 2


def best_center(ds):
    """Best 0.25 GHz-window center from the phantom's narrow sweep."""
    fp = B.RESULTS / f"bw_meas_narrow_{ds}.json"
    d = json.load(open(fp))
    q = [r for r in d["rows"] if abs(r["width"] - 0.25) < 1e-6]
    return min(q, key=lambda r: r["err"])["center"]


def band_for(center, w):
    lo, hi = center - w / 2, center + w / 2   # keep width, shift to fit [LO,HI]
    if lo < LO: lo, hi = LO, LO + w
    if hi > HI: lo, hi = HI - w, HI
    return round(max(lo, LO), 3), round(min(hi, HI), 3)


def run(ds):
    full = (LO, HI); FG, FGG = B.make_grid(*full)
    data = B.get_data(ds, FG, full); folds = data["sess"].copy()   # session LOSO
    ch = B.chance_baseline(data, folds)
    c0 = best_center(ds)
    print(f"\n===== {ds} [LOSO] center {c0} GHz, chance {ch*25.4:.1f} mm =====", flush=True)
    grid = []
    for label, chans in ANT:
        sub = {**data, "Yc": data["Yc"][:, chans, :]}
        row = {"antenna": label, "cells": []}
        broke = False
        for w in WIDTHS:
            if broke:
                row["cells"].append({"width": w, "err_mm": None, "skipped": True}); continue
            lo, hi = band_for(c0, w)
            cols = B._cols(FGG, (lo + hi) / 2, hi - lo)
            e = C.cnn_eval_band(sub, cols, folds, epochs=EPOCHS, n_seeds=SEEDS) * 25.4
            broke = e > BROKEN
            row["cells"].append({"width": w, "band": [lo, hi], "err_mm": round(e, 2),
                                 "broken": bool(broke)})
            print(f"  {label:24s} {w:>4}GHz [{lo:g}-{hi:g}]: {e:5.1f} mm"
                  f"{'  BROKEN' if broke else ''}", flush=True)
        grid.append(row)
    out = dict(dataset=ds, mode="loso", center=c0, chanceIn=ch, brokenMm=BROKEN,
               widths=WIDTHS, grid=grid)
    json.dump(out, open(B.RESULTS / f"bw_grid_measured_{ds}.json", "w"), indent=1)
    print(f"  saved bw_grid_measured_{ds}.json", flush=True)


if __name__ == "__main__":
    t0 = time.time()
    for ds in ["empty", "F4", "F5"]:
        run(ds)
    print(f"\nALL MEASURED GRIDS DONE ({time.time()-t0:.0f}s)", flush=True)
