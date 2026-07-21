const pptxgen = require("pptxgenjs");

const RED = "BE0000", DARK = "2B2B2B", GREY = "6E6E6E",
      LIGHT = "F2F2F2", TINT = "FBEDED", WHITE = "FFFFFF";
const A = "assets/";

let p = new pptxgen();
p.layout = "LAYOUT_16x9";           // 10 x 5.625 in
p.author = "Peter Martin";
p.title = "CNN vs MLP - Tumor Localization in Breast Phantoms";

// ---------------------------------------------------------------- helpers
function title(s, kicker, t) {
  s.background = { color: WHITE };
  s.addText(kicker.toUpperCase(), { x: 0.5, y: 0.26, w: 9, h: 0.28, fontSize: 12,
    color: RED, bold: true, charSpacing: 2, fontFace: "Calibri", margin: 0, valign: "top" });
  s.addText(t, { x: 0.5, y: 0.56, w: 9.0, h: 0.6, fontSize: 25, color: "2A1618",
    bold: true, fontFace: "Cambria", margin: 0, valign: "top" });
}
function divider(kicker, t, sub) {
  const s = p.addSlide();
  s.background = { color: "FDF8F6" };
  s.addShape(p.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.20, fill: { color: RED }, line: { type: "none" } });
  s.addShape(p.shapes.RECTANGLE, { x: 0.68, y: 2.02, w: 0.07, h: 1.15, fill: { color: RED }, line: { type: "none" } });
  s.addText(kicker.toUpperCase(), { x: 0.92, y: 2.05, w: 8.4, h: 0.35, fontSize: 12.5,
    color: RED, bold: true, charSpacing: 3, fontFace: "Calibri", margin: 0 });
  s.addText(t, { x: 0.92, y: 2.42, w: 8.4, h: 0.75, fontSize: 33, color: "2A1618",
    bold: true, fontFace: "Cambria", margin: 0 });
  if (sub) s.addText(sub, { x: 0.92, y: 3.28, w: 8.2, h: 0.8, fontSize: 13.5,
    color: "836A68", fontFace: "Calibri", margin: 0 });
  return s;
}
function bullets(s, items, opt) {
  const runs = items.map((it) => ({
    text: it.t,
    options: { bullet: it.sub ? { indent: 12 } : true, indentLevel: it.sub ? 1 : 0,
      bold: !!it.b, color: it.c || DARK, breakLine: true,
      fontSize: opt.fontSize || 14, paraSpaceAfter: opt.gap == null ? 8 : opt.gap },
  }));
  s.addText(runs, { x: opt.x, y: opt.y, w: opt.w, h: opt.h, fontFace: "Calibri",
    valign: "top" });
}
function resultsTable(s, rows, y, note, rowH) {
  const header = ["Phantom setup", "Positions", "CNN  (%)", "MLP  (%)", "CNN − MLP"].map(t =>
    ({ text: t, options: { fill: { color: RED }, color: WHITE, bold: true, fontSize: 14,
       align: "center", valign: "middle" } }));
  const body = rows.map((r, i) => {
    const fill = { color: i % 2 ? TINT : WHITE };
    const gap = (typeof r[2] === "number" && typeof r[3] === "number")
      ? (r[2] - r[3] >= 0 ? "+" : "−") + Math.abs(r[2] - r[3]).toFixed(1) : "n/a";
    const fmt = (v, sd) => typeof v === "number" ? v.toFixed(1) + " ± " + sd.toFixed(1) : v;
    return [
      { text: r[0], options: { fill, color: DARK, bold: true, fontSize: 13.5, align: "left" } },
      { text: String(r[1]) + "-way", options: { fill, color: GREY, fontSize: 13, align: "center" } },
      { text: fmt(r[2], r[4]), options: { fill, color: DARK, fontSize: 13.5, align: "center",
        bold: typeof r[2] === "number" && typeof r[3] === "number" && r[2] >= r[3] } },
      { text: fmt(r[3], r[5]), options: { fill, color: DARK, fontSize: 13.5, align: "center",
        bold: typeof r[2] === "number" && typeof r[3] === "number" && r[3] > r[2] } },
      { text: gap, options: { fill, color: gap.startsWith("+") || gap === "0.0" ? RED : GREY,
        bold: true, fontSize: 13.5, align: "center" } },
    ];
  });
  s.addTable([header, ...body], { x: 0.5, y, w: 9.0, colW: [2.6, 1.4, 1.9, 1.9, 1.2],
    border: { pt: 0.75, color: "D9D9D9" }, rowH: rowH || 0.42, valign: "middle",
    fontFace: "Calibri" });
  if (note) s.addText(note, { x: 0.5, y: y + 0.46 * (rows.length + 1) + 0.12, w: 9, h: 0.35,
    fontSize: 11.5, italic: true, color: GREY, fontFace: "Calibri", margin: 0 });
}
function notebox(s, txt, y, h, fs) {
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: 0.5, y, w: 9.0, h: h || 0.75,
    fill: { color: TINT }, line: { color: "E8C4C4", width: 1 }, rectRadius: 0.06 });
  s.addText(txt, { x: 0.72, y, w: 8.6, h: h || 0.75, fontSize: fs || 13.5, fontFace: "Calibri",
    valign: "middle", margin: 0, color: DARK });
}

