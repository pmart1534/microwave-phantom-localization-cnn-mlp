# Results Inventory (as of 2026-08-21, evening)

CNN = Imager_CNN_LOSO.m defaults (raw mag+phase, all 16 S-params, full 0.1-8 GHz,
single-stage, LOSO per-position vote) unless noted. 100 ep = canonical;
20 ep = fast regime (parity certified; convergence-audited).

## 1. Normal LOSO, Aug18-20 A3 campaign (all @100 ep)

| Dataset | Sessions | N-way | LOSO |
|---|---|---|---|
| Metal day-1 | 1143/1210/1239 | 49 | 99.32 +/- 1.18 |
| Beet 1 cm | 1334/1444/1512 | 49 | 99.32 +/- 1.18 (sole miss = documented mislabel R3C5P1; honest 100) |
| Metal next-day | 0909/0938/1008 | 49 | 100.00 +/- 0.00 |
| Fresh calibration | 1103/1200/1258 | 49 | 100.00 +/- 0.00 |
| Antenna reattach (4-way) | 1258+1509/1631/1703 | 49 | 100.00 +/- 0.00 |
| Antenna-unit SWAP (4-way) | 0856/0922/0954/1020 | 49 | 97.96 +/- 1.67 |
| Oil change (fresh canola/session) | 1120/1154/1225 | 49 | 97.96 +/- 0.00 |
| A3F4 Aug20 | 1655/1804/1820 | 37 | 98.20 +/- 3.12 |
| Empty/Nothing NULL CONTROL | 1744/1807/0802 | 49 | 3.40 +/- 2.36 (chance 2.0 - passes) |

## 2. Cross-split experiments (Imager_CNN_XDay.m, @100 ep)

| Train -> Test | Result |
|---|---|
| Day-1 metal -> day-2 metal | 100.00 |
| Fresh-cal (pristine) -> reattached | 99.32 (exposure worth ~0.7 - intrinsic robustness) |
| Day-2 metal (pristine) -> swapped units | 93.37 +/- 6.95 (folds 100/93.9/95.9/83.7; exposure worth ~4.6; worst = full reversal) |

## 3. Position-disjoint (Imager_CNN_ValPos.m, train 49 corners -> test 8 unseen P9 centers)

- Classification -> nearest corner: mean 1.08 in (median 0.73), own-cell hit 23.7% (ideal 0.53 in, chance 1.74)
- Regression (fc(2) xy head): mean 0.539 in = grid floor; per-cell consistent, pulled to trained manifold
- Verdict: no true interpolation on 0.75-in-pitch grid. LOPO harness = next build.

## 4. Reduced configs @ 2-5 GHz (all16 / refl-only-4ant / pair-1&3-fullS)

| Dataset | all16 | refl4 | pair13 | ep |
|---|---|---|---|---|
| Metal day-1 | 98.6 | 96.6 | 97.3 | 100 |
| Beet | 98.6 | 96.6 | 98.0 | 100 |
| Metal next-day | 99.3 | 97.3 | 98.0 | 100 |
| Fresh-cal | 98.6 | 98.0 | 95.2 | 100 |
| Reattach (4-way) | 99.5 | 99.5 | 99.0 | 100 |
| Swap (4-way) | 97.5 | 88.8* | 90.8* | 20 (*audit: still-improving; promote to 100 ep before quoting) |
| Oil | 97.3 | 96.6 | 96.6 | 20 |
| A3F4 Aug | 86.5 | 81.1 | 87.4 | 20 (band cut costs ~12 pts here, unlike July F4) |

Bonus full-band refl-only (all 4 ant): metal 98.6, beet 93.9, metal-day2 100.0, fresh-cal 98.0.

## 5. Preprocessing ablations (variants vs same-epoch reference)

Ideal metal (100 ep, ref 99.32): nobase 99.3 | nomean 100.0 | nobase+nomean 100.0 |
zs-off 99.3 | zs-row 99.3 | zs-global 99.3 | innorm-off 99.3 | ALL-OFF 99.3.

Reattach 4-way (100 ep, ref 100.0): all singles 99.5-100.0 | ALL-OFF 94.9.

Swap 4-way (20 ep, ref 97.96): nobase 99.5 | nomean 97.5 | nobase+nomean 99.5 |
zs-off 98.0 | zs-row 98.0 | zs-global 95.4 | innorm-off 97.5 | ALL-OFF 17.9.

