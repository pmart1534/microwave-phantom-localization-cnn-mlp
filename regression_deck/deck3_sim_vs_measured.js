// DECK 3 - Sim vs measured on the EMPTY phantom. UofU warm-red theme, light titles.
//   ->  Deck3_Sim_vs_Measured.pptx
const pptxgen = require("pptxgenjs");
const CRIMSON="BE0000", CRIMSONDK="8E1010", GOLD="C8890B", ROSE="E0A99E",
      REDMID="C0564A", INK="2A1618", MUTE="836A68", LIGHT="FFFFFF",
      CARD="FBF4F2", LINE="E7D6D1", CREAM="EAD3CB", GRAYW="C9B3AE", CREAMBG="FDF8F6";
const HEAD="Cambria", BODY="Calibri";
const shadow=()=>({type:"outer",color:"7A5C5E",blur:7,offset:3,angle:90,opacity:0.18});
const pres=new pptxgen();
pres.defineLayout({name:"W",width:13.33,height:7.5}); pres.layout="W";
pres.author="Peter Martin"; pres.title="Sim vs Measured";
const W=13.33,H=7.5;
function title(s,t,sub){
  s.addText(t,{x:0.6,y:0.42,w:W-1.2,h:0.7,fontFace:HEAD,fontSize:29,bold:true,color:INK,margin:0});
  if(sub)s.addText(sub,{x:0.6,y:1.13,w:W-1.2,h:0.4,fontFace:BODY,fontSize:14,color:CRIMSON,bold:true,margin:0});}
function card(s,x,y,w,h,fill){s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x,y,w,h,rectRadius:0.09,
  fill:{color:fill||CARD},line:{color:LINE,width:1},shadow:shadow()});}
function bullets(s,x,y,w,h,arr,fs){s.addText(arr.map(b=>({text:b,options:{bullet:true,breakLine:true,paraSpaceAfter:8}})),
  {x,y,w,h,fontFace:BODY,fontSize:fs||13,color:INK,valign:"top",margin:0});}
function imgCaption(s,x,y,w,h,path,cap){card(s,x-0.1,y-0.1,w+0.2,h+0.55);
  s.addImage({path,x,y,w,h});
  s.addText(cap,{x:x-0.1,y:y+h+0.02,w:w+0.2,h:0.4,align:"center",fontFace:BODY,fontSize:13,bold:true,color:INK,margin:0});}
function titleLight(s,part,ttl,sub,stats){s.background={color:CREAMBG};
  s.addShape(pres.shapes.RECTANGLE,{x:0,y:0,w:W,h:0.26,fill:{color:CRIMSON},line:{type:"none"}});
  s.addShape(pres.shapes.RECTANGLE,{x:0.9,y:2.02,w:0.09,h:1.5,fill:{color:CRIMSON},line:{type:"none"}});
  s.addText(part,{x:1.2,y:2.02,w:11,h:0.45,fontFace:BODY,fontSize:15,color:CRIMSON,bold:true,charSpacing:3,margin:0});
  s.addText(ttl,{x:1.2,y:2.5,w:11.2,h:1.0,fontFace:HEAD,fontSize:34,bold:true,color:INK,margin:0});
  s.addText(sub,{x:1.2,y:3.62,w:11.0,h:0.7,fontFace:BODY,fontSize:15.5,color:MUTE,margin:0});
  stats.forEach((c,i)=>{const x=1.2+i*3.95;
    s.addText(c[0],{x,y:4.95,w:3.85,h:0.7,fontFace:HEAD,fontSize:25,bold:true,color:CRIMSON,margin:0});
    s.addText(c[1],{x,y:5.62,w:3.9,h:0.6,fontFace:BODY,fontSize:12.5,color:MUTE,margin:0});});}
function closingLight(s,heading,items){s.background={color:CREAMBG};
  s.addShape(pres.shapes.RECTANGLE,{x:0,y:0,w:W,h:0.26,fill:{color:CRIMSON},line:{type:"none"}});
  s.addText(heading,{x:0.9,y:0.7,w:11,h:0.8,fontFace:HEAD,fontSize:28,bold:true,color:CRIMSON,margin:0});
  items.forEach((c,i)=>{const y=1.7+i*1.06;
    s.addShape(pres.shapes.OVAL,{x:0.9,y:y+0.05,w:0.42,h:0.42,fill:{color:CRIMSON}});
    s.addText(String(i+1),{x:0.9,y:y+0.05,w:0.42,h:0.42,align:"center",valign:"middle",fontFace:HEAD,fontSize:15,bold:true,color:LIGHT,margin:0});
    s.addText([{text:c[0]+":  ",options:{bold:true,color:INK}},{text:c[1],options:{color:MUTE}}],
      {x:1.5,y:y-0.05,w:11.2,h:0.95,fontFace:BODY,fontSize:14,valign:"middle",margin:0});});
  s.addText("github.com/pmart1534/microwave-phantom-localization-cnn-mlp",{x:0.9,y:7.0,w:11.5,h:0.35,fontFace:BODY,fontSize:11,color:CRIMSON,margin:0});}

