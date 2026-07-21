// DECK 2 - Simulated 3D (x,y,z) regression. UofU warm-red theme, light titles.
//   ->  Deck2_Simulated_Regression.pptx
const pptxgen = require("pptxgenjs");
const CRIMSON="BE0000", CRIMSONDK="8E1010", GOLD="C8890B", ROSE="E0A99E",
      REDMID="C0564A", INK="2A1618", MUTE="836A68", LIGHT="FFFFFF",
      CARD="FBF4F2", LINE="E7D6D1", CREAM="EAD3CB", GRAYW="C9B3AE", CREAMBG="FDF8F6";
const HEAD="Cambria", BODY="Calibri";
const shadow=()=>({type:"outer",color:"7A5C5E",blur:7,offset:3,angle:90,opacity:0.18});
const pres=new pptxgen();
pres.defineLayout({name:"W",width:13.33,height:7.5}); pres.layout="W";
pres.author="Peter Martin"; pres.title="Simulated Regression";
const W=13.33,H=7.5;
function title(s,t,sub){
  s.addText(t,{x:0.6,y:0.42,w:W-1.2,h:0.7,fontFace:HEAD,fontSize:29,bold:true,color:INK,margin:0});
  if(sub)s.addText(sub,{x:0.6,y:1.13,w:W-1.2,h:0.4,fontFace:BODY,fontSize:14,color:CRIMSON,bold:true,margin:0});}
function card(s,x,y,w,h,fill){s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x,y,w,h,rectRadius:0.09,
  fill:{color:fill||CARD},line:{color:LINE,width:1},shadow:shadow()});}
function bullets(s,x,y,w,h,arr,fs){s.addText(arr.map(b=>({text:b,options:{bullet:true,breakLine:true,paraSpaceAfter:8}})),
  {x,y,w,h,fontFace:BODY,fontSize:fs||13,color:INK,valign:"top",margin:0});}
function numberedCards(s,items,accent){
  items.forEach((st,i)=>{const y=1.75+i*1.28; card(s,0.6,y,W-1.2,1.12);
    s.addShape(pres.shapes.OVAL,{x:0.85,y:y+0.28,w:0.56,h:0.56,fill:{color:accent}});
    s.addText(String(i+1),{x:0.85,y:y+0.28,w:0.56,h:0.56,align:"center",valign:"middle",fontFace:HEAD,fontSize:20,bold:true,color:LIGHT,margin:0});
    s.addText(st[0],{x:1.65,y:y+0.16,w:2.2,h:0.8,fontFace:HEAD,fontSize:17,bold:true,color:accent,valign:"middle",margin:0});
    s.addText(st[1],{x:3.95,y:y+0.06,w:W-4.75,h:1.0,fontFace:BODY,fontSize:12.5,color:INK,valign:"middle",margin:0});});}
function statcard(s,x,y,w,big,small,col){card(s,x,y,w,1.55);
  s.addText(big,{x,y:y+0.18,w,h:0.7,align:"center",fontFace:HEAD,fontSize:30,bold:true,color:col||CRIMSON,margin:0});
  s.addText(small,{x:x+0.1,y:y+0.95,w:w-0.2,h:0.5,align:"center",fontFace:BODY,fontSize:12.5,color:MUTE,margin:0});}
// light title slide: mostly white, crimson highlights
function titleLight(s,part,ttl,sub,stats){s.background={color:CREAMBG};
  s.addShape(pres.shapes.RECTANGLE,{x:0,y:0,w:W,h:0.26,fill:{color:CRIMSON},line:{type:"none"}});
  s.addShape(pres.shapes.RECTANGLE,{x:0.9,y:2.02,w:0.09,h:1.5,fill:{color:CRIMSON},line:{type:"none"}});
  s.addText(part,{x:1.2,y:2.02,w:11,h:0.45,fontFace:BODY,fontSize:15,color:CRIMSON,bold:true,charSpacing:3,margin:0});
  s.addText(ttl,{x:1.2,y:2.5,w:11.2,h:1.0,fontFace:HEAD,fontSize:36,bold:true,color:INK,margin:0});
  s.addText(sub,{x:1.2,y:3.62,w:11.0,h:0.7,fontFace:BODY,fontSize:15.5,color:MUTE,margin:0});
  stats.forEach((c,i)=>{const x=1.2+i*3.95;
    s.addText(c[0],{x,y:4.95,w:3.7,h:0.7,fontFace:HEAD,fontSize:28,bold:true,color:CRIMSON,margin:0});
    s.addText(c[1],{x,y:5.62,w:3.85,h:0.6,fontFace:BODY,fontSize:12.5,color:MUTE,margin:0});});}
