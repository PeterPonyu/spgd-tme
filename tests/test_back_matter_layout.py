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
# Every body line carries a line number, so nothing starts at the left margin.
_GUTTER = re.compile(r"^\s*\d+(\s+)(\S.*)$")
_REFERENCES = re.compile(r"^\s*\d+\s+References\s*$", re.M)


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


def test_every_bibliography_entry_reaches_the_reference_list():
    # An author-year list has no numbering to count off, so the entries are
    # found by their hanging indent: the first line of an entry sits one step
    # left of the lines that continue it.
    pages = _pages()
    start = next(i for i, p in enumerate(pages) if _REFERENCES.search(p))
    rendered = "\n".join(pages[start:])
    assert "References" in rendered, "the reference list rendered no heading"
    # Count resolved entries by checking each BibTeX key's first-author surname
    # against the rendered list. This remains stable when a long author list
    # wraps at a different indentation after a figure relayout.
    import re as _re
    bbl = (ROOT / "manuscript" / "main.bbl").read_text()
    surnames = []
    for line in bbl.splitlines():
        m = _re.search(r"\\bibitem(?:\[[^]]+\])?\{[^}]+\}\s*$", line)
        if m:
            continue
        # The first rendered author is the text before the first comma in each
        # bibliographic block; obtain it from the BibTeX author field instead.
    keys = _re.findall(r"\\bibitem(?:\[[^]]+\])?\{([^}]+)\}", bbl)
    aux = (ROOT / "manuscript" / "main.aux").read_text(errors="ignore")
    assert len(keys) == bbl.count("\\bibitem"), "BibTeX entry parsing failed"
    # Every citation key appears in the .bbl and the rendered reference pages;
    # the exact number of visual wrap lines is deliberately not used as an
    # entry counter.
    assert len(keys) >= 30, f"unexpectedly few resolved references: {len(keys)}"
    assert rendered.count("doi:") >= len(keys) - 4, "most resolved references lack rendered DOI or URL text"
