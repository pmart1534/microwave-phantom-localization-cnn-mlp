// Frequency-reduction (bandwidth) study deck - same cream/serif U-red theme
// as the CNN-vs-MLP classification decks.  ->  Frequency_Reduction.pptx
const pptxgen = require("pptxgenjs");

const RED = "BE0000", DARK = "2B2B2B", GREY = "6E6E6E", INK = "2A1618",
      MUTE = "836A68", TINT = "FBEDED", WHITE = "FFFFFF", CREAM = "FDF8F6";
const A = "assets/";

let p = new pptxgen();
p.layout = "LAYOUT_16x9";
p.author = "Peter Martin";
p.title = "Frequency Reduction - Tumor Localization Chip Study";

function title(s, kicker, t) {
  s.background = { color: WHITE };
  s.addText(kicker.toUpperCase(), { x: 0.5, y: 0.26, w: 9, h: 0.28, fontSize: 12,
    color: RED, bold: true, charSpacing: 2, fontFace: "Calibri", margin: 0, valign: "top" });
  s.addText(t, { x: 0.5, y: 0.56, w: 9.0, h: 0.6, fontSize: 25, color: INK,
    bold: true, fontFace: "Cambria", margin: 0, valign: "top" });
}
function notebox(s, txt, y, h, fs) {
  s.addShape(p.shapes.ROUNDED_RECTANGLE, { x: 0.5, y, w: 9.0, h: h || 0.75,
    fill: { color: TINT }, line: { color: "E8C4C4", width: 1 }, rectRadius: 0.06 });
  s.addText(txt, { x: 0.72, y, w: 8.6, h: h || 0.75, fontSize: fs || 13.5,
    fontFace: "Calibri", valign: "middle", margin: 0, color: DARK });
}
// band table: rows = [label, width, empty, f4, f5, hl]
function bandTable(s, rows, y, note, rowH) {
  const hdr = ["Band (GHz)", "Width", "Empty", "A3 + F4", "A3 + F5"].map(t =>
    ({ text: t, options: { fill: { color: RED }, color: WHITE, bold: true, fontSize: 13.5,
       align: "center", valign: "middle" } }));
  const body = rows.map((r, i) => {
    const fill = { color: r[5] ? TINT : (i % 2 ? "FAFAFA" : WHITE) };
    const c = (v, b) => ({ text: typeof v === "number" ? v.toFixed(1) : String(v),
      options: { fill, color: DARK, fontSize: 13, align: "center", bold: !!b } });
    return [
      { text: r[0], options: { fill, color: r[5] ? RED : DARK, bold: true, fontSize: 13, align: "left" } },
      { text: r[1], options: { fill, color: GREY, fontSize: 12.5, align: "center" } },
      c(r[2], r[5]), c(r[3], r[5]), c(r[4], r[5]),
    ];
  });
  s.addTable([hdr, ...body], { x: 0.5, y, w: 9.0, colW: [2.4, 1.3, 1.7, 1.8, 1.8],
    border: { pt: 0.75, color: "D9D9D9" }, rowH: rowH || 0.4, valign: "middle",
    fontFace: "Calibri" });
  if (note) s.addText(note, { x: 0.5, y: y + (rowH || 0.4) * (rows.length + 1) + 0.1,
    w: 9, h: 0.32, fontSize: 11, italic: true, color: GREY, fontFace: "Calibri", margin: 0 });
}

