r"""Clean bandwidth comparison: vary ONLY the frequency band, holding protocol and
data fixed at the DECK's settings so it lines up with the deck's ~3.9 mm numbers.

  measured (empty/F4/F5) : LOSO (leave-one-session-out), all takes
  sim_all                : 8-fold position-disjoint CV over (x,y), FULL depth stack

Same small CNN as bandwidth_cnn (coarse center x width grid). k-NN is recorded
too, but note it SATURATES (~0) under measured LOSO (it just retrieves the known
position); it is only meaningful for sim's position-disjoint folds.
"""
from __future__ import annotations
import numpy as np, json, time
import bandwidth_sweep_reg as B
import bandwidth_cnn as C

JOBS = [("empty", "loso"), ("F4", "loso"), ("F5", "loso"), ("sim_all", "pos8")]


def folds_for(data, mode):
    if mode == "loso":
        return data["sess"].copy()
    if mode == "pos8":
        return B.foldize(data["pos"], k=8)
    raise ValueError(mode)


for ds, mode in JOBS:
    t0 = time.time()
    band = B.DEFAULT_BAND[ds]; FG, FGG = B.make_grid(*band)
    data = B.get_data(ds, FG, band); folds = folds_for(data, mode)
    ch = B.chance_baseline(data, folds)
    print(f"\n===== {ds} [{mode}]  {data['Yc'].shape[0]} samples, "
          f"{len(np.unique(data['pos']))} positions, {len(np.unique(folds))} folds, "
          f"chance {ch*25.4:.1f} mm =====", flush=True)
    dr_cnn = C.sweep_dense_cnn(data, FGG, band, folds)
    dr_knn = [dict(center=r["center"], width=r["width"], ncols=r["ncols"],
                   err=B.eval_band(data, B._cols(FGG, r["center"], r["width"]), folds, "knn"))
              for r in dr_cnn]
    out = dict(dataset=ds, mode=mode, band=band, chanceIn=ch,
               nPositions=int(len(np.unique(data["pos"]))), nSamples=int(data["Yc"].shape[0]),
               widths=C.CNN_WIDTHS, center_step=C.CNN_CENTER_STEP,
               epochs=C.EPOCHS, n_seeds=C.N_SEEDS, dense_cnn=dr_cnn, dense_knn=dr_knn)
    json.dump(out, open(B.RESULTS / f"bw_clean_{ds}.json", "w"), indent=1)
    for w in C.CNN_WIDTHS:
        cw = [r for r in dr_cnn if abs(r["width"] - w) < 1e-6]
        if cw:
            b = min(cw, key=lambda r: r["err"])
            print(f"  w{w}GHz: best center {b['center']}GHz  CNN {b['err']*25.4:.1f} mm", flush=True)
    print(f"  saved bw_clean_{ds}.json  ({time.time()-t0:.0f}s)", flush=True)
print("\nALL CLEAN SWEEPS DONE", flush=True)
