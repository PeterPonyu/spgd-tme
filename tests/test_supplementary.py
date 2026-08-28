"""The Data availability statement is only true if the bundle it names is built."""
from __future__ import annotations

import importlib.util
import sys
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
