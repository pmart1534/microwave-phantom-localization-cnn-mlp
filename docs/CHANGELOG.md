# Changelog

Running log of what changed, when, and why. Newest first. Each substantive
change to code, method, or results should land as its own commit with a matching
entry here.

## 2026-08-21 - F5 promotions: band collapse is REAL, not under-training

- f5aug-p100 @100ep: headline 98.10 (F5 ~ F4 at full band); all16@2-5 54.29,
  refl4@2-5 31.43, pair13@2-5 41.90 - essentially identical to the 20ep values.
  The 44-pt band-cut penalty is physical: Aug-F5's position information lives
  substantially outside 2-5 GHz, unlike July's F5 (93 at 2-4).
- Band-location probe launched (0.1-2, 5-8, 1-5, 0.1-5).


## 2026-08-21 - A3F5 parity suite (@20ep) + audit-driven promotions

- A3F5 Aug21 (sessions 1317/1341/1409, 35-way; aborted 1307 excluded).
- @20ep: headline 96.19; all16@2-5 56.19; refl4@2-5 30.48; pair13@2-5 44.76;
  ablation nobase 96.2 / nomean 90.5 / zsoff 97.1 / zsglobal 95.2 /
  ALL-OFF 75.2; mag-only 88.6.
- Convergence audit flagged MOST of the suite (F5 trains slower than any other
  dataset) - headline + 3 band cells promoted to 100ep (f5aug-p100 labels)
  before comparison with F4. 20ep band numbers are floors, not finals.


## 2026-08-21 - Wider bands, original-paper pipeline, feature reduction (ideal + swap, @20ep)

- Bands (ideal/swap): 1-3: 99.3/82.1 | 2-4: 99.3/96.4 | 3-5: 98.6/96.9.
  Windows touching sub-2 GHz are swap-fragile; 2-4 and 3-5 robust.
- ORIGINAL-PAPER pipeline (baseline sub + mag/phase + input-layer zscore, no
  session stats): ideal 100.0 (linear) / 100.0 (dB); swap 92.4 / 92.9.
  dB-vs-linear magnitude: no difference. Original data manipulation fully
  sufficient on clean data; costs ~5-7 pts under unit swap vs per-session z.
  CNN_LOSO_MAGDB switch added.
- Feature reduction (ideal/swap): pair13 98.0/93.4 (full), 98.6/90.8 (2-5);
  refl-pair13 95.9/77.6, 95.9/76.5; single-S11 84.4/50.5, 72.1/52.0.
  Hardware reduction is the axis swap punishes hardest (single antenna ~ coin flip).


## 2026-08-21 - Band windows + only-one-preprocessing (ideal + swap, @20ep)

- Bands (ideal/swap): 1-5: 99.3/97.5 | 2-4.5: 99.3/96.9 | 1-2: 76.9/36.2 |
  2-3: 98.6/76.5 | 3-4: 98.0/95.4 | 4-5: 91.2/92.9. Swap's robust 1-GHz
  window is 3-4 (95.4), NOT 2-3 (76.5) - band placement interacts with
  perturbation robustness.
- ONLY-ONE-step (keep exactly one mechanism; ideal/swap):
  only-baseline 99.3/95.9 | only-meansub 100.0/96.9 | only-zscore 98.6/99.5 |
  only-innorm 99.3/19.9. Baseline alone IS sufficient (single-measurement
  deployment viable); the input-layer norm alone fails on swap because its
  constants are train-derived, not session-local - normalization must be
  computed from the deployment session.


## 2026-08-21 - Cheap-device factorial complete (component x hardware x band, @20ep)

- 3 datasets (metal-e20 / swap4e20 / oil3e20) x {both,mag,phase} x {all16,refl4}
  x {full, 2-5 GHz}; 32 new cells + reuse. Note: one earlier progress peek
  misattributed swap mag/all16/2-5 as 100.0 - JSON value is 99.0.
- KEY PATTERNS: (1) magnitude NEEDS transmission - mag+refl-only collapses
  (metal 78.2, swap 86.7, oil 91.8) while phase+refl-only holds (98.6/86.7/96.6);
  (2) best cheap config = MAG-ONLY + ALL-16 + 2-5 GHz: 98.0/99.0/96.6 - drop
  the vector receiver and half the band, keep the transmission paths;
  (3) full-cheap (mag+refl+2-5) pays 10-15 pts: 87.8/83.7/89.1;
  (4) phase-only degrades most on swap (77.6 refl 2-5) - fingerprints in phase
  reconfirmed from the third direction.
- 18 convergence-audit flags across the grid (mostly low cells) - promote
  before quoting any individual low cell.


## 2026-08-21 - Mag-only swap transfer 98.47 (mechanism confirmed) + first LOPO regression

- MAG-ONLY pristine-day2 -> swapped units (@20ep): 98.47 +/- 3.06 vs 93.37 for
  mag+phase - dropping phase recovers +5.1 pts of transfer; 3 of 4 swap
  sessions at 100, full-reversal session 83.7 -> 93.9. Unit fingerprints are
  PHASE-borne; a magnitude-only front end is unit-agnostic without needing
  swap examples in training.
- LOPO REGRESSION (Imager_CNN_LOPO.m, metal day-1, 49 holds, @20ep, stats
  exclude held-out position): per-hold vote error mean 0.758 in / median
  0.739 in (chance ~1.74; grid pitch 0.25-0.75). Edge positions worst
  (extrapolation: up to 1.8 in); interior best (down to 0.09 in). The honest
  "localize a position never sampled" number.


## 2026-08-21 - Overnight: oil-change + A3F4 LOSO, swap reduced configs, ablations, mag-only

- OIL-CHANGE LOSO (1120/1154/1225, canola replaced per session, @100ep):
  97.96 +/- 0.00 - first environmental perturbation with a consistent small
  cost (~1.4 pts vs metal 99.32; every fold 98.0). Partial OilSwap01 excluded;
  OilChange03's two stray positions dropped by intersection.
