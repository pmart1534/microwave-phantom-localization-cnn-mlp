"""Build the input x model x antenna x phantom factorial table.

Reads results/*_loso_*.json, keeps only the native-grid factorial runs (those
carrying an `inputKind` field: raw | physics | tdr), pairs CNN vs MLP for each
(setup, sessionSet, inputKind, antenna, ports), and writes:
  results/factorial_table.md  /  .csv

Rows are grouped so you can read, per phantom + antenna count, how CNN and MLP
compare across the three input representations.
"""
from __future__ import annotations
import json, csv
from pathlib import Path
from collections import defaultdict

RESULTS = Path(__file__).resolve().parent / "results"
INPUT_ORDER = {"raw": 0, "physics": 1, "tdr": 2}
ANT_ORDER = {"all": 0, "pair": 1, "refl": 2, "single": 3}


def ports_str(r):
    p = r.get("ports", [])
    if not isinstance(p, (list, tuple)):
        p = [p]
    return "-".join(str(int(x)) for x in p)


def antenna_label(mode, ports):
    return {"all": "all-4", "single": f"single {ports}",
            "pair": f"pair {ports}", "refl": f"refl {ports}"}.get(mode, mode)


def main():
    groups = defaultdict(dict)   # key -> {CNN:r, MLP:r}
    for f in sorted(RESULTS.glob("*_loso_*.json")):
        try:
            r = json.loads(f.read_text())
        except Exception:
            continue
        if "inputKind" not in r:          # only the new factorial runs
            continue
        clf = r.get("classifier", "single")
        key = (r.get("setup", "?"), r.get("sessionSet", "?"), clf, r["inputKind"],
               r.get("antennaMode", "?"), ports_str(r))
        groups[key][r.get("method", "?")] = r
    if not groups:
        print("No factorial (inputKind) results yet."); return

    def sort_key(k):
        setup, sset, clf, inp, mode, ports = k
        return (setup, sset, ANT_ORDER.get(mode, 9), ports,
                INPUT_ORDER.get(inp, 9), clf)

    header = ["setup", "sessions", "classifier", "antenna", "input", "n_way",
              "chance%", "CNN pos-vote%", "MLP pos-vote%"]
    table = []
    for key in sorted(groups, key=sort_key):
        setup, sset, clf, inp, mode, ports = key
        cnn, mlp = groups[key].get("CNN"), groups[key].get("MLP")
        any_r = cnn or mlp

        def cell(r):
            if r is None or r.get("losoPosMean") is None:
                return "-"
            return f"{r['losoPosMean']:.1f} +/- {r['losoPosStd']:.1f}"
        table.append([setup, sset, clf, antenna_label(mode, ports), inp,
                      any_r.get("numClasses", "?"), f"{any_r.get('chancePct', 0):.1f}",
                      cell(cnn), cell(mlp)])

    md = ["| " + " | ".join(header) + " |",
          "|" + "|".join(["---"] * len(header)) + "|"]
    md += ["| " + " | ".join(str(x) for x in row) + " |" for row in table]
    (RESULTS / "factorial_table.md").write_text("\n".join(md) + "\n")
    with open(RESULTS / "factorial_table.csv", "w", newline="") as f:
        w = csv.writer(f); w.writerow(header); w.writerows(table)
    print("\n".join(md))
    print(f"\nWrote {RESULTS/'factorial_table.md'} ({len(table)} rows)")


if __name__ == "__main__":
    main()
