# SPGD-TME revision V3 enhancement package

Additive analyses generated in the stable source repository to deepen the V2
revision. Every result here is reproducible from the documented inputs with the
scripts in this directory; provider-controlled source libraries remain subject to their original access terms. Nothing in this package modifies a lock, a
historical call, a probe JSON, or a manuscript number, and the frozen cutoff
`c* = 0.80` is never re-tuned.

## Reproduce

```bash
cd <repository-root>
python revision_v3/scan_all_libraries.py         # Task A: 8-library complete scan (~25 s)
python revision_v3/downstream_and_gate_fulln.py  # Tasks B+C: full-n fits (~15 min)
python revision_v3/comparator_tangram.py         # Task D: fresh Tangram refit (~3 min)
```

## Validation anchor (why these numbers can be trusted)

- Every platform designated cosine with a historical lock reproduces to six
  decimals: openST 0.972678, Xenium 0.980196, CosMx BCC 0.603666
  (`out/validation_anchor.csv`).
- The full-n BCC tumor RMSE recomputed here, 0.1516, equals the manuscript's
  reported full-n value (R2-13: 0.1516 [0.1477, 0.1561]).

## Findings by reviewer point

### R2-3 — malignant-neighbor selection rule (was the largest open gate)
`out/complete_eligible_scan.csv`, `out/library_rule_comparison.csv`,
`NEIGHBOR_RULE_LOCK_SPEC.md`.

The complete eligible scan is now available for **all eight libraries**,
including the four (openST, Xenium, Xenium FLEX, CosMx BCC) the V2 note listed
as "designated-only until their full eligible scans are available." Under the
maximum-eligible rule at `c* = 0.80`, three KEEP libraries flip to ABSTAIN:

| Library | Designated → call | Max-eligible neighbor → call |
|---|---|---|
| CosMx NSCLC | fibroblast 0.6482 → KEEP | epithelial 0.8473 → ABSTAIN |
| CosMx HCC | Stellate.cells 0.6486 → KEEP | CD3+ αβ T cells 0.8541 → ABSTAIN |
| CosMx BCC | Normal.Kerat 0.6037 → KEEP | Melanocyte 0.8247 → ABSTAIN |

The HCC flip is driven by an immune neighbor (CD3+ T cells), which is
biologically implausible collinearity and most likely a small-panel artifact.
This is direct evidence that an unconstrained maximum rule is unsafe and that
the manuscript's decision to keep the designated pair primary is correct. The
lock spec recommends locking the designated-pair rule and publishing this scan
as the R2-3 sensitivity audit.

### R2-2 — origin and stability of c* = 0.80
`out/cutoff_separability.json`.

Across all eight libraries the maximum designated-KEEP cosine is 0.6486 and the
minimum designated-ABSTAIN cosine is 0.8616. The frozen 0.80 lies inside the
empty interval (0.6486, 0.8616); no designated cosine falls in that band, so all
eight designated calls are invariant for every cutoff in 0.75-0.85. This is a
principled, data-grounded justification for 0.80 that does not re-tune it.

### R2-4 — platform/library clustering
`out/clustered_bootstrap.json`.

Library-clustered bootstrap (8 clusters, B = 4000) on the fraction of eligible
eligible pairs with cosine >= 0.80: point 0.239, 95% CI [0.119, 0.400] over 109 eligible pairs (of a 112-column all-annotation scan).

### R2-5 — external comparators (matched, same locked truth)
`out/comparator_tangram.json`, `comparator_matched.py`, `out/comparator_matched.csv`.

Tangram was run as a fresh independent method on CosMx BCC (800-spot matched
subset): SPGD `build_v4` is more accurate on every axis (overall RMSE 0.108 vs
0.206, tumor RMSE 0.157 vs 0.491, type PCC 0.605 vs 0.330, spot PCC 0.844 vs
0.551, JSD 0.094 vs 0.254). `comparator_matched.py` additionally re-scores the
real saved RCTD (spacexr 2.2.1) and cell2location runs from the deconv-lab
pipeline against the same locked truth alongside a fresh SPGD fit: SPGD beats
cell2location on openST (overall RMSE 0.093 vs 0.121) and is close to RCTD on the
two Xenium libraries (0.087 vs 0.088; 0.093 vs 0.089), with RCTD retaining a
lower malignant-coordinate RMSE. Reported without a uniform-superiority claim.
The matched harness reads external saved outputs; set `SPGD_DECONV_ROOT` to the
deconv-lab checkout to rerun.

### Gate-input scope (C03) at full n
`out/gate_input_fulln.csv`.

The bounded C03 P-versus-S audit is repeated at full n. openST remains
DISCREPANT at full scale (P = 0.9727 ABSTAIN, S = 0.6895 KEEP); Xenium, Xenium
FLEX, and CosMx BCC are identical between P and S. This confirms the C03 finding
was not a 400-spot artifact and supports defining P as the gate input while
retaining S for the composition fit.

### Downstream of a locked flip (contract for R2-3)
`out/bcc_abstain_downstream.json`.

If BCC were locked to ABSTAIN, the Cancer.cells coordinate (full-n tumor RMSE
0.1516 under KEEP) is withheld, and the non-malignant simplex is renormalized
and re-scored (RMSE 0.2140, type PCC 0.417, spot PCC 0.661). The withheld
coordinate is reported as missing, never scored as zero.

## Integrity

- Reads references read-only; writes only under `revision_v3/out/`.
- No lock, historical call, probe JSON, or manuscript number is modified.
- Runs in the stable source repo; the V2 capture tree and the concurrent
  MIRROR_v3_enhanced work are untouched.

## Release status and follow-up

- R2-16 NanoString licence: the governing non-commercial agreement was read clause by clause;
  the semantic clause determination and redistribution boundary are recorded in the top-level
  `LICENSES.md`. The confidential agreement text is not redistributed.
- cell2location / RCTD are re-scored from the deconv-lab pipeline's real saved runs via
  `comparator_matched.py` (set `SPGD_DECONV_ROOT`); a from-scratch install is only needed to
  regenerate those saved outputs.
- The `codex/v3-public-release` GitHub branch is public. A V3 Zenodo deposit is still pending
  creation with a fresh credential and a final payload audit; the V2 DOI remains the citable
  archival release until then.
