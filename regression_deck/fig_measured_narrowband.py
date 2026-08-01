"""Measured empty (metal) narrow-band: is ~1.75-2 GHz the best center, and how
narrow can it go? CNN under LOSO. Reads results/bw_meas_narrow_empty.json.

Left : error vs center for 0.25 GHz windows across 1-8 GHz (the sweet spot).
Right: error vs bandwidth at ~2 GHz center, down to 0.1 GHz, vs wide references.
"""
import os, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

CRIMSON="#BE0000"; GREEN="#2E7D5B"; GOLD="#C8890B"; INK="#1E293B"; MUTE="#5B6B7B"; TEAL="#2C5F7C"
HERE=os.path.dirname(__file__); RES=os.path.join(HERE,"..","results")
mm=lambda x:x*25.4
d=json.load(open(os.path.join(RES,"bw_meas_narrow_empty.json")))
q=[r for r in d["rows"] if abs(r["width"]-0.25)<1e-6]
q.sort(key=lambda r:r["center"])
cen=[r["center"] for r in q]; err=[mm(r["err"]) for r in q]
best=min(q,key=lambda r:r["err"])

fig,(a1,a2)=plt.subplots(1,2,figsize=(12.8,5.4),gridspec_kw={"width_ratios":[1.7,1]})
# ---- panel 1: 0.25 GHz window error vs center
a1.add_patch(Rectangle((1.5,0),0.75,20,color=GREEN,alpha=0.10,zorder=0))  # sweet spot 1.5-2.25
a1.text(1.875,0.4,"sweet spot\n~1.5-2.25 GHz",ha="center",va="bottom",fontsize=8.5,color=GREEN)
a1.plot(cen,err,"-o",color=TEAL,lw=2,ms=5,zorder=3)
# mark 1.75-2 and best
for r,c,lab,col in [(next(x for x in q if abs(x["center"]-1.875)<1e-3),CRIMSON,"1.75-2 GHz\n(your pick)",CRIMSON),
                    (best,GOLD,f"best {best['lo']:g}-{best['hi']:g}",GOLD)]:
    a1.plot(r["center"],mm(r["err"]),"o",color=col,ms=10,zorder=4)
    a1.annotate(lab,(r["center"],mm(r["err"])),textcoords="offset points",xytext=(6,-24),fontsize=8.5,color=col,fontweight="bold")
a1.set_xlabel("center of 0.25 GHz window (GHz)",fontsize=11); a1.set_ylabel("measured lateral error, median (mm)",fontsize=11)
a1.set_title("0.25 GHz windows across 1-8 GHz: low band wins",fontsize=12,fontweight="bold",color=INK)
a1.set_ylim(0,14); a1.grid(True,color="#EAF0F4",lw=0.7); a1.set_axisbelow(True)

# ---- panel 2: width knee at ~2 GHz center
def at(lo,hi):
    for r in d["rows"]:
        if abs(r["lo"]-lo)<1e-3 and abs(r["hi"]-hi)<1e-3: return mm(r["err"])
    return None
widths=["0.1 GHz\n1.95-2.05","0.15 GHz\n1.925-2.075","0.25 GHz\n1.75-2.0"]
wv=[at(1.95,2.05),at(1.925,2.075),at(1.75,2.0)]
bars=a2.bar(widths,wv,color=GOLD,edgecolor="k",linewidth=0.5,width=0.6)
for b,v in zip(bars,wv): a2.text(b.get_x()+b.get_width()/2,v+0.1,f"{v:.1f}",ha="center",va="bottom",fontsize=11,fontweight="bold",color=INK)
a2.axhline(2.9,color=GREEN,ls="--",lw=1.3); a2.text(2.4,2.9,"2-4 GHz band (2.9)",ha="right",va="bottom",fontsize=8,color=GREEN)
a2.axhline(4.3,color=MUTE,ls=":",lw=1.3);  a2.text(2.4,4.3,"full 1-8 GHz (4.3)",ha="right",va="bottom",fontsize=8,color=MUTE)
a2.set_ylabel("measured lateral error (mm)",fontsize=11)
a2.set_title("Even 100 MHz at ~2 GHz holds up",fontsize=12,fontweight="bold",color=INK)
a2.set_ylim(0,6); a2.grid(True,axis="y",color="#EAF0F4",lw=0.7); a2.set_axisbelow(True)
for ax in (a1,a2):
    for s in ax.spines.values(): s.set_color("#D8E2EA")

fig.suptitle("Measured metal target: the localizer's sweet spot is ~1.5-2.25 GHz, and it needs almost no width there",
             fontsize=13.5,fontweight="bold",color=INK,y=0.99)
fig.text(0.5,0.01,"CNN under LOSO. 1.75-2 GHz (3.5 mm) sits in the flat sweet spot (best 2-2.25 = 3.3 mm); it collapses below 1.5 GHz "
         "(13.6 mm at 1-1.25,\nwhere the antenna barely radiates) and drifts up above ~2.5 GHz. A 100 MHz window at ~2 GHz still reaches 3.5 mm.",
         ha="center",fontsize=9.2,color=MUTE,style="italic")
fig.subplots_adjust(left=0.07,right=0.98,top=0.88,bottom=0.19,wspace=0.22)
fig.savefig(os.path.join(HERE,"measured_narrowband.png"),dpi=160); print("wrote measured_narrowband.png")
