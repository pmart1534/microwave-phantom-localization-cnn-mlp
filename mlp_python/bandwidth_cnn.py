r"""CNN version of the bandwidth requirement study.

Mirrors bandwidth_sweep_reg.py (same data, same leave-one-POSITION-out folds,
same per-session z-score + StandardScaler feature pipeline, same 1-8 GHz measured
/ 2-8 GHz sim grid) but the regressor is a small 2-D CNN over the (channel x
frequency) image, so we confirm the k-NN signal-floor knee with the actual model.

CNN is ~1000x more expensive per band than k-NN, so the grid is COARSER: a
center-step of 0.5 GHz and a reduced width set. That still resolves the knee
(error vs bandwidth) and the best center, and pins the absolute accuracy at the
sweet band. Tones are left to the k-NN run.

Usage (from mlp_python/):  python bandwidth_cnn.py --dataset empty
"""
from __future__ import annotations
import os, json, time, argparse
import numpy as np
import torch, torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader

import bandwidth_sweep_reg as B   # reuse loaders / folds / feature pipeline

CNN_WIDTHS = [0.5, 1.0, 2.0, 3.0, 4.0, 6.0]
CNN_CENTER_STEP = 1.0     # coarse (CNN is ~1000x k-NN); resolves knee + best center
EPOCHS = 35
N_SEEDS = 1
FOLDS_K = 5               # 5-fold position CV (fewer trainings than k-NN's 8)


class BandCNN(nn.Module):
    """Width-agnostic: adaptive pool collapses the (channel,freq) map to a fixed size."""
    def __init__(self, rows):
        super().__init__()
        self.c = nn.Sequential(
            nn.Conv2d(1, 16, 3, padding=1), nn.ReLU(), nn.MaxPool2d((1, 2)),
            nn.Conv2d(16, 32, 3, padding=1), nn.ReLU(),
            nn.AdaptiveAvgPool2d((min(rows, 8), 4)),
        )
        self.f = nn.Sequential(nn.Flatten(), nn.Linear(32 * min(rows, 8) * 4, 64),
                               nn.ReLU(), nn.Dropout(0.2), nn.Linear(64, 2))

    def forward(self, x):
        return self.f(self.c(x))


def _to_img(Xz, ncols, nchan):
    """standardized feature vector [mag(C*F), phase(C*F)] -> (N,1,2C,F) image."""
    N = Xz.shape[0]
    mag = Xz[:, :nchan * ncols].reshape(N, nchan, ncols)
    ph = Xz[:, nchan * ncols:].reshape(N, nchan, ncols)
    return np.concatenate([mag, ph], axis=1)[:, None, :, :].astype(np.float32)


def cnn_eval_band(data, cols, folds, epochs=EPOCHS, n_seeds=N_SEEDS):
    Yc, pos, sess, tgt = data["Yc"], data["pos"], data["sess"], data["tgt"]
    ncols = len(cols); nchan = Yc.shape[1]
    fold_errs = []
    for fo in np.unique(folds):
        te = folds == fo; tr = ~te
        if te.sum() == 0 or tr.sum() == 0:
            continue
        Xtr = B._raw_feats(Yc[tr][:, :, cols]); Xte = B._raw_feats(Yc[te][:, :, cols])
        Xtr_z, Xte_z = B._per_session_z(Xtr, sess[tr], Xte, sess[te])
        from sklearn.preprocessing import StandardScaler
        sc = StandardScaler().fit(Xtr_z)
        Xtr_i = _to_img(sc.transform(Xtr_z), ncols, nchan); Xte_i = _to_img(sc.transform(Xte_z), ncols, nchan)
        Ttr = tgt[tr].astype(np.float32); Tte = tgt[te]
        preds = []
        for s in range(n_seeds):
            torch.manual_seed(s)
            net = BandCNN(2 * nchan)
            opt = torch.optim.Adam(net.parameters(), lr=1e-3)
            lossf = nn.MSELoss()
            dl = DataLoader(TensorDataset(torch.tensor(Xtr_i), torch.tensor(Ttr)),
                            batch_size=32, shuffle=True)
            net.train()
            for _ in range(epochs):
                for xb, yb in dl:
                    opt.zero_grad(); l = lossf(net(xb), yb); l.backward(); opt.step()
            net.eval()
            with torch.no_grad():
                preds.append(net(torch.tensor(Xte_i)).numpy())
        pred = np.mean(preds, axis=0)
        fold_errs.append(B._pos_median_err(pred, pos[te], Tte))
    return float(np.mean(fold_errs))


def sweep_dense_cnn(data, FG_GHZ, band, folds):
    lo, hi = band; rows = []
    for w in CNN_WIDTHS:
        if w > hi - lo:
            continue
        centers = np.round(np.arange(lo + w / 2, hi - w / 2 + 1e-9, CNN_CENTER_STEP), 3)
        for c in centers:
            cols = B._cols(FG_GHZ, c, w)
            if cols.size < 2:
                continue
            rows.append(dict(center=float(c), width=float(w), ncols=int(cols.size),
                             err=cnn_eval_band(data, cols, folds)))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--fmin", type=float, default=None)
    ap.add_argument("--fmax", type=float, default=None)
    args = ap.parse_args()
    band = (args.fmin or B.DEFAULT_BAND[args.dataset][0], args.fmax or B.DEFAULT_BAND[args.dataset][1])
    FG, FG_GHZ = B.make_grid(*band)
    t0 = time.time()
    data = B.get_data(args.dataset, FG, band)
    folds = B.foldize(data["pos"], k=FOLDS_K)
    ch = B.chance_baseline(data, folds)
    print(f"[{args.dataset}] band {band[0]}-{band[1]}GHz, {data['Yc'].shape[0]} samples, "
          f"{len(np.unique(data['pos']))} positions; chance {ch*25.4:.1f}mm", flush=True)
    dr = sweep_dense_cnn(data, FG_GHZ, band, folds)
    # per-width best center
    for w in CNN_WIDTHS:
        cw = [r for r in dr if abs(r["width"] - w) < 1e-6]
        if cw:
            b = min(cw, key=lambda r: r["err"])
            print(f"  width {w}GHz: best center {b['center']}GHz  {b['err']*25.4:.1f}mm ({time.time()-t0:.0f}s)", flush=True)
    out = dict(dataset=args.dataset, band=band, model="cnn", chanceIn=ch,
               nPositions=int(len(np.unique(data["pos"]))), widths=CNN_WIDTHS,
               center_step=CNN_CENTER_STEP, epochs=EPOCHS, n_seeds=N_SEEDS, dense_cnn=dr)
    p = B.RESULTS / f"bw_sweep_cnn_{args.dataset}.json"
    json.dump(out, open(p, "w"), indent=1)
    print(f"  saved {p.name}  (total {time.time()-t0:.0f}s)", flush=True)


if __name__ == "__main__":
    main()
