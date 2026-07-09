# External dependencies & reproducibility

This repo is the **code + results + docs** for the localization study. Two
classes of things it needs live **outside** the repo and are referenced by
absolute path on Peter's machine. They are documented here so the provenance is
clear and so the paths can be repointed on another machine.

## 1. Raw measurement data (NOT in the repo)

The Hunter 4-port VNA sweeps (`baseline_T*.csv` + `RnCmPp_T*.csv`, one folder
per session) are large and live under the data tree, not here:

| Setup | Parent folder (holds per-session subfolders) | Sessions used |
|---|---|---|
| Empty (A3) | `…/Sam Antennas/MediumAntenna/Separated/June18` | 1530, 1547, 1611 (port-remap `2 1 4 3`) |
| F4 (A3) | `…/Sam Antennas/MediumAntenna/Separated/July03/A3_F4_SamMed` | all 4 (1623, 1642, 1707, 1726) |
| F5 (A3) | `…/Sam Antennas/MediumAntenna/Separated/July03/A3_F5_SamMed` | last 3 (1432, 1454, 1516) |

Full prefix: `C:\Users\peter\Desktop\EM Imaging\BreastPhantom\HunterVNA\DataMeasurements\`.
Point the scripts at these via `--setup` (Python) or `CNN_LOSO_PARENT` (MATLAB).

## 2. Shared code (from sibling projects, NOT vendored)

The scripts import a few modules that belong to other projects in the same
workspace. Changes to those belong to *their* projects, not this one, so they
are documented rather than copied in:

| Module | Location | Used by |
|---|---|---|
| `hunter_loader.py`, `physics_features*.py`, `data.py` | `…/Above 95 Percent/code/` | `run_mlp_loso.py`, `run_mlp_regloso.py` |
| `loadHunterVnaFolder.m` | `…/Imager Program/` | all `Imager_CNN_*.m` |
| Python venv | `…/Above 95 Percent/venv/` | all Python scripts |

If you move the repo, update the hard-coded paths near the top of
`run_mlp_regloso.py` (the `ABOVE95_CODE` insert) and the `LOADER_DIR` /
`ADJ_JSON` constants in the `.m` files.

## 3. Target-defining input (vendored snapshot)

`position_adjustments.json` — the photo-digitized true positions that define the
regression targets where the glandular insert blocked a corner — lives in yet
another project (`Research Paper/github_repo/detectable_change/A3_hunter/`).
Because it **defines the regression targets**, a snapshot is versioned here at
`reference/position_adjustments.snapshot.json` for reproducibility. The scripts
still read the live file by default; the snapshot is the record of what produced
a given result. If the live file changes, refresh the snapshot in the same
commit that re-runs affected results.

## Environment

- MATLAB R2025b (Deep Learning Toolbox), CUDA GPU (results run on an RTX 3070
  laptop GPU).
- Python via the Above-95 venv (numpy, scikit-learn, joblib).
