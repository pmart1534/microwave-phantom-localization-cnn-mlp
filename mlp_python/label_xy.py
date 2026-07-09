"""Canonical RnCmPp label -> (x, y) inches for the Hunter 6x6 phantom grid.

Single source of truth for REGRESSION targets, shared by run_mlp_regloso.py
and mirrored exactly by ../cnn_matlab/Imager_CNN_RegLOSO.m.  Matches
gridToPhysical in AntennaImaging_DataRecording.m / AntennaImaging_ML.m,
xyCoords in loadHunterVnaFolder.m, and rcp_to_xy in
detectable_change/A3_hunter/detectable_difference_hunter.py:

    cell centre : x = (col - 0.5) * 1.0 in     (origin top-left, y down)
    sub-position: +/- 0.375 in from centre     (0.5 half-cell - 0.125 half-divider)
      P1 = TL (-,-)   P2 = TR (+,-)   P3 = BR (+,+)   P4 = BL (-,+)

NOTE: hunter_loader._rcp_to_xy is a DIFFERENT (approximate) mapping -- pitch
1.25 in and +/-0.25 offsets -- kept as-is for the classification plot
pipelines.  Do NOT use it for regression targets.

Where the glandular insert blocked the exact corner spot, the true measured
position was digitized from calibrated phantom photos (adjust_positions.py)
into position_adjustments.json.  Pass adjust_key ('A3_Empty' | 'A3_F4' |
'A3_F5') to apply those overrides; A3_Empty has none.
"""
from __future__ import annotations
import json, re
from pathlib import Path
import numpy as np

CELL_IN = 1.0
DIVIDER_IN = 0.25
SPOFF = CELL_IN / 2.0 - DIVIDER_IN / 2.0        # 0.375 in
SUBOFF = {1: (-SPOFF, -SPOFF), 2: (+SPOFF, -SPOFF),
          3: (+SPOFF, +SPOFF), 4: (-SPOFF, +SPOFF)}

ADJ_JSON = Path(r"C:\Users\peter\Desktop\EM Imaging\Research Paper\github_repo"
                r"\detectable_change\A3_hunter\position_adjustments.json")

_RCP = re.compile(r"R(\d+)C(\d+)P(\d+)", re.IGNORECASE)


def rcp_to_xy(r: int, c: int, p: int) -> tuple[float, float]:
    ox, oy = SUBOFF[p]
    return (c - 0.5) * CELL_IN + ox, (r - 0.5) * CELL_IN + oy


def label_to_xy(label: str) -> tuple[float, float]:
    m = _RCP.match(str(label))
    if not m:
        raise ValueError(f"bad position label {label!r}")
    return rcp_to_xy(int(m.group(1)), int(m.group(2)), int(m.group(3)))


def load_adjustments(adjust_key: str | None) -> dict[str, tuple[float, float]]:
    """{label: (x, y)} photo-digitized overrides for one phantom setup."""
    if not adjust_key or str(adjust_key).lower() == "none":
        return {}
    data = json.loads(ADJ_JSON.read_text())
    if adjust_key not in data:
        raise KeyError(f"{adjust_key!r} not in {ADJ_JSON.name} "
                       f"(available: {sorted(data)})")
    return {k: (float(v[0]), float(v[1])) for k, v in data[adjust_key].items()}


def targets_for_labels(labels, adjust_key: str | None = None) -> np.ndarray:
    """labels -> (N, 2) float64 inches, with per-setup photo overrides applied."""
    adj = load_adjustments(adjust_key)
    out = np.empty((len(labels), 2), dtype=np.float64)
    for i, lbl in enumerate(labels):
        out[i] = adj.get(str(lbl), label_to_xy(lbl))
    return out
