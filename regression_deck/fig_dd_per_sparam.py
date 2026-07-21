"""Deck 3 - per-S-parameter detectable-difference maps, measured and simulated.

Shows how specific ANTENNAS drive the pattern: reflection Sii is strongest near
antenna i.

METHODS (different by necessity):
  - Measured DD = the detectable_change program's metric (detdifplot): the 95%
    confidence-interval gap between baseline and object-present distributions
    over the 16 repeat takes, band-averaged and in dB. From the program's npz.
  - Simulated DD = |dS| = |S_tumor - S_empty| directly (band-averaged, dB): the
    solve is deterministic with an exact baseline, so there is no distribution
    and the CI-gap collapses to the plain differential.
Both drawn in grid-inch coordinates with the phantom bowl and the 4 antennas.
"""
import os, glob, re, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Rectangle

INK="#1E293B"; MUTE="#5B6B7B"; OUT_C="#3A2A28"
HERE=os.path.dirname(__file__)
A3H=r"C:\Users\peter\Desktop\EM Imaging\Research Paper\github_repo\detectable_change\A3_hunter\results\detectable_diff_A3_Empty.npz"
SIM=r"C:\Users\peter\Desktop\EM Imaging\Simulation Data\SamMakin\Data Results\A3_Metal_1cm"
GPG=r"C:\Users\peter\Desktop\EM Imaging\Simulation Data\SamMakin\grid_placed_global.csv"
ANT={1:(1.242,4.494),2:(1.237,1.636),3:(4.97,1.544),4:(5.002,4.587)}
BOWL=(3.124,3.028); RX=1.901; RY=3.233
REFL=["S11","S22","S33","S44"]; REFL_IDX={"S11":(0,0),"S22":(1,1),"S33":(2,2),"S44":(3,3)}

def draw(ax):
    ax.add_patch(Ellipse(BOWL,2*RX,2*RY,fill=False,edgecolor=OUT_C,lw=1.3,zorder=1))
    for n,(x,y) in ANT.items():
        ax.add_patch(Rectangle((x-0.13,y-0.22),0.26,0.44,facecolor="0.15",edgecolor="k",zorder=5))
        ax.text(x,y,str(n),ha="center",va="center",color="w",fontsize=7,fontweight="bold",zorder=6)
    ax.set_aspect("equal"); ax.set_xlim(-0.2,6.6); ax.set_ylim(6.6,-0.2)
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_color("#D8E2EA")

# ---- measured per-S-param DD from the program's npz ----
d=np.load(A3H,allow_pickle=True); rows=d["rows_MAX"]; keys=[str(k) for k in d["sparam_keys"]]; avg=d["avg_lin"]
mx=np.array([float(r[1]) for r in rows]); my=np.array([float(r[2]) for r in rows])
def meas_dd(sp):
    col=keys.index(sp); lin=avg[:,col]
    return 20*np.log10(np.maximum(lin,1e-9))

# ---- sim per-S-param |dS| at z=+15 mm ----
def read_s4p(path):
    vals=[]; sc=1e9
    for line in open(path):
        s=line.strip()
        if not s or s.startswith("!"): continue
        if s.startswith("#"): sc=1e6 if " mhz" in s.lower() else 1e9; continue
        vals.extend(float(t) for t in s.split())
    v=np.asarray(vals); per=1+2*16; nf=len(v)//per; v=v[:nf*per].reshape(nf,per)
    b=v[:,1:].reshape(nf,16,2); return (b[:,:,0]*np.exp(1j*np.deg2rad(b[:,:,1]))).reshape(nf,4,4)
base=read_s4p(os.path.join(SIM,"baseline_empty_b1_2.s4p"))
gl=[l.split(",") for l in open(GPG).read().splitlines()[1:]]
gsim=np.array([[float(r[3]),float(r[4])] for r in gl]); gloc=np.array([[float(r[1]),float(r[2])] for r in gl])
M=np.column_stack([gsim,np.ones(len(gsim))]); cx=np.linalg.lstsq(M,gloc[:,0],rcond=None)[0]; cy=np.linalg.lstsq(M,gloc[:,1],rcond=None)[0]
sx=[]; sy=[]; sdd={sp:[] for sp in REFL}
for f in glob.glob(os.path.join(SIM,"P*DenseZ15_*.s4p")):
    js=f[:-4]+".json"
    if not os.path.exists(js): continue
    m=json.load(open(js)); S=read_s4p(f)
    if S.shape!=base.shape: continue
    lx=cx[0]*m["tumor_x_mm"]+cx[1]*m["tumor_y_mm"]+cx[2]; ly=cy[0]*m["tumor_x_mm"]+cy[1]*m["tumor_y_mm"]+cy[2]
    sx.append(lx/25.4); sy.append((145.9-ly)/23.85)
    dS=np.abs(S-base)
    for sp in REFL: i,j=REFL_IDX[sp]; sdd[sp].append(20*np.log10(max(np.mean(dS[:,i,j]),1e-9)))
sx=np.array(sx); sy=np.array(sy)

fig,axes=plt.subplots(2,4,figsize=(13.2,7.0))
for col,sp in enumerate(REFL):
    # measured (top)
    ax=axes[0,col]; draw(ax); v=meas_dd(sp)
    sc=ax.scatter(mx,my,c=v,s=90,cmap="jet",vmin=np.percentile(v,5),vmax=np.percentile(v,95),edgecolor="k",linewidth=0.3,zorder=3)
    ax.set_title(sp,fontsize=13,fontweight="bold",color=INK)
    if col==0: ax.text(-0.13,0.5,"MEASURED",transform=ax.transAxes,rotation=90,va="center",ha="center",fontsize=12,fontweight="bold",color=INK)
    # sim (bottom)
    ax=axes[1,col]; draw(ax); v=np.array(sdd[sp])
    ax.scatter(sx,sy,c=v,s=70,cmap="jet",vmin=np.percentile(v,5),vmax=np.percentile(v,95),edgecolor="k",linewidth=0.3,zorder=3)
    if col==0: ax.text(-0.13,0.5,"SIMULATED",transform=ax.transAxes,rotation=90,va="center",ha="center",fontsize=12,fontweight="bold",color=INK)

fig.suptitle("Per-antenna reflection: detectable difference by S-parameter (each Sii peaks near antenna i)",
             fontsize=14,fontweight="bold",color=INK,y=0.99)
fig.text(0.5,0.01,
   "Each reflection Sii localizes near an antenna in both domains (color = detectable difference, dB), confirming the expected physics. "
   "Sim and measured use\nindependent port numbering, so Sii maps to its own antenna within each domain. Measured DD = 95% CI-gap over the 16 repeat takes "
   "(detdifplot);\nsimulated DD = |dS| directly (deterministic solve, no confidence interval). Colour is scaled per panel.",
   ha="center",va="bottom",fontsize=9.4,color=MUTE,style="italic")
fig.subplots_adjust(left=0.03,right=0.99,top=0.92,bottom=0.10,hspace=0.12,wspace=0.06)
p=os.path.join(HERE,"dd_per_sparam.png")
fig.savefig(p,dpi=160); print("wrote",p)
