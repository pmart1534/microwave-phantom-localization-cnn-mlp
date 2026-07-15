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

**Sim vs. measured, done right (model-agnostic k-NN, matched single layer).**
Comparing the CNN across sim and measured is confounded by data volume (the sim's
multi-depth sweep has ~940 training samples; a single sim layer has only ~82 —
too few to train a conv net, so the single-layer CNN LOO *collapses* to 29.5 mm
even though the signal is fine). Stripping that out with a training-free **k-NN
leave-one-position-out** on one layer, oil-only:

| single-layer k-NN LOO | xy error | chance |
|---|---|---|
| sim empty (z=+5) | 6.7 mm | 36 |
| **measured empty** | **6.0 mm** | 34 |
| measured F5 (glandular insert) | 13.4 mm | 33 |

**Sim ≈ measured for the oil-only phantom (6.7 vs 6.0 mm)** — the sim signal is
*not* unrealistically smooth; the real bench interpolates just as well. Two things
had masked this: (1) the CNN's sim advantage was **data quantity**, not signal
quality; (2) the **glandular insert** — not "sim vs real" — is what makes F5 hard:
F5 k-NN is 13.4 mm and the F5 single-point CNN LOPO was 14 mm, so they *match* —
the CNN hit F5's genuine ~13 mm interpolation floor set by the insert, it did not
"fail to interpolate." On the empty phantom that floor is ~6 mm in both sim and
measured. (Single-point LOPO ran via `LOPO_UNIT=subpos`; the single-layer sim LOO
via `SIM_CV=loo SIM_ONE_DEPTH`.)

**Measured-empty single-point CNN LOPO closes the loop (9.9 mm — starved on
distinct positions, not on raw samples).** Trained conv net, true
leave-one-position-out on the empty phantom, 3 sessions pooled (June18 ×3), 51
positions, raw/all-antenna: **median 9.9 mm** (mean 12.0; 66.7% ≤0.5 in, 96.1%
≤1 in; spread 0.039 in — very confident). This **loses to training-free k-NN
(6.0 mm)** on the *same* task, and the reason is subtle and important. Each grid
position is measured **16 times** (takes `T01…T16`); `buildSession` uses **every
take as its own sample**, so pooled empty is ~50 pos × 16 takes × 3 sessions ≈
**2,400 raw training samples** — plenty. Raw count is *not* the limiter. The
limiter is **distinct spatial positions (~50)**: the 16 takes and the 3 sessions
are *repeat measurements of the same grid points* (differing only by noise and
drift), so they add no new tumor locations. The map signal→(x,y) is anchored by
only ~50 places. The sim learning curve's real x-axis is distinct positions (the
sim has no repeat takes — noiseless): 82 → collapse, 245 → 11 mm, ~400–500 →
~4 mm; the sim hit 3.9 mm by sampling ~1,000 *distinct* locations (13 depth
planes × ~82). Measured empty's ~50 distinct locations sit in that starved
region → ~10 mm, exactly as seen.

The takes/sessions still help — but on a *different* axis: they teach a
noise/drift-robust map at **known** positions, which is precisely **LOSO**
(unseen session, seen positions) = **3.9 mm**; they do nothing for **LOPO**
(unseen position) because re-measuring the 50 known points says nothing about the
51st. That LOSO-vs-LOPO split is the fingerprint. And k-NN extracts 6 mm from the
same data without fitting anything, so the information is present — the CNN simply
can't *learn* a spatial map from ~50 anchor points, however many noisy copies of
each it sees. So the sim↔measured CNN gap (3.9 vs 9.9 mm) is **distinct-position
coverage, not sim-vs-real fidelity**: to match 3.9 mm on the bench we'd need many
more distinct measured locations (denser grid and/or multiple tumor depths, as
the sim has), not more takes and not a better model. (`LOPO_MODE=pooled
LOPO_UNIT=subpos`, result `cnn_reglopo_pooled_subpos_June18_remap_raw.json`.)

