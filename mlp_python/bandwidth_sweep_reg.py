r"""How much BANDWIDTH does the (x,y) REGRESSION localizer really need?

Companion to the classification bandwidth study (which found ~1-5 GHz best).
Here we ask the same question with the REGRESSION localizer, for the SIMULATED
metal phantom and each MEASURED config (empty / F4 / F5).

KEY difference from the earlier regression scaffold (bandwidth_sweep.py): the
probe is leave-one-POSITION-group-out CV, NOT leave-one-session-out. Under LOSO
on a fixed grid the model just RECOGNISES a known position (k-NN error collapses
to ~0 for every band), so no sweet spot ever appears. Holding out whole
positions forces the model to INTERPOLATE to an unseen location -- that is where
a too-narrow / mis-centred band genuinely hurts, so the bandwidth curve is real.

Grid: MEASURED swept on 1-8 GHz (bench spans 0.1-8, so 1-5 is reachable); SIM on
2-8 GHz (its data limit). Common protocol otherwise: complex baseline-subtracted
dS, per-session z-score (KEY trick), position-level median error, K=8
position-disjoint folds, targets in the shared grid-inch frame.

Sweeps (--sweep): dense (center x width), grow (from best center), tones (greedy).
Models (--model): knn (fast signal floor, used for dense) + mlp (confirms the
signal is learnable, used for grow). Outputs are namespaced bw_sweep_reg_*.json
and results/bw_cache_reg/ so the classification track is untouched.

Usage (from mlp_python/):
  python bandwidth_sweep_reg.py --dataset empty --sweep dense,grow,tones --model both
"""
from __future__ import annotations
import os, sys, glob, json, argparse, time
from pathlib import Path
import numpy as np

from run_mlp_loso import list_sessions, load_session, NATIVE_FREQ
from run_mlp_regloso import pos_id_to_label
from label_xy import targets_for_labels
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from sklearn.neural_network import MLPRegressor
from scipy.interpolate import interp1d

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RESULTS = ROOT / "results"
CACHE = RESULTS / "bw_cache_reg"
KNN_K = 8
ENSEMBLE_SEEDS = (42, 7, 13)
N_FOLDS = 8

BASE = r"C:\Users\peter\Desktop\EM Imaging\BreastPhantom\HunterVNA\DataMeasurements\Sam Antennas\MediumAntenna\Separated"
MEAS = {
    "empty": dict(setup=BASE + r"\June18",              adjust="A3_Empty", sessions=None,                     remap=[2, 1, 4, 3]),
    "F4":    dict(setup=BASE + r"\July03\A3_F4_SamMed", adjust="A3_F4",    sessions=None,                     remap=None),
    "F5":    dict(setup=BASE + r"\July03\A3_F5_SamMed", adjust="A3_F5",    sessions=["1432", "1454", "1516"], remap=None),
}
SIM = r"C:\Users\peter\Desktop\EM Imaging\Simulation Data\SamMakin\Data Results\A3_Metal_1cm"
GPG = r"C:\Users\peter\Desktop\EM Imaging\Simulation Data\SamMakin\grid_placed_global.csv"
SIM_DEPTHS = {5: "b1", 10: "b1", 15: "b1_2", 20: "b1_2"}
# full depth stack with per-batch empty baseline (from Imager_CNN_SimReg.m baseMap);
# z=3 mm is a leftover odd depth and is excluded, matching the deck.
SIM_ALL_DEPTHS = {0: "b1", 5: "b1", 10: "b1",
                  -5: "b1_2", 15: "b1_2", 20: "b1_2", 25: "b1_2", 30: "b1_2",
                  -15: "b1_3", -10: "b1_3", 35: "b1_3", 40: "b1_3", 45: "b1_3"}
SIM_PERM = [2, 0, 1, 3]

# per-dataset default band (GHz); sim capped at 2 GHz by its data
DEFAULT_BAND = {"empty": (1.0, 8.0), "F4": (1.0, 8.0), "F5": (1.0, 8.0),
                "sim": (2.0, 8.0), "sim_all": (2.0, 8.0)}
GRID_STEP_MHZ = 15.0


def make_grid(fmin_ghz, fmax_ghz):
    n = int(round((fmax_ghz - fmin_ghz) * 1000.0 / GRID_STEP_MHZ)) + 1
    fg = np.linspace(fmin_ghz * 1e9, fmax_ghz * 1e9, n)
    return fg, fg / 1e9


