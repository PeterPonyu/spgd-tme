"""What the author guidelines require of the page, not of the science.

Four of these are desk-check items rather than review items: a manuscript that
fails them is returned before an editor reads it, and none of them are visible
in the prose. They are checked against the built PDF, so they are skipped when
it has not been compiled.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MS = ROOT / "manuscript"
PDF = MS / "main.pdf"

pytestmark = pytest.mark.skipif(
    not PDF.exists() or shutil.which("pdftotext") is None,
    reason="needs a compiled manuscript/main.pdf and pdftotext",
)

# The body carries fourteen display equations and eight closed intervals; only
# the intervals reach the text as a bracketed pair of numbers, so anything else
# in brackets is a citation that survived the move off numeric references.
INTERVALS = {"[0, 1]", "[0,1]"}
BRACKETED_NUMBERS = re.compile(r"\[\s*\d[\d,\s\u2013-]*\]")
# Frontiers prescribes this order for a Methods article. The headings the paper
# used before were descriptive, mapped onto the order one for one, and matched
# none of the required names.
REQUIRED_SECTIONS = (
    "Introduction",
    "Materials and Equipment",
    "Methods",
    "Results",
    "Discussion",
)
WORD_COUNT_SOURCES = ("intro.tex", "materials.tex", "methods.tex", "results.tex", "discussion.tex")


def _text() -> str:
    return subprocess.run(
        ["pdftotext", "-layout", str(PDF), "-"], capture_output=True, text=True, check=True
    ).stdout


def test_the_manuscript_carries_line_numbers():
    # "must contain page and line numbers in order to facilitate the review
    # process". Page numbers come with the class; line numbers do not.
    #
    # Tables print numbers at the start of a line too, so the gutter is not
    # read off a column. It is the unbroken run 1..n, which only a numbered
    # margin produces: a missing number breaks the run at that line.
    source = (MS / "main.tex").read_text()
    assert "\\usepackage{lineno}" in source and "\\linenumbers" in source
    starts = {int(n) for n in re.findall(r"^\s*(\d+)\s", _text(), re.M)}
    run = 0
    while run + 1 in starts:
        run += 1
    assert run > 400, f"the line-number gutter runs 1..{run}"


def test_citations_are_author_year_rather_than_bracketed_numbers():
    # Square brackets are reserved for the physics and mathematics titles; the
    # journal's own published articles carry (Author, Year) against an
    # alphabetical list.
    stray = set(BRACKETED_NUMBERS.findall(_text())) - INTERVALS
    assert stray == set(), f"numeric citations survived: {sorted(stray)}"
    assert re.search(r"\([A-Z][^()]{2,40}, (19|20)\d\d[a-z]?\)", _text()), "no author-year citation"


def test_the_first_page_states_the_word_and_float_counts():
    # "Please indicate the number of words and the number of figures and tables
    # included in your manuscript on the first page."
    first = _text().split("\f")[0]
    stated = re.search(
        r"Word count \(main text\):\s*([\d,]+)\s+Figures:\s*(\d+)\s+Tables:\s*(\d+)", first
    )
    assert stated, "the first page does not state the word, figure and table counts"
    words, figures, tables = (int(g.replace(",", "")) for g in stated.groups())
    assert (figures, tables) == (15, 3), f"stated {figures} figures and {tables} tables"
    assert words <= 12000, f"stated {words} words against a 12,000 limit"

    if shutil.which("texcount") is None:
        pytest.skip("texcount is not installed, so the stated count cannot be re-derived")
    counted = subprocess.run(
        ["texcount", "-1", "-sum", "-merge", *WORD_COUNT_SOURCES],
        cwd=MS, capture_output=True, text=True, check=True,
    ).stdout.strip()
    assert words == int(counted), f"the first page states {words}, the body counts {counted}"


def test_the_section_headings_follow_the_methods_format():
    headings = re.findall(r"^\s*\d+\s+(\d)\s{2,}([A-Z][A-Za-z ]+?)\s*$", _text(), re.M)
    assert [name for _, name in headings] == list(REQUIRED_SECTIONS), headings
    assert [n for n, _ in headings] == [str(i) for i in range(1, len(REQUIRED_SECTIONS) + 1)]
