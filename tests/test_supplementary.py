"""The Data availability statement is only true if the bundle it names is built."""
from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "manuscript" / "scripts"))
sys.path.insert(0, str(ROOT / "scripts"))

_spec = importlib.util.spec_from_file_location("assemble_supp", ROOT / "scripts" / "29_assemble_supplementary.py")
supp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(supp)

from check_manuscript_shell import REQUIRED_EVIDENCE  # noqa: E402


def test_every_required_evidence_file_has_a_bundle_name():
    for name in REQUIRED_EVIDENCE:
        assert (supp.PLOTDATA / name).is_file(), name
        assert name not in supp.PLOTDATA_WITHHELD, name


def test_public_name_leaves_no_substrate_codename():
    for name in (p.name for p in supp.PLOTDATA.iterdir()):
        assert "realgt" not in supp.public_name(name)
        assert "crossdonor" not in supp.public_name(name)


def test_forbidden_list_covers_the_paths_and_codenames_that_leaked():
    for token in ("/home/", "desktop/labs", "deconv-lab", "spgd-deconv", "realgt"):
        assert token in supp.FORBIDDEN, token


def test_provenance_strip_removes_machine_directories_at_any_depth():
    node = {"keep": 1, "out_dir": "/somewhere", "rows": [{"pair_dir": "/x", "n": 2}]}
    assert supp.strip_provenance(node) == {"keep": 1, "rows": [{"n": 2}]}


def test_declaration_promises_only_what_the_bundle_carries():
    """The statement claimed the reference matrices travel; they are 118-481 MB
    and licensed by their depositors, so it now promises their digest instead."""
    text = (ROOT / "manuscript" / "declarations.tex").read_text()
    assert "locked reference matrices, the plotted" not in text
    assert "identified in that bundle by digest rather than redistributed" in text


def test_every_binding_the_bundle_rewrites_is_still_in_the_source():
    """The rewrite is a string match against scripts that are edited elsewhere.
    A binding that moves silently ships a script that stops on its first line, so
    the match is asserted here rather than discovered by a reviewer."""
    for name, rebind in supp.R_ENTRY.items():
        body = (supp.RENDER / "R" / name).read_text()
        for old, _ in rebind:
            assert old in body, f"{name} no longer binds {old!r}"
    body = (supp.RENDER / "generate_tables.py").read_text()
    for old, _ in supp.PY_REBIND:
        assert old in body, f"generate_tables.py no longer binds {old!r}"


def test_bundled_entry_points_read_the_bundle_and_not_the_workbench():
    bundle = ROOT / "supplementary"
    if not bundle.is_dir():
        return
    for name in supp.R_ENTRY:
        body = (bundle / "render" / name).read_text()
        assert "FIGURES.md" not in body
        assert 'file.path(root, "plotdata")' in body
        assert 'file.path(root, "figures")' in body
        assert "manuscript/scripts/R/" not in body


def test_readme_names_only_commands_the_bundle_can_run():
    """Two entry points draw the figures, not one: render_disk_faces.R stops at
    Figure 11 and render_F12_keep.R draws the twelfth. The README said one command
    covered 2-12, which is the kind of claim a reviewer tests first."""
    assert "Figures 2-11" in supp.README
    assert "render/render_F12_keep.R" in supp.README
    assert "Figures 2-12" not in supp.README
    assert "TikZ picture" not in supp.README
    assert "Figure1.jpg" in supp.README
    assert "render/render_F13.py" in supp.README
    assert "render/render_F14.py" in supp.README
    assert "render/render_F15.py" in supp.README
    assert "T4_gate_calls.tex" in supp.README
    bundle = ROOT / "supplementary"
    if bundle.is_dir():
        for script in ("render_disk_faces.R", "render_F12_keep.R", "generate_tables.py",
                       "render_F13.py", "render_F14.py", "render_F15.py"):
            assert (bundle / "render" / script).is_file(), script
        assert (bundle / "tables" / "T4_gate_calls.tex").is_file()


def test_index_does_not_call_an_emit_stage_a_figure_number():
    """The emit stages were numbered before the figures were renumbered, so
    F9_type_floor.csv prints as Figure 11. Heading it "Figure 9" sent a reader
    checking one panel to another panel's tables."""
    lines = supp.index_lines([supp.PLOTDATA / "F9_type_floor.csv", supp.PLOTDATA / "T1_materials.csv"])
    assert any(line.strip() == "Emit stage F9" for line in lines)
    assert not any(line.strip() == "Figure 9" for line in lines)
    assert any(line.strip() == "Table 1" for line in lines)


def test_revision_audit_tables_ship_with_the_bundle():
    """R2-P3 names the lock specification and R2-P14 the complete pair scan as
    Supplementary evidence. Both must be configured to ship, whatever plotdata
    happens to contain, or the letters point at files a reviewer cannot open."""
    assert "analyses/" in supp.README
    for src_rel, _ in supp.ANALYSES_EXTRA:
        assert (supp.REVISION / src_rel).is_file(), src_rel
    names = {dst for _, dst in supp.ANALYSES_EXTRA}
    for required in (
        "perturbation_summary.csv",
        "summary_metrics.csv",
        "stratified_metrics.csv",
        "conditional_rmse_fulln.json",
        "conditional_rmse_fulln.csv",
    ):
        assert required in names, required
    for src_name, _ in supp.FIGURE_PY:
        assert (supp.REVISION / src_name).is_file(), src_name


def test_unpacked_bundle_carries_documented_figure_and_table_inputs():
    """Acceptance is unpack-in-empty-dir, not 'four extra scripts exist'."""
    archive = ROOT / "supplementary.zip"
    if not archive.is_file():
        return
    with tempfile.TemporaryDirectory() as tmp:
        dest = Path(tmp)
        with zipfile.ZipFile(archive) as zf:
            zf.extractall(dest)
        for rel in (
            "render/render_disk_faces.R",
            "render/render_F12_keep.R",
            "render/render_F13.py",
            "render/render_F14.py",
            "render/render_F15.py",
            "render/generate_tables.py",
            "tables/T4_gate_calls.tex",
            "analyses/perturbation_summary.csv",
            "analyses/summary_metrics.csv",
            "analyses/stratified_metrics.csv",
            "analyses/conditional_rmse_fulln.json",
            "plotdata/T1_materials.csv",
            "plotdata/T2_timing.csv",
            "plotdata/T3_donor_matrix.csv",
        ):
            assert (dest / rel).is_file(), rel
        py = sys.executable
        for script, expected in (
            ("render/render_F13.py", "F13_revision_audit.pdf"),
            ("render/render_F14.py", "F14_revision_support.pdf"),
            ("render/render_F15.py", "F15_v3_fulln_comparator.pdf"),
            ("render/generate_tables.py", None),
        ):
            subprocess.run([py, str(dest / script)], check=True, cwd=dest)
            if expected:
                assert (dest / "figures" / expected).is_file(), expected
        assert (dest / "tables" / "T1_materials.tex").is_file()
        assert (dest / "tables" / "T2_timing.tex").is_file()
        assert (dest / "tables" / "T3_donor_matrix.tex").is_file()