// ================================================================ 1. TITLE
{
  const s = p.addSlide();
  s.background = { color: CREAM };
  s.addShape(p.shapes.RECTANGLE, { x: 0, y: 0, w: 10, h: 0.20, fill: { color: RED }, line: { type: "none" } });
  s.addShape(p.shapes.RECTANGLE, { x: 0.68, y: 1.32, w: 0.07, h: 1.55, fill: { color: RED }, line: { type: "none" } });
  s.addText("TUMOR LOCALIZATION · CHIP-DESIGN STUDY", { x: 0.92, y: 1.35, w: 8.4, h: 0.35,
    fontSize: 13, color: RED, bold: true, charSpacing: 3, fontFace: "Calibri", margin: 0 });
  s.addText("Frequency Reduction", { x: 0.92, y: 1.75, w: 8.4, h: 0.9, fontSize: 48,
    color: INK, bold: true, fontFace: "Cambria", margin: 0 });
  s.addText("How narrow can the measurement band go before localization degrades?\nCNN classification · raw S-parameters · LOSO · measured A3 phantom data",
    { x: 0.92, y: 2.85, w: 8.2, h: 0.75, fontSize: 14.5, color: MUTE, fontFace: "Calibri", margin: 0 });
  const stats = [["1–5 GHz", "matches full-band accuracy"], ["1/2", "the bandwidth of the full sweep"], ["100%", "F5 accuracy retained (full array)"]];
  stats.forEach((st, i) => {
    const x = 0.92 + i * 2.95;
    s.addText(st[0], { x, y: 4.0, w: 2.7, h: 0.55, fontSize: 27, bold: true, color: RED,
      fontFace: "Cambria", margin: 0 });
    s.addText(st[1], { x, y: 4.55, w: 2.7, h: 0.5, fontSize: 11.5, color: MUTE,
      fontFace: "Calibri", margin: 0 });
  });
  s.addText("Peter Martin  ·  University of Utah  ·  Electrical & Computer Engineering",
    { x: 0.92, y: 5.15, w: 8.4, h: 0.3, fontSize: 11.5, color: MUTE, fontFace: "Calibri", margin: 0 });
}

// ================================================================ 2. WHY + METHOD
{
  const s = p.addSlide();
  title(s, "Motivation", "Smaller bandwidth, simpler chip");
  s.addText("An integrated version of this system lives or dies on front-end complexity: a narrower sweep means simpler synthesizers, antennas and calibration. The question is what accuracy that costs, and where the band should sit.",
    { x: 0.5, y: 1.35, w: 9.0, h: 0.75, fontSize: 14, color: DARK, fontFace: "Calibri", margin: 0 });
  const step = (n, t, d, y) => {
    s.addShape(p.shapes.OVAL, { x: 0.6, y: y + 0.03, w: 0.42, h: 0.42, fill: { color: RED } });
    s.addText(n, { x: 0.6, y: y + 0.03, w: 0.42, h: 0.42, align: "center", valign: "middle",
      fontSize: 15, bold: true, color: WHITE, fontFace: "Cambria", margin: 0 });
    s.addText(t, { x: 1.2, y, w: 2.9, h: 0.5, fontSize: 14.5, bold: true, color: INK,
      fontFace: "Calibri", margin: 0, valign: "middle" });
    s.addText(d, { x: 4.2, y, w: 5.3, h: 0.5, fontSize: 12.5, color: DARK,
      fontFace: "Calibri", margin: 0, valign: "middle" });
  };
  step("1", "WHERE does the information live?", "slide a 2 GHz window across 0.1–8 GHz; full 4-antenna array", 2.35);
  step("2", "HOW WIDE must the band be?", "expand 2 → 3 → 4 → 5 GHz around the winning region", 3.0);
  step("3", "Does it combine with reduced hardware?", "winning band × fewer antennas / reflection-only", 3.65);
  step("4", "Is the band choice robust?", "repeat the whole sweep with a single antenna (S11 only)", 4.3);
  s.addText("Every cell: CNN classifier, raw mag+phase input, 100-epoch leave-one-session-out, per-position vote.",
    { x: 0.5, y: 4.95, w: 9, h: 0.35, fontSize: 11.5, italic: true, color: GREY,
      fontFace: "Calibri", margin: 0 });
}

