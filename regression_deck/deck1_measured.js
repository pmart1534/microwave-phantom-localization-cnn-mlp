// DECK 1 - Measured phantom (x,y) regression. UofU warm-red theme.
//   ->  Deck1_Measured_Regression.pptx
const pptxgen = require("pptxgenjs");
// ---- warm University-of-Utah palette ----
const CRIMSON="BE0000", CRIMSONDK="8E1010", DARK="2E1214", GOLD="C8890B",
      ROSE="E0A99E", REDMID="C0564A", INK="2A1618", MUTE="836A68",
      LIGHT="FFFFFF", CARD="FBF4F2", LINE="E7D6D1", CREAM="EAD3CB", GRAYW="C9B3AE",
      CREAMBG="FDF8F6";
const HEAD="Cambria", BODY="Calibri";
const shadow=()=>({type:"outer",color:"7A5C5E",blur:7,offset:3,angle:90,opacity:0.18});
const pres=new pptxgen();
pres.defineLayout({name:"W",width:13.33,height:7.5}); pres.layout="W";
pres.author="Peter Martin"; pres.title="Measured Regression";
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
    s.addText(st[0],{x:1.65,y:y+0.16,w:2.5,h:0.8,fontFace:HEAD,fontSize:17,bold:true,color:accent,valign:"middle",margin:0});
    s.addText(st[1],{x:4.25,y:y+0.06,w:W-5.05,h:1.0,fontFace:BODY,fontSize:12.7,color:INK,valign:"middle",margin:0});});}
function triPanel(s,items,takeaway,iy){
  iy=iy||1.92; const iw=3.5,ih=3.62,gap=0.35,tot=3*iw+2*gap,sx=(W-tot)/2;
  items.forEach((e,i)=>{const x=sx+i*(iw+gap);
    card(s,x-0.12,iy-0.14,iw+0.24,ih+0.7);
    s.addImage({path:e[0],x,y:iy,w:iw,h:ih});
    s.addText([{text:e[1]+"   ",options:{bold:true,color:INK}},{text:e[2],options:{color:CRIMSON,bold:true}}],
      {x:x-0.12,y:iy+ih+0.02,w:iw+0.24,h:0.38,align:"center",fontFace:BODY,fontSize:13,margin:0});});
  s.addText(takeaway,{x:0.6,y:6.72,w:W-1.2,h:0.5,fontFace:BODY,fontSize:13.5,italic:true,color:MUTE,align:"center",margin:0});}
function barChart(s,series,opts){
  s.addChart(pres.charts.BAR,series,Object.assign({barDir:"col",showValue:true,dataLabelPosition:"outEnd",
    dataLabelColor:INK,dataLabelFontSize:10,dataLabelFormatCode:"0.00",valAxisTitle:"median error (inches)",
    showValAxisTitle:true,valAxisTitleColor:MUTE,valAxisTitleFontSize:12,catAxisLabelColor:INK,catAxisLabelFontSize:13,
    valAxisLabelColor:MUTE,valGridLine:{color:"F0E4E0",size:0.5},catGridLine:{style:"none"},
    legendColor:INK,legendFontSize:11,valAxisMinVal:0},opts));}
function statcard(s,x,y,w,big,small,col){card(s,x,y,w,1.55);
  s.addText(big,{x,y:y+0.18,w,h:0.7,align:"center",fontFace:HEAD,fontSize:30,bold:true,color:col||CRIMSON,margin:0});
  s.addText(small,{x:x+0.1,y:y+0.95,w:w-0.2,h:0.5,align:"center",fontFace:BODY,fontSize:12.5,color:MUTE,margin:0});}
function dot(s,cx,cy,r,fill,ln){s.addShape(pres.shapes.OVAL,{x:cx-r,y:cy-r,w:2*r,h:2*r,
  fill:{color:fill},line:ln?{color:ln,width:1}:{type:"none"}});}
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
titleLight(s,"PART 1 . PHYSICAL MEASUREMENTS","(x, y) tumor localization on the A3 phantom",
  "Bench VNA S-parameters to continuous coordinate regression: CNN vs MLP, under LOSO, LOPO-cell and single-position hold-out",
  [["0.15 in","best cross-session error (empty)"],["3.9 mm","about a sixth of a grid cell"],["3 phantoms","empty, F4, F5 inserts"]]);

