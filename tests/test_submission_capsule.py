"""The submission capsule contract.

A capsule that has been split into section files, or that points at a figure the
portal will not accept, fails silently: it compiles here and is rejected there.
These tests read whatever `scripts/28_assemble_submission.py` last wrote and are
skipped when the capsule has not been built.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CAPSULE = ROOT / "submission"
TEX = CAPSULE / "manuscript.tex"
FIGURE_COUNT = 12

pytestmark = pytest.mark.skipif(
    not TEX.exists(), reason="capsule not built; run scripts/28_assemble_submission.py"
)


def _tex() -> str:
    return TEX.read_text()


def test_capsule_has_no_subdirectories():
    assert [p.name for p in CAPSULE.iterdir() if p.is_dir()] == []


def test_capsule_carries_exactly_one_tex():
    assert sorted(p.name for p in CAPSULE.glob("*.tex")) == ["manuscript.tex"]


def test_no_section_file_survived_as_an_include():
    assert "\\input{" not in _tex()


def test_every_figure_is_a_flat_jpeg_named_by_the_tex():
    named = re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", _tex())
    assert named == [f"Figure{n}.jpg" for n in range(1, FIGURE_COUNT + 1)]
    for name in named:
        assert (CAPSULE / name).exists(), f"{name} is referenced but not shipped"


def test_shipped_figures_are_jpeg_and_nothing_else():
    shipped = sorted(p.name for p in CAPSULE.iterdir() if p.suffix not in {".tex", ".pdf"})
    assert shipped == sorted(f"Figure{n}.jpg" for n in range(1, FIGURE_COUNT + 1))


def test_bibliography_is_inline_so_the_capsule_needs_no_bibtex():
    text = _tex()
    assert "\\bibliography{" not in text
    assert "\\bibliographystyle{" not in text
    assert "\\begin{thebibliography}" in text


def test_nothing_reaches_outside_the_capsule_directory():
    # A surviving path separator inside a braced argument is a reference to a
    # file the portal will not receive.
    for match in re.finditer(r"\\(includegraphics|input|include)(?:\[[^\]]*\])?\{([^}]+)\}", _tex()):
        assert "/" not in match.group(2), match.group(0)
