"""Hardware x bandwidth break map, v2: per-phantom BEST-CENTER band ladders.

Same layout as analyze_break_descent.py, but each phantom's band columns
converge on its own best frequency (empty -> 2.0 GHz, F4 -> 3.0, F5 -> 2.25),
so panel column labels differ per phantom.

Outputs:
  results/break_descent_best.md
  results/break_descent_map_best.png
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

RESULTS = Path(__file__).resolve().parent / "results"

PHANTOMS = {  # name -> (json prefix, best center label, band ladder)
    # Empty keeps its ORIGINAL ~1.875 GHz narrow bands: the full-array placement
    # scan was saturated (99-100 everywhere) so its "best 2.0" pick was noise,
    # and at reduced hardware the original slot measurably wins (76/75 vs 71/59).
    "Empty (best ~1.875 GHz)": ("June18_remap",
        ["1-4", "2-4", "1.5-2.5", "1.5-2", "2-2.25", "1.825-1.925", "1.85-1.9"]),
    "F4 (best ~3.0 GHz)": ("A3_F4_SamMed_all4",
        ["1-4", "2-4", "2.5-3.5", "2.5-3", "3-3.25", "2.95-3.05", "2.975-3.025"]),
    "F5 (best ~2.25 GHz)": ("A3_F5_SamMed_last3",
        ["1-4", "2-4", "2-3", "2-2.5", "2-2.25", "2.2-2.3", "2.225-2.275"]),
}
BAND_W = ["3", "2", "1", "0.5", "0.25", "0.1", "0.05"]
HW = [
    ("16 S-params (full)", "all_ant1-2-3-4"),
    ("4 ant, refl only", "refl_ant1-2-3-4"),
    ("2 ant (1&3), full S", "pair_ant1-3"),
    ("2 ant (1&3), refl only", "refl_ant1-3"),
    ("1 ant (S11 only)", "single_ant1"),
]
CMAP = LinearSegmentedColormap.from_list(
    "acc", ["#8E1010", "#BE0000", "#E8A33D", "#F5E6A3", "#7BA05B", "#3E7A3E"])


def cell(pre, tag, band):
    f = RESULTS / f"cnn_loso_{pre}_raw_{tag}_band{band}.json"
    if not f.exists():
        return None
    r = json.loads(f.read_text())
    return (r["losoPosMean"], r["losoPosStd"])


def main():
    lines = ["# Break map v2: per-phantom best-center band ladders",
             "",
             "CNN, raw, LOSO. Each phantom's bands converge on ITS OWN best frequency",
             "(from the 0.25/0.1 GHz placement scans). A phantom scoring <50% (BROKEN)",
             "stops descending at that hardware level; missing cells were skipped.",
             ""]
    fig, axes = plt.subplots(1, 3, figsize=(15.5, 4.6))
    for ax, (ph, (pre, bands)) in zip(axes, PHANTOMS.items()):
        grid = np.full((len(HW), len(bands)), np.nan)
        lines.append(f"## {ph}")
        lines.append("")
        lines.append("| hardware | " + " | ".join(f"{b} ({w}G)" for b, w in zip(bands, BAND_W)) + " | breaks at |")
        lines.append("|---" * (len(bands) + 2) + "|")
        for i, (label, tag) in enumerate(HW):
            cells, bb = [], None
            broken = False
            for j, b in enumerate(bands):
                v = None if broken else cell(pre, tag, b)
                if v is None:
                    cells.append("skip")
                else:
                    grid[i, j] = v[0]
                    cells.append(f"{v[0]:.1f}±{v[1]:.1f}")
                    if v[0] < 50 and bb is None:
                        bb, broken = b, True
            lines.append(f"| {label} | " + " | ".join(cells) + f" | {bb + ' GHz' if bb else 'never'} |")
        lines.append("")
        for i in range(len(HW)):
            for j in range(len(bands)):
                v = grid[i, j]
                if np.isnan(v):
                    ax.text(j, i, "—", ha="center", va="center", fontsize=9, color="#999")
                else:
                    broken = v < 50
                    ax.text(j, i, f"{v:.0f}", ha="center", va="center", fontsize=9.5,
                            fontweight="bold" if broken else "normal",
                            color="white" if v < 68 else "#222")
                    if broken:
                        ax.add_patch(plt.Rectangle((j - .5, i - .5), 1, 1, fill=False,
                                                   edgecolor="black", lw=2.2))
        ax.imshow(grid, cmap=CMAP, vmin=20, vmax=100, aspect="auto")
        ax.set_title(ph, fontsize=12, fontweight="bold")
        ax.set_xticks(range(len(bands)))
        ax.set_xticklabels([f"{b}\n({w} GHz)" for b, w in zip(bands, BAND_W)], fontsize=7)
        ax.set_yticks(range(len(HW)))
        ax.set_yticklabels([h[0] for h in HW] if ax is axes[0] else [""] * len(HW), fontsize=9)
    fig.suptitle("Break map v2 - each phantom's bands converge on ITS OWN best frequency. "
                 "Black box = BROKEN (<50%), — = skipped after break",
                 fontsize=11.5, y=0.99)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(RESULTS / "break_descent_map_best.png", dpi=180)
    (RESULTS / "break_descent_best.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
