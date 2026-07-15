// DECK 1 — Measured phantom (x,y) regression: setup, algorithm, LOSO / LOPO-cell
// / LOPO-single-position across Empty, F4, F5.  ->  Deck1_Measured_Regression.pptx
const pptxgen = require("pptxgenjs");
const NAVY="0E2233",BLUE="0B5D7A",TEAL="1C9AA8",MINT="2CC4A3",CORAL="D64545",
      AMBER="E0A100",INK="1E293B",MUTE="5B6B7B",LIGHT="FFFFFF",CARD="F3F7FA",LINE="D8E2EA";
const HEAD="Cambria",BODY="Calibri";
const shadow=()=>({type:"outer",color:"5B6B7B",blur:7,offset:3,angle:90,opacity:0.18});
const pres=new pptxgen();
pres.defineLayout({name:"W",width:13.33,height:7.5}); pres.layout="W";
pres.author="Peter Martin"; pres.title="Measured Regression";
const W=13.33,H=7.5;
function title(s,t,sub){
  s.addText(t,{x:0.6,y:0.42,w:W-1.2,h:0.7,fontFace:HEAD,fontSize:29,bold:true,color:INK,margin:0});
  if(sub)s.addText(sub,{x:0.6,y:1.13,w:W-1.2,h:0.4,fontFace:BODY,fontSize:14,color:TEAL,bold:true,margin:0});}
function card(s,x,y,w,h,fill){s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x,y,w,h,rectRadius:0.09,
  fill:{color:fill||CARD},line:{color:LINE,width:1},shadow:shadow()});}
function triPanel(s,items,takeaway,iy){
  iy=iy||1.92; const iw=3.5,ih=3.62,gap=0.35,tot=3*iw+2*gap,sx=(W-tot)/2;
  items.forEach((e,i)=>{const x=sx+i*(iw+gap);
    card(s,x-0.12,iy-0.14,iw+0.24,ih+0.7);
    s.addImage({path:e[0],x,y:iy,w:iw,h:ih});
    s.addText([{text:e[1]+"   ",options:{bold:true,color:INK}},{text:e[2],options:{color:TEAL,bold:true}}],
      {x:x-0.12,y:iy+ih+0.02,w:iw+0.24,h:0.38,align:"center",fontFace:BODY,fontSize:13,margin:0});});
  s.addText(takeaway,{x:0.6,y:6.72,w:W-1.2,h:0.5,fontFace:BODY,fontSize:13.5,italic:true,color:MUTE,align:"center",margin:0});}
function bullets(s,x,y,w,h,arr,fs){s.addText(arr.map((b,i)=>({text:b,options:{bullet:true,breakLine:true,paraSpaceAfter:8}})),
  {x,y,w,h,fontFace:BODY,fontSize:fs||13,color:INK,valign:"top",margin:0});}

// ============ 1. TITLE
let s=pres.addSlide(); s.background={color:NAVY};
s.addText("PART 1 · PHYSICAL MEASUREMENTS",{x:0.9,y:2.05,w:11.5,h:0.5,fontFace:BODY,fontSize:15,color:MINT,bold:true,charSpacing:3,margin:0});
s.addText("(x, y) tumor localization on the A3 phantom",{x:0.9,y:2.6,w:11.5,h:1.1,fontFace:HEAD,fontSize:38,bold:true,color:LIGHT,margin:0});
s.addText("Bench VNA S-parameters → continuous coordinate regression — CNN vs MLP, under LOSO, LOPO-cell and single-position hold-out",
  {x:0.9,y:3.8,w:11.4,h:0.7,fontFace:BODY,fontSize:15.5,color:"AECBD6",margin:0});
[["0.15 in","best cross-session error (empty)"],["3.9 mm","= a sixth of a grid cell"],["3 phantoms","empty · F4 · F5 inserts"]].forEach((c,i)=>{
  const x=0.9+i*3.95;
  s.addText(c[0],{x,y:4.95,w:3.7,h:0.7,fontFace:HEAD,fontSize:28,bold:true,color:MINT,margin:0});
  s.addText(c[1],{x,y:5.62,w:3.7,h:0.6,fontFace:BODY,fontSize:12.5,color:"AECBD6",margin:0});});

