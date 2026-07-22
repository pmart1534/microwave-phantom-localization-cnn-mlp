"""Zero-shot sim -> measured: train a CNN on simulated tumor dS, test on measured.

No measured data is seen during training. Pipeline established earlier:
  - differential dS = S(tumor) - S(empty baseline)   [cancels the constant offset]
  - sim S-matrix remapped to the PHYSICAL antenna order (perm [2,0,1,3])
  - both resampled to a common 2-8 GHz grid (256 pts); input = [Re, Im] of the
    16 S-params -> 32 x 256 image, each row z-scored per sample
  - targets in the shared GRID-INCH frame (sim via grid_placed_global affine;
    measured via label_xy)
Train on sim near-patch depths (+5..+20 mm, matching the measured tumor height).
Report median (x,y) error on: held-out SIM positions (in-domain sanity) and the
MEASURED set (the zero-shot transfer), vs a predict-centre chance baseline.
"""
import os, glob, re, json, sys
import numpy as np
import torch, torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader

torch.manual_seed(0); np.random.seed(0)
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "mlp_python"))
sys.path.insert(0, os.path.join(HERE, "..", "Above 95 Percent"))
from label_xy import targets_for_labels

SIM = r"C:\Users\peter\Desktop\EM Imaging\Simulation Data\SamMakin\Data Results\A3_Metal_1cm"
GPG = r"C:\Users\peter\Desktop\EM Imaging\Simulation Data\SamMakin\grid_placed_global.csv"
MEASROOT = r"C:\Users\peter\Desktop\EM Imaging\BreastPhantom\HunterVNA\DataMeasurements\Sam Antennas\MediumAntenna\Separated\June18"
DEPTHS = {5:"b1", 10:"b1", 15:"b1_2", 20:"b1_2"}      # near-patch, matches measured height
PERM = [2, 0, 1, 3]
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

def resamp(f, S16):    # S16: (nf,16) complex -> (256,16)
    out=np.empty((256,16),complex)
    for k in range(16): out[:,k]=np.interp(FG,f,S16[:,k].real)+1j*np.interp(FG,f,S16[:,k].imag)
    return out

def to_img(dS16):      # (256,16) complex -> (32,256) float, each row z-scored
    rows=np.concatenate([dS16.real.T, dS16.imag.T], axis=0)   # (32,256)
    rows=(rows-rows.mean(1,keepdims=True))/(rows.std(1,keepdims=True)+1e-9)
    return rows.astype(np.float32)

# ---- affine sim-mm -> local-mm, then local-mm -> grid-inch ----
gl=[l.split(",") for l in open(GPG).read().splitlines()[1:]]
gsim=np.array([[float(r[3]),float(r[4])] for r in gl]); gloc=np.array([[float(r[1]),float(r[2])] for r in gl])
M=np.column_stack([gsim,np.ones(len(gsim))]); cX=np.linalg.lstsq(M,gloc[:,0],rcond=None)[0]; cY=np.linalg.lstsq(M,gloc[:,1],rcond=None)[0]
def sim_to_inch(xmm,ymm):
    lx=cX[0]*xmm+cX[1]*ymm+cX[2]; ly=cY[0]*xmm+cY[1]*ymm+cY[2]
    return lx/25.4, (145.9-ly)/23.85

# ---- SIM training tensors ----
bases={b: resamp(*(lambda f,S:(f,S.reshape(len(f),16)))(*read_s4p(os.path.join(SIM,f"baseline_empty_{b}.s4p")))) for b in set(DEPTHS.values())}
Xs=[]; Ys=[]; Ps=[]
for z,bk in DEPTHS.items():
    for f in glob.glob(os.path.join(SIM,f"P*DenseZ{z}_*.s4p")):
        js=f[:-4]+".json";
        if not os.path.exists(js): continue
        m=json.load(open(js))
        fr,S=read_s4p(f); S=S[:,PERM][:,:,PERM]                       # remap to physical
        dS=resamp(fr,S.reshape(len(fr),16))-bases[bk]
        Xs.append(to_img(dS)); xi,yi=sim_to_inch(m["tumor_x_mm"],m["tumor_y_mm"]); Ys.append([xi,yi])
        Ps.append((round(m["tumor_x_mm"],1),round(m["tumor_y_mm"],1)))
Xs=np.array(Xs); Ys=np.array(Ys,np.float32); Ps=np.array(Ps)
print(f"sim samples: {len(Xs)}  target x[{Ys[:,0].min():.1f},{Ys[:,0].max():.1f}] y[{Ys[:,1].min():.1f},{Ys[:,1].max():.1f}] in")

# hold out 20% of unique sim positions for in-domain sanity
uP=np.unique(Ps,axis=0); np.random.shuffle(uP); nhe=int(0.2*len(uP))
hepos=set(map(tuple,uP[:nhe])); hemask=np.array([tuple(p) in hepos for p in Ps])
Xtr,Ytr=Xs[~hemask],Ys[~hemask]; Xhe,Yhe=Xs[hemask],Ys[hemask]

# ---- MEASURED test tensors (June18, 3 sessions, per-position per-session) ----
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
print(f"measured samples: {len(Xm)}  target x[{Ym[:,0].min():.1f},{Ym[:,0].max():.1f}] y[{Ym[:,1].min():.1f},{Ym[:,1].max():.1f}] in")

# ---- CNN ----
class Net(nn.Module):
    def __init__(s):
        super().__init__()
        s.c=nn.Sequential(nn.Conv2d(1,32,3,padding=1),nn.ReLU(),nn.MaxPool2d(2),
                          nn.Conv2d(32,32,3,padding=1),nn.ReLU(),nn.MaxPool2d(2),nn.Dropout(0.3))
        s.f=nn.Sequential(nn.Flatten(),nn.Linear(32*8*64,64),nn.ReLU(),nn.Linear(64,2))
    def forward(s,x): return s.f(s.c(x))

def T(a): return torch.tensor(a).unsqueeze(1)
net=Net(); opt=torch.optim.Adam(net.parameters(),lr=1e-3); lossf=nn.MSELoss()
dl=DataLoader(TensorDataset(T(Xtr),torch.tensor(Ytr)),batch_size=16,shuffle=True)
for ep in range(80):
    net.train()
    for xb,yb in dl: opt.zero_grad(); l=lossf(net(xb),yb); l.backward(); opt.step()

def med_err(X,Y):
    net.eval()
    with torch.no_grad(): p=net(T(X)).numpy()
    e=np.hypot(p[:,0]-Y[:,0],p[:,1]-Y[:,1]); return np.median(e),e,p
he_m,_,_=med_err(Xhe,Yhe)
zs_m,zs_e,zs_p=med_err(Xm,Ym)
cen=Ytr.mean(0); chance=np.median(np.hypot(Ym[:,0]-cen[0],Ym[:,1]-cen[1]))
print("="*56)
print(f"IN-DOMAIN  (train sim, test held-out sim): {he_m:.3f} in ({he_m*25.4:.1f} mm)")
print(f"ZERO-SHOT  (train sim, test MEASURED)    : {zs_m:.3f} in ({zs_m*25.4:.1f} mm)")
print(f"CHANCE     (predict sim centroid on meas): {chance:.3f} in ({chance*25.4:.1f} mm)")
print("="*56)
np.savez(os.path.join(HERE,"results","zero_shot_sim2meas.npz"),
         meas_true=Ym, meas_pred=zs_p, meas_err=zs_e,
         he=he_m, zs=zs_m, chance=chance)
