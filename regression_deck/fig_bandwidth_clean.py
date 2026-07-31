"""Clean bandwidth curves under DECK-MATCHED protocols (vary only the band).

measured empty/F4/F5: CNN under LOSO (k-NN saturates -> shown for sim only).
sim_all: CNN + k-NN under strict (x,y)-disjoint 8-fold on the full depth stack.
Reads results/bw_clean_{empty,F4,F5,sim_all}.json.
"""
import os, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CRIMSON="#BE0000"; GOLD="#C8890B"; GREEN="#2E7D5B"; INK="#1E293B"; MUTE="#5B6B7B"; TEAL="#2C5F7C"
HERE=os.path.dirname(__file__); RES=os.path.join(HERE,"..","results")
mm=lambda x:x*25.4
def load(ds): return json.load(open(os.path.join(RES,f"bw_clean_{ds}.json")))
def bpw(rows):
    ws=sorted(set(r["width"] for r in rows))
    return ws,[mm(min([r for r in rows if abs(r["width"]-w)<1e-6],key=lambda r:r["err"])["err"]) for w in ws]

PANELS=[("empty","A3 empty (metal)  -  CNN, LOSO",TEAL,"cnn"),
        ("F4","A3 F4 gland  -  CNN, LOSO",GOLD,"cnn"),
        ("F5","A3 F5 gland  -  CNN, LOSO",CRIMSON,"cnn"),
        ("sim_all","Simulated, full depth  -  strict (x,y)-LOPO",GREEN,"both")]

fig,axs=plt.subplots(2,2,figsize=(11.8,8.4))
for ax,(ds,title,col,which) in zip(axs.ravel(),PANELS):
    d=load(ds)
    ws,ec=bpw(d["dense_cnn"])
    ax.plot(ws,ec,"-o",color=col,lw=2.3,ms=6,label="CNN",zorder=3)
    if which=="both":
        _,ek=bpw(d["dense_knn"])
        ax.plot(ws,ek,"--s",color=MUTE,lw=1.8,ms=5,label="k-NN floor",zorder=2)
    ax.axhline(mm(d["chanceIn"]),color=MUTE,ls=":",lw=1.1)
    ax.text(ws[-1],mm(d["chanceIn"]),"  chance",va="center",fontsize=8,color=MUTE)
    if ds!="sim_all":
        ax.axhline(3.9,color="#B0B0B0",ls="-",lw=0.8)
        ax.text(ws[0],3.9,"deck 3.9mm ",va="bottom",ha="left",fontsize=7.5,color="#9098A0")
    ax.set_title(title,fontsize=11.5,fontweight="bold",color=INK)
    ax.set_xlabel("bandwidth used (GHz)",fontsize=10.5); ax.set_ylabel("localization error (mm)",fontsize=10.5)
    top=max(mm(d["chanceIn"])*1.05, max(ec)*1.2)
    ax.set_ylim(0,top); ax.grid(True,color="#EAF0F4",lw=0.7); ax.set_axisbelow(True)
    if which=="both": ax.legend(fontsize=9,framealpha=0.95,loc="upper left")
    for s in ax.spines.values(): s.set_color("#D8E2EA")
fig.suptitle("Bandwidth under deck-matched protocols (vary only the band)",fontsize=15,fontweight="bold",color=INK,y=0.995)
fig.text(0.5,0.958,"measured = LOSO (k-NN saturates, CNN only); sim = strict (x,y)-disjoint 8-fold on the full depth stack",
         ha="center",fontsize=10.5,color=MUTE)
fig.text(0.5,0.01,"Measured CNN reaches deck-level accuracy and is FLAT vs bandwidth: a 2 GHz band matches the full sweep (empty 2.9mm @2-4GHz). "
         "Sim: the k-NN floor\nputs the lateral info in the low band (~5.5mm @2-3GHz); the small CNN underperforms its own floor and mis-picks a high band "
         "(capacity-limited on this harder task).",ha="center",fontsize=9.5,color=MUTE,style="italic")
fig.subplots_adjust(left=0.07,right=0.98,top=0.885,bottom=0.10,hspace=0.32,wspace=0.20)
fig.savefig(os.path.join(HERE,"bw_clean.png"),dpi=160); print("wrote bw_clean.png")
