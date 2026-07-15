// DECK 3 — Sim vs measured on the EMPTY phantom: grids, raw S-params, the
// corrected numerical comparison, and a sim->measured transfer probe.
//   ->  Deck3_Sim_vs_Measured.pptx
const pptxgen = require("pptxgenjs");
const NAVY="0E2233",BLUE="0B5D7A",TEAL="1C9AA8",MINT="2CC4A3",CORAL="D64545",
      AMBER="E0A100",INK="1E293B",MUTE="5B6B7B",LIGHT="FFFFFF",CARD="F3F7FA",LINE="D8E2EA";
const HEAD="Cambria",BODY="Calibri";
const shadow=()=>({type:"outer",color:"5B6B7B",blur:7,offset:3,angle:90,opacity:0.18});
const pres=new pptxgen();
pres.defineLayout({name:"W",width:13.33,height:7.5}); pres.layout="W";
pres.author="Peter Martin"; pres.title="Sim vs Measured";
const W=13.33,H=7.5;
function title(s,t,sub){
  s.addText(t,{x:0.6,y:0.42,w:W-1.2,h:0.7,fontFace:HEAD,fontSize:29,bold:true,color:INK,margin:0});
  if(sub)s.addText(sub,{x:0.6,y:1.13,w:W-1.2,h:0.4,fontFace:BODY,fontSize:14,color:TEAL,bold:true,margin:0});}
function card(s,x,y,w,h,fill){s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x,y,w,h,rectRadius:0.09,
  fill:{color:fill||CARD},line:{color:LINE,width:1},shadow:shadow()});}
function bullets(s,x,y,w,h,arr,fs){s.addText(arr.map(b=>({text:b,options:{bullet:true,breakLine:true,paraSpaceAfter:8}})),
  {x,y,w,h,fontFace:BODY,fontSize:fs||13,color:INK,valign:"top",margin:0});}

// ============ 1. TITLE
let s=pres.addSlide(); s.background={color:NAVY};
s.addText("PART 3 · SIM  ↔  MEASURED",{x:0.9,y:2.05,w:11.5,h:0.5,fontFace:BODY,fontSize:15,color:MINT,bold:true,charSpacing:3,margin:0});
s.addText("Comparing simulation and bench — empty phantom",{x:0.9,y:2.6,w:11.6,h:1.1,fontFace:HEAD,fontSize:36,bold:true,color:LIGHT,margin:0});
s.addText("Do the two agree? The signal interpolates equally well on both — the apparent gap is data coverage, not simulation fidelity",
  {x:0.9,y:3.8,w:11.4,h:0.7,fontFace:BODY,fontSize:15.5,color:"AECBD6",margin:0});
[["6.7 ≈ 6.0 mm","k-NN signal floor: sim ≈ measured"],["distinct positions","the real driver of the CNN gap"],["R² = 0.65","a learnable sim→measured transfer"]].forEach((c,i)=>{
  const x=0.9+i*3.95;
  s.addText(c[0],{x,y:4.95,w:3.9,h:0.7,fontFace:HEAD,fontSize:25,bold:true,color:MINT,margin:0});
  s.addText(c[1],{x,y:5.62,w:3.9,h:0.6,fontFace:BODY,fontSize:12.5,color:"AECBD6",margin:0});});

// ============ 2. TWO GRIDS
s=pres.addSlide(); s.background={color:LIGHT};
title(s,"Two different sampling grids","Same phantom, very different coverage — this matters for every comparison that follows");
s.addImage({path:"grid_sim_vs_physical.png",x:0.7,y:1.75,w:12.0,h:5.2});