- A3F4 LOSO (1655/1804/1820, 37-way, @100ep): 98.20 +/- 3.12.
- Reduced trio @2-5 GHz (20ep): swap4 97.45 / 88.78 (refl) / 90.82 (pair) -
  swap + hardware reduction compounds; oil3 97.3/96.6/96.6 (free);
  f4aug 86.5/81.1/87.4 (band cut costs ~12 pts on this F4 set, unlike July F4).
- Preprocessing ablation (20ep): oil3 singles all 97.3-98.0, ALL-OFF 83.7;
  f4aug singles 93.7-97.3, ALL-OFF 82.0. Drift ladder for raw input now:
  ideal 99.3 -> reattach 94.9 -> oil 83.7 / f4 82.0 -> swap 17.9.
- MAG-ONLY full band (20ep): swap4 100.00 (BEATS mag+phase 97.96 - phase
  carries the unit fingerprints), oil3 97.96, f4aug 97.30.
- Convergence audit: flagged runs are mostly low-loss fine-tuning; the two
  worth promoting to 100ep are swap refl/pair @2-5 (folds still at 0.4-0.7 loss).


## 2026-08-20 - Swap-set ablation (20-epoch fast regime): preprocessing IS load-bearing under structural mismatch

- swap4e20 ablation (9 variants incl. same-epoch reference, 20 epochs + curves):
  reference 97.96; no-baseline 99.49; no-meansub 97.45; nobase+nomean 99.49;
  zscore off/row 97.96; zscore-global 95.41; inputnorm-none 97.45;
  **ALL-OFF 17.86 +/- 10.85 - collapse.**
- Completes the drift-severity ladder for raw (no preprocessing) input:
  ideal 99.3 -> reattach 94.9 -> swap 17.9. Any single normalization mechanism
  restores 95-99.5 everywhere; with none, structural unit-location mismatch
  breaks the CNN entirely. The "redundant safety nets" have a real cliff.
- Epoch parity certified: single-S11 metal @20 = 84.35 +/- 13.1 (exactly the
  100-epoch mean); convergence audit flagged only that run's folds 1-2 as
  still-improving on loss (accuracy already at parity). 20-epoch + curves is
  now the standard exploration regime.


## 2026-08-20 - First position-disjoint test (Imager_CNN_ValPos.m): corners -> unseen cell centers

- Train: all 2352 corner samples (day-1 metal, 3 sessions, 49 classes/targets).
  Test: 384 P9 cell-center samples from the sessions' validation/ folders -
  positions never seen as class or target. Per-session stats from corners only.
- CLASSIFICATION -> nearest corner: mean err 1.08 in (median 0.73), own-cell
  corner hit only 23.7% (ideal snap = 0.530 in; chance = 1.74 in).
- REGRESSION (same body, fc(2) xy head): mean err 0.539 in = almost exactly
  the corner-to-center distance; predictions are per-cell consistent but
  displaced ~0.5 in toward the trained-position manifold (see scatter).
- Reading: both heads beat chance clearly but neither truly interpolates to
  unseen positions on this 0.75-in-pitch grid; the regression error sits AT the
  geometric floor of the training grid. This is the honest LOPO-flavored
  baseline the Joel-Harley revision plan starts from.


## 2026-08-20 - Antenna-swap 4-way LOSO: 97.96 - first visible (but small) dent

- Swap set (Aug20, A3_MetalTumor_SwapAntLocation/: 4 sessions, each a
  different unit->port arrangement; every held-out arrangement's unit-port
  pairings unseen in training): LOSO 97.96 +/- 1.67 (folds 98.0/100.0/95.9/98.0).
- First perturbation to score below 99 at full array/band - unit fingerprints
  carry a measurable ~2 pts - but position information dominates: the model
  localizes at ~98% through completely rearranged antenna units.
- Also: train-normal->test-reattached (cnn_xday normtrain-reattachtest) 99.32
  vs 100.00 with-exposure LOSO: reattach robustness is intrinsic, not learned.


## 2026-08-20 - Z-score reconciliation complete: it was the model, not the physics

- CNN single-S11 Aug18 metal: z-on 84.35 +/- 12.30 vs z-off 82.99 +/- 10.07
  (~1.4 pts, within fold noise) - antenna count does not revive the need.
- CNN F5-last3 all16 z-off: 100.00 (= reference) - hard phantom/drift does not
  either (at full array).
- Verdict: the old A2 study needed per-session normalization because of the
  MODEL (MLP/LogReg, no internal normalization: 99.32 -> 90.48 without z on the
  same Aug18 data). The CNN's batch-norm self-normalizes; it only pays (~5 pts)
  when ALL preprocessing is removed under reattach drift.


## 2026-08-20 - Freshant preprocessing ablation complete (corrects prior commit message)

- freshant4 (reattach, 4-way), all16/full band, reference 100.00:
  no-baseline 100.0 | no-meansub 100.0 | nobase+nomean 100.0 | zscore-off 100.0
  | zscore-row 99.5 | zscore-global 100.0 | inputnorm-none 100.0 |
  ALL-OFF 94.90 +/- 2.63.
- Correction: the previous commit message said "all 8 variants 99.5-100" -
  the all-off variant is 94.90. Under reattach drift the CNN needs AT LEAST ONE
  normalization mechanism (either the subtractions or a z-score - any single
  one restores 100), but no specific one: the steps are redundant safety nets,
  and only removing all of them at once costs anything (~5 pts).


## 2026-08-20 - Preprocessing ablation (ideal 3-session metal LOSO): every step worth ~0 here

- New switches in Imager_CNN_LOSO.m: CNN_LOSO_NO_BASELINE, CNN_LOSO_ZSCORE
  (pixel|row|global|off), CNN_LOSO_INPUTNORM (zscore|none); each appends its
  own setLabel suffix.
