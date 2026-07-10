"""Predicted-vs-actual position figures for the regression deck.

Reads a cnn_regloso_* or cnn_reglopo_* result JSON (whose perPosition entries
now carry predX/predY) and draws the true grid positions, the model's predicted
positions, and an arrow from each true point to its prediction. Near-insert
positions (over the glandular insert) are marked distinctly.

Usage:
    python make_pred_vs_actual.py <result.json> "<Title>" <out.png>
"""
import sys, json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

C_EXT   = "#1f77b4"   # exterior true
C_INS   = "#d62728"   # near-insert true
C_PRED  = "#2ca02c"   # predicted
C_ARROW = "#888888"


def draw(json_path, title, out_png):
    r = json.loads(Path(json_path).read_text())
    pp = [e for e in r.get("perPosition", [])
          if e.get("predX") is not None and np.isfinite(e.get("predX", np.nan))]
    tx = np.array([e["x"] for e in pp]);      ty = np.array([e["y"] for e in pp])
    px = np.array([e["predX"] for e in pp]);  py = np.array([e["predY"] for e in pp])
    near = np.array([bool(e.get("nearInsert", False)) for e in pp])
    err = np.array([e.get("medianErrIn", np.nan) for e in pp])

    fig, ax = plt.subplots(figsize=(6.2, 6.4))

    # arrows true -> predicted
    for i in range(len(tx)):
        ax.annotate("", xy=(px[i], py[i]), xytext=(tx[i], ty[i]),
                    arrowprops=dict(arrowstyle="->", color=C_ARROW, lw=1.3, alpha=0.9))
    # true positions (circles), colored by insert membership
    ax.scatter(tx[~near], ty[~near], s=70, facecolors="none", edgecolors=C_EXT,
               linewidths=1.8, zorder=3, label="true (exterior)")
    if near.any():
        ax.scatter(tx[near], ty[near], s=70, facecolors="none", edgecolors=C_INS,
                   linewidths=1.8, zorder=3, label="true (near insert)")
    # predicted positions (filled diamonds)
    ax.scatter(px, py, s=42, c=C_PRED, marker="D", zorder=4, label="predicted")

    for v in range(9):
        ax.axhline(v, color="grey", lw=0.4, alpha=0.4, zorder=1)
        ax.axvline(v, color="grey", lw=0.4, alpha=0.4, zorder=1)
    ax.set_xlim(-0.2, max(6.5, tx.max() + 0.6))
    ax.set_ylim(max(6.6, ty.max() + 0.6), -0.2)     # y down, origin top-left
    ax.set_aspect("equal")
    ax.set_xlabel("X (inches)"); ax.set_ylabel("Y (inches)")

    med = float(r.get("losoPosMedianErr", [np.nan])[0]) if isinstance(
        r.get("losoPosMedianErr"), list) else r.get("overall", {}).get("medianErrIn", np.nanmedian(err))
    ax.set_title(f"{title}\nmedian error {med:.3f} in   "
                 f"(mean arrow {np.nanmean(err):.3f} in, n={len(tx)})",
                 fontsize=11, fontweight="bold")
    ax.legend(handles=[
        Line2D([0], [0], marker="o", color="none", markeredgecolor=C_EXT,
               markersize=9, markeredgewidth=1.8, label="true (exterior)"),
        Line2D([0], [0], marker="o", color="none", markeredgecolor=C_INS,
               markersize=9, markeredgewidth=1.8, label="true (near insert)"),
        Line2D([0], [0], marker="D", color=C_PRED, linestyle="none",
               markersize=8, label="predicted"),
    ], loc="upper right", fontsize=8, framealpha=0.9)
    fig.tight_layout()
    fig.savefig(out_png, dpi=160)
    plt.close(fig)
    print(f"saved {out_png}  (median {med:.3f} in, {len(tx)} positions)")


if __name__ == "__main__":
    draw(sys.argv[1], sys.argv[2], sys.argv[3])