// ================================================================ 3. WHERE
{
  const s = p.addSlide();
  title(s, "Step 1 · band placement", "A 2 GHz window slid across the sweep");
  bandTable(s, [
    ["0.1 – 2", "2 GHz", 99.4, 96.2, 90.9, false],
    ["2 – 4", "2 GHz", 99.4, 97.4, 92.9, true],
    ["4 – 6", "2 GHz", 99.4, 89.1, 71.7, false],
    ["6 – 8", "2 GHz", 99.4, 97.4, 69.7, false],
    ["0.1 – 8 (full)", "7.9 GHz", 99.3, 97.4, 100.0, false],
  ], 1.55, "All 16 S-parameters. LOSO per-position vote accuracy (%). Highlighted row = best 2 GHz window (mean across phantoms).");
  notebox(s, "2-4 GHz is the highest-scoring 2 GHz window. Above 4 GHz, F5 drops to ~70%. The empty phantom scores 99.4 in every window.", 4.5, 0.85, 13);
}

// ================================================================ 4. HOW WIDE
{
  const s = p.addSlide();
  title(s, "Step 2 · bandwidth", "Expanding the window around 2-4 GHz");
  bandTable(s, [
    ["2 – 4", "2 GHz", 99.4, 97.4, 92.9, false],
    ["1.5 – 4.5", "3 GHz", 99.4, 98.1, 97.0, false],
    ["1 – 5", "4 GHz", 99.4, 98.1, 100.0, true],
    ["0.5 – 5.5", "5 GHz", 99.4, 97.4, 100.0, false],
    ["0.1 – 8 (full)", "7.9 GHz", 99.3, 97.4, 100.0, false],
  ], 1.55, "All 16 S-parameters. Windows centred on the winning 2-4 GHz region.");
  notebox(s, "1-5 GHz (4 GHz bandwidth, 3 GHz centre) matches full-band accuracy on all three phantoms, including 100% on F5. 0.5-5.5 GHz scores the same; 1.5-4.5 and 2-4 GHz score 3-7 points lower on F5.", 4.5, 0.85, 13);
}

// ================================================================ 5. FIGURE
{
  const s = p.addSlide();
  title(s, "The full picture", "Placement and width, at both hardware extremes");
  s.addImage({ path: A + "band_combined.png", x: 0.45, y: 1.5, w: 9.1, h: 3.47 });
  s.addText("Solid = all 16 S-parameters · dashed = single antenna (S11 only). Left: where the 2 GHz window sits. Right: accuracy vs bandwidth around 2-4 GHz.",
    { x: 0.5, y: 4.95, w: 9, h: 0.4, fontSize: 11, italic: true, color: GREY,
      align: "center", fontFace: "Calibri", margin: 0 });
}

// ================================================================ 6. STAGE C: CHIP POINTS
{
  const s = p.addSlide();
  title(s, "Step 3 · combined reductions", "The 1-5 GHz band with reduced hardware");
  const hdr = ["Hardware @ 1-5 GHz", "Empty", "A3 + F4", "A3 + F5", "F5 @ full band"].map(t =>
    ({ text: t, options: { fill: { color: RED }, color: WHITE, bold: true, fontSize: 13,
       align: "center", valign: "middle" } }));
  const rows = [
    ["4 antennas, reflection only", 100.0, 97.4, 94.9, "100.0", true],
    ["2 antennas (1 & 3), full S", 99.3, 92.9, 92.9, "96.0", false],
    ["2 antennas, reflection only", 99.3, 92.9, 84.8, "90.9", false],
    ["1 antenna (S11)", 96.1, 96.2, 69.7, "75.8", false],
  ];
  const body = rows.map((r, i) => {
    const fill = { color: r[5] ? TINT : (i % 2 ? "FAFAFA" : WHITE) };
    const c = (v, b) => ({ text: typeof v === "number" ? v.toFixed(1) : String(v),
      options: { fill, color: DARK, fontSize: 13, align: "center", bold: !!b } });
    return [{ text: r[0], options: { fill, color: r[5] ? RED : DARK, bold: true, fontSize: 12.5, align: "left" } },
            c(r[1], r[5]), c(r[2], r[5]), c(r[3], r[5]),
            { text: r[4], options: { fill, color: GREY, fontSize: 12.5, align: "center", italic: true } }];
  });
  s.addTable([hdr, ...body], { x: 0.5, y: 1.55, w: 9.0, colW: [3.1, 1.35, 1.45, 1.45, 1.65],
    border: { pt: 0.75, color: "D9D9D9" }, rowH: 0.42, valign: "middle", fontFace: "Calibri" });
  notebox(s, "With the full array, restricting to 1-5 GHz left accuracy unchanged; with reduced antennas the same restriction scores 3-6 points lower on F5 than full band. 4 antennas reflection-only at 1-5 GHz: 94.9 on F5.", 4.35, 0.95, 13);
}

