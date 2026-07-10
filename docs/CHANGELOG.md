# Changelog

Running log of what changed, when, and why. Newest first. Each substantive
change to code, method, or results should land as its own commit with a matching
entry here.

## 2026-07-09

- **Experiment 3 — heatmap (structured) output** (`Imager_CNN_RegLOPO.m`,
  `HEAD_MODE=heatmap`). Head → `fc(G)→softmax→regression` over a 0.4-in anchor
  grid, Gaussian soft target, centroid readout; fold train/predict refactored
  into `fitPredictFold`. **Negative: F5 pooled/cell 0.895 (heatmap), 0.865
  (heatmap+mixup)** vs 0.664 baseline; near-insert nearly doubled (centroid
  mass-leakage pulls predictions to grid centre). **Verdict on all 3 experiments:
  mixup is the only winner; posval and heatmap both hurt on this small dataset.**
- **Experiment 2 — position-disjoint validation** (`Imager_CNN_RegLOPO.m`,
  `POSVAL_FRAC` flag; `trainCNNReg` gained optional validation data +
  `OutputNetwork='best-validation'`, `ValidationPatience=Inf` to isolate model
  selection from early-stop). Carve a fraction of TRAIN *positions* out as a
  validation set and keep the best-validation net. **Negative result: F5
  pooled/cell 0.664 → 0.927** — losing ~20% of the scarce training positions
  outweighed the selection benefit.
- **Experiment 2b — posval + mixup combined.** Mixup replenishes the lost data:
  F5 pooled/cell 0.722 — better than posval alone (0.927) but still below mixup
  alone (0.572). Conclusion: position-disjoint validation is a net negative on
  this dataset regardless; mixup alone is the winner. (One transient
  `CUDA_ERROR_UNKNOWN`/heap-corruption GPU crash on first attempt; clean on
  retry — 2nd such transient GPU fault this session.)
- **Experiment 1 — mixup augmentation** (`Imager_CNN_RegLOPO.m`, behind the
  `MIXUP_ALPHA` flag; off by default so baseline behavior is unchanged). Offline
  mixup: append `ratio·N` synthetic train samples, each a convex blend of a
  random training pair with matching blended `(x, y)` target. Train-only, no
  LOPO leakage. **F5 pooled/cell: 0.664 → 0.572 in** (~14%), and near-insert
  improved *more* than exterior (0.75→0.61 vs 0.65→0.56) — teaching a smooth
  signal→coordinate map helps the barrier region most. See `RESULTS.md §4`.
- **Repo initialized.** Placed the CNN-vs-MLP localization study (classification
  + regression + LOPO) under git. Added `.gitignore`, `docs/` (METHODS, RESULTS,
  DEPENDENCIES, this CHANGELOG), and a versioned snapshot of the target-defining
  `position_adjustments.json` under `reference/`.
- **LOPO whole-cell, first pass COMPLETE** (`Imager_CNN_RegLOPO.m`,
  raw/all-antenna CNN, 40 epochs). Both modes, all 3 setups (F4 pooled/cell
  re-run after its transient `0xc0000409` GPU crash: 0.482 in, near/ext
  0.75/0.41). Results: interpolation to an unseen cell is ~3–4× harder than
  LOSO; pooled beats in-session on all three setups; near-insert error exceeds
  exterior everywhere (glandular barrier surfaces under interpolation, starkest
  F4 pooled ~1.8×). See `RESULTS.md §3`.

## 2026-07-08

- **Metric change: error distance only.** Removed the nearest-position "snap
  accuracy" from both regression scripts' printouts and JSON — per decision that
  continuous localization error is the meaningful metric. Predictions are never
  snapped.
- **Added diagnostics** to both regression scripts: per-position prediction
  **spread** (confidence proxy) and **near-insert / exterior stratification**
  (so insert-region error doesn't pollute exterior stats).
- **MLP physics-input memory fix** (`run_mlp_regloso.py`): the 51.6k-D physics
  features OOM'd with 3 threaded float64 seeds on a 16 GB machine → switched to
  sequential seeds + float32 cast.
- **Stage-2 regression results** (raw + physics × CNN + MLP × 3 setups)
  completed. CNN wins decisively; raw ≈ physics for CNN; physics *breaks* the
  MLP (predicts centroid). See `RESULTS.md §2`.

## 2026-07-07/08 (regression conversion)

- **Built the regression pipeline** converting the position *classifiers* to
  continuous `(x, y)` regression:
  - `mlp_python/label_xy.py` — canonical `RnCmPp → (x, y)` grid map (±0.375 in
    corner offsets) + photo-adjustment overrides. Single source of truth for
    targets; deliberately bypasses `hunter_loader._rcp_to_xy` (a different,
    approximate map fine only for classification plots).
  - `mlp_python/run_mlp_regloso.py` — 3-seed `MLPRegressor(256,128)` average,
    v2 preprocessing default, `--adjust-key`, optional `--ridge`.
  - `cnn_matlab/Imager_CNN_RegLOSO.m` — same conv trunk, head → `fc(2) +
    regressionLayer`, v2 default, `CNN_LOSO_ADJUST_KEY`.
- **Geometry verified**: canonical corners + photo adjustments (A3_F4 16 pos,
  A3_F5 9 pos, A3_Empty none) checked against the recording code.
- First LOSO regression runs (raw) confirmed the CNN localizes to ~0.16 in.

## Earlier (classification baseline)

- `Imager_CNN_LOSO.m` (MATLAB) vs `run_mlp_loso.py` (Python) head-to-head under
  leave-one-session-out, antenna subsets (all / pair / single / refl). Empty /
  F4 / F5 A3 setups. See top-level `README.md`.
