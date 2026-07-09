r"""MLP (x,y) REGRESSION Leave-One-Session-Out driver -- the regression
counterpart to run_mlp_loso.py and the head-to-head twin of
../cnn_matlab/Imager_CNN_RegLOSO.m.

Pipeline (identical to the classifier up to the head):

    full16 native-791 load  ->  optional port remap  ->  antenna subset
    ->  complex baseline subtraction        (v2: NO per-session mean sub)
    ->  raw | physics | tdr features        (byte-identical to classifier)
    ->  per-session z-score                 (the cross-session "KEY" trick)
    ->  3-seed MLPRegressor(256,128) average  [optional +Ridge via --ridge]

Targets are TRUE physical (x, y) inches from the RnCmPp labels via
label_xy.py (canonical 0.375-in corner offsets), with the photo-digitized
overrides from position_adjustments.json applied where the glandular insert
blocked the exact corner (--adjust-key A3_F4 | A3_F5 | A3_Empty).

Metrics per fold and LOSO mean+/-std (error DISTANCE only -- predictions are
never snapped to grid positions):
    trial-level    : mean/median Euclidean error (in), % within 0.5 in / 1 in
    position-level : median predicted point over each position's trials,
                     then that point's error (the majority-vote analog)
    spread         : per-position mean radial distance of the trial
                     predictions from their median point (confidence proxy;
                     expect inflation over the glandular insert)
    stratified     : near-insert (photo-adjusted labels) vs exterior groups,
                     so insert-region error never pollutes the exterior stats
    centroid       : predict-the-train-centroid baseline (regression "chance")

Usage (from this folder, using the Above 95 Percent venv):
    ..\..\"Above 95 Percent"\venv\Scripts\python.exe run_mlp_regloso.py ^
        --setup "C:\...\Separated\June18" --antenna all --input physics ^
        --adjust-key A3_Empty --port-remap 2,1,4,3

Outputs:
    ../results/mlp_regloso_<tag>.json   (reg_ prefix keeps these out of the
    classification table/figure builders)
"""
from __future__ import annotations
import json, argparse, time
from collections import defaultdict
from pathlib import Path
import numpy as np

# Reuse the classifier driver's loading + feature code so the two pipelines
# cannot drift apart (it also puts Above 95 Percent/code on sys.path).
from run_mlp_loso import (list_sessions, parse_antenna, load_session,
                          calibrate, build_features,
                          ENSEMBLE_SEEDS, TOTAL_COLS, RESULTS_DIR)
from label_xy import targets_for_labels, load_adjustments
from data import per_session_zscore                               # noqa: E402
from sklearn.preprocessing import StandardScaler                  # noqa: E402
from sklearn.neural_network import MLPRegressor                   # noqa: E402
from sklearn.linear_model import Ridge                            # noqa: E402

HALF_CELL_IN = 0.5


def pos_id_to_label(pos_id: int) -> str:
    """sparse pos id -> 'RnCmPp'.  pos = ((r-1)*COLS+(c-1))*4+(p-1)."""
    cell, p = divmod(int(pos_id), 4)
    r, c = divmod(cell, TOTAL_COLS)
    return f"R{r + 1}C{c + 1}P{p + 1}"


def _fit_predict_reg(seed, X_tr, T_tr, X_te):
    reg = MLPRegressor(hidden_layer_sizes=(256, 128), max_iter=200,
                       early_stopping=True, validation_fraction=0.1,
                       n_iter_no_change=15, random_state=seed, verbose=False)
    reg.fit(X_tr, T_tr)
    return reg.predict(X_te)


