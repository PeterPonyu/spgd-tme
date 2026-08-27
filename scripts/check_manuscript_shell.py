#!/usr/bin/env python
"""Manuscript shell contract. Does not compile the PDF and does not fit SPGD."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MS = ROOT / "manuscript"
REQUIRED_CAPTIONS = (
    "F1_protocol.tex",
    "F2_spatial_maps.tex",
    "F3_cohort.tex",
    "F4_ulcerated.tex",
    "F5_wound.tex",
    "F6_keep.tex",
    "F7_dose.tex",
    "F8_donor.tex",
    "F9_myeloid.tex",
    "F10_eval.tex",
    "F11_floor.tex",
    "F12_keep.tex",
    "T1_materials.tex",
    "T2_timing.tex",
    "T3_donor_matrix.tex",
)
REQUIRED_EVIDENCE = (
    "F2_pair_cards.csv",
    "F2_truth_mass.csv",
    "F2_native_refuse.csv",
    "F2_realgt2_cosine.csv",
    "F2_donor_edges.csv",
    "F2D_A_from_B_truth_maps.csv",
    "F2D_B_from_A_truth_maps.csv",
    "F9_D_from_C_truth_maps.csv",
    "F4_keep_spatial_fulln_compare.csv",
    "cells_spatial.csv.gz",
    "F3_collinearity_sweep.csv",
    "F3_t0_bootstrap.csv",
    "F3_t0_fulln.csv",
    "F4_refusal.csv",
    "F5_donor_transfer.csv",
    "F9_type_floor.csv",
    "F9_condition_occupancy.csv",
    "F9_condition_spot_truth.csv",
    "F10_myeloid_occupancy.csv",
    "F4_keep_spatial.csv",
    "F4_keep_spatial_summary.csv",
    "F4_keep_spatial_fulln.csv",
    "F4_keep_spatial_fulln_summary.csv",
    "F2_condition_cell_summary.csv",
    "T1_materials.csv",
    "T2_timing.csv",
    "T3_donor_matrix.csv",
    "F12_keep_cosine.csv",
    "F12_donor_rmse.csv",
)
REQUIRED_RENDERED = (
    "F2_hero.pdf",
    "F3_cohort.pdf",
    "F4_ulcerated.pdf",
    "F5_wound.pdf",
    "F6_keep.pdf",
    "F7_dose.pdf",
    "F8_donor.pdf",
    "F9_myeloid.pdf",
    "F10_eval.pdf",
    "F11_floor.pdf",
    "F12_keep.pdf",
)
REQUIRED_DIRECT_INCLUDES = {
    "F2_hero.pdf": r"\includegraphics[width=\textwidth]{figs/rendered/F2_hero.pdf}",
    "F3_cohort.pdf": r"\includegraphics[width=\textwidth]{figs/rendered/F3_cohort.pdf}",
    "F11_floor.pdf": r"\includegraphics[width=\textwidth]{figs/rendered/F11_floor.pdf}",
    "F12_keep.pdf": r"\includegraphics[width=\textwidth]{figs/rendered/F12_keep.pdf}",
}
BANNED = ("survival", "biomarker", "0.2034", "0.1126")
# Every .tex a reader receives. declarations.tex was outside this list when it
# was added and reached the PDF claiming a SHA-256 column Table 1 does not print.
PROSE_FILES = (
    "abstract.tex",
    "intro.tex",
    "materials.tex",
    "methods.tex",
    "results.tex",
    "discussion.tex",
    "declarations.tex",
)
READER_LEAKS = (
    "sha-256",
    "sha256",
    "crossdonor.csv",
    "realgt",
    "plotdata",
    "run_tissue_name",
)
LOCAL_PATH_MARKERS = ("/home/", "desktop/labs", "file://")


def main() -> None:
    main_tex = (MS / "main.tex").read_text()
    results_tex = (MS / "results.tex").read_text()
    body = main_tex + "\n" + results_tex
    if "FAIL-CLOSED" not in main_tex or "RequireManuscriptFile" not in main_tex:
        raise SystemExit("main.tex missing fail-closed manuscript-file gate")
    for stem, include in REQUIRED_DIRECT_INCLUDES.items():
        silent = f"IfFileExists{{figs/rendered/{stem}}}"
        if silent in body:
            raise SystemExit(f"main.tex still has a silent empty fallback for {stem}")
        if include not in body:
            raise SystemExit(f"main.tex missing direct include for {stem}")
    for name in REQUIRED_EVIDENCE:
        if name not in main_tex:
            raise SystemExit(f"main.tex does not require {name}")
        path = ROOT / "data" / "plotdata" / name
        if not path.is_file() or path.stat().st_size == 0:
            raise SystemExit(f"missing evidence {path}")
    for name in REQUIRED_RENDERED:
        if name not in main_tex:
            raise SystemExit(f"main.tex does not require {name}")
        path = MS / "figs" / "rendered" / name
        if not path.is_file() or path.stat().st_size == 0:
            raise SystemExit(f"missing rendered {path}")
    for name in REQUIRED_CAPTIONS:
        path = MS / "captions" / name
        if not path.is_file():
            raise SystemExit(f"missing caption {path}")
        blob = path.read_text().lower()
        for tok in BANNED:
            if tok in blob:
                raise SystemExit(f"banned token {tok} in {path}")
        for tok in READER_LEAKS:
            if tok in blob:
                raise SystemExit(f"reader leak {tok} in {path}")
    theme = MS / "scripts/R/theme_tme.R"
    if not theme.is_file() or "theme_tme" not in theme.read_text():
        raise SystemExit("missing theme_tme")
    if not (MS / "scripts/R/render_disk_faces.R").is_file():
        raise SystemExit("missing render_disk_faces.R")
    if not (MS / "scripts/R/spatial_geom.R").is_file():
        raise SystemExit("missing spatial_geom.R")
    if not (MS / "figs/fig_pack.tex").is_file():
        raise SystemExit("missing merged protocol figure")
    if r"\input{figs/fig_pack.tex}" not in body:
        raise SystemExit("manuscript missing merged fig_pack.tex")
    contract = ROOT / "FIGURES.md"
    if not contract.is_file() or "11 data figures + 3 tables" not in contract.read_text():
        raise SystemExit("missing 11+3 figure contract")
    n_fig = body.count("\\begin{figure}")
    if n_fig != 12:
        raise SystemExit(f"manuscript must contain exactly 12 numbered figures, found {n_fig}")
    if "\\textbf{Schematic.}" in main_tex:
        raise SystemExit("main.tex still uses unnumbered Schematic")
    publication_text = "\n".join(
        [main_tex, contract.read_text()]
        + [(MS / name).read_text() for name in PROSE_FILES]
        + [(MS / "captions" / name).read_text() for name in REQUIRED_CAPTIONS]
    ).lower()
    for marker in LOCAL_PATH_MARKERS:
        if marker in publication_text:
            raise SystemExit(f"local path leakage in publication text: {marker}")
    for tok in BANNED:
        if tok in publication_text:
            raise SystemExit(f"banned token {tok} in publication text")
    reader_body = "\n".join(
        [(MS / name).read_text() for name in PROSE_FILES]
        + [(MS / "captions" / name).read_text() for name in REQUIRED_CAPTIONS]
        + [(MS / "tables" / name).read_text() for name in ("T1_materials.tex", "T2_timing.tex", "T3_donor_matrix.tex")]
    ).lower()
    for tok in READER_LEAKS:
        if tok in reader_body:
            raise SystemExit(f"reader leak {tok} in publication body")
    if not (MS / "references.bib").is_file():
        raise SystemExit("missing references.bib")
    print("MANUSCRIPT_SHELL_OK")


if __name__ == "__main__":
    main()
