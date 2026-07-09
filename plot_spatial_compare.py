"""Side-by-side spatial per-position LOSO accuracy maps: CNN vs MLP.

For a given setup + session-set, draws a grid of maps (rows = antenna mode
all/pair/single, cols = CNN vs MLP) coloured by per-position accuracy across
LOSO folds. Positions the model gets wrong (low accuracy) show up red; correct
positions green. Lets you see WHERE each method fails -- e.g. whether errors
cluster over the glandular insert.

Reads results/{cnn,mlp}_loso_<setup>_<sessionset>_<mode>_ant<ports>.json.

Usage:
    python plot_spatial_compare.py                 # all setups/session-sets found
    python plot_spatial_compare.py A3_F5_SamMed all5
"""
from __future__ import annotations
import sys, json
from pathlib import Path
from collections import defaultdict
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize

RESULTS = Path(__file__).resolve().parent / "results"
MODES = [("all", "all 16"), ("pair", "pair 1&3"), ("single", "single S11")]


def load(method, setup, sset, mode):
    for f in RESULTS.glob(f"{method}_loso_{setup}_{sset}_{mode}_ant*.json"):
        return json.loads(f.read_text())
    return None


def per_pos_xy_acc(r):
    xs, ys, acc = [], [], []
    for e in r.get("perPosition", []):
        x, y, a = e.get("x"), e.get("y"), e.get("acc")
        if x is None or (isinstance(x, float) and np.isnan(x)):
            continue
        xs.append(x); ys.append(y); acc.append(a)
    return np.array(xs), np.array(ys), np.array(acc)


def discover():
    """Return sorted set of (setup, sessionSet) present in results/."""
    combos = set()
    for f in RESULTS.glob("*_loso_*.json"):
        try:
            r = json.loads(f.read_text())
        except Exception:
            continue
        sset = r.get("sessionSet") or f"{len(r.get('sessionNames', []))}sess"
        combos.add((r.get("setup", "?"), sset))
    return sorted(combos)


def draw(setup, sset):
    fig, axes = plt.subplots(len(MODES), 2, figsize=(11, 15),
                             constrained_layout=True)
    cmap = plt.get_cmap("RdYlGn"); norm = Normalize(0, 100)
    any_data = False
    for row, (mode, mode_lbl) in enumerate(MODES):
        for col, method in enumerate(("cnn", "mlp")):
            ax = axes[row, col]
            r = load(method, setup, sset, mode)
            if r is None:
                ax.set_axis_off(); ax.set_title(f"{method.upper()} {mode_lbl}\n(no data)"); continue
            any_data = True
            xs, ys, acc = per_pos_xy_acc(r)
            ax.scatter(xs, ys, c=acc, cmap=cmap, norm=norm, s=300,
                       edgecolors="black", linewidths=0.5, zorder=3)
            # annotate ONLY the positions the model gets wrong (acc < 100),
            # so the error clusters stand out instead of a wall of "100"s.
            for x, y, a in zip(xs, ys, acc):
                if a < 100:
                    ax.text(x, y, f"{int(round(a))}", ha="center", va="center",
                            fontsize=7, fontweight="bold", zorder=4,
                            color="black" if a > 25 else "white")
            for v in range(9):
                ax.axhline(v, color="grey", lw=0.4, alpha=0.5, zorder=1)
                ax.axvline(v, color="grey", lw=0.4, alpha=0.5, zorder=1)
            ax.set_xlim(0, 7); ax.set_ylim(7.5, 0); ax.set_aspect("equal")
            mean = float(np.mean(acc)) if len(acc) else 0.0
            nwrong = int(np.sum(acc < 100))
            ax.set_title(f"{method.upper()}  --  {mode_lbl}\n"
                         f"mean {mean:.1f}%   ({nwrong}/{len(acc)} pos <100%)",
                         fontsize=10, fontweight="bold")
            if row == len(MODES) - 1:
                ax.set_xlabel("X (in)")
            if col == 0:
                ax.set_ylabel("Y (in)")
    if not any_data:
        plt.close(fig); return None
    cbar = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap),
                        ax=axes, shrink=0.4, pad=0.02, location="right")
    cbar.set_label("per-position LOSO accuracy across folds (%)", fontweight="bold")
    fig.suptitle(f"{setup}   [{sset}]   --   per-position LOSO accuracy: CNN vs MLP\n"
                 f"(only sub-100% positions are labelled; larger insert -> bigger central error cluster)",
                 fontsize=12, fontweight="bold")
    out = RESULTS / f"spatial_compare_{setup}_{sset}.png"
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def main():
    if len(sys.argv) >= 3:
        combos = [(sys.argv[1], sys.argv[2])]
    else:
        combos = discover()
    for setup, sset in combos:
        out = draw(setup, sset)
        if out:
            print(f"saved {out}")


if __name__ == "__main__":
    main()
