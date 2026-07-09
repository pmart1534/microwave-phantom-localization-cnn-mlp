"""Build the CNN-vs-MLP comparison table from results/*.json.

Scans results/ for cnn_loso_*.json and mlp_loso_*.json, pairs them by
(setup, antennaMode, ports), and writes a side-by-side Markdown + CSV table
of LOSO per-position accuracy.  Run it any time after either method produces
new results:

    python make_comparison.py
"""
from __future__ import annotations
import json, csv
from pathlib import Path
from collections import defaultdict

RESULTS = Path(__file__).resolve().parent / "results"


def key_of(r):
    p = r.get("ports", [])
    if not isinstance(p, (list, tuple)):   # MATLAB jsonencode writes a scalar for 1 port
        p = [p]
    ports = "-".join(str(int(x)) for x in p)
    sset = r.get("sessionSet") or f"{len(r.get('sessionNames', []))}sess"
    return (r.get("setup", "?"), sset, r.get("antennaMode", "?"), ports)


def load_all():
    rows = defaultdict(dict)   # key -> {"CNN": r, "MLP": r}
    for f in sorted(RESULTS.glob("*_loso_*.json")):
        try:
            r = json.loads(f.read_text())
        except Exception as e:
            print(f"  skip {f.name}: {e}"); continue
        rows[key_of(r)][r.get("method", "?")] = r
    return rows


def fmt(r, field):
    if r is None:
        return "-"
    m = r.get(field + "Mean")
    s = r.get(field + "Std")
    if m is None:
        return "-"
    return f"{m:.1f} +/- {s:.1f}"


def main():
    rows = load_all()
    if not rows:
        print(f"No results in {RESULTS}. Run the CNN and/or MLP first.")
        return

    header = ["setup", "sessions", "antenna", "ports", "n_way", "chance%",
              "CNN pos-vote%", "MLP pos-vote%", "CNN trial%", "MLP trial%"]
    table = []
    for (setup, sset, mode, ports), d in sorted(rows.items()):
        cnn, mlp = d.get("CNN"), d.get("MLP")
        any_r = cnn or mlp
        table.append([
            setup, sset, mode, ports,
            any_r.get("numClasses", "?"),
            f"{any_r.get('chancePct', 0):.1f}",
            fmt(cnn, "losoPos"), fmt(mlp, "losoPos"),
            fmt(cnn, "losoTrial"), fmt(mlp, "losoTrial"),
        ])

    # Markdown
    md = ["| " + " | ".join(header) + " |",
          "|" + "|".join(["---"] * len(header)) + "|"]
    for row in table:
        md.append("| " + " | ".join(str(x) for x in row) + " |")
    md_txt = "\n".join(md)
    (RESULTS / "comparison_table.md").write_text(md_txt + "\n")

    # CSV
    with open(RESULTS / "comparison_table.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(header); w.writerows(table)

    print(md_txt)
    print(f"\nWrote {RESULTS/'comparison_table.md'} and .csv")
    missing = [k for k, d in rows.items() if len(d) < 2]
    if missing:
        print("\nOnly one method present for:")
        for k in missing:
            have = "CNN" if "CNN" in rows[k] else "MLP"
            print(f"  {' / '.join(k)}  (have {have})")


if __name__ == "__main__":
    main()
