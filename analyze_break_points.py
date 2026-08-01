"""Per-phantom bandwidth breaking-point analysis.

Scans all matched CNN band-sweep results (raw input, all 16 S-params, LOSO)
and, for each phantom, builds the best-window-per-width curve and finds where
the model crosses each failure tier:

  DEGRADED   mean < 90% of that phantom's full-band accuracy
  UNSTABLE   fold-to-fold sigma >= 10 points (session-dependence)
  BROKEN     mean < 50% absolute (headline break)
  DEEP       mean < 25% absolute

Outputs:
  results/break_analysis.md      per-phantom curves + break table
  results/break_curve.png        best-per-width curve with tier lines
"""
from __future__ import annotations
import json, re
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

RESULTS = Path(__file__).resolve().parent / "results"
RED, DARK, GREY, GOLD = "#BE0000", "#333333", "#8a8a8a", "#C8890B"

PHANTOMS = {  # name -> (setup, sessionSet, full-band mean)
    "Empty": ("June18", "remap", 99.35),
    "F4":    ("A3_F4_SamMed", "all4", 97.44),
    "F5":    ("A3_F5_SamMed", "last3", 100.0),
}
BAND_RE = re.compile(r"_band([\d.]+)-([\d.]+)\.json$")


def collect():
    """-> {phantom: [(width, lo, hi, mean, sd), ...]} from matched band runs."""
    out = {k: [] for k in PHANTOMS}
    for f in RESULTS.glob("cnn_loso_*_raw_all_ant1-2-3-4_band*.json"):
        m = BAND_RE.search(f.name)
        if not m:
            continue
        try:
            r = json.loads(f.read_text())
        except Exception:
            continue
        if r.get("classifier", "single") != "single" or r.get("inputKind") != "raw":
            continue
        for name, (setup, sset, _) in PHANTOMS.items():
            if r.get("setup") == setup and r.get("sessionSet") == sset:
                lo, hi = float(m.group(1)), float(m.group(2))
                out[name].append((round(hi - lo, 3), lo, hi,
                                  r["losoPosMean"], r["losoPosStd"]))
    return out


def best_per_width(rows):
    """-> sorted [(width, lo, hi, mean, sd)] keeping the best window per width."""
    by_w = {}
    for w, lo, hi, m, s in rows:
        if w not in by_w or m > by_w[w][3]:
            by_w[w] = (w, lo, hi, m, s)
    return sorted(by_w.values())


def tier_crossings(curve, full):
    """First width (descending) at which each tier is crossed, using the BEST
    window per width. Returns dict tier -> width or None."""
    tiers = {"degraded": None, "unstable": None, "broken50": None, "deep25": None}
    for w, lo, hi, m, s in sorted(curve, reverse=True):
        if m < 0.9 * full and tiers["degraded"] is None:
            tiers["degraded"] = w
        if s >= 10 and tiers["unstable"] is None:
            tiers["unstable"] = w
        if m < 50 and tiers["broken50"] is None:
            tiers["broken50"] = w
        if m < 25 and tiers["deep25"] is None:
            tiers["deep25"] = w
    return tiers


def main():
    data = collect()
    lines = ["# Bandwidth breaking-point analysis",
             "",
             "CNN classification, raw input, all 16 S-parameters, LOSO per-position vote.",
             "Best window per width (placement optimised at every width).",
             "",
             "Tiers: DEGRADED < 90% of full-band | UNSTABLE fold sigma >= 10 | "
             "BROKEN < 50% | DEEP < 25%", ""]
    fig, ax = plt.subplots(figsize=(9.6, 5.2))
    colors = {"Empty": GREY, "F4": GOLD, "F5": RED}
    table = []
    for name, (setup, sset, full) in PHANTOMS.items():
        curve = best_per_width(data[name])
        t = tier_crossings(curve, full)
        table.append((name, full, curve, t))
        lines.append(f"## {name} (full-band {full:.1f}%)")
        lines.append("")
        lines.append("| width (GHz) | best window | mean % | fold sigma | flags |")
        lines.append("|---|---|---|---|---|")
        for w, lo, hi, m, s in sorted(curve, reverse=True):
            flags = []
            if m < 0.9 * full: flags.append("DEGRADED")
            if s >= 10: flags.append("UNSTABLE")
            if m < 50: flags.append("BROKEN")
            if m < 25: flags.append("DEEP")
            lines.append(f"| {w:g} | {lo:g}-{hi:g} | {m:.1f} | {s:.1f} | {' '.join(flags) or '-'} |")
        lines.append("")
        lines.append(f"Breaking points: degraded at {t['degraded'] or 'never'} GHz, "
                     f"unstable at {t['unstable'] or 'never'} GHz, "
                     f"broken(<50%) at {t['broken50'] or 'never'} GHz, "
                     f"deep(<25%) at {t['deep25'] or 'never'} GHz.")
        lines.append("")
        ws = [c[0] for c in sorted(curve, reverse=True)]
        ms = [c[3] for c in sorted(curve, reverse=True)]
        ss = [c[4] for c in sorted(curve, reverse=True)]
        ax.errorbar(ws, ms, yerr=ss, fmt="-o", color=colors[name], lw=2, ms=5,
                    capsize=3, label=f"{name} (full {full:.0f}%)", alpha=0.9)
    ax.axhline(50, color=DARK, ls="--", lw=1.2)
    ax.text(4.05, 51.5, "BROKEN < 50%", fontsize=9.5, color=DARK)
    ax.axhline(25, color=DARK, ls=":", lw=1.1)
    ax.text(4.05, 26.5, "DEEP < 25%", fontsize=9.5, color=GREY)
    ax.set_xscale("log")
    ax.set_xticks([0.05, 0.1, 0.25, 0.5, 1, 2, 3, 4])
    ax.set_xticklabels(["0.05", "0.1", "0.25", "0.5", "1", "2", "3", "4"])
    ax.set_xlabel("bandwidth (GHz), best placement per width, log scale", fontsize=11)
    ax.set_ylabel("LOSO accuracy (%)  (error bars = fold-to-fold sigma)", fontsize=11)
    ax.set_title("Where the CNN breaks: accuracy vs bandwidth per phantom",
                 fontsize=12.5, fontweight="bold", color=DARK)
    ax.grid(alpha=0.3); ax.legend(loc="lower right", fontsize=10)
    ax.set_ylim(0, 105)
    fig.tight_layout()
    fig.savefig(RESULTS / "break_curve.png", dpi=180)
    (RESULTS / "break_analysis.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines[-40:]))
    print(f"\nwrote {RESULTS/'break_analysis.md'} and break_curve.png")


if __name__ == "__main__":
    main()