// ============ 2. MEASUREMENT SETUP
s=pres.addSlide(); s.background={color:LIGHT};
title(s,"Measurement setup","4-port VNA, A3 breast phantom in canola oil, Sam Medium antennas");
numberedCards(s,[
  ["Phantom & medium","A3 breast phantom submerged in canola oil (breast-tissue-like permittivity). A metal fishing-weight tumor is moved to each grid position."],
  ["RF acquisition","4 antennas into a 4-port VNA. Full 4x4 S-matrix (16 S-parameters), magnitude and phase, swept 0.1 to 8 GHz (791 points)."],
  ["Sampling grid","6x6 array of cells, pitch about 25.4 x 23.85 mm. Each cell has 4 sub-positions at its corners (about 9.5 mm in). Roughly 51 sub-positions on the empty phantom."],
  ["Repeats & sessions","16 takes per position; 3 to 4 sessions per phantom (re-set between sessions, so real drift). Three variants: empty, F4 (small insert), F5 (large insert)."],
],CRIMSON);

// ============ 2b. SETUP IN PICTURES (3 phantoms)
s=pres.addSlide(); s.background={color:LIGHT};
title(s,"The three phantoms, in pictures","6x6 measurement grid over the oil-filled A3 phantom; red mounts hold the 4 antennas");
[["setup_photos/A3.jpg","Empty (A3)"],["setup_photos/A3F4.jpg","F4 insert"],["setup_photos/A3F5.jpg","F5 insert"]].forEach((e,i)=>{
  const x=0.82+i*4.0; imgCaption(s,x,1.75,3.7,4.4,e[0],e[1]);});

// ============ 3. ALGORITHM & TRAINING
s=pres.addSlide(); s.background={color:LIGHT};
title(s,"From “which cell” to “exact (x, y)”","Same CNN and MLP as the classifier, with the head swapped for coordinate regression");
numberedCards(s,[
  ["Targets","Grid label RnCmPp to a true (x,y) in inches (corner offsets of 0.375 in; photo-digitized where an insert blocked a corner). Never snapped to a grid point."],
  ["Models","CNN: conv trunk (32 to 32) then fc(2) + regression. MLP: 3-seed ensemble. Input = raw 16 S-params as a 32 x freq image; per-session z-score; v2 preprocessing."],
  ["Metric","Euclidean error in inches (x25.4 = mm). Median error plus percent within the 0.5 in half-cell."],
  ["Protocols","LOSO holds out a whole session. LOPO-cell holds out a whole 1 in cell. LOPO single-position holds out one sub-position (its cell-mates stay in training)."],
],CRIMSON);

