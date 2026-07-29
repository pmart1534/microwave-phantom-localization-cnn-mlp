"""CNN vs k-NN bandwidth knee: best-achievable error vs bandwidth, both models.

Reads results/bw_sweep_reg_{ds}.json (k-NN) and bw_sweep_cnn_{ds}.json (CNN),
same data / folds / grid. Confirms whether the k-NN sweet-spot band holds for
the trained CNN.
"""
import os, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CRIMSON="#BE0000"; TEAL="#2C5F7C"; INK="#1E293B"; MUTE="#5B6B7B"
HERE=os.path.dirname(__file__); RES=os.path.join(HERE,"..","results")
DS=[("empty","A3 empty (metal target)"),("F4","A3 F4 gland"),
    ("F5","A3 F5 gland"),("sim","Simulated metal")]
mm=lambda x:x*25.4

def best_per_width(dr):
    ws=sorted(set(r["width"] for r in dr)); out=[]
    for w in ws:
        cw=[r for r in dr if abs(r["width"]-w)<1e-6]; b=min(cw,key=lambda r:r["err"])
        out.append((w,mm(b["err"])))
    return np.array(out)

fig,axs=plt.subplots(2,2,figsize=(11.8,8.4))
for ax,(ds,title) in zip(axs.ravel(),DS):
    dk=json.load(open(os.path.join(RES,f"bw_sweep_reg_{ds}.json")))
    dc=json.load(open(os.path.join(RES,f"bw_sweep_cnn_{ds}.json")))
    bk=best_per_width(dk["dense_knn"]); bc=best_per_width(dc["dense_cnn"])
    ax.plot(bk[:,0],bk[:,1],"-o",color=TEAL,lw=2,ms=6,label="k-NN (signal floor)")
    ax.plot(bc[:,0],bc[:,1],"-s",color=CRIMSON,lw=2.2,ms=7,label="CNN (trained model)")
    ax.axhline(mm(dk["chanceIn"]),color=MUTE,ls="--",lw=1.1)
    ax.text(bk[-1,0],mm(dk["chanceIn"]),"  chance",va="center",fontsize=8.5,color=MUTE)
    ax.set_title(f"{title}  (band {dk['band'][0]:g}-{dk['band'][1]:g} GHz)",fontsize=12,fontweight="bold",color=INK)
    ax.set_xlabel("bandwidth used (GHz)",fontsize=10.5); ax.set_ylabel("best-achievable error (mm)",fontsize=10.5)
    ax.set_ylim(0,max(mm(dk["chanceIn"])*1.05, bc[:,1].max()*1.2))
    ax.grid(True,color="#EAF0F4",lw=0.7); ax.set_axisbelow(True); ax.legend(fontsize=9,framealpha=0.95,loc="lower right")
    for s in ax.spines.values(): s.set_color("#D8E2EA")
fig.suptitle("Bandwidth knee: does the trained CNN agree with the k-NN signal floor?",
             fontsize=15,fontweight="bold",color=INK,y=0.985)
fig.text(0.5,0.945,"best center at each width, leave-one-position-out CV (same data/folds for both models)",
         ha="center",fontsize=10.5,color=MUTE)
fig.text(0.5,0.012,"Measured (empty/F4/F5): CNN confirms a narrow ~1-3 GHz band is as good as the full sweep. Sim: only 340 samples, so the "
         "CNN is data-starved\nand noisier than the training-free k-NN; the k-NN low-band sweet spot is the more reliable read for sim.",
         ha="center",fontsize=9.7,color=MUTE,style="italic")
fig.subplots_adjust(left=0.07,right=0.98,top=0.90,bottom=0.11,hspace=0.34,wspace=0.20)
p=os.path.join(HERE,"bw_cnn_vs_knn.png"); fig.savefig(p,dpi=160); print("wrote",os.path.basename(p))
