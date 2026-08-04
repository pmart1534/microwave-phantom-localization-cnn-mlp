r"""Make the deterministic simulation behave like the bench, so LOSO / classification
become meaningful on sim.

The sim has ONE noise-free S-parameter set per position -> classification is
trivially 100% and there are no 'sessions' to leave out. We synthesize the two
nuisances the bench actually has (measured June18 A3):
  - per-take additive noise      : signal/noise ~ 6.6x  (SNR-matched, per channel)
  - cross-session drift ~12%     : a smooth, mostly COMMON-MODE complex gain that
                                   varies session to session (freq-structured +
                                   small per-antenna + small freq shift), so it is
                                   NOT removed by per-session z-score -> LOSO is a
                                   real generalization test.

We match the measured RATIOS (SNR, drift %), not absolute levels, because the sim
tumor dS is ~5-7x weaker (antenna-model mismatch). Output mimics the measured
cache: dict(Yc=(N,16,F) complex dS, pos, sess, tgt) with N = P x sessions x takes.

Run:  python sim_noise.py            # build noisy sim + k-NN LOSO reg + classification
"""
from __future__ import annotations
import os, glob, json
import numpy as np
import bandwidth_sweep_reg as B

SIM = B.SIM; GPG = B.GPG; PERM = B.SIM_PERM
FG = np.linspace(2e9, 8e9, 256); DF = FG[1] - FG[0]

# --- nuisance budget, calibrated to measured June18 A3 ---
SNR          = 6.6      # per-cell |S| signal/noise (match measured)
DRIFT_RIPPLE = 0.12     # per-session common-mode freq-shape gain ripple (frac of signal)
ANT_GAIN_STD = 0.05     # per-session per-antenna complex gain std (keep small: don't scramble the which-antenna pattern)
FSHIFT_STD   = 30e6     # per-session resonance/frequency jitter (Hz)
N_MODES      = 3        # low-order frequency modes in the drift ripple


def _resamp(f, S16):
    out = np.empty((FG.size, 16), complex)
    for k in range(16):
        out[:, k] = np.interp(FG, f, S16[:, k].real) + 1j * np.interp(FG, f, S16[:, k].imag)
    return out


def load_sim_ds(depth=15, baseline_key="b1_2"):
    """One dS per (x,y) at a near-patch depth (~measured tumor height). Physical order."""
    gl = [l.split(",") for l in open(GPG).read().splitlines()[1:]]
    gsim = np.array([[float(r[3]), float(r[4])] for r in gl]); gloc = np.array([[float(r[1]), float(r[2])] for r in gl])
    M = np.column_stack([gsim, np.ones(len(gsim))])
    cX = np.linalg.lstsq(M, gloc[:, 0], rcond=None)[0]; cY = np.linalg.lstsq(M, gloc[:, 1], rcond=None)[0]
    to_inch = lambda x, y: ((cX[0]*x+cX[1]*y+cX[2]) / 25.4, (145.9-(cY[0]*x+cY[1]*y+cY[2])) / 23.85)
    fb, Sb = B.read_s4p(os.path.join(SIM, f"baseline_empty_{baseline_key}.s4p"))
    base = _resamp(fb, Sb.reshape(len(fb), 16))
    dS, tgt = [], []
    for fp in glob.glob(os.path.join(SIM, f"P*DenseZ{depth}_*.s4p")):
        js = fp[:-4] + ".json"
        if not os.path.exists(js): continue
        m = json.load(open(js)); fr, S = B.read_s4p(fp); S = S[:, PERM][:, :, PERM]
        dS.append(_resamp(fr, S.reshape(len(fr), 16)) - base)
        tgt.append(list(to_inch(m["tumor_x_mm"], m["tumor_y_mm"])))
    return np.array(dS).transpose(0, 2, 1), np.array(tgt, float)   # (P,16,F), (P,2)


