# Minimal-chip map: tone descent + magnitude-only

CNN, LOSO. mag+phase = standard raw input; mag only = |S| rows only
(scalar power-detector measurement). Native grid 10 MHz: 1 pt = single
CW tone. Missing cells: not run (or skipped after a <50% break).

## Empty (center ~1.875 GHz)

| config | 1-4 (3 GHz) | 2-2.25 (0.25 GHz) | 1.85-1.9 (0.05 GHz) | 1.86-1.89 (4 pts) | 1.86-1.88 (3 pts) | 1.87-1.88 (2 pts) | 1.87-1.87 (1 pt) |
|---|---|---|---|---|---|---|---|
| 1 ant (S11), mag+phase | 98.0±2.0 | 86.3±2.0 | 74.5±3.9 | 73.2±2.3 | 68.0±2.3 | 69.3±4.9 | 66.0±4.5 |
| 1 ant (S11), mag only | 98.7±2.3 | 70.6±7.1 | 30.1±1.1 | - | - | - | - |
| 2 ant (1&3) refl, mag+phase | 99.3±1.1 | 99.3±1.1 | 94.8±1.1 | 94.1±3.4 | 93.5±4.5 | 94.8±4.1 | 91.5±6.0 |
| 2 ant (1&3) refl, mag only | 99.3±1.1 | 95.4±1.1 | 78.4±2.0 | 71.2±4.1 | 60.1±4.9 | 56.2±4.1 | 49.7±4.9 |

## F4 (center ~3.0 GHz)

| config | 1-4 (3 GHz) | 3-3.25 (0.25 GHz) | 2.975-3.025 (0.05 GHz) | 2.98-3.01 (4 pts) | 2.99-3.01 (3 pts) | 2.99-3 (2 pts) | 3-3 (1 pt) |
|---|---|---|---|---|---|---|---|
| 1 ant (S11), mag+phase | 95.5±6.1 | 78.2±4.4 | 70.5±4.9 | 61.5±6.9 | 64.7±6.7 | 64.7±10.5 | 60.9±9.7 |
| 1 ant (S11), mag only | 86.5±1.3 | 35.9±5.9 | - | - | - | - | - |
| 2 ant (1&3) refl, mag+phase | 94.9±3.0 | 91.7±2.5 | 89.1±4.4 | 88.5±8.5 | 91.0±6.5 | 90.4±4.4 | 90.4±3.8 |
| 2 ant (1&3) refl, mag only | 94.9±2.1 | 85.3±3.2 | 80.1±5.7 | 76.9±5.5 | 73.7±8.5 | 66.0±8.2 | 69.9±8.5 |
