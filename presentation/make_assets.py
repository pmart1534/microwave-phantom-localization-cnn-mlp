"""Generate themed diagram PNGs for the CNN-vs-MLP deck (U-of-U red theme).
v2: bigger boxes / shorter labels so no text touches borders (QA fixes)."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle

RED, DARK, GREY, LIGHT = "#BE0000", "#333333", "#777777", "#F2F2F2"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 12})
OUT = r"C:\Users\peter\Desktop\EM Imaging\CNN vs MLP\presentation\assets"


def box(ax, x, y, w, h, text, fc="white", ec=DARK, fs=11.5, bold=False, lw=1.6):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.06",
                                fc=fc, ec=ec, lw=lw))
    ax.text(x + w/2, y + h/2, text, ha="center", va="center", fontsize=fs,
            color=("white" if fc == RED else DARK),
            fontweight="bold" if bold else "normal")


def arrow(ax, x0, y0, x1, y1, color=RED, lw=2.4):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>",
                                 mutation_scale=22, color=color, lw=lw))


# ------------------------------------------------------------- 1. setup flow
fig, ax = plt.subplots(figsize=(11.5, 2.1))
steps = [("Breast phantom\n+ tumor", "white"), ("4-port VNA\n0.1–8 GHz sweep", "white"),
         ("16 complex\nS-parameters", "white"), ("'AI'\nCNN / MLP", RED),
         ("Predicted\nposition", "white")]
w, h, gap = 2.05, 1.15, 0.5
x = 0.1
for i, (t, fc) in enumerate(steps):
    box(ax, x, 0.4, w, h, t, fc=fc, fs=12, bold=(fc == RED))
    if i < len(steps) - 1:
        arrow(ax, x + w + 0.05, 0.4 + h/2, x + w + gap - 0.05, 0.4 + h/2)
    x += w + gap
ax.set_xlim(0, x); ax.set_ylim(0, 2.0); ax.axis("off")
fig.savefig(f"{OUT}/setup_flow.png", dpi=200, bbox_inches="tight", transparent=True)
plt.close(fig)

# ------------------------------------------------------------- 2. CNN architecture
fig, ax = plt.subplots(figsize=(12, 3.1))
items = [("Input image\nchannels × 791\nfrequencies", "white", 1.85),
         ("Conv2D\n[4×20] × 32\nBN + ReLU", LIGHT, 1.65),
         ("Conv2D\n[2×10] × 32\nBN + ReLU", LIGHT, 1.65),
         ("Fully connected\n64, BN + ReLU\ndropout 0.3", LIGHT, 1.85),
         ("FC + softmax\nN positions", RED, 1.65)]
x = 0.1
for i, (t, fc, wd) in enumerate(items):
    box(ax, x, 0.65, wd, 1.6, t, fc=fc, fs=11.5, bold=(fc == RED))
    if i < len(items) - 1:
        arrow(ax, x + wd + 0.05, 1.45, x + wd + 0.45 - 0.05, 1.45)
    x += wd + 0.45
ax.text(0.1, 0.18, "trained with Adam · 100 epochs · batch 16 · MATLAB Deep Learning Toolbox (GPU)",
        fontsize=11.5, color=GREY, style="italic")
ax.set_xlim(0, x); ax.set_ylim(0, 2.7); ax.axis("off")
fig.savefig(f"{OUT}/cnn_arch.png", dpi=200, bbox_inches="tight", transparent=True)
plt.close(fig)

# ------------------------------------------------------------- 3. MLP architecture
fig, ax = plt.subplots(figsize=(12, 3.1))
items = [("Flattened\nfeature vector\n(one long list)", "white", 1.85),
         ("Dense 256\nReLU", LIGHT, 1.5),
         ("Dense 128\nReLU", LIGHT, 1.5),
         ("softmax\nN positions", RED, 1.55),
         ("3-seed average\n+ LogReg vote", "white", 1.85)]
x = 0.1
for i, (t, fc, wd) in enumerate(items):
    box(ax, x, 0.65, wd, 1.6, t, fc=fc, fs=11.5, bold=(fc == RED))
    if i < len(items) - 1:
        arrow(ax, x + wd + 0.05, 1.45, x + wd + 0.45 - 0.05, 1.45)
    x += wd + 0.45
ax.text(0.1, 0.18, "trained with Adam · early stopping on validation split · Python scikit-learn (CPU)",
        fontsize=11.5, color=GREY, style="italic")
ax.set_xlim(0, x); ax.set_ylim(0, 2.7); ax.axis("off")
fig.savefig(f"{OUT}/mlp_arch.png", dpi=200, bbox_inches="tight", transparent=True)
plt.close(fig)

# ------------------------------------------------------------- 4. preprocessing pipeline
fig, ax = plt.subplots(figsize=(12.4, 3.4))
steps = [("1", "Baseline\nsubtraction", "Y = S − S_baseline\nisolates the tumor's\nperturbation"),
         ("2", "Session mean\nsubtraction", "removes what a whole\nsession shares\n(setup offsets)"),
         ("3", "Input\nrepresentation", "raw | physics | TDR\nidentical for\nCNN and MLP"),
         ("4", "Per-session\nz-score", "each session scaled by\nits own statistics\n(drift robustness)")]
w, h, gap = 2.6, 2.15, 0.45
x = 0.1
for i, (n, t, d) in enumerate(steps):
    box(ax, x, 0.55, w, h, "", fc="white")
    ax.add_patch(Circle((x + 0.36, 0.55 + h - 0.42), 0.21, fc=RED, ec="none"))
    ax.text(x + 0.36, 0.55 + h - 0.425, n, ha="center", va="center", color="white",
            fontsize=13, fontweight="bold")
    ax.text(x + 0.64, 0.55 + h - 0.42, t, ha="left", va="center", fontsize=11.5,
            color=DARK, fontweight="bold")
    ax.text(x + w/2, 0.55 + (h - 0.9)/2, d, ha="center", va="center", fontsize=10.5,
            color=GREY)
    if i < len(steps) - 1:
        arrow(ax, x + w + 0.05, 0.55 + h/2, x + w + gap - 0.05, 0.55 + h/2)
    x += w + gap
ax.set_xlim(0, x); ax.set_ylim(0.2, 3.05); ax.axis("off")
fig.savefig(f"{OUT}/pipeline.png", dpi=200, bbox_inches="tight", transparent=True)
plt.close(fig)

# ------------------------------------------------------------- 5. LOSO diagram
fig, ax = plt.subplots(figsize=(11, 3.3))
sess = ["Session 1", "Session 2", "Session 3"]
for f in range(3):
    y = 2.4 - f * 0.95
    ax.text(0.05, y + 0.31, f"Fold {f+1}", fontsize=12.5, fontweight="bold", color=DARK,
            va="center")
    for s in range(3):
        xx = 1.35 + s * 2.35
        test = (s == f)
        box(ax, xx, y, 2.05, 0.62, sess[s] + ("  ·  TEST" if test else ""),
            fc=(RED if test else LIGHT), fs=11, bold=test)
    ax.text(8.6, y + 0.31, "train on the rest", fontsize=11, color=GREY, va="center",
            style="italic")
ax.text(0.05, 0.05, "Leave-One-Session-Out: the model NEVER sees the test session, "
        "so the score reflects a brand-new day of measurements", fontsize=12, color=DARK)
ax.set_xlim(0, 10.4); ax.set_ylim(-0.25, 3.25); ax.axis("off")
fig.savefig(f"{OUT}/loso.png", dpi=200, bbox_inches="tight", transparent=True)
plt.close(fig)

# ------------------------------------------------------------- 6. derived channels (real data)
import glob, os
SESS = (r"C:\Users\peter\Desktop\EM Imaging\BreastPhantom\HunterVNA\DataMeasurements"
        r"\Sam Antennas\MediumAntenna\Separated\July03\A3_F5_SamMed"
        r"\BreastPhantom_A3_F5_FishingWeight_20260703_1432")
def read_s11(path):
    raw = np.genfromtxt(path, delimiter=",", skip_header=1)
    return raw[:, 0] / 1e9, raw[:, 1] * np.exp(1j * np.deg2rad(raw[:, 2]))
f, s_obj = read_s11(os.path.join(SESS, "R3C4P1_T01.csv"))
bl = [read_s11(p)[1] for p in sorted(glob.glob(os.path.join(SESS, "baseline_T*.csv")))]
Y = s_obj - np.mean(bl, axis=0)
env = np.abs(np.fft.ifft(Y))[:64]
fig, axes = plt.subplots(1, 5, figsize=(13.5, 2.3))
panels = [(np.abs(Y), "|Y|  magnitude", f), (np.unwrap(np.angle(Y)), "∠Y  phase", f),
          (np.real(Y), "Re(Y)", f), (np.imag(Y), "Im(Y)", f),
          (env, "|IFFT(Y)|  TDR envelope", np.arange(64))]
for ax2, (yv, t, xv) in zip(axes, panels):
    ax2.plot(xv, yv, color=RED, lw=1.1)
    ax2.set_title(t, fontsize=12, color=DARK, fontweight="bold")
    ax2.tick_params(labelsize=8, colors=GREY)
    for sp in ax2.spines.values():
        sp.set_color(GREY)
    ax2.set_xlabel("GHz" if len(xv) > 100 else "time bin", fontsize=9, color=GREY)
fig.tight_layout()
fig.savefig(f"{OUT}/derived_channels.png", dpi=200, bbox_inches="tight", facecolor="white")
plt.close(fig)

print("assets v2 done")
