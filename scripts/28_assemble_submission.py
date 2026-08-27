#!/usr/bin/env python
"""Assemble the flat submission capsule from the sectioned manuscript.

The editing copy is split across section, caption and table files and draws its
figures from ``manuscript/figs``. A submission capsule may not be: it is one
directory with no subdirectories, one ``.tex``, and ``FigureN.jpg`` raster
figures that the ``.tex`` names explicitly.

Run from anywhere:

    python scripts/28_assemble_submission.py
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "manuscript"
RENDERED = MANUSCRIPT / "figs" / "rendered"
OUT = ROOT / "submission"

# Submission figure number -> source. Figure 1 is a TikZ picture in the editing
# copy, so it is compiled to a page of its own before rasterising.
TIKZ_SOURCE = MANUSCRIPT / "figs" / "fig_pack.tex"
FIGURES: dict[int, str] = {
    2: "F2_hero",
    3: "F3_cohort",
    4: "F4_ulcerated",
    5: "F5_wound",
    6: "F6_keep",
    7: "F7_dose",
    8: "F8_donor",
    9: "F9_myeloid",
    10: "F10_eval",
    11: "F11_floor",
    12: "F12_keep",
}
FIGURE_DPI = 300

INPUT_RE = re.compile(r"(?:\\protect\s*)?\\input\{([^}]+)\}")
GRAPHICS_RE = re.compile(r"\\includegraphics(\[[^\]]*\])?\{figs/rendered/([A-Za-z0-9_]+)\.pdf\}")


def run(cmd: list[str], cwd: Path) -> None:
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if proc.returncode != 0:
        sys.exit(f"FAIL: {' '.join(cmd)}\n{proc.stdout[-3000:]}\n{proc.stderr[-2000:]}")


def render_protocol_pdf(work: Path) -> Path:
    """Compile the TikZ protocol panel to a tightly cropped one-page PDF."""
    body = TIKZ_SOURCE.read_text()
    standalone = work / "Figure1.tex"
    standalone.write_text(
        "\\documentclass[border=2pt]{standalone}\n"
        "\\usepackage{amsmath}\n"
        "\\usepackage{tikz}\n"
        "\\usetikzlibrary{arrows.meta,positioning,calc,fit}\n"
        "\\begin{document}\n"
        f"{body}\n"
        "\\end{document}\n"
    )
    run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "Figure1.tex"], work)
    return work / "Figure1.pdf"


def rasterise(pdf: Path, dest: Path) -> None:
    """pdftoppm writes <prefix>-1.jpg; there is only ever one page here."""
    prefix = dest.with_suffix("")
    run(
        ["pdftoppm", "-jpeg", "-r", str(FIGURE_DPI), "-jpegopt", "quality=92",
         "-singlefile", str(pdf), str(prefix)],
        dest.parent,
    )
    if not dest.exists():
        sys.exit(f"FAIL: {dest.name} was not produced from {pdf}")


def inline_inputs(text: str, base: Path, depth: int = 0) -> str:
    """Splice every \\input target into the text it was called from."""
    if depth > 8:
        sys.exit("FAIL: \\input nesting deeper than eight levels")

    def repl(match: re.Match[str]) -> str:
        target = match.group(1)
        path = base / target
        if not path.suffix:
            path = path.with_suffix(".tex")
        if not path.exists():
            sys.exit(f"FAIL: missing \\input target {path}")
        return inline_inputs(path.read_text().rstrip("\n"), base, depth + 1)

    return INPUT_RE.sub(repl, text)


def flatten(bbl: str) -> str:
    text = (MANUSCRIPT / "main.tex").read_text()

    # The guard block names editing-copy paths. Re-point it at the capsule's own
    # figures so the submission build stays fail-closed on missing evidence.
    text = re.sub(r"\\RequireManuscriptFile\{[^}]*\}\n", "", text)
    guards = "".join(f"\\RequireManuscriptFile{{Figure{n}.jpg}}\n" for n in range(1, 13))
    text = text.replace(
        "% Missing evidence must stop the build. No placeholder figures or tables.",
        "% Missing evidence must stop the build. No placeholder figures or tables.",
    )
    text = text.replace("\\begin{document}", guards + "\n\\begin{document}", 1)

    # Figure 1 ships as a raster like every other figure, so the picture is
    # replaced before the TikZ source could be spliced in, and TikZ itself stops
    # being a dependency the capsule build has to satisfy.
    text = text.replace(
        "\\input{figs/fig_pack.tex}",
        "\\includegraphics[width=\\textwidth]{Figure1.jpg}",
    )
    text = re.sub(r"\\usepackage\{tikz\}\n\\usetikzlibrary\{[^}]*\}\n", "", text)
    if "tikz" in text:
        sys.exit("FAIL: TikZ survived into a capsule whose figures are all raster")
    # Graphics are renamed after splicing: the calls live in the section files.
    text = GRAPHICS_RE.sub(_graphics_repl, inline_inputs(text, MANUSCRIPT))

    # A capsule must compile without bibtex, so the resolved list replaces the
    # \bibliography call. references.bib stays in the editing copy.
    # A callable replacement: the .bbl is full of backslashes that re would
    # otherwise read as escapes in the replacement string.
    text, swapped = re.subn(
        r"\\bibliographystyle\{[^}]*\}\s*\n\\bibliography\{[^}]*\}",
        lambda _: bbl.strip(),
        text,
    )
    if swapped != 1:
        sys.exit(f"FAIL: expected one \\bibliography call, replaced {swapped}")

    leftover = INPUT_RE.search(text) or GRAPHICS_RE.search(text)
    if leftover:
        sys.exit(f"FAIL: unresolved reference {leftover.group(0)}")
    return strip_comments(text)


def strip_comments(text: str) -> str:
    """Drop whole-line comments from the capsule source.

    The editing copy explains every typesetting decision to whoever edits it
    next. An editor opening the submitted source is not that reader, and the
    notes name the target journal and the reasoning behind page breaks. TeX
    discards a whole-line comment together with its newline, so removing the
    line is typographically identical. Trailing comments are left alone: a
    line-final % suppresses a space and is load-bearing.
    """
    kept = [ln for ln in text.split("\n") if not ln.lstrip().startswith("%")]
    return "\n".join(kept)


def _graphics_repl(match: re.Match[str]) -> str:
    opts, stem = match.group(1) or "", match.group(2)
    number = next((n for n, s in FIGURES.items() if s == stem), None)
    if number is None:
        sys.exit(f"FAIL: {stem} has no submission figure number")
    return f"\\includegraphics{opts}{{Figure{number}.jpg}}"


def main() -> None:
    bbl_path = MANUSCRIPT / "main.bbl"
    if not bbl_path.exists():
        sys.exit("FAIL: build the editing copy first; main.bbl is missing")

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    work = OUT / "_work"
    work.mkdir()

    rasterise(render_protocol_pdf(work), OUT / "Figure1.jpg")
    for number, stem in sorted(FIGURES.items()):
        source = RENDERED / f"{stem}.pdf"
        if not source.exists():
            sys.exit(f"FAIL: render the figures first; {source} is missing")
        rasterise(source, OUT / f"Figure{number}.jpg")

    (OUT / "manuscript.tex").write_text(flatten(bbl_path.read_text()))
    shutil.rmtree(work)

    run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "manuscript.tex"], OUT)
    run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "manuscript.tex"], OUT)
    for junk in ("manuscript.aux", "manuscript.log", "manuscript.out"):
        (OUT / junk).unlink(missing_ok=True)

    strays = sorted(p.name for p in OUT.iterdir() if p.is_dir())
    if strays:
        sys.exit(f"FAIL: capsule must be flat, found directories {strays}")
    print(f"wrote {OUT.relative_to(ROOT)}/ with {len(list(OUT.iterdir()))} flat files")


if __name__ == "__main__":
    main()
