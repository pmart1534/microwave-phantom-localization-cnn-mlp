r"""Full-bandwidth (1-8 GHz) column for the measured hardware x bandwidth grid.

Same method as bandwidth_grid_measured.py (session-LOSO CNN, 5 antenna configs),
but at the FULL 1-8 GHz band -- the reference column so we can see how much
accuracy is lost by narrowing. Writes results/bw_grid_measured_full_{ds}.json.
"""
from __future__ import annotations
import numpy as np, json, time
import bandwidth_sweep_reg as B
import bandwidth_cnn as C

R = lambda p: (p - 1) * 4 + (p - 1)
ANT = [
    ("16 S-params (full)",     list(range(16))),
    ("4 ant, refl only",       [R(1), R(2), R(3), R(4)]),
    ("2 ant (1&3), full S",    [0, 2, 8, 10]),
    ("2 ant (1&3), refl only", [R(1), R(3)]),
    ("1 ant (S11 only)",       [R(1)]),
]
EPOCHS, SEEDS = 35, 2

t0 = time.time()
for ds in ["empty", "F4", "F5"]:
    FG, FGG = B.make_grid(1.0, 8.0)
    data = B.get_data(ds, FG, (1.0, 8.0)); folds = data["sess"].copy()
    ch = B.chance_baseline(data, folds)
    cols = np.arange(FG.size)                          # full 1-8 GHz
    print(f"\n=== {ds} [LOSO] full 1-8 GHz ({cols.size} pts), chance {ch*25.4:.1f} mm ===", flush=True)
    rows = []
    for label, chans in ANT:
        sub = {**data, "Yc": data["Yc"][:, chans, :]}
        e = C.cnn_eval_band(sub, cols, folds, epochs=EPOCHS, n_seeds=SEEDS) * 25.4
        rows.append({"antenna": label, "err_mm": round(e, 2), "band": [1.0, 8.0]})
        print(f"  {label:24s}: {e:5.1f} mm  ({time.time()-t0:.0f}s)", flush=True)
    json.dump(dict(dataset=ds, mode="loso", band=[1.0, 8.0], chanceIn=ch, rows=rows),
              open(B.RESULTS / f"bw_grid_measured_full_{ds}.json", "w"), indent=1)
    print(f"  saved bw_grid_measured_full_{ds}.json", flush=True)
print(f"\nMEASURED FULL-BAND COLUMN DONE ({time.time()-t0:.0f}s)", flush=True)
