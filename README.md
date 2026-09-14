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

The release runs in dependency order:

1. `python scripts/check_scaffold.py` — verifies the required inputs and layout.
2. `python -m pytest tests -q` — the 104-check release contract (seven checks read the built
   PDF and are skipped until `manuscript/main.pdf` exists).
3. `Rscript manuscript/scripts/R/render_disk_faces.R`,
   `Rscript manuscript/scripts/R/render_F12_keep.R`, and
   `python manuscript/scripts/generate_tables.py` — reproduce the figures and table bodies
   from `data/plotdata/`.
4. The `revision_v3/` scripts — rerun the V3 numerical audits; see `revision_v3/README.md`.

## Tested environment

CPython 3.13.7; R with ggplot2, patchwork, dplyr, tidyr, ragg, and Cairo; a TeX Live
installation with `latexmk`, `bibtex`, and `latexdiff` for the manuscript builds. Wall-clock
timings were measured on an Intel Core Ultra 9 275HX (24 logical CPUs, 62 GiB RAM) with no
accelerator; they are environment-specific benchmarks, not hardware-independent constants.

## Troubleshooting

- Missing provider-controlled inputs: obtain the source libraries from their original
  repositories under their access terms; the release identifies derived matrices by content
  digest and does not redistribute them.
- Missing R packages or LaTeX tooling: install the packages listed above; checks (1)–(2)
  need neither.
- Stale derived files: `submission/`, `supplementary/`, and `manuscript/main.pdf` are all
  rebuilt from source by the scripts above; delete and rerun rather than patching outputs.

## Release boundary

`LICENSES.md` describes the separation between code, figure-level derived values, and
provider-controlled source data. Machine paths, private workbench records, agent transcripts,
and compute-queue notes are excluded. The V2 release remains available in the Git history;
V3 is additive and does not rewrite historical calls.

## Citation and archive

Cite a frozen build through its versioned Zenodo record rather than through a branch name.

The V2 reproducibility package is deposited and citable. The V3 repository branch is now
publicly visible and accompanies the manuscript as the review-build source. A versioned V3
Zenodo deposit has not yet been created; until that deposit exists, cite the V2 archive DOI
for the archival release and use the V3 branch as the review-build source.
