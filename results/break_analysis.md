# Bandwidth breaking-point analysis

CNN classification, raw input, all 16 S-parameters, LOSO per-position vote.
Best window per width (placement optimised at every width).

Tiers: DEGRADED < 90% of full-band | UNSTABLE fold sigma >= 10 | BROKEN < 50% | DEEP < 25%

## Empty (full-band 99.3%)

| width (GHz) | best window | mean % | fold sigma | flags |
|---|---|---|---|---|
| 5 | 0.5-5.5 | 99.3 | 1.1 | - |
| 4 | 1-5 | 99.3 | 1.1 | - |
| 3.9 | 0.1-4 | 99.3 | 1.1 | - |
| 3 | 1-4 | 99.3 | 1.1 | - |
| 2 | 2-4 | 99.3 | 1.1 | - |
| 1.9 | 0.1-2 | 99.3 | 1.1 | - |
| 1 | 1-2 | 99.3 | 1.1 | - |
| 0.5 | 1.5-2 | 99.3 | 1.1 | - |
| 0.25 | 2-2.25 | 100.0 | 0.0 | - |
| 0.2 | 1.775-1.975 | 99.3 | 1.1 | - |
| 0.1 | 1.825-1.925 | 98.7 | 2.3 | - |
| 0.05 | 1.85-1.9 | 99.3 | 1.1 | - |

Breaking points: degraded at never GHz, unstable at never GHz, broken(<50%) at never GHz, deep(<25%) at never GHz.

## F4 (full-band 97.4%)

| width (GHz) | best window | mean % | fold sigma | flags |
|---|---|---|---|---|
| 5 | 0.5-5.5 | 97.4 | 3.0 | - |
| 4 | 1-5 | 98.1 | 2.5 | - |
| 3.9 | 0.1-4 | 98.1 | 2.5 | - |
| 3 | 1-4 | 98.1 | 2.5 | - |
| 2 | 2-4 | 97.4 | 2.1 | - |
| 1.9 | 0.1-2 | 96.2 | 4.4 | - |
| 1 | 1.5-2.5 | 98.7 | 1.5 | - |
| 0.5 | 2.5-3 | 97.4 | 2.1 | - |
| 0.25 | 3.5-3.75 | 98.1 | 2.5 | - |
| 0.2 | 1.775-1.975 | 95.5 | 3.8 | - |
| 0.1 | 1.825-1.925 | 94.9 | 5.1 | - |
| 0.05 | 1.85-1.9 | 90.4 | 7.1 | - |

Breaking points: degraded at never GHz, unstable at never GHz, broken(<50%) at never GHz, deep(<25%) at never GHz.

## F5 (full-band 100.0%)

| width (GHz) | best window | mean % | fold sigma | flags |
|---|---|---|---|---|
| 5 | 0.5-5.5 | 100.0 | 0.0 | - |
| 4 | 1-5 | 100.0 | 0.0 | - |
| 3.9 | 0.1-4 | 100.0 | 0.0 | - |
| 3 | 1-4 | 100.0 | 0.0 | - |
| 2 | 2-4 | 92.9 | 4.6 | - |
| 1.9 | 0.1-2 | 90.9 | 5.2 | - |
| 1 | 1.5-2.5 | 92.9 | 12.2 | UNSTABLE |
| 0.5 | 1.5-2 | 88.9 | 14.3 | DEGRADED UNSTABLE |
| 0.25 | 2-2.25 | 83.8 | 3.5 | DEGRADED |
| 0.2 | 1.775-1.975 | 73.7 | 16.7 | DEGRADED UNSTABLE |
| 0.1 | 1.825-1.925 | 62.6 | 17.5 | DEGRADED UNSTABLE |
| 0.05 | 1.85-1.9 | 59.6 | 17.8 | DEGRADED UNSTABLE |

Breaking points: degraded at 0.5 GHz, unstable at 1.0 GHz, broken(<50%) at never GHz, deep(<25%) at never GHz.
