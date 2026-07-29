"""Bandwidth requirement for the (x,y) regression localizer.

Reads results/bw_sweep_reg_{empty,F4,F5,sim}.json (k-NN signal-floor sweep,
leave-one-position-out CV) and makes three figures:
  bw_knee.png    - best-achievable error vs bandwidth, per config (the headline)
  bw_heatmap.png - center x width error heatmaps (where the good bands are)
  bw_tones.png   - error vs number of discrete tones (a multi-tone chip)

k-NN is a RELATIVE signal-floor probe used to locate the informative band; it is
not the absolute achievable accuracy (the CNN does better and is confirmed
separately). Read the shape, not the mm.
"""
import os, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CRIMSON="#BE0000"; GOLD="#C8890B"; GREEN="#2E7D5B"; INK="#1E293B"; MUTE="#5B6B7B"; TEAL="#2C5F7C"
HERE=os.path.dirname(__file__); RES=os.path.join(HERE,"..","results")
DS=[("empty","A3 empty (metal target)",TEAL),("F4","A3 F4 gland",GOLD),
    ("F5","A3 F5 gland",CRIMSON),("sim","Simulated metal",GREEN)]
mm=lambda x:x*25.4
def load(ds): return json.load(open(os.path.join(RES,f"bw_sweep_reg_{ds}.json")))

def best_per_width(dr):
    ws=sorted(set(r["width"] for r in dr)); out=[]
    for w in ws:
        cw=[r for r in dr if abs(r["width"]-w)<1e-6]; b=min(cw,key=lambda r:r["err"])
        out.append((w,mm(b["err"]),b["center"]))
    return out

# ---------------- FIG 1: knee (best-achievable vs bandwidth) ----------------
fig,axs=plt.subplots(2,2,figsize=(11.6,8.2))
for ax,(ds,title,col) in zip(axs.ravel(),DS):
    d=load(ds); bw=best_per_width(d["dense_knn"])
    ws=[b[0] for b in bw]; er=[b[1] for b in bw]
    ax.plot(ws,er,"-o",color=col,lw=2.2,ms=6,zorder=3)
    for w,e,c in bw: ax.annotate(f"{c:g}",(w,e),textcoords="offset points",xytext=(0,8),
                                 ha="center",fontsize=7.5,color=MUTE)
    ax.axhline(mm(d["chanceIn"]),color=MUTE,ls="--",lw=1.2,zorder=1)
    ax.text(ws[-1],mm(d["chanceIn"]),"  chance",va="center",fontsize=8.5,color=MUTE)
    ax.set_title(f"{title}   (band {d['band'][0]:g}-{d['band'][1]:g} GHz)",fontsize=12,fontweight="bold",color=INK)
    ax.set_xlabel("bandwidth used (GHz)",fontsize=10.5); ax.set_ylabel("best-achievable error (mm)",fontsize=10.5)
    ax.set_ylim(0,max(mm(d["chanceIn"])*1.05,max(er)*1.25)); ax.grid(True,color="#EAF0F4",lw=0.7); ax.set_axisbelow(True)
    for s in ax.spines.values(): s.set_color("#D8E2EA")
fig.suptitle("How much bandwidth does the regression localizer need?",
             fontsize=15,fontweight="bold",color=INK,y=0.985)
fig.text(0.5,0.945,"k-NN signal floor, best center at each width; number by each point = that band's best center (GHz)",
         ha="center",fontsize=10.5,color=MUTE)
fig.text(0.5,0.012,"Best-achievable error is nearly flat down to ~1-1.5 GHz for every config (empty is flat to <0.5 GHz): the localization\n"
         "information sits in the low-mid band, so a narrow front end suffices.",ha="center",fontsize=10,color=MUTE,style="italic")
fig.subplots_adjust(left=0.07,right=0.98,top=0.90,bottom=0.11,hspace=0.34,wspace=0.20)
fig.savefig(os.path.join(HERE,"bw_knee.png"),dpi=160); print("wrote bw_knee.png")

# ---------------- FIG 2: center x width heatmaps ----------------
fig,axs=plt.subplots(2,2,figsize=(11.8,8.4))
for ax,(ds,title,col) in zip(axs.ravel(),DS):
    d=load(ds); dr=d["dense_knn"]
    ws=sorted(set(r["width"] for r in dr))
    cs=sorted(set(r["center"] for r in dr))
    Z=np.full((len(ws),len(cs)),np.nan)
    for r in dr:
        Z[ws.index(r["width"]),cs.index(r["center"])]=mm(r["err"])
    im=ax.imshow(Z,aspect="auto",origin="lower",cmap="RdYlGn_r",
                 extent=[min(cs),max(cs),0,len(ws)],vmin=np.nanmin(Z),vmax=np.nanpercentile(Z,95))
    ax.set_yticks(np.arange(len(ws))+0.5); ax.set_yticklabels([f"{w:g}" for w in ws],fontsize=8.5)
    # mark best cell
    bi=np.unravel_index(np.nanargmin(Z),Z.shape); ax.plot(cs[bi[1]],bi[0]+0.5,"*",color="black",ms=14,mec="white",mew=0.8)
    ax.set_title(f"{title}  (best {np.nanmin(Z):.1f}mm)",fontsize=11.5,fontweight="bold",color=INK)
    ax.set_xlabel("center frequency (GHz)",fontsize=10); ax.set_ylabel("width (GHz)",fontsize=10)
    plt.colorbar(im,ax=ax,fraction=0.046,pad=0.03,label="error (mm)")
fig.suptitle("Localization error by band (center x width) - dark red = worse; star = best band",
             fontsize=13,fontweight="bold",color=INK,y=0.995)
fig.subplots_adjust(left=0.06,right=0.98,top=0.93,bottom=0.07,hspace=0.30,wspace=0.22)
fig.savefig(os.path.join(HERE,"bw_heatmap.png"),dpi=160); print("wrote bw_heatmap.png")

# ---------------- FIG 3: tones ----------------
fig,ax=plt.subplots(figsize=(8.6,5.4))
for ds,title,col in DS:
    d=load(ds); tn=d.get("tones_knn",[])
    if not tn: continue
    ns=[t["n"] for t in tn]; er=[mm(t["err"]) for t in tn]
    ax.plot(ns,er,"-o",color=col,lw=2,ms=5,label=title)
ax.set_xlabel("number of discrete tones (greedy-selected)",fontsize=11)
ax.set_ylabel("k-NN localization error (mm)",fontsize=11)
ax.set_title("A few discrete tones already localize well (multi-tone chip)",fontsize=12.5,fontweight="bold",color=INK)
ax.grid(True,color="#EAF0F4",lw=0.7); ax.set_axisbelow(True); ax.legend(fontsize=9.5,framealpha=0.95)
for s in ax.spines.values(): s.set_color("#D8E2EA")
fig.tight_layout(); fig.savefig(os.path.join(HERE,"bw_tones.png"),dpi=160); print("wrote bw_tones.png")
