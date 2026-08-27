# Compute queue (do not run until scheduled)

Scaffold and unit tests do not need this file. The jobs below call `build_v4`
or rebuild CosMx h5ad and stay behind `SPGD_TME_COMPUTE=1`.

| Order | Command | Why it is heavy |
|---|---|---|
| Q1 | already on disk (`A_from_B`, `B_from_A`, `D_from_C`) | Do not rerun; nonempty dirs refuse overwrite |
| sit | `SPGD_TME_COMPUTE=1 conda run -n dl python -u scripts/14_run_sitting.py` | pytest + preflight + Q2–Q6 + bootstrap + P4c |
| Q2 | inside sitting / `02` | 33 SPGD fits on 400-spot subsets; per-substrate resume |
| Q3 | inside sitting / `03` | Cheap; needs F3 csv |
| Q4 | inside sitting / `04` | 3 SPGD fits on new pairs |
| Q5 | inside sitting / `05` | One SPGD-sized timing pass |
| Q6 | inside sitting / `06` | Schema + T1; needs Q2–Q5 tables |
| INTERVAL | inside sitting / `13` | B=1000 on saved π̂; 0 fits |
| P4c | inside sitting / `10` | full-n t=0 ×3 |

Default pytest excludes `tests/compute`. Do not background-wait these here.

**Wall clock (CPU only — no GPU box):**
- Measured full-n t=0 (script 17, 2026-08-27): openST 267.7 s (n=6971), Xenium 24.2 s (n=2864), CosMx 234.6 s (n=5686). One t-cycle across three substrates is 526 s. Projected full-n × 11 t × 3 = **1.61 h**, not 24 h.
- The old ~24 h figure assumed a much slower per-spot cost and is retired.
- Do not spend leftover hours rewriting the locked 400-spot F3 table as a full-n dose grid unless scheduled. The hour projection is now measured; the sitting F3 face stays the 400-spot sweep.

**Calendar:**
- Closed: P0 truth faces, `07` cosine, T1 hashes (`11`), F2/F9/F10 R, Methods body, preflight, sitting driver.
- One sit: `14` serial. Do not background. Do not parallel Q2 and Q4.
- After sitting: R F3–F5 + `latexmk`. Extra GPU queue is empty (`GPU_QUEUE.md`).
- Do not rebuild Q1. Do not run full-n × 11 t F3. Do not rsync h5ad to AutoDL.
