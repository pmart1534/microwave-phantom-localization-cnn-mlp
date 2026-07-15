"""Deck 3 (exploratory) — can a model learn a sim->measured mapping?

Only the EMPTY baseline gives a cleanly *paired* sim vs measured signal (the
position grids/frames differ, so per-tumor positions can't be paired). So we ask
a bounded question on the empty antenna response:

  given the simulated 16 S-parameters at a frequency, can a model predict the
  MEASURED 16 S-parameters at that frequency — and does it generalize to
  frequencies it never saw?

Both put on a shared 2-8 GHz grid. Input = 32-D real vector (16 S-params x
[Re,Im]) from sim; target = same for measured. Train on 70% of frequencies,
test on the held-out 30%. Compare a linear (Ridge) map vs a small MLP, and
report the raw (pre-model) correlation for reference.
"""
import os, glob
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.neural_network import MLPRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import r2_score

TEAL="#1C9AA8"; BLUE="#0B5D7A"; CORAL="#D64545"; MINT="#2CC4A3"; INK="#1E293B"; MUTE="#5B6B7B"; AMBER="#E0A100"
HERE=os.path.dirname(__file__)
SIMB=r"C:\Users\peter\Desktop\EM Imaging\Simulation Data\SamMakin\Data Results\A3_Metal_1cm\baseline_empty_b1.s4p"
SESS=r"C:\Users\peter\Desktop\EM Imaging\BreastPhantom\HunterVNA\DataMeasurements\Sam Antennas\MediumAntenna\Separated\June18\BreastPhantom_A3_FishingWeight_20260618_1530"

def read_s4p(path):
    vals=[]; scale=1e9
    for line in open(path):
        s=line.strip()
        if not s or s.startswith("!"): continue
        if s.startswith("#"):
            low=s.lower(); scale=1e6 if " mhz" in low else 1e9; continue
        vals.extend(float(t) for t in s.split())
    v=np.asarray(vals); per=1+2*16; nf=len(v)//per
    v=v[:nf*per].reshape(nf,per); body=v[:,1:].reshape(nf,16,2)
    S=body[:,:,0]*np.exp(1j*np.deg2rad(body[:,:,1]))   # (nf,16)
    return v[:,0]*scale, S

def read_meas_csv(path):
    a=np.genfromtxt(path,delimiter=",",skip_header=1)
    a=a[:,~np.all(np.isnan(a),axis=0)]
    f=a[:,0]; body=a[:,1:].reshape(len(f),16,2)
    S=body[:,:,0]*np.exp(1j*np.deg2rad(body[:,:,1]))
    return f, S

# load + resample to shared 2-8 GHz
fs, Ss = read_s4p(SIMB)
Sm_list=[read_meas_csv(f)[1] for f in sorted(glob.glob(os.path.join(SESS,"baseline_T*.csv")))]
fm,_ = read_meas_csv(sorted(glob.glob(os.path.join(SESS,"baseline_T*.csv")))[0])
Sm=np.mean(Sm_list,axis=0)
grid=np.linspace(2e9,8e9,512)
def resamp(f,S):
    out=np.empty((len(grid),16),complex)
    for k in range(16):
        out[:,k]=np.interp(grid,f,S[:,k].real)+1j*np.interp(grid,f,S[:,k].imag)
    return out
Xs=resamp(fs,Ss); Xm=resamp(fm,Sm)

# feature matrices: 32-D real (Re,Im of 16 params)
def feats(S): return np.column_stack([S.real, S.imag])
A=feats(Xs); B=feats(Xm)   # (512,32) sim -> measured

# raw correlation (before any learning), on magnitudes per port
raw_r=np.mean([np.corrcoef(np.abs(Xs[:,k]),np.abs(Xm[:,k]))[0,1] for k in range(16)])

# 70/30 frequency split (interleaved so both cover the band)
idx=np.arange(len(grid)); test=idx%10<3; train=~test
As,Bs=A[train],B[train]; At,Bt=A[test],B[test]
mu,sd=As.mean(0),As.std(0)+1e-9
def z(x): return (x-mu)/sd