# ---------------------------------------------------------------- loaders
def _resamp_stack(Y, f, FG):
    re = interp1d(f, Y.real, axis=-1, bounds_error=False, fill_value="extrapolate")(FG)
    im = interp1d(f, Y.imag, axis=-1, bounds_error=False, fill_value="extrapolate")(FG)
    return re + 1j * im


def read_s4p(path):
    vals = []; sc = 1e9
    for line in open(path):
        s = line.strip()
        if not s or s.startswith("!"):
            continue
        if s.startswith("#"):
            sc = 1e6 if " mhz" in s.lower() else 1e9; continue
        vals.extend(float(t) for t in s.split())
    v = np.asarray(vals); per = 1 + 2 * 16; nf = len(v) // per
    v = v[:nf * per].reshape(nf, per); b = v[:, 1:].reshape(nf, 16, 2)
    S = (b[:, :, 0] * np.exp(1j * np.deg2rad(b[:, :, 1]))).reshape(nf, 4, 4)
    return v[:, 0] * sc, S


def load_measured(cfg, FG):
    """Pool all sessions -> dict(Yc=(N,16,F), pos, sess, tgt). Positions present in ALL sessions only."""
    sess_files = list_sessions(Path(cfg["setup"]), only=cfg["sessions"])
    loaded = {}
    for j, (name, path) in enumerate(sess_files):
        per_pos, base, _ = load_session(path, "all", (1, 2, 3, 4), remap=cfg["remap"])
        loaded[name] = (j, per_pos, base)
    pos_sets = [set(pp.keys()) for _, pp, _ in loaded.values()]
    valid = sorted(set.intersection(*pos_sets))
    labels = [pos_id_to_label(p) for p in valid]
    xy = targets_for_labels(labels, cfg["adjust"])
    tgt_of = {p: xy[i] for i, p in enumerate(valid)}
    Yc, pos, sess, tgt = [], [], [], []
    for name, (sid, per_pos, base) in loaded.items():
        for p in valid:
            Y = per_pos[p] - base[None, :, :]                    # v2 baseline subtract, no mean sub
            Yc.append(_resamp_stack(Y, NATIVE_FREQ, FG))
            n = per_pos[p].shape[0]
            pos += [p] * n; sess += [sid] * n; tgt += [tgt_of[p]] * n
    return dict(Yc=np.concatenate(Yc), pos=np.array(pos, np.int64),
                sess=np.array(sess, np.int64), tgt=np.array(tgt, float))


def load_sim(FG):
    gl = [l.split(",") for l in open(GPG).read().splitlines()[1:]]
    gsim = np.array([[float(r[3]), float(r[4])] for r in gl])
    gloc = np.array([[float(r[1]), float(r[2])] for r in gl])
    M = np.column_stack([gsim, np.ones(len(gsim))])
    cX = np.linalg.lstsq(M, gloc[:, 0], rcond=None)[0]
    cY = np.linalg.lstsq(M, gloc[:, 1], rcond=None)[0]
    def to_inch(xmm, ymm):
        return (cX[0]*xmm+cX[1]*ymm+cX[2]) / 25.4, (145.9 - (cY[0]*xmm+cY[1]*ymm+cY[2])) / 23.85
    bases = {}
    for bk in set(SIM_DEPTHS.values()):
        f, S = read_s4p(os.path.join(SIM, f"baseline_empty_{bk}.s4p"))
        bases[bk] = _resamp_stack((S.reshape(len(f), 16)).T[None], f, FG)[0].T  # (F,16)
    Yc, pos, tgt = [], [], []
    key_to_pid = {}
    for z, bk in SIM_DEPTHS.items():
        for fp in glob.glob(os.path.join(SIM, f"P*DenseZ{z}_*.s4p")):
            js = fp[:-4] + ".json"
            if not os.path.exists(js):
                continue
            m = json.load(open(js)); fr, S = read_s4p(fp)
            S = S[:, SIM_PERM][:, :, SIM_PERM]
            dS = _resamp_stack((S.reshape(len(fr), 16)).T[None], fr, FG)[0].T - bases[bk]  # (F,16)
            key = (round(m["tumor_x_mm"], 1), round(m["tumor_y_mm"], 1))
            key_to_pid.setdefault(key, len(key_to_pid))
            Yc.append(dS.T)                                       # (16,F)
            pos.append(key_to_pid[key]); tgt.append(list(to_inch(m["tumor_x_mm"], m["tumor_y_mm"])))
    return dict(Yc=np.stack(Yc), pos=np.array(pos, np.int64),
                sess=np.zeros(len(pos), np.int64), tgt=np.array(tgt, float))


