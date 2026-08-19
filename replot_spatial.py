"""Regenerate the per-position spatial accuracy map from a result JSON with
the improved style: red (0%) -> yellow -> green (100%) colormap, markers
sized from the grid spacing so neighbours never touch, and labels only on
imperfect positions, offset beside the dot.

Usage (any shell, from the "CNN vs MLP" folder):
    python replot_spatial.py results/cnn_loso_Aug18_metal_raw_all_ant1-2-3-4.json [...]
Overwrites the matching *_spatial.png next to each JSON.
"""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

ACC_CMAP = LinearSegmentedColormap.from_list(
    "acc", ["#B81C1C", "#E85C24", "#FABF4A", "#8CC266", "#388C3D"])


def replot(json_path: Path):
    r = json.loads(json_path.read_text())
    pos = r["perPosition"]
    xs = np.array([p["x"] for p in pos], float)
    ys = np.array([p["y"] for p in pos], float)
    accs = np.array([p["acc"] for p in pos], float)

    d = np.hypot(xs[:, None] - xs[None, :], ys[:, None] - ys[None, :])
    d[d == 0] = np.inf
    gap = d.min()                       # nearest-neighbour spacing (inches)

    fig, ax = plt.subplots(figsize=(6.6, 6.2))
    span = max(np.ptp(xs), np.ptp(ys)) + gap
    mk_pt = 0.80 * gap / span * 5.4 * 72   # marker diameter in points
    sc = ax.scatter(xs, ys, s=mk_pt**2, c=accs, cmap=ACC_CMAP,
                    vmin=0, vmax=100, edgecolors="white", linewidths=0.9, zorder=3)
    x_mid = (xs.min() + xs.max()) / 2
    for x, y, a in zip(xs, ys, accs):
        if a < 99.5:
            # diagonal offset, flipped away from the nearest plot edge
            right = x <= x_mid
            ax.annotate(f"{a:.0f}%", (x, y),
                        xytext=(x + (0.35 if right else -0.35) * gap, y - 0.55 * gap),
                        fontsize=10, fontweight="bold", color="#262626",
                        ha="left" if right else "right", va="bottom", zorder=5,
                        bbox=dict(boxstyle="round,pad=0.15", fc="white",
                                  ec="#BBBBBB", lw=0.6, alpha=0.85))
    cb = fig.colorbar(sc, ax=ax, fraction=0.046, pad=0.03)
    cb.set_label("LOSO accuracy (%)")
    ax.invert_yaxis()
    ax.set_aspect("equal")
    ax.set_facecolor("#FBFBFB")
    ax.grid(alpha=0.25, zorder=0)
    ax.set_xlim(xs.min() - gap, xs.max() + gap)
    ax.set_ylim(ys.max() + gap, ys.min() - gap)
    ax.set_xlabel("X (inches)")
    ax.set_ylabel("Y (inches)")
    ax.set_title(f"Per-position LOSO accuracy  -  mean {accs.mean():.1f}%",
                 fontsize=12.5, fontweight="bold")
    out = json_path.with_name(json_path.stem + "_spatial.png")
    fig.tight_layout()
    fig.savefig(out, dpi=180)
    plt.close(fig)
    print("wrote", out)


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        replot(Path(arg))