Protocol note: measured empty **LOSO** is 3.9 mm but tests an unseen *session* at
*seen* positions (easier); **LOPO** (9.9 mm) tests an unseen *position* — the hard,
apples-to-apples match to k-NN. The 3.9→9.9 mm jump is that protocol difference
plus the data starvation above.

## 4. Improving interpolation (LOPO pooled/cell experiments)

Baseline = plain LOPO pooled/cell (§3). Testbed = **F5** (hardest setup),
raw/all-antenna, 40 epochs.

| variant | median (in) | ≤0.5 in | ≤1 in | near / ext |
|---|---|---|---|---|
| baseline | 0.664 | 33% | 67% | 0.75 / 0.65 |
| **+ mixup** (α=0.4, ratio=1) | **0.572** | 39% | 76% | **0.61 / 0.56** |
| + position-disjoint val (frac=0.2) | 0.927 | 24% | 55% | 1.12 / 0.89 |
| + mixup **&** posval | 0.722 | 33% | 70% | 0.84 / 0.72 |
| + heatmap head (σ=0.6) | 0.895 | 15% | 58% | 1.42 / 0.85 |
| + heatmap **&** mixup | 0.865 | 15% | 58% | 1.50 / 0.84 |

**Exp 1 — mixup: helps, and helps the barrier most.** −0.09 in overall (~14%),
and the **near-insert cells improve more than exterior** (0.75→0.61 vs
0.65→0.56). Offline mixup appends synthetic training samples that are convex
blends of random training pairs with matching blended `(x, y)` targets
(`MIXUP_ALPHA` flag). Contrary to the over-smoothing worry, synthesizing
intermediate signal↔coordinate points *fills* the spatial gaps rather than
washing out the dielectric discontinuity — net-positive exactly where
interpolation was hardest.

**Exp 2 — position-disjoint validation: hurts, even with mixup.** Standalone,
holding 20% of the ~30 training positions out for best-network selection cost
more than it gained: 0.664 → 0.927. Combined with mixup to replenish the lost
data it recovers to 0.722 — better than posval alone, but still well below
**mixup alone (0.572)**. Conclusion: on a dataset this small, sacrificing
positions for model selection is a net negative regardless; **mixup alone is the
winner so far.**

**Exp 3 — heatmap output: hurts (centroid bias).** The softmax-over-anchors
head with centroid readout underperformed the plain xy head (0.895 vs 0.664),
and mixup didn't rescue it (0.865). Near-insert error nearly doubled (0.75 →
1.42): the centroid readout's softmax mass-leakage pulls predictions toward the
grid centre, penalising exactly the interior/insert positions. Tunable in
principle (sharper σ, finer anchors, temperature-scaled soft-argmax), but as a
first pass the structured head is a net negative.

### Verdict (interpolation-improvement experiments)

Of the three fixes tried on F5 pooled/cell, **only mixup helps** (0.664 → 0.572,
~14%, and it helps the glandular-barrier region most). Position-disjoint
validation and the heatmap head both *hurt* on this small dataset — the first
starves training of scarce positions, the second adds a center-pulling bias.
**Mixup on a plain (x,y) head is the keeper.** Natural next steps: apply mixup
to F4/June18 and to the LOSO models; optionally revisit the heatmap head with a
sharper soft-argmax if structured output is wanted later.

See `CHANGELOG.md` for the running log of what changed when.

## 5. Simulated 3D (x, y, z) localization

