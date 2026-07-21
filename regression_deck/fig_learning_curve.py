"""Deck 2 - sim CNN localization vs. training-data volume (depth-count sweep).

Each point trains the 8-fold sim CNN on a growing number of DEPTH PLANES; every
extra plane adds ~82 new distinct (x,y) positions. Shows the CNN needs ~400-500
distinct positions before it localizes well.
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

NAVY="#0E2233"; BLUE="#0B5D7A"; TEAL="#1C9AA8"; MINT="#2CC4A3"
CORAL="#D64545"; INK="#1E293B"; MUTE="#5B6B7B"; GREEN="#2E7D5B"
OUT = os.path.dirname(__file__)

# (depth planes, training samples, lateral xy median mm)
DATA = [(1,82,33.55),(3,245,11.35),(5,410,4.84),(7,569,3.98),
        (9,724,3.82),(11,898,3.81),(13,1074,3.92)]
d  = np.array([x[0] for x in DATA])
n  = np.array([x[1] for x in DATA])
xy = np.array([x[2] for x in DATA])
CHANCE = 36.0; PLATEAU = 3.85

fig, ax = plt.subplots(figsize=(9.0, 5.6))
ax.axhline(CHANCE, color=CORAL, ls="--", lw=1.4, zorder=1)
ax.text(n[-1], CHANCE+0.4, "chance (~36 mm)", ha="right", va="bottom",
        color=CORAL, fontsize=10, fontweight="bold")
ax.axhline(PLATEAU, color=GREEN, ls=":", lw=1.6, zorder=1)

ax.plot(n, xy, "-o", color=BLUE, lw=2.6, ms=10, zorder=3)
# point labels: number of depth planes, placed consistently above each point
for di, ni, yi in zip(d, n, xy):
    lab = "1 plane" if di == 1 else f"{di}"
    ax.annotate(lab, (ni, yi), textcoords="offset points", xytext=(0, 12),
                ha="center", va="bottom", fontsize=10.5, color=INK, fontweight="bold")

# what 'd'/the labels mean, in the empty upper-right region
ax.text(560, 27,
        "point label = number of DEPTH PLANES\nthe CNN trained on\n(each plane adds ~82 new positions)",
        fontsize=10.5, color=MUTE, ha="left", va="center",
        bbox=dict(boxstyle="round,pad=0.5", fc="#F3F7FA", ec="#D8E2EA"))
# plateau label placed BELOW its line, clear of the point labels
ax.text(880, 1.7, "plateau ~3.8 mm", color=GREEN, fontsize=10.5,
        fontweight="bold", ha="center", va="center")

ax.set_xlabel("training samples  (~82 per depth plane)", fontsize=12)
ax.set_ylabel("lateral (xy) median error (mm)", fontsize=12)
ax.set_title("Sim CNN localization vs. training-data volume",
             fontsize=14, fontweight="bold", color=INK)
ax.set_ylim(0, 38); ax.set_xlim(0, 1160)
ax.grid(True, color="#EAF0F4", lw=0.7); ax.set_axisbelow(True)
for s in ax.spines.values(): s.set_color("#D8E2EA")
fig.subplots_adjust(left=0.09, right=0.97, top=0.91, bottom=0.12)
p = os.path.join(OUT, "sim_depth_learning_curve.png")
fig.savefig(p, dpi=160); print("wrote", p)
