r"""Sim-vs-measured CLASSIFICATION reduction grid (LOSO position classification).

Noise-injected sim (synthetic sessions) and each measured phantom, under the same
protocol: k-NN position classifier, per-session z-score, leave-one-session-out.
Grid = antenna reduction x band narrowing, each dataset at its own best center.
Skip-after-break: once accuracy < 50% (BROKEN) the rest of that row is skipped.

k-NN is the fast stand-in; the CNN full-config anchor is 99.5% (classify_cnn) ~
k-NN's 100%, so the breakage pattern is faithful. Writes results/classify_grid_*.json.
"""
from __future__ import annotations
import sys, numpy as np, json, time
import bandwidth_sweep_reg as B
import sim_noise as SN

MODEL = sys.argv[1] if len(sys.argv) > 1 else "knn"   # knn (fast) | cnn (actual model)
if MODEL == "cnn":
    import classify_cnn as CC

R = lambda p: (p - 1) * 4 + (p - 1)
ANT = [("16 S-params (full)",     list(range(16))),
       ("4 ant, refl only",       [R(1), R(2), R(3), R(4)]),
       ("2 ant (1&3), full S",    [0, 2, 8, 10]),
       ("2 ant (1&3), refl only", [R(1), R(3)]),
       ("1 ant (S11 only)",       [R(1)])]
WIDTHS = ["full", 3.0, 2.0, 1.0, 0.5, 0.25, 0.1]
BROKEN_ACC = 50.0
CENTER = {"empty": 2.125, "F4": 2.875, "F5": 3.375, "sim": 3.25}


def band_for(center, w, lo, hi):
    if w == "full": return lo, hi
    a, b = center - w/2, center + w/2
    if a < lo: a, b = lo, lo + w
    if b > hi: a, b = hi - w, hi
    return round(max(a, lo), 3), round(min(b, hi), 3)


def get_ds(name):
    if name == "sim":
        dS, tgt = SN.load_sim_ds(); snr, dr = SN.measured_calibration()
        data = SN.synth(dS, tgt, snr, dr * SN.DRIFT_GAIN, noise=True, drift=True)
        return data, SN.FG / 1e9, 2.0, 8.0
    FG, FGG = B.make_grid(1.0, 8.0)
    return B.get_data(name, FG, (1.0, 8.0)), FGG, 1.0, 8.0


def run(name):
    t0 = time.time()
    data, FGG, lo, hi = get_ds(name); center = CENTER[name]
    nclass = int(len(np.unique(data["pos"])))
    print(f"\n=== {name}  ({nclass}-class, chance {100/nclass:.1f}%, center {center} GHz) ===", flush=True)
    grid = []
    for label, chans in ANT:
        row = {"antenna": label, "cells": []}; broke = False
        for w in WIDTHS:
            if broke:
                row["cells"].append({"width": w, "acc": None, "skipped": True}); continue
            bl, bh = band_for(center, w, lo, hi)
            cols = np.where((FGG >= bl) & (FGG <= bh))[0]
            dd = {**data, "Yc": data["Yc"][:, chans, :][:, :, cols]}
            acc = (CC.cnn_classify_loso(dd, epochs=30, n_seeds=1) if MODEL == "cnn"
                   else SN.knn_classify_loso(dd)) * 100
            broke = acc < BROKEN_ACC
            row["cells"].append({"width": w, "band": [bl, bh], "acc": round(acc, 1), "broken": bool(broke)})
            print(f"  {label:24s} {str(w):>5}: {acc:5.1f}%{'  BROKEN' if broke else ''}", flush=True)
        grid.append(row)
    fn = f"classify_grid_{name}.json" if MODEL == "knn" else f"classify_grid_cnn_{name}.json"
    json.dump(dict(dataset=name, model=MODEL, center=center, nclass=nclass, chance=100/nclass,
                   widths=[str(w) for w in WIDTHS], grid=grid),
              open(B.RESULTS / fn, "w"), indent=1)
    print(f"  saved {fn} ({time.time()-t0:.0f}s)", flush=True)


if __name__ == "__main__":
    print(f"model = {MODEL}", flush=True)
    for ds in ["sim", "empty", "F4", "F5"]:
        run(ds)
    print("\nCLASSIFY GRID DONE", flush=True)
