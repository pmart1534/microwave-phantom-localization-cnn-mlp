"""Minimal-chip map: tone-count descent + magnitude-only, same heatmap format
as the break-descent maps.

Panels: Empty, F4 (the phantoms still unbroken at reduced hardware).
Rows: hardware x component (mag+phase vs magnitude-only).
Columns: 3 GHz anchor -> 0.25 -> 0.05 GHz -> 4 -> 3 -> 2 -> 1 frequency points
(native grid 10 MHz; "1 pt" = a single CW tone). Band centers follow each
phantom's chosen center (empty ~1.875 GHz original slot, F4 ~3.0 GHz).

Outputs: results/minimal_chip_map.png + results/minimal_chip.md
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

PHANTOMS = {  # name -> (json prefix, band list in column order)
    "Empty (center ~1.875 GHz)": ("June18_remap",
        ["1-4", "2-2.25", "1.85-1.9", "1.86-1.89", "1.86-1.88", "1.87-1.88", "1.87-1.87"]),
    "F4 (center ~3.0 GHz)": ("A3_F4_SamMed_all4",
        ["1-4", "3-3.25", "2.975-3.025", "2.98-3.01", "2.99-3.01", "2.99-3", "3-3"]),
}
COL_W = ["3 GHz", "0.25 GHz", "0.05 GHz", "4 pts", "3 pts", "2 pts", "1 pt"]
ROWS = [  # label -> (hw tag, input tag)
    ("1 ant (S11), mag+phase", "single_ant1", "raw"),
    ("1 ant (S11), mag only", "single_ant1", "rawmag"),
    ("2 ant (1&3) refl, mag+phase", "refl_ant1-3", "raw"),
    ("2 ant (1&3) refl, mag only", "refl_ant1-3", "rawmag"),
]
CMAP = LinearSegmentedColormap.from_list(
    "acc", ["#8E1010", "#BE0000", "#E8A33D", "#F5E6A3", "#7BA05B", "#3E7A3E"])


def cell(pre, itag, hwtag, band):
    f = RESULTS / f"cnn_loso_{pre}_{itag}_{hwtag}_band{band}.json"
    if not f.exists():
        return None
    r = json.loads(f.read_text())
    return (r["losoPosMean"], r["losoPosStd"])


def main():
    lines = ["# Minimal-chip map: tone descent + magnitude-only",
             "",
             "CNN, LOSO. mag+phase = standard raw input; mag only = |S| rows only",
             "(scalar power-detector measurement). Native grid 10 MHz: 1 pt = single",
             "CW tone. Missing cells: not run (or skipped after a <50% break).", ""]
    fig, axes = plt.subplots(1, 2, figsize=(12.4, 4.0))
    for ax, (ph, (pre, bands)) in zip(axes, PHANTOMS.items()):
        grid = np.full((len(ROWS), len(bands)), np.nan)
        lines.append(f"## {ph}")
        lines.append("")
        lines.append("| config | " + " | ".join(f"{b} ({w})" for b, w in zip(bands, COL_W)) + " |")
        lines.append("|---" * (len(bands) + 1) + "|")
        for i, (label, hwtag, itag) in enumerate(ROWS):
            cells = []
            for j, b in enumerate(bands):
                v = cell(pre, itag, hwtag, b)
                if v is None:
                    cells.append("-")
                else:
                    grid[i, j] = v[0]
                    cells.append(f"{v[0]:.1f}±{v[1]:.1f}")
            lines.append(f"| {label} | " + " | ".join(cells) + " |")
        lines.append("")
        for i in range(len(ROWS)):
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
        ax.set_xticklabels([f"{b}\n({w})" for b, w in zip(bands, COL_W)], fontsize=6.8)
        ax.set_yticks(range(len(ROWS)))
        ax.set_yticklabels([r[0] for r in ROWS] if ax is axes[0] else [""] * len(ROWS), fontsize=8.5)
    fig.suptitle("Tone-count descent and magnitude-only input - black box = below 50%, — = not run",
                 fontsize=11.5, y=0.99)
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(RESULTS / "minimal_chip_map.png", dpi=180)
    (RESULTS / "minimal_chip.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