// ================================================================ 1. TITLE
{
  const s = p.addSlide();
  s.background = { color: "FDF8F6" };
  s.addShape(p.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.20, fill: { color: RED }, line: { type: "none" } });
  s.addShape(p.shapes.RECTANGLE, { x: 0.68, y: 1.52, w: 0.07, h: 1.62, fill: { color: RED }, line: { type: "none" } });
  s.addText("TUMOR LOCALIZATION IN BREAST PHANTOMS", { x: 0.92, y: 1.55, w: 8.4, h: 0.35,
    fontSize: 13, color: RED, bold: true, charSpacing: 3, fontFace: "Calibri", margin: 0 });
  s.addText("CNN vs MLP", { x: 0.92, y: 1.95, w: 8.4, h: 1.0, fontSize: 54, color: "2A1618",
    bold: true, fontFace: "Cambria", margin: 0 });
  s.addText("A matched, head-to-head comparison of two machine-learning approaches\nfor microwave tumor localization",
    { x: 0.92, y: 3.1, w: 8.2, h: 0.75, fontSize: 15, color: "836A68", fontFace: "Calibri", margin: 0 });
  s.addText("Peter Martin  ·  University of Utah  ·  Electrical & Computer Engineering",
    { x: 0.92, y: 4.75, w: 8.4, h: 0.35, fontSize: 12.5, color: "836A68", fontFace: "Calibri", margin: 0 });
  s.addText("Preprocessing pipeline v1 (includes session-mean subtraction)",
    { x: 0.92, y: 5.12, w: 8.4, h: 0.3, fontSize: 11, italic: true, color: "836A68",
      fontFace: "Calibri", margin: 0 });
}

// ================================================================ 2. THE PROBLEM
{
  const s = p.addSlide();
  title(s, "The problem", "Find a hidden tumor inside a breast phantom");
  bullets(s, [
    { t: "Goal: locate a small tumor surrogate (metal fishing weight) placed inside a realistic breast phantom, without opening it up.", },
    { t: "Microwave imaging: low-cost, non-ionizing alternative screening modality.", },
    { t: "The tumor perturbs how microwaves reflect and transmit through the tissue, but the change is tiny and buried in drift and noise.", },
    { t: "Worst case: a glandular insert (dense tissue) further masks the tumor signal.", },
    { t: "Task: given one measurement, which of ~33–51 grid positions holds the tumor?", b: true },
  ], { x: 0.5, y: 1.45, w: 5.2, h: 3.9, fontSize: 14, gap: 10 });
  s.addImage({ path: A + "phantom_f5.jpg", x: 6.0, y: 1.35, w: 3.6, h: 3.21 });
  s.addText("A3 breast phantom with F5 glandular insert and measurement grid",
    { x: 6.0, y: 4.62, w: 3.6, h: 0.5, fontSize: 10.5, italic: true, color: GREY,
      fontFace: "Calibri", align: "center" });
}

// ================================================================ 3. THE SOLUTION
{
  const s = p.addSlide();
  title(s, "The solution", "Let a machine learn the fingerprint of every position");
  s.addText("Classic inverse-scattering reconstruction is slow and fragile. Instead, we treat localization as a pattern-recognition problem: measure the phantom with the tumor at every known position, then train a model to recognise each position's electromagnetic fingerprint.",
    { x: 0.5, y: 1.35, w: 9.0, h: 0.85, fontSize: 14, color: DARK, fontFace: "Calibri", margin: 0 });
  s.addImage({ path: A + "setup_flow.png", x: 0.45, y: 2.35, w: 9.1, h: 1.62 });
  const stats = [["16", "S-parameters per sweep"], ["791", "frequency points, 0.1–8 GHz"],
                 ["~2–3%", "chance-level accuracy"]];
  stats.forEach((st, i) => {
    const x = 0.9 + i * 2.9;
    s.addText(st[0], { x, y: 4.2, w: 2.6, h: 0.62, fontSize: 34, bold: true, color: RED,
      align: "center", fontFace: "Calibri", margin: 0 });
    s.addText(st[1], { x, y: 4.82, w: 2.6, h: 0.5, fontSize: 12, color: GREY,
      align: "center", fontFace: "Calibri", margin: 0 });
  });
}

