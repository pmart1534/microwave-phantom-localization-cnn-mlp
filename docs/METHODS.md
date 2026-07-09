# Methods

This project compares two localization methods (CNN in MATLAB, MLP in Python)
on the **same** Hunter 4-port VNA data of the **A3 breast phantom**, under
**identical** cross-validation protocols. It covers two tasks:

- **Classification** — predict which discrete grid position a target sits at.
- **Regression** — predict the continuous `(x, y)` inch coordinate directly.

And three evaluation protocols, kept strictly distinct in code and in output
filenames so results never mix:

| Protocol | Holds out | Question it answers | Script(s) |
|---|---|---|---|
| **LOSO** | a whole recording session | new scan of a *known* grid | `Imager_CNN_LOSO.m`, `run_mlp_loso.py`, `Imager_CNN_RegLOSO.m`, `run_mlp_regloso.py` |
| **LOPO pooled** | a position, across *all* sessions | interpolate to an unseen spot **and** generalize across sessions | `Imager_CNN_RegLOPO.m` (`LOPO_MODE=pooled`) |
| **LOPO in-session** | a position, within one session at a time | *pure* spatial interpolation (session drift removed) | `Imager_CNN_RegLOPO.m` (`LOPO_MODE=insession`) |

LOPO also has a **granularity** switch (`LOPO_UNIT`): `cell` holds out a whole
`RxCy` cell (all sub-positions, ~1 inch gap — the hard test); `subpos` holds
out one sub-position (its 3 cell-mates ~0.75 in away stay in training — gentle).

## Data pipeline (shared by all protocols)

1. **Load** one Hunter session folder → complex 4-port S-parameters at the
   native 791-point, 0.1–8 GHz grid (16 S-params, or `2·mag/phase` = 32 rows).
2. **Baseline subtraction** — subtract the averaged empty-chamber baseline:
   `Y = S − S_baseline` (per S-param).
3. **Preprocessing = v2 (default):** baseline subtraction **only**. The older
   v1 per-session *mean* subtraction is available as an ablation
   (`--session-mean` / `CNN_LOSO_MEANSUB=1`) but is **not** the default — v1 was
   found to bake a preprocessing flaw into cross-session results.
4. **Input representation** (identical channel set for CNN and MLP):
   - `raw` — magnitude + phase per S-param.
   - `physics` — mag, phase, real, imag, + IFFT/TDR envelope per S-param.
   - `tdr` — IFFT/TDR envelope only.
5. **Per-session z-score** ("the KEY trick") — standardize each session by its
   own per-pixel statistics. Applied to train and test sessions alike.
6. **Head:**
   - Classification — `fc(nClasses) → softmax`.
   - Regression — `fc(2) → regressionLayer` (MSE on `(x, y)` inches).
   The convolutional trunk is otherwise unchanged between tasks.

The CNN and MLP each keep their **native** front-end (CNN eats the raw image,
MLP eats the flattened feature vector) — deliberate, so we compare the methods
as actually used, not swapped inputs.

## Regression targets — grid geometry

Continuous targets come from the `RnCmPp` labels via the canonical grid map
(`mlp_python/label_xy.py`, mirrored in the MATLAB `labelToXY`):

```
cell centre : x = (col − 0.5) · 1.0 in,  y = (row − 0.5) · 1.0 in   (origin top-left, y down)
sub-position: ±0.375 in from centre  (0.5 half-cell − 0.125 half-divider)
              P1 = TL(−,−)  P2 = TR(+,−)  P3 = BR(+,+)  P4 = BL(−,+)
```

**Photo-corrected positions.** Where the glandular insert blocked the exact
corner spot, the true measured position was digitized from calibrated phantom
photos and stored in `position_adjustments.json` (a snapshot lives in
`reference/`). Applied via `--adjust-key` / `CNN_LOSO_ADJUST_KEY`:
`A3_Empty` (0 corrections), `A3_F4` (16, mean shift 0.198 in),
`A3_F5` (9, mean 0.226 in, max 0.382 in).

> Note: `hunter_loader._rcp_to_xy` uses a *different* approximate grid
> (1.25 in pitch, ±0.25 in). That is fine for the classification dot plots it
> serves but is **wrong for regression targets** — `label_xy.py` is the single
> source of truth for regression and is used everywhere targets matter.

## Metrics (regression) — error distance only

Predictions are **never** snapped to grid positions. Every accuracy number is a
Euclidean distance in inches from the continuous prediction to the true target.

- **Trial-level** — error per individual trial: mean, median, % within 0.5 in
  (half-cell), % within 1 in.
- **Position-level** — the majority-vote analog: take the **median** predicted
  point over a position's ~16 trials, then that point's error. Same summary
  stats across positions.
- **Prediction spread** — per position, the mean radial distance of its trial
  predictions from their median point. A built-in confidence proxy; inflates
  where the model is uncertain.
- **Stratified** — `near-insert` (the photo-adjusted labels that hug the
  glandular insert) vs `exterior`, reported separately so insert-region error
  never pollutes the exterior statistics.
- **Centroid baseline** — error of always predicting the training centroid
  ("regression chance"); a trained model must beat it decisively.

## Reproducibility notes

- **No leakage.** In LOSO the held-out session is never used as validation
  during training. In LOPO the held-out position's samples are excluded from
  training; per-session z-score is label-free (standardizes signal pixels, never
  sees the `(x, y)` target), so it cannot leak position identity.
- **Same positions.** All protocols restrict to positions present in every
  session, so the label set matches across folds and methods.
- **Determinism.** `rng(42)` (MATLAB) / fixed seeds `(42, 7, 13)` (Python
  3-seed ensemble). GPU nondeterminism gives small run-to-run variation.