// ============ 1. TITLE (light)
let s=pres.addSlide();
titleLight(s,"PART 3 . SIM vs MEASURED","Comparing simulation and bench, empty phantom",
  "Do the two agree? The signal interpolates equally well on both; the apparent gap is data coverage, not simulation fidelity",
  [["6.7 vs 6.0 mm","k-NN signal floor: sim ~ measured"],["distinct positions","the real driver of the CNN gap"],["R2 = 0.65","a learnable sim->measured transfer"]]);

// ============ 1b. THE TWO SETUPS
s=pres.addSlide(); s.background={color:LIGHT};
title(s,"The two setups, side by side","The physical A3 phantom on its grid, and the HFSS model of the same phantom");
imgCaption(s,1.7,1.9,3.62,4.3,"setup_photos/A3.jpg","Measured: A3 phantom + 6x6 grid + antennas");
imgCaption(s,6.6,1.9,5.03,4.3,"setup_photos/SimulatedImage01.png","Simulated: HFSS phantom, oil, antennas, tumor");

// ============ 2. TWO GRIDS + OVERLAY
s=pres.addSlide(); s.background={color:LIGHT};
title(s,"Two sampling grids, and their overlay","Same phantom, different coverage; the right panel registers both into one physical frame");
s.addImage({path:"grid_sim_vs_physical.png",x:0.5,y:1.7,w:12.35,h:5.35});

// ============ 3. SETUP DIFFERENCES
s=pres.addSlide(); s.background={color:LIGHT};
title(s,"What differs between the two","Same antenna design, but grid, depth coverage, band and noise differ");
const rows=[
  ["","Simulated (HFSS)","Measured (bench VNA)"],
  ["Antennas","Sam's Medium Antennas (HFSS model)","Sam's Medium Antennas (physical build)"],
  ["Grid","uniform 10 mm lattice, 91 positions","6x6 cells, 4 corners each; 51 measured"],
  ["Depth","13 planes, z = -15 to +45 mm","single height, ~5 to 20 mm (near the patch)"],
  ["Frequency","2 to 8 GHz, 3001 points","0.1 to 8 GHz, 791 points"],
  ["Noise / drift","none (deterministic solve)","measurement noise + cross-session drift"],
  ["Repeats","one solve per position","16 takes x 3 sessions per position"],
];
s.addTable(rows.map((r,ri)=>r.map((c,ci)=>({text:c,options:{
  fontFace:ci===0?HEAD:BODY,bold:ri===0||ci===0,fontSize:ri===0?15:13.5,
  color:ri===0?LIGHT:(ci===0?CRIMSON:INK),align:ci===0?"left":"center",valign:"middle",
  fill:{color:ri===0?CRIMSON:(ri%2?CARD:LIGHT)},margin:[4,6,4,6]}}))),
  {x:0.7,y:1.85,w:11.9,colW:[2.7,4.6,4.6],rowH:0.6,border:{type:"solid",color:LINE,pt:1}});
s.addText("The 4 antennas are the SAME design in both; a fair sim vs measured comparison controls for the grid, depth, band and noise.",
  {x:0.7,y:6.7,w:11.9,h:0.5,fontFace:BODY,fontSize:13,italic:true,color:MUTE,align:"center",margin:0});

// ============ 4. RAW REFLECTIONS PER PORT
s=pres.addSlide(); s.background={color:LIGHT};
title(s,"Reflection per antenna, sim vs measured","Same design, yet the measured ports differ from each other; the sim ones are near-identical");
s.addImage({path:"raw_sparam_sim_vs_meas.png",x:2.35,y:1.7,w:8.6,h:5.28});

// ============ 5. DETECTABLE-DIFFERENCE PATTERN
s=pres.addSlide(); s.background={color:LIGHT};
title(s,"Detectable-difference pattern, measured vs sim","The tumor's detectable change per position; the spatial pattern matches");
s.addImage({path:"dd_measured_vs_sim.png",x:0.9,y:1.75,w:11.5,h:5.35});