- Day-1 metal (1143/1210/1239), all16/full band, reference 99.32:
  no-baseline 99.32; no-meansub 100.00; zscore off/row/global all 99.32;
  inputnorm-none 99.32; ALL-OFF (completely raw S into the CNN) 99.32.
- Reading: on tight same-morning sessions the between-session drift is small
  enough that the CNN needs no preprocessing at all; baseline sub and mean-sub
  are mutually redundant; mean-sub alone costs 0.68 (drop it -> 100.00).
  The pipeline earns its keep only under real drift - the follow-up ablation
  should run on freshant4 (raw reattach drift 0.014-0.017 EXCEEDS the 0.011
  position signal) where zscore-off is predicted to collapse.


## 2026-08-19 - Antenna-reattach set at reduced configs: no damage

- freshant4 (4-way) x 2-5 GHz configs: all16 99.49, refl-all4 99.49,
  pair13 98.98 - equal to or HIGHER than every 3-session dataset's reduced
  numbers (extra training fold helps more than reattach hurts). Antenna
  re-seating remains free even at reduced hardware/band.


## 2026-08-19 - Reduced-config table complete + antenna-reattach LOSO 100.00

- 2-5 GHz x 3 configs x 4 datasets complete (`*_band2-5` results): all16
  98.6-99.3; refl-all4 96.6-98.0; pair13 95.2-98.0. Band cut costs ~1-2 pts,
  hardware cuts ~1-3 more; no dataset (incl. fresh-cal) reacts worse than others.
  Bonus full-band refl/pair runs from the interrupted first sweep kept.
- ANTENNA-REATTACH 4-way LOSO (freshCal03 1258 + FreshPlaceAnt 1509/1631/1703,
  full features/band): 100.00 +/- 0.00 - every fold perfect, including the
  pre-reattach reference fold. Physically removing/re-attaching antennas does
  not break cross-session generalization at full array/band
  (`cnn_loso_Aug18_freshant4_*`).


## 2026-08-19 - Fresh-calibration metal LOSO: 100.00

- Aug19 fresh-cal metal sessions (1103/1200/1258, VNA recalibrated before each):
  LOSO 100.00 +/- 0.00, all folds and all positions perfect
  (`cnn_loso_Aug18_freshcal_*`). Per-session recalibration does not hurt -
  the per-session baseline subtraction + z-score absorbs the new calibration
  state entirely.


## 2026-08-19 - Cross-day result: train day-1 metal -> test day-2 = 100.00

- `cnn_xday_Aug18_metal-d1train-d2test_*`: trained once on the three Aug18
  day-1 metal sessions (2352 samples, 504 s), evaluated on each Aug19 day-2
  session. 100.00% position-vote AND trial-level on all three test sessions;
  zero positions below 100. Overnight drift costs nothing at full array/band
  with per-session z-score.


## 2026-08-19 - Results: next-day metal LOSO 100.0; empty null-control at chance

- Metal next-day (Aug19 0909/0938/1008): LOSO 100.00 +/- 0.00 (all folds perfect).
- Empty/Nothing (1744/1807/0802): LOSO 3.40 +/- 2.36 vs 2.0% chance - the
  null-control confirms position labels carry no exploitable drift signal when
  nothing is placed (Nothing_Test01 fold 6.1, others 2.0).
- Cross-day run (train day-1 metal, test day-2) auto-started next.


## 2026-08-19 - Aug19 data: next-day metal + empty null-control LOSO; cross-day script

- New Aug19 sessions in Separated/Aug18: 3 next-day metal (0909/0938/1008) and
  3 empty/Nothing (1744/1807/0802; 02-03 have 96 positions - the position
  intersection in the LOSO script automatically restricts to the typical 49).
- `cnn_matlab/aug19_loso.sh`: LOSO on each set separately (running).
- `cnn_matlab/Imager_CNN_XDay.m` (new, generated from Imager_CNN_LOSO.m):
  fixed train/test session-group split - trains ONCE on CNN_XDAY_TRAIN_SESSIONS,
  evaluates per CNN_XDAY_TEST_SESSIONS session; test data never enters training;
  per-session z-score stays per-session. Outputs cnn_xday_*.
- `cnn_matlab/xday_metal.sh`: train day-1 metal (1143/1210/1239) -> test day-2
  metal (0909/0938/1008); queued to auto-start after the LOSO runs finish.


## 2026-08-18 - Spatial accuracy plots restyled (green = 100%)

- `Imager_CNN_LOSO.m` spatial figure + new `replot_spatial.py` (regenerates any
  existing result's spatial PNG from its JSON, no retraining): red->yellow->
  green colormap (100% = green), markers sized from grid spacing so neighbours
  never touch, labels only on imperfect positions in white callout boxes,
  offset diagonally and flipped away from the nearest plot edge.
- Aug18 metal + beet spatial PNGs regenerated in the new style.


## 2026-08-18 - Aug18 A3 metal-tumor and beet-1cm LOSO (main CNN)

- New Aug18 data (Separated/Aug18): 3 metal-tumor + 3 beet-1cm sessions,
  49 positions x 16 trials, July03 antenna convention (no remap).
- Main CNN defaults (raw, all 16 S-params, full band, single-stage, 100 ep):
  metal 99.32 +/- 1.18, beet 99.32 +/- 1.18 (folds 100/98/100 both).
  The 1 cm beet matches metal exactly at full array + full band.
- Post repaste/BIOS: ~6.2-6.5 min per full-band fold (~3x faster than the
  15-25 min typical earlier in the study); both runs in 41 min wall.


## 2026-08-04 - Minimal-chip sweep complete: tone descent + magnitude-only; deck Part 4

- `cnn_matlab/minimal_chip_sweep.sh` finished (priority-ordered, 8 groups).
  Tone descent 4->3->2->1 freq points at each phantom's center (empty 1.875 GHz
  original slot, F4 3.0 GHz) on single-S11 and refl-pair13; magnitude-only
  (CNN_LOSO_COMPONENT=mag) ladders on the same hardware.