// ============ 4. PROTOCOL EXPLAINER (new)
s=pres.addSlide(); s.background={color:LIGHT};
title(s,"Three ways to test the model","Each hold-out asks a harder question about generalization");
const px0=[0.7,5.05,9.4], cw=3.55, cy=1.75, ch=4.95;
const protos=[
  {t:"LOSO",sub:"leave one session out",hold:"a whole recording session",q:"Can it read a NEW scan of positions it already knows?",diff:"Easiest",dc:GOLD},
  {t:"LOPO single-position",sub:"leave one sub-position out",hold:"one point (its 3 cell-mates ~0.75 in away stay in)",q:"Can it reach an unseen point that has close neighbors?",diff:"Medium",dc:REDMID},
  {t:"LOPO-cell",sub:"leave one whole cell out",hold:"all 4 points of a 1 in cell",q:"Can it bridge a full inch to a spot with NO nearby signature?",diff:"Hardest",dc:CRIMSONDK},
];
protos.forEach((p,i)=>{const x=px0[i]; card(s,x,cy,cw,ch);
  s.addText(p.t,{x:x+0.2,y:cy+0.22,w:cw-0.4,h:0.5,fontFace:HEAD,fontSize:19,bold:true,color:CRIMSON,margin:0});
  s.addText(p.sub,{x:x+0.2,y:cy+0.72,w:cw-0.4,h:0.32,fontFace:BODY,fontSize:12.5,italic:true,color:MUTE,margin:0});
  // schematic band
  const gy=cy+1.35, gx=x+cw/2;
  if(i===0){ // LOSO: 3 session bars, last = test
    ["S1 train","S2 train","S3 test"].forEach((lbl,k)=>{const by=cy+1.15+k*0.5;
      const on=k===2; s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x:x+0.55,y:by,w:cw-1.1,h:0.4,rectRadius:0.04,
        fill:{color:on?CRIMSON:CARD},line:{color:on?CRIMSON:LINE,width:1}});
      s.addText(lbl,{x:x+0.55,y:by,w:cw-1.1,h:0.4,align:"center",valign:"middle",fontFace:BODY,fontSize:11,
        bold:on,color:on?LIGHT:MUTE,margin:0});});
  } else if(i===2){ // cell: 4x4 dots, one 2x2 cell crimson
    const r=0.075, sp=0.42, x00=gx-1.5*sp, y00=cy+1.35;
    for(let a=0;a<4;a++)for(let b=0;b<4;b++){const held=(a<2&&b<2);
      dot(s,x00+b*sp,y00+a*sp,r,held?CRIMSON:CARD,held?CRIMSON:MUTE);}
    s.addText("one cell held out",{x:x+0.2,y:y00+4*sp-0.15,w:cw-0.4,h:0.3,align:"center",fontFace:BODY,fontSize:10.5,color:MUTE,margin:0});
  } else { // subpos: one 2x2 cell, one dot crimson
    const r=0.11, sp=0.62, x00=gx-0.5*sp, y00=cy+1.55;
    for(let a=0;a<2;a++)for(let b=0;b<2;b++){const held=(a===0&&b===0);
      dot(s,x00+b*sp,y00+a*sp,r,held?CRIMSON:CARD,held?CRIMSON:MUTE);}
    s.addText("one point held out,\ncell-mates stay",{x:x+0.2,y:y00+2*sp-0.05,w:cw-0.4,h:0.5,align:"center",fontFace:BODY,fontSize:10.5,color:MUTE,margin:0});
  }
  s.addText([{text:"Held out:  ",options:{bold:true,color:INK}},{text:p.hold,options:{color:INK}}],
    {x:x+0.2,y:cy+3.15,w:cw-0.4,h:0.6,fontFace:BODY,fontSize:11.5,valign:"top",margin:0});
  s.addText([{text:"Question:  ",options:{bold:true,color:INK}},{text:p.q,options:{color:INK}}],
    {x:x+0.2,y:cy+3.75,w:cw-0.4,h:0.75,fontFace:BODY,fontSize:11.5,valign:"top",margin:0});
  s.addShape(pres.shapes.ROUNDED_RECTANGLE,{x:x+0.2,y:cy+ch-0.5,w:1.5,h:0.34,rectRadius:0.17,fill:{color:p.dc},line:{type:"none"}});
  s.addText(p.diff,{x:x+0.2,y:cy+ch-0.5,w:1.5,h:0.34,align:"center",valign:"middle",fontFace:BODY,fontSize:11,bold:true,color:LIGHT,margin:0});
});

// ============ 5. LOSO RESULTS (bar)
s=pres.addSlide(); s.background={color:LIGHT};
title(s,"New scan of a known grid (LOSO)","Median localization error by model, across the three phantoms");
barChart(s,[
  {name:"CNN (raw)",labels:["Empty","F4 insert","F5 insert"],values:[0.154,0.164,0.223]},
  {name:"MLP (raw)",labels:["Empty","F4 insert","F5 insert"],values:[0.481,0.695,0.759]},
  {name:"predict-centre (chance)",labels:["Empty","F4 insert","F5 insert"],values:[1.34,1.73,1.30]},
],{x:0.6,y:1.7,w:7.5,h:5.1,chartColors:[CRIMSON,GOLD,GRAYW],showLegend:true,legendPos:"t",valAxisMaxVal:2});
card(s,8.5,1.7,4.2,5.1);
s.addText("Summary",{x:8.75,y:1.9,w:3.7,h:0.4,fontFace:HEAD,fontSize:16,bold:true,color:CRIMSON,margin:0});
bullets(s,8.75,2.4,3.7,4.2,[
  "The CNN achieves the lowest error: 0.15 in (3.9 mm) on empty, under a quarter inch on F5.",
  "Raw and physics inputs are equivalent for the CNN, so raw is preferred (simpler, faster).",
  "The MLP error is 3 to 4x higher; with physics features it degrades to the predict-centre baseline.",
  "At least 90 percent of positions fall within the half-cell on all three phantoms.",
]);

// ============ 6. LOSO EXAMPLES (spatial)
s=pres.addSlide(); s.background={color:LIGHT};
title(s,"Predicted vs. actual, LOSO (CNN)","Crimson diamonds = prediction, open circles = true position, arrow = error");
triPanel(s,[["pred_vs_actual_loso_empty.png","Empty","0.15 in"],["pred_vs_actual_loso_f4.png","F4 insert","0.16 in"],["pred_vs_actual_loso_f5.png","F5 insert","0.22 in"]],
  "Across the empty, F4 and F5 phantoms the CNN localizes to within a fifth of a cell; a new measurement session does not degrade performance.");