function closingLight(s,heading,items){s.background={color:CREAMBG};
  s.addShape(pres.shapes.RECTANGLE,{x:0,y:0,w:W,h:0.26,fill:{color:CRIMSON},line:{type:"none"}});
  s.addText(heading,{x:0.9,y:0.7,w:11,h:0.8,fontFace:HEAD,fontSize:28,bold:true,color:CRIMSON,margin:0});
  items.forEach((c,i)=>{const y=1.7+i*1.06;
    s.addShape(pres.shapes.OVAL,{x:0.9,y:y+0.05,w:0.42,h:0.42,fill:{color:CRIMSON}});
    s.addText(String(i+1),{x:0.9,y:y+0.05,w:0.42,h:0.42,align:"center",valign:"middle",fontFace:HEAD,fontSize:15,bold:true,color:LIGHT,margin:0});
    s.addText([{text:c[0]+":  ",options:{bold:true,color:INK}},{text:c[1],options:{color:MUTE}}],
      {x:1.5,y:y-0.05,w:11.2,h:0.95,fontFace:BODY,fontSize:14,valign:"middle",margin:0});});
  s.addText("github.com/pmart1534/microwave-phantom-localization-cnn-mlp",{x:0.9,y:7.0,w:11.5,h:0.35,fontFace:BODY,fontSize:11,color:CRIMSON,margin:0});}
function imgCaption(s,x,y,w,h,path,cap){card(s,x-0.1,y-0.1,w+0.2,h+0.55);
  s.addImage({path,x,y,w,h});
  s.addText(cap,{x:x-0.1,y:y+h+0.02,w:w+0.2,h:0.4,align:"center",fontFace:BODY,fontSize:13,bold:true,color:INK,margin:0});}

// ============ 1. TITLE (light)
let s=pres.addSlide();
titleLight(s,"PART 2 . SIMULATED DATA","3D (x, y, z) tumor localization in HFSS",
  "A dense simulated tumor sweep (91 positions x 13 depth planes) lets us resolve depth and measure how much data the CNN needs",
  [["3.9 mm","lateral error (8-fold)"],["2.1 mm","depth error, not the weak axis"],["~450","training positions needed"]]);

// ============ 2. SIM SETUP
s=pres.addSlide(); s.background={color:LIGHT};
title(s,"Simulation setup","HFSS full-wave model of Sam's Medium antennas + the A3 phantom (SamMakin tumor sweep)");
numberedCards(s,[
  ["Model","HFSS full-wave solve of Sam's Medium antennas (the same 4-antenna array as the bench) around the A3 phantom in oil. A metal tumor is moved through a 3D grid; a dielectric (beet) tumor is run identically for comparison."],
  ["Sampling","Uniform 10 mm (x,y) lattice, 91 positions, swept over 13 depth planes z = -15 to +45 mm (5 mm steps). 1074 tumor positions total (off-grid z = 3 mm excluded)."],
  ["Signal","4-port S-matrix exported 2 to 8 GHz (3001 pts, resampled to 256). Input = differential dS = S(tumor) minus S(empty), using each depth's own HFSS-batch empty baseline."],
  ["Task","Same conv trunk as the measured CNN, head to fc(3) for (x,y,z) in mm. 8-fold position cross-validation; lateral and depth error reported separately."],
],CRIMSON);

// ============ 3. SETUP IN PICTURES
s=pres.addSlide(); s.background={color:LIGHT};
title(s,"The simulated setup, in pictures","HFSS model of the antenna array, phantom and tumor");
imgCaption(s,1.15,1.9,5.2,3.9,"setup_photos/sim_model.png","Full HFSS model");
imgCaption(s,6.95,1.9,5.2,3.9,"setup_photos/sim_closeup.png","Antennas + tumor closeup");
s.addText("Replace the placeholders in regression_deck/setup_photos/ (sim_model.*, sim_closeup.*) with real HFSS screenshots.",
  {x:0.6,y:6.05,w:W-1.2,h:0.5,fontFace:BODY,fontSize:12.5,italic:true,color:MUTE,align:"center",margin:0});

