"""Deck 3 - how much differential signal a BEET (dielectric) tumor produces
versus a METAL tumor, in simulation and on the bench.

Mean |dS| (object minus empty baseline, over frequency and all 16 S-parameters):
  - sim metal / sim beet: A3_Metal_1cm / A3_Beet_1cm at z=+15 mm (matched depth,
    identical positions, so only the material differs).
  - measured metal / beet: June18 (metal) and July09 (beet), per-position averaged
    over 16 takes, over all grid positions.
Absolute scale differs between sim and bench; the informative quantity is the
beet/metal RATIO within each domain.
"""
import os, glob, re
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CRIMSON="#BE0000"; GOLD="#C8890B"; INK="#1E293B"; MUTE="#5B6B7B"; TEAL="#1C9AA8"
HERE=os.path.dirname(__file__)
SIM=r"C:\Users\peter\Desktop\EM Imaging\Simulation Data\SamMakin\Data Results"
MEAS=r"C:\Users\peter\Desktop\EM Imaging\BreastPhantom\HunterVNA\DataMeasurements\Sam Antennas\MediumAntenna\Separated"

def read_s4p(path):
    vals=[]; sc=1e9
    for line in open(path):
        s=line.strip()
        if not s or s.startswith("!"): continue
        if s.startswith("#"): sc=1e6 if " mhz" in s.lower() else 1e9; continue
        vals.extend(float(t) for t in s.split())
    v=np.asarray(vals); per=1+2*16; nf=len(v)//per; v=v[:nf*per].reshape(nf,per)
    b=v[:,1:].reshape(nf,16,2); return b[:,:,0]*np.exp(1j*np.deg2rad(b[:,:,1]))

def read_meas(path):
    a=np.genfromtxt(path,delimiter=",",skip_header=1); a=a[:,~np.all(np.isnan(a),axis=0)]
    b=a[:,1:].reshape(a.shape[0],16,2); return b[:,:,0]*np.exp(1j*np.deg2rad(b[:,:,1]))

def sim_dS(folder, baseline, depthtok="DenseZ15_"):
    base=read_s4p(os.path.join(folder,baseline))
    vals=[]
    for f in glob.glob(os.path.join(folder,f"P*{depthtok}*.s4p")):
        try: S=read_s4p(f)
        except: continue
        if S.shape==base.shape: vals.append(np.mean(np.abs(S-base)))
    return np.array(vals)

def meas_dS(session):
    base=np.mean([read_meas(f) for f in sorted(glob.glob(os.path.join(session,"baseline_T*.csv")))],axis=0)
    stems=sorted({re.match(r"(R\d+C\d+P\d+)_T",os.path.basename(f)).group(1)
                  for f in glob.glob(os.path.join(session,"R*C*P*_T*.csv"))})
    vals=[]
    for st in stems:
        S=np.mean([read_meas(f) for f in sorted(glob.glob(os.path.join(session,f"{st}_T*.csv")))],axis=0)
        if S.shape==base.shape: vals.append(np.mean(np.abs(S-base)))
    return np.array(vals)

sm=sim_dS(os.path.join(SIM,"A3_Metal_1cm"),"baseline_empty_b1_2.s4p")   # z=15 -> b1_2 batch
sb=sim_dS(os.path.join(SIM,"A3_Beet_1cm"),"baseline_empty.s4p")         # beet single baseline
# July09 has same-day metal (FishingWeight) and beet -> clean material comparison
mm=meas_dS(os.path.join(MEAS,"July09","BreastPhantom_A3_FishingWeight_20260709_1045"))
mb=meas_dS(os.path.join(MEAS,"July09","BreastPhantom_A3_Beet_1cm_20260709_1138"))
vals={"sim_metal":np.median(sm),"sim_beet":np.median(sb),"meas_metal":np.median(mm),"meas_beet":np.median(mb)}
print("median mean|dS|:", {k:round(v,4) for k,v in vals.items()})
sr=vals["sim_beet"]/vals["sim_metal"]; mr=vals["meas_beet"]/vals["meas_metal"]
print(f"beet/metal ratio: sim {sr:.2f}  measured {mr:.2f}")

fig,(a1,a2)=plt.subplots(1,2,figsize=(11.6,5.4))
# absolute (each domain its own scale)
for ax,(dom,mv,bv,rat) in zip([a1,a2],
      [("Simulated",vals["sim_metal"],vals["sim_beet"],sr),
       ("Measured",vals["meas_metal"],vals["meas_beet"],mr)]):
    bars=ax.bar(["metal","beet"],[mv,bv],color=[MUTE,CRIMSON],width=0.6,edgecolor="k",linewidth=0.5)
    ax.set_title(f"{dom}\nbeet = {rat*100:.0f}% of metal",fontsize=13,fontweight="bold",color=INK)
    ax.set_ylabel("median mean |dS|  (over freq & 16 S-params)",fontsize=10.5)
    for b,v in zip(bars,[mv,bv]): ax.text(b.get_x()+b.get_width()/2,v,f"{v:.4f}",ha="center",va="bottom",fontsize=11,color=INK)
    ax.grid(True,axis="y",color="#EAF0F4",lw=0.7); ax.set_axisbelow(True); ax.set_ylim(0,max(mv,bv)*1.25)
    for s in ax.spines.values(): s.set_color("#D8E2EA")

fig.suptitle("Differential signal: beet (dielectric) vs metal tumor, simulated and measured",
             fontsize=14,fontweight="bold",color=INK,y=0.99)
fig.text(0.5,0.005,
   f"In simulation (identical size and position, only the material differs) the beet produces {sr*100:.0f}% of the metal signal, near the Clausius-Mossotti\n"
   f"estimate (~85%). On the bench the beet produces {mr*100:.0f}% of the metal signal; the larger gap likely reflects object size / placement differences\n"
   f"between the two measurements, or a weaker real-beet contrast than the sim model (eps_r=50 placeholder) assumes.",
   ha="center",va="bottom",fontsize=9.6,color=MUTE,style="italic")
fig.subplots_adjust(left=0.08,right=0.97,top=0.84,bottom=0.20,wspace=0.22)
p=os.path.join(HERE,"beet_vs_metal_dS.png")
fig.savefig(p,dpi=160); print("wrote",p)