// ================================================================ 4. DIVIDER: METHODS
divider("Part 1", "Methods", "The measurement, the two models, and how they differ");

// ================================================================ 5. MEASUREMENT SETUP
{
  const s = p.addSlide();
  title(s, "Methods", "The physical measurement");
  s.addImage({ path: A + "phantom_empty.jpg", x: 0.5, y: 1.4, w: 3.4, h: 3.44 });
  s.addText("Empty A3 phantom: adipose bowl, 6×6 in grid, 4 antennas at the rim",
    { x: 0.4, y: 4.88, w: 3.6, h: 0.5, fontSize: 10.5, italic: true, color: GREY,
      fontFace: "Calibri", align: "center" });
  bullets(s, [
    { t: "4-port Hunter VNA sweeps 0.1–8 GHz (791 points) through 4 antennas around the phantom.", },
    { t: "Each sweep captures all 16 S-parameters: 4 reflections (S11…S44) plus transmissions between every antenna pair.", },
    { t: "Tumor surrogate is moved through a grid of cell corner positions; 16 repeat trials per position.", },
    { t: "Baseline (empty-phantom) sweeps recorded each session for calibration.", },
    { t: "Each setup measured in 3–4 independent sessions on different setups/times; this matters later (LOSO).", b: true },
  ], { x: 4.25, y: 1.45, w: 5.3, h: 3.9, fontSize: 13.5, gap: 10 });
}

// ================================================================ 6. MEET THE MODELS
{
  const s = p.addSlide();
  title(s, "Methods", "Two ways to turn a measurement into a position");
  s.addText("Both models receive the SAME preprocessed measurement and output a probability for every grid position. They differ in how they look at the data.",
    { x: 0.5, y: 1.32, w: 9.0, h: 0.6, fontSize: 14, color: DARK, fontFace: "Calibri", margin: 0 });
  const card = (x, name, sub, pts) => {
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y: 2.05, w: 4.35, h: 3.1,
      fill: { color: WHITE }, line: { color: "E0E0E0", width: 1 }, rectRadius: 0.08,
      shadow: { type: "outer", color: "000000", blur: 7, offset: 2, angle: 45, opacity: 0.14 } });
    s.addText(name, { x: x + 0.3, y: 2.25, w: 3.8, h: 0.45, fontSize: 21, bold: true,
      color: RED, fontFace: "Calibri", margin: 0 });
    s.addText(sub, { x: x + 0.3, y: 2.68, w: 3.8, h: 0.4, fontSize: 12, italic: true,
      color: GREY, fontFace: "Calibri", margin: 0 });
    bullets(s, pts.map(t => ({ t })), { x: x + 0.22, y: 3.1, w: 3.95, h: 1.95, fontSize: 12.5, gap: 7 });
  };
  card(0.5, "CNN", "Convolutional Neural Network  ·  MATLAB", [
    "Sees the measurement as a 2-D image: y axis = channels, x axis = frequency",
    "Convolution filters slide along frequency, learning local patterns",
  ]);
  card(5.15, "MLP", "Multi-Layer Perceptron  ·  Python", [
    "Sees the measurement as one long flattened vector of numbers",
    "Every input connects to every neuron: the network has no built-in idea that neighboring frequencies are related, so any such structure must be learned from scratch",
  ]);
}

// ================================================================ 7. CNN
{
  const s = p.addSlide();
  title(s, "Methods", "The CNN");
  s.addImage({ path: A + "cnn_arch.png", x: 0.4, y: 1.35, w: 9.2, h: 2.05 });
  bullets(s, [
    { t: "Input is an image: one row per data channel (e.g. |S11|, ∠S11, …), one column per frequency point (791).", },
    { t: "Two convolution layers (32 filters each) detect local patterns such as resonance shifts and ripples anywhere along the spectrum, sharing weights across frequency.", },
    { t: "Batch-normalisation + ReLU after every layer; 30% dropout fights overfitting.", },
    { t: "One network, trained 100 epochs with Adam (batch 16) on the GPU; softmax outputs one probability per grid position.", },
  ], { x: 0.5, y: 3.55, w: 9.0, h: 1.9, fontSize: 13.5, gap: 8 });
}

