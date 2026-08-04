"""Sim CNN lateral error: band (full vs 2-4 GHz) x protocol (deck random k-fold vs
strict (x,y)-disjoint), tuned MATLAB GPU CNN. Reconciles the deck's ~3.9 mm with
the honest strict-split numbers. Reads results/cnn_simreg_*_bwtest.json.
"""
import os, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CRIMSON="#BE0000"; GREEN="#2E7D5B"; INK="#1E293B"; MUTE="#5B6B7B"; GOLD="#C8890B"
HERE=os.path.dirname(__file__); RES=os.path.join(HERE,"..","results")
def lat(tag): return json.load(open(os.path.join(RES,f"cnn_simreg_{tag}.json")))["lateral_medianMm"]

A=lat("8fold_nf256_5mmgrid_bwtest")          # random kfold, full
B=lat("8fold_nf256_5mmgrid_b2-4_bwtest")     # random kfold, 2-4
C=lat("8foldXY_nf256_5mmgrid_bwtest")        # strict xy, full
D=lat("8foldXY_nf256_5mmgrid_b2-4_bwtest")   # strict xy, 2-4

fig,ax=plt.subplots(figsize=(8.8,5.6))
groups=["random k-fold\n(deck protocol: leaky)","strict (x,y)-disjoint\n(honest: unseen position)"]
full=[A,C]; narrow=[B,D]
x=np.arange(2); w=0.36
b1=ax.bar(x-w/2,full,w,label="full band 2-8 GHz",color=GREEN,edgecolor="k",linewidth=0.5)
b2=ax.bar(x+w/2,narrow,w,label="2-4 GHz",color=GOLD,edgecolor="k",linewidth=0.5)
for bars in (b1,b2):
    for bb in bars: ax.text(bb.get_x()+bb.get_width()/2,bb.get_height()+0.15,f"{bb.get_height():.1f}",
                            ha="center",va="bottom",fontsize=12,fontweight="bold",color=INK)
ax.axhline(2.9,color=CRIMSON,ls="--",lw=1.3)
ax.text(1.48,2.9,"measured CNN @2-4GHz (2.9mm)",ha="right",va="bottom",fontsize=8.5,color=CRIMSON)
ax.set_xticks(x); ax.set_xticklabels(groups,fontsize=11)
ax.set_ylabel("sim lateral (x,y) error, median (mm)",fontsize=11.5)
ax.set_ylim(0,11); ax.legend(fontsize=10,framealpha=0.95,loc="upper left")
ax.set_title("Simulated CNN lateral error: band x cross-validation protocol",fontsize=13,fontweight="bold",color=INK)
ax.grid(True,axis="y",color="#EAF0F4",lw=0.7); ax.set_axisbelow(True)
for s in ax.spines.values(): s.set_color("#D8E2EA")
fig.text(0.5,0.005,
    "Simulated CNN median lateral error (mm), full 2-8 GHz vs 2-4 GHz band, under random 8-fold vs strict (x,y)-disjoint 8-fold CV.\n"
    "Dashed line = measured empty CNN at 2-4 GHz (2.9 mm).",
    ha="center",fontsize=9,color=MUTE,style="italic")
fig.subplots_adjust(left=0.10,right=0.97,top=0.91,bottom=0.20)
fig.savefig(os.path.join(HERE,"sim_band_protocol.png"),dpi=160); print("wrote sim_band_protocol.png")
