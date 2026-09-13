from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _shell_module():
    spec = importlib.util.spec_from_file_location(
        "check_manuscript_shell", ROOT / "scripts/check_manuscript_shell.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_manuscript_shell_contract():
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts/check_manuscript_shell.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout
    assert "MANUSCRIPT_SHELL_OK" in proc.stdout


def test_table_captions_read_above_and_figure_captions_below():
    check = _shell_module()._check_caption_placement
    body = (
        (ROOT / "manuscript/main.tex").read_text()
        + "\n"
        + (ROOT / "manuscript/results.tex").read_text()
    )
    check(body)
    flipped_table = (
        r"\begin{table}" "\n" r"\input{tables/T1_materials.tex}" "\n" r"\caption{x}" "\n" r"\end{table}"
    )
    flipped_figure = (
        r"\begin{figure}" "\n" r"\caption{x}" "\n" r"\includegraphics{a.pdf}" "\n" r"\end{figure}"
    )
    for bad in (flipped_table, flipped_figure):
        with pytest.raises(SystemExit):
            check(bad)


def test_main_tex_has_fail_closed_errmessage():
    main_tex = (ROOT / "manuscript/main.tex").read_text()
    assert "\\errmessage{FAIL-CLOSED:" in main_tex
    assert "RequireManuscriptFile" in main_tex
    assert "F3_t0_bootstrap.csv" in main_tex
    assert "F3_t0_fulln.csv" in main_tex
    for stem in ("F2_hero.pdf", "F3_cohort.pdf", "F11_floor.pdf"):
        assert f"IfFileExists{{figs/rendered/{stem}}}" not in main_tex


def test_reader_text_has_no_internal_ledger():
    names = [
        "abstract.tex",
        "intro.tex",
        "materials.tex",
        "methods.tex",
        "results.tex",
        "discussion.tex",
        "declarations.tex",
    ]
    blob = "\n".join((ROOT / "manuscript" / n).read_text().lower() for n in names)
    for cap in (ROOT / "manuscript/captions").glob("*.tex"):
        blob += "\n" + cap.read_text().lower()
    for tok in ("sha-256", "sha256", "crossdonor.csv", "realgt", "plotdata"):
        assert tok not in blob


def test_required_figures_are_directly_included():
    blob = (
        (ROOT / "manuscript/main.tex").read_text()
        + (ROOT / "manuscript/results.tex").read_text()
    )
    expected = (
        r"\includegraphics[width=\textwidth]{figs/rendered/F2_hero.pdf}",
        r"\includegraphics[width=\textwidth]{figs/rendered/F3_cohort.pdf}",
        r"\includegraphics[width=\textwidth]{figs/rendered/F4_ulcerated.pdf}",
        r"\includegraphics[width=\textwidth]{figs/rendered/F5_wound.pdf}",
        r"\includegraphics[width=\textwidth]{figs/rendered/F6_keep.pdf}",
        r"\includegraphics[width=\textwidth]{figs/rendered/F7_dose.pdf}",
        r"\includegraphics[width=\textwidth]{figs/rendered/F8_donor.pdf}",
        r"\includegraphics[width=\textwidth]{figs/rendered/F9_myeloid.pdf}",
        r"\includegraphics[width=\textwidth]{figs/rendered/F10_eval.pdf}",
        r"\includegraphics[width=\textwidth]{figs/rendered/F11_floor.pdf}",
        r"\includegraphics[width=\textwidth]{figs/rendered/F12_keep.pdf}",
    )
    for include in expected:
        assert include in blob
    assert blob.count("\\begin{figure}") == 15
    assert r"\input{figs/fig_pack.tex}" in blob


def test_f11_caption_only_claims_plotted_mean_and_floor_metadata():
    blob = (ROOT / "manuscript/captions/F11_floor.tex").read_text().lower()
    assert "mean spot occupancy" in blob
    assert "fifty reference cells" in blob
    # The panel plots the nonzero share, so the caption may name that; the
    # 0.05 shoulder in the same table is not drawn anywhere and must not leak.
    assert "below 0.05" not in blob
    assert "exactly empty" not in blob


def test_references_bib_exists():
    bib = (ROOT / "manuscript/references.bib").read_text()
    assert "Yerly" in bib
    assert "Schott" in bib
    assert "zenodo.14330691" in bib.lower() or "14330691" in bib

CAPTION_LEADS = {
    "F1_protocol.tex": "Two locked operators compute mixed-spot TME composition and decide when the tumor column is reportable.",
    "F2_spatial_maps.tex": "Four-patient CosMx basal-cell carcinoma is the mixed-spot TME object.",
    "F3_cohort.tex": "Four-patient cell-level fields give a clinically separable tissue.",
    "F4_ulcerated.tex": "Patient A is more stromal and Patient B is tumor-rich on the ulcerated-nodular pair.",
    "F5_wound.tex": "Tumor fraction falls and stromal and myeloid occupancy rise along the wound axis.",
    "F6_keep.tex": "The protocol reports CosMx tumor coordinates and places them beside locked tumor truth.",
    "F7_dose.tex": "The frozen cutoff \\(c^\\star=0.80\\) tracks malignant--neighbor collinearity as it is dialled up:",
    "F8_donor.tex": "Directed donor transfer recovers composition across patients.",
    "F9_myeloid.tex": "MoMacDC is an occupancy axis on the computed pairs.",
    "F10_eval.tex": "The evaluation board collects the interval, the full-n confirmation, donor RMSE, and the timed pass.",
    "F11_floor.tex": "Every reported type clears the builder floor of fifty reference cells, and occupancy on that supported simplex is concentrated in one column.",
    "F12_keep.tex": "The same frozen cosine reports KEEP on independent CosMx carcinomas.",
}

REQUIRED_BIB_KEYS = (
    "Lopez2022",
    "Ma2022",
    "Biancalani2021",
    "Danaher2022",
    "Li2022integrate",
    "Sangaram2024",
    "Dvorak1986",
    "Gavish2023",
)

DEFENSIVE_PHRASES = (
    "this sitting",
    "we did not",
    "we do not evaluate",
    "was not evaluated",
    "not evaluated",
    "not reported",
    "we lack",
    "highest error",
    "incomplete",
    "unavailable",
    "only one keep",
    "we have not",
    "we cannot",
    "we failed",
)


def test_caption_leads_are_contribution_first():
    for name, lead in CAPTION_LEADS.items():
        blob = (ROOT / "manuscript/captions" / name).read_text().strip()
        assert blob.startswith(lead), name


def test_captions_and_abstract_have_no_structural_ref():
    blobs = [(ROOT / "manuscript/abstract.tex").read_text()]
    for cap in (ROOT / "manuscript/captions").glob("*.tex"):
        blobs.append(cap.read_text())
    for blob in blobs:
        low = blob.lower()
        assert r"\ref{" not in blob
        assert r"\pageref{" not in blob
        assert "see figure" not in low
        assert "see table" not in low
        assert "see section" not in low
        assert "see panel" not in low
        assert "as in (" not in low
        assert "as shown in figure" not in low
        assert "as shown in table" not in low
        assert "figure~" not in low
        assert "table~" not in low
        assert "section~" not in low
        assert "grey squares in a--" not in low


def test_official_captions_spell_each_panel():
    for name in CAPTION_LEADS:
        blob = (ROOT / "manuscript/captions" / name).read_text()
        for letter in "ABCDEF":
            assert f"({letter})~" in blob, (name, letter)
        assert "(A--" not in blob and "(D--" not in blob, name


def test_bib_has_contribution_neighborhood():
    bib = (ROOT / "manuscript/references.bib").read_text()
    for key in REQUIRED_BIB_KEYS:
        assert f"@{key}" in bib or f"{{{key}," in bib, key


def test_intro_cites_method_neighborhood():
    intro = (ROOT / "manuscript/intro.tex").read_text()
    assert "Lopez2022" in intro or "Ma2022" in intro
    assert "Danaher2022" in intro or "Li2022integrate" in intro
    assert "Dvorak1986" in intro or "Gavish2023" in intro


def test_abstract_opens_with_operators():
    first = (ROOT / "manuscript/abstract.tex").read_text().strip().split(".")[0]
    assert "two locked operators" in first.lower()


def test_discussion_ends_with_short_scope():
    raw = (ROOT / "manuscript/discussion.tex").read_text()
    paras = [p.strip() for p in raw.split("\n\n") if p.strip()]
    last = paras[-1]
    n_lines = last.count("\n") + 1
    assert n_lines <= 12
    import re
    assert len(re.findall(r"(?<!\d)\.(?!\d)", last)) <= 4
    low = last.lower()
    assert "cosmx" in low
    assert "c-from-d" in low or "materials ledger" in low
    assert "methods object" in low
    body_before = "\n\n".join(paras[:-1]).lower()
    for tok in DEFENSIVE_PHRASES:
        assert tok not in body_before, tok


def test_spatial_geom_keeps_native_axes():
    theme = (ROOT / "manuscript/scripts/R/theme_tme.R").read_text()
    geom = (ROOT / "manuscript/scripts/R/spatial_geom.R").read_text()
    metric = (ROOT / "manuscript/scripts/R/render_metric_faces.R").read_text()
    spatial = (ROOT / "manuscript/scripts/R/render_spatial_faces.R").read_text()
    orchestrator = (ROOT / "manuscript/scripts/R/render_disk_faces.R").read_text()
    blob = theme + geom + metric + spatial + orchestrator
    assert "if (yr > xr)" not in blob
    assert "crop_dense" not in blob
    assert "coord_fixed" not in blob
    assert "to_um" in theme
    assert "fov_rectangles" in geom
    assert "spot_on_tissue" in geom
    assert "fill_axes" in geom
    assert "pack_layout" in geom
    assert "row_fill" in geom
    assert "source" in orchestrator and "spatial_geom.R" in orchestrator


def test_rendered_faces_relabel_internal_identifiers():
    """Axis labels are reader-facing, so the renderer must map code names."""
    theme = (ROOT / "manuscript/scripts/R/theme_tme.R").read_text()
    metric = (ROOT / "manuscript/scripts/R/render_metric_faces.R").read_text()
    for internal, shown in (
        ("extract_signature", "Signature extraction"),
        ("specificity_weight", "Specificity weights"),
        ("fit_gamma", "Weighted fit"),
        ("self_gate", "Platform self-gate"),
        ("refuse", "Reportability gate"),
        ("poisson_fit", "Poisson close"),
    ):
        assert f'"{internal}" = "{shown}"' in theme, internal
    for internal, shown in (
        ("realgt2", "Xenium FLEX"),
        ("realgt3", "CosMx"),
    ):
        assert shown in theme, internal
    assert "pretty_step(timing$step)" in metric
    assert "factor(timing$step, levels = timing$step)" not in metric


def test_reader_body_has_no_defensive_voice():
    names = [
        "abstract.tex",
        "intro.tex",
        "materials.tex",
        "methods.tex",
        "results.tex",
        "discussion.tex",
    ]
    blob = "\n".join((ROOT / "manuscript" / n).read_text().lower() for n in names)
    for name in CAPTION_LEADS:
        blob += "\n" + (ROOT / "manuscript/captions" / name).read_text().lower()
    for tok in DEFENSIVE_PHRASES:
        assert tok not in blob, tok