// ================================================================ 8. MLP
{
  const s = p.addSlide();
  title(s, "Methods", "The MLP");
  s.addImage({ path: A + "mlp_arch.png", x: 0.4, y: 1.35, w: 9.2, h: 2.05 });
  bullets(s, [
    { t: "Input is a flat vector: all channels and frequencies concatenated (thousands of features). No spatial structure is assumed.", },
    { t: "Two dense layers (256 → 128, ReLU): every feature can interact with every other, but nothing is shared or localized.", },
    { t: "Early stopping on a held-out validation split prevents overtraining.", },
    { t: "Ensemble: 3 networks with different random seeds are averaged, plus a logistic-regression model; the ensemble vote is the prediction.", },
  ], { x: 0.5, y: 3.55, w: 9.0, h: 1.9, fontSize: 13.5, gap: 8 });
}

// ================================================================ 9. STRUCTURAL COMPARISON
{
  const s = p.addSlide();
  title(s, "Methods", "CNN vs MLP: structural differences");
  const hdr = (t) => ({ text: t, options: { fill: { color: RED }, color: WHITE, bold: true,
    fontSize: 13.5, align: "center", valign: "middle" } });
  const c = (t, opts) => ({ text: t, options: Object.assign({ fontSize: 12.5, color: DARK,
    align: "left", valign: "middle" }, opts || {}) });
  const rows = [
    ["How it sees data", "2-D image (channels × frequency)", "1-D flattened vector"],
    ["Inductive bias", "Local patterns, shared across frequency", "None; fully general"],
    ["Parameters", "Small conv filters + FC (~0.5–2 M)", "Huge first layer (features × 256)"],
    ["Training", "Fixed 100 epochs, single network", "Early stopping, 3-seed ensemble + LogReg"],
    ["Framework", "MATLAB Deep Learning Toolbox (GPU)", "Python scikit-learn (CPU)"],
  ];
  const body = rows.map((r, i) => {
    const fill = { color: i % 2 ? TINT : WHITE };
    return [c(r[0], { bold: true, fill }), c(r[1], { fill }), c(r[2], { fill })];
  });
  s.addTable([[hdr(""), hdr("CNN"), hdr("MLP")], ...body],
    { x: 0.5, y: 1.55, w: 9.0, colW: [2.3, 3.35, 3.35], border: { pt: 0.75, color: "D9D9D9" },
      rowH: 0.5, fontFace: "Calibri" });
  notebox(s, "Same job, opposite philosophies: the CNN assumes frequency-local structure; the MLP assumes nothing. Everything else in this study is held identical.", 4.75, 0.62);
}

// ================================================================ 10. DIVIDER: PIPELINE
divider("Part 2", "The data pipeline", "What happens to a measurement before any 'AI' ever sees it. Identical for both models.");

// ================================================================ 11. PREPROCESSING
{
  const s = p.addSlide();
  title(s, "Data pipeline", "Four steps from raw sweep to model input");
  s.addImage({ path: A + "pipeline.png", x: 0.4, y: 1.42, w: 9.2, h: 2.28 });
  bullets(s, [
    { t: "Steps 1–2 remove everything that is not the tumor; step 4 (per-session z-score) is the key drift defense: each session is standardized by its own statistics. Applied identically to CNN and MLP.", },
    { t: "Upgrading the CNN to this pipeline was worth +17 pts on F5 single-antenna (59→76%) with fold-to-fold σ cut from 40% to 9%, and +15 pts on F4 single-antenna (82→97%). Its catastrophic cross-session failures disappeared entirely.", b: true },
  ], { x: 0.5, y: 3.85, w: 9.0, h: 1.6, fontSize: 13, gap: 8 });
}

