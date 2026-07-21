"""Deck 3 - sim 1 cm uniform grid vs the physical measurement grid, plus an
overlay of the two in a common physical frame.

Left  : simulated tumor positions (uniform 10 mm lattice).
Middle: the physical 6x6 cell grid (placement_grid_6x6.csv) with the traced A3
        phantom bowl; measured sub-positions filled.
Right : both grids registered into the same physical (mm) frame via
        grid_placed_global.csv, with the phantom bowl.
"""
import os, glob, re, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse

BLUE="#0B5D7A"; TEAL="#1C9AA8"; CRIMSON="#BE0000"; INK="#1E293B"; MUTE="#5B6B7B"; OUT_C="#3A2A28"
HERE=os.path.dirname(__file__)
SIMDIR=r"C:\Users\peter\Desktop\EM Imaging\Simulation Data\SamMakin"
GRID=os.path.join(SIMDIR,"placement_grid_6x6.csv")
GPG =os.path.join(SIMDIR,"grid_placed_global.csv")
SESS=r"C:\Users\peter\Desktop\EM Imaging\BreastPhantom\HunterVNA\DataMeasurements\Sam Antennas\MediumAntenna\Separated\June18\BreastPhantom_A3_FishingWeight_20260618_1530"

# ---- sim lattice (unique xy in sim-mm frame) ----
pp = json.load(open(os.path.join(HERE,"..","results","cnn_simreg_8fold_nf256_5mmgrid.json")))["perPosition"]
sxy = np.array(sorted({(round(p["x"],1), round(p["y"],1)) for p in pp}))
sim_x, sim_y = sxy[:,0], sxy[:,1]

# ---- physical grid (local mm) ----
labels=[]; px=[]; py=[]
for ln in open(GRID).read().splitlines()[1:]:
    lab,x,y=ln.split(","); labels.append(lab); px.append(float(x)); py.append(float(y))
px=np.array(px); py=np.array(py)

# measured sub-positions (map RnCmPp -> HxVyCz)
CORNER={"P1":"C1","P2":"C2","P3":"C4","P4":"C3"}
meas=set()
for f in glob.glob(os.path.join(SESS,"R*C*P*_T01.csv")):
    m=re.match(r"R(\d+)C(\d+)P(\d)", os.path.basename(f))
    if m: r,c,p=m.groups(); meas.add(f"H{c}V{r}{CORNER['P'+p]}")
mm=np.array([lab in meas for lab in labels])

# ---- registration: fit affine sim-mm -> local-mm from grid_placed_global ----
gl_sim=[]; gl_loc=[]
for ln in open(GPG).read().splitlines()[1:]:
    parts=ln.split(",");
    gl_loc.append([float(parts[1]),float(parts[2])]); gl_sim.append([float(parts[3]),float(parts[4])])
gl_sim=np.array(gl_sim); gl_loc=np.array(gl_loc)
M=np.column_stack([gl_sim, np.ones(len(gl_sim))])          # [sx, sy, 1]
cx,_,_,_=np.linalg.lstsq(M, gl_loc[:,0], rcond=None)
cy,_,_,_=np.linalg.lstsq(M, gl_loc[:,1], rcond=None)
def sim2loc(x,y): return cx[0]*x+cx[1]*y+cx[2], cy[0]*x+cy[1]*y+cy[2]
sim_lx, sim_ly = sim2loc(sim_x, sim_y)
print(f"affine residual (mm): {np.hypot(*(np.array(sim2loc(gl_sim[:,0],gl_sim[:,1]))-gl_loc.T)).mean():.2f}")

# ---- phantom bowl (grid-inch -> local mm): x_mm=25.4*x_in, y_mm=145.9-23.85*y_in ----
BC_in=(3.124,3.028); RX_in=1.901; RY_in=3.233
bowl_cx=25.4*BC_in[0]; bowl_cy=145.9-23.85*BC_in[1]
bowl_w=2*25.4*RX_in;   bowl_h=2*23.85*RY_in
def bowl(ax,lw=1.6): ax.add_patch(Ellipse((bowl_cx,bowl_cy),bowl_w,bowl_h,fill=False,edgecolor=OUT_C,lw=lw,zorder=1))

fig,(a1,a2,a3)=plt.subplots(1,3,figsize=(13.2,6.0))

# panel 1: sim (sim-mm)
a1.scatter(sim_x,sim_y,s=34,facecolor=TEAL,edgecolor="white",linewidth=0.4,zorder=3)
a1.set_title("Simulated grid\nuniform 10 mm lattice",fontsize=12.5,fontweight="bold",color=INK)

# panel 2: measured (local mm) + bowl
bowl(a2)
a2.scatter(px[~mm],py[~mm],s=34,facecolor="none",edgecolor="#B7C4CE",linewidth=1.2,zorder=2)
a2.scatter(px[mm],py[mm],s=40,facecolor=CRIMSON,edgecolor="white",linewidth=0.4,zorder=3)
a2.set_title("Physical grid + phantom\n6x6 cells, 51 measured",fontsize=12.5,fontweight="bold",color=INK)

# panel 3: overlay in local mm
bowl(a3)
a3.scatter(sim_lx,sim_ly,s=30,facecolor=TEAL,edgecolor="none",alpha=0.85,zorder=2,label="simulated lattice")
a3.scatter(px[mm],py[mm],s=44,facecolor="none",edgecolor=CRIMSON,linewidth=1.6,zorder=3,label="measured positions")
a3.set_title("Overlay (same physical frame)\nvia grid_placed_global",fontsize=12.5,fontweight="bold",color=INK)
a3.legend(loc="lower center",fontsize=9,framealpha=0.95)

for ax in (a1,a2,a3):
    ax.set_aspect("equal"); ax.set_xlabel("x (mm)",fontsize=10.5); ax.set_ylabel("y (mm)",fontsize=10.5)
    ax.grid(True,color="#EAF0F4",lw=0.6); ax.set_axisbelow(True)
    for s in ax.spines.values(): s.set_color("#D8E2EA")

fig.suptitle("Two sampling grids on the same phantom, and their overlay",fontsize=14.5,fontweight="bold",color=INK,y=0.99)
fig.text(0.5,0.01,
   "The sim samples a dense uniform lattice; the bench samples a sparser 6x6 cell grid. Registered into one frame "
   "(right), the measured\npositions sit inside the simulated coverage, over the same phantom region.",
   ha="center",va="bottom",fontsize=10.0,color=MUTE,style="italic")
fig.subplots_adjust(left=0.06,right=0.98,top=0.86,bottom=0.16,wspace=0.24)
p=os.path.join(HERE,"grid_sim_vs_physical.png")
fig.savefig(p,dpi=160); print("wrote",p)
