# CNN vs MLP — localization on Hunter 4-port A3 data

A like-for-like comparison of the two localization methods used in this
project, on the **same** Hunter 4-port VNA sessions of the **A3 phantom**,
under the **same** honest cross-validation protocols, with the **same**
antenna-subset options. It covers **position classification** and, as of
July 2026, continuous **`(x, y)` regression** and a **spatial-interpolation**
(leave-one-position-out) study.

> **Documentation:** methodology in [`docs/METHODS.md`](docs/METHODS.md),
> all result tables + findings in [`docs/RESULTS.md`](docs/RESULTS.md), external
> data/code paths in [`docs/DEPENDENCIES.md`](docs/DEPENDENCIES.md), running
> change log in [`docs/CHANGELOG.md`](docs/CHANGELOG.md). The sections below
> document the original **classification** study; regression and LOPO are in the
> docs.

## Map

| Path | What |
|---|---|
| `cnn_matlab/` | MATLAB CNN — `Imager_CNN_LOSO.m` (classify), `Imager_CNN_RegLOSO.m` (regression), `Imager_CNN_RegLOPO.m` (leave-one-position-out) |
| `mlp_python/` | Python MLP — `run_mlp_loso.py` (classify), `run_mlp_regloso.py` (regression), `label_xy.py` (grid→xy targets) |
| `results/` | all `*.json` results + `*.png` figures (LOSO `*_loso_*`, regression `*_regloso_*`, LOPO `*_reglopo_<mode>_<unit>_*` — never collide) |
| `docs/` | methods, results, dependencies, changelog |
| `reference/` | versioned snapshot of the target-defining `position_adjustments.json` |
| `presentation/` | slide decks + figures |

---

