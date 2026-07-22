"""Test 2 - baseline-calibrated sim -> measured transfer.

Test 1 (zero_shot_sim2meas.py) trained a CNN on simulated tumor dS and tested
directly on the bench: it collapsed to ~74 mm (worse than chance). The measured
antenna response is simply out-of-distribution for a sim-only model.

Here we first LEARN the sim->measured antenna gap on the EMPTY baseline (the one
cleanly paired state), exactly as in sim_meas_correlation.py: a per-frequency
linear (ridge) map  y = M z(x)  from the 32-D sim vector [Re,Im of 16 S-params]
to the measured 32-D vector, R2 ~ 0.65 on held-out frequencies. Because a tumor
signal is a DIFFERENCE dS = S_tumor - S_empty, the map's mean/intercept cancel and
the calibrated tumor signal is simply

    dS_measured-like = coef_ @ (dS_sim / sd)        (applied per frequency)

We then train the SAME CNN on the calibrated sim dS and test on the untouched
measured dS. Controlled against an uncalibrated path (a hard antenna permutation
only, = Test 1) so the only difference is the learned calibration.

Reports median (x,y) error on the measured bench for:
  chance (predict centroid) | uncalibrated (perm only) | CALIBRATED (learned map)
plus each path's in-domain held-out-sim sanity.
"""
import os, glob, re, json, sys
import numpy as np
import torch, torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
from sklearn.linear_model import Ridge
from sklearn.metrics import r2_score

torch.manual_seed(0); np.random.seed(0)
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "mlp_python"))
sys.path.insert(0, os.path.join(HERE, "..", "Above 95 Percent"))
from label_xy import targets_for_labels

SIM = r"C:\Users\peter\Desktop\EM Imaging\Simulation Data\SamMakin\Data Results\A3_Metal_1cm"
GPG = r"C:\Users\peter\Desktop\EM Imaging\Simulation Data\SamMakin\grid_placed_global.csv"
MEASROOT = r"C:\Users\peter\Desktop\EM Imaging\BreastPhantom\HunterVNA\DataMeasurements\Sam Antennas\MediumAntenna\Separated\June18"
DEPTHS = {5:"b1", 10:"b1", 15:"b1_2", 20:"b1_2"}
PERM = [2, 0, 1, 3]                      # sim -> physical antenna order (uncalibrated path)
FG = np.linspace(2e9, 8e9, 256)

def read_s4p(path):
    vals=[]; sc=1e9
    for line in open(path):
        s=line.strip()
        if not s or s.startswith("!"): continue
        if s.startswith("#"): sc=1e6 if " mhz" in s.lower() else 1e9; continue
        vals.extend(float(t) for t in s.split())
    v=np.asarray(vals); per=1+2*16; nf=len(v)//per; v=v[:nf*per].reshape(nf,per)
    b=v[:,1:].reshape(nf,16,2); S=(b[:,:,0]*np.exp(1j*np.deg2rad(b[:,:,1]))).reshape(nf,4,4)
    return v[:,0]*sc, S

def read_meas(path):
    a=np.genfromtxt(path,delimiter=",",skip_header=1); a=a[:,~np.all(np.isnan(a),axis=0)]
    b=a[:,1:].reshape(a.shape[0],16,2); S=(b[:,:,0]*np.exp(1j*np.deg2rad(b[:,:,1]))).reshape(a.shape[0],4,4)
    return a[:,0], S

def resamp(f, S16):
    out=np.empty((256,16),complex)
    for k in range(16): out[:,k]=np.interp(FG,f,S16[:,k].real)+1j*np.interp(FG,f,S16[:,k].imag)
    return out

def to_img(dS16):
    rows=np.concatenate([dS16.real.T, dS16.imag.T], axis=0)
    rows=(rows-rows.mean(1,keepdims=True))/(rows.std(1,keepdims=True)+1e-9)
    return rows.astype(np.float32)

# ---------- 1. LEARN the sim->measured calibration on the empty baseline ----------
# sim empty (b1) and one measured empty session, resampled to a 512-pt grid.
GRID=np.linspace(2e9,8e9,512)
def resamp512(f,S16):
    out=np.empty((512,16),complex)
    for k in range(16): out[:,k]=np.interp(GRID,f,S16[:,k].real)+1j*np.interp(GRID,f,S16[:,k].imag)
    return out
