// DECK 5 - Augmenting the simulation to match the bench (WHY + HOW each step).
// UofU warm-red theme, light title.  ->  Deck5_Sim_Augmentation.pptx
const pptxgen = require("pptxgenjs");
const CRIMSON="BE0000", GOLD="C8890B", INK="2A1618", MUTE="836A68", LIGHT="FFFFFF",
      CARD="FBF4F2", LINE="E7D6D1", CREAMBG="FDF8F6";
const HEAD="Cambria", BODY="Calibri";
const shadow=()=>({type:"outer",color:"7A5C5E",blur:7,offset:3,angle:90,opacity:0.18});
const pres=new pptxgen();
pres.defineLayout({name:"W",width:13.33,height:7.5}); pres.layout="W";
pres.author="Peter Martin"; pres.title="Sim Augmentation";
const W=13.33,H=7.5;
function title(s,t,sub){s.background={color:LIGHT};
  s.addShape(pres.shapes.RECTANGLE,{x:0,y:0,w:W,h:0.12,fill:{color:CRIMSON},line:{type:"none"}});
  s.addText(t,{x:0.55,y:0.32,w:W-1.1,h:0.62,fontFace:HEAD,fontSize:25,bold:true,color:INK,margin:0});
  if(sub)s.addText(sub,{x:0.55,y:0.98,w:W-1.1,h:0.4,fontFace:BODY,fontSize:13.5,color:CRIMSON,bold:true,margin:0});}
function card(s,x,y,w,h,fill){s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x,y,w,h,rectRadius:0.09,
  fill:{color:fill||CARD},line:{color:LINE,width:1},shadow:shadow()});}
function bullets(s,x,y,w,h,arr,fs){s.addText(arr.map(b=>({text:b.t!==undefined?b.t:b,options:{bullet:b.b!==false?{indent:14}:false,
  indentLevel:b.lvl||0,breakLine:true,paraSpaceAfter:7,bold:b.bold||false,color:b.color||INK}})),
  {x,y,w,h,fontFace:BODY,fontSize:fs||13.5,color:INK,valign:"top",margin:0});}
function titleLight(s,part,ttl,sub,stats){s.background={color:CREAMBG};
  s.addShape(pres.shapes.RECTANGLE,{x:0,y:0,w:W,h:0.26,fill:{color:CRIMSON},line:{type:"none"}});
  s.addShape(pres.shapes.RECTANGLE,{x:0.9,y:2.02,w:0.09,h:1.5,fill:{color:CRIMSON},line:{type:"none"}});
  s.addText(part,{x:1.2,y:2.02,w:11,h:0.45,fontFace:BODY,fontSize:15,color:CRIMSON,bold:true,charSpacing:3,margin:0});
  s.addText(ttl,{x:1.2,y:2.5,w:11.4,h:1.0,fontFace:HEAD,fontSize:33,bold:true,color:INK,margin:0});
  s.addText(sub,{x:1.2,y:3.72,w:11.2,h:0.8,fontFace:BODY,fontSize:15,color:MUTE,margin:0});
  stats.forEach((c,i)=>{const x=1.2+i*3.95;
    s.addText(c[0],{x,y:5.15,w:3.85,h:0.6,fontFace:HEAD,fontSize:20,bold:true,color:CRIMSON,margin:0});
    s.addText(c[1],{x,y:5.7,w:3.9,h:0.7,fontFace:BODY,fontSize:12.5,color:MUTE,margin:0});});}
function imgFit(s,path,aspect,top,maxH){const areaY=top||1.5,areaH=maxH||5.7,maxW=12.4;
  let w=maxW,h=maxW/aspect; if(h>areaH){h=areaH;w=areaH*aspect;}
  s.addImage({path,x:(W-w)/2,y:areaY+(areaH-h)/2,w,h});}

// ---- 1. TITLE ----
let s=pres.addSlide();
titleLight(s,"SIM AUGMENTATION","Making the simulation behave like the bench",
  "The HFSS sim is noise-free, so classification is trivially perfect and there are no sessions to hold out. We inject the bench's two measured nuisances so the sim supports LOSO and classification.",
  [["SNR ~6.6x","per-take measurement noise"],["~12%","cross-session drift"],["-> LOSO + classify","on augmented sim"]]);

// ---- 2. WHY AUGMENT ----
s=pres.addSlide(); title(s,"Why augment the simulation?",
  "The deterministic sim cannot exercise the protocols the bench uses");
card(s,0.6,1.6,6.0,4.9);
s.addText("The problem",{x:0.85,y:1.78,w:5.5,h:0.4,fontFace:HEAD,fontSize:16,bold:true,color:CRIMSON,margin:0});
bullets(s,0.85,2.35,5.55,4.0,[
  "HFSS gives ONE noise-free S-parameter set per position.",
  "Classification is then trivially 100% - each position is a unique, exactly-repeatable signal.",
  "There are no 'sessions' or repeat 'takes', so leave-one-session-out (LOSO) cannot even be run.",
  "So the sim can't tell us where a real system breaks under noise, reduced antennas, or narrow bandwidth.",
],13.5);
card(s,6.9,1.6,5.8,4.9);
s.addText("The fix",{x:7.15,y:1.78,w:5.4,h:0.4,fontFace:HEAD,fontSize:16,bold:true,color:CRIMSON,margin:0});
bullets(s,7.15,2.35,5.35,4.0,[
  "Inject the two nuisances the bench actually has, measured from the June18 A3 data:",
  {t:"per-take measurement noise (signal/noise ~6.6x)",lvl:1},
  {t:"cross-session drift (~12% of the signal)",lvl:1},
  "Synthesize N sessions x takes per position, so the augmented sim has the SAME data structure as the bench.",
  "Match the RATIOS, not absolute levels - the sim tumor signal is ~5-7x weaker (antenna-model mismatch).",
],13.5);

