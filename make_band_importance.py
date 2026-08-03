"""Band-placement importance plot: LOSO accuracy vs window CENTER, one series
per window width, one panel per phantom. All runs: CNN, raw, 16 S-params, LOSO.

This is a sufficiency scan: each point trains the model on ONLY that window,
so the curve shows where in the spectrum the position information lives.
If 0.1 GHz scan results exist (scan_100mhz.sh) they appear as their own series.

Output: results/band_importance.png
"""
from __future__ import annotations
import json, re
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RESULTS = Path(__file__).resolve().parent / "results"
PHANTOMS = {"Empty": "June18_remap", "F4": "A3_F4_SamMed_all4", "F5": "A3_F5_SamMed_last3"}
# widths to draw as series: width -> (color, marker)
SERIES = {0.1: ("#BE0000", "s"), 0.25: ("#E8A33D", "o"),
          0.5: ("#7BA05B", "^"), 1.0: ("#4477AA", "D"), 2.0: ("#888888", "v")}
BAND_RE = re.compile(r"_band([\d.]+)-([\d.]+)\.json$")


def collect(pre):
    rows = []
    for f in RESULTS.glob(f"cnn_loso_{pre}_raw_all_ant1-2-3-4_band*.json"):
        m = BAND_RE.search(f.name)
        if not m:
            continue
        lo, hi = float(m.group(1)), float(m.group(2))
        r = json.loads(f.read_text())
        rows.append((round(hi - lo, 3), (lo + hi) / 2, r["losoPosMean"], r["losoPosStd"]))
    return rows


def main():
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.6), sharey=True)
    for ax, (ph, pre) in zip(axes, PHANTOMS.items()):
        rows = collect(pre)
        ax.axvspan(1.75, 2.25, color="#FBEDED", zorder=0)
        for w, (col, mk) in SERIES.items():
            pts = sorted((c, m, s) for ww, c, m, s in rows if abs(ww - w) < 1e-6)
            if len(pts) < 2:
                continue
            cs, ms, ss = zip(*pts)
            ax.errorbar(cs, ms, yerr=ss, fmt=f"-{mk}", color=col, lw=1.8, ms=5,
                        capsize=2.5, alpha=0.9, label=f"{w:g} GHz wide")
        ax.axhline(50, color="#333", ls="--", lw=1)
        ax.set_title(ph, fontsize=12.5, fontweight="bold")
        ax.set_xlabel("window center (GHz)", fontsize=10.5)
        ax.set_xlim(0.4, 4.1)
        ax.grid(alpha=0.3)
    axes[0].set_ylabel("LOSO accuracy (%)", fontsize=10.5)
    axes[0].set_ylim(0, 105)
    axes[0].legend(loc="lower right", fontsize=9)
    fig.suptitle("Where the information lives: train on ONLY one window, slide it across the spectrum "
                 "(shaded = 1.75-2.25 GHz; dashed = broken)", fontsize=11.5, y=0.99)
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(RESULTS / "band_importance.png", dpi=180)
    print("wrote", RESULTS / "band_importance.png")


if __name__ == "__main__":
    main()