// ============ 4. DEPTH STRUCTURE + dS-vs-depth
s=pres.addSlide(); s.background={color:LIGHT};
title(s,"Depth planes and the signal they carry","13 tumor heights; the perturbation peaks at the radiating patch and fades with distance");
s.addImage({path:"sim_dS_vs_depth.png",x:0.45,y:1.95,w:8.0,h:4.41});
card(s,8.7,1.8,4.05,4.85);
s.addText("The physical driver",{x:8.95,y:2.0,w:3.6,h:0.4,fontFace:HEAD,fontSize:16,bold:true,color:CRIMSON,margin:0});
bullets(s,8.95,2.55,3.6,4.0,[
  "dS = tumor minus empty, averaged over frequency and all 16 S-parameters.",
  "Port/feed is at z = +3 mm, but the radiating patch sits ~15 to 20 mm in (feed-line offset).",
  "dS peaks right at the patch (~15 to 20 mm), where the tumor is nearest the radiator.",
  "Falls off both ways; far depths carry the least signal, so localization degrades there. (Measured tumor sat at z = +40 mm.)",
],12);

// ============ 4b. MEASURED CONFIRMS THE DEPTH SHAPE
s=pres.addSlide(); s.background={color:LIGHT};
title(s,"The bench sees the same depth shape","Measured tumor perturbation across 4 heights, independent of the simulation");
s.addImage({path:"measured_dS_vs_depth.png",x:0.45,y:1.95,w:8.0,h:4.70});
card(s,8.7,1.8,4.05,4.85);
s.addText("Same story on the bench",{x:8.95,y:2.0,w:3.6,h:0.4,fontFace:HEAD,fontSize:16,bold:true,color:CRIMSON,margin:0});
bullets(s,8.95,2.55,3.6,4.0,[
  "4 measured tumor heights (July10), a full 51-position grid at each.",
  "Mean |dS| peaks at +15 mm, right at the radiating patch, exactly like the sim.",
  "Falls off both ways; the bench and the simulation agree on where the signal lives.",
  "Depths are port-relative; the +25 mm session was mislabeled '2.5 cm below' in the README.",
],12);

// ============ 5. ALGORITHM
s=pres.addSlide(); s.background={color:LIGHT};
title(s,"The 3D localization network","Same architecture as the measured CNN, with one extra output for depth");
numberedCards(s,[
  ["Input","dS as a 32 x 256 image (16 S-params x [mag, phase], 256 frequencies). Per-sample z-score normalization."],
  ["Trunk","2 conv blocks (32 filters each) plus pooling and dropout, identical to the measured (x,y) CNN."],
  ["Head","fc(3) plus regression to (x, y, z) in mm. Trained with an L2 coordinate loss, 60 epochs."],
  ["Evaluation","8-fold hold-out by POSITION (every position predicted once, out-of-fold). Lateral = sqrt(dx^2+dy^2); depth = |dz|, reported separately so one axis cannot hide the other."],
],CRIMSON);

// ============ 6. HOW MUCH DATA
s=pres.addSlide(); s.background={color:LIGHT};
title(s,"How much data does the CNN need?","Train on more depth planes (more distinct positions) and watch the error fall");
s.addImage({path:"sim_depth_learning_curve.png",x:0.5,y:1.75,w:7.9,h:4.92});
card(s,8.6,1.75,4.15,4.92);
s.addText("The threshold",{x:8.85,y:1.95,w:3.7,h:0.4,fontFace:HEAD,fontSize:16,bold:true,color:CRIMSON,margin:0});
bullets(s,8.85,2.5,3.7,4.0,[
  "1 depth plane (82 positions): 33 mm, about chance. The conv net cannot train.",
  "3 planes (245): 11 mm. 5 planes (410): 4.8 mm.",
  "Plateau ~3.8 mm from 7 planes (about 570) on.",
  "So it needs ~400 to 500 DISTINCT positions to localize; below ~250 it is poor.",
  "Distinct positions matter, not raw sample count (see Part 3).",
],12);