// ============ 2. MEASUREMENT SETUP
s=pres.addSlide(); s.background={color:LIGHT};
title(s,"Measurement setup","4-port VNA · A3 breast phantom in canola oil · Sam Medium antennas");
const setup=[
  ["Phantom & medium","A3 breast phantom submerged in canola oil (breast-tissue-like permittivity). A metal 'fishing-weight' tumor is moved to each grid position."],
  ["RF acquisition","4 antennas → 4-port VNA. Full 4×4 S-matrix (16 S-parameters), magnitude+phase, swept 0.1–8 GHz (791 points)."],
  ["Sampling grid","6×6 array of cells, pitch ≈25.4×23.85 mm. Each cell has 4 sub-positions at its corners (±9.5 mm). ~51 sub-positions measured on the empty phantom."],
  ["Repeats & sessions","16 takes per position; 3 sessions per phantom (re-set between sessions → real drift). Three phantom variants: empty, F4 (small glandular insert), F5 (large insert)."],
];
setup.forEach((st,i)=>{const y=1.75+i*1.28; card(s,0.6,y,W-1.2,1.12);
  s.addShape(pres.shapes.OVAL,{x:0.85,y:y+0.28,w:0.56,h:0.56,fill:{color:BLUE}});
  s.addText(String(i+1),{x:0.85,y:y+0.28,w:0.56,h:0.56,align:"center",valign:"middle",fontFace:HEAD,fontSize:20,bold:true,color:LIGHT,margin:0});
  s.addText(st[0],{x:1.65,y:y+0.16,w:2.5,h:0.8,fontFace:HEAD,fontSize:17,bold:true,color:BLUE,valign:"middle",margin:0});
  s.addText(st[1],{x:4.25,y:y+0.08,w:W-5.05,h:0.96,fontFace:BODY,fontSize:13,color:INK,valign:"middle",margin:0});});

// ============ 3. ALGORITHM & TRAINING
s=pres.addSlide(); s.background={color:LIGHT};
title(s,"From “which cell” to “exact (x, y)”","Same CNN & MLP as the classifier — the head swapped for coordinate regression");
const steps=[
  ["Targets","Grid label RnCmPp → true (x,y) in inches (±0.375 in corner offsets; photo-digitized where an insert blocked a corner). Never snapped to a grid point."],
  ["Models","CNN: conv trunk (32→32) → fc(2) + regression. MLP: 3-seed ensemble. Input = raw 16 S-params as a 32×freq image; per-session z-score; v2 preprocessing (no session-mean)."],
  ["Metric","Euclidean error in inches (×25.4 = mm). Median error + % within the 0.5-in half-cell; near-insert vs exterior reported separately."],
  ["Protocols","LOSO = hold out a whole session. LOPO-cell = hold out a whole 1-in cell. LOPO-subpos = hold out a single sub-position (its cell-mates stay in training)."],
];
steps.forEach((st,i)=>{const y=1.75+i*1.28; card(s,0.6,y,W-1.2,1.12);
  s.addShape(pres.shapes.OVAL,{x:0.85,y:y+0.28,w:0.56,h:0.56,fill:{color:TEAL}});
  s.addText(String(i+1),{x:0.85,y:y+0.28,w:0.56,h:0.56,align:"center",valign:"middle",fontFace:HEAD,fontSize:20,bold:true,color:LIGHT,margin:0});
  s.addText(st[0],{x:1.65,y:y+0.16,w:2.4,h:0.8,fontFace:HEAD,fontSize:17,bold:true,color:TEAL,valign:"middle",margin:0});
  s.addText(st[1],{x:4.1,y:y+0.06,w:W-4.9,h:1.0,fontFace:BODY,fontSize:12.5,color:INK,valign:"middle",margin:0});});

// ============ 4. LOSO RESULTS
s=pres.addSlide(); s.background={color:LIGHT};
title(s,"New scan of a known grid (LOSO)","Median localization error — the CNN nails it; the MLP lags and physics features break it");
s.addChart(pres.charts.BAR,[
  {name:"CNN (raw)",labels:["Empty","F4 insert","F5 insert"],values:[0.154,0.164,0.223]},
  {name:"MLP (raw)",labels:["Empty","F4 insert","F5 insert"],values:[0.481,0.695,0.759]},
  {name:"predict-centre (chance)",labels:["Empty","F4 insert","F5 insert"],values:[1.34,1.73,1.30]},
],{x:0.6,y:1.7,w:7.5,h:5.1,barDir:"col",chartColors:[BLUE,AMBER,"C3CED6"],showValue:true,dataLabelPosition:"outEnd",
  dataLabelColor:INK,dataLabelFontSize:10,dataLabelFormatCode:"0.00",valAxisTitle:"median error (inches)",showValAxisTitle:true,
  valAxisTitleColor:MUTE,valAxisTitleFontSize:12,catAxisLabelColor:INK,catAxisLabelFontSize:13,valAxisLabelColor:MUTE,
  valGridLine:{color:"EAF0F4",size:0.5},catGridLine:{style:"none"},showLegend:true,legendPos:"t",legendColor:INK,legendFontSize:11,valAxisMaxVal:2,valAxisMinVal:0});