The SamMakin HFSS tumor sweep: one 10 mm lead tumor moved over **1074 positions**
on a **uniform 5 mm depth grid, 13 depths (z = −15…+45 mm)** — the off-grid z=3 mm
plane is excluded so depth spacing is uniform. `cnn_matlab/Imager_CNN_SimReg.m`
reuses the CNN with a Touchstone (.s4p) loader, **differential dS input**
(subtract each depth's own HFSS-batch empty baseline), an `fc(3)` head, and
**8-fold position cross-validation** (true per-position LOPO is infeasible).
Lateral and depth error reported separately.

| metric | CNN | centroid (chance) | k-NN floor |
|---|---|---|---|
| lateral xy (median) | **3.92 mm** (64% ≤5mm, 93% ≤10mm) | 36.5 mm | 3.3 mm |
| depth z (median)   | **2.09 mm** (82% ≤5mm) | 16.3 mm | ~2 mm |

**The CNN localizes a tumor in 3D to ~3.9 mm laterally / ~2.1 mm in depth** over
the full ±(15–45) mm depth span — far below the 10 mm grid.

**Depth accuracy varies smoothly with depth (leave-one-depth-out, `SIM_CV=depth`,
per-depth z-error):** ~1.2–1.5 mm through the interior (−5 to +20 mm), climbing
steadily at the deep end (25→30→40 mm = 2.3→2.8→3.2 mm). A gradual
range-resolution falloff for far tumors, *not* a cliff — a genuine depth effect
that persists on fully-trained interior depths. (An earlier z=3-included run read
0.8 mm at z=5 mm; that was the odd 3 mm plane acting as a 2 mm-away helper — on
the uniform grid z=5 is 1.5 mm, the honest value.)

**The "edges" are extrapolation, not hard depths.** In the earlier −5…+30 mm
dataset, the extreme depths −5 and +30 gave z ≈ 6–8 mm — but once the range was
extended to −15…+45 (giving them neighbors on both sides), **−5 dropped to ~1.2 mm
and +30 to ~2.8 mm**. The model just can't reach past its sampled depth range; the
extremes −15/+45 mm are the ~8–10 mm extrapolation limits. **Usable depth is
bounded by the depth *sampling range*, not the model** — and interior unseen
depths are predicted about as well as trained ones (8-fold ≈ depth-out in the
interior), proving a *continuous* learned depth mapping.

Depth is competitive with the lateral axis here:
with fine depth sampling and full-band frequency access it resolves to ~1–2 mm
through the bulk of the range. (Feasibility + a physics exploration of the sim —
`Simulation Data/SamMakin/sim_feasibility_check.py`, `sim_explore.py` — found the
signal is depth-robust, that low freq carries xy while high freq carries depth,
and that reflections alone suffice; only position varies, so localization is the
only learnable target.)

**Metal vs. dielectric (beet) tumor — localizes as well.** The same sweep with a
beet (dielectric) tumor instead of the lead one — ~81% of the metal signal
magnitude — run identically (`SIM_LABEL=beet`, single baseline, 1065 positions,
`Dense_Run_Bundle/ALL_RESULTS`): **xy 3.64 mm, z 2.07 mm**, statistically
identical to metal (3.92 / 2.09) with the same per-depth structure. In the
*noiseless* sim the ~19% weaker dielectric contrast costs nothing — the signal is
still far above the numerical floor and equally position-coherent, so
localization is unaffected. Realistic dielectric tumors are as localizable as
metal here. (Caveat: on real measured data a noise floor could change this — beet
sits closer to it; a sim↔measured check would tell.)

**CNN data-quantity threshold (why the single-layer LOO collapses).** 8-fold xy
error vs. number of depth planes included (metal; `SIM_DEPTHS`) — and the axis
that matters is **distinct positions**: the sim is noiseless with no repeat takes,
so each sample *is* a distinct location. 1 depth (82 distinct positions) 33 mm ≈
chance → 3 depths (245) 11 mm → 5 depths (410) 4.8 mm → plateau ~3.8 mm from 7
depths (570) on. So the conv net needs **~400–500 distinct labeled positions** to
localize; below ~250 it's poor, at ~82 it's dead. Distinct positions — not raw
sample count. That's why a single sim layer collapses (82 positions), and why the
measured empty CNN **LOPO** is stuck at 9.9 mm *despite* ~2,400 raw samples: those
are 16 repeat takes × 3 sessions of only ~50 distinct grid points (§3). The
training-free **k-NN** (fits nothing) is therefore the right probe of *signal*
interpolability, decoupled from the CNN's hunger for distinct positions. Figure:
`regression_deck/sim_depth_learning_curve.png`.