// ============ 7. 8-FOLD RESULTS
s=pres.addSlide(); s.background={color:LIGHT};
title(s,"3D localization result (8-fold)","Every position predicted from a model that never saw it, lateral and depth separately");
statcard(s,0.7,1.9,2.75,"3.9 mm","lateral (xy) median\nvs 36.5 mm chance",CRIMSON);
statcard(s,3.65,1.9,2.75,"2.1 mm","depth (z) median\nvs 16.3 mm chance",REDMID);
statcard(s,6.6,1.9,2.75,"93 %","of positions within\n10 mm laterally",CRIMSONDK);
statcard(s,9.55,1.9,2.75,"3.6 / 2.1","beet (dielectric)\nxy / z, same as metal",GOLD);
card(s,0.7,3.75,11.6,2.95);
s.addText("What this establishes",{x:1.0,y:3.95,w:10,h:0.4,fontFace:HEAD,fontSize:17,bold:true,color:CRIMSON,margin:0});
bullets(s,1.0,4.5,11.3,2.1,[
  "Depth is NOT the weak axis. With fine depth sampling and full-band frequency, z resolves to ~2 mm, better than the lateral k-NN floor.",
  "A dielectric (beet) tumor localizes identically to metal (3.6 / 2.1 mm). In the noiseless sim the ~19 percent weaker contrast costs nothing.",
  "Chance is 36 mm laterally / 16 mm in depth, so the model is about 10x better than guessing the centre on both axes.",
],13.5);

// ============ 8. DEPTH GENERALIZATION
s=pres.addSlide(); s.background={color:LIGHT};
title(s,"Predicting an unseen depth plane","Leave one whole depth out; interior depths interpolate, only the outer edge depths fail");
s.addImage({path:"sim_depth_lopo.png",x:0.4,y:1.75,w:9.4,h:3.9});
card(s,9.95,1.75,2.9,3.9);
s.addText("Range-bound, not model-bound",{x:10.15,y:1.9,w:2.6,h:0.6,fontFace:HEAD,fontSize:14,bold:true,color:CRIMSON,margin:0});
bullets(s,10.15,2.6,2.6,3.0,[
  "Interior unseen depths: ~1 to 3 mm, a continuous learned depth map.",
  "Only the two outer edge depths (-15 / +45) blow up, pure extrapolation.",
  "Extending the sweep turned the OLD outer edges into good interior points.",
],11.5);
s.addText("Usable depth is bounded by the sampling range, not the model. Sample wider and the good region grows.",
  {x:0.6,y:6.75,w:W-1.2,h:0.5,fontFace:BODY,fontSize:13.5,italic:true,color:MUTE,align:"center",margin:0});

// ============ 9. PER-DEPTH PREDICTION EXAMPLES
s=pres.addSlide(); s.background={color:LIGHT};
title(s,"Predicted vs. actual, by depth","Arrows = lateral error, marker color = depth error, red ring = grid-edge position");
const iw=3.95,ih=3.75,gap=0.3,tot=3*iw+2*gap,sx=(W-tot)/2,iy=1.85;
[["sim_depth_examples/sim_depthplot_zp15_n25.png","z = +15 mm  (peak signal)"],
 ["sim_depth_examples/sim_depthplot_zp30_n25.png","z = +30 mm  (interior)"],
 ["sim_depth_examples/sim_depthplot_zp45_n25.png","z = +45 mm  (outer edge)"]].forEach((e,i)=>{
  const x=sx+i*(iw+gap); card(s,x-0.1,iy-0.12,iw+0.2,ih+0.6);
  s.addImage({path:e[0],x,y:iy,w:iw,h:ih});
  s.addText(e[1],{x:x-0.1,y:iy+ih+0.0,w:iw+0.2,h:0.36,align:"center",fontFace:BODY,fontSize:13,bold:true,color:CRIMSON,margin:0});});
s.addText("Interior depths (z=+15/+30) predict tightly; the +45 mm outer edge shows the extrapolation blow-up in both lateral arrows and depth color.",
  {x:0.6,y:6.7,w:W-1.2,h:0.5,fontFace:BODY,fontSize:13,italic:true,color:MUTE,align:"center",margin:0});

// ============ 10. CONCLUSIONS (light)
s=pres.addSlide();
closingLight(s,"Part 2, bottom line",[
 ["Full 3D localization works in sim","3.9 mm lateral, 2.1 mm depth. The CNN resolves all three coordinates well below a grid step."],
 ["Depth is a strong axis, not a weak one","fine depth sampling and full-band frequency make z (~2 mm) actually beat the lateral floor."],
 ["The CNN needs ~400 to 500 distinct positions","below that it degrades fast; at one depth plane (82) it collapses to chance. A concrete data target."],
 ["Depth generalizes across the sampled range","unseen interior depths interpolate to ~1 to 3 mm; only the outer edge depths extrapolate and fail."],
 ["Metal is about equal to dielectric in the noiseless sim","a beet tumor localizes as well as metal, so realistic contrast is not the bottleneck here."],
]);

pres.writeFile({fileName:"Deck2_Simulated_Regression.pptx"}).then(f=>console.log("wrote "+f));