card(s,8.5,1.7,4.2,5.1);
s.addText("What it says",{x:8.75,y:1.9,w:3.7,h:0.4,fontFace:HEAD,fontSize:16,bold:true,color:BLUE,margin:0});
bullets(s,8.75,2.4,3.7,4.2,[
  "CNN wins everywhere — 0.15 in (3.9 mm) on empty, under ¼ in even on F5.",
  "Raw ≈ physics for the CNN, so raw is the pick (simpler, faster).",
  "MLP is 3–4× worse; with physics it collapses to the predict-centre baseline.",
  "≥90 % of positions land within the half-cell on all three phantoms.",
]);

// ============ 5. LOSO EXAMPLES
s=pres.addSlide(); s.background={color:LIGHT};
title(s,"Predicted vs. actual — LOSO","Diamonds = CNN prediction · circles = true position · arrow = the error");
triPanel(s,[["pred_vs_actual_loso_empty.png","Empty","0.15 in"],["pred_vs_actual_loso_f4.png","F4 insert","0.16 in"],["pred_vs_actual_loso_f5.png","F5 insert","0.22 in"]],
  "Across empty, small (F4) and large (F5) inserts the CNN lands within a fifth of a cell — a new measurement session is not a problem.");

// ============ 6. LOPO-CELL RESULTS
s=pres.addSlide(); s.background={color:LIGHT};
title(s,"Interpolating to an unseen cell (LOPO-cell)","Hold a whole 1-in cell out of training — predict a spot with no signature nearby");
s.addChart(pres.charts.BAR,[
  {name:"pooled (all sessions)",labels:["Empty","F4 insert","F5 insert"],values:[0.473,0.487,0.667]},
  {name:"in-session (drift removed)",labels:["Empty","F4 insert","F5 insert"],values:[0.661,0.609,0.753]},
],{x:0.6,y:1.7,w:7.5,h:5.1,barDir:"col",chartColors:[TEAL,"9AC7CE"],showValue:true,dataLabelPosition:"outEnd",
  dataLabelColor:INK,dataLabelFontSize:11,dataLabelFormatCode:"0.00",valAxisTitle:"median error (inches)",showValAxisTitle:true,
  valAxisTitleColor:MUTE,valAxisTitleFontSize:12,catAxisLabelColor:INK,catAxisLabelFontSize:13,valAxisLabelColor:MUTE,
  valGridLine:{color:"EAF0F4",size:0.5},catGridLine:{style:"none"},showLegend:true,legendPos:"t",legendColor:INK,legendFontSize:11,valAxisMaxVal:1,valAxisMinVal:0});
card(s,8.5,1.7,4.2,5.1);
s.addText("Three findings",{x:8.75,y:1.9,w:3.7,h:0.4,fontFace:HEAD,fontSize:16,bold:true,color:TEAL,margin:0});
bullets(s,8.75,2.4,3.7,4.2,[
  "Interpolation is 3–4× harder than session transfer (0.47–0.67 vs 0.15–0.22 in).",
  "Pooled beats in-session on all three — for interpolation, more data > removing drift.",
  "The glandular barrier surfaces: near-insert cells become WORSE than exterior (reverse of LOSO).",
]);

// ============ 7. LOPO-CELL EXAMPLES
s=pres.addSlide(); s.background={color:LIGHT};
title(s,"Predicted vs. actual — LOPO-cell (unseen cells)","Arrows grow and pull inward; red-ringed points sit over the glandular insert");
triPanel(s,[["pred_vs_actual_lopo_empty.png","Empty","0.47 in"],["pred_vs_actual_lopo_f4.png","F4 insert","0.49 in"],["pred_vs_actual_lopo_f5.png","F5 insert","0.67 in"]],
  "Interpolation error climbs with insert size (0.47 → 0.49 → 0.67 in) and concentrates near the insert — the CNN can't bridge a dielectric barrier it never sampled.");