ridge=Ridge(alpha=1.0).fit(z(As),Bs)
mlp=MLPRegressor(hidden_layer_sizes=(128,128),activation="relu",max_iter=4000,
                 random_state=0,alpha=1e-3).fit(z(As),Bs)
r2_ridge=r2_score(Bt,ridge.predict(z(At)))
r2_mlp  =r2_score(Bt,mlp.predict(z(At)))
# recovered-magnitude correlation on held-out freqs, using the LINEAR map (the one that generalizes)
predB=ridge.predict(z(A))                    # full grid for plotting
pred_cplx=predB[:,:16]+1j*predB[:,16:]
learned_r=np.mean([np.corrcoef(np.abs(pred_cplx[test,k]),np.abs(Xm[test,k]))[0,1] for k in range(16)])

print(f"raw |S| corr (sim vs meas, per-port avg): {raw_r:.3f}")
print(f"held-out R2  Ridge(linear): {r2_ridge:.3f}   MLP: {r2_mlp:.3f}")
print(f"held-out learned |S| corr (linear): {learned_r:.3f}")

# ---- figure: (a) one port raw vs learned, (b) predicted-vs-actual scatter on test freqs
fig,(a1,a2)=plt.subplots(1,2,figsize=(12.8,5.2))
g=grid/1e9
k=0  # S11
a1.plot(g,np.abs(Xs[:,k]),color=TEAL,lw=1.8,label="sim |S11| (input)")
a1.plot(g,np.abs(Xm[:,k]),color=CORAL,lw=1.8,label="measured |S11| (target)")
a1.plot(g,np.abs(pred_cplx[:,k]),color=BLUE,lw=1.7,ls="--",label="sim after linear map → measured")
a1.set_xlabel("frequency (GHz)",fontsize=11); a1.set_ylabel("|S11|",fontsize=11)
a1.set_title("Linear map pulls sim toward measured, port S11",fontsize=12.5,fontweight="bold",color=INK)
a1.legend(fontsize=9.5,framealpha=0.95); a1.grid(True,color="#EAF0F4",lw=0.7); a1.set_axisbelow(True)

# scatter predicted vs actual (all 32 dims, test freqs) — linear map
a2.scatter(Bt.ravel(), ridge.predict(z(At)).ravel(), s=8, color=BLUE, alpha=0.35, edgecolor="none")
lim=[min(Bt.min(),-1.05), max(Bt.max(),1.05)]
a2.plot(lim,lim,color=MUTE,lw=1.2,ls="--")
a2.set_xlabel("measured (actual)",fontsize=11); a2.set_ylabel("linear-map predicted",fontsize=11)
a2.set_title(f"Held-out frequencies — R² = {r2_ridge:.2f} (linear)",fontsize=12.5,fontweight="bold",color=INK)
a2.grid(True,color="#EAF0F4",lw=0.7); a2.set_axisbelow(True); a2.set_aspect("equal")
for ax in (a1,a2):
    for s in ax.spines.values(): s.set_color("#D8E2EA")

fig.suptitle("Exploratory: can a model bridge the sim↔measured antenna gap? (empty baseline)",
             fontsize=14,fontweight="bold",color=INK,y=1.0)
fig.text(0.5,-0.03,
   f"Raw sim-vs-measured |S| correlation is {raw_r:.2f}. A LINEAR transfer maps sim→measured to R²={r2_ridge:.2f} on frequencies it never saw — "
   f"a real, learnable relationship. A flexible MLP overfits the single paired baseline (R²={r2_mlp:.2f}); nonlinear domain adaptation needs far more paired data.",
   ha="center",va="top",fontsize=10.0,color=MUTE,style="italic")
fig.tight_layout(rect=[0,0.06,1,0.97])
p=os.path.join(HERE,"sim_meas_correlation.png")
fig.savefig(p,dpi=160,bbox_inches="tight"); print("wrote",p)

# save metrics for the deck
import json
json.dump(dict(raw_r=raw_r,r2_ridge=r2_ridge,r2_mlp=r2_mlp,learned_r=learned_r),
          open(os.path.join(HERE,"sim_meas_correlation.json"),"w"),indent=1)