Oil (20 ep, 5 variants): nobase 98.0 | nomean 97.3 | zs-off 98.0 | zs-global 98.0 | ALL-OFF 83.7.

A3F4 Aug (20 ep, 5 variants): nobase 97.3 | nomean 93.7 | zs-off 96.4 | zs-global 96.4 | ALL-OFF 82.0.

HEADLINE - drift-severity ladder for raw (no preprocessing) input:
ideal 99.3 -> reattach 94.9 -> oil 83.7 / A3F4 82.0 -> swap 17.9.
Any single normalization mechanism restores 95-99.5 everywhere.

Reconciliation vs old A2 study (it was the MODEL): MLP on Aug18 metal 99.32 with
z-score vs 90.48 +/- 13.5 without; CNN indifferent everywhere tested
(single-S11 metal 84.4 vs 83.0; F5 all16 z-off 100.0).

## 6. Component (magnitude vs phase)

- Mag-only full band (20 ep): SWAP 100.00 (beats mag+phase 97.96 - phase carries
  unit fingerprints), oil 97.96, A3F4 97.3.
- July minimal-chip study (June18 empty + July F4): mag-only near-parity at
  1-4 GHz (98.7/86.5 single-ant), collapses narrow (empty 30.1 @50 MHz,
  F4 35.9 @0.25 GHz); single-tone mag+phase works (empty 66/91.5, F4 61/90.4
  at 1/2-ant refl).

## 7. Diagnostics

- Loss-vs-epoch curves (CNN_LOSO_CURVES=1, monitoring-only validation +
  auto CONVERGED/STILL-IMPROVING audit): metal LOSO converges by ~epoch 5,
  flat thereafter, no overfit signature (reviewer figure done).
- Epoch parity: 20 ep == 100 ep on hard configs (single-S11 metal 84.35 both;
  swap ref 97.96 both). 20 ep + curves = standard exploration regime.

## 8. July campaign (June18 empty / July03 F4, F5) - summary

- CNN-vs-MLP matched factorial (input x antenna x phantom, v1/v2 pipelines),
  hierarchical ablation, refl-only: CNN >= MLP everywhere except F4 refl-pair.
  Decks: CNN_vs_MLP_Comparison[_v2_noMeanSub].pptx.
- Frequency_Reduction.pptx (17 slides): band placement/width (1-5 GHz parity),
  break tiers, placement scans (0.25 + 0.1 GHz; per-phantom best centers),
  break-descent maps v1/v2 (hardware x band), minimal-chip (tones + mag-only).

## 9. Known gaps / queued next

- Promote swap refl/pair @2-5 to 100 ep (audit-flagged).
- Mag-only day2->swap transfer (mechanism test for phase fingerprints).
- LOPO harness (regression + distance-scored classification), per Joel Harley.
- P5-P8 edge-midpoint positions never measured; P9 centers only in metal day-1
  sessions' validation/ folders.
- Oil/A3F4 loss-curve promotions where audit flagged (mostly low-loss).
- Session-01 swap arrangement note truncated in README (scored 100 on pristine
  transfer - possibly near-normal arrangement; confirm layout).

## 10. Added 2026-08-21 (deadline day)

- Oil caveat: 2 of 3 LOSO misses (R6C3P2, R6C4P1) sit in OilChange03's
  documented row-6 error region; clean-region accuracy ~99.2.
- Pristine->swap transfer: mag+phase 93.37; MAG-ONLY 98.47 (+5.1; mechanism
  confirmed - unit fingerprints are phase-borne).
- LOPO regression (metal, 49 holds, stats exclude held-out position, @20ep):
  vote err mean 0.758 in / median 0.739 (chance ~1.74); interior 0.09-0.5,
  edges up to 1.8 (extrapolation).
- Cheap-device factorial @20ep, {both,mag,phase} x {all16,refl4} x {full,2-5}
  x {metal,swap,oil}: winner = MAG + ALL16 + 2-5 GHz (98.0/99.0/96.6);
  mag+refl collapses (78.2 metal) - magnitude needs transmission; full-cheap
  (mag+refl+2-5) = 87.8/83.7/89.1; phase-only worst on swap (77.6).
  18 audit flags - promote low cells before quoting individually.