- Single-tone (1 CW frequency point), mag+phase: empty 66.0 (1 ant) / 91.5
  (2 ant refl); F4 60.9 / 90.4. Tone count 4->1 changes accuracy by only ~5 pts.
- Magnitude-only: near parity at 1-4 GHz (empty 98.7/99.3, F4 86.5/94.9) but
  collapses as band narrows: 1 ant crosses 50% at 0.05 GHz (empty 30.1) and
  0.25 GHz (F4 35.9) - the only sub-50 empty cell in the study; 2 ant refl
  reaches a single tone at 49.7 (empty) / 69.9 (F4).
- `analyze_minimal_chip.py` (new): `results/minimal_chip_map.png` + `.md`,
  same heatmap format as the break maps (rows = hardware x component).
- Deck: new slide 17 "Part 4 - further reduction" (17 slides total).


## 2026-08-04 - Deck rewritten to objective descriptions (user request)

- `presentation/gen_deck_band.js`: 22 rewrites removing conclusions/inferences
  from noteboxes, headings, and bullets - text now states what the data shows
  (numbers, which cells cross thresholds) without interpretive claims
  ("those are physics", "bandwidth is survivable", design principles, etc.).
  Recommendation slide keeps the spec cards but with data-only support text.
- Rebuilt Frequency_Reduction.pptx (16 slides) + PDF.


## 2026-08-04 - Component ablation (mag/phase), tone descent, empty reverted to original bands

- `Imager_CNN_LOSO.m`: new `CNN_LOSO_COMPONENT=mag|phase|both` (raw mode row
  selection; tagged rawmag/rawphase in filenames AND inputKind so canonical raw
  selections are unaffected). mag-only models a scalar power-detector chip.
- `cnn_matlab/minimal_chip_sweep.sh` (new, running): priority-ordered sweep on
  the surviving reduced-hardware configs (single-S11 + refl-pair13, empty + F4):
  tone descent 4->3->2->1 frequency points (native grid = 10 MHz spacing, so
  "2 2" = single-tone CW) and magnitude-only ladders. <50% early stop + reuse.
- `cnn_matlab/component_sweep_empty.sh` (new, superseded by the above mid-flight).
- EMPTY REVERTED to original ~1.875 GHz narrow bands everywhere (user decision):
  the full-array placement scan was saturated (99-100 above 1.45 GHz) so its
  "best 2.0 GHz" pick was noise, and at single antenna it was measurably worse
  (71/59 vs 76/75 at 0.1/0.05 GHz). Lesson: optimize placement at deployment
  hardware. `analyze_break_descent_best.py` + v2 map regenerated accordingly.
- First tone results (single-S11 empty, 2.0-center before revert): 4 pts 59.5,
  3 pts 54.3 - kept on disk as rawlegacy comparison points.


## 2026-08-04 - Break descent v2: per-phantom best-center ladders + map + deck slide

- `cnn_matlab/break_descent_best.sh` (new): adaptive descent where each phantom's
  band ladder converges on ITS OWN best frequency (empty -> 2.0 GHz, F4 -> 3.0,
  F5 -> 2.25); skip-if-exists reuse + <50% early stop (break check also fires on
  reused results).
- `analyze_break_descent_best.py` (new): `results/break_descent_best.md` +
  `results/break_descent_map_best.png` (per-panel column labels). Original v1
  map/figure kept unchanged per user request.
- Findings: F4's single-antenna break VANISHES at its own center (70.5% at 50 MHz
  vs broken at 0.5 GHz before) - it was placement, not information. F5 floors
  rise ~10-15 pts (full-array 50 MHz: 74.7 vs 59.6) and refl-pair survives 1 GHz
  (52.5), but reduced-hardware breaks remain (pair/refl-pair break at 0.5 GHz,
  single at 1 GHz). Caveat: full-array best centers shift at reduced hardware
  (empty S11 50 MHz: 58.8 at 2.0-center vs 74.5 at old 1.85-1.9).
- Deck: new slide 15 (break map v2) after the original; 16 slides total.


## 2026-08-01 - 0.1 GHz placement scan complete: each phantom has its own best frequency

- `cnn_matlab/scan_100mhz.sh` finished (27 runs; resume/skip logic added after a
  mid-scan pause for a BIOS update; one CUDA-error casualty re-run).
- Best 100 MHz slot per phantom: empty 1.95-2.05 (100.0, indifferent above 1.45),
  F4 2.95-3.05 (97.4, small target rewards higher f), F5 2.2-2.3 (78.8, large
  lossy insert forces low). F5 has a local DIP at 1.7-2.05 (62-67) - the descent's
  1.825-1.925/1.85-1.9 slots were NOT its best, so the ultra-narrow floors in the
  break verdict are conservative (true 0.1 GHz floor ~79, not 62.6).
- `make_band_importance.py`: 0.1 GHz series + per-phantom best-slot stars added
  to `results/band_importance.png`.
- Deck: new slide 11 "Each phantom has its own best frequency" (sufficiency-scan
  figure + phantom-dependence note); 15 slides total.


## 2026-08-01 - Band-placement importance plot + 0.1 GHz placement scan

- `make_band_importance.py` (new): sufficiency-scan figure `results/band_importance.png`
  - LOSO accuracy vs window center, one series per width (0.25/0.5/1/2 GHz, and
  0.1 GHz once scan_100mhz.sh lands), one panel per phantom. Shows where in the
  spectrum the position information lives.