fs,Ss=read_s4p(os.path.join(SIM,"baseline_empty_b1.s4p"))
SESS0=sorted(glob.glob(os.path.join(MEASROOT,"BreastPhantom_A3_*")))[0]
mbf=sorted(glob.glob(os.path.join(SESS0,"baseline_T*.csv")))
fm,_=read_meas(mbf[0]); Sm=np.mean([read_meas(b)[1] for b in mbf],axis=0)
Xs512=resamp512(fs,Ss.reshape(len(fs),16)); Xm512=resamp512(fm,Sm.reshape(len(fm),16))
A=np.column_stack([Xs512.real,Xs512.imag]); B=np.column_stack([Xm512.real,Xm512.imag])  # (512,32)
idx=np.arange(512); test=idx%10<3; train=~test
mu,sd=A[train].mean(0),A[train].std(0)+1e-9
ridge=Ridge(alpha=1.0).fit((A[train]-mu)/sd, B[train])
r2=r2_score(B[test], ridge.predict((A[test]-mu)/sd))
COEF=ridge.coef_            # (32,32) targets x features
print(f"calibration map: held-out R2 = {r2:.3f}  (sim empty -> measured empty)")

def calibrate(dS16):        # (256,16) complex sim dS -> measured-like (256,16) complex
    X=np.column_stack([dS16.real, dS16.imag]) / sd      # (256,32), intercept/mean cancel for a difference
    Y=X @ COEF.T                                         # (256,32)
    return Y[:,:16] + 1j*Y[:,16:]

# ---------- affine sim-mm -> grid-inch ----------
gl=[l.split(",") for l in open(GPG).read().splitlines()[1:]]
gsim=np.array([[float(r[3]),float(r[4])] for r in gl]); gloc=np.array([[float(r[1]),float(r[2])] for r in gl])
Maf=np.column_stack([gsim,np.ones(len(gsim))]); cX=np.linalg.lstsq(Maf,gloc[:,0],rcond=None)[0]; cY=np.linalg.lstsq(Maf,gloc[:,1],rcond=None)[0]
def sim_to_inch(xmm,ymm):
    lx=cX[0]*xmm+cX[1]*ymm+cX[2]; ly=cY[0]*xmm+cY[1]*ymm+cY[2]
    return lx/25.4, (145.9-ly)/23.85

# ---------- 2. SIM tumor tensors: uncalibrated (perm) and calibrated (map) ----------
raw_bases={b: resamp(*(lambda f,S:(f,S.reshape(len(f),16)))(*read_s4p(os.path.join(SIM,f"baseline_empty_{b}.s4p")))) for b in set(DEPTHS.values())}
Xu=[]; Xc=[]; Ys=[]; Ps=[]
for z,bk in DEPTHS.items():
    fb0,Sb0=read_s4p(os.path.join(SIM,f"baseline_empty_{bk}.s4p"))
    base_perm=resamp((fb0), (Sb0[:,PERM][:,:,PERM]).reshape(len(fb0),16))
    for f in glob.glob(os.path.join(SIM,f"P*DenseZ{z}_*.s4p")):
        js=f[:-4]+".json"
        if not os.path.exists(js): continue
        m=json.load(open(js)); fr,S=read_s4p(f)
        dS_raw=resamp(fr,S.reshape(len(fr),16))-raw_bases[bk]          # raw sim order (for the map)
        dS_perm=resamp(fr,(S[:,PERM][:,:,PERM]).reshape(len(fr),16))-base_perm  # physical order (perm only)
        Xu.append(to_img(dS_perm)); Xc.append(to_img(calibrate(dS_raw)))
        xi,yi=sim_to_inch(m["tumor_x_mm"],m["tumor_y_mm"]); Ys.append([xi,yi])
        Ps.append((round(m["tumor_x_mm"],1),round(m["tumor_y_mm"],1)))
Xu=np.array(Xu); Xc=np.array(Xc); Ys=np.array(Ys,np.float32); Ps=np.array(Ps)
print(f"sim samples: {len(Xu)}")

uP=np.unique(Ps,axis=0); np.random.shuffle(uP); nhe=int(0.2*len(uP))
hepos=set(map(tuple,uP[:nhe])); hemask=np.array([tuple(p) in hepos for p in Ps])

# ---------- 3. MEASURED test tensors (untouched) ----------
Xm=[]; Ym=[]
for sess in sorted(glob.glob(os.path.join(MEASROOT,"BreastPhantom_A3_*"))):
    bfiles=sorted(glob.glob(os.path.join(sess,"baseline_T*.csv")))
    if not bfiles: continue
    fb,_=read_meas(bfiles[0]); base=resamp(fb, np.mean([read_meas(b)[1] for b in bfiles],axis=0).reshape(len(fb),16))
    stems=sorted({re.match(r"(R\d+C\d+P\d+)_T",os.path.basename(x)).group(1) for x in glob.glob(os.path.join(sess,"R*C*P*_T*.csv"))})
    tg=targets_for_labels(stems,"A3_Empty")
    for st,xy in zip(stems,tg):
        Sp=np.mean([read_meas(x)[1] for x in sorted(glob.glob(os.path.join(sess,f"{st}_T*.csv")))],axis=0)
        dS=resamp(fb,Sp.reshape(len(fb),16))-base
        Xm.append(to_img(dS)); Ym.append([xy[0],xy[1]])
