r"""Regression (x,y) on the noise-injected sim under LOSO, across the hardware x band
reduction grid -- the regression companion to classify_grid, on augmented sim.

Uses the same synthetic sessions as sim_noise + the regression CNN
(bandwidth_cnn.cnn_eval_band) with leave-one-session-out. Writes
results/sim_reg_noisy_grid.json (median lateral error, mm).
"""
from __future__ import annotations
import numpy as np, json, time
import bandwidth_sweep_reg as B
import bandwidth_cnn as C
import sim_noise as SN

R = lambda p: (p - 1) * 4 + (p - 1)
ANT = [("16 S-params (full)",     list(range(16))),
       ("4 ant, refl only",       [R(1), R(2), R(3), R(4)]),
       ("2 ant (1&3), full S",    [0, 2, 8, 10]),
       ("2 ant (1&3), refl only", [R(1), R(3)]),
       ("1 ant (S11 only)",       [R(1)])]
WIDTHS = ["full", 3.0, 2.0, 1.0, 0.5, 0.25, 0.1]
CENTER, LO, HI, BROKEN = 3.25, 2.0, 8.0, 20.0
FGG = SN.FG / 1e9


def band_for(w):
    if w == "full": return LO, HI
    a, b = CENTER - w/2, CENTER + w/2
    if a < LO: a, b = LO, LO + w
    if b > HI: a, b = HI - w, HI
    return round(max(a, LO), 3), round(min(b, HI), 3)


if __name__ == "__main__":
    t0 = time.time()
    dS, tgt = SN.load_sim_ds(); snr, dr = SN.measured_calibration()
    data = SN.synth(dS, tgt, snr, dr * SN.DRIFT_GAIN, noise=True, drift=True)
    folds = data["sess"]
    print(f"noisy sim regression grid: {data['Yc'].shape[0]} samples, LOSO over {len(np.unique(folds))} sessions", flush=True)
    grid = []
    for label, chans in ANT:
        dd = {**data, "Yc": data["Yc"][:, chans, :]}
        row = {"antenna": label, "cells": []}; broke = False
        for w in WIDTHS:
            if broke:
                row["cells"].append({"width": str(w), "err_mm": None, "skipped": True}); continue
            bl, bh = band_for(w); cols = np.where((FGG >= bl) & (FGG <= bh))[0]
            e = C.cnn_eval_band(dd, cols, folds, epochs=30, n_seeds=1) * 25.4
            broke = e > BROKEN
            row["cells"].append({"width": str(w), "band": [bl, bh], "err_mm": round(e, 2), "broken": bool(broke)})
            print(f"  {label:24s} {str(w):>5}: {e:5.1f} mm{'  BROKEN' if broke else ''}  ({time.time()-t0:.0f}s)", flush=True)
        grid.append(row)
    json.dump(dict(dataset="sim_noisy", mode="loso", center=CENTER, brokenMm=BROKEN,
                   widths=[str(w) for w in WIDTHS], grid=grid),
              open(B.RESULTS / "sim_reg_noisy_grid.json", "w"), indent=1)
    print(f"\nSIM NOISY REGRESSION GRID DONE ({time.time()-t0:.0f}s)", flush=True)
