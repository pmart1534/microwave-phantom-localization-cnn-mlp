# Changelog

Running log of what changed, when, and why. Newest first. Each substantive
change to code, method, or results should land as its own commit with a matching
entry here.

## 2026-07-31 - Frequency_Reduction deck: Part 2 "trying to break it" (slides 9-12)

- `presentation/gen_deck_band.js`: appended four slides - break-tier definitions
  (DEGRADED/UNSTABLE/BROKEN/DEEP), the nine-window 0.25 GHz placement scan
  (2-2.25 GHz best; below ~1.25 GHz even the empty phantom crosses the 50% line),
  the best-per-width descent curve (`assets/break_curve.png`), and the per-phantom
  break verdict table (Empty/F4 never break; F5 degraded at 0.5 GHz, unstable at
  1 GHz, never <50%; floors 99.3/90.4/59.6 at 50 MHz).
- Rebuilt `Frequency_Reduction.pptx` (12 slides) + PDF.
- Adaptive hardware x band break-descent sweep (`cnn_matlab/break_descent.sh`)
  launched in background; results will extend this deck as Part 3.


## 2026-07-31

- **Breaking-point analysis + ultra-narrow descent + 0.25 GHz placement scan.**
  New `analyze_break_points.py` (-> `results/break_analysis.md`,
  `break_curve.png`): per-phantom best-window-per-width curves with failure
  tiers (DEGRADED < 90% of full-band, UNSTABLE fold-sigma >= 10, BROKEN < 50%,
  DEEP < 25%). Conv kernels now clamp to `min(20,nFreq)` / `min(10,nFreq)`
  (original program's convention) enabling windows below 0.2 GHz. Findings with
  the full array: Empty NEVER breaks by any tier down to 0.05 GHz (99.3%); F4
  never crosses any tier (floor 90.4 +/- 7.1 at 0.05 GHz); F5 degrades at
  0.5 GHz, goes unstable at 1 GHz, but never crosses 50% (floor 59.6 +/- 17.8
  at 0.05 GHz). Placement scan across nine 0.25 GHz windows: best slot is
  phantom-dependent (F5: 2-2.25 at 83.8 +/- 3.5, beating 1.75-2's 80.8 +/- 12.6;
  F4: 3.5-3.75 at 98.1). With 16 S-parameters the model cannot be pushed below
  50% by bandwidth alone.

## 2026-07-29

- **Sub-4 GHz "break it" descent (Phases 1-2, CNN, raw, all 16 S-params).**
  Ceiling: 0.1-4 GHz AND 1-4 GHz both hit F5 = 100% (the no-above-4-GHz chip
  constraint is free; 1-4 even beats same-width 1.5-4.5). Best-per-width on F5:
  3 GHz 100 -> 2 GHz 92.9 -> 1 GHz 92.9 (1.5-2.5) -> 0.5 GHz 88.9 (1.5-2) ->
  0.25 GHz 80.8 (1.75-2). Mean degrades gracefully but fold-to-fold sigma
  EXPLODES below 1 GHz width (F5 +/-12-20 vs +/-0-5 at 3 GHz): narrow bands
  become session-unstable before they become inaccurate. Empty stays 99.4
  everywhere, F4 88-99.

## 2026-07-17

- **Frequency-reduction deck.** `presentation/Frequency_Reduction.pptx` (8
  slides, same cream/serif theme as the classification decks): motivation,
  band-placement table, bandwidth-expansion table, combined figure, chip
  operating points @ 1-5 GHz, single-antenna robustness check, recommendation
  (spec 1-5 GHz, fallback 1.5-4.5, avoid >5 and <1 alone, antennas<->bandwidth
  trade). Generator `gen_deck_band.js`.


- **Stage C (chip operating point) + single-antenna band sweep.**
  At the winning 1-5 GHz band: refl-all 100/97.4/94.9, pair full-S
  99.3/92.9/92.9, pair refl-only 99.3/92.9/84.8, single S11 96.1/96.2/69.7
  (empty/F4/F5). Reductions COMPOUND on F5: the band cut that was free with 16
  S-params costs 3-6 pts once antennas/transmission are removed. Single-antenna
  band sweep (all windows): 2-4 GHz again the best 2 GHz window (0.1-2 GHz
  collapses to 25% on F5 without array diversity); accuracy climbs monotonically
  with width, needing ~5 GHz (0.5-5.5) for near-parity with full band. Combined
  figure: `results/band_sweep_combined.png`. Takeaway: antennas and bandwidth
  are partially interchangeable information budgets; the 2-4 GHz region is the
  information centre at both hardware extremes.

- **Bandwidth-reduction sweep (CNN classification, chip-design study).**
  `Imager_CNN_LOSO.m` gains `CNN_LOSO_BAND="lo hi"` (GHz) to crop the frequency
  axis; outputs tagged `_band<lo>-<hi>`. Stage A: four 2 GHz windows x 3
  phantoms (raw, all 16 S-params, LOSO). Winner 2-4 GHz (mean 96.6%); high
  bands collapse on F5 (~70%, penetration physics). Expansion around the same
  region: 3/4/5 GHz. Result: **1-5 GHz (4 GHz BW) recovers full-band accuracy
  on every phantom** (empty 99.4 / F4 98.1 / F5 100.0); 1.5-4.5 GHz costs only
  ~1-3 pts on F5; 2-4 GHz alone costs 7 pts on F5. Curve:
  `results/band_sweep_curve.png`.

- **Classification decks: restyle + training-cost comparison.** Both
  `presentation/CNN_vs_MLP_Comparison{,_v2_noMeanSub}.pptx` reskinned from the
  solid-red title/divider slabs to the casual warm theme used by the regression
  decks (cream `FDF8F6` background, thin red top bar, red vertical accent,
  Cambria serif titles, muted greys). Added measured training-time facts in four
  places (structural table row, per-model cost bullets, summary box, conclusions
  card): CNN 5-45 min per LOSO fold on RTX 3070, ~20 GPU-h full sweep; MLP
  10 s-7 min per fold on CPU, ~3-4 CPU-h for the same sweep (~10x faster);
  inference is milliseconds for both.

- **Deck 3 revision (sim vs measured).** Reskinned to warm UofU theme with light
  title/closing slides; all em dashes removed. (1) Grid slide is now 3 panels:
  sim lattice, physical grid with the traced A3 bowl, and a true OVERLAY
  registered into one physical frame via `grid_placed_global.csv` (exact affine,
  0.0 mm residual). (2) Setup table: antennas are the SAME design ("Sam's Medium
  Antennas") in both; measured depth corrected to ~5 to 20 mm (near the patch),
  not +40 mm. (3) Raw S-parameters now shown PER PORT (2x2), not averaged, with
  measured clipped to 2-8 GHz: sim ports near-identical, measured ports differ.
  (4) New detectable-difference slide: measured empty DD (from the
  detectable_change program's npz) vs sim empty DD at z=+15 mm, same physical
  frame, showing the same spatial pattern (`fig_dd_compare.py`). (5) Numbers
  slide adds a "What is k-NN?" explainer and shows measured CNN LOSO (3.9 mm) vs
  LOPO single-position (9.9 mm). (6) Correlation figure caption wraps (no longer
  squished). Also removed the wrong +40 mm measured marker from the Deck 2 dS
  figure.

- **Deck 2 revision (simulated) + shared style fixes.** (1) Light title/closing
  slides (mostly white, crimson highlights) replacing the dark maroon, applied to
  Deck 1 and Deck 2. (2) Deck 2 reskinned to the UofU warm-red theme; all em
  dashes removed. (3) "Sam's Medium antennas" naming. (4) `fig_dS_vs_depth`
  caption now wraps (3 lines) so the plot is no longer squished; figure saved at
  fixed aspect and placed undistorted. (5) `fig_learning_curve.py` (new,
  replacing the inline figure): point labels clarified ("1 plane", then plane
  counts) with an explicit "point label = number of depth planes" box; plateau
  label moved clear of the point labels. (6) `fig_depth_lopo` renames "range
  edge" to "outer edge depth". (7) New "setup in pictures" slide in Deck 1 and
  Deck 2; placeholders live in `regression_deck/setup_photos/` (measured_bench,
  measured_grid, sim_model, sim_closeup) for the user to replace.
- **Located measured multi-depth data**: `.../Separated/July10/A3TumorDepthTesting_JULY10`,
  4 sessions at tumor heights (port-relative) -20, -7, +15, +25 mm (the 1227
  session's "2.5 cm below" is actually +25 above). The measured analog to the sim
  depth sweep.
- **Measured |dS| vs depth** (`fig_measured_dS_vs_depth.py` -> `measured_dS_vs_depth.png`,
  new Deck 2 slide "The bench sees the same depth shape"). Mean |dS| (tumor minus
  empty baseline, per-position averaged over 16 takes) at the 4 measured heights:
  -20 mm 0.0023, -7 mm 0.0042, +15 mm 0.0053 (peak), +25 mm 0.0044. The bench
  perturbation peaks at the radiating patch (+15 mm) and falls off both ways, the
  same shape the noiseless sim shows: an independent measured confirmation of the
  depth story.

## 2026-07-16

- **Deck 1 revision (measured).** (1) Predicted-vs-actual plots now overlay the
  TRACED A3 phantom bowl + F4/F5 glandular outlines (from
  detectable_change/A3_hunter/paper_figure_A3.py) instead of a binary
  near/exterior guess, so insert membership is read directly off the figure.
  (2) UofU warm-red theme (crimson/gold/maroon) across all slides; all em dashes
  removed. (3) New protocol-explainer slide (LOSO vs LOPO-cell vs single-position,
  with schematics + difficulty ladder). (4) LOPO slides now state the model (CNN)
  and define pooled vs in-session. (5) Single-position split into a graphical
  slide + an accuracy slide, matching the other two protocols. (6) Mixup slide
  reframed ("lower is better; grey = worse, crimson = the only win"). F4
  single-position run launched (pooled/subpos, 39 positions) to complete the set;
  its figure/number are placeholders until it lands.

## 2026-07-15

- **Three presentation decks** (`regression_deck/deck{1,2,3}_*.js` →
  `Deck1_Measured_Regression.pptx`, `Deck2_Simulated_Regression.pptx`,
  `Deck3_Sim_vs_Measured.pptx`). Deck 1: measured setup/algorithm + LOSO,
  LOPO-cell, LOPO-subpos across empty/F4/F5. Deck 2: sim setup, |ΔS|-vs-depth,
  data-need learning curve, 8-fold 3D result, depth generalization, per-depth
  examples. Deck 3: sim-vs-measured grids, raw S-param domain gap, the corrected
  numerical comparison (signal ~6 mm both; CNN gap = distinct-position coverage),
  and an exploratory sim→measured transfer. Reusable `render_pptx.ps1`
  (PowerPoint COM → PNG). QA renders gitignored.
- **New figures** (`regression_deck/`): `sim_dS_vs_depth.png` (tumor
  perturbation peaks at z≈15–20 mm, falls off both ways), `sim_depth_lopo.png`
  (leave-one-depth-out; interior ~1–3 mm, edges extrapolate), `grid_sim_vs_physical.png`
  (uniform 10 mm sim vs 6×6 physical cells, 51 measured), `raw_sparam_sim_vs_meas.png`
  (antenna domain gap), `sim_meas_correlation.png` (linear sim→measured transfer
  R²=0.65 on held-out freqs; MLP overfits, R²<0).
- **Figure fixes.** `sim_dS_vs_depth.png` now distinguishes the antenna **port /
  feed** (z = +3 mm) from the **radiating patch** (~15–20 mm in, due to the
  feed-line offset), plus the measured-tumor depth (z = +40 mm). The |ΔS| peak at
  ~15 mm coincides with the patch radiator — the tumor is nearest the *radiating
  element* there, not the feed. (Earlier drafts wrongly put the antenna at +3 mm
  and called the peak a pure array effect.) All raw S-parameter plots now display
  in dB (`sim_meas_correlation.png` S11 panel converted; `raw_sparam_*` already dB).

## 2026-07-14

- **Measured-empty single-point CNN LOPO (closes the sim↔measured comparison).**
  True leave-one-position-out on the empty A3 phantom, 3 June18 sessions pooled,
  51 positions, raw/all-antenna: **median 9.9 mm** (mean 12.0; 66.7% ≤0.5 in).
  Loses to training-free k-NN (6.0 mm) on the same task. Correction to first
  draft: each position is measured 16× (takes `T01…T16`) and `buildSession` uses
  every take as a sample, so training is ~2,400 raw samples — raw count is *not*
  the limiter. The limiter is **distinct spatial positions (~50)**; takes and
  sessions are repeat measurements of the same grid points, so they add
  robustness (→ LOSO 3.9 mm) but no new locations (→ LOPO 9.9 mm). The sim hit
  3.9 mm via ~1,000 *distinct* locations (13 depths × ~82). Gap is
  **distinct-position coverage, not sim-vs-real fidelity**. `RESULTS.md §3`.
- **Sim CNN data-quantity learning curve** (`SIM_DEPTHS` filter). 8-fold xy vs #
  depth planes (metal): 1 depth (82) 33 mm ≈ chance → 3 (245) 11 mm → 5 (410)
  4.8 mm → plateau ~3.8 mm from 7 (570). CNN needs ~400–500 samples to localize.
  Explains why single-layer LOO collapses while multi-depth works. Figure
  `sim_depth_learning_curve.png`, `RESULTS.md §5`.

## 2026-07-11

- **Beet (dielectric) tumor localization.** Loader now auto-detects a single
  `baseline_empty.s4p` (beet) vs the per-batch map (metal); `SIM_LABEL` tags
  outputs. 8-fold on the beet sweep (1065 pos): **xy 3.64 mm, z 2.07 mm** —
  statistically identical to metal (3.92 / 2.09). In the noiseless sim the ~19%
  weaker dielectric contrast costs nothing (signal still far above the numerical
  floor, equally position-coherent). See `RESULTS.md §5`.
- **Clean 5 mm depth grid** — data consolidated to `Data Results/A3_Metal_1cm`
  (single folder, per-batch empty baselines); loader rewritten to subtract each
  depth's own HFSS-batch baseline and to **exclude the off-grid z=3 mm plane**
  (`SIM_EXCLUDE_Z`). 1074 positions, 13 uniform depths. 8-fold: xy 3.92 mm,
  z 2.09 mm. Removing z=3 raised z=5's depth-out error 0.8→1.5 mm — z=3 had been
  a 2 mm-away helper; 1.5 mm is the honest uniform-grid value. Results tagged
  `_5mmgrid` (z=3-included versions preserved). See `RESULTS.md §5`.
- **Sim depth range extended to z = −15…+45 mm** (added b1_3_ALL_RESULTS →
  1134 positions, 14 depths). 8-fold: xy 3.71 mm, z 1.98 mm. Per-depth
  leave-one-depth-out shows (a) a **genuine gradual depth falloff** — z-error
  0.8 mm near the antenna plane climbing to ~3.7 mm at +40 mm; (b) the earlier
  "hard edges" −5/+30 mm were pure **extrapolation** — with neighbors on both
  sides they drop to 1.5/2.5 mm; new edges −15/+45 mm are the ~8–10 mm limits.
  Usable depth is bounded by the sampling range, not the model. See `RESULTS.md §5`.

## 2026-07-10

- **Simulated 3D (x,y,z) localization** (`cnn_matlab/Imager_CNN_SimReg.m`).
  SamMakin HFSS tumor sweep, 738 positions × 9 depths, differential dS input,
  `fc(3)` head, 8-fold position CV. **Result: lateral 3.35 mm, depth 1.55 mm**
  median (vs 36.7 / 8.6 mm chance) — matches k-NN floor on xy, beats it on z.
  Depth is not the weak axis (fine z sampling + full-band freq). Feasibility
  (`sim_feasibility_check.py`) + physics exploration (`sim_explore.py`, in the
  Simulation Data tree) established the signal is learnable and depth-robust.
  See `RESULTS.md §5`.
- **Leave-one-depth-out** (`SIM_CV=depth` mode added). Interior depths (0–25 mm)
  predict an unseen depth plane to z ≈ 1 mm — proves the CNN learned a continuous
  depth mapping, not memorized planes. Edge depths (−5/+30 mm) are extrapolation
  and degrade to 6–8 mm (expected). xy unaffected. See `RESULTS.md §5`.
- **Deck extended to the full phantom × protocol matrix** — predicted-vs-actual
  figures for empty/F4/F5 under both LOSO and LOPO (`regression_deck/`).

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