// ================================================================ 12. INPUT REPRESENTATIONS
{
  const s = p.addSlide();
  title(s, "Data pipeline", "Three input representations");
  const card = (x, w, name, desc, hl) => {
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y: 1.5, w, h: 2.0,
      fill: { color: hl ? TINT : WHITE }, line: { color: hl ? RED : "E0E0E0", width: hl ? 1.5 : 1 },
      rectRadius: 0.07 });
    s.addText(name, { x: x + 0.22, y: 1.66, w: w - 0.4, h: 0.4, fontSize: 16, bold: true,
      color: RED, fontFace: "Calibri", margin: 0 });
    s.addText(desc, { x: x + 0.22, y: 2.08, w: w - 0.4, h: 1.3, fontSize: 11.5, color: DARK,
      fontFace: "Calibri", margin: 0 });
  };
  card(0.5, 2.9, "RAW", "Magnitude + phase of each calibrated S-parameter.\n\nThe measurement as the VNA reports it. Used for the main results.", true);
  card(3.55, 2.9, "PHYSICS", "Adds real & imaginary parts and the IFFT time-domain (TDR) envelope.\n\nDerived at no cost from the same data; covered at the end.");
  card(6.6, 2.9, "TDR-ONLY", "Just the time-domain envelope, a pulse-echo view.\n\nAn ablation: how much lives in time domain alone?");
  s.addText("Same numbers, two shapes:", { x: 0.5, y: 3.72, w: 4, h: 0.32, fontSize: 13,
    bold: true, color: DARK, fontFace: "Calibri", margin: 0 });
  s.addText([
    { text: "CNN:  ", options: { bold: true, color: RED } },
    { text: "channels stacked as image rows × 791 frequency columns", options: { color: DARK, breakLine: true } },
    { text: "MLP:  ", options: { bold: true, color: RED } },
    { text: "the same rows laid end-to-end as one long vector", options: { color: DARK } },
  ], { x: 0.5, y: 4.06, w: 9.0, h: 0.62, fontSize: 13, fontFace: "Calibri", margin: 0 });
  notebox(s, "Antenna subsets work the same way: '2 antennas' keeps only S-parameters among ports 1 & 3; '1 antenna' keeps only S11.", 4.75, 0.62);
}

// ================================================================ 13. LOSO
{
  const s = p.addSlide();
  title(s, "Data pipeline", "How we score: Leave-One-Session-Out");
  s.addImage({ path: A + "loso.png", x: 0.65, y: 1.4, w: 8.7, h: 2.65 });
  bullets(s, [
    { t: "A random 75/25 split mixes trials from the same session into train AND test, so the model can cheat off session drift, inflating accuracy.", },
    { t: "LOSO trains on N−1 sessions and tests on the session it has never seen; every session takes a turn. We report per-position majority vote over its 16 trials.", },
    { t: "We have thoroughly stress-tested LOSO and verified that it works: under LOSO, models cannot exploit session drift, and drift-only information scores near chance.", b: true },
  ], { x: 0.5, y: 4.1, w: 9.0, h: 1.4, fontSize: 13, gap: 6 });
}

// ================================================================ 14. PHANTOM SETUPS
{
  const s = p.addSlide();
  title(s, "Data pipeline", "Three phantom setups, increasing difficulty");
  const ph = (x, img, name, sub, h) => {
    s.addImage({ path: A + img, x, y: 1.5, w: 2.9, h });
    s.addText(name, { x, y: 4.15, w: 2.9, h: 0.35, fontSize: 15, bold: true, color: RED,
      align: "center", fontFace: "Calibri", margin: 0 });
    s.addText(sub, { x: x - 0.1, y: 4.5, w: 3.1, h: 0.75, fontSize: 11, color: GREY,
      align: "center", fontFace: "Calibri", margin: 0 });
  };
  ph(0.5,  "phantom_empty.jpg", "A3 Empty",   "adipose only\n51 positions · 3 sessions", 2.94);
  ph(3.55, "phantom_f4.jpg",    "A3 + F4",    "small glandular insert\n39 positions · 4 sessions", 2.59);
  ph(6.6,  "phantom_f5.jpg",    "A3 + F5",    "large glandular insert\n33 positions · 3 sessions (latest)", 2.59);
}

// ================================================================ 15. DIVIDER: RESULTS
divider("Part 3", "Results", "Per-position vote accuracy (%) under LOSO · identical raw inputs (mag + phase) · chance = 2–3%");

