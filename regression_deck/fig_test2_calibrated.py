"""Deck 3 - Test 2: baseline-calibrated sim -> measured transfer.

Left: measured median (x,y) error for the sim-trained CNN, uncalibrated (Test 1,
antenna permutation only) vs calibrated (the learned linear sim->measured map
applied to the sim tumor signal), against the predict-centre chance line.
Right: the calibrated model's predictions on measured data.
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse

CRIMSON="#BE0000"; GOLD="#C8890B"; GREEN="#2E7D5B"; INK="#1E293B"; MUTE="#5B6B7B"; OUT_C="#3A2A28"; TRUE_C="#2C5F7C"
HERE=os.path.dirname(__file__)
d=np.load(os.path.join(HERE,"..","results","test2_calibrated_sim2meas.npz"))
mm=lambda x:float(x)*25.4
ch,zu,zc,r2=mm(d["chance"]),mm(d["zs_u"]),mm(d["zs_c"]),float(d["r2"])
t=d["meas_true"]; p=d["pred_cal"]
BOWL=(3.124,3.028); RX=1.901; RY=3.233
better = zc < zu

fig,(a1,a2)=plt.subplots(1,2,figsize=(12.6,5.6))
# ---- bars
labels=["chance\n(predict centre)","uncalibrated\n(Test 1, perm only)","CALIBRATED\n(learned map)"]
vals=[ch,zu,zc]; cols=[MUTE,"#9AA6B2",CRIMSON if not better else GREEN]
bars=a1.bar(labels,vals,color=cols,width=0.62,edgecolor="k",linewidth=0.5)
for b,v in zip(bars,vals): a1.text(b.get_x()+b.get_width()/2,v+1,f"{v:.0f} mm",ha="center",va="bottom",fontsize=12,fontweight="bold",color=INK)
a1.axhline(ch,color=MUTE,ls="--",lw=1.2,zorder=0)
a1.set_ylabel("measured median (x,y) error (mm)",fontsize=12); a1.set_ylim(0,max(vals)*1.18)
ttl = "Calibration recovers accuracy" if better else "Linear calibration is not enough"
a1.set_title(ttl,fontsize=13,fontweight="bold",color=INK)
a1.grid(True,axis="y",color="#EAF0F4",lw=0.7); a1.set_axisbelow(True)
for s in a1.spines.values(): s.set_color("#D8E2EA")

# ---- spatial (calibrated predictions on measured)
a2.add_patch(Ellipse(BOWL,2*RX,2*RY,fill=False,edgecolor=OUT_C,lw=1.5,zorder=1))
for i in range(len(t)):
    a2.annotate("",xy=(p[i,0],p[i,1]),xytext=(t[i,0],t[i,1]),
                arrowprops=dict(arrowstyle="->",color="#C9B3AE",lw=0.7,alpha=0.6),zorder=2)
a2.scatter(t[:,0],t[:,1],s=55,facecolors="none",edgecolors=TRUE_C,linewidths=1.5,zorder=3,label="true position")
a2.scatter(p[:,0],p[:,1],s=42,c=CRIMSON,marker="D",edgecolors="white",linewidths=0.4,zorder=4,label="calibrated prediction")
a2.set_aspect("equal"); a2.set_xlim(-0.2,6.6); a2.set_ylim(6.6,-0.2)
a2.set_xlabel("X (in)",fontsize=11); a2.set_ylabel("Y (in)",fontsize=11)
a2.set_title("Calibrated predictions on the bench",fontsize=13,fontweight="bold",color=INK)
a2.grid(True,color="#EAF0F4",lw=0.6); a2.set_axisbelow(True)
a2.legend(loc="lower right",fontsize=9,framealpha=0.95)
for s in a2.spines.values(): s.set_color("#D8E2EA")

fig.suptitle(f"Test 2: calibrate the sim toward the bench (empty-baseline map, R2 = {r2:.2f}), then transfer",
             fontsize=14,fontweight="bold",color=INK,y=0.99)
if better:
    msg=(f"The learned linear map is applied to the simulated tumor signal before training. Direct (uncalibrated) transfer sat at {zu:.0f} mm; "
         f"after calibration\nthe sim-trained CNN reaches {zc:.0f} mm on the bench"
         + (f", now beating the {ch:.0f} mm chance line" if zc<ch else f", closing toward the {ch:.0f} mm chance line")
         + ". A single empty-baseline\ncalibration already recovers much of the gap, without ever training on a measured tumor.")
else:
    msg=(f"The learned linear map is applied to the simulated tumor signal before training. It does not close the gap: calibrated transfer is {zc:.0f} mm "
         f"vs {zu:.0f} mm\nuncalibrated, both above the {ch:.0f} mm chance line. A single empty-baseline linear map is too weak; per-row normalization removes its amplitude\n"
         "effect, and the remaining domain gap needs paired tumor data or nonlinear adaptation.")
fig.text(0.5,0.01,msg,ha="center",va="bottom",fontsize=10.0,color=MUTE,style="italic")
fig.subplots_adjust(left=0.07,right=0.98,top=0.90,bottom=0.20,wspace=0.20)
pth=os.path.join(HERE,"test2_calibrated_sim2meas.png")
fig.savefig(pth,dpi=160); print("wrote",pth)