// ============ 6. NUMERICAL COMPARISON
s=pres.addSlide(); s.background={color:LIGHT};
title(s,"The numbers, signal vs. model","Does the SIGNAL interpolate, and can the CNN learn it? (empty phantom)");
const t2=[
  ["Probe","Sim empty","Measured empty"],
  ["k-NN (training-free signal floor)","6.7 mm","6.0 mm"],
  ["CNN LOSO (new session, seen positions)","-","3.9 mm"],
  ["CNN LOPO single-position (unseen position)","-","9.9 mm"],
  ["CNN 8-fold (full depth stack, ~1000 pos)","3.9 mm","-"],
];
s.addTable(t2.map((r,ri)=>r.map((c,ci)=>({text:c,options:{
  fontFace:BODY,bold:ri===0||ci===0,fontSize:ri===0?13:13,
  color:ri===0?LIGHT:((ci>=1&&ri>0)?CRIMSON:INK),align:ci===0?"left":"center",valign:"middle",
  fill:{color:ri===0?CRIMSON:(ri%2?CARD:LIGHT)},margin:[5,6,5,6]}}))),
  {x:0.6,y:1.8,w:7.7,colW:[4.3,1.7,1.7],rowH:0.72,border:{type:"solid",color:LINE,pt:1}});
card(s,8.5,1.8,4.25,2.0,CARD);
s.addText("What is k-NN?",{x:8.7,y:1.95,w:3.8,h:0.35,fontFace:HEAD,fontSize:14,bold:true,color:CRIMSON,margin:0});
s.addText("A training-free baseline: to locate a held-out spot it just averages the (x,y) of the most similar measured signals. Nothing is fit, so it measures how well the SIGNAL alone pins down location, a floor any trained model should beat.",
  {x:8.7,y:2.35,w:3.85,h:1.4,fontFace:BODY,fontSize:11.5,color:INK,valign:"top",margin:0});
card(s,8.5,3.95,4.25,2.75,CARD);
s.addText("What the numbers mean",{x:8.7,y:4.1,w:3.8,h:0.35,fontFace:HEAD,fontSize:14,bold:true,color:CRIMSON,margin:0});
bullets(s,8.7,4.5,3.85,2.1,[
  "Signal floor is the same: sim 6.7 ~ measured 6.0 mm. Sim is realistic, not smoother.",
  "LOSO (3.9) sees a new session at KNOWN spots (easy); LOPO single-position (9.9) reaches an UNSEEN spot (hard, ~50 distinct positions).",
  "Sim hits 3.9 on unseen spots only via ~1000 distinct positions.",
],10.5);
s.addText("The sim vs measured CNN gap is distinct-position COVERAGE, not fidelity. To match 3.9 mm on the bench: denser grid / more depths, not a better model.",
  {x:0.6,y:6.75,w:7.7,h:0.55,fontFace:BODY,fontSize:11.5,italic:true,color:MUTE,align:"left",margin:0});

// ============ 7. SIM->MEASURED TRANSFER (exploratory)
s=pres.addSlide(); s.background={color:LIGHT};
title(s,"Can a model bridge the gap? (exploratory)","Learn a sim to measured map on the empty baseline, test on unseen frequencies");
s.addImage({path:"sim_meas_correlation.png",x:0.5,y:1.9,w:8.5,h:3.45});
card(s,9.2,1.8,3.55,4.1);
s.addText("First-pass finding",{x:9.4,y:1.97,w:3.2,h:0.4,fontFace:HEAD,fontSize:15,bold:true,color:CRIMSON,margin:0});
bullets(s,9.4,2.5,3.25,3.2,[
  "Raw sim-vs-measured |S| correlation: 0.61.",
  "A LINEAR transfer predicts measured from sim to R2 = 0.65 on frequencies it never saw, a real learnable relationship.",
  "A flexible MLP overfits the single paired baseline (R2 < 0).",
],11.5);
s.addText("Preliminary: only the empty baseline is cleanly paired. Nonlinear domain adaptation (and any use for calibrating sim toward the bench) needs far more paired data: multiple sessions and, ideally, matched tumor positions.",
  {x:0.6,y:6.6,w:W-1.2,h:0.6,fontFace:BODY,fontSize:12.5,italic:true,color:MUTE,align:"center",margin:0});

// ============ 8. CONCLUSIONS (light)
s=pres.addSlide();
closingLight(s,"Part 3, bottom line",[
 ["Sim and measured agree at the signal level","the empty phantom interpolates to ~6 mm on BOTH (k-NN); the simulation is realistic, not artificially smooth."],
 ["The detectable-difference pattern matches","bench and sim place the tumor's strongest change in the same regions (toward the antenna sides)."],
 ["The CNN gap is data coverage, not fidelity","sim's 3.9 mm comes from ~1000 distinct positions; measured's 9.9 mm from only ~50. Same model, different coverage."],
 ["Takes and sessions are not new positions","16 takes x 3 sessions add robustness (great for LOSO) but no new tumor locations (no help for interpolation)."],
 ["A sim to measured transfer is learnable","a linear map already reaches R2 = 0.65 on unseen frequencies, a promising if preliminary calibration path."],
]);

pres.writeFile({fileName:"Deck3_Sim_vs_Measured.pptx"}).then(f=>console.log("wrote "+f));
