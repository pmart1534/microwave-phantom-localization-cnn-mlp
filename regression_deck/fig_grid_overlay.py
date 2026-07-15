"""Deck 3 — sim 1 cm uniform grid  vs  the physical measurement grid.

Left : simulated tumor positions — a uniform 10 mm lattice over the phantom.
Right: the physical 6x6 cell grid (placement_grid_6x6.csv). Each cell holds 4
sub-positions at the corners; cell pitch is ~25.4 x 23.85 mm (asymmetric, wider
than tall). Sub-positions actually MEASURED on the empty phantom are filled.
"""
import os, glob, re, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BLUE="#0B5D7A"; TEAL="#1C9AA8"; MINT="#2CC4A3"; CORAL="#D64545"
INK="#1E293B"; MUTE="#5B6B7B"; AMBER="#E0A100"
HERE=os.path.dirname(__file__)
GRID=r"C:\Users\peter\Desktop\EM Imaging\Simulation Data\SamMakin\placement_grid_6x6.csv"
SESS=r"C:\Users\peter\Desktop\EM Imaging\BreastPhantom\HunterVNA\DataMeasurements\Sam Antennas\MediumAntenna\Separated\June18\BreastPhantom_A3_FishingWeight_20260618_1530"

# ---- sim uniform grid: unique xy from the 8-fold result ----
pp = json.load(open(os.path.join(HERE,"..","results","cnn_simreg_8fold_nf256_5mmgrid.json")))["perPosition"]
sx = np.array([p["x"] for p in pp]); sy = np.array([p["y"] for p in pp])
uxy = sorted(set(zip(np.round(sx,1), np.round(sy,1))))
ux = np.array([a for a,_ in uxy]); uy = np.array([b for _,b in uxy])

# ---- physical grid ----
labels=[]; px=[]; py=[]
for ln in open(GRID).read().splitlines()[1:]:
    lab,x,y = ln.split(","); labels.append(lab); px.append(float(x)); py.append(float(y))
px=np.array(px); py=np.array(py)

# ---- which physical sub-positions were measured (map RnCmPp -> HxVyCz) ----
CORNER={"P1":"C1","P2":"C2","P3":"C4","P4":"C3"}
meas=set()
for f in glob.glob(os.path.join(SESS,"R*C*P*_T01.csv")):
    m=re.match(r"R(\d+)C(\d+)P(\d)", os.path.basename(f))
    if m:
        r,c,p=m.groups()
        meas.add(f"H{c}V{r}{CORNER['P'+p]}")
measmask=np.array([lab in meas for lab in labels])
print(f"sim unique positions: {len(ux)} | physical labels: {len(labels)} | measured: {measmask.sum()}")

fig,(a1,a2)=plt.subplots(1,2,figsize=(12.8,6.2))

# sim panel
a1.scatter(ux,uy,s=42,facecolor=TEAL,edgecolor="white",linewidth=0.4,zorder=3)
a1.set_title("Simulated grid — uniform 10 mm lattice",fontsize=13,fontweight="bold",color=INK,pad=26)
a1.text(0.5,1.015,f"{len(ux)} unique (x,y) positions  ·  13 depth planes each",
        transform=a1.transAxes,ha="center",va="bottom",fontsize=10.5,color=TEAL)

# physical panel: sub-positions, measured filled
a2.scatter(px[~measmask],py[~measmask],s=48,facecolor="none",edgecolor="#B7C4CE",
           linewidth=1.3,zorder=2,label="grid position (not measured)")
a2.scatter(px[measmask],py[measmask],s=54,facecolor=CORAL,edgecolor="white",
           linewidth=0.5,zorder=3,label=f"measured on empty ({measmask.sum()})")
a2.set_title("Physical grid — 6×6 cells, 4 corners each",fontsize=13,fontweight="bold",color=INK,pad=26)
a2.text(0.5,1.015,"cell pitch ≈ 25.4 × 23.85 mm (wider than tall)  ·  corners ±9.5 mm",
        transform=a2.transAxes,ha="center",va="bottom",fontsize=10.5,color=CORAL)
a2.legend(loc="lower center",fontsize=9.5,framealpha=0.95,ncol=1)

for ax in (a1,a2):
    ax.set_aspect("equal"); ax.set_xlabel("x (mm)",fontsize=11); ax.set_ylabel("y (mm)",fontsize=11)
    ax.grid(True,color="#EAF0F4",lw=0.7); ax.set_axisbelow(True)
    for s in ax.spines.values(): s.set_color("#D8E2EA")

fig.text(0.5,-0.01,
   "The sim samples a dense, uniform lattice at many depths; the bench samples a sparser 6×6 cell grid at one tumor height. "
   "Different geometry AND different coverage — both matter when comparing the two.",
   ha="center",va="top",fontsize=10.3,color=MUTE,style="italic")
fig.tight_layout(rect=[0,0.05,1,0.99])
p=os.path.join(HERE,"grid_sim_vs_physical.png")
fig.savefig(p,dpi=160,bbox_inches="tight"); print("wrote",p)
