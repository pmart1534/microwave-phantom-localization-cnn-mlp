r"""Isolate WHY the bandwidth-study CNN sits ~13 mm while the decks report ~3.9 mm.

Two hypotheses:
  (A) it's the narrow 2-4 GHz band  -> then widening to full band recovers it.
  (B) it's the harder protocol (leave-one-POSITION-out) + less data -> then the
      SAME band under the deck's easier protocol (LOSO / random 8-fold) recovers it.

We test the same CNN (and k-NN) on the empty and sim caches under:
  - LOPO  : leave-one-position-out (the bandwidth study's probe)
  - LOSO  : leave-one-session-out  (the deck's measured protocol; empty only)
  - rand8 : random 8-fold sample split (the deck's sim protocol, near-patch subset)
each at the 2-4 GHz sweet band AND the full band.
"""
from __future__ import annotations
import numpy as np
import bandwidth_sweep_reg as B
import bandwidth_cnn as C

def folds_for(data, mode):
    if mode == "lopo":
        return B.foldize(data["pos"], k=5)
    if mode == "loso":
        return data["sess"].copy()
    if mode == "rand8":
        return np.random.RandomState(0).randint(0, 8, size=data["Yc"].shape[0])
    raise ValueError(mode)

def run(dataset, modes, bands):
    full = B.DEFAULT_BAND[dataset]; FG, FGG = B.make_grid(*full)
    data = B.get_data(dataset, FG, full)
    print(f"\n===== {dataset}  ({data['Yc'].shape[0]} samples, {len(np.unique(data['pos']))} positions) =====", flush=True)
    for mode in modes:
        folds = folds_for(data, mode)
        for (c, w, label) in bands:
            cols = B._cols(FGG, c, w)
            ek = B.eval_band(data, cols, folds, "knn")
            ec = C.cnn_eval_band(data, cols, folds, epochs=C.EPOCHS, n_seeds=C.N_SEEDS)
            print(f"  {mode:5s} | {label:9s} ({cols.size:3d} cols): kNN {ek*25.4:5.1f} mm   CNN {ec*25.4:5.1f} mm", flush=True)

# empty: LOPO vs LOSO, at sweet band and full band
run("empty", ["lopo", "loso"], [(3.0, 2.0, "2-4 GHz"), (4.5, 7.0, "1-8 GHz")])
# sim: LOPO vs random-8fold, at sweet band and full band
run("sim", ["lopo", "rand8"], [(3.0, 2.0, "2-4 GHz"), (5.0, 6.0, "2-8 GHz")])
print("\nDONE", flush=True)