// ============ 8. LOPO-SUBPOS (single position)
s=pres.addSlide(); s.background={color:LIGHT};
title(s,"Hold out a single position (LOPO-subpos)","Remove ONE sub-position — its 3 cell-mates (~0.375 in away) stay in training");
s.addImage({path:"../results/cnn_reglopo_pooled_subpos_June18_remap_raw_spatial.png",x:0.55,y:1.75,w:5.0,h:4.9});
s.addText("Empty · 0.39 in (9.9 mm)",{x:0.55,y:6.62,w:5.0,h:0.35,align:"center",fontFace:BODY,fontSize:13,bold:true,color:TEAL,margin:0});
s.addImage({path:"../results/cnn_reglopo_pooled_subpos_A3_F5_SamMed_last3_raw_spatial.png",x:5.75,y:1.75,w:5.0,h:4.9});
s.addText("F5 insert · 0.55 in (13.9 mm)",{x:5.75,y:6.62,w:5.0,h:0.35,align:"center",fontFace:BODY,fontSize:13,bold:true,color:TEAL,margin:0});
card(s,10.95,1.75,1.9,4.9);
s.addText("Why easier than cell",{x:11.05,y:1.9,w:1.7,h:0.6,fontFace:HEAD,fontSize:13.5,bold:true,color:BLUE,margin:0});
s.addText([{text:"Cell-mates remain as close anchors, so subpos < cell error:",options:{breakLine:true,paraSpaceAfter:6}},
  {text:"empty 0.39 vs 0.47 in",options:{bullet:true,breakLine:true,fontSize:11}},
  {text:"F5 0.55 vs 0.67 in",options:{bullet:true,breakLine:true,fontSize:11}},
  {text:"Still > the 6 mm k-NN signal floor → the CNN is data-starved on ~50 positions (see Part 3).",options:{fontSize:11}}],
  {x:11.05,y:2.55,w:1.7,h:4.0,fontFace:BODY,fontSize:11.5,color:INK,valign:"top",margin:0});

// ============ 9. PROTOCOL COMPARISON
s=pres.addSlide(); s.background={color:LIGHT};
title(s,"All three protocols side by side","How hard is each generalization task? (raw-CNN median error, inches)");
s.addChart(pres.charts.BAR,[
  {name:"LOSO (new session)",labels:["Empty","F4","F5"],values:[0.154,0.164,0.223]},
  {name:"LOPO-subpos (1 point)",labels:["Empty","F4","F5"],values:[0.392,null,0.546]},
  {name:"LOPO-cell (whole cell)",labels:["Empty","F4","F5"],values:[0.473,0.487,0.667]},
],{x:0.6,y:1.7,w:7.7,h:5.1,barDir:"col",chartColors:[BLUE,MINT,TEAL],showValue:true,dataLabelPosition:"outEnd",
  dataLabelColor:INK,dataLabelFontSize:10,dataLabelFormatCode:"0.00",valAxisTitle:"median error (inches)",showValAxisTitle:true,
  valAxisTitleColor:MUTE,valAxisTitleFontSize:12,catAxisLabelColor:INK,catAxisLabelFontSize:13,valAxisLabelColor:MUTE,
  valGridLine:{color:"EAF0F4",size:0.5},catGridLine:{style:"none"},showLegend:true,legendPos:"t",legendColor:INK,legendFontSize:11,valAxisMaxVal:0.8,valAxisMinVal:0});
card(s,8.6,1.7,4.1,5.1);
s.addText("The ladder of difficulty",{x:8.85,y:1.9,w:3.6,h:0.4,fontFace:HEAD,fontSize:15,bold:true,color:BLUE,margin:0});
bullets(s,8.85,2.4,3.6,4.2,[
  "LOSO (0.15–0.22 in): a new scan of KNOWN positions — easy.",
  "LOPO-subpos (0.39–0.55): unseen point, close anchors — medium.",
  "LOPO-cell (0.47–0.67): unseen 1-in cell, no anchor — hardest.",
  "Insert size raises every bar; the gap widens as the task gets harder.",
]);

