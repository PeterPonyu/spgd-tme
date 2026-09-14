# SPGD-TME figure contract (2026-08-27)

User bar: **14 data figures + 3 tables of data faces**, plus **1** numbered protocol figure (15 figures + 3 tables).

Figures 2–12 carry at least panels A–E (target A–F). Figures 13–15 are the V3 revision boards (rule audit, calibration, full-n/comparator). The four former TikZ schematics live as panels of Figure 1.

| ID | Object | Role | Section |
|---|---|---|---|
| Fig 1 | Protocol, equations, gates, donor split, metrics, timing | numbered schematic | Methods |
| Fig 2 | Mixed-spot instance | result | Results |
| Fig 3 | Four-patient cell-level geography | result | Results |
| Fig 4 | Ulcerated-nodular spatial field | result | Results |
| Fig 5 | Wound-axis spatial field | result | Results |
| Fig 6 | CosMx KEEP tumor geography | result | Results |
| Fig 7 | Collinearity dose and refusal | result | Results |
| Fig 8 | Donor-transfer recovery | result | Results |
| Fig 9 | Myeloid and stromal occupancy | result | Results |
| Fig 10 | Evaluation board | result | Results |
| Fig 11 | Pair type-floor occupancy | result | Results |
| Fig 12 | Independent KEEP-carcinoma board | result | Results |
| Fig 13 | Rule selection and reference perturbation | revision | Results |
| Fig 14 | Truth-stratified calibration and block bootstrap | revision | Results |
| Fig 15 | Full-n gate, complete scan, Tangram, BCC consequence | revision | Results |

Do **not** reprint CBC official spatial A–D as this paper’s hero.
Do **not** add T4, 17-method rank, KM/TCGA, MERFISH/STARmap main text.
Reader PDF does **not** print SHA hashes or internal filenames.

## Submission capsule

The editing copy under `manuscript/` is sectioned; the capsule is not. Build it with
`python scripts/28_assemble_submission.py`, which writes `submission/` and refuses to
finish if any of the contract below is violated.

- One flat directory. No subdirectories.
- One `.tex`. Every section, table body and caption is spliced in, and the resolved
  bibliography is inline, so the capsule compiles without bibtex and without a `.bib`.
- Figures are `Figure1.jpg`–`Figure15.jpg` at 300 dpi, named explicitly by the `.tex`.
  Figure 1 is the TikZ protocol panel compiled and rasterised like the rest, so the
  capsule does not depend on TikZ.

| Capsule | Source |
|---|---|
| `Figure1.jpg` | `manuscript/figs/fig_pack.tex` |
| `Figure2.jpg` | `F2_hero.pdf` |
| `Figure3.jpg` | `F3_cohort.pdf` |
| `Figure4.jpg` | `F4_ulcerated.pdf` |
| `Figure5.jpg` | `F5_wound.pdf` |
| `Figure6.jpg` | `F6_keep.pdf` |
| `Figure7.jpg` | `F7_dose.pdf` |
| `Figure8.jpg` | `F8_donor.pdf` |
| `Figure9.jpg` | `F9_myeloid.pdf` |
| `Figure10.jpg` | `F10_eval.pdf` |
| `Figure11.jpg` | `F11_floor.pdf` |
| `Figure12.jpg` | `F12_keep.pdf` |
| `Figure13.jpg` | `F13_revision_audit.pdf` |
| `Figure14.jpg` | `F14_revision_support.pdf` |
| `Figure15.jpg` | `F15_v3_fulln_comparator.pdf` |

`submission/` is generated and untracked; the assembler is the tracked artifact.

Post-sitting plotdata for F3–F5 and T1–T3 are complete. Cell-level maps are I/O extracts. Mixed-spot coordinates are spatial-bin centroids in the same CosMx pixel frame as the cells. Rendering uses `to_um` without swapping axes and does not quantile-crop tissue. Manuscript rendering consumes these files only; no additional fits are run.