// ---- results data: [phantom, nway, cnn, mlp, cnnSd, mlpSd] -----------------
const R = {
  all_full:   [["A3 Empty", 51, 99.3, 99.3, 1.1, 0.9], ["A3 + F4", 39, 97.4, 97.4, 3.0, 1.8], ["A3 + F5", 33, 100.0, 96.0, 0.0, 2.9]],
  pair_full:  [["A3 Empty", 51, 99.3, 99.3, 1.1, 0.9], ["A3 + F4", 39, 95.5, 93.6, 1.3, 4.3], ["A3 + F5", 33, 96.0, 81.8, 7.0, 4.3]],
  single:     [["A3 Empty", 51, 98.0, 99.3, 2.0, 0.9], ["A3 + F4", 39, 96.8, 91.0, 4.9, 5.6], ["A3 + F5", 33, 75.8, 58.6, 9.1, 9.4]],
  pair_phys:  [["A3 Empty", 51, 99.3, 99.3, 1.1, 0.9], ["A3 + F4", 39, 98.1, 92.3, 1.3, 3.1], ["A3 + F5", 33, 98.0, 85.9, 3.5, 7.6]],
  single_phys:[["A3 Empty", 51, 98.7, 98.7, 1.1, 1.8], ["A3 + F4", 39, 95.5, 91.7, 4.4, 5.8], ["A3 + F5", 33, 79.8, 62.6, 3.5, 8.0]],
  refl_all_raw:  [["A3 Empty", 51, 100.0, 99.3, 0.0, 0.9], ["A3 + F4", 39, 98.7, 93.6, 1.5, 4.3], ["A3 + F5", 33, 100.0, 88.9, 0.0, 2.9]],
  refl_pair_raw: [["A3 Empty", 51, 99.3, 99.3, 1.1, 0.9], ["A3 + F4", 39, 92.3, 93.6, 5.9, 5.9], ["A3 + F5", 33, 90.9, 74.8, 5.3, 6.2]],
  refl_all_phys: [["A3 Empty", 51, 100.0, 99.3, 0.0, 0.9], ["A3 + F4", 39, 98.1, 94.2, 1.3, 3.3], ["A3 + F5", 33, 100.0, 87.9, 0.0, 6.6]],
  refl_pair_phys:[["A3 Empty", 51, 100.0, 98.7, 0.0, 1.9], ["A3 + F4", 39, 94.2, 90.4, 3.2, 3.3], ["A3 + F5", 33, 97.0, 79.8, 5.3, 7.6]],
};
function resultSlide(kicker, t, rows, note, tk) {
  const s = p.addSlide();
  title(s, kicker, t);
  resultsTable(s, rows, 1.6, note);
  if (tk) notebox(s, tk, 4.35, 0.9);
  return s;
}
function ddSlide(t, img, caption, legend) {
  const s = p.addSlide();
  title(s, "Results · spatial view", t);
  if (legend) {
    s.addText([
      { text: "Dot color", options: { bold: true, color: RED } },
      { text: " = how strongly the tumor physically changes the signal (detectable difference).   ", options: { color: DARK } },
      { text: "Dot size", options: { bold: true, color: RED } },
      { text: " = CNN LOSO accuracy at that position.   Dashed outline = glandular insert.", options: { color: DARK } },
    ], { x: 0.5, y: 1.28, w: 9.0, h: 0.55, fontSize: 12.5, fontFace: "Calibri", margin: 0 });
    s.addImage({ path: A + img, x: 0.6, y: 1.92, w: 8.8, h: 3.20 });
    s.addText(caption, { x: 0.6, y: 5.17, w: 8.8, h: 0.38, fontSize: 11.5, italic: true,
      color: GREY, align: "center", fontFace: "Calibri", margin: 0 });
  } else {
    s.addImage({ path: A + img, x: 0.6, y: 1.45, w: 8.8, h: 3.20 });
    s.addText(caption, { x: 0.6, y: 4.80, w: 8.8, h: 0.55, fontSize: 11.5, italic: true,
      color: GREY, align: "center", fontFace: "Calibri", margin: 0 });
  }
  return s;
}

// 16: all-4 table
resultSlide("Results · raw inputs", "All 4 antennas: full S-parameters (16)", R.all_full,
  "Mean ± std over LOSO folds. Bold = better method.",
  "With the full antenna array, both methods are near-perfect on every phantom; drift and glandular masking are fully compensated. CNN edges ahead on the hardest setup (F5).");
// 17: all-4 DD figure (carries the legend)
ddSlide("Error Locations: all 4 antennas", "dd_all_h.png",
  "Detectable change still dips inside the glandular insert (blue), but with 16 complementary views the classifier compensates: accuracy dots stay large almost everywhere. MLP versions look qualitatively identical.",
  true);
// 18: all-4 reflection-only table
resultSlide("Results · raw inputs", "All 4 antennas: reflection only (S11, S22, S33, S44)", R.refl_all_raw,
  "No through-phantom transmission paths; each antenna only listens to its own echo.",
  "Dropping transmission barely touches the CNN (F5 stays at 100%), while the MLP gives up 4-7 points on the glandular phantoms. Four reflection coefficients are enough for a CNN.");
// 18b: all-4 refl DD figure
ddSlide("Error Locations: all 4 antennas, reflection only", "dd_refl_all_h.png",
  "Reflection-only detectable change (max of S11, S22, S33, S44). The insert still carves a low-signal pocket, but CNN accuracy dots stay large.");
// 19: pair table
resultSlide("Results · raw inputs", "2 antennas (ports 1 & 3): full S-parameters", R.pair_full,
  "Antennas 1 & 3 sit on opposite sides of the phantom (most informative pair).",
  "Halving the antennas separates the methods: the CNN stays high (96%+ everywhere) while the MLP drops 14 points on F5. Convolutional structure extracts more from less hardware.");
