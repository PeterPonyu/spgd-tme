# SPGD-TME status (2026-08-26)

**Step:** Post-sitting manuscript build complete from locked plotdata.  
**Object:** Methods companion to the existing SPGD stack. Public leaf is SPGT. Official CBC SPGD untouched.  
**Package:** 11 data figures + 3 tables of data faces; 12 numbered figures + 3 tables in the manuscript.

## Closed (short CPU, 0 new fits)

- Tasks 0–3, Q1 pairs, `07` cosine, `08` truth faces
- T1 hashes (`11_emit_t1_materials.py`, 12 rows)
- F2 / F9 / F10 rendered from disk (`manuscript/figs/rendered/`)
- F3–F5 rendered; T1–T3 generated and integrated with measured Results text
- Preflight `00` OK (types, gene overlap, donor triples, Q6 hash inputs, `build_v4` import, RAM)
- Sitting plotdata present, including B=1000 t=0 intervals and full-n confirmation
- SPGT public leaf

## Sitting stack (completed)

The completed outputs are retained under `data/plotdata/`; manuscript rebuilds do not rerun the sitting.

- Window 1: Q2→Q6 (33+3+1 fits) + substrate checkpoints
- INTERVAL: B=1000 on saved t=0 π̂ (0 fits)
- Window 2: `10` full-n t=0 ×3
- Resume skips completed tables; a crash does not redo finished substrates/steps
- Expected wall ~2–4 h; 6 h comfortable; 8 h is slack. GPU-h = 0

## Do not

- Rebuild donor pairs
- Set `SPGD_TME_COMPUTE=1` unless a sit is explicitly started
- Spend leftover hours on full-n × 11 t
- Book extra GPU (`GPU_QUEUE.md` is empty)
- Write CBC or `realgt4_benchmark`
- Invent RMSE / DestVI / survival numbers
