"""Sim CNN lateral error across narrower / shifted bands, using the ~4 mm method
(tuned MATLAB GPU CNN, deck random k-fold). Reads results/cnn_simreg_*_bwtest.json.

Left : error vs bandwidth at the best center (how narrow can we go).
Right: error vs center for 1 GHz windows (where to place the band).
"""
import os, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CRIMSON="#BE0000"; GREEN="#2E7D5B"; GOLD="#C8890B"; INK="#1E293B"; MUTE="#5B6B7B"; TEAL="#2C5F7C"
HERE=os.path.dirname(__file__); RES=os.path.join(HERE,"..","results")
def lat(suffix):
    tag = "8fold_nf256_5mmgrid" + suffix + "_bwtest"
    return json.load(open(os.path.join(RES,f"cnn_simreg_{tag}.json")))["lateral_medianMm"]

# ---- best-achievable error vs bandwidth (pick best center at each width) ----
by_width = {
    6.0:  ("full 2-8", lat("")),
    2.0:  ("2-4",      lat("_b2-4")),
    1.0:  ("3-4",      lat("_b3-4")),
    0.5:  ("3-3.5",    lat("_b3-3.5")),
    0.25: ("3-3.25",   lat("_b3-3.25")),
}
ws = sorted(by_width); errs=[by_width[w][1] for w in ws]; labs=[by_width[w][0] for w in ws]

# ---- 1 GHz windows across center ----
onegz = [(2.5,"_b2-3"),(3.5,"_b3-4"),(4.5,"_b4-5"),(5.5,"_b5-6"),(6.5,"_b6-7"),(7.5,"_b7-8")]
cen=[c for c,_ in onegz]; cerr=[lat(s) for _,s in onegz]

fig,(a1,a2)=plt.subplots(1,2,figsize=(12.6,5.4))
# panel 1
a1.plot(ws,errs,"-o",color=TEAL,lw=2.3,ms=7,zorder=3)
for w,e,l in zip(ws,errs,labs):
    a1.annotate(f"{l}\n{e:.1f}",(w,e),textcoords="offset points",xytext=(0,10),ha="center",fontsize=8.5,color=INK)
a1.axhline(3.95,color=GREEN,ls="--",lw=1.2); a1.text(6,3.95,"full-band 3.95mm",ha="right",va="bottom",fontsize=8.5,color=GREEN)
a1.set_xlabel("bandwidth used (GHz)",fontsize=11); a1.set_ylabel("sim lateral error, median (mm)",fontsize=11)
a1.set_title("How narrow can the band be?  (best center each width)",fontsize=12,fontweight="bold",color=INK)
a1.set_ylim(0,8); a1.grid(True,color="#EAF0F4",lw=0.7); a1.set_axisbelow(True)

# panel 2
bars=a2.bar([f"{c-0.5:g}-{c+0.5:g}" for c in cen],cerr,color=[GREEN if e<5 else (GOLD if e<8 else CRIMSON) for e in cerr],
            edgecolor="k",linewidth=0.5,width=0.66)
for b,e in zip(bars,cerr): a2.text(b.get_x()+b.get_width()/2,e+0.15,f"{e:.1f}",ha="center",va="bottom",fontsize=10.5,fontweight="bold",color=INK)
a2.axhline(3.95,color=GREEN,ls="--",lw=1.2)
a2.set_xlabel("1 GHz window (GHz)",fontsize=11); a2.set_ylabel("sim lateral error, median (mm)",fontsize=11)
a2.set_title("Where to center a 1 GHz band",fontsize=12,fontweight="bold",color=INK)
a2.set_ylim(0,13); a2.grid(True,axis="y",color="#EAF0F4",lw=0.7); a2.set_axisbelow(True)
for ax in (a1,a2):
    for s in ax.spines.values(): s.set_color("#D8E2EA")

fig.suptitle("Sim narrow-band sweep (tuned GPU CNN, deck k-fold - the ~4 mm method)",fontsize=14,fontweight="bold",color=INK,y=0.99)
fig.text(0.5,0.01,"Graceful narrowing at the 3-4 GHz center: 1 GHz -> 4.9 mm, 0.5 GHz -> 5.6 mm, even 0.25 GHz -> 6.4 mm (vs 3.95 full). "
         "But the band must sit LOW:\na 1 GHz window at 3-4 GHz is 4.9 mm; at 7-8 GHz it is 12 mm. Center matters far more than width.",
         ha="center",fontsize=9.3,color=MUTE,style="italic")
fig.subplots_adjust(left=0.07,right=0.98,top=0.88,bottom=0.19,wspace=0.22)
fig.savefig(os.path.join(HERE,"sim_narrowband.png"),dpi=160); print("wrote sim_narrowband.png")
