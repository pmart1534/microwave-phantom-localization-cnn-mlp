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
  const stats = [["1–5 GHz", "recommended band"], ["1/2", "the bandwidth of the full sweep"], ["100%", "F5 accuracy retained (full array)"]];
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
  title(s, "Step 1 · band placement", "A 2 GHz window: the low-mid band wins");
  bandTable(s, [
    ["0.1 – 2", "2 GHz", 99.4, 96.2, 90.9, false],
    ["2 – 4", "2 GHz", 99.4, 97.4, 92.9, true],
    ["4 – 6", "2 GHz", 99.4, 89.1, 71.7, false],
    ["6 – 8", "2 GHz", 99.4, 97.4, 69.7, false],
    ["0.1 – 8 (full)", "7.9 GHz", 99.3, 97.4, 100.0, false],
  ], 1.55, "All 16 S-parameters. LOSO per-position vote accuracy (%). Highlighted row = best 2 GHz window (mean across phantoms).");
  notebox(s, "The 2-4 GHz window wins. Above 4 GHz, F5 collapses to ~70%: the large lossy glandular insert attenuates high-frequency energy before it reaches interior positions. The empty phantom is band-agnostic.", 4.5, 0.85, 13);
}

// ================================================================ 4. HOW WIDE
{
  const s = p.addSlide();
  title(s, "Step 2 · bandwidth", "Expanding around 2-4 GHz: the knee is at 4 GHz");
  bandTable(s, [
    ["2 – 4", "2 GHz", 99.4, 97.4, 92.9, false],
    ["1.5 – 4.5", "3 GHz", 99.4, 98.1, 97.0, false],
    ["1 – 5", "4 GHz", 99.4, 98.1, 100.0, true],
    ["0.5 – 5.5", "5 GHz", 99.4, 97.4, 100.0, false],
    ["0.1 – 8 (full)", "7.9 GHz", 99.3, 97.4, 100.0, false],
  ], 1.55, "All 16 S-parameters. Windows centred on the winning 2-4 GHz region.");
  notebox(s, "1-5 GHz (4 GHz bandwidth, 3 GHz centre) recovers full-band accuracy on every phantom, including 100% on F5. Going wider adds nothing; going narrower costs F5 3-7 points. Half the bandwidth, zero accuracy cost.", 4.5, 0.85, 13);
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
  notebox(s, "The reductions compound on F5: a band cut that is free with the full array costs 3-6 points once antennas or transmission paths are also removed. Best reduced operating point: 4 antennas, reflection-only, 1-5 GHz = 95% on the hardest phantom.", 4.35, 0.95, 13);
}

// ================================================================ 7. ROBUSTNESS (1 ANTENNA)
{
  const s = p.addSlide();
  title(s, "Step 4 · robustness check", "The same sweep with one antenna confirms the band");
  bandTable(s, [
    ["0.1 – 2", "2 GHz", 87.6, 43.6, 25.3, false],
    ["2 – 4", "2 GHz", 97.4, 92.9, 62.6, true],
    ["4 – 6", "2 GHz", 95.4, 79.5, 52.5, false],
    ["6 – 8", "2 GHz", 98.7, 83.3, 53.5, false],
    ["0.5 – 5.5", "5 GHz", 98.0, 95.5, 74.8, false],
    ["0.1 – 8 (full)", "7.9 GHz", 98.0, 96.8, 75.8, false],
  ], 1.42, "S11 only. Note 0.1-2 GHz: fine with the full array (90.9 on F5), catastrophic alone (25.3).", 0.38);
  notebox(s, "2-4 GHz wins again, so the band choice is robust; but with one antenna there is no knee - accuracy climbs to ~5 GHz. Antennas and bandwidth are partially interchangeable information budgets.", 4.62, 0.72, 12.5);
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
  cc(0.5, 1.5, "Spec: 1-5 GHz", "4 GHz bandwidth, 3 GHz centre. Full-band accuracy on every phantom with the array; the anchor for any hardware configuration.", true);
  cc(5.15, 1.5, "Fallback: 1.5-4.5 GHz", "3 GHz bandwidth costs only 1-3 points on the hardest phantom; 2-4 GHz is the floor (-7 on F5).");
  cc(0.5, 3.28, "Avoid: above 5 GHz and below 1 GHz alone", "High bands carry no F5 information (insert attenuation). Pure low band collapses without array diversity.");
  cc(5.15, 3.28, "Design principle", "Antennas and bandwidth trade against each other. Cut one aggressively, not both: 4-ant reflection-only @ 1-5 GHz keeps 95% on F5.");
  s.addText("All results: CNN classification, raw S-parameters, leave-one-session-out, measured A3 phantom data. Details in results/ and docs/CHANGELOG.md.",
    { x: 0.5, y: 5.05, w: 9, h: 0.35, fontSize: 10.5, italic: true, color: GREY,
      fontFace: "Calibri", margin: 0 });
}

p.writeFile({ fileName: "Frequency_Reduction.pptx" }).then(() => console.log("band deck written"));
