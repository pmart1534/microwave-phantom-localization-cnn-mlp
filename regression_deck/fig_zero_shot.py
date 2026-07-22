"""Deck 3 - zero-shot sim -> measured: direct transfer collapses.

Left: median (x,y) error for the CNN trained on simulated tumor dS, evaluated on
held-out SIM (in-domain), a predict-centre chance baseline, and the MEASURED set
(zero-shot). Right: the zero-shot predictions on measured data collapse to a
small biased region, far from the true positions.
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
from matplotlib.lines import Line2D

CRIMSON="#BE0000"; GOLD="#C8890B"; GREEN="#2E7D5B"; INK="#1E293B"; MUTE="#5B6B7B"; OUT_C="#3A2A28"; TRUE_C="#2C5F7C"
HERE=os.path.dirname(__file__)
# unified experiment (Test 1 = the uncalibrated path of test2_calibrated_sim2meas)
d=np.load(os.path.join(HERE,"..","results","test2_calibrated_sim2meas.npz"))
he,zs,ch=float(d["he_u"])*25.4,float(d["zs_u"])*25.4,float(d["chance"])*25.4
t=d["meas_true"]; p=d["pred_uncal"]
BOWL=(3.124,3.028); RX=1.901; RY=3.233

fig,(a1,a2)=plt.subplots(1,2,figsize=(12.6,5.6))
# bars
bars=a1.bar(["in-domain\n(sim -> held-out sim)","chance\n(predict centre)","ZERO-SHOT\n(sim -> measured)"],
            [he,ch,zs],color=[GREEN,MUTE,CRIMSON],width=0.62,edgecolor="k",linewidth=0.5)
for b,v in zip(bars,[he,ch,zs]): a1.text(b.get_x()+b.get_width()/2,v+1,f"{v:.0f} mm",ha="center",va="bottom",fontsize=12,fontweight="bold",color=INK)
a1.set_ylabel("median (x,y) error (mm)",fontsize=12); a1.set_ylim(0,zs*1.18)
a1.axhline(ch,color=MUTE,ls="--",lw=1.2,zorder=0)
a1.set_title("Direct transfer is worse than chance",fontsize=13,fontweight="bold",color=INK)
a1.grid(True,axis="y",color="#EAF0F4",lw=0.7); a1.set_axisbelow(True)
for s in a1.spines.values(): s.set_color("#D8E2EA")

# spatial collapse
a2.add_patch(Ellipse(BOWL,2*RX,2*RY,fill=False,edgecolor=OUT_C,lw=1.5,zorder=1))
for i in range(len(t)):
    a2.annotate("",xy=(p[i,0],p[i,1]),xytext=(t[i,0],t[i,1]),
                arrowprops=dict(arrowstyle="->",color="#C9B3AE",lw=0.7,alpha=0.6),zorder=2)
a2.scatter(t[:,0],t[:,1],s=55,facecolors="none",edgecolors=TRUE_C,linewidths=1.5,zorder=3,label="true position")
a2.scatter(p[:,0],p[:,1],s=42,c=CRIMSON,marker="D",edgecolors="white",linewidths=0.4,zorder=4,label="zero-shot prediction")
a2.set_aspect("equal"); a2.set_xlim(-0.2,6.6); a2.set_ylim(6.6,-0.2)
a2.set_xlabel("X (in)",fontsize=11); a2.set_ylabel("Y (in)",fontsize=11)
a2.set_title("Predictions collapse to a biased region",fontsize=13,fontweight="bold",color=INK)
a2.grid(True,color="#EAF0F4",lw=0.6); a2.set_axisbelow(True)
a2.legend(loc="lower right",fontsize=9,framealpha=0.95)
for s in a2.spines.values(): s.set_color("#D8E2EA")

fig.suptitle("Zero-shot sim to measured: the CNN localizes sim, but direct transfer fails",
             fontsize=14,fontweight="bold",color=INK,y=0.99)
fig.text(0.5,0.01,
   "Trained only on simulated tumor dS, the CNN localizes held-out sim positions (15 mm), but applied directly to measured data its predictions "
   "collapse\nto a small biased region (worse than chance). The measured S-parameters are out-of-distribution relative to sim: the antenna domain gap "
   "breaks direct transfer.\nThis motivates calibrating the sim toward the bench (next test).",
   ha="center",va="bottom",fontsize=10.0,color=MUTE,style="italic")
fig.subplots_adjust(left=0.07,right=0.98,top=0.90,bottom=0.20,wspace=0.20)
pth=os.path.join(HERE,"zero_shot_sim2meas.png")
fig.savefig(pth,dpi=160); print("wrote",pth)
