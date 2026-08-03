r"""Measured empty (metal target) narrow-band sweep to test whether ~1.75-2 GHz is
the best center. CNN under LOSO (the deck's measured protocol), band-masked.

  - 0.25 GHz windows stepped every 0.25 GHz across 1-8 GHz (1.75-2 sits among them)
  - 0.15 and 0.10 GHz windows at the low centers (1.75 / 1.875 / 2.0)

Writes results/bw_meas_narrow_empty.json.
"""
from __future__ import annotations
import sys, numpy as np, json, time
import bandwidth_sweep_reg as B
import bandwidth_cnn as C

DS = sys.argv[1] if len(sys.argv) > 1 else "empty"    # empty | F4 | F5
band = (1.0, 8.0); FG, FGG = B.make_grid(*band)
d = B.get_data(DS, FG, band); folds = d["sess"].copy()   # LOSO = session folds
ch = B.chance_baseline(d, folds)
print(f"{DS} [LOSO] {d['Yc'].shape[0]} samples, {len(np.unique(folds))} sessions, chance {ch*25.4:.1f} mm", flush=True)

bands = []
for c in np.round(np.arange(1.125, 7.876, 0.25), 3):          # 0.25 GHz across 1-8
    bands.append((round(c - 0.125, 3), round(c + 0.125, 3)))
for w in (0.15, 0.10):                                         # narrower at the low centers
    for c in (1.75, 1.875, 2.0):
        bands.append((round(c - w/2, 3), round(c + w/2, 3)))

rows = []
t0 = time.time()
for lo, hi in bands:
    cols = B._cols(FGG, (lo + hi) / 2, hi - lo)
    if cols.size < 2:
        print(f"  {lo}-{hi}: too few cols ({cols.size}), skip", flush=True); continue
    e = C.cnn_eval_band(d, cols, folds, epochs=35, n_seeds=2)
    rows.append(dict(lo=lo, hi=hi, width=round(hi - lo, 3), center=round((lo + hi) / 2, 3),
                     ncols=int(cols.size), err=e))
    print(f"  {lo}-{hi} GHz (w{round(hi-lo,3)}, {cols.size}c): {e*25.4:.1f} mm  ({time.time()-t0:.0f}s)", flush=True)

json.dump(dict(dataset=DS, mode="loso", chanceIn=ch, rows=rows),
          open(B.RESULTS / f"bw_meas_narrow_{DS}.json", "w"), indent=1)
print(f"MEAS NARROW {DS} DONE", flush=True)
