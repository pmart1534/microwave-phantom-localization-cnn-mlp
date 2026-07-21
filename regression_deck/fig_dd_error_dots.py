"""Regression analog of the classification DD-accuracy dot plot.

Classification deck: dot COLOR = detectable difference (DD), dot SIZE = accuracy;
accuracy tracked DD (signal strength / antenna proximity). Here, for the
regression LOPO-cell error: dot COLOR = DD, dot SIZE = error distance (bigger =
worse). If regression error tracked DD like classification, the big dots would
sit on the cold (blue, low-DD) points. Instead they sit at the grid EDGES and
over the insert, showing edge/extrapolation geometry dominates, not DD.
"""
import os, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Polygon
from matplotlib.lines import Line2D

INK="#1E293B"; MUTE="#5B6B7B"; OUT_C="#3A2A28"
HERE=os.path.dirname(__file__)
RES=os.path.join(HERE,"..","results")
DDDIR=r"C:\Users\peter\Desktop\EM Imaging\Research Paper\github_repo\detectable_change\A3_hunter\results"

BOWL=(3.124,3.028); RX=1.901; RY=3.233
from make_pred_vs_actual import A3_F4_OUTLINE, A3_F5_OUTLINE
OUTLINES={"F4":A3_F4_OUTLINE,"F5":A3_F5_OUTLINE}

PH=[("Empty","cnn_reglopo_pooled_cell_June18_remap_raw.json","detectable_diff_A3_Empty.npz","empty"),
    ("F4 insert","cnn_reglopo_pooled_cell_A3_F4_SamMed_all4_raw.json","detectable_diff_A3_F4.npz","F4"),
    ("F5 insert","cnn_reglopo_pooled_cell_A3_F5_SamMed_last3_raw.json","detectable_diff_A3_F5.npz","F5")]

fig,axes=plt.subplots(1,3,figsize=(13.4,6.0))
sc=None
for ax,(ttl,resf,ddf,kind) in zip(axes,PH):
    r=json.load(open(os.path.join(RES,resf)))
    pp=[e for e in r["perPosition"] if e.get("medianErrIn") is not None]
    x=np.array([e["x"] for e in pp]); y=np.array([e["y"] for e in pp])
    err=np.array([e["medianErrIn"] for e in pp])
    dd=np.load(os.path.join(DDDIR,ddf),allow_pickle=True)["rows_MAX"]
    ddx=np.array([float(rr[1]) for rr in dd]); ddy=np.array([float(rr[2]) for rr in dd])
    dddb=np.array([float(rr[3]) for rr in dd])
    # match each result position to nearest DD position
    ddval=np.array([dddb[np.argmin((ddx-xi)**2+(ddy-yi)**2)] for xi,yi in zip(x,y)])
    # outlines
    ax.add_patch(Ellipse(BOWL,2*RX,2*RY,fill=False,edgecolor=OUT_C,lw=1.4,zorder=1))
    if kind in OUTLINES:
        ax.add_patch(Polygon(OUTLINES[kind],closed=True,fill=True,facecolor=OUT_C,alpha=0.06,zorder=1))
        ax.add_patch(Polygon(OUTLINES[kind],closed=True,fill=False,edgecolor=OUT_C,lw=1.4,linestyle=(0,(4,2)),zorder=2))
    sizes=30+320*np.clip(err,0,1.0)              # dot size ∝ error (clipped at 1 in)
    rho=np.corrcoef(err,ddval)[0,1]
    sc=ax.scatter(x,y,c=ddval,s=sizes,cmap="jet",vmin=-48,vmax=-30,
                  edgecolor="k",linewidth=0.4,alpha=0.72,zorder=3)
    ax.set_title(f"{ttl}\nmed {np.median(err):.2f} in   corr(err,DD)={rho:+.2f}",fontsize=12,fontweight="bold",color=INK)
    ax.set_aspect("equal"); ax.set_xlim(-0.2,6.6); ax.set_ylim(6.6,-0.2)
    ax.set_xlabel("X (in)",fontsize=10.5)
    if ax is axes[0]: ax.set_ylabel("Y (in)",fontsize=10.5)
    ax.grid(True,color="#EAF0F4",lw=0.6); ax.set_axisbelow(True)
    for s in ax.spines.values(): s.set_color("#D8E2EA")

cb=fig.colorbar(sc,ax=axes,shrink=0.7,pad=0.015,location="right")
cb.set_label("detectable difference (dB)  [dot COLOR]",fontsize=10)
# size legend
handles=[Line2D([0],[0],marker="o",color="w",markerfacecolor="#888",markeredgecolor="k",
                markersize=np.sqrt(30+320*e),label=f"{e:.1f} in") for e in (0.2,0.5,0.9)]
axes[0].legend(handles=handles,title="error (dot SIZE)",loc="lower left",fontsize=8,title_fontsize=8.5,framealpha=0.95,labelspacing=1.4)

fig.suptitle("Regression error vs. detectable difference (dot size = error, color = DD)",
             fontsize=14.5,fontweight="bold",color=INK,y=0.99)
fig.text(0.5,0.02,
   "Dot color (DD) does not track dot size (error): the correlation is weak and inconsistent (empty -0.18, F4 -0.47, F5 +0.15). "
   "Unlike classification,\nwhere accuracy followed signal strength, regression error is driven by geometry: grid edges (F5 edge error ~2.5x interior) and the insert barrier.",
   ha="center",va="bottom",fontsize=9.6,color=MUTE,style="italic")
fig.subplots_adjust(left=0.05,right=0.9,top=0.88,bottom=0.15,wspace=0.16)
p=os.path.join(HERE,"dd_vs_error_dots.png")
fig.savefig(p,dpi=160); print("wrote",p)