def load_sim_all(FG):
    """Full depth stack (13 depths, per-batch baseline). Positions keyed by (x,y)
    so all depths of one (x,y) share a pos id -> strict LOPO grouping over (x,y)."""
    gl = [l.split(",") for l in open(GPG).read().splitlines()[1:]]
    gsim = np.array([[float(r[3]), float(r[4])] for r in gl])
    gloc = np.array([[float(r[1]), float(r[2])] for r in gl])
    M = np.column_stack([gsim, np.ones(len(gsim))])
    cX = np.linalg.lstsq(M, gloc[:, 0], rcond=None)[0]
    cY = np.linalg.lstsq(M, gloc[:, 1], rcond=None)[0]
    def to_inch(xmm, ymm):
        return (cX[0]*xmm+cX[1]*ymm+cX[2]) / 25.4, (145.9 - (cY[0]*xmm+cY[1]*ymm+cY[2])) / 23.85
    bases = {}
    for bk in set(SIM_ALL_DEPTHS.values()):
        f, S = read_s4p(os.path.join(SIM, f"baseline_empty_{bk}.s4p"))
        bases[bk] = _resamp_stack((S.reshape(len(f), 16)).T[None], f, FG)[0].T   # (F,16)
    Yc, pos, tgt = [], [], []
    key_to_pid = {}
    for z, bk in SIM_ALL_DEPTHS.items():
        for fp in glob.glob(os.path.join(SIM, f"P*DenseZ{z}_*.s4p")):
            js = fp[:-4] + ".json"
            if not os.path.exists(js):
                continue
            m = json.load(open(js)); fr, S = read_s4p(fp)
            S = S[:, SIM_PERM][:, :, SIM_PERM]
            dS = _resamp_stack((S.reshape(len(fr), 16)).T[None], fr, FG)[0].T - bases[bk]
            key = (round(m["tumor_x_mm"], 1), round(m["tumor_y_mm"], 1))    # (x,y) only
            key_to_pid.setdefault(key, len(key_to_pid))
            Yc.append(dS.T); pos.append(key_to_pid[key])
            tgt.append(list(to_inch(m["tumor_x_mm"], m["tumor_y_mm"])))
    return dict(Yc=np.stack(Yc), pos=np.array(pos, np.int64),
                sess=np.zeros(len(pos), np.int64), tgt=np.array(tgt, float))


def get_data(dataset, FG, band):
    CACHE.mkdir(parents=True, exist_ok=True)
    fp = CACHE / f"{dataset}_{band[0]:g}-{band[1]:g}.npz"
    if fp.exists():
        d = np.load(fp)
        print(f"  loaded cache {fp.name}", flush=True)
        return {k: d[k] for k in ("Yc", "pos", "sess", "tgt")}
    print(f"  building cache {fp.name} ...", flush=True)
    if dataset == "sim_all":
        data = load_sim_all(FG)
    elif dataset == "sim":
        data = load_sim(FG)
    else:
        data = load_measured(MEAS[dataset], FG)
    np.savez_compressed(fp, **data)
    return data


# ---------------------------------------------------------------- eval
def _raw_feats(Yc):
    mag = np.abs(Yc).astype(np.float32); ph = np.angle(Yc).astype(np.float32)
    N = Yc.shape[0]
    return np.concatenate([mag.reshape(N, -1), ph.reshape(N, -1)], axis=1)


def _per_session_z(Xtr, str_, Xte, ste):
    Xtr_z = np.empty_like(Xtr); Xte_z = np.empty_like(Xte); stats = {}
    for s in np.unique(str_):
        m = str_ == s; mu = Xtr[m].mean(0); sd = Xtr[m].std(0) + 1e-8
        stats[s] = (mu, sd); Xtr_z[m] = (Xtr[m] - mu) / sd
    for s in np.unique(ste):
        m = ste == s
        mu, sd = stats.get(s, (Xte[m].mean(0), Xte[m].std(0) + 1e-8))
        Xte_z[m] = (Xte[m] - mu) / sd
    return Xtr_z, Xte_z