Xm=np.array(Xm); Ym=np.array(Ym,np.float32)
print(f"measured samples: {len(Xm)}")

# ---------- 4. train the same CNN on each sim variant ----------
class Net(nn.Module):
    def __init__(s):
        super().__init__()
        s.c=nn.Sequential(nn.Conv2d(1,32,3,padding=1),nn.ReLU(),nn.MaxPool2d(2),
                          nn.Conv2d(32,32,3,padding=1),nn.ReLU(),nn.MaxPool2d(2),nn.Dropout(0.3))
        s.f=nn.Sequential(nn.Flatten(),nn.Linear(32*8*64,64),nn.ReLU(),nn.Linear(64,2))
    def forward(s,x): return s.f(s.c(x))

def T(a): return torch.tensor(a).unsqueeze(1)
def train_eval(Xall, seed):
    torch.manual_seed(seed); np.random.seed(1000+seed)
    Xtr,Ytr=Xall[~hemask],Ys[~hemask]; Xhe,Yhe=Xall[hemask],Ys[hemask]
    net=Net(); opt=torch.optim.Adam(net.parameters(),lr=1e-3); lossf=nn.MSELoss()
    dl=DataLoader(TensorDataset(T(Xtr),torch.tensor(Ytr)),batch_size=16,shuffle=True)
    for ep in range(80):
        net.train()
        for xb,yb in dl: opt.zero_grad(); l=lossf(net(xb),yb); l.backward(); opt.step()
    net.eval()
    def med(X,Y):
        with torch.no_grad(): p=net(T(X)).numpy()
        return np.median(np.hypot(p[:,0]-Y[:,0],p[:,1]-Y[:,1])), p
    he,_=med(Xhe,Yhe); zs,p=med(Xm,Ym); return he,zs,p

# multi-seed: a single CNN training on 340 sim samples is high-variance, so
# average the transfer over 5 seeds and keep the median-seed predictions to plot.
SEEDS=[0,1,2,3,4]
cen=Ys[~hemask].mean(0); chance=np.median(np.hypot(Ym[:,0]-cen[0],Ym[:,1]-cen[1]))
res={"uncal":[], "cal":[]}
for sd_i in SEEDS:
    hu,zu,pu=train_eval(Xu,sd_i); hc,zc,pc=train_eval(Xc,sd_i)
    res["uncal"].append((hu,zu,pu)); res["cal"].append((hc,zc,pc))
    print(f"seed {sd_i}: uncal in-domain {hu:.3f} / meas {zu:.3f} in | cal in-domain {hc:.3f} / meas {zc:.3f} in")

def summarize(key):
    he=np.array([r[0] for r in res[key]]); zs=np.array([r[1] for r in res[key]])
    j=int(np.argsort(zs)[len(zs)//2])              # median-performing seed for plotting
    return np.median(he), np.median(zs), res[key][j][2]
he_u,zs_u,p_u=summarize("uncal"); he_c,zs_c,p_c=summarize("cal")

def mm(x): return x*25.4
print("="*60)
print(f"calibration map held-out R2                 : {r2:.3f}")
print(f"CHANCE      (predict sim centroid)          : {chance:.3f} in ({mm(chance):.1f} mm)")
print(f"UNCALIBRATED in-domain / measured (median-of-{len(SEEDS)}): {he_u:.3f} / {zs_u:.3f} in ({mm(zs_u):.1f} mm)")
print(f"CALIBRATED   in-domain / measured (median-of-{len(SEEDS)}): {he_c:.3f} / {zs_c:.3f} in ({mm(zs_c):.1f} mm)")
print("="*60)
os.makedirs(os.path.join(HERE,"results"),exist_ok=True)
np.savez(os.path.join(HERE,"results","test2_calibrated_sim2meas.npz"),
         meas_true=Ym, pred_uncal=p_u, pred_cal=p_c,
         he_u=he_u, zs_u=zs_u, he_c=he_c, zs_c=zs_c, chance=chance, r2=r2,
         uncal_meas_all=np.array([r[1] for r in res["uncal"]]),
         cal_meas_all=np.array([r[1] for r in res["cal"]]))
print("saved results/test2_calibrated_sim2meas.npz")