- `cnn_matlab/scan_100mhz.sh` (new, launched): nine 100 MHz windows across
  0.95-3.55 GHz x 3 phantoms to verify the ~1.85-1.925 GHz ultra-narrow placement
  was actually optimal (it was inherited from the 0.25 GHz scan, not proven).


## 2026-08-01 - Break-descent complete: hardware x band map + deck Part 3

- Adaptive descent (`cnn_matlab/break_descent.sh`) finished: 4 reduced-hardware
  levels x up to 7 bands x 3 phantoms with per-phantom early stop below 50%.
- `analyze_break_descent.py` (new): builds `results/break_descent.md` grid +
  `results/break_descent_map.png` 3-panel heatmap (black box = broken, blank =
  skipped after break); includes the full-array row from the Part 2 study.
- Findings: Empty never breaks anywhere (floor 74.5% at S11 + 50 MHz); F4 breaks
  only at single-antenna 0.5 GHz (39.7%); F5 breaks at every reduced-hardware
  level, and its breaking point widens as hardware shrinks: 0.1 GHz (refl-all4,
  47.5) -> 0.5 GHz (pair full-S, 35.4) -> 1 GHz (refl-pair 45.5 / single 21.2).
- `presentation/gen_deck_band.js`: appended Part 3 (map figure + verdict table
  slides 13-14); Part 2 notebox now points to Part 3. Rebuilt pptx (14 slides)
  + PDF.


## 2026-07-31 - Frequency_Reduction deck: Part 2 "trying to break it" (slides 9-12)

- `presentation/gen_deck_band.js`: appended four slides - break-tier definitions
  (DEGRADED/UNSTABLE/BROKEN/DEEP), the nine-window 0.25 GHz placement scan
  (2-2.25 GHz best; below ~1.25 GHz even the empty phantom crosses the 50% line),
  the best-per-width descent curve (`assets/break_curve.png`), and the per-phantom
  break verdict table (Empty/F4 never break; F5 degraded at 0.5 GHz, unstable at
  1 GHz, never <50%; floors 99.3/90.4/59.6 at 50 MHz).
- Rebuilt `Frequency_Reduction.pptx` (12 slides) + PDF.
- Adaptive hardware x band break-descent sweep (`cnn_matlab/break_descent.sh`)
  launched in background; results will extend this deck as Part 3.


## 2026-07-31