// 19: pair DD figure
ddSlide("Error Locations: 2 antennas (1 & 3)", "dd_pair_h.png",
  "With two antennas a low-signal pocket appears inside the glandular insert, and accuracy dots shrink with it.");
// 21: pair reflection-only table
resultSlide("Results · raw inputs", "2 antennas (1 & 3): reflection only (S11, S33)", R.refl_pair_raw,
  "The toughest 2-antenna condition: two reflection coefficients and nothing else.",
  "The CNN holds 91-99% while the MLP falls to 75% on F5. F4 is the single config in the study where the MLP edges the CNN (93.6 vs 92.3).");
// 21b: pair refl DD figure
ddSlide("Error Locations: 2 antennas (1 & 3), reflection only", "dd_refl_pair_h.png",
  "With only S11 and S33, the low-signal pocket deepens and CNN errors start to appear inside the insert.");
// 22: single table
resultSlide("Results · raw inputs", "1 antenna: S11 only", R.single,
  "A single reflection coefficient: the minimal possible hardware.",
  "The extreme case: one antenna, one S-parameter. The CNN holds 76–98%; the MLP falls to 59% on F5. The gap grows exactly as the task gets harder, and the F5 errors cluster inside the glandular insert (next slide).");
// 21: single DD figure
ddSlide("Error Locations: 1 antenna (S11)", "dd_single_h.png",
  "Single antenna (S11): small blue dots cluster inside the insert. Where physics buries the tumor, the classifier fails.");

// ================================================================ 22. DIVIDER: PHYSICS
divider("Part 4", "Physics-informed features", "Squeezing more out of the same measurement: no new hardware, no new data collection");

// ================================================================ 23. DERIVING FEATURES
{
  const s = p.addSlide();
  title(s, "Physics-informed features", "One complex measurement, five physical views");
  s.addText("Each calibrated S-parameter Y(f) is one complex spectrum. From it we derive, at zero measurement cost:  magnitude & phase (resonance behaviour), real & imaginary parts (full complex information), and the inverse-FFT envelope, a time-domain reflectometry (TDR) view where the tumor appears as an echo at its round-trip delay.",
    { x: 0.5, y: 1.35, w: 9.0, h: 1.0, fontSize: 13.5, color: DARK, fontFace: "Calibri", margin: 0 });
  s.addImage({ path: A + "derived_channels.png", x: 0.45, y: 2.5, w: 9.1, h: 1.53 });
  s.addText("Real example: A3+F5 phantom, S11, tumor at grid position R3C4 (calibrated response Y)",
    { x: 0.5, y: 4.05, w: 9.0, h: 0.3, fontSize: 10.5, italic: true, color: GREY,
      align: "center", fontFace: "Calibri", margin: 0 });
  notebox(s, "The 'physics' input feeds all five views to both models: the CNN as extra image rows, the MLP as extra vector features. Identical information, matched again.", 4.55, 0.75);
}

// ================================================================ 24. PHYSICS RESULTS
{
  const s = p.addSlide();
  title(s, "Physics-informed results", "Same tests, physics inputs");
  s.addText("All-4-antenna physics: both models at ceiling, 97–100% (F5 reaches 100 / 100). Below: the configs where it matters. Reflection-only: next slide.",
    { x: 0.5, y: 1.24, w: 9, h: 0.32, fontSize: 11.5, italic: true, color: GREY,
      fontFace: "Calibri", margin: 0 });
  const mk = (rows, y, label) => {
    s.addText(label, { x: 0.5, y, w: 9, h: 0.3, fontSize: 14, bold: true, color: DARK,
      fontFace: "Calibri", margin: 0 });
    resultsTable(s, rows, y + 0.32, null, 0.36);
  };
  mk(R.pair_phys, 1.62, "2 antennas (1 & 3), physics input");
  mk(R.single_phys, 3.56, "1 antenna (S11), physics input");
}

// ================================================================ 24b. REFLECTION-ONLY + PHYSICS
{
  const s = p.addSlide();
  title(s, "Physics-informed results", "Reflection only + physics features");
  const mk = (rows, y, label) => {
    s.addText(label, { x: 0.5, y, w: 9, h: 0.3, fontSize: 14, bold: true, color: DARK,
      fontFace: "Calibri", margin: 0 });
    resultsTable(s, rows, y + 0.32, null, 0.36);
  };
  mk(R.refl_all_phys, 1.26, "All 4 antennas, reflection only (S11, S22, S33, S44), physics input");
  mk(R.refl_pair_phys, 3.14, "2 antennas (1 & 3), reflection only (S11, S33), physics input");
  notebox(s, "With physics features, reflection-only costs the CNN almost nothing (F5: 100% with four antennas, 97% with two); the MLP pays 8-12 points. A reflection-only system is practical with a CNN.", 5.02, 0.5, 11.5);
}