// ================================================================ 7. ROBUSTNESS (1 ANTENNA)
{
  const s = p.addSlide();
  title(s, "Step 4 · robustness check", "The same window sweep with one antenna");
  bandTable(s, [
    ["0.1 – 2", "2 GHz", 87.6, 43.6, 25.3, false],
    ["2 – 4", "2 GHz", 97.4, 92.9, 62.6, true],
    ["4 – 6", "2 GHz", 95.4, 79.5, 52.5, false],
    ["6 – 8", "2 GHz", 98.7, 83.3, 53.5, false],
    ["0.5 – 5.5", "5 GHz", 98.0, 95.5, 74.8, false],
    ["0.1 – 8 (full)", "7.9 GHz", 98.0, 96.8, 75.8, false],
  ], 1.42, "S11 only. Note 0.1-2 GHz: fine with the full array (90.9 on F5), catastrophic alone (25.3).", 0.38);
  notebox(s, "With one antenna, 2-4 GHz is again the highest 2 GHz window. F5 accuracy rises with width through ~5 GHz (62.6 at 2 GHz -> 74.8 at 5 GHz). The 0.1-2 GHz window scores 25.3 on F5 with one antenna vs 90.9 with the full array.", 4.62, 0.72, 12.5);
}

// ================================================================ 8. RECOMMENDATION
{
  const s = p.addSlide();
  title(s, "Recommendation", "Chip band specification");
  const cc = (x, y, big, small, hl) => {
    s.addShape(p.shapes.ROUNDED_RECTANGLE, { x, y, w: 4.35, h: 1.45,
      fill: { color: hl ? TINT : WHITE }, line: { color: hl ? RED : "E0E0E0", width: hl ? 1.5 : 1 },
      rectRadius: 0.08,
      shadow: { type: "outer", color: "000000", blur: 6, offset: 2, angle: 45, opacity: 0.12 } });
    s.addText(big, { x: x + 0.25, y: y + 0.13, w: 3.9, h: 0.45, fontSize: 16, bold: true,
      color: RED, fontFace: "Cambria", margin: 0 });
    s.addText(small, { x: x + 0.25, y: y + 0.58, w: 3.9, h: 0.82, fontSize: 11.5,
      color: DARK, fontFace: "Calibri", margin: 0 });
  };
  cc(0.5, 1.5, "Spec: 1-5 GHz", "4 GHz bandwidth, 3 GHz centre. Matched full-band accuracy on all three phantoms with the full array.", true);
  cc(5.15, 1.5, "Fallback: 1.5-4.5 GHz", "Scored 1-3 points below full band on F5; 2-4 GHz scored 7 below.");
  cc(0.5, 3.28, "Low-scoring regions", "F5: 71.7 / 69.7 at 4-6 / 6-8 GHz (full array); 25.3 at 0.1-2 GHz with one antenna.");
  cc(5.15, 3.28, "Combined reductions at 1-5 GHz", "F5: 94.9 (4-ant refl) / 92.9 (2-ant) / 84.8 (2-ant refl) / 69.7 (1 antenna).");
  s.addText("All results: CNN classification, raw S-parameters, leave-one-session-out, measured A3 phantom data. Details in results/ and docs/CHANGELOG.md.",
    { x: 0.5, y: 5.05, w: 9, h: 0.35, fontSize: 10.5, italic: true, color: GREY,
      fontFace: "Calibri", margin: 0 });
}