def synth(dS, tgt, n_sess=3, n_take=16, seed=0, noise=True, drift=True):
    """dS:(P,16,F) -> (N,16,F) with per-session drift + per-take noise; N=P*n_sess*n_take."""
    rng = np.random.RandomState(seed)
    P, C, F = dS.shape
    sig = np.median(np.abs(dS), axis=(0, 2))              # per-channel signal level (16,)
    sigma = sig / SNR                                     # per-channel noise std
    fn = np.linspace(0, 1, F)
    Yc, pos, sess, tg = [], [], [], []
    for k in range(n_sess):
        if drift:
            ripple = np.ones(F, complex)
            for m in range(N_MODES):
                c = rng.normal(0, DRIFT_RIPPLE, 2)
                ripple += (c[0] + 1j*c[1]) * np.cos((m+1) * np.pi * fn)
            antg = (1 + rng.normal(0, ANT_GAIN_STD, C)) + 1j*rng.normal(0, ANT_GAIN_STD, C)
            shift = int(round(rng.normal(0, FSHIFT_STD) / DF))
            G = (ripple[None, :] * antg[:, None])         # (C,F) common-mode ripple x per-antenna
            dS_k = np.roll(dS, shift, axis=2) * G[None, :, :]
        else:
            dS_k = dS
        for t in range(n_take):
            if noise:
                nz = (rng.normal(0, 1, dS_k.shape) + 1j*rng.normal(0, 1, dS_k.shape))
                nz = nz * (sigma[None, :, None] / np.sqrt(2))
            else:
                nz = 0
            Yc.append(dS_k + nz); pos.append(np.arange(P)); sess.append(np.full(P, k)); tg.append(tgt)
    return dict(Yc=np.concatenate(Yc), pos=np.concatenate(pos).astype(np.int64),
                sess=np.concatenate(sess).astype(np.int64), tgt=np.concatenate(tg))


def knn_classify_loso(data):
    """Leave-one-session-out position classification (per-session z-score + k-NN)."""
    from sklearn.preprocessing import StandardScaler
    from sklearn.neighbors import KNeighborsClassifier
    Yc, pos, sess = data["Yc"], data["pos"], data["sess"]
    X = B._raw_feats(Yc)
    accs = []
    for te in np.unique(sess):
        tr = sess != te
        Xtr, Xte = X[tr], X[~tr]
        Xtr_z, Xte_z = B._per_session_z(Xtr, sess[tr], Xte, sess[~tr])
        sc = StandardScaler().fit(Xtr_z)
        clf = KNeighborsClassifier(n_neighbors=5).fit(sc.transform(Xtr_z), pos[tr])
        accs.append((clf.predict(sc.transform(Xte_z)) == pos[~tr]).mean())
    return float(np.mean(accs))


def _cls_band(d, chans, lo, hi):
    FGG = FG / 1e9; cols = np.where((FGG >= lo) & (FGG <= hi))[0]
    return knn_classify_loso({**d, "Yc": d["Yc"][:, chans, :][:, :, cols]}) * 100


if __name__ == "__main__":
    dS, tgt = load_sim_ds(); P = dS.shape[0]
    print(f"sim: {P} (x,y) positions at z=15 mm; synthesizing 3 sessions x 16 takes\n")

    # sanity: with no nuisances there are no sessions to distinguish -> trivially perfect
    d0 = synth(dS, tgt, noise=False, drift=False)
    print(f"NOISELESS sanity: full-config LOSO classification {_cls_band(d0, list(range(16)), 2, 8):.1f}%  (trivial)\n")

    # realistic sim: SNR-matched noise + per-session drift -> LOSO is a real test
    d = synth(dS, tgt, noise=True, drift=True)
    print("NOISE + DRIFT sim -- LOSO position classification (87 classes) under reduction:")
    for lbl, ch, lo, hi in [("all-16, full 2-8",   list(range(16)), 2, 8),
                            ("4 refl, full 2-8",    [0, 5, 10, 15],  2, 8),
                            ("1 ant (S11), full",   [0],             2, 8),
                            ("1 ant (S11), 1 GHz",  [0],             2.75, 3.75),
                            ("1 ant (S11), 0.25GHz",[0],             3.0, 3.25),
                            ("1 ant (S11), 0.1 GHz",[0],             3.2, 3.3)]:
        print(f"  {lbl:22s}: {_cls_band(d, ch, lo, hi):5.1f}%")