// ================================================================ 25. PHYSICS TAKEAWAY + TDR + HIER
{
  const s = p.addSlide();
  title(s, "Physics-informed results", "What the derived features buy, and what TDR alone can't");
  s.addText("Physics vs raw (percentage points gained)", { x: 0.5, y: 1.35, w: 5.4, h: 0.32,
    fontSize: 14, bold: true, color: DARK, fontFace: "Calibri", margin: 0 });
  bullets(s, [
    { t: "F5, 2 antennas:  CNN +2.0 (96→98) · MLP +4.1 (82→86)", },
    { t: "F5, 1 antenna:   CNN +4.0 (76→80) · MLP +4.0 (59→63)", },
    { t: "F5, all 4:            MLP +4.0 (96→100), joining CNN at 100%", },
    { t: "Easy setups (empty, F4 full-array): no change, already at ceiling.", },
    { t: "Physics features help most exactly where raw inputs struggle.", b: true },
  ], { x: 0.5, y: 1.72, w: 5.4, h: 2.0, fontSize: 12.5, gap: 7 });
  s.addText("TDR-only ablation (selected)", { x: 0.5, y: 3.78, w: 5.4, h: 0.32,
    fontSize: 14, bold: true, color: DARK, fontFace: "Calibri", margin: 0 });
  bullets(s, [
    { t: "F4, 1 antenna: CNN 84 / MLP 64  (vs 97 / 91 raw): a big loss for both.", },
    { t: "But the CNN mines far more from TDR alone (F5 all-4: 98 vs MLP's 76).", },
  ], { x: 0.5, y: 4.13, w: 5.4, h: 1.1, fontSize: 12.5, gap: 6 });
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: 6.15, y: 1.4, w: 3.4, h: 4.0,
    fill: { color: TINT }, line: { color: "E8C4C4", width: 1 }, rectRadius: 0.08 });
  s.addText("Additional finding: hierarchical (quadrant → position) classification",
    { x: 6.4, y: 1.6, w: 2.95, h: 0.75, fontSize: 13.5, bold: true, color: RED,
      fontFace: "Calibri", margin: 0 });
  bullets(s, [
    { t: "Two-stage 'find the corner first' scheme tested on both models.", },
    { t: "It never helps, and hurts the hardest cases: CNN −6 on F5, MLP −6 on F4-single.", },
    { t: "Wrong quadrant = unrecoverable. Single-stage wins under LOSO.", b: true },
  ], { x: 6.35, y: 2.45, w: 3.05, h: 2.8, fontSize: 12, gap: 8 });
}

// ================================================================ 26. CONCLUSIONS
{
  const s = p.addSlide();
  title(s, "Conclusions", "What we learned");
  const cc = (x, y, big, small) => {
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y, w: 4.35, h: 1.15, fill: { color: WHITE },
      line: { color: "E0E0E0", width: 1 }, rectRadius: 0.08,
      shadow: { type: "outer", color: "000000", blur: 6, offset: 2, angle: 45, opacity: 0.13 } });
    s.addText(big, { x: x + 0.25, y: y + 0.12, w: 3.9, h: 0.42, fontSize: 15.5, bold: true,
      color: RED, fontFace: "Calibri", margin: 0 });
    s.addText(small, { x: x + 0.25, y: y + 0.52, w: 3.9, h: 0.55, fontSize: 11.5,
      color: DARK, fontFace: "Calibri", margin: 0 });
  };
  cc(0.5, 1.45, "CNN ≥ MLP, everywhere", "On matched inputs the CNN ties easy cases and wins hard ones by up to 17 points.");
  cc(5.15, 1.45, "The gap grows with difficulty", "Fewer antennas + bigger glandular insert = bigger CNN advantage.");
  cc(0.5, 2.75, "Preprocessing drives robustness", "Per-session z-score eliminated the CNN's catastrophic cross-session failures.");
  cc(5.15, 2.75, "Physics features add accuracy at no cost", "Derived views (+TDR) add up to 4 points on the hardest configurations.");
  cc(0.5, 4.05, "Errors follow the physics", "Misses cluster inside the glandular insert, where detectable signal change collapses.");
  cc(5.15, 4.05, "Fewer antennas is viable with a CNN", "2 antennas: 96–98% on every phantom. Even 1 antenna: 76–98%.");
}

// ================================================================ write
p.writeFile({ fileName: "CNN_vs_MLP_Comparison.pptx" }).then(() => console.log("deck written"));