def _pos_median_err(pred, pos, tgt):
    errs = []
    for p in np.unique(pos):
        m = pos == p
        errs.append(np.linalg.norm(np.median(pred[m], axis=0) - tgt[m][0]))
    return float(np.median(errs))


def foldize(pos, k=N_FOLDS, seed=0):
    uP = np.unique(pos); rng = np.random.RandomState(seed); rng.shuffle(uP)
    fold_of = {p: i % k for i, p in enumerate(uP)}
    return np.array([fold_of[p] for p in pos])


def eval_band(data, cols, folds, model="knn", n_seeds=1):
    Yc, pos, sess, tgt = data["Yc"], data["pos"], data["sess"], data["tgt"]
    fold_errs = []
    for fo in np.unique(folds):
        te = folds == fo; tr = ~te
        if te.sum() == 0 or tr.sum() == 0:
            continue
        Xtr = _raw_feats(Yc[tr][:, :, cols]); Xte = _raw_feats(Yc[te][:, :, cols])
        Xtr_z, Xte_z = _per_session_z(Xtr, sess[tr], Xte, sess[te])
        sc = StandardScaler().fit(Xtr_z)
        Xtr_s = sc.transform(Xtr_z).astype(np.float32); Xte_s = sc.transform(Xte_z).astype(np.float32)
        Ttr = tgt[tr]
        if model == "knn":
            nn = NearestNeighbors(n_neighbors=min(KNN_K, len(Xtr_s))).fit(Xtr_s)
            dist, idx = nn.kneighbors(Xte_s)
            w = 1.0 / (dist + 1e-6); w /= w.sum(1, keepdims=True)
            pred = np.einsum("nk,nkd->nd", w, Ttr[idx])
        else:
            preds = []
            for es in ENSEMBLE_SEEDS[:n_seeds]:
                reg = MLPRegressor(hidden_layer_sizes=(256, 128), max_iter=300,
                                   early_stopping=True, validation_fraction=0.1,
                                   n_iter_no_change=15, random_state=es)
                reg.fit(Xtr_s, Ttr); preds.append(reg.predict(Xte_s))
            pred = np.mean(preds, axis=0)
        fold_errs.append(_pos_median_err(pred, pos[te], tgt[te]))
    return float(np.mean(fold_errs))


# ---------------------------------------------------------------- sweeps
WIDTHS = [0.25, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 6.0]
CENTER_STEP = 0.25


def _cols(FG_GHZ, c, w):
    return np.where((FG_GHZ >= c - w / 2) & (FG_GHZ <= c + w / 2))[0]


def sweep_dense(data, FG_GHZ, band, folds, model, n_seeds=1):
    lo, hi = band; rows = []
    for w in WIDTHS:
        if w > hi - lo:
            continue
        centers = np.round(np.arange(lo + w / 2, hi - w / 2 + 1e-9, CENTER_STEP), 3)
        for c in centers:
            cols = _cols(FG_GHZ, c, w)
            if cols.size < 2:
                continue
            rows.append(dict(center=float(c), width=float(w), ncols=int(cols.size),
                             err=eval_band(data, cols, folds, model, n_seeds)))
    return rows


def best_center(rows, width):
    cand = [r for r in rows if abs(r["width"] - width) < 1e-6]
    return min(cand, key=lambda r: r["err"]) if cand else None


def sweep_grow(data, FG_GHZ, band, folds, c0, model, n_seeds=3):
    lo, hi = band; rows = []
    for w in [0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 7.0]:
        if c0 - w / 2 < lo or c0 + w / 2 > hi:
            continue
        cols = _cols(FG_GHZ, c0, w)
        if cols.size < 2:
            continue
        rows.append(dict(center=float(c0), width=float(w), ncols=int(cols.size),
                         err=eval_band(data, cols, folds, model, n_seeds)))
    return rows


