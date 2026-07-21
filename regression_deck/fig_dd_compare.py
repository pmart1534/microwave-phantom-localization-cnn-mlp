"""Deck 3 - detectable-difference (DD) pattern, measured vs simulated (empty).

Measured DD comes straight from the detectable_change program's output
(detectable_diff_A3_Empty.npz: max over S-parameters of the tumor differential,
in dB, per position). Sim DD is the same statistic computed on the HFSS sweep at
z=+15 mm (the near-patch depth that matches the bench data). Both are drawn as
color dot maps in the same physical (mm) frame with the phantom bowl, so the
spatial pattern can be compared.
"""
import os, glob, re, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse

INK="#1E293B"; MUTE="#5B6B7B"; OUT_C="#3A2A28"
HERE=os.path.dirname(__file__)
SIMDIR=r"C:\Users\peter\Desktop\EM Imaging\Simulation Data\SamMakin"
A3H=r"C:\Users\peter\Desktop\EM Imaging\Research Paper\github_repo\detectable_change\A3_hunter\results\detectable_diff_A3_Empty.npz"
SIMDATA=os.path.join(SIMDIR,"Data Results","A3_Metal_1cm")

# ---- bowl (grid-inch -> local mm) and inch->mm helpers ----
def in2mm(x,y): return 25.4*x, 145.9-23.85*y
BC=in2mm(3.124,3.028); bowl_w=2*25.4*1.901; bowl_h=2*23.85*3.233
def bowl(ax): ax.add_patch(Ellipse(BC,bowl_w,bowl_h,fill=False,edgecolor=OUT_C,lw=1.6,zorder=1))

# ---- measured DD from the program's npz ----
d=np.load(A3H, allow_pickle=True); rows=d["rows_MAX"]
mx=np.array([in2mm(float(r[1]),float(r[2]))[0] for r in rows])
my=np.array([in2mm(float(r[1]),float(r[2]))[1] for r in rows])
mdd=np.array([float(r[3]) for r in rows])

# ---- sim DD at +15 mm ----
def read_s4p(path):
    vals=[]; sc=1e9
    for line in open(path):
        s=line.strip()
        if not s or s.startswith("!"): continue
        if s.startswith("#"):
            sc=1e6 if " mhz" in s.lower() else 1e9; continue
        vals.extend(float(t) for t in s.split())
    v=np.asarray(vals); per=1+2*16; nf=len(v)//per; v=v[:nf*per].reshape(nf,per)
    b=v[:,1:].reshape(nf,16,2); return b[:,:,0]*np.exp(1j*np.deg2rad(b[:,:,1]))
_,=(0,)
base=read_s4p(os.path.join(SIMDATA,"baseline_empty_b1_2.s4p"))
sx=[]; sy=[]; sdd=[]
for f in glob.glob(os.path.join(SIMDATA,"P*DenseZ15_*.s4p")):
    m=re.search(r"Xm?(-?\d+p?\d*)_Ym?(-?\d+p?\d*)", os.path.basename(f))
    # parse tumor x,y from filename (X..._Y...); use json sidecar for reliability
    js=f[:-4]+".json"
    if not os.path.exists(js): continue
    meta=json.load(open(js)); x=meta["tumor_x_mm"]; y=meta["tumor_y_mm"]
    S=read_s4p(f)
    if S.shape!=base.shape: continue
    dd=np.max(np.abs(S-base))
    sx.append(x); sy.append(y); sdd.append(20*np.log10(max(dd,1e-6)))
sx=np.array(sx); sy=np.array(sy); sdd=np.array(sdd)

# register sim -> local mm via grid_placed_global
gl=[l.split(",") for l in open(os.path.join(SIMDIR,"grid_placed_global.csv")).read().splitlines()[1:]]
gsim=np.array([[float(r[3]),float(r[4])] for r in gl]); gloc=np.array([[float(r[1]),float(r[2])] for r in gl])
M=np.column_stack([gsim,np.ones(len(gsim))])
cx=np.linalg.lstsq(M,gloc[:,0],rcond=None)[0]; cy=np.linalg.lstsq(M,gloc[:,1],rcond=None)[0]
slx=cx[0]*sx+cx[1]*sy+cx[2]; sly=cy[0]*sx+cy[1]*sy+cy[2]
print(f"measured DD: {len(mdd)} pos, {mdd.min():.0f}..{mdd.max():.0f} dB | sim DD: {len(sdd)} pos, {sdd.min():.0f}..{sdd.max():.0f} dB")

fig,(a1,a2)=plt.subplots(1,2,figsize=(12.4,6.0))
for ax,(X,Y,DD,ttl) in [(a1,(mx,my,mdd,"MEASURED  (bench VNA, empty)")),
                        (a2,(slx,sly,sdd,"SIMULATED  (HFSS, empty, z=+15 mm)"))]:
    bowl(ax)
    sc=ax.scatter(X,Y,c=DD,s=150,cmap="jet",vmin=np.percentile(DD,5),vmax=np.percentile(DD,95),
                  edgecolor="k",linewidth=0.4,zorder=3)
    cb=fig.colorbar(sc,ax=ax,shrink=0.82,pad=0.02); cb.set_label("max detectable change (dB)",fontsize=10)
    ax.set_title(ttl,fontsize=12.5,fontweight="bold",color=INK)
    ax.set_aspect("equal"); ax.set_xlabel("x (mm)",fontsize=10.5); ax.set_ylabel("y (mm)",fontsize=10.5)
    ax.grid(True,color="#EAF0F4",lw=0.6); ax.set_axisbelow(True)
    for s in ax.spines.values(): s.set_color("#D8E2EA")

fig.suptitle("Detectable-difference pattern, measured vs simulated (empty phantom)",
             fontsize=14.5,fontweight="bold",color=INK,y=0.99)
fig.text(0.5,0.01,
   "Both show the tumor's detectable change as a color map (max over S-parameters, per position). Absolute dB differs "
   "(different antennas\nand noise), but the SPATIAL pattern is similar: the change is strongest toward the antenna sides and weaker in the middle.",
   ha="center",va="bottom",fontsize=10.0,color=MUTE,style="italic")
fig.subplots_adjust(left=0.06,right=0.98,top=0.90,bottom=0.15,wspace=0.20)
p=os.path.join(HERE,"dd_measured_vs_sim.png")
fig.savefig(p,dpi=160); print("wrote",p)
