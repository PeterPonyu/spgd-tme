# SPGD-TME

Frontiers in Genetics Methods companion to CBC SPGD.
New tree. Does not write `capsules/spgd-deconv` or `deconv-lab/data/realgt4_benchmark`.

**Now:** post-sitting F3–F5 and T1–T3 are rendered into the locked 12-figure + 3-table manuscript. Rebuilds consume `data/plotdata/` only; donor pairs and experimental CSVs are not regenerated.

```bash
conda run -n dl python scripts/check_scaffold.py
conda run -n dl python -m pytest tests -q
```

Heavy scripts exit 3 unless `SPGD_TME_COMPUTE=1`.
