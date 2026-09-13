# SPGD-TME

Reproducibility release for *Two locked operators report mixed-spot TME composition on CosMx carcinomas*.
The repository preserves the V2 release history and adds the V3 review build as an additive,
reviewable release layer.

## V3 review build

The current revision contains 15 figures and 3 tables. It evaluates two locked operators:

- a cosine-based KEEP/ABSTAIN reportability gate with a cutoff fixed before the sensitivity sweeps;
- a Patient-ID disjoint donor split for mixed-spot construction and reference transfer.

The V3 layer adds the full-input eight-library scan, cutoff stability and clustered bootstrap,
a library-clustered permutation test of platform family against pair collinearity, the full-n
gate-input audit, downstream abstention analysis, reference-floor sensitivity, repeated
timing, and the corrected conditional-renormalization audit.

It also adds a matched multi-method comparison on identical spot sets and the same locked
cell-count truth: a fresh independent Tangram refit on CosMx BCC, and RCTD and cell2location
re-scored from their real saved runs on Xenium, Xenium FLEX, and openST. The comparison is
reported with its losses as well as its wins — RCTD attains a lower malignant-coordinate RMSE
on Xenium and a lower overall RMSE on Xenium FLEX — because the article's claim concerns the
reportability state rather than aggregate accuracy.

Exact numerical outputs are retained in machine-readable files under `revision_v3/analyses/`
and `revision_v3/out/`.

## Reproduction

Render-level checks that do not require provider-controlled raw inputs:

```bash
python scripts/check_scaffold.py
python -m pytest tests -q
```

The V3 numerical analyses are run from the scripts under `revision_v3/`. Source libraries and
provider-controlled reference inputs must be obtained from their original repositories under
their applicable access terms. The governing NanoString agreement has been read clause by
clause; it permits non-commercial redistribution of derived reference matrices only under
same-licence terms that a CC-BY supplement cannot carry, so this release identifies those
matrices by content digest instead of shipping them. See `LICENSES.md` for the full boundary.

## Release boundary

`LICENSES.md` describes the separation between code, figure-level derived values, and
provider-controlled source data. Machine paths, private workbench records, agent transcripts,
and compute-queue notes are excluded. The V2 release remains available in the Git history;
V3 is additive and does not rewrite historical calls.

## Citation and archive

Cite a frozen build through its versioned Zenodo record rather than through a branch name.

The V2 reproducibility package is deposited and citable. The V3 package accompanies the
manuscript as Supplementary Material; its archival deposit is scheduled for acceptance so that
the released version matches the accepted text. Until that deposit exists, treat this
repository and the archive as synchronized only for V2.
