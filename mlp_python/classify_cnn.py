r"""Position-classification CNN under leave-one-session-out, for the noisy sim and
the measured phantoms (same model + protocol so they're comparable).

Input per sample: [|dS|, angle(dS)] of the selected S-parameters over the selected
frequency columns -> (2C, ncols) image, per-session z-scored (the KEY trick).
Head: softmax over the position classes. LOSO: train on all-but-one session,
test on the held-out one; report mean accuracy.
"""
from __future__ import annotations
import numpy as np
import torch, torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
from sklearn.preprocessing import StandardScaler
import bandwidth_sweep_reg as B


def _to_img(Xz, ncols, nchan):
    N = Xz.shape[0]
    mag = Xz[:, :nchan*ncols].reshape(N, nchan, ncols)
    ph = Xz[:, nchan*ncols:].reshape(N, nchan, ncols)
    return np.concatenate([mag, ph], axis=1)[:, None, :, :].astype(np.float32)


class ClsCNN(nn.Module):
    def __init__(self, rows, nclass):
        super().__init__()
        r = min(rows, 8)
        self.c = nn.Sequential(
            nn.Conv2d(1, 16, 3, padding=1), nn.ReLU(), nn.MaxPool2d((1, 2)),
            nn.Conv2d(16, 32, 3, padding=1), nn.ReLU(), nn.AdaptiveAvgPool2d((r, 4)))
        self.f = nn.Sequential(nn.Flatten(), nn.Linear(32*r*4, 64), nn.ReLU(),
                               nn.Dropout(0.2), nn.Linear(64, nclass))

    def forward(self, x):
        return self.f(self.c(x))


def cnn_classify_loso(data, chans=None, cols=None, epochs=40, n_seeds=1):
    Yc, pos, sess = data["Yc"], data["pos"], data["sess"]
    if chans is not None: Yc = Yc[:, chans, :]
    if cols is not None:  Yc = Yc[:, :, cols]
    nchan, ncols = Yc.shape[1], Yc.shape[2]
    classes = np.unique(pos); cmap = {c: i for i, c in enumerate(classes)}
    y = np.array([cmap[p] for p in pos])
    X = B._raw_feats(Yc)
    accs = []
    for te in np.unique(sess):
        tr = sess != te
        Xtr_z, Xte_z = B._per_session_z(X[tr], sess[tr], X[~tr], sess[~tr])
        sc = StandardScaler().fit(Xtr_z)
        Xtr = _to_img(sc.transform(Xtr_z), ncols, nchan); Xte = _to_img(sc.transform(Xte_z), ncols, nchan)
        ytr, yte = y[tr], y[~tr]
        preds = []
        for s in range(n_seeds):
            torch.manual_seed(s)
            net = ClsCNN(2*nchan, len(classes))
            opt = torch.optim.Adam(net.parameters(), lr=1e-3); lf = nn.CrossEntropyLoss()
            dl = DataLoader(TensorDataset(torch.tensor(Xtr), torch.tensor(ytr)), batch_size=64, shuffle=True)
            for _ in range(epochs):
                net.train()
                for xb, yb in dl:
                    opt.zero_grad(); l = lf(net(xb), yb); l.backward(); opt.step()
            net.eval()
            with torch.no_grad(): preds.append(net(torch.tensor(Xte)).numpy())
        accs.append((np.mean(preds, axis=0).argmax(1) == yte).mean())
    return float(np.mean(accs))


if __name__ == "__main__":
    import sim_noise as SN
    dS, tgt = SN.load_sim_ds()
    snr_c, drift = SN.measured_calibration()
    d = SN.synth(dS, tgt, snr_c, drift * SN.DRIFT_GAIN, noise=True, drift=True)
    P = len(np.unique(d["pos"]))
    print(f"noisy sim: {P} positions, {d['Yc'].shape[0]} samples, 3 synthetic sessions")
    print(f"chance = {100/P:.1f}%")
    acc = cnn_classify_loso(d, epochs=40, n_seeds=2)
    print(f"classification CNN, LOSO, full config (16 S-params, 2-8 GHz): {acc*100:.1f}%")