def sweep_tones(data, FG_GHZ, band, folds, model="knn", max_tones=8, cand_step=0.1):
    lo, hi = band
    cand = sorted(set(int(np.argmin(np.abs(FG_GHZ - g)))
                      for g in np.arange(lo, hi + 1e-9, cand_step)))
    chosen, rows = [], []
    for _ in range(max_tones):
        best = None
        for ci in cand:
            if ci in chosen:
                continue
            e = eval_band(data, np.array(sorted(chosen + [ci])), folds, model, 1)
            if best is None or e < best[1]:
                best = (ci, e)
        chosen.append(best[0])
        rows.append(dict(n=len(chosen), tone_ghz=float(FG_GHZ[best[0]]),
                         tones_ghz=[float(FG_GHZ[c]) for c in sorted(chosen)], err=best[1]))
    return rows


def chance_baseline(data, folds):
    errs = []
    for fo in np.unique(folds):
        te = folds == fo; tr = ~te
        cen = data["tgt"][tr].mean(0)
        errs.append(_pos_median_err(np.repeat(cen[None], te.sum(), 0), data["pos"][te], data["tgt"][te]))
    return float(np.mean(errs))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", required=True, help="empty|F4|F5|sim")
    ap.add_argument("--sweep", default="dense,grow,tones")
    ap.add_argument("--model", default="both", help="knn|mlp|both")
    ap.add_argument("--fmin", type=float, default=None)
    ap.add_argument("--fmax", type=float, default=None)
    args = ap.parse_args()
    band = (args.fmin or DEFAULT_BAND[args.dataset][0], args.fmax or DEFAULT_BAND[args.dataset][1])
    FG, FG_GHZ = make_grid(*band)
    sweeps = args.sweep.split(","); models = ["knn", "mlp"] if args.model == "both" else [args.model]

    t0 = time.time()
    data = get_data(args.dataset, FG, band)
    folds = foldize(data["pos"])
    nP = len(np.unique(data["pos"]))
    print(f"[{args.dataset}] band {band[0]}-{band[1]}GHz, {FG.size} freqs, {data['Yc'].shape[0]} samples, "
          f"{nP} positions, {N_FOLDS} folds ({time.time()-t0:.1f}s)", flush=True)
    ch = chance_baseline(data, folds)
    print(f"  chance (predict centroid): {ch:.3f} in ({ch*25.4:.1f} mm)", flush=True)

    out = dict(dataset=args.dataset, band=band, grid=f"{FG.size}pts", nFolds=N_FOLDS,
               nSamples=int(data["Yc"].shape[0]), nPositions=nP, chanceIn=ch, widths=WIDTHS)

    # Tiered: k-NN is the fast signal-floor -> runs the whole dense grid and picks the
    # best center. The MLP (expensive) only CONFIRMS the knee via the grow curve at that
    # center; we never run the dense MLP grid.
    c0 = None
    if "dense" in sweeps or "grow" in sweeps:
        t = time.time(); dr = sweep_dense(data, FG_GHZ, band, folds, "knn", 1)
        out["dense_knn"] = dr
        b1 = best_center(dr, 1.0) or best_center(dr, min(WIDTHS))
        c0 = b1["center"]
        print(f"  [knn] dense: {len(dr)} windows ({time.time()-t:.0f}s); "
              f"best 1GHz center={c0}GHz err={b1['err']:.3f}in ({b1['err']*25.4:.1f}mm)", flush=True)
    if "grow" in sweeps and c0 is not None:
        out["grow_center"] = c0
        out["grow_knn"] = sweep_grow(data, FG_GHZ, band, folds, c0, "knn", 1)
        if "mlp" in models:
            out["grow_mlp"] = sweep_grow(data, FG_GHZ, band, folds, c0, "mlp", 3)
        print(f"  grow from {c0}GHz done ({time.time()-t0:.0f}s)", flush=True)
    if "dense_mlp" in sweeps:   # opt-in only; very slow
        out["dense_mlp"] = sweep_dense(data, FG_GHZ, band, folds, "mlp", 3)
    if "tones" in sweeps:
        t = time.time(); out["tones_knn"] = sweep_tones(data, FG_GHZ, band, folds)
        tr = out["tones_knn"]
        print(f"  [knn] tones: 1->{tr[0]['err']:.3f}  {len(tr)}->{tr[-1]['err']:.3f}in ({time.time()-t:.0f}s)", flush=True)
    RESULTS.mkdir(exist_ok=True)
    p = RESULTS / f"bw_sweep_reg_{args.dataset}.json"
    json.dump(out, open(p, "w"), indent=1)
    print(f"  saved {p.name}  (total {time.time()-t0:.0f}s)", flush=True)


if __name__ == "__main__":
    main()
