r"""Antenna-count / reflection-only reduction WITHIN the bandwidth sweet spot.

Combines the two reduction axes: restrict the (x,y) regressor to the sweet-spot
band (default 2-4 GHz) AND to fewer antennas / reflection-only, for sim and each
measured config. This is the "simplest chip" corner: narrow band + few ports.

Reuses bandwidth_sweep_reg's cached data, folds, feature pipeline, and eval
(k-NN signal floor); optionally CNN-confirms (bandwidth_cnn). Antenna configs
match the Deck 1 full-band study:
  all-16    all S-parameters
  refl-all  the 4 reflections Sii (no transmission)
  refl-1&3  reflections of ports 1 & 3
  refl-1    reflection of port 1 only

Usage:  python bandwidth_antenna.py --model knn        # fast, all datasets
        python bandwidth_antenna.py --model cnn        # confirm (slower)
"""
from __future__ import annotations
import os, json, time, argparse
import numpy as np
import bandwidth_sweep_reg as B

# full16 row = (i-1)*4+(j-1); reflection Sii of port p is at (p-1)*4+(p-1)
R = lambda p: (p - 1) * 4 + (p - 1)
ANT = {
    "all-16":   list(range(16)),
    "refl-all": [R(1), R(2), R(3), R(4)],
    "refl-1&3": [R(1), R(3)],
    "refl-1":   [R(1)],
}
BAND = (2.0, 4.0)          # the sweet spot (center 3, width 2)


def subset_channels(data, chans):
    return {**data, "Yc": data["Yc"][:, chans, :]}


def run(model):
    results = {}
    for ds in ["empty", "F4", "F5", "sim"]:
        full = B.DEFAULT_BAND[ds]
        FG, FG_GHZ = B.make_grid(*full)
        data = B.get_data(ds, FG, full)
        folds = B.foldize(data["pos"], k=(8 if model == "knn" else 5))
        cols = B._cols(FG_GHZ, (BAND[0] + BAND[1]) / 2, BAND[1] - BAND[0])
        ch = B.chance_baseline(data, folds)
        row = {"chanceIn": ch, "band": BAND, "ncols": int(cols.size)}
        t0 = time.time()
        for name, chans in ANT.items():
            sub = subset_channels(data, chans)
            if model == "knn":
                e = B.eval_band(sub, cols, folds, "knn")
            else:
                import bandwidth_cnn as C
                e = C.cnn_eval_band(sub, cols, folds, epochs=C.EPOCHS, n_seeds=C.N_SEEDS)
            row[name] = e
            print(f"  [{ds}/{model}] {name:9s} ({len(chans)} ch): {e*25.4:.1f} mm  ({time.time()-t0:.0f}s)", flush=True)
        results[ds] = row
        print(f"[{ds}] chance {ch*25.4:.1f}mm  band {BAND[0]}-{BAND[1]}GHz done", flush=True)
    out = os.path.join(str(B.RESULTS), f"bw_antenna_{model}.json")
    json.dump(results, open(out, "w"), indent=1)
    print("saved", os.path.basename(out))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="knn", help="knn|cnn")
    run(ap.parse_args().model)