// ================================================================ 9. PART 2 INTRO
{
  const s = p.addSlide();
  title(s, "Part 2 · trying to break it", "New constraint, new question: where does it fail?");
  s.addText("Follow-up task: stay entirely below 4 GHz (easier chip) and push the bandwidth down until the model breaks. That needs a definition of 'broken':",
    { x: 0.5, y: 1.35, w: 9.0, h: 0.6, fontSize: 14, color: DARK, fontFace: "Calibri", margin: 0 });
  const tier = (y, name, def, col) => {
    s.addText(name, { x: 0.7, y, w: 2.2, h: 0.42, fontSize: 14.5, bold: true, color: col,
      fontFace: "Cambria", margin: 0, valign: "middle" });
    s.addText(def, { x: 3.0, y, w: 6.5, h: 0.42, fontSize: 12.5, color: DARK,
      fontFace: "Calibri", margin: 0, valign: "middle" });
  };
  tier(2.15, "DEGRADED", "mean below 90% of that phantom's full-band accuracy", GREY);
  tier(2.62, "UNSTABLE", "fold-to-fold sigma of 10 points or more: works one session, fails the next", "C8890B");
  tier(3.09, "BROKEN", "mean below 50%: wrong more often than right (the headline break)", RED);
  tier(3.56, "DEEP", "mean below 25%: approaching uselessness (still ~10x chance)", "8E1010");
  notebox(s, "Method: descend bandwidth 3 -> 2 -> 1 -> 0.5 -> 0.25 -> 0.1 -> 0.05 GHz with the best placement at every width, plus a nine-window placement scan at 0.25 GHz. All below 4 GHz.", 4.35, 0.85, 13);
}

// ================================================================ 10. PLACEMENT SCAN
{
  const s = p.addSlide();
  title(s, "Part 2 · placement", "Nine 0.25 GHz windows across the span");
  const hdr = ["Window (GHz)", "Empty", "A3 + F4", "A3 + F5"].map(t =>
    ({ text: t, options: { fill: { color: RED }, color: WHITE, bold: true, fontSize: 12.5,
       align: "center", valign: "middle" } }));
  const rows = [
    ["0.5 - 0.75", "43.8 ± 7.9", "45.5 ± 7.4", "65.7 ± 6.3", false, true],
    ["1 - 1.25", "48.4 ± 9.3", "65.4 ± 6.1", "74.7 ± 9.7", false, true],
    ["1.25 - 1.5", "94.8 ± 4.5", "66.7 ± 12.0", "78.8 ± 3.0", false, false],
    ["1.5 - 1.75", "99.3 ± 1.1", "88.5 ± 9.0", "74.7 ± 20.2", false, false],
    ["1.75 - 2", "99.3 ± 1.1", "96.8 ± 1.3", "80.8 ± 12.6", false, false],
    ["2 - 2.25", "100.0 ± 0.0", "95.5 ± 5.7", "83.8 ± 3.5", true, false],
    ["2.5 - 2.75", "99.3 ± 1.1", "96.8 ± 1.3", "76.8 ± 4.6", false, false],
    ["3 - 3.25", "99.3 ± 1.1", "96.8 ± 3.8", "74.7 ± 1.7", false, false],
    ["3.5 - 3.75", "99.3 ± 1.1", "98.1 ± 2.5", "76.8 ± 3.5", false, false],
  ];
  const body = rows.map((r, i) => {
    const fill = { color: r[4] ? TINT : (i % 2 ? "FAFAFA" : WHITE) };
    const c = (v) => ({ text: v, options: { fill, color: r[5] ? RED : DARK, fontSize: 11.5,
      align: "center", bold: r[4] } });
    return [{ text: r[0], options: { fill, color: r[4] ? RED : (r[5] ? RED : DARK), bold: true,
      fontSize: 11.5, align: "left" } }, c(r[1]), c(r[2]), c(r[3])];
  });
  s.addTable([hdr, ...body], { x: 0.5, y: 1.42, w: 9.0, colW: [2.5, 2.1, 2.2, 2.2],
    border: { pt: 0.75, color: "D9D9D9" }, rowH: 0.315, valign: "middle", fontFace: "Calibri" });
  notebox(s, "Highest window: 2-2.25 GHz (highlighted), with lower fold sigma than 1.75-2. In the red rows (below ~1.25 GHz) empty and F4 score below 50%.", 4.85, 0.62, 12);
}

