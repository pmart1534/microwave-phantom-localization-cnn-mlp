# Results

All numbers are **leave-one-*-out**, full 4-antenna array (16 S-params) unless
noted. Regression metric = position-level median localization error in inches
(lower is better); classification metric = per-position vote accuracy (higher
is better). See `METHODS.md` for definitions.

## 1. Classification (recap)

Per-position vote accuracy, LOSO. Full table and discussion in the top-level
`README.md`. Headline: with the full 16-S-param array, **CNN ≈ MLP, both near
ceiling** (97–100%) on empty/F4/F5; they diverge only under aggressive antenna
reduction (single S11), where the CNN suffers high-variance single-fold
collapses and the MLP's per-session z-score keeps it steadier.

## 2. Regression — LOSO (new scan of a known grid)

Position median error in inches (**% of positions within the 0.5 in half-cell**).
Raw input, all 16 S-params. Centroid baseline = "regression chance."

| Setup | CNN raw | CNN physics | MLP raw | MLP physics | Centroid |
|---|---|---|---|---|---|
| June18 empty (51 pos) | **0.156 (100%)** | 0.156 (99%) | 0.481 (54%) | 1.330 (11%) | 1.34 |
| F4 small insert (39 pos) | **0.167 (97%)** | 0.162 (94%) | 0.695 (29%) | 1.084 (19%) | 1.73 |
| F5 large insert (33 pos) | **0.221 (90%)** | 0.258 (88%) | 0.759 (30%) | 1.312 (11%) | 1.30 |

**Findings**

1. **The CNN owns regression** — ~0.16 in on empty (a sixth of a cell), under a
   quarter-inch even on F5, 88–100% of positions inside the half-cell.
2. **CNN is input-robust; raw is the pick.** Physics ≈ raw for the CNN
   everywhere (raw marginally better on F4/F5), so raw wins on simplicity/speed.
3. **The MLP is the opposite of its classification self.** Raw MLP is 3–4×
   worse than the CNN, and **physics features break it entirely** — all three
   land at the centroid baseline (it just predicts grid center). The
   ~52k-dimensional physics vector swamps the MLP's capacity for regression.
   (In classification, physics was the MLP's *best* configuration.)

**Insert stratification (physics-input LOSO — raw runs predate the stratified
metric).** Near-insert vs exterior median error:

| | CNN near / ext | MLP near / ext |
|---|---|---|
| F4 | 0.134 / 0.169 | 1.189 / 0.907 |
| F5 | 0.228 / 0.280 | 1.646 / 1.170 |

In **LOSO**, near-insert positions are localized *as well or better* than
exterior for the CNN. Interpretation: every position (insert included) appears
in training, so the model memorizes the insert signatures; "near-insert" here
mostly reflects central-vs-edge grid geometry (central = easier).

## 3. Regression — LOPO whole-cell (interpolate to an unseen location)

Hold out a whole cell (all its sub-positions) — the model must predict a
location it has **never seen a signature for**. Raw input, all 16 S-params,
40 epochs (reduced for the many folds; preliminary).

| Setup | pooled/cell | in-session/cell | *(LOSO raw, ref)* |
|---|---|---|---|
| June18 empty | **0.448 (59%)** | 0.661 (29%) | *0.156* |
| F4 small insert | **0.482 (51%)** | 0.609 (40%) | *0.167* |
| F5 large insert | **0.664 (33%)** | 0.753 (31%) | *0.221* |

Near-insert vs exterior median error (LOPO whole-cell):

| | pooled near / ext | in-session near / ext |
|---|---|---|
| F4 | **0.75 / 0.41** | 0.67 / 0.54 |
| F5 | 0.75 / 0.65 | 0.93 / 0.69 |

**Findings**

1. **Interpolation is ~3–4× harder than session transfer.** LOPO-cell errors
   (0.45–0.75 in) vastly exceed LOSO (0.16–0.22 in). The data supports "new scan
   of a known grid" far better than "predict an unmeasured spot." *This is the
   headline distinction between the two protocols.*
2. **Pooled beats in-session on all three setups** (June18 0.45 vs 0.66;
   F4 0.48 vs 0.61; F5 0.66 vs 0.75) — despite in-session removing session
   drift. For interpolation, the extra training data from pooling outweighs the
   drift it introduces: **more data > cleaner data**.
3. **The glandular barrier finally shows up.** In LOPO, near-insert cells are
   *worse* than exterior in every insert setup — starkest at **F4 pooled (0.75
   vs 0.41 in, ~1.8×)**, and F5 in-session (0.93 vs 0.69). This is the
   **opposite** of the LOSO pattern. Because the held-out insert position is
   never seen, the model must interpolate across the dielectric discontinuity at
   the barrier, where the field is non-smooth and interpolation fails hardest.
   The interpolation test surfaces physics the session-transfer test masked.

> Sub-position LOPO granularity is parked (gentle interpolation, ~5× the fold
> cost); run only if whole-cell proves insufficient.

## 4. Improving interpolation (LOPO pooled/cell experiments)

Baseline = plain LOPO pooled/cell (§3). Testbed = **F5** (hardest setup),
raw/all-antenna, 40 epochs.

| variant | median (in) | ≤0.5 in | ≤1 in | near / ext |
|---|---|---|---|---|
| baseline | 0.664 | 33% | 67% | 0.75 / 0.65 |
| **+ mixup** (α=0.4, ratio=1) | **0.572** | 39% | 76% | **0.61 / 0.56** |

**Exp 1 — mixup: helps, and helps the barrier most.** −0.09 in overall (~14%),
and the **near-insert cells improve more than exterior** (0.75→0.61 vs
0.65→0.56). Offline mixup appends synthetic training samples that are convex
blends of random training pairs with matching blended `(x, y)` targets
(`MIXUP_ALPHA` flag). Contrary to the over-smoothing worry, synthesizing
intermediate signal↔coordinate points *fills* the spatial gaps rather than
washing out the dielectric discontinuity — net-positive exactly where
interpolation was hardest.

Queued (pooled/cell):
- **Exp 2 — position-disjoint validation** — model selection on held-out
  *positions* (not trials), rewarding spatial generalization.
- **Exp 3 — structured output** — heatmap-over-grid regression (centroid
  readout) and/or a Gaussian-Process head (smooth interpolation +
  distance-aware uncertainty).

See `CHANGELOG.md` for the running log of what changed when.