def train_predict_reg(X_tr, T_tr, X_te, use_ridge=False):
    """Same standardization chain as the classifier's train_predict, with the
    3-seed probability average replaced by a 3-seed prediction average.
    Seeds run SEQUENTIALLY (not joblib-threaded): with the 51.6k-D physics
    features, three concurrent float64 Adam optimizers OOM a 16 GB machine."""
    mu = X_tr.mean(0); sd = X_tr.std(0) + 1e-8
    X_tr_z = (X_tr - mu) / sd; X_te_z = (X_te - mu) / sd
    sc = StandardScaler().fit(X_tr_z)
    X_tr_s = sc.transform(X_tr_z).astype(np.float32, copy=False)
    X_te_s = sc.transform(X_te_z).astype(np.float32, copy=False)
    del X_tr_z, X_te_z
    preds = [_fit_predict_reg(es, X_tr_s, T_tr, X_te_s) for es in ENSEMBLE_SEEDS]
    pred = np.mean(preds, axis=0)
    if use_ridge:
        rd = Ridge(alpha=1.0).fit(X_tr_s, T_tr)
        pred = (pred * len(ENSEMBLE_SEEDS) + rd.predict(X_te_s)) / (len(ENSEMBLE_SEEDS) + 1)
    return pred


def err_stats(err: np.ndarray) -> dict:
    return dict(meanErrIn=float(err.mean()),
                medianErrIn=float(np.median(err)),
                pctWithinHalfIn=float((err <= HALF_CELL_IN).mean() * 100),
                pctWithin1In=float((err <= 1.0).mean() * 100))


# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--setup", required=True,
                    help="parent folder holding the per-session subfolders")
    ap.add_argument("--antenna", default="all",
                    help="all | pair:1,3 | single:1 | refl:1,3 | refl:1,2,3,4")
    ap.add_argument("--input", dest="input_kind", default="physics",
                    choices=["raw", "physics", "tdr"])
    ap.add_argument("--sessions", default="",
                    help="comma list of session name substrings to KEEP")
    ap.add_argument("--set-label", dest="set_label", default="")
    ap.add_argument("--port-remap", dest="port_remap", default="",
                    help="e.g. 2,1,4,3 for June18 empty")
    ap.add_argument("--adjust-key", dest="adjust_key", default="none",
                    help="position_adjustments.json key: A3_Empty | A3_F4 | "
                         "A3_F5 | none (photo-corrected true positions)")
    ap.add_argument("--session-mean", dest="session_mean", action="store_true",
                    help="ABLATION: re-enable v1 per-session mean subtraction "
                         "(default = v2, baseline subtraction only)")
    ap.add_argument("--ridge", action="store_true",
                    help="blend a Ridge regressor 3:1 with the MLP ensemble "
                         "(regression analog of the classifier's LogReg vote)")
    args = ap.parse_args()
    remap = [int(x) for x in args.port_remap.replace(" ", "").split(",")] if args.port_remap else None

    mode, ports = parse_antenna(args.antenna)
    parent = Path(args.setup)
    setup_name = parent.name
    only = [t for t in args.sessions.replace(" ", "").split(",") if t] or None

    sess_files = list_sessions(parent, only=only)
    set_label = args.set_label.strip() or f"{len(sess_files)}sess"
    if args.session_mean:
        set_label += "-meansub"         # keep the v1 ablation outputs separate
    if len(sess_files) < 2:
        print(f"[ERROR] LOSO needs >=2 sessions; found {len(sess_files)} in {parent}")
        return
    preproc = "v1_session_mean" if args.session_mean else "v2_no_session_mean"
    print("=" * 66)
    print(f"MLP REG LOSO  --  {setup_name}  [{set_label}]  --  {mode.upper()} ports {ports}")
    print(f"  input={args.input_kind}  preproc={preproc}  adjust={args.adjust_key}"
          f"  ridge={args.ridge}")
    print(f"  sessions: {[n for n, _ in sess_files]}")
    print("=" * 66)

    sessions = {}
    for name, path in sess_files:
        t0 = time.time()
        per_pos, base_c, _ = load_session(path, mode, ports, remap=remap)
        sessions[name] = (per_pos, base_c)
        print(f"  loaded {name}: {len(per_pos)} positions  ({time.time()-t0:.1f}s)")

    # valid positions = present in every session
    pos_sets = [set(pp.keys()) for pp, _ in sessions.values()]
    valid = sorted(set.intersection(*pos_sets))
    n_pos = len(valid)
    valid_labels = [pos_id_to_label(p) for p in valid]
    valid_xy = targets_for_labels(valid_labels, args.adjust_key)   # (n_pos, 2)
    target_of = {p: valid_xy[i] for i, p in enumerate(valid)}
    # positions hugging the glandular insert = the photo-adjusted labels
    adj_labels = set(load_adjustments(args.adjust_key).keys())
    near_insert = {p: (valid_labels[i] in adj_labels) for i, p in enumerate(valid)}
    n_adjusted = sum(near_insert.values())
    print(f"  common positions: {n_pos}   photo-adjusted (near-insert): {n_adjusted}")

    # precompute features + targets per session
    feats, yposes = {}, {}
    for name, (per_pos, base_c) in sessions.items():
        Xc = np.concatenate([per_pos[p] for p in valid], axis=0)
        ypos = np.concatenate([np.full(per_pos[p].shape[0], p) for p in valid]).astype(np.int64)
        Y = calibrate(Xc, base_c, mean_sub=args.session_mean)      # v2 default
        feats[name] = build_features(Y, mode, args.input_kind)
        yposes[name] = ypos

    sids = list(sessions.keys())
    fold_summ = []
    pos_err_acc = defaultdict(list)      # pos id -> per-fold median-point error
    pos_spread_acc = defaultdict(list)   # pos id -> per-fold prediction spread
    for test_sid in sids:
        t0 = time.time()
        train_sids = [s for s in sids if s != test_sid]
        X_tr = np.concatenate([feats[s] for s in train_sids])
        T_tr = np.concatenate([np.stack([target_of[int(p)] for p in yposes[s]])
                               for s in train_sids])
        sess_tr = np.concatenate([np.full(feats[s].shape[0], j)
                                  for j, s in enumerate(train_sids)])
        X_te = feats[test_sid]
        ypos_te = yposes[test_sid]
        T_te = np.stack([target_of[int(p)] for p in ypos_te])

        X_tr_z, _ = per_session_zscore(X_tr, sess_tr)              # the KEY trick
        X_tr_z = X_tr_z.astype(np.float32, copy=False)   # bound memory (51.6k-D)
        del X_tr
        mu = X_te.mean(0); sd = X_te.std(0) + 1e-8
        X_te_z = ((X_te - mu) / sd).astype(np.float32, copy=False)

        pred = train_predict_reg(X_tr_z, T_tr, X_te_z, use_ridge=args.ridge)

        # trial-level
        trial_err = np.linalg.norm(pred - T_te, axis=1)
        trial = err_stats(trial_err)

        # position-level: median predicted point per position (vote analog),
        # plus spread = mean radial distance of the trials from that median
        by_pos = defaultdict(list)
        for p, xy in zip(ypos_te, pred):
            by_pos[int(p)].append(xy)
        rows = []
        for p, preds_p in by_pos.items():
            P = np.stack(preds_p)
            med = np.median(P, axis=0)
            e = float(np.linalg.norm(med - target_of[p]))
            spr = float(np.linalg.norm(P - med, axis=1).mean())
            rows.append((p, e, spr))
            pos_err_acc[p].append(e)
            pos_spread_acc[p].append(spr)
        errs = np.array([r[1] for r in rows])
        sprs = np.array([r[2] for r in rows])
        position = err_stats(errs)
        position["medianSpreadIn"] = float(np.median(sprs))

        # stratified: near-insert (photo-adjusted) vs exterior positions
        strat = {}
        for gname, sel in (("nearInsert", True), ("exterior", False)):
            ge = np.array([r[1] for r in rows if near_insert[r[0]] == sel])
            gs = np.array([r[2] for r in rows if near_insert[r[0]] == sel])
            strat[gname] = (dict(n=int(ge.size), **err_stats(ge),
                                 medianSpreadIn=float(np.median(gs)))
                            if ge.size else dict(n=0))

        # centroid baseline (regression "chance")
        centroid = T_tr.mean(0)
        base_err = np.linalg.norm(T_te - centroid[None, :], axis=1)
        baseline = err_stats(base_err)

        fold_summ.append(dict(testSession=test_sid, trial=trial, position=position,
                              stratified=strat, baselineCentroid=baseline))
        ni = strat["nearInsert"]
        ni_txt = (f"near-insert med={ni['medianErrIn']:.3f}in(n={ni['n']})  "
                  if ni["n"] else "")
        print(f"  fold test={test_sid}:  trial med={trial['medianErrIn']:.3f}in  "
              f"pos med={position['medianErrIn']:.3f}in  "
              f"<=0.5in {position['pctWithinHalfIn']:.0f}%  "
              f"spread={position['medianSpreadIn']:.3f}in  {ni_txt}"
              f"centroid med={baseline['medianErrIn']:.2f}in  ({time.time()-t0:.1f}s)")

    def loso(fn):
        v = [fn(f) for f in fold_summ]
        return float(np.mean(v)), float(np.std(v))

    def loso_group(gname, key):
        v = [f["stratified"][gname][key] for f in fold_summ
             if f["stratified"][gname]["n"]]
        return [float(np.mean(v)), float(np.std(v))] if v else None

    per_position = []
    for i, p in enumerate(valid):
        per_position.append(dict(
            label=valid_labels[i], pos=int(p),
            x=float(valid_xy[i][0]), y=float(valid_xy[i][1]),
            medianErrIn=float(np.mean(pos_err_acc[p])),
            spreadIn=float(np.mean(pos_spread_acc[p])),
            nearInsert=bool(near_insert[p])))

    result = dict(
        method="MLP-REG", task="regression_xy_inches",
        setup=setup_name, sessionSet=set_label,
        inputKind=args.input_kind, freqGrid="native791",
        preproc=preproc, adjustKey=args.adjust_key, ridge=bool(args.ridge),
        antennaMode=mode, ports=list(ports),
        numSessions=len(sids), sessionNames=sids,
        numPositions=n_pos, numAdjustedTargets=int(n_adjusted),
        folds=fold_summ,
        losoTrialMeanErr=loso(lambda f: f["trial"]["meanErrIn"]),
        losoTrialMedianErr=loso(lambda f: f["trial"]["medianErrIn"]),
        losoPosMeanErr=loso(lambda f: f["position"]["meanErrIn"]),
        losoPosMedianErr=loso(lambda f: f["position"]["medianErrIn"]),
        losoPosPctHalfIn=loso(lambda f: f["position"]["pctWithinHalfIn"]),
        losoPosPct1In=loso(lambda f: f["position"]["pctWithin1In"]),
        losoPosMedianSpread=loso(lambda f: f["position"]["medianSpreadIn"]),
        losoNearInsertMedianErr=loso_group("nearInsert", "medianErrIn"),
        losoNearInsertPctHalfIn=loso_group("nearInsert", "pctWithinHalfIn"),
        losoNearInsertMedianSpread=loso_group("nearInsert", "medianSpreadIn"),
        losoExteriorMedianErr=loso_group("exterior", "medianErrIn"),
        losoExteriorPctHalfIn=loso_group("exterior", "pctWithinHalfIn"),
        losoExteriorMedianSpread=loso_group("exterior", "medianSpreadIn"),
        losoCentroidMedianErr=loso(lambda f: f["baselineCentroid"]["medianErrIn"]),
        perPosition=per_position,
    )
    ports_tag = "-".join(str(p) for p in ports)
    tag = f"{setup_name}_{set_label}_{args.input_kind}_{mode}_ant{ports_tag}".replace(" ", "_")
    out = RESULTS_DIR / f"mlp_regloso_{tag}.json"
    with open(out, "w") as f:
        json.dump(result, f, indent=2)

    print("-" * 66)
    print(f"  LOSO position median err : {result['losoPosMedianErr'][0]:.3f} "
          f"+/- {result['losoPosMedianErr'][1]:.3f} in")
    print(f"  LOSO position <=0.5 in   : {result['losoPosPctHalfIn'][0]:.1f} %")
    print(f"  LOSO median spread       : {result['losoPosMedianSpread'][0]:.3f} in")
    if result["losoNearInsertMedianErr"]:
        print(f"  near-insert / exterior   : {result['losoNearInsertMedianErr'][0]:.3f}"
              f" / {result['losoExteriorMedianErr'][0]:.3f} in median")
    print(f"  centroid baseline median : {result['losoCentroidMedianErr'][0]:.2f} in")
    print(f"  saved {out}")


if __name__ == "__main__":
    main()
