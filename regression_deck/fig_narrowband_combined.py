"""Combined measured vs sim narrow-band picture.
  Left : error vs center for 0.25 GHz windows -- measured (1-8) and sim (2-8).
         Shows the sweet-spot OFFSET (measured ~2 GHz, sim ~3-3.25 GHz).
  Right: error vs bandwidth (how narrow), each at its own best center.

UNITS: measured JSON stores error in INCHES (x25.4); sim MATLAB JSON stores
lateral_medianMm already in MM.
"""
import os, json, glob, re
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

CRIMSON="#BE0000"; GREEN="#2E7D5B"; GOLD="#C8890B"; INK="#1E293B"; MUTE="#5B6B7B"; TEAL="#2C5F7C"
HERE=os.path.dirname(__file__); RES=os.path.join(HERE,"..","results")

# measured (inches -> mm)
dm=json.load(open(os.path.join(RES,"bw_meas_narrow_empty.json")))
mq=sorted([r for r in dm["rows"] if abs(r["width"]-0.25)<1e-6],key=lambda r:r["center"])
mc=[r["center"] for r in mq]; me=[r["err"]*25.4 for r in mq]

# sim (mm direct)
def sv(f): return json.load(open(f))["lateral_medianMm"]
srows=[]
for f in glob.glob(os.path.join(RES,"cnn_simreg_8fold_nf256_5mmgrid_b*_bwtest.json")):
    m=re.search(r"_b([0-9.]+)-([0-9.]+)_bwtest",f)
    if m: srows.append((float(m.group(1)),float(m.group(2)),round(float(m.group(2))-float(m.group(1)),3),sv(f)))
sq=sorted([r for r in srows if abs(r[2]-0.25)<1e-3],key=lambda r:r[0])
sc=[(r[0]+r[1])/2 for r in sq]; se=[r[3] for r in sq]

fig,(a1,a2)=plt.subplots(1,2,figsize=(13,5.4),gridspec_kw={"width_ratios":[1.55,1]})
# ---- panel 1: center offset
a1.add_patch(Rectangle((1.5,0),0.75,20,color=TEAL,alpha=0.08)); a1.text(1.875,0.5,"meas\n~2",ha="center",fontsize=8,color=TEAL)
a1.add_patch(Rectangle((2.875,0),0.75,20,color=GREEN,alpha=0.08)); a1.text(3.25,0.5,"sim\n~3.25",ha="center",fontsize=8,color=GREEN)
a1.plot(mc,me,"-o",color=TEAL,lw=2,ms=5,label="measured (metal, LOSO)")
a1.plot(sc,se,"-s",color=GREEN,lw=2,ms=5,label="sim (metal, k-fold)")
a1.set_xlabel("center of 0.25 GHz window (GHz)",fontsize=11); a1.set_ylabel("lateral error, median (mm)",fontsize=11)
a1.set_title("0.25 GHz window vs center: measured peaks LOWER than sim",fontsize=11.5,fontweight="bold",color=INK)
a1.set_ylim(0,14); a1.set_xlim(0.8,8.2); a1.legend(fontsize=9.5,framealpha=0.95)
a1.grid(True,color="#EAF0F4",lw=0.7); a1.set_axisbelow(True)

# ---- panel 2: how narrow (width) at each best center
def matm(lo,hi):
    for r in dm["rows"]:
        if abs(r["lo"]-lo)<1e-3 and abs(r["hi"]-hi)<1e-3: return r["err"]*25.4
def sim_at(lo,hi):
    for r in srows:
        if abs(r[0]-lo)<1e-3 and abs(r[1]-hi)<1e-3: return r[3]
mw=[0.1,0.15,0.25]; mv=[matm(1.95,2.05),matm(1.925,2.075),matm(1.75,2.0)]
sw=[0.1,0.15,0.25,1.0,2.0,6.0]
sv2=[sim_at(2.95,3.05),sim_at(2.925,3.075),sim_at(3,3.25),sim_at(3,4),sim_at(2,4),sv(os.path.join(RES,"cnn_simreg_8fold_nf256_5mmgrid_bwtest.json"))]
a2.plot(sw,sv2,"-s",color=GREEN,lw=2,ms=6,label="sim @ ~3-3.5 GHz")
a2.plot(mw,mv,"-o",color=TEAL,lw=2,ms=6,label="measured @ ~2 GHz")
for w,v in zip(sw,sv2): a2.annotate(f"{v:.1f}",(w,v),textcoords="offset points",xytext=(0,7),ha="center",fontsize=8,color=GREEN)
for w,v in zip(mw,mv): a2.annotate(f"{v:.1f}",(w,v),textcoords="offset points",xytext=(0,-13),ha="center",fontsize=8,color=TEAL)
a2.set_xscale("log"); a2.set_xticks([0.1,0.25,0.5,1,2,6]); a2.set_xticklabels(["0.1","0.25","0.5","1","2","6"])
a2.set_xlabel("bandwidth used (GHz, log)",fontsize=11); a2.set_ylabel("lateral error, median (mm)",fontsize=11)
a2.set_title("How narrow (at each best center)",fontsize=11.5,fontweight="bold",color=INK)
a2.set_ylim(0,9); a2.legend(fontsize=9.5,framealpha=0.95,loc="upper right")
a2.grid(True,which="both",color="#EAF0F4",lw=0.7); a2.set_axisbelow(True)
for ax in (a1,a2):
    for s in ax.spines.values(): s.set_color("#D8E2EA")

fig.suptitle("Localization error by 0.25 GHz window center (left) and by bandwidth at the best center (right)",
             fontsize=13,fontweight="bold",color=INK,y=0.99)
fig.subplots_adjust(left=0.07,right=0.98,top=0.88,bottom=0.19,wspace=0.22)
fig.savefig(os.path.join(HERE,"narrowband_combined.png"),dpi=160); print("wrote narrowband_combined.png")