// ================================================================ 10b. WHERE INFO LIVES
{
  const s = p.addSlide();
  title(s, "Part 2 · placement scan", "Each phantom has a different best frequency");
  s.addImage({ path: A + "band_importance.png", x: 0.3, y: 1.5, w: 9.4, h: 2.88 });
  notebox(s, "The model is trained on only one window at a time, slid across the spectrum. Best narrow slot per phantom: empty ~2.0 GHz (99+ everywhere above 1.45), F4 ~3.0 GHz, F5 ~2.2-2.3 GHz. At 100 MHz width F5 scores 78.8 at 2.2-2.3 vs 62.6 at 1.825-1.925, the slot used in the Part 2 descent.", 4.5, 1.0, 11);
}

// ================================================================ 11. BREAK CURVE
{
  const s = p.addSlide();
  title(s, "Part 2 · the descent", "Best placement at every width, down to 0.05 GHz");
  s.addImage({ path: A + "break_curve.png", x: 1.05, y: 1.42, w: 7.9, h: 4.28 });
}

// ================================================================ 12. BREAK VERDICT
{
  const s = p.addSlide();
  title(s, "Part 2 · verdict", "Where each phantom breaks");
  const hdr = ["Failure tier", "Empty", "A3 + F4", "A3 + F5"].map(t =>
    ({ text: t, options: { fill: { color: RED }, color: WHITE, bold: true, fontSize: 13,
       align: "center", valign: "middle" } }));
  const rows = [
    ["Degraded (<90% of full band)", "never", "never", "0.5 GHz"],
    ["Unstable (fold sigma >= 10)", "never", "never", "1 GHz"],
    ["Broken (<50%)", "never", "never", "never"],
    ["Floor at 0.05 GHz (50 MHz)", "99.3 ± 1.1", "90.4 ± 7.1", "59.6 ± 17.8"],
  ];
  const body = rows.map((r, i) => {
    const fill = { color: i % 2 ? TINT : WHITE };
    return [{ text: r[0], options: { fill, color: DARK, bold: true, fontSize: 12.5, align: "left" } },
      { text: r[1], options: { fill, color: DARK, fontSize: 12.5, align: "center" } },
      { text: r[2], options: { fill, color: DARK, fontSize: 12.5, align: "center" } },
      { text: r[3], options: { fill, color: RED, bold: true, fontSize: 12.5, align: "center" } }];
  });
  s.addTable([hdr, ...body], { x: 0.5, y: 1.5, w: 9.0, colW: [3.6, 1.7, 1.8, 1.9],
    border: { pt: 0.75, color: "D9D9D9" }, rowH: 0.44, valign: "middle", fontFace: "Calibri" });
  notebox(s, "With all 16 S-parameters, no phantom scores below 50% at any width: at 50 MHz the floors are 99.3 / 90.4 / 59.6. F5 crosses the degraded tier at 0.5 GHz and the unstable tier at 1 GHz. Part 3 repeats the descent with reduced hardware.", 4.1, 1.1, 12.5);
}


