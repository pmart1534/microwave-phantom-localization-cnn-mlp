// DECK 4 - Bandwidth & hardware reduction: RESULTS ONLY (no conclusions/summaries).
// UofU warm-red theme, light title.  ->  Deck4_Reduction_Results.pptx
const pptxgen = require("pptxgenjs");
const CRIMSON="BE0000", GOLD="C8890B", INK="2A1618", MUTE="836A68", LIGHT="FFFFFF",
      LINE="E7D6D1", CREAMBG="FDF8F6";
const HEAD="Cambria", BODY="Calibri";
const pres=new pptxgen();
pres.defineLayout({name:"W",width:13.33,height:7.5}); pres.layout="W";
pres.author="Peter Martin"; pres.title="Bandwidth & Hardware Reduction - Results";
const W=13.33,H=7.5;

function titleLight(s,part,ttl,sub,stats){s.background={color:CREAMBG};
  s.addShape(pres.shapes.RECTANGLE,{x:0,y:0,w:W,h:0.26,fill:{color:CRIMSON},line:{type:"none"}});
  s.addShape(pres.shapes.RECTANGLE,{x:0.9,y:2.02,w:0.09,h:1.5,fill:{color:CRIMSON},line:{type:"none"}});
  s.addText(part,{x:1.2,y:2.02,w:11,h:0.45,fontFace:BODY,fontSize:15,color:CRIMSON,bold:true,charSpacing:3,margin:0});
  s.addText(ttl,{x:1.2,y:2.5,w:11.4,h:1.0,fontFace:HEAD,fontSize:33,bold:true,color:INK,margin:0});
  s.addText(sub,{x:1.2,y:3.72,w:11.2,h:0.7,fontFace:BODY,fontSize:15,color:MUTE,margin:0});
  stats.forEach((c,i)=>{const x=1.2+i*3.95;
    s.addText(c[0],{x,y:4.95,w:3.85,h:0.6,fontFace:HEAD,fontSize:20,bold:true,color:CRIMSON,margin:0});
    s.addText(c[1],{x,y:5.5,w:3.9,h:0.7,fontFace:BODY,fontSize:12.5,color:MUTE,margin:0});});}

// image slide: crimson title bar + factual sub + centered image fit to the area below
function imgSlide(ttl,sub,path,aspect){         // aspect = width/height of the PNG
  const s=pres.addSlide(); s.background={color:LIGHT};
  s.addShape(pres.shapes.RECTANGLE,{x:0,y:0,w:W,h:0.12,fill:{color:CRIMSON},line:{type:"none"}});
  s.addText(ttl,{x:0.55,y:0.32,w:W-1.1,h:0.6,fontFace:HEAD,fontSize:24,bold:true,color:INK,margin:0});
  if(sub)s.addText(sub,{x:0.55,y:0.95,w:W-1.1,h:0.4,fontFace:BODY,fontSize:13,color:CRIMSON,bold:true,margin:0});
  const areaY=1.5, areaH=5.75, maxW=12.5, maxH=areaH;
  let w=maxW, h=maxW/aspect;
  if(h>maxH){ h=maxH; w=maxH*aspect; }
  const x=(W-w)/2, y=areaY+(areaH-h)/2;
  s.addImage({path,x,y,w,h});
  return s;
}

// ---- 1. TITLE (results only) ----
let s=pres.addSlide();
titleLight(s,"RESULTS","Bandwidth & hardware reduction for the tumor localizer",
  "Median (x,y) localization error as the RF band is narrowed and antennas / features are removed",
  [["Measured","A3 phantom, session-LOSO CNN"],
   ["Simulated","HFSS metal, 8-fold CNN"],
   ["Metric","median lateral (x,y) error, mm"]]);

// ---- figure slides (factual titles only) ----
imgSlide("Localization error vs bandwidth used",
  "k-NN signal floor; per configuration, best center at each width",
  "bw_knee.png", 11.6/8.2);

imgSlide("Localization error vs number of discrete tones",
  "Greedy-selected frequency tones; per configuration",
  "bw_tones.png", 8.6/5.4);

imgSlide("Error by 0.25 GHz window center, and by bandwidth at the best center",
  "Measured (empty/F4/F5) and simulated; 0.25 GHz windows across the band (left), bandwidth knee (right)",
  "narrowband_combined.png", 13.0/5.4);

imgSlide("Simulated CNN error: band x cross-validation protocol",
  "Full 2-8 GHz vs 2-4 GHz; random 8-fold vs strict (x,y)-disjoint 8-fold",
  "sim_band_protocol.png", 8.8/5.6);

imgSlide("Hardware reduction x band narrowing",
  "Median lateral (x,y) error, mm; each panel at its own best center; black box = >20 mm",
  "reduction_grid.png", 16.0/10.5);

imgSlide("Simulated CNN: lateral (x,y) vs depth (z) error",
  "Same reduction grid; simulated only (measured is single-depth)",
  "sim_depth_grid.png", 13.0/4.8);

pres.writeFile({fileName:"Deck4_Reduction_Results.pptx"}).then(f=>console.log("wrote "+f));
