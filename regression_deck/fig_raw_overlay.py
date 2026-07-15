"""Deck 3 — raw S-parameters, simulated vs measured antennas (empty phantom).

Overlays the empty-phantom baseline for the HFSS 'Sam' antennas (sim) and the
bench 'Sam Medium' antennas (measured): reflection |S11| and coupling |S21| in
dB vs frequency. Shows how far the two antenna models are from each other — the
domain gap any sim->measured transfer would have to bridge.
"""
import os, glob, re
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BLUE="#0B5D7A"; TEAL="#1C9AA8"; CORAL="#D64545"; INK="#1E293B"; MUTE="#5B6B7B"; AMBER="#E0A100"
HERE=os.path.dirname(__file__)
SIMB=r"C:\Users\peter\Desktop\EM Imaging\Simulation Data\SamMakin\Data Results\A3_Metal_1cm\baseline_empty_b1.s4p"
SESS=r"C:\Users\peter\Desktop\EM Imaging\BreastPhantom\HunterVNA\DataMeasurements\Sam Antennas\MediumAntenna\Separated\June18\BreastPhantom_A3_FishingWeight_20260618_1530"

def read_s4p(path):
    vals=[]; scale=1e9
    for line in open(path):
        s=line.strip()
        if not s or s.startswith("!"): continue
        if s.startswith("#"):
            low=s.lower(); scale = 1e6 if " mhz" in low else 1e9; continue
        vals.extend(float(t) for t in s.split())
    v=np.asarray(vals); per=1+2*16; nf=len(v)//per
    v=v[:nf*per].reshape(nf,per); body=v[:,1:].reshape(nf,16,2)
    S=(body[:,:,0]*np.exp(1j*np.deg2rad(body[:,:,1]))).reshape(nf,4,4)
    return v[:,0]*scale, S

def read_meas_csv(path):
    """Frequency + 16 (mag,phase) columns -> (freq_hz, S[nf,4,4])."""
    arr=np.genfromtxt(path,delimiter=",",skip_header=1)
    arr=arr[:,~np.all(np.isnan(arr),axis=0)]   # drop trailing empty col
    f=arr[:,0]; body=arr[:,1:].reshape(len(f),16,2)
    S=(body[:,:,0]*np.exp(1j*np.deg2rad(body[:,:,1]))).reshape(len(f),4,4)
    return f, S

# sim
fs, Ss = read_s4p(SIMB)
# measured: average the 16 baseline takes for a clean curve
mfiles=sorted(glob.glob(os.path.join(SESS,"baseline_T*.csv")))
Sm_list=[];
for mf in mfiles:
    fm, S = read_meas_csv(mf); Sm_list.append(S)
Sm=np.mean(Sm_list,axis=0)
print(f"sim nf={len(fs)} ({fs[0]/1e9:.1f}-{fs[-1]/1e9:.1f} GHz) | meas nf={len(fm)} ({fm[0]/1e9:.2f}-{fm[-1]/1e9:.1f} GHz), {len(mfiles)} takes avg")

def dB(x): return 20*np.log10(np.maximum(np.abs(x),1e-6))

fig,(a1,a2)=plt.subplots(1,2,figsize=(12.8,5.2))
# reflection S11 (avg of the 4 diagonal ports for robustness)
s11_sim=np.mean([dB(Ss[:,i,i]) for i in range(4)],axis=0)
s11_mea=np.mean([dB(Sm[:,i,i]) for i in range(4)],axis=0)
a1.plot(fs/1e9,s11_sim,color=TEAL,lw=2.0,label="simulated (HFSS 'Sam')")
a1.plot(fm/1e9,s11_mea,color=CORAL,lw=1.7,label="measured ('Sam Medium')")
a1.set_title("Reflection  |S11|  (avg of 4 ports)",fontsize=12.5,fontweight="bold",color=INK)

# coupling S21 (avg of the 12 off-diagonal pairs)
off=[(i,j) for i in range(4) for j in range(4) if i!=j]
s21_sim=np.mean([dB(Ss[:,i,j]) for i,j in off],axis=0)
s21_mea=np.mean([dB(Sm[:,i,j]) for i,j in off],axis=0)
a2.plot(fs/1e9,s21_sim,color=TEAL,lw=2.0,label="simulated (HFSS 'Sam')")
a2.plot(fm/1e9,s21_mea,color=CORAL,lw=1.7,label="measured ('Sam Medium')")
a2.set_title("Coupling  |Sij|  (avg of 12 pairs)",fontsize=12.5,fontweight="bold",color=INK)

for ax in (a1,a2):
    ax.axvspan(2,8,color=TEAL,alpha=0.05,zorder=0)   # shared 2-8 GHz band
    ax.set_xlabel("frequency (GHz)",fontsize=11); ax.set_ylabel("magnitude (dB)",fontsize=11)
    ax.grid(True,color="#EAF0F4",lw=0.7); ax.set_axisbelow(True)
    ax.legend(fontsize=10,framealpha=0.95); ax.set_xlim(0,8)
    for s in ax.spines.values(): s.set_color("#D8E2EA")

fig.suptitle("Raw S-parameters — simulated vs measured antennas (empty phantom)",
             fontsize=14.5,fontweight="bold",color=INK,y=1.02)
fig.text(0.5,-0.03,
   "The two antenna models resonate and couple differently — a real domain gap. Sim is exported 2-8 GHz; the bench sweeps 0.1-8 GHz. "
   "Shaded band = the shared 2-8 GHz range used for any comparison.",
   ha="center",va="top",fontsize=10.2,color=MUTE,style="italic")
fig.tight_layout(rect=[0,0.06,1,0.98])
p=os.path.join(HERE,"raw_sparam_sim_vs_meas.png")
fig.savefig(p,dpi=160,bbox_inches="tight"); print("wrote",p)