| | CNN (this project's original method) | MLP (the "Above 95 Percent" method) |
|---|---|---|
| Language | MATLAB (`cnn_matlab/`) | Python (`mlp_python/`) |
| Input | raw `[rows × freq]` S-parameter image | ~physics feature vector |
| Normalization | `imageInputLayer` z-score | per-session z-score ("KEY" trick) + scaler |
| Model | 2×conv2d → FC → softmax | 3-seed `MLP(256,128)` ensemble [+ LogReg] |
| Metric | per-position vote accuracy, LOSO | per-position vote accuracy, LOSO |

Each method keeps its **native** front-end (the CNN eats the raw image, the
MLP eats hand-built physics features) — that is deliberate. We are comparing
the *methods as actually used*, not swapping their inputs. Both are held to
the identical evaluation: N-fold leave-one-session-out, per-position majority
vote, on the positions common to every session.

## Why LOSO instead of the original 75/25 split

The original `Imager_ML_MultiSession.m` uses a 75/25 stratified split. That
mixes trials from the *same* session into both train and test, so the model
can exploit session-specific drift (VNA warm-up, cable position, temperature)
as a shortcut — inflating the number. **LOSO** trains on whole sessions and
tests on a held-out session it has never seen, so the reported accuracy is an
honest estimate of how the system generalizes to a *new* measurement session.
`cnn_matlab/Imager_CNN_LOSO.m` is the original CNN method with **only** that
change: 75/25 split → leave-one-session-out.

## Datasets (Hunter 4-port, A3 phantom, 3 sessions each)

Same setups as the original 2-port A2 study, re-recorded on the 4-port Hunter:

| Setup | Status | Location |
|---|---|---|
| Empty | ✅ have it | `BreastPhantom/HunterVNA/DataMeasurements/Sam Antennas/MediumAntenna/Separated/June18` |
| F4 (fishing weight) | ⏳ recording | (point the scripts at its parent folder when ready) |
| F5 (fishing weight) | ⏳ recording | (point the scripts at its parent folder when ready) |

Each setup is a **parent folder** containing one subfolder per session
(a Hunter batch-sweep: `baseline_T*.csv` + `RnCmPp_T*.csv`).

## Antenna subsets (from the same 4-port data)

Both programs offer identical antenna options, selecting S-parameters out of
the full 4-port measurement:

| Option | Antennas | S-parameters | CNN rows |
|---|---|---|---|
| **all** | 4 | all 16 | 32 |
| **pair** e.g. 1 & 3 | 2 | S11, S13, S31, S33 | 8 |
| **pair** e.g. 2 & 4 | 2 | S22, S24, S42, S44 | 8 |
| **single** e.g. 1 | 1 | S11 only | 2 |

Use opposite-side pairs (1 & 3 or 2 & 4) for the most informative 2-antenna
test — in the "Separated" configs those antennas sit across the phantom.

## How to run

### CNN (MATLAB)
Open `cnn_matlab/Imager_CNN_LOSO.m` in MATLAB (R2025b) and run it. It will:
1. ask you to pick the **parent folder** for a setup (holds the session subfolders),
2. ask the **antenna subset** (all / pair / single, and which antennas),
3. run N-fold LOSO and save `results/cnn_loso_<tag>.json` + bar/spatial PNGs.

### MLP (Python)
From `mlp_python/`, using the bundled Above-95 venv:
```
..\..\"Above 95 Percent"\venv\Scripts\python.exe run_mlp_loso.py ^
    --setup "C:\...\MediumAntenna\Separated\June18" ^
    --antenna all
```
`--antenna` accepts: `all`, `pair:1,3`, `pair:2,4`, `single:1` (…`single:4`).
Saves `results/mlp_loso_<tag>.json`.

## Results

Both write JSON with the same keys (`losoPosMean`, `losoPosStd`,
`foldPosAcc`, `perPosition`, …) into `results/`, so a given
setup + antenna choice yields one `cnn_loso_*.json` and one `mlp_loso_*.json`
you can lay side by side. Run `python make_comparison.py` to regenerate
`results/comparison_table.md` / `.csv`.

### Empty setup (Sam Med, June18, 3 sessions, 51-way, chance 2.0%)

CNN = full 100-epoch runs in MATLAB; MLP = the Above-95 pipeline. Per-position
vote accuracy, leave-one-session-out:

| antenna | CNN LOSO | MLP LOSO |
|---|---|---|
| all 16 (4 antennas) | **100.0 ± 0.0** | 99.3 ± 0.9 |
| pair 1 & 3 (S11,S13,S31,S33) | 97.4 ± 2.3 | 99.3 ± 0.9 |
| single 1 (S11 only) | 98.0 ± 2.0 | 100.0 ± 0.0 |

**Validation:** the MLP `all` result (99.3 ± 0.9, folds 100/98.0/100) is an
exact match to the previously published
`Above 95 Percent/results/hunter_sam_med_sep_june18/results.json`, confirming
the MLP driver reproduces the established pipeline. The empty/fishing-weight
data is highly separable, so every configuration sits near ceiling.

### F4 and F5 (the informative setups)  — July03, per-position vote LOSO

F4 = 4 full sessions (partial session `1703` excluded). F5 = 5 sessions, also
run as latter-3 (dropping the 2 noisy early sessions 1356/1417).

| setup | sessions | antenna | CNN | MLP |
|---|---|---|---|---|
| F4 | all-4 | all 16 | 96.8 ± 2.5 | 98.1 ± 1.1 |
| F4 | all-4 | pair 1&3 | 98.1 ± 2.5 | 94.9 ± 3.6 |
| F4 | all-4 | single S11 | 82.1 ± **25.9** | 87.8 ± 7.8 |
| F5 | all-5 | all 16 | 100.0 ± 0.0 | 100.0 ± 0.0 |
| F5 | all-5 | pair 1&3 | 95.2 ± 1.7 | 92.7 ± 3.1 |
| F5 | all-5 | single S11 | 70.9 ± **27.2** | 66.1 ± 11.1 |
| F5 | latter-3 | all 16 | 99.0 ± 1.7 | 99.0 ± 1.4 |
| F5 | latter-3 | pair 1&3 | 94.9 ± 1.7 | 85.9 ± 5.2 |
| F5 | latter-3 | single S11 | 58.6 ± **40.4** | 68.7 ± 5.2 |

**Headline findings**
1. **Full 16-S-param array: CNN ≈ MLP, both near ceiling** on every setup (97–100%). With the whole array, session drift is a non-issue for either method.
2. **Two antennas (pair 1&3): roughly tied**, CNN a touch ahead on F4/F5. Both stay 93–98%. Halving the antennas costs little.
3. **One antenna (S11 only) is where they diverge — in *variance*, not mean.** Means are comparable (~60–88%), but the CNN suffers **catastrophic single-fold collapses** on the hard/noisy held-out session (folds hitting 12%, 24%, 43% ≈ chance), giving huge spread (±26–40). The MLP's per-session z-score keeps it far steadier (±5–11). So under aggressive antenna reduction + session drift, **the MLP is the more reliable method even when its average isn't higher.**
4. **Target matters:** F4 single-antenna (~82–88%) is much easier than F5 single-antenna (~58–71%) — F5's glandular structure is harder to localize from one reflection coefficient.
5. The 2 noisy early F5 sessions *help* the MLP at high antenna counts (more data, normalized) but are exactly the folds that make single-antenna models collapse.

The full machine-readable table is `results/comparison_table.md` / `.csv`
(regenerate with `python make_comparison.py`).

### Spatial error maps (where each method fails)

`python plot_spatial_compare.py` draws per-position LOSO accuracy on the grid
(green = always right, red = always wrong), CNN vs MLP, for each antenna mode.
Saved as `results/spatial_compare_<setup>_<sessionset>.png`. Only sub-100%
positions are labelled so error clusters stand out.

**Confirms the glandular-insert hypothesis.** With a single antenna (S11),
the wrong positions are not random — they form a **compact cluster in the
centre of the phantom**, right where the glandular insert sits, while edge and
corner positions stay at 100%. And the cluster scales with insert size:

- **F5 (larger insert):** deep central errors (0–40%), tightly clustered;
  single-antenna mean 66–71%.
- **F4 (smaller insert):** shallower errors (mostly 75% = wrong in 1 of 4
  folds), more diffuse; single-antenna mean 82–88%.

Physically sensible: the insert perturbs the local dielectric, and with only
one reflection coefficient there isn't enough spatial diversity to resolve a
marble *inside* that perturbed region. Adding antennas (pair, then all 16)
progressively fills in the central cluster until it disappears.

Caveat: the CNN (MATLAB loader) and MLP (Python loader) assign slightly
different absolute X/Y inch coordinates, so compare each method's cluster to
its *own* grid, not pixel-to-pixel across the two columns. The qualitative
pattern (central cluster, shrinking with more antennas / smaller insert) is
identical in both.

### Known difference in the front-ends (by design)

Each method uses its **native** loader, which includes the frequency grid:
- **CNN** reads the raw Hunter CSV at its native **791 points, 0.1–8 GHz**.
- **MLP** (`hunter_loader.py`) **resamples to the legacy 201-point grid**.

This is inherent to "same data, native inputs" — both have access to the same
measurement, each processes it its own way. If you ever want to remove even
this difference, resample the CNN input to 201 points (or the MLP to 791).

## Notes / honesty

- **No leakage in CNN LOSO.** The held-out session is never used as validation
  data during training (the original 75/25 code passed the test set as
  validation; LOSO training here does not).
- **Same positions.** Both restrict to the positions present in *every*
  session so the label set and chance level match across folds and methods.
- **Shared data path.** The CNN reuses `Imager Program/loadHunterVnaFolder.m`;
  the MLP reuses `Above 95 Percent/code/hunter_loader.py`. Antenna row-subset
  mappings are defined consistently in both (S_ij where both ports are selected).
