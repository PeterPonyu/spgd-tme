# Window trainer audit (2026-08-26)

There is no separate ML trainer class. The mother fit is `build_v4` via
`src/spgd_wrap.py`. Windows are script entry points.

| Script | Window | Gate | Inputs on disk | Wired |
|---|---|---|---|---|
| 02 sweep 33×400 | 1 | yes | openST/Xenium/CosMx benches | `apply_abstain` + t=0 π̂ dump |
| 03 F4 | 1 | no (needs F3) | — | cheap |
| 04 donor ×3 | 1 | yes | Q1 h5ad + truth | `apply_abstain` |
| 05 T2 | 1 | yes | openST 400 | refuse is real apply, not `max(w)` |
| 06 emit | 1 | no | needs Q2–Q5 csv | schema + T1 |
| 10 full-n t=0 ×3 | 2 | yes | full benches | `apply_abstain` |
| 09 seed1 t=0 ×3 | 2 fallback | yes | needs F3 | `apply_abstain` |

Smoke (300-spot leftover, not Window 1): `run_spgd` and blended-ref path both
returned a finite 300×13 frame. One 300-spot fit ≈ 45 s.

INTERVAL writer is `scripts/13_bootstrap_t0.py` (0 extra fits; needs `F3_pi_t0_*.csv`).
Sitting driver: `scripts/14_run_sitting.py` (pytest → preflight → Q2 → Q3 → INTERVAL → Q4 → Q5 → Q6 → `10`).
openST has no `benchmark_spots_counts.h5ad`; wrap falls back to spots.

Do not start 14 / 02 unless a 6 h sit is approved. 8 h is slack, not a second grid.
