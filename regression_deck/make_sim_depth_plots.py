"""Per-depth predicted-vs-actual plots for the sim 3D localization.

For a given depth plane, show the xy grid, the true tumor positions (circles),
the model's predicted positions (diamonds), and an arrow for each. Uses the
8-fold result (every position predicted once, out-of-fold). Predicted markers
are colored by depth error |dz| so one plot shows both lateral (arrows) and
depth (color) accuracy for that plane.

Usage:
    python make_sim_depth_plots.py <8fold_result.json> <outdir> z1 z2 ...
"""
import sys, json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

C_TRUE = "#1f77b4"; C_EDGE = "#d62728"; C_ARROW = "#9aa0a6"
CMAP = "viridis"


def plot_depth(pp, zlevel, gx, gy, out, maxn=None):
    full = [p for p in pp if round(p["z"]) == zlevel]
    if not full:
        print(f"  z={zlevel}: no positions"); return
    fx = np.array([p["x"] for p in full]); fy = np.array([p["y"] for p in full])
    # grid spacing + set of positions actually MEASURED at this depth
    dx = int(np.median(np.diff(gx))); dy = int(np.median(np.diff(gy)))
    present = set(zip(np.round(fx).astype(int), np.round(fy).astype(int)))
    def _edge(ax_, ay_):
        # exterior = missing ANY of its 4 orthogonal neighbors in the measured set
        out = np.zeros(len(ax_), bool)
        for i in range(len(ax_)):
            xi, yi = int(round(ax_[i])), int(round(ay_[i]))
            neigh = [(xi + dx, yi), (xi - dx, yi), (xi, yi + dy), (xi, yi - dy)]
            out[i] = not all(nb in present for nb in neigh)
        return out
    # edge/interior stats computed on ALL positions at this depth (representative)
    fxy = np.hypot(np.array([p["predX"] for p in full]) - fx,
                   np.array([p["predY"] for p in full]) - fy)
    fe = _edge(fx, fy)
    mi = np.median(fxy[~fe]) if (~fe).any() else np.nan
    me = np.median(fxy[fe]) if fe.any() else np.nan
    mdz = np.median([abs(p["predZ"] - p["z"]) for p in full])
    nfull = len(full)
    # subsample for PLOTTING only (stats above stay on the full set)
    sub = full
    if maxn and len(full) > maxn:
        order = np.lexsort((fy, fx))
        idx = order[np.linspace(0, len(order) - 1, maxn).round().astype(int)]
        sub = [full[i] for i in sorted(set(idx))]
    tx = np.array([p["x"] for p in sub]); ty = np.array([p["y"] for p in sub])
    px = np.array([p["predX"] for p in sub]); py = np.array([p["predY"] for p in sub])
    dz = np.array([abs(p["predZ"] - p["z"]) for p in sub])
    xy_err = np.hypot(px - tx, py - ty)
    edge = _edge(tx, ty)

    fig, ax = plt.subplots(figsize=(6.6, 6.0))
    for xv in gx: ax.axvline(xv, color="grey", lw=0.3, alpha=0.35, zorder=0)
    for yv in gy: ax.axhline(yv, color="grey", lw=0.3, alpha=0.35, zorder=0)
    # arrows true -> predicted
    for i in range(len(tx)):
        ax.annotate("", xy=(px[i], py[i]), xytext=(tx[i], ty[i]),
                    arrowprops=dict(arrowstyle="->", color=C_ARROW, lw=1.2, alpha=0.9), zorder=2)
    # true positions: interior (blue) vs outer-edge (red ring)
    ax.scatter(tx[~edge], ty[~edge], s=95, facecolors="none", edgecolors=C_TRUE,
               linewidths=1.8, zorder=3)
    ax.scatter(tx[edge], ty[edge], s=110, facecolors="none", edgecolors=C_EDGE,
               linewidths=2.2, zorder=3)
    # predicted positions, colored by depth error
    sc = ax.scatter(px, py, s=55, c=dz, cmap=CMAP, vmin=0, vmax=max(6, np.percentile(dz, 90)),
                    marker="D", edgecolors="k", linewidths=0.4, zorder=4)
    cb = fig.colorbar(sc, ax=ax, shrink=0.8, pad=0.02)
    cb.set_label("depth error |dz| (mm)")

    ax.set_aspect("equal"); ax.set_xlabel("X (mm)"); ax.set_ylabel("Y (mm)")
    ax.set_xlim(min(gx) - 8, max(gx) + 8); ax.set_ylim(min(gy) - 8, max(gy) + 8)
    shown = f", showing {len(sub)}" if (maxn and len(sub) < nfull) else ""
    ax.set_title(f"Sim localization — depth z = {zlevel:+d} mm  (n={nfull}{shown})\n"
                 f"lateral: interior {mi:.1f} / edge {me:.1f} mm   ·   depth {mdz:.1f} mm",
                 fontsize=11, fontweight="bold")
    ax.legend(handles=[
        Line2D([0], [0], marker="o", color="none", markeredgecolor=C_TRUE,
               markersize=10, markeredgewidth=1.8, label="true (interior)"),
        Line2D([0], [0], marker="o", color="none", markeredgecolor=C_EDGE,
               markersize=10, markeredgewidth=2.2, label="true (outer edge)"),
        Line2D([0], [0], marker="D", color="#4c9f70", linestyle="none",
               markeredgecolor="k", markersize=8, label="predicted"),
    ], loc="upper left", fontsize=8.5, framealpha=0.9)
    fig.tight_layout()
    fig.savefig(out, dpi=160); plt.close(fig)
    print(f"  saved {os.path.basename(out)}  (n={len(sub)}, xy {np.median(xy_err):.1f}mm, dz {np.median(dz):.1f}mm)")


def main():
    args = sys.argv[1:]
    maxn = None
    if "--max" in args:
        i = args.index("--max"); maxn = int(args[i + 1]); del args[i:i + 2]
    js, outdir = args[0], args[1]
    zlist = [int(z) for z in args[2:]]
    os.makedirs(outdir, exist_ok=True)
    pp = json.loads(open(js).read())["perPosition"]
    gx = sorted(set(round(p["x"]) for p in pp))
    gy = sorted(set(round(p["y"]) for p in pp))
    suff = f"_n{maxn}" if maxn else ""
    for z in zlist:
        tag = f"zp{z:02d}" if z >= 0 else f"zm{abs(z):02d}"
        plot_depth(pp, z, gx, gy, os.path.join(outdir, f"sim_depthplot_{tag}{suff}.png"), maxn)


if __name__ == "__main__":
    main()