// ---- 3. WHAT THE BENCH HAS (the justification figure) ----
s=pres.addSlide(); title(s,"What the bench has that the sim lacks",
  "Measured on the tumor differential dS: per-take noise (A), session-to-session drift (B); the augmentation reproduces both (C)");
imgFit(s,"sim_augmentation.png",15.5/4.6,1.55,5.5);

// ---- 4. STEP 1: NOISE ----
s=pres.addSlide(); title(s,"Step 1: additive measurement noise",
  "Why: the bench has per-take noise    How: SNR-matched, per S-parameter");
card(s,0.6,1.6,6.0,4.9);
s.addText("Why",{x:0.85,y:1.78,w:5.5,h:0.4,fontFace:HEAD,fontSize:16,bold:true,color:CRIMSON,margin:0});
bullets(s,0.85,2.35,5.55,4.0,[
  "Each measured position is taken 16 times; the takes vary (thermal/receiver noise).",
  "Measured signal / take-to-take noise = ~6.6x (median over all S-parameters).",
  "Without this, the sim classifier never makes a mistake.",
],13.5);
card(s,6.9,1.6,5.8,4.9);
s.addText("How",{x:7.15,y:1.78,w:5.4,h:0.4,fontFace:HEAD,fontSize:16,bold:true,color:CRIMSON,margin:0});
bullets(s,7.15,2.35,5.35,4.0,[
  "Add complex Gaussian noise to each S-parameter, generating multiple synthetic takes per position.",
  {t:"noise std per channel:  sigma_c = sim_signal_c / SNR_c",bold:true},
  "SNR_c pulled per S-parameter from the bench (reflections higher, transmission lower), not one global value.",
  "This matches the bench's signal-to-noise ratio while respecting that the sim signal is weaker.",
],13.5);

// ---- 5. STEP 2: DRIFT ----
s=pres.addSlide(); title(s,"Step 2: cross-session drift",
  "Why: sessions differ, and LOSO must be a real test    How: common-mode, frequency-structured");
card(s,0.6,1.6,6.0,4.9);
s.addText("Why",{x:0.85,y:1.78,w:5.5,h:0.4,fontFace:HEAD,fontSize:16,bold:true,color:CRIMSON,margin:0});
bullets(s,0.85,2.35,5.55,4.0,[
  "Between sessions (recalibration, cabling, temperature) the response drifts ~12% of the signal.",
  "A per-session z-score removes any constant scale, so drift must be FREQUENCY-STRUCTURED to survive it.",
  "If it survives z-score, held-out sessions look genuinely different - so LOSO tests real generalization.",
],13.5);
card(s,6.9,1.6,5.8,4.9);
s.addText("How",{x:7.15,y:1.78,w:5.4,h:0.4,fontFace:HEAD,fontSize:16,bold:true,color:CRIMSON,margin:0});
bullets(s,7.15,2.35,5.35,4.0,[
  "Per session: a smooth complex gain (a few low-order frequency modes) shared across antennas,",
  {t:"+ a small per-antenna gain and a small frequency (resonance) jitter.",lvl:1},
  "Kept mostly COMMON-MODE across the 4 antennas so the 'which-antenna' spatial pattern is not scrambled.",
  "Amplitude set so the synthetic cross-session variation lands at ~12%, matching the bench.",
],13.5);

// ---- 6. VALIDATION ----
s=pres.addSlide(); title(s,"Validation: synthetic vs bench",
  "The augmented sim reproduces the measured statistics it was calibrated to");
const rows=[["Statistic","Bench (June18 A3)","Augmented sim"],
  ["Per-channel SNR (signal / noise)","6.6x","6.8x  (matched per S-param)"],
  ["Cross-session drift (% of signal)","~12%","13%"],
  ["Full-config LOSO classification","~99-100%","99.5%  (CNN)"],
  ["Noiseless sanity (no nuisances)","-","100%  (trivial)"]];
s.addTable(rows.map((r,ri)=>r.map((c,ci)=>({text:c,options:{
  fontFace:BODY,bold:ri===0||ci===0,fontSize:14,color:ri===0?LIGHT:(ci>0&&ri>0?CRIMSON:INK),
  align:ci===0?"left":"center",valign:"middle",fill:{color:ri===0?CRIMSON:(ri%2?CARD:LIGHT)},margin:[6,8,6,8]}}))),
  {x:1.0,y:1.9,w:11.3,colW:[5.1,3.1,3.1],rowH:0.78,border:{type:"solid",color:LINE,pt:1}});
s.addText("Calibrated to, and validated against, the same measured baselines/tumor takes - not tuned by hand.",
  {x:1.0,y:6.4,w:11.3,h:0.5,fontFace:BODY,fontSize:13,italic:true,color:MUTE,align:"center",margin:0});

// ---- 7. RESULT: classification (measured = your classification-CNN track) ----
s=pres.addSlide(); title(s,"Result: classification under reduction (LOSO)",
  "Measured (Empty/F4/F5) = the classification-CNN track (cnn_loso, per-position vote); Sim = augmented. Black box = <50%.");
imgFit(s,"classify_grid_matched.png",16.0/10.5,1.5,5.75);

// ---- 8. RESULT: regression on augmented sim ----
s=pres.addSlide(); title(s,"Regression (x,y) on the augmented sim (LOSO)",
  "Median lateral error under hardware x band reduction; reflection-only beats all-16 once realistic noise is present");
imgFit(s,"sim_reg_noisy_grid.png",9.5/5.2,1.55,5.6);

pres.writeFile({fileName:"Deck5_Sim_Augmentation.pptx"}).then(f=>console.log("wrote "+f));