- **Breaking-point analysis + ultra-narrow descent + 0.25 GHz placement scan.**
  New `analyze_break_points.py` (-> `results/break_analysis.md`,
  `break_curve.png`): per-phantom best-window-per-width curves with failure
  tiers (DEGRADED < 90% of full-band, UNSTABLE fold-sigma >= 10, BROKEN < 50%,
  DEEP < 25%). Conv kernels now clamp to `min(20,nFreq)` / `min(10,nFreq)`
  (original program's convention) enabling windows below 0.2 GHz. Findings with
  the full array: Empty NEVER breaks by any tier down to 0.05 GHz (99.3%); F4
  never crosses any tier (floor 90.4 +/- 7.1 at 0.05 GHz); F5 degrades at
  0.5 GHz, goes unstable at 1 GHz, but never crosses 50% (floor 59.6 +/- 17.8
  at 0.05 GHz). Placement scan across nine 0.25 GHz windows: best slot is
  phantom-dependent (F5: 2-2.25 at 83.8 +/- 3.5, beating 1.75-2's 80.8 +/- 12.6;
  F4: 3.5-3.75 at 98.1). With 16 S-parameters the model cannot be pushed below
  50% by bandwidth alone.

## 2026-07-29

- **Sub-4 GHz "break it" descent (Phases 1-2, CNN, raw, all 16 S-params).**
  Ceiling: 0.1-4 GHz AND 1-4 GHz both hit F5 = 100% (the no-above-4-GHz chip
  constraint is free; 1-4 even beats same-width 1.5-4.5). Best-per-width on F5:
  3 GHz 100 -> 2 GHz 92.9 -> 1 GHz 92.9 (1.5-2.5) -> 0.5 GHz 88.9 (1.5-2) ->
  0.25 GHz 80.8 (1.75-2). Mean degrades gracefully but fold-to-fold sigma
  EXPLODES below 1 GHz width (F5 +/-12-20 vs +/-0-5 at 3 GHz): narrow bands
  become session-unstable before they become inaccurate. Empty stays 99.4
  everywhere, F4 88-99.

## 2026-07-17

- **Frequency-reduction deck.** `presentation/Frequency_Reduction.pptx` (8
  slides, same cream/serif theme as the classification decks): motivation,
  band-placement table, bandwidth-expansion table, combined figure, chip
  operating points @ 1-5 GHz, single-antenna robustness check, recommendation
  (spec 1-5 GHz, fallback 1.5-4.5, avoid >5 and <1 alone, antennas<->bandwidth
  trade). Generator `gen_deck_band.js`.


- **Stage C (chip operating point) + single-antenna band sweep.**
  At the winning 1-5 GHz band: refl-all 100/97.4/94.9, pair full-S
  99.3/92.9/92.9, pair refl-only 99.3/92.9/84.8, single S11 96.1/96.2/69.7
  (empty/F4/F5). Reductions COMPOUND on F5: the band cut that was free with 16
  S-params costs 3-6 pts once antennas/transmission are removed. Single-antenna
  band sweep (all windows): 2-4 GHz again the best 2 GHz window (0.1-2 GHz
  collapses to 25% on F5 without array diversity); accuracy climbs monotonically
  with width, needing ~5 GHz (0.5-5.5) for near-parity with full band. Combined
  figure: `results/band_sweep_combined.png`. Takeaway: antennas and bandwidth
  are partially interchangeable information budgets; the 2-4 GHz region is the
  information centre at both hardware extremes.

- **Bandwidth-reduction sweep (CNN classification, chip-design study).**
  `Imager_CNN_LOSO.m` gains `CNN_LOSO_BAND="lo hi"` (GHz) to crop the frequency
  axis; outputs tagged `_band<lo>-<hi>`. Stage A: four 2 GHz windows x 3
  phantoms (raw, all 16 S-params, LOSO). Winner 2-4 GHz (mean 96.6%); high
  bands collapse on F5 (~70%, penetration physics). Expansion around the same
  region: 3/4/5 GHz. Result: **1-5 GHz (4 GHz BW) recovers full-band accuracy
  on every phantom** (empty 99.4 / F4 98.1 / F5 100.0); 1.5-4.5 GHz costs only
  ~1-3 pts on F5; 2-4 GHz alone costs 7 pts on F5. Curve:
  `results/band_sweep_curve.png`.

- **Classification decks: restyle + training-cost comparison.** Both
  `presentation/CNN_vs_MLP_Comparison{,_v2_noMeanSub}.pptx` reskinned from the
  solid-red title/divider slabs to the casual warm theme used by the regression
  decks (cream `FDF8F6` background, thin red top bar, red vertical accent,
  Cambria serif titles, muted greys). Added measured training-time facts in four
  places (structural table row, per-model cost bullets, summary box, conclusions
  card): CNN 5-45 min per LOSO fold on RTX 3070, ~20 GPU-h full sweep; MLP
  10 s-7 min per fold on CPU, ~3-4 CPU-h for the same sweep (~10x faster);
  inference is milliseconds for both.

- **Deck 3 revision (sim vs measured).** Reskinned to warm UofU theme with light
  title/closing slides; all em dashes removed. (1) Grid slide is now 3 panels:
  sim lattice, physical grid with the traced A3 bowl, and a true OVERLAY
  registered into one physical frame via `grid_placed_global.csv` (exact affine,
  0.0 mm residual). (2) Setup table: antennas are the SAME design ("Sam's Medium
  Antennas") in both; measured depth corrected to ~5 to 20 mm (near the patch),
  not +40 mm. (3) Raw S-parameters now shown PER PORT (2x2), not averaged, with
  measured clipped to 2-8 GHz: sim ports near-identical, measured ports differ.
  (4) New detectable-difference slide: measured empty DD (from the
  detectable_change program's npz) vs sim empty DD at z=+15 mm, same physical
  frame, showing the same spatial pattern (`fig_dd_compare.py`). (5) Numbers
  slide adds a "What is k-NN?" explainer and shows measured CNN LOSO (3.9 mm) vs
  LOPO single-position (9.9 mm). (6) Correlation figure caption wraps (no longer
  squished). Also removed the wrong +40 mm measured marker from the Deck 2 dS
  figure.

- **Deck 2 revision (simulated) + shared style fixes.** (1) Light title/closing
  slides (mostly white, crimson highlights) replacing the dark maroon, applied to
  Deck 1 and Deck 2. (2) Deck 2 reskinned to the UofU warm-red theme; all em
  dashes removed. (3) "Sam's Medium antennas" naming. (4) `fig_dS_vs_depth`
  caption now wraps (3 lines) so the plot is no longer squished; figure saved at
  fixed aspect and placed undistorted. (5) `fig_learning_curve.py` (new,
  replacing the inline figure): point labels clarified ("1 plane", then plane
  counts) with an explicit "point label = number of depth planes" box; plateau
  label moved clear of the point labels. (6) `fig_depth_lopo` renames "range
  edge" to "outer edge depth". (7) New "setup in pictures" slide in Deck 1 and
  Deck 2; placeholders live in `regression_deck/setup_photos/` (measured_bench,
  measured_grid, sim_model, sim_closeup) for the user to replace.
- **Located measured multi-depth data**: `.../Separated/July10/A3TumorDepthTesting_JULY10`,
  4 sessions at tumor heights (port-relative) -20, -7, +15, +25 mm (the 1227
  session's "2.5 cm below" is actually +25 above). The measured analog to the sim
  depth sweep.
- **Measured |dS| vs depth** (`fig_measured_dS_vs_depth.py` -> `measured_dS_vs_depth.png`,
  new Deck 2 slide "The bench sees the same depth shape"). Mean |dS| (tumor minus
  empty baseline, per-position averaged over 16 takes) at the 4 measured heights:
  -20 mm 0.0023, -7 mm 0.0042, +15 mm 0.0053 (peak), +25 mm 0.0044. The bench
  perturbation peaks at the radiating patch (+15 mm) and falls off both ways, the
  same shape the noiseless sim shows: an independent measured confirmation of the
  depth story.

## 2026-07-16

- **Deck 1 revision (measured).** (1) Predicted-vs-actual plots now overlay the
  TRACED A3 phantom bowl + F4/F5 glandular outlines (from
  detectable_change/A3_hunter/paper_figure_A3.py) instead of a binary
  near/exterior guess, so insert membership is read directly off the figure.
  (2) UofU warm-red theme (crimson/gold/maroon) across all slides; all em dashes
  removed. (3) New protocol-explainer slide (LOSO vs LOPO-cell vs single-position,
  with schematics + difficulty ladder). (4) LOPO slides now state the model (CNN)
  and define pooled vs in-session. (5) Single-position split into a graphical
  slide + an accuracy slide, matching the other two protocols. (6) Mixup slide
  reframed ("lower is better; grey = worse, crimson = the only win"). F4
  single-position run launched (pooled/subpos, 39 positions) to complete the set;
  its figure/number are placeholders until it lands.

## 2026-07-15

- **Three presentation decks** (`regression_deck/deck{1,2,3}_*.js` →
  `Deck1_Measured_Regression.pptx`, `Deck2_Simulated_Regression.pptx`,
  `Deck3_Sim_vs_Measured.pptx`). Deck 1: measured setup/algorithm + LOSO,
  LOPO-cell, LOPO-subpos across empty/F4/F5. Deck 2: sim setup, |ΔS|-vs-depth,
  data-need learning curve, 8-fold 3D result, depth generalization, per-depth
  examples. Deck 3: sim-vs-measured grids, raw S-param domain gap, the corrected
  numerical comparison (signal ~6 mm both; CNN gap = distinct-position coverage),
  and an exploratory sim→measured transfer. Reusable `render_pptx.ps1`
  (PowerPoint COM → PNG). QA renders gitignored.
- **New figures** (`regression_deck/`): `sim_dS_vs_depth.png` (tumor
  perturbation peaks at z≈15–20 mm, falls off both ways), `sim_depth_lopo.png`
  (leave-one-depth-out; interior ~1–3 mm, edges extrapolate), `grid_sim_vs_physical.png`
  (uniform 10 mm sim vs 6×6 physical cells, 51 measured), `raw_sparam_sim_vs_meas.png`
  (antenna domain gap), `sim_meas_correlation.png` (linear sim→measured transfer
  R²=0.65 on held-out freqs; MLP overfits, R²<0).
- **Figure fixes.** `sim_dS_vs_depth.png` now distinguishes the antenna **port /
  feed** (z = +3 mm) from the **radiating patch** (~15–20 mm in, due to the
  feed-line offset), plus the measured-tumor depth (z = +40 mm). The |ΔS| peak at
  ~15 mm coincides with the patch radiator — the tumor is nearest the *radiating
  element* there, not the feed. (Earlier drafts wrongly put the antenna at +3 mm
  and called the peak a pure array effect.) All raw S-parameter plots now display
  in dB (`sim_meas_correlation.png` S11 panel converted; `raw_sparam_*` already dB).

## 2026-07-14

- **Measured-empty single-point CNN LOPO (closes the sim↔measured comparison).**
  True leave-one-position-out on the empty A3 phantom, 3 June18 sessions pooled,
  51 positions, raw/all-antenna: **median 9.9 mm** (mean 12.0; 66.7% ≤0.5 in).
  Loses to training-free k-NN (6.0 mm) on the same task. Correction to first
  draft: each position is measured 16× (takes `T01…T16`) and `buildSession` uses
  every take as a sample, so training is ~2,400 raw samples — raw count is *not*
  the limiter. The limiter is **distinct spatial positions (~50)**; takes and
  sessions are repeat measurements of the same grid points, so they add
  robustness (→ LOSO 3.9 mm) but no new locations (→ LOPO 9.9 mm). The sim hit
  3.9 mm via ~1,000 *distinct* locations (13 depths × ~82). Gap is
  **distinct-position coverage, not sim-vs-real fidelity**. `RESULTS.md §3`.
- **Sim CNN data-quantity learning curve** (`SIM_DEPTHS` filter). 8-fold xy vs #
  depth planes (metal): 1 depth (82) 33 mm ≈ chance → 3 (245) 11 mm → 5 (410)
  4.8 mm → plateau ~3.8 mm from 7 (570). CNN needs ~400–500 samples to localize.
  Explains why single-layer LOO collapses while multi-depth works. Figure
  `sim_depth_learning_curve.png`, `RESULTS.md §5`.

## 2026-07-11

- **Beet (dielectric) tumor localization.** Loader now auto-detects a single
  `baseline_empty.s4p` (beet) vs the per-batch map (metal); `SIM_LABEL` tags
  outputs. 8-fold on the beet sweep (1065 pos): **xy 3.64 mm, z 2.07 mm** —
  statistically identical to metal (3.92 / 2.09). In the noiseless sim the ~19%
  weaker dielectric contrast costs nothing (signal still far above the numerical
  floor, equally position-coherent). See `RESULTS.md §5`.
- **Clean 5 mm depth grid** — data consolidated to `Data Results/A3_Metal_1cm`
  (single folder, per-batch empty baselines); loader rewritten to subtract each
  depth's own HFSS-batch baseline and to **exclude the off-grid z=3 mm plane**
  (`SIM_EXCLUDE_Z`). 1074 positions, 13 uniform depths. 8-fold: xy 3.92 mm,
  z 2.09 mm. Removing z=3 raised z=5's depth-out error 0.8→1.5 mm — z=3 had been
  a 2 mm-away helper; 1.5 mm is the honest uniform-grid value. Results tagged
  `_5mmgrid` (z=3-included versions preserved). See `RESULTS.md §5`.
- **Sim depth range extended to z = −15…+45 mm** (added b1_3_ALL_RESULTS →
  1134 positions, 14 depths). 8-fold: xy 3.71 mm, z 1.98 mm. Per-depth
  leave-one-depth-out shows (a) a **genuine gradual depth falloff** — z-error
  0.8 mm near the antenna plane climbing to ~3.7 mm at +40 mm; (b) the earlier
  "hard edges" −5/+30 mm were pure **extrapolation** — with neighbors on both
  sides they drop to 1.5/2.5 mm; new edges −15/+45 mm are the ~8–10 mm limits.
  Usable depth is bounded by the sampling range, not the model. See `RESULTS.md §5`.

## 2026-07-10

- **Simulated 3D (x,y,z) localization** (`cnn_matlab/Imager_CNN_SimReg.m`).
  SamMakin HFSS tumor sweep, 738 positions × 9 depths, differential dS input,
  `fc(3)` head, 8-fold position CV. **Result: lateral 3.35 mm, depth 1.55 mm**
  median (vs 36.7 / 8.6 mm chance) — matches k-NN floor on xy, beats it on z.
  Depth is not the weak axis (fine z sampling + full-band freq). Feasibility
  (`sim_feasibility_check.py`) + physics exploration (`sim_explore.py`, in the
  Simulation Data tree) established the signal is learnable and depth-robust.
  See `RESULTS.md §5`.
- **Leave-one-depth-out** (`SIM_CV=depth` mode added). Interior depths (0–25 mm)
  predict an unseen depth plane to z ≈ 1 mm — proves the CNN learned a continuous
  depth mapping, not memorized planes. Edge depths (−5/+30 mm) are extrapolation
  and degrade to 6–8 mm (expected). xy unaffected. See `RESULTS.md §5`.
- **Deck extended to the full phantom × protocol matrix** — predicted-vs-actual
  figures for empty/F4/F5 under both LOSO and LOPO (`regression_deck/`).

## 2026-07-09

- **Experiment 3 — heatmap (structured) output** (`Imager_CNN_RegLOPO.m`,
  `HEAD_MODE=heatmap`). Head → `fc(G)→softmax→regression` over a 0.4-in anchor
  grid, Gaussian soft target, centroid readout; fold train/predict refactored
  into `fitPredictFold`. **Negative: F5 pooled/cell 0.895 (heatmap), 0.865
  (heatmap+mixup)** vs 0.664 baseline; near-insert nearly doubled (centroid
  mass-leakage pulls predictions to grid centre). **Verdict on all 3 experiments:
  mixup is the only winner; posval and heatmap both hurt on this small dataset.**
- **Experiment 2 — position-disjoint validation** (`Imager_CNN_RegLOPO.m`,
  `POSVAL_FRAC` flag; `trainCNNReg` gained optional validation data +
  `OutputNetwork='best-validation'`, `ValidationPatience=Inf` to isolate model
  selection from early-stop). Carve a fraction of TRAIN *positions* out as a
  validation set and keep the best-validation net. **Negative result: F5
  pooled/cell 0.664 → 0.927** — losing ~20% of the scarce training positions
  outweighed the selection benefit.
- **Experiment 2b — posval + mixup combined.** Mixup replenishes the lost data:
  F5 pooled/cell 0.722 — better than posval alone (0.927) but still below mixup
  alone (0.572). Conclusion: position-disjoint validation is a net negative on
  this dataset regardless; mixup alone is the winner. (One transient
  `CUDA_ERROR_UNKNOWN`/heap-corruption GPU crash on first attempt; clean on
  retry — 2nd such transient GPU fault this session.)
- **Experiment 1 — mixup augmentation** (`Imager_CNN_RegLOPO.m`, behind the
  `MIXUP_ALPHA` flag; off by default so baseline behavior is unchanged). Offline
  mixup: append `ratio·N` synthetic train samples, each a convex blend of a
  random training pair with matching blended `(x, y)` target. Train-only, no
  LOPO leakage. **F5 pooled/cell: 0.664 → 0.572 in** (~14%), and near-insert
  improved *more* than exterior (0.75→0.61 vs 0.65→0.56) — teaching a smooth
  signal→coordinate map helps the barrier region most. See `RESULTS.md §4`.
- **Repo initialized.** Placed the CNN-vs-MLP localization study (classification
  + regression + LOPO) under git. Added `.gitignore`, `docs/` (METHODS, RESULTS,
  DEPENDENCIES, this CHANGELOG), and a versioned snapshot of the target-defining
  `position_adjustments.json` under `reference/`.
- **LOPO whole-cell, first pass COMPLETE** (`Imager_CNN_RegLOPO.m`,
  raw/all-antenna CNN, 40 epochs). Both modes, all 3 setups (F4 pooled/cell
  re-run after its transient `0xc0000409` GPU crash: 0.482 in, near/ext
  0.75/0.41). Results: interpolation to an unseen cell is ~3–4× harder than
  LOSO; pooled beats in-session on all three setups; near-insert error exceeds
  exterior everywhere (glandular barrier surfaces under interpolation, starkest
  F4 pooled ~1.8×). See `RESULTS.md §3`.

## 2026-07-08

- **Metric change: error distance only.** Removed the nearest-position "snap
  accuracy" from both regression scripts' printouts and JSON — per decision that
  continuous localization error is the meaningful metric. Predictions are never
  snapped.
- **Added diagnostics** to both regression scripts: per-position prediction
  **spread** (confidence proxy) and **near-insert / exterior stratification**
  (so insert-region error doesn't pollute exterior stats).
- **MLP physics-input memory fix** (`run_mlp_regloso.py`): the 51.6k-D physics
  features OOM'd with 3 threaded float64 seeds on a 16 GB machine → switched to
  sequential seeds + float32 cast.
- **Stage-2 regression results** (raw + physics × CNN + MLP × 3 setups)
  completed. CNN wins decisively; raw ≈ physics for CNN; physics *breaks* the
  MLP (predicts centroid). See `RESULTS.md §2`.

## 2026-07-07/08 (regression conversion)

- **Built the regression pipeline** converting the position *classifiers* to
  continuous `(x, y)` regression:
  - `mlp_python/label_xy.py` — canonical `RnCmPp → (x, y)` grid map (±0.375 in
    corner offsets) + photo-adjustment overrides. Single source of truth for
    targets; deliberately bypasses `hunter_loader._rcp_to_xy` (a different,
    approximate map fine only for classification plots).
  - `mlp_python/run_mlp_regloso.py` — 3-seed `MLPRegressor(256,128)` average,
    v2 preprocessing default, `--adjust-key`, optional `--ridge`.
  - `cnn_matlab/Imager_CNN_RegLOSO.m` — same conv trunk, head → `fc(2) +
    regressionLayer`, v2 default, `CNN_LOSO_ADJUST_KEY`.
- **Geometry verified**: canonical corners + photo adjustments (A3_F4 16 pos,
  A3_F5 9 pos, A3_Empty none) checked against the recording code.
- First LOSO regression runs (raw) confirmed the CNN localizes to ~0.16 in.

## Earlier (classification baseline)

- `Imager_CNN_LOSO.m` (MATLAB) vs `run_mlp_loso.py` (Python) head-to-head under
  leave-one-session-out, antenna subsets (all / pair / single / refl). Empty /
  F4 / F5 A3 setups. See top-level `README.md`.
