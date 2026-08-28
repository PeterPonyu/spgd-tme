"""The back matter has to arrive in one piece.

The declarations are seven statements an editor checks in a single pass, and a
reference list is read by lookup. Both break if the float queue drains through
them or if one statement lands overleaf, and both breakages are invisible in the
source: the .tex is unchanged and only the page breaks move. These tests read the
built PDF, so they are skipped when it has not been compiled.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PDF = ROOT / "manuscript" / "main.pdf"

pytestmark = pytest.mark.skipif(
    not PDF.exists() or shutil.which("pdftotext") is None,
    reason="needs a compiled manuscript/main.pdf and pdftotext",
)

STATEMENTS = (
    "Data availability statement.",
    "Ethics statement.",
    "Author contributions.",
    "Funding.",
    "Acknowledgments.",
    "Conflict of interest.",
    "Generative AI statement.",
)


def _pages() -> list[str]:
    out = subprocess.run(
        ["pdftotext", "-layout", str(PDF), "-"], capture_output=True, text=True, check=True
    ).stdout
    return out.split("\f")


def test_every_declaration_lands_on_the_declarations_page():
    pages = _pages()
    hosts = [i for i, p in enumerate(pages) if "Declarations" in p]
    assert len(hosts) == 1, f"the Declarations heading appears on pages {hosts}"
    page = pages[hosts[0]]
    missing = [s for s in STATEMENTS if s not in page]
    assert missing == [], f"pushed off the declarations page: {missing}"


def test_no_figure_or_table_interrupts_the_back_matter():
    pages = _pages()
    start = next(i for i, p in enumerate(pages) if "Declarations" in p)
    for i, page in enumerate(pages[start:], start=start):
        stray = re.findall(r"(?:Figure|Table) \d+:", page)
        assert stray == [], f"page {i + 1} of the back matter carries {stray}"


def test_the_reference_list_runs_without_a_break():
    pages = _pages()
    start = next(i for i, p in enumerate(pages) if re.search(r"^\s*References\s*$", p, re.M))
    numbered = []
    for page in pages[start:]:
        numbered += [int(n) for n in re.findall(r"^\s*\[(\d+)\]", page, re.M)]
    assert numbered == list(range(1, len(numbered) + 1)), numbered
    assert numbered, "the reference list rendered no entries"