// ============ 10. IMPROVING INTERPOLATION
s=pres.addSlide(); s.background={color:LIGHT};
title(s,"Can we teach it to interpolate?","Three fixes on the hardest case (F5 LOPO-cell, baseline 0.664 in) — only one helps");
s.addChart(pres.charts.BAR,[{name:"median error",labels:["baseline","+mixup","+posval","+mix&pos","+heatmap","+heat&mix"],values:[0.664,0.572,0.927,0.722,0.895,0.865]}],
  {x:0.6,y:1.75,w:8.0,h:5.0,barDir:"col",chartColors:[MINT,MINT,CORAL,CORAL,CORAL,CORAL],showValue:true,dataLabelPosition:"outEnd",
    dataLabelColor:INK,dataLabelFontSize:11,dataLabelFormatCode:"0.00",valAxisTitle:"median error (inches)",showValAxisTitle:true,
    valAxisTitleColor:MUTE,valAxisTitleFontSize:12,catAxisLabelColor:INK,catAxisLabelFontSize:12,valAxisLabelColor:MUTE,
    valGridLine:{color:"EAF0F4",size:0.5},catGridLine:{style:"none"},showLegend:false,valAxisMaxVal:1,valAxisMinVal:0});
card(s,8.85,1.75,3.85,5.0);
s.addText("Verdict",{x:9.1,y:1.95,w:3.4,h:0.4,fontFace:HEAD,fontSize:16,bold:true,color:MINT,margin:0});
s.addText([
  {text:"Mixup — WIN",options:{bold:true,color:MINT,breakLine:true}},
  {text:"blend sample pairs + their (x,y): 0.664 → 0.572, and it helps the barrier region most.",options:{breakLine:true,paraSpaceAfter:10,fontSize:12}},
  {text:"Position-disjoint validation — no",options:{bold:true,color:CORAL,breakLine:true}},
  {text:"starves the ~30 scarce training positions.",options:{breakLine:true,paraSpaceAfter:10,fontSize:12}},
  {text:"Heatmap output — no",options:{bold:true,color:CORAL,breakLine:true}},
  {text:"centroid readout biases predictions toward centre.",options:{fontSize:12}},
],{x:9.1,y:2.45,w:3.4,h:4.2,fontFace:BODY,fontSize:13,color:INK,valign:"top",margin:0});

// ============ 11. CONCLUSIONS
s=pres.addSlide(); s.background={color:NAVY};
s.addText("Part 1 — bottom line",{x:0.9,y:0.7,w:11,h:0.8,fontFace:HEAD,fontSize:28,bold:true,color:LIGHT,margin:0});
[["The CNN localizes to a sixth of a cell","≈0.15 in (3.9 mm) cross-session on empty, <¼ in with a glandular insert — regression works, and the CNN owns it."],
 ["Raw beats physics for regression","physics features are redundant for the CNN and outright break the MLP — the reverse of the classification result."],
 ["Difficulty ladder: LOSO < subpos < cell","a new scan of known spots is easy; an unseen single point is medium; an unseen whole cell is 3–4× harder than LOSO."],
 ["The glandular barrier is real & measurable","LOPO error concentrates on near-insert cells and grows with insert size — the model can't interpolate across the dielectric jump."],
 ["Mixup is the one lever that helps","teaching a smooth signal→coordinate map cuts error 14 %; validation-splitting and heatmap output hurt on this small set."],
].forEach((c,i)=>{const y=1.7+i*1.06;
  s.addShape(pres.shapes.OVAL,{x:0.9,y:y+0.05,w:0.42,h:0.42,fill:{color:MINT}});
  s.addText(String(i+1),{x:0.9,y:y+0.05,w:0.42,h:0.42,align:"center",valign:"middle",fontFace:HEAD,fontSize:15,bold:true,color:NAVY,margin:0});
  s.addText([{text:c[0]+"  —  ",options:{bold:true,color:LIGHT}},{text:c[1],options:{color:"AECBD6"}}],
    {x:1.5,y:y-0.05,w:11.2,h:0.95,fontFace:BODY,fontSize:14,valign:"middle",margin:0});});
s.addText("github.com/pmart1534/microwave-phantom-localization-cnn-mlp",{x:0.9,y:7.0,w:11.5,h:0.35,fontFace:BODY,fontSize:11,color:TEAL,margin:0});

pres.writeFile({fileName:"Deck1_Measured_Regression.pptx"}).then(f=>console.log("wrote "+f));