// ============ 3. SETUP DIFFERENCES
s=pres.addSlide(); s.background={color:LIGHT};
title(s,"What differs between the two","Antennas, grid, depth coverage and frequency span all differ");
const rows=[
  ["","Simulated (HFSS)","Measured (bench VNA)"],
  ["Antennas","'Sam' model, full-wave solve","'Sam Medium', physical build"],
  ["Grid","uniform 10 mm lattice, 91 positions","6×6 cells, 4 corners each; 51 measured"],
  ["Depth","13 planes, z = −15 … +45 mm","single tumor height only"],
  ["Frequency","2–8 GHz, 3001 points","0.1–8 GHz, 791 points"],
  ["Noise / drift","none (deterministic solve)","measurement noise + cross-session drift"],
  ["Repeats","one solve per position","16 takes × 3 sessions per position"],
];
s.addTable(rows.map((r,ri)=>r.map((c,ci)=>({text:c,options:{
  fontFace:ci===0?HEAD:BODY,bold:ri===0||ci===0,fontSize:ri===0?15:13.5,
  color:ri===0?LIGHT:(ci===0?BLUE:INK),align:ci===0?"left":"center",valign:"middle",
  fill:{color:ri===0?BLUE:(ri%2?CARD:LIGHT)},margin:[4,6,4,6]}}))),
  {x:0.7,y:1.85,w:11.9,colW:[2.7,4.6,4.6],rowH:0.6,border:{type:"solid",color:LINE,pt:1}});
s.addText("Different geometry, coverage, band and noise — a fair sim↔measured comparison must control for all of these.",
  {x:0.7,y:6.7,w:11.9,h:0.5,fontFace:BODY,fontSize:13,italic:true,color:MUTE,align:"center",margin:0});

// ============ 4. RAW S-PARAMS
s=pres.addSlide(); s.background={color:LIGHT};
title(s,"Raw S-parameters — the antenna domain gap","How far apart are the simulated and measured antennas, before any tumor?");
s.addImage({path:"raw_sparam_sim_vs_meas.png",x:0.7,y:1.8,w:12.0,h:4.6});
s.addText("The two antenna models resonate and couple differently — a real domain gap that any sim→measured transfer must bridge.",
  {x:0.7,y:6.55,w:11.9,h:0.5,fontFace:BODY,fontSize:13.5,italic:true,color:MUTE,align:"center",margin:0});

// ============ 5. NUMERICAL COMPARISON (the corrected story)
s=pres.addSlide(); s.background={color:LIGHT};
title(s,"The numbers — signal vs. model","Two probes of the empty phantom: does the SIGNAL interpolate, and can the CNN learn it?");
const t2=[
  ["Probe (leave-one-position-out)","Trains on","Sim empty","Measured empty"],
  ["k-NN  (training-free — pure signal)","nothing","6.7 mm","6.0 mm"],
  ["CNN  (~150 samples ≈ 50 positions)","measured","—","9.9 mm"],
  ["CNN  (full depth stack, ~1000 pos)","sim","3.9 mm","—"],
];
s.addTable(t2.map((r,ri)=>r.map((c,ci)=>({text:c,options:{
  fontFace:BODY,bold:ri===0||ci===0,fontSize:ri===0?13.5:14,
  color:ri===0?LIGHT:((ci>=2&&ri>0)?BLUE:INK),align:ci===0?"left":"center",valign:"middle",
  fill:{color:ri===0?BLUE:(ri%2?CARD:LIGHT)},margin:[5,6,5,6]}}))),
  {x:0.6,y:1.8,w:7.6,colW:[3.5,1.4,1.35,1.35],rowH:0.72,border:{type:"solid",color:LINE,pt:1}});
card(s,8.4,1.8,4.3,4.9);
s.addText("What the numbers mean",{x:8.65,y:1.98,w:3.8,h:0.4,fontFace:HEAD,fontSize:15.5,bold:true,color:BLUE,margin:0});
bullets(s,8.65,2.5,3.8,4.1,[
  "Signal interpolates EQUALLY well: sim 6.7 ≈ measured 6.0 mm (k-NN). Sim is not unrealistically smooth.",
  "The measured CNN (9.9 mm) trains on 16 takes × 3 sessions but only ~50 DISTINCT positions — data-starved, so it loses to k-NN.",
  "The sim CNN reaches 3.9 mm only via ~1000 distinct positions (13 depths).",
  "So the sim↔measured CNN gap is distinct-position COVERAGE, not fidelity.",
],12);
s.addText("To match the sim's 3.9 mm on the bench we need more distinct measured locations (denser grid / more depths) — not a better model.",
  {x:0.6,y:6.85,w:7.6,h:0.5,fontFace:BODY,fontSize:11.5,italic:true,color:MUTE,align:"left",margin:0});