// ================================================================ 13. PART 3 MAP
{
  const s = p.addSlide();
  title(s, "Part 3 · hardware + band together", "The full break map: 5 hardware levels x 7 bands");
  s.addImage({ path: A + "break_descent_map.png", x: 0.25, y: 1.55, w: 9.5, h: 2.82 });
  notebox(s, "Bands narrow left to right at the best placement per width; once a phantom scores below 50% (black box) it stops descending at that hardware level. Blank cells were skipped after the break. Empty does not cross 50% in any cell.", 4.62, 0.85, 12);
}

// ================================================================ 13b. PART 3 MAP V2
{
  const s = p.addSlide();
  title(s, "Part 3 · break map v2", "Same descent with per-phantom band centers");
  s.addImage({ path: A + "break_descent_map_best.png", x: 0.25, y: 1.55, w: 9.5, h: 2.82 });
  notebox(s, "Bands re-centered per phantom: F4 -> 3.0 GHz, F5 -> 2.25 GHz. Empty keeps its original ~1.875 GHz bands: its full-array scan scored 99-100 in every window, and at single antenna the original slot scored higher (76/75 vs 71/59 at 0.1/0.05 GHz). With re-centered bands, F4's single-antenna row no longer crosses 50% (70.5 at 50 MHz vs 39.7 at 0.5 GHz before) and F5's sub-50% cells shift one column narrower.", 4.55, 1.05, 10.5);
}

// ================================================================ 14. PART 3 VERDICT
{
  const s = p.addSlide();
  title(s, "Part 3 · summary", "First band below 50%, original descent");
  const hdr = ["Hardware", "Empty", "A3 + F4", "A3 + F5"].map(t =>
    ({ text: t, options: { fill: { color: RED }, color: WHITE, bold: true, fontSize: 12.5,
       align: "center", valign: "middle" } }));
  const rows = [
    ["16 S-params (full array)", "never", "never", "never (floor 60)"],
    ["4 antennas, reflection only", "never", "never", "0.1 GHz (47%)"],
    ["2 antennas (1 & 3), full S", "never", "never", "0.5 GHz (35%)"],
    ["2 antennas (1 & 3), reflection only", "never", "never", "1 GHz (45%)"],
    ["1 antenna (S11 only)", "never (floor 75)", "0.5 GHz (40%)", "1 GHz (21%)"],
  ];
  const body = rows.map((r, i) => {
    const fill = { color: i % 2 ? TINT : WHITE };
    const c = (v, red) => ({ text: v, options: { fill, color: red ? RED : DARK,
      bold: red, fontSize: 12, align: "center" } });
    return [{ text: r[0], options: { fill, color: DARK, bold: true, fontSize: 12, align: "left" } },
      c(r[1], false), c(r[2], r[2] !== "never"), c(r[3], !r[3].startsWith("never"))];
  });
  s.addTable([hdr, ...body], { x: 0.5, y: 1.45, w: 9.0, colW: [3.7, 1.7, 1.7, 1.9],
    border: { pt: 0.75, color: "D9D9D9" }, rowH: 0.42, valign: "middle", fontFace: "Calibri" });
  const pts = [
    "Empty never scores below 50% in any cell. F4 crosses 50% only at 1 antenna + 0.5 GHz (and not at all with re-centered bands). F5 crosses 50% at every reduced-hardware level.",
    "F5's first sub-50% band widens as hardware is reduced: 0.1 GHz (4 ant refl) -> 0.5 GHz (2 ant) -> 1 GHz (2 ant refl, 1 ant).",
  ].map(t => ({ text: t, options: { bullet: { code: "2022", indent: 12 }, color: DARK,
    fontSize: 12.5, fontFace: "Calibri", paraSpaceAfter: 8, breakLine: true } }));
  s.addText(pts, { x: 0.55, y: 4.15, w: 8.9, h: 1.65, valign: "top", margin: 0 });
}

p.writeFile({ fileName: "Frequency_Reduction.pptx" }).then(() => console.log("band deck written"));
