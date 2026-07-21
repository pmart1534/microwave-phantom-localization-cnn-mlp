"""Deck 3 - raw transmission (coupling) S-parameters, sim vs measured (empty).

Companion to the per-port reflection figure. Shows four representative
transmission terms (antenna-to-antenna coupling): S21, S31, S41, S32.
Measured is clipped to the shared 2-8 GHz band.
"""
import os, glob
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

TEAL="#1C9AA8"; CORAL="#D64545"; INK="#1E293B"; MUTE="#5B6B7B"
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
    a=np.genfromtxt(path,delimiter=",",skip_header=1)
    a=a[:,~np.all(np.isnan(a),axis=0)]
    f=a[:,0]; body=a[:,1:].reshape(len(f),16,2)
    S=(body[:,:,0]*np.exp(1j*np.deg2rad(body[:,:,1]))).reshape(len(f),4,4)
    return f, S

fs, Ss = read_s4p(SIMB)
mfiles=sorted(glob.glob(os.path.join(SESS,"baseline_T*.csv")))
Sm=np.mean([read_meas_csv(f)[1] for f in mfiles],axis=0)
fm,_ = read_meas_csv(mfiles[0]); mk = fm >= 2e9

def dB(x): return 20*np.log10(np.maximum(np.abs(x),1e-6))
PAIRS=[(1,0),(2,0),(3,0),(2,1)]   # S21, S31, S41, S32 (0-indexed i,j)

fig,axes=plt.subplots(2,2,figsize=(11.4,7.0),sharex=True,sharey=True)
for (i,j),ax in zip(PAIRS,axes.ravel()):
    ax.plot(fs/1e9, dB(Ss[:,i,j]), color=TEAL, lw=2.0, label="simulated")
    ax.plot(fm[mk]/1e9, dB(Sm[mk,i,j]), color=CORAL, lw=1.7, label="measured")
    ax.set_title(f"Coupling  |S{i+1}{j+1}|", fontsize=12.5, fontweight="bold", color=INK)
    ax.grid(True, color="#EAF0F4", lw=0.7); ax.set_axisbelow(True)
    ax.set_xlim(2,8); ax.set_ylim(-70,-10)
    for sp in ax.spines.values(): sp.set_color("#D8E2EA")
    if (i,j) in PAIRS[2:]: ax.set_xlabel("frequency (GHz)", fontsize=11)
    ax.set_ylabel("magnitude (dB)", fontsize=11)
    if (i,j)==PAIRS[0]: ax.legend(fontsize=10, framealpha=0.95, loc="upper right")

fig.suptitle("Transmission (antenna coupling), simulated vs measured (empty phantom, 2-8 GHz)",
             fontsize=14, fontweight="bold", color=INK, y=0.99)
fig.text(0.5, 0.005,
    "Antenna-to-antenna coupling also differs between simulation and bench, most below the shared band and in the fine resonances.\n"
    "Below 2 GHz the measured coupling is out-of-band noise and is not shown.",
    ha="center", va="bottom", fontsize=10.2, color=MUTE, style="italic")
fig.subplots_adjust(left=0.07, right=0.98, top=0.90, bottom=0.13, hspace=0.22, wspace=0.14)
p=os.path.join(HERE,"transmission_sim_vs_meas.png")
fig.savefig(p, dpi=160); print("wrote", p)
