"""Predicted-vs-actual position figures for the regression deck.

Reads a cnn_regloso_* or cnn_reglopo_* result JSON (perPosition entries carry
predX/predY) and draws the true grid positions, the model's predicted positions,
and an arrow from each true point to its prediction.

The traced A3 phantom bowl + F4/F5 glandular outlines (grid-inch coordinates,
from detectable_change/A3_hunter/paper_figure_A3.py) are overlaid so you can see
directly which positions sit over the glandular insert, instead of a binary
near/exterior guess.

Usage:
    python make_pred_vs_actual.py <result.json> "<Title>" <out.png> [empty|F4|F5]
    (kind is inferred from the filename if omitted)
"""
import sys, json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Ellipse, Polygon

# ---- warm (UofU) palette ----
C_TRUE   = "#2C5F7C"   # true position (steel blue open circle)
C_PRED   = "#BE0000"   # predicted (crimson filled diamond)
C_ARROW  = "#B9A9A6"   # error arrow (warm grey)
C_OUT    = "#3A2A28"   # traced outlines (warm charcoal)

# ---- traced A3 outlines (grid inches) ----
BOWL_CENTER = (3.124, 3.028); BOWL_RX = 1.901; BOWL_RY = 3.233
A3_F4_OUTLINE = [
    (1.86,3.14),(1.72,2.96),(1.63,2.75),(1.50,2.47),(1.50,2.18),(1.61,1.93),
    (1.79,1.73),(2.05,1.64),(2.39,1.83),(2.62,1.92),(2.81,2.03),(2.98,2.12),
    (3.14,2.13),(3.28,2.23),(3.40,2.33),(3.50,2.45),(3.59,2.57),(3.64,2.72),
    (3.69,2.85),(3.85,2.97),(3.92,3.14),(4.01,3.33),(4.09,3.55),(4.17,3.83),
    (4.09,4.06),(3.90,4.22),(3.70,4.35),(3.44,4.36),(3.25,4.47),(3.02,4.46),
    (2.81,4.34),(2.64,4.21),(2.53,4.00),(2.47,3.82),(2.40,3.71),(2.33,3.62),
    (2.26,3.54),(2.21,3.45),(2.13,3.36),(2.01,3.27),
]
A3_F5_OUTLINE = [
    (1.40,3.43),(1.42,3.14),(1.50,2.87),(1.65,2.62),(1.80,2.39),(1.94,2.14),
    (2.13,1.92),(2.38,1.77),(2.64,1.61),(2.91,1.42),(3.23,1.33),(3.54,1.46),
    (3.81,1.64),(4.06,1.81),(4.22,2.07),(4.35,2.31),(4.42,2.56),(4.45,2.81),
    (4.50,3.02),(4.58,3.22),(4.55,3.43),(4.55,3.64),(4.53,3.85),(4.59,4.12),
    (4.54,4.38),(4.42,4.62),(4.06,4.57),(3.85,4.65),(3.65,4.72),(3.47,4.95),
    (3.23,5.27),(2.94,5.25),(2.67,5.15),(2.49,4.88),(2.29,4.72),(2.04,4.62),
    (1.82,4.46),(1.65,4.23),(1.49,3.99),(1.43,3.71),
]
OUTLINES = {"F4": A3_F4_OUTLINE, "F5": A3_F5_OUTLINE}


def infer_kind(json_path):
    s = str(json_path).lower()
    if "f4" in s: return "F4"
    if "f5" in s: return "F5"
    return "empty"


def draw(json_path, title, out_png, kind=None):
    if kind is None:
        kind = infer_kind(json_path)
    r = json.loads(Path(json_path).read_text())
    pp = [e for e in r.get("perPosition", [])
          if e.get("predX") is not None and np.isfinite(e.get("predX", np.nan))]
    tx = np.array([e["x"] for e in pp]);      ty = np.array([e["y"] for e in pp])
    px = np.array([e["predX"] for e in pp]);  py = np.array([e["predY"] for e in pp])
    err = np.array([e.get("medianErrIn", np.nan) for e in pp])

    fig, ax = plt.subplots(figsize=(6.2, 6.4))

    # grid
    for v in range(9):
        ax.axhline(v, color="#E3D6D2", lw=0.5, zorder=0)
        ax.axvline(v, color="#E3D6D2", lw=0.5, zorder=0)
    # traced phantom bowl + glandular outline
    ax.add_patch(Ellipse(BOWL_CENTER, 2*BOWL_RX, 2*BOWL_RY, fill=False,
                         edgecolor=C_OUT, lw=1.6, zorder=1))
    if kind in OUTLINES:
        ax.add_patch(Polygon(OUTLINES[kind], closed=True, fill=True,
                             facecolor=C_OUT, alpha=0.07, zorder=1))
        ax.add_patch(Polygon(OUTLINES[kind], closed=True, fill=False,
                             edgecolor=C_OUT, lw=1.6, linestyle=(0, (4, 2)), zorder=2))

    # arrows true -> predicted
    for i in range(len(tx)):
        ax.annotate("", xy=(px[i], py[i]), xytext=(tx[i], ty[i]),
                    arrowprops=dict(arrowstyle="->", color=C_ARROW, lw=1.3, alpha=0.95),
                    zorder=3)
    # true positions (open circles) + predicted (crimson diamonds)
    ax.scatter(tx, ty, s=72, facecolors="none", edgecolors=C_TRUE,
               linewidths=1.8, zorder=4)
    ax.scatter(px, py, s=44, c=C_PRED, marker="D", edgecolors="white",
               linewidths=0.4, zorder=5)

    ax.set_xlim(-0.2, max(6.5, tx.max() + 0.6))
    ax.set_ylim(max(6.6, ty.max() + 0.6), -0.2)     # y down, origin top-left
    ax.set_aspect("equal")
    ax.set_xlabel("X (inches)"); ax.set_ylabel("Y (inches)")
    for sp in ax.spines.values(): sp.set_color("#D8C7C2")

    med = float(r.get("losoPosMedianErr", [np.nan])[0]) if isinstance(
        r.get("losoPosMedianErr"), list) else r.get("overall", {}).get("medianErrIn", np.nanmedian(err))
    ax.set_title(f"{title}\nmedian error {med:.3f} in   "
                 f"(mean arrow {np.nanmean(err):.3f} in, n={len(tx)})",
                 fontsize=11, fontweight="bold", color="#2A1618")
    handles = [
        Line2D([0], [0], marker="o", color="none", markeredgecolor=C_TRUE,
               markersize=9, markeredgewidth=1.8, label="true position"),
        Line2D([0], [0], marker="D", color=C_PRED, linestyle="none",
               markersize=8, label="predicted"),
        Line2D([0], [0], color=C_OUT, lw=1.6, label="phantom bowl"),
    ]
    if kind in OUTLINES:
        handles.append(Line2D([0], [0], color=C_OUT, lw=1.6, linestyle=(0, (4, 2)),
                              label="glandular insert"))
    ax.legend(handles=handles, loc="upper right", fontsize=8, framealpha=0.92)
    fig.tight_layout()
    fig.savefig(out_png, dpi=160)
    plt.close(fig)
    print(f"saved {out_png}  (kind={kind}, median {med:.3f} in, {len(tx)} positions)")


if __name__ == "__main__":
    kind = sys.argv[4] if len(sys.argv) > 4 else None
    draw(sys.argv[1], sys.argv[2], sys.argv[3], kind)
