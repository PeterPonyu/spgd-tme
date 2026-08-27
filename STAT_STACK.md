# SPGD-TME sufficient statistical stack (locked 2026-08-26)

Official sitting package stays **10 data figures + 3 tables**. Numbered TikZ schematics are manuscript figures, not additional sitting faces. No extra dose figure, no T4.

| Layer | Object | n / unit | Fits | When |
|---|---|---|---:|---|
| PRIMARY | F3 dose–response, 3 substrates × 11 t × seed 0 × 400 spots | 33 rows | 33 | Window 1 Q2 |
| CONFIRM (required) | Full-n t=0 only, same 3 substrates | 6971 / 2864 / 5686 | 3 | Window 2 P4c |
| INTERVAL | Spot bootstrap B=1000 on already-fit π̂ | percentile 95% CI | 0 | After Q2 (`13_bootstrap_t0.py`) |
| INSTANCE | 4 directed CosMx pairs; C→D locked | 6475 spots + 1 lock | 3 | Window 1 Q4 |
| OCCUPANCY | F9 type floor, already on disk | 24 type×pair; ρ=−0.849 | 0 | P0 done |
| ORTHOGONAL | realgt2 FLEX cosine, same 2864 spots | 1 cosine vs lock | 0 | Tonight P4a |
| OPTIONAL extra | seed=1 t=0 ×3 (mutex if full-n does not fit) | 3 rows, other file | 3 | Window 2 fallback only |

**Do not:** rewrite locked 400-spot F3 as a full-n dose grid unless scheduled (measured full-n × 11 t × 3 projection is 1.61 h, not 24 h), realgt2 as fourth F3 facet (+11 fits), GPU/remote 4090, 17-method board, MERFISH/STARmap main text, Paper B merge.

`build_v4` is CPU numpy. Local GPU and AutoDL 4090 are **not booked**.