// ============ 7. SINGLE-POSITION RESULTS (bar)
s=pres.addSlide(); s.background={color:LIGHT};
title(s,"Interpolating to an unseen position (single-position LOPO, CNN)","Hold out one sub-position; its three cell-mates remain in training");
barChart(s,[{name:"single-position median error",labels:["Empty","F4 insert","F5 insert"],values:[0.392,null,0.546]}],
  {x:0.6,y:1.7,w:7.7,h:5.1,chartColors:[CRIMSON],dataLabelFontSize:12,showLegend:false,valAxisMaxVal:0.7});
card(s,8.6,1.7,4.1,5.1);
s.addText("Reading it",{x:8.85,y:1.9,w:3.6,h:0.4,fontFace:HEAD,fontSize:16,bold:true,color:CRIMSON,margin:0});
bullets(s,8.85,2.4,3.6,4.2,[
  "Empty 0.39 in (9.9 mm), F5 0.55 in (13.9 mm).",
  "F4 result is being computed and will be added.",
  "Both are below the matching whole-cell values, since the three cell-mates provide close anchors.",
  "Both remain above the roughly 6 mm signal floor, indicating the CNN is data-limited at about 50 distinct positions.",
]);

// ============ 8. SINGLE-POSITION EXAMPLES (spatial)
s=pres.addSlide(); s.background={color:LIGHT};
title(s,"Predicted vs. actual, single-position (CNN, pooled)","Hold out one sub-position; its three cell-mates remain in training");
triPanel(s,[["pred_vs_actual_subpos_empty.png","Empty","0.39 in"],["pred_vs_actual_subpos_f4.png","F4 insert","pending"],["pred_vs_actual_subpos_f5.png","F5 insert","0.55 in"]],
  "With close cell-mates retained in training, single-position error is lower than the whole-cell hold-out (empty 0.39 vs 0.47 in, F5 0.55 vs 0.67 in).");

// ============ 9. LOPO-CELL RESULTS (bar)
s=pres.addSlide(); s.background={color:LIGHT};
title(s,"Interpolating to an unseen cell (LOPO-cell, CNN)","Hold a whole 1 in cell out of training, then predict a location with no nearby signature");
barChart(s,[
  {name:"pooled (train on all other sessions + positions)",labels:["Empty","F4 insert","F5 insert"],values:[0.473,0.487,0.667]},
  {name:"in-session (train + test within one session)",labels:["Empty","F4 insert","F5 insert"],values:[0.661,0.609,0.753]},
],{x:0.6,y:1.7,w:7.5,h:5.1,chartColors:[CRIMSON,ROSE],dataLabelFontSize:11,showLegend:true,legendPos:"t",valAxisMaxVal:1});
card(s,8.5,1.7,4.2,5.1);
s.addText("Findings",{x:8.75,y:1.9,w:3.7,h:0.4,fontFace:HEAD,fontSize:16,bold:true,color:CRIMSON,margin:0});
bullets(s,8.75,2.4,3.7,4.2,[
  "Model = CNN (raw, all 4 antennas), same as LOSO.",
  "Pooled = the held-out cell is removed from every session, training on all remaining data. In-session = training and testing within one session (drift removed).",
  "Interpolation is 3 to 4x harder than a new session (0.47 to 0.67 vs 0.15 to 0.22 in).",
  "Pooled outperforms in-session on all three phantoms: for interpolation, additional data outweighs drift removal.",
]);

// ============ 10. LOPO-CELL EXAMPLES (spatial)
s=pres.addSlide(); s.background={color:LIGHT};
title(s,"Predicted vs. actual, LOPO-cell (CNN, pooled)","Predicting locations never sampled; the dashed outline is the glandular insert");
triPanel(s,[["pred_vs_actual_lopo_empty.png","Empty","0.47 in"],["pred_vs_actual_lopo_f4.png","F4 insert","0.49 in"],["pred_vs_actual_lopo_f5.png","F5 insert","0.67 in"]],
  "Interpolation error increases with insert size (0.47, 0.49, 0.67 in) and predictions pull inward, concentrating over the glandular insert the CNN never sampled.");

