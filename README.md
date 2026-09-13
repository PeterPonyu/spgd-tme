# SPGD-TME

Reproducibility release for *Two locked operators report mixed-spot TME composition on CosMx carcinomas*.
The repository preserves the V2 release history and adds the V3 review build as an additive,
reviewable release layer.

## V3 review build

The current revision contains 15 figures and 3 tables. It evaluates two locked operators:

- a cosine-based KEEP/ABSTAIN reportability gate with a cutoff fixed before the sensitivity sweeps;
- a Patient-ID disjoint donor split for mixed-spot construction and reference transfer.

The V3 layer adds the full-input eight-library scan, cutoff stability and clustered bootstrap,
full-n gate-input audit, downstream abstention analysis, reference-floor sensitivity, repeated
timing, corrected conditional-renormalization audit, and a matched Tangram comparator. Exact
numerical outputs are retained in machine-readable files under `revision_v3/analyses/` and
`revision_v3/out/`.

## Reproduction

Render-level checks that do not require provider-controlled raw inputs:

```bash
python scripts/check_scaffold.py
python -m pytest tests -q
```

The V3 numerical analyses are run from the scripts under `revision_v3/`. Source libraries and
provider-controlled reference inputs must be obtained from their original repositories under
their applicable access terms. This release does not redistribute NanoString raw files or
reference matrices unless the governing provider agreement expressly permits it.

## Release boundary

`LICENSES.md` describes the separation between code, figure-level derived values, and
provider-controlled source data. Machine paths, private workbench records, agent transcripts,
and compute-queue notes are excluded. The V2 release remains available in the Git history;
V3 is additive and does not rewrite historical calls.

## Citation and archive

Use the versioned Zenodo record associated with the release when citing a frozen build. The
repository and archive should be considered synchronized only after the corresponding public
release verification has been completed.
