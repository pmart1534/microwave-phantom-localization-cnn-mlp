"""Antenna reduction within the 2-4 GHz sweet spot (the 'simplest chip' corner).

Grouped bars per config: all-16 -> reflection-all -> refl-1&3 -> refl-1, at the
2-4 GHz band. k-NN always; CNN overlaid if bw_antenna_cnn.json exists.
"""
import os, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

TEAL="#2C5F7C"; CRIMSON="#BE0000"; INK="#1E293B"; MUTE="#5B6B7B"
HERE=os.path.dirname(__file__); RES=os.path.join(HERE,"..","results")
DS=[("empty","A3 empty (metal target)"),("F4","A3 F4 gland"),
    ("F5","A3 F5 gland"),("sim","Simulated metal")]
CFG=["all-16","refl-all","refl-1&3","refl-1"]
LBL=["all 16","reflection\nall 4","reflection\n1 & 3","reflection\n1 only"]
mm=lambda x:x*25.4
kn=json.load(open(os.path.join(RES,"bw_antenna_knn.json")))
cp=os.path.join(RES,"bw_antenna_cnn.json")
cn=json.load(open(cp)) if os.path.exists(cp) else None

fig,axs=plt.subplots(2,2,figsize=(11.6,8.4))
x=np.arange(len(CFG))
for ax,(ds,title) in zip(axs.ravel(),DS):
    kv=[mm(kn[ds][c]) for c in CFG]
    if cn:
        w=0.38
        ax.bar(x-w/2,kv,w,color=TEAL,label="k-NN floor",edgecolor="k",linewidth=0.4)
        cv=[mm(cn[ds][c]) for c in CFG]
        ax.bar(x+w/2,cv,w,color=CRIMSON,label="CNN",edgecolor="k",linewidth=0.4)
        for xi,(a,b) in enumerate(zip(kv,cv)):
            ax.text(xi-w/2,a+0.4,f"{a:.1f}",ha="center",va="bottom",fontsize=8,color=INK)
            ax.text(xi+w/2,b+0.4,f"{b:.1f}",ha="center",va="bottom",fontsize=8,color=INK)
    else:
        ax.bar(x,kv,0.6,color=TEAL,label="k-NN floor",edgecolor="k",linewidth=0.4)
        for xi,a in enumerate(kv): ax.text(xi,a+0.4,f"{a:.1f}",ha="center",va="bottom",fontsize=9,color=INK)
    ax.axhline(mm(kn[ds]["chanceIn"]),color=MUTE,ls="--",lw=1.1)
    ax.text(len(CFG)-0.5,mm(kn[ds]["chanceIn"]),"chance",va="bottom",ha="right",fontsize=8.5,color=MUTE)
    ax.set_title(title,fontsize=12,fontweight="bold",color=INK)
    ax.set_xticks(x); ax.set_xticklabels(LBL,fontsize=9)
    ax.set_ylabel("error at 2-4 GHz (mm)",fontsize=10.5)
    top=max(mm(kn[ds]["chanceIn"]),max(kv))*1.15
    if cn: top=max(top,max(mm(cn[ds][c]) for c in CFG)*1.15)
    ax.set_ylim(0,top); ax.grid(True,axis="y",color="#EAF0F4",lw=0.7); ax.set_axisbelow(True)
    ax.legend(fontsize=9,framealpha=0.95,loc="upper left")
    for s in ax.spines.values(): s.set_color("#D8E2EA")
fig.suptitle("Simplest-chip corner: antenna reduction WITHIN the 2-4 GHz sweet spot",
             fontsize=15,fontweight="bold",color=INK,y=0.985)
fig.text(0.5,0.945,"fewer antennas / reflection-only, restricted to the 2-4 GHz band (leave-one-position-out CV)",
         ha="center",fontsize=10.5,color=MUTE)
fig.text(0.5,0.012,"Both models agree on the ordering: more antennas help, and F5 / sim degrade most as ports drop (transmission carries their signal). "
         "The k-NN floor shows the\ninformation supports a minimal front end on the easy metal target (~8 mm at 1 antenna); the trained CNN is uniformly higher here "
         "(data-limited under leave-one-position-out).",
         ha="center",fontsize=9.5,color=MUTE,style="italic")
fig.subplots_adjust(left=0.07,right=0.98,top=0.90,bottom=0.11,hspace=0.30,wspace=0.20)
p=os.path.join(HERE,"bw_antenna.png"); fig.savefig(p,dpi=160); print("wrote",os.path.basename(p))