// ============ 11. PROTOCOL COMPARISON
s=pres.addSlide(); s.background={color:LIGHT};
title(s,"All three protocols side by side","Difficulty of each generalization task (raw CNN median error, inches)");
barChart(s,[
  {name:"LOSO (new session)",labels:["Empty","F4","F5"],values:[0.154,0.164,0.223]},
  {name:"single-position (1 point)",labels:["Empty","F4","F5"],values:[0.392,null,0.546]},
  {name:"LOPO-cell (whole cell)",labels:["Empty","F4","F5"],values:[0.473,0.487,0.667]},
],{x:0.6,y:1.7,w:7.7,h:5.1,chartColors:[GOLD,REDMID,CRIMSONDK],dataLabelFontSize:10,showLegend:true,legendPos:"t",valAxisMaxVal:0.8});
card(s,8.6,1.7,4.1,5.1);
s.addText("The ladder of difficulty",{x:8.85,y:1.9,w:3.6,h:0.4,fontFace:HEAD,fontSize:15,bold:true,color:CRIMSON,margin:0});
bullets(s,8.85,2.4,3.6,4.2,[
  "LOSO (0.15 to 0.22 in): a new scan of KNOWN positions. Easiest.",
  "Single-position (0.39 to 0.55): unseen point, close anchors. Medium.",
  "LOPO-cell (0.47 to 0.67): unseen 1 in cell, no anchor. Hardest.",
  "Larger inserts increase error at every protocol, and the gap widens as the task becomes harder.",
]);

// ============ 12. IMPROVING INTERPOLATION (clarified)
s=pres.addSlide(); s.background={color:LIGHT};
title(s,"Improving interpolation on the hardest case","Three techniques evaluated on F5 LOPO-cell (baseline 0.664 in); only one reduces error");
barChart(s,[{name:"median error",labels:["baseline","+mixup","+posval","+mix&pos","+heatmap","+heat&mix"],values:[0.664,0.572,0.927,0.722,0.895,0.865]}],
  {x:0.6,y:1.75,w:8.0,h:5.0,chartColors:[GRAYW,CRIMSON,GRAYW,GRAYW,GRAYW,GRAYW],dataLabelFontSize:11,showLegend:false,valAxisMaxVal:1});
card(s,8.85,1.75,3.85,5.0);
s.addText("What this shows",{x:9.1,y:1.95,w:3.4,h:0.4,fontFace:HEAD,fontSize:16,bold:true,color:CRIMSON,margin:0});
s.addText([
  {text:"Lower is better. Grey bars increased error relative to the baseline; the crimson bar is the only reduction.",options:{breakLine:true,paraSpaceAfter:10,fontSize:12}},
  {text:"Mixup: effective",options:{bold:true,color:CRIMSON,breakLine:true}},
  {text:"blending sample pairs and their (x,y) targets reduces error 0.664 to 0.572, with the largest gain in the insert region.",options:{breakLine:true,paraSpaceAfter:9,fontSize:12}},
  {text:"Position-split validation and heatmap output: not effective",options:{bold:true,color:MUTE,breakLine:true}},
  {text:"the former reduces the ~30 available training positions; the latter biases predictions toward the grid centre.",options:{fontSize:12}},
],{x:9.1,y:2.45,w:3.4,h:4.3,fontFace:BODY,fontSize:13,color:INK,valign:"top",margin:0});

// ============ 13. CONCLUSIONS (light)
s=pres.addSlide();
closingLight(s,"Part 1, summary",[
 ["The CNN localizes to a sixth of a cell","about 0.15 in (3.9 mm) cross-session on empty, under a quarter inch with a glandular insert. Continuous regression is feasible, and the CNN is the stronger model."],
 ["Raw input outperforms physics features","physics features are redundant for the CNN and degrade the MLP, the reverse of the classification result."],
 ["Difficulty ordering: LOSO < single-position < cell","a new scan of known positions is the easiest task; an unseen single position is intermediate; an unseen whole cell is 3 to 4x harder than LOSO."],
 ["The glandular insert is measurable in the errors","under LOPO, predictions pull inward and concentrate over the traced insert, which the CNN never sampled."],
 ["Mixup is the only effective augmentation","learning a continuous signal-to-coordinate map reduces error 14 percent; validation-splitting and heatmap output increase error on this small dataset."],
]);

pres.writeFile({fileName:"Deck1_Measured_Regression.pptx"}).then(f=>console.log("wrote "+f));
