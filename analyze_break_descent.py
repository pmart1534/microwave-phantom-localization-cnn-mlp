"""Hardware x bandwidth break-descent map.

Reads the adaptive descent results (cnn_matlab/break_descent.sh): four
hardware levels x seven descending bands x three phantoms, where a phantom
stops descending at a hardware level once it scores <50% (BROKEN).

Outputs:
  results/break_descent.md          full grid + per-phantom break boundaries
  results/break_descent_map.png     3-panel heatmap (phantom x hardware x band)
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

PHANTOMS = {  # display name -> json filename prefix
    "Empty": "June18_remap",
    "F4": "A3_F4_SamMed_all4",
    "F5": "A3_F5_SamMed_last3",
}
HW = [  # display label -> json tag
    ("16 S-params (full)", "all_ant1-2-3-4"),
    ("4 ant, refl only", "refl_ant1-2-3-4"),
    ("2 ant (1&3), full S", "pair_ant1-3"),
    ("2 ant (1&3), refl only", "refl_ant1-3"),
    ("1 ant (S11 only)", "single_ant1"),
]
BANDS = ["1-4", "2-4", "1.5-2.5", "1.5-2", "2-2.25", "1.825-1.925", "1.85-1.9"]
BAND_W = ["3", "2", "1", "0.5", "0.25", "0.1", "0.05"]

CMAP = LinearSegmentedColormap.from_list(
    "acc", ["#8E1010", "#BE0000", "#E8A33D", "#F5E6A3", "#7BA05B", "#3E7A3E"])


def load():
    """-> {phantom: {hw_tag: {band: (mean, sd) or None}}}"""
    out = {}
    for ph, pre in PHANTOMS.items():
        out[ph] = {}
        for _, tag in HW:
            row = {}
            for b in BANDS:
                f = RESULTS / f"cnn_loso_{pre}_raw_{tag}_band{b}.json"
                if f.exists():
                    r = json.loads(f.read_text())
                    row[b] = (r["losoPosMean"], r["losoPosStd"])
                else:
                    row[b] = None
            out[ph][tag] = row
    return out


def break_boundary(row):
    """First band (in descent order) with mean <50, else None."""
    for b in BANDS:
        v = row[b]
        if v is not None and v[0] < 50:
            return b
    return None


def main():
    data = load()
    lines = ["# Hardware x bandwidth break-descent map",
             "",
             "CNN, raw input, LOSO per-position vote. Bands descend in width at the",
             "best placement per width; a phantom that scores <50% (BROKEN) stops",
             "descending at that hardware level. Missing cells = skipped after break.",
             ""]
    fig, axes = plt.subplots(1, 3, figsize=(15.5, 4.6))
    for ax, (ph, _) in zip(axes, PHANTOMS.items()):
        grid = np.full((len(HW), len(BANDS)), np.nan)
        lines.append(f"## {ph}")
        lines.append("")
        lines.append("| hardware | " + " | ".join(f"{b} ({w}G)" for b, w in zip(BANDS, BAND_W)) + " | breaks at |")
        lines.append("|---" * (len(BANDS) + 2) + "|")
        for i, (label, tag) in enumerate(HW):
            row = data[ph][tag]
            cells = []
            for j, b in enumerate(BANDS):
                v = row[b]
                if v is None:
                    cells.append("skip")
                else:
                    grid[i, j] = v[0]
                    cells.append(f"{v[0]:.1f}±{v[1]:.1f}")
            bb = break_boundary(row)
            lines.append(f"| {label} | " + " | ".join(cells) + f" | {bb + ' GHz' if bb else 'never'} |")
        lines.append("")
        im = ax.imshow(grid, cmap=CMAP, vmin=20, vmax=100, aspect="auto")
        for i in range(len(HW)):
            for j in range(len(BANDS)):
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
        ax.set_title(ph, fontsize=12.5, fontweight="bold")
        ax.set_xticks(range(len(BANDS)))
        ax.set_xticklabels([f"{b}\n({w} GHz)" for b, w in zip(BANDS, BAND_W)], fontsize=7.5)
        ax.set_yticks(range(len(HW)))
        ax.set_yticklabels([h[0] for h in HW] if ax is axes[0] else [""] * len(HW), fontsize=9)
    fig.suptitle("LOSO accuracy (%) across hardware reduction x band narrowing — black box = BROKEN (<50%), — = skipped after break",
                 fontsize=11.5, y=0.99)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(RESULTS / "break_descent_map.png", dpi=180)
    (RESULTS / "break_descent.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
