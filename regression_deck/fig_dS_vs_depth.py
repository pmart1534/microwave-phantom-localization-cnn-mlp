"""Deck 2 - how much overall 'difference' the tumor makes vs depth.

For every position s4p, dS = S_tumor - S_empty (batch-matched baseline). Reduce
to one scalar per position: mean |dS| over frequency and all 16 S-parameters.
Then summarize per depth plane (median across positions, with IQR band).

This is the physical driver behind the depth story: the perturbation is largest
where the tumor sits closest to the antenna plane and decays with distance, so
far/edge depths carry less signal and localize worse.
"""
import os, glob, re
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

NAVY="#0E2233"; BLUE="#0B5D7A"; TEAL="#1C9AA8"; MINT="#2CC4A3"
CORAL="#D64545"; AMBER="#E0A100"; INK="#1E293B"; MUTE="#5B6B7B"
SIM = r"C:\Users\peter\Desktop\EM Imaging\Simulation Data\SamMakin\Data Results\A3_Metal_1cm"
OUT = os.path.dirname(__file__)

# batch baseline map (metal); z=3 (Depth3) excluded
BATCH = {0:"b1",5:"b1",10:"b1", -5:"b1_2",15:"b1_2",20:"b1_2",25:"b1_2",30:"b1_2",
         -15:"b1_3",-10:"b1_3",35:"b1_3",40:"b1_3",45:"b1_3"}

def read_s4p(path):
    vals=[]; scale=1e9
    with open(path) as fh:
        for line in fh:
            s=line.strip()
            if not s or s.startswith("!"): continue
            if s.startswith("#"):
                low=s.lower()
                scale = 1.0 if (" hz" in low and " ghz" not in low and " mhz" not in low) else \
                        (1e6 if " mhz" in low else 1e9)
                continue
            vals.extend(float(t) for t in s.split())
    v=np.asarray(vals); per=1+2*16; nf=len(v)//per
    v=v[:nf*per].reshape(nf,per)
    body=v[:,1:].reshape(nf,16,2)
    S=body[:,:,0]*np.exp(1j*np.deg2rad(body[:,:,1]))   # (nf,16)
    return v[:,0]*scale, S

def depth_of(fn):
    m=re.search(r"DenseZ(-?\d+)", fn)
    return int(m.group(1)) if m else None

# load batch baselines once
base={}
for b in set(BATCH.values()):
    _, S = read_s4p(os.path.join(SIM, f"baseline_empty_{b}.s4p"))
    base[b]=S

files=[f for f in glob.glob(os.path.join(SIM,"P*.s4p"))]
per_depth={}
for i,f in enumerate(files):
    z=depth_of(os.path.basename(f))
    if z is None or z not in BATCH: continue
    try:
        _, S = read_s4p(f)
    except Exception: continue
    dS = S - base[BATCH[z]]
    if dS.shape != base[BATCH[z]].shape: continue
    m = np.mean(np.abs(dS))            # scalar: mean |dS| over freq & 16 params
    per_depth.setdefault(z, []).append(m)
    if i % 200 == 0: print(f"  {i}/{len(files)}")

zs=sorted(per_depth)
med=np.array([np.median(per_depth[z]) for z in zs])
q1 =np.array([np.percentile(per_depth[z],25) for z in zs])
q3 =np.array([np.percentile(per_depth[z],75) for z in zs])
zs=np.array(zs)
print("per-depth mean|dS| median:", dict(zip(zs.tolist(), np.round(med,4).tolist())))

fig, ax = plt.subplots(figsize=(9.8, 5.4))
ax.fill_between(zs, q1, q3, color=TEAL, alpha=0.15, label="inter-quartile range")
ax.plot(zs, med, "-o", color=BLUE, lw=2.4, ms=8, zorder=3, label="median over positions")
ymax = max(q3)*1.10
# antenna PORT / feed point at z = +3 mm
ax.axvline(3, color=CORAL, lw=1.8, ls="--", zorder=2)
ax.annotate("antenna port / feed\n(z = +3 mm)", (3, ymax),
            textcoords="offset points", xytext=(-8, -2), ha="right", va="top",
            fontsize=9.5, color=CORAL, fontweight="bold")
# radiating PATCH element sits ~15-20 mm in (feed-line offset), where ΔS peaks
ax.axvspan(15, 20, color=AMBER, alpha=0.18, zorder=1)
ax.annotate("antenna patch (radiator, ~15-20 mm)\nΔS peaks here", (17.5, ymax),
            textcoords="offset points", xytext=(0, -2), ha="center", va="top",
            fontsize=9.7, color="#9A6D00", fontweight="bold")
# measured-tumor depth reference (sim↔real match) at z = +40 mm
ax.axvline(40, color=MUTE, lw=1.4, ls=":", zorder=2)
ax.annotate("measured tumor\ndepth (z = +40 mm)", (40, ymax),
            textcoords="offset points", xytext=(-6, -2), ha="right", va="top",
            fontsize=9.3, color=MUTE, fontweight="bold")
ax.set_ylim(top=ymax)
ax.set_xlabel("tumor depth z (mm)", fontsize=12)
ax.set_ylabel("mean |ΔS|  (tumor − empty, over freq & all 16 S-params)", fontsize=11.5)
ax.set_title("How much the tumor perturbs the signal, by depth",
             fontsize=13.5, fontweight="bold", color=INK)
ax.grid(True, color="#EAF0F4", lw=0.7); ax.set_axisbelow(True)
for s in ax.spines.values(): s.set_color("#D8E2EA")
ax.legend(fontsize=10.5, framealpha=0.95, loc="lower center")
fig.text(0.5, 0.015,
    "The port/feed is at +3 mm, but the radiating patch sits ~15-20 mm in (feed-line offset), and the\n"
    "perturbation peaks right there, where the tumor is nearest the radiator. It falls off with distance,\n"
    "so far depths carry the least signal.",
    ha="center", va="bottom", fontsize=10.0, color=MUTE, style="italic")
fig.subplots_adjust(left=0.12, right=0.97, top=0.90, bottom=0.24)
p=os.path.join(OUT,"sim_dS_vs_depth.png")
fig.savefig(p, dpi=160); print("wrote", p)