// ============ 6. SIM->MEASURED TRANSFER (exploratory)
s=pres.addSlide(); s.background={color:LIGHT};
title(s,"Can a model bridge the gap? (exploratory)","Learn a sim→measured map on the empty baseline, test on unseen frequencies");
s.addImage({path:"sim_meas_correlation.png",x:0.55,y:1.75,w:8.5,h:3.9});
card(s,9.2,1.75,3.55,3.9);
s.addText("First-pass finding",{x:9.4,y:1.92,w:3.2,h:0.4,fontFace:HEAD,fontSize:15,bold:true,color:BLUE,margin:0});
bullets(s,9.4,2.45,3.2,3.1,[
  "Raw sim-vs-measured |S| correlation: 0.61.",
  "A LINEAR transfer predicts measured from sim to R² = 0.65 on frequencies it never saw — a real, learnable relationship.",
  "A flexible MLP overfits the single paired baseline (R² < 0).",
],11.5);
s.addText("Preliminary — only the empty baseline is cleanly paired. Nonlinear domain adaptation (and any use for calibrating sim toward the bench) needs far more paired data: multiple sessions and, ideally, matched tumor positions.",
  {x:0.6,y:6.7,w:W-1.2,h:0.6,fontFace:BODY,fontSize:12.5,italic:true,color:MUTE,align:"center",margin:0});

// ============ 7. CONCLUSIONS
s=pres.addSlide(); s.background={color:NAVY};
s.addText("Part 3 — bottom line",{x:0.9,y:0.75,w:11,h:0.8,fontFace:HEAD,fontSize:28,bold:true,color:LIGHT,margin:0});
[["Sim and measured agree at the signal level","the empty phantom interpolates to ~6 mm on BOTH benches (k-NN) — the simulation is realistic, not artificially smooth."],
 ["The CNN gap is data coverage, not fidelity","sim's 3.9 mm comes from ~1000 distinct positions; measured's 9.9 mm from only ~50. Same model, different coverage."],
 ["Takes and sessions ≠ new positions","16 takes × 3 sessions add robustness (great for LOSO) but no new tumor locations (no help for interpolation)."],
 ["A real antenna domain gap exists","simulated and measured antennas resonate/couple differently — visible in the raw S-parameters."],
 ["A sim→measured transfer is learnable","a linear map already reaches R² = 0.65 on unseen frequencies — a promising, if preliminary, calibration path."],
].forEach((c,i)=>{const y=1.7+i*1.06;
  s.addShape(pres.shapes.OVAL,{x:0.9,y:y+0.05,w:0.42,h:0.42,fill:{color:MINT}});
  s.addText(String(i+1),{x:0.9,y:y+0.05,w:0.42,h:0.42,align:"center",valign:"middle",fontFace:HEAD,fontSize:15,bold:true,color:NAVY,margin:0});
  s.addText([{text:c[0]+"  —  ",options:{bold:true,color:LIGHT}},{text:c[1],options:{color:"AECBD6"}}],
    {x:1.5,y:y-0.05,w:11.2,h:0.95,fontFace:BODY,fontSize:14,valign:"middle",margin:0});});
s.addText("github.com/pmart1534/microwave-phantom-localization-cnn-mlp",{x:0.9,y:7.0,w:11.5,h:0.35,fontFace:BODY,fontSize:11,color:TEAL,margin:0});

pres.writeFile({fileName:"Deck3_Sim_vs_Measured.pptx"}).then(f=>console.log("wrote "+f));
