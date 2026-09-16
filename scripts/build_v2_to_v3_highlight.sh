#!/usr/bin/env bash
# Build the V2-to-V3 highlight PDF.
#
# latexdiff --flatten leaves three defects that stop pdflatex on this manuscript, so they are
# repaired here rather than by hand on each rebuild:
#   - \protect glued to inlined caption text        -> \protectMaterials
#   - \hskip0pt followed by the word "plus"         -> parsed as glue syntax
#   - \DIFadd markup inserted inside \csname        -> unterminated csname
# --disable-citation-markup stops latexdiff wrapping each \cite in an unbreakable \mbox; a
# citation-dense deleted paragraph otherwise overruns the text block (a >1000pt overfull line
# that clips off the page). Citations then break normally; only their own add/del colour is
# dropped, while the surrounding prose keeps its highlight.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MS="$ROOT/manuscript"
OLD_REF="${1:-v2-public-release}"
OLD_DIR="$(mktemp -d)"
trap 'rm -rf "$OLD_DIR"' EXIT

git -C "$ROOT" archive "$OLD_REF" manuscript | tar -x -C "$OLD_DIR"

cd "$MS"
latexdiff --flatten --disable-citation-markup "$OLD_DIR/manuscript/main.tex" main.tex > main_diff_V2_to_V3.tex
# A clean flattened copy of the current manuscript: identical inputs leave the
# body unmarked, so this supplies each table in its revised form.
latexdiff --flatten --disable-citation-markup main.tex main.tex > main_diff_new_flat.tex

sed -i 's/\\protect\([A-Za-z]\)/\\protect \1/g' main_diff_V2_to_V3.tex
sed -i 's/\\hskip0pt%DIFAUXCMD/\\hskip0pt\\relax%DIFAUXCMD/g' main_diff_V2_to_V3.tex
sed -i 's/\\csname \\DIFadd{\([A-Za-z]*\)}\\endcsname/\\csname \1\\endcsname/g' main_diff_V2_to_V3.tex
# Bibliographies are generated output, not a manuscript change.  Replace the
# flattened added bibliography with the current bbl so unchanged references stay black.
# latexdiff lengthens the Discussion, so the journal \clearpage would leave two
# leftover lines alone on the next page. Keep the float drain; drop the page
# break so Declarations continue on that page instead of after a white gap.
python - <<'PY2'
import re
from pathlib import Path
d=Path("main_diff_V2_to_V3.tex"); b=Path("main.bbl")
s=d.read_text(); bb=b.read_text()

# latexdiff marks up table cells, and when it deletes a whole row it comments
# out that row's terminating \\ along with the row.  The next \midrule then
# lands inside an unfinished row and TeX stops on "Misplaced \noalign".  The
# markup is not worth the breakage: a table's revision is legible from the table
# itself, so each tabular is restored to its current form and the surrounding
# prose keeps its highlight.
TABULAR = re.compile(r"\\begin\{tabular\}.*?\\end\{tabular\}", re.S)
clean = TABULAR.findall(Path("main_diff_new_flat.tex").read_text())
marked = TABULAR.findall(s)
if len(clean) != len(marked):
    raise SystemExit(f"tabular counts differ: {len(marked)} in the diff, {len(clean)} current")
for old, new in zip(marked, clean):
    s = s.replace(old, new, 1)
start=s.find("\\bibliographystyle{plainnat}")
end=s.find("\\end{thebibliography}", start)
bs=bb.find("\\begin{thebibliography}"); be=bb.find("\\end{thebibliography}", bs)
if min(start,end,bs,be) < 0:
    raise SystemExit("bibliography boundaries not found")
s=s[:start]+"\\bibliographystyle{plainnat}\n"+bb[bs:be+len("\\end{thebibliography}")]+s[end+len("\\end{thebibliography}"):]
last = "\\DIFadd{The computational cost of the added decision layer"
if last not in s:
    raise SystemExit("last Discussion paragraph not found")
s = s.replace(
    last,
    "\\enlargethispage{2\\baselineskip}\n" + last,
    1,
)
marker = "\\DIFaddbegin \\FloatBarrier\n\\DIFaddend \\clearpage"
if marker not in s:
    raise SystemExit("Discussion FloatBarrier/clearpage marker not found")
s = s.replace(marker, "\\DIFaddbegin \\FloatBarrier\n\\DIFaddend", 1)
d.write_text(s)
PY2

# The rendered figure PDFs total ~35 MB once pdfTeX embeds them, which is already
# over a 20 MB attachment cap. The submission JPEGs are the same 300 dpi faces
# the clean manuscript uses (that PDF is 14 MB). Point the highlight at those
# rasters so the review aid can occupy a portal slot.
python - <<'PY3'
import re
import shutil
from pathlib import Path

figures = {
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
    13: "F13_revision_audit",
    14: "F14_revision_support",
    15: "F15_v3_fulln_comparator",
}
src_dir = Path("../submission")
raster = Path("figs/highlight_raster")
raster.mkdir(parents=True, exist_ok=True)
missing = [n for n in figures if not (src_dir / f"Figure{n}.jpg").exists()]
if missing:
    raise SystemExit(
        "highlight needs the submission JPEGs; run scripts/28_assemble_submission.py first"
        f" (missing Figure{missing[0]}.jpg)"
    )
for n in figures:
    shutil.copy2(src_dir / f"Figure{n}.jpg", raster / f"Figure{n}.jpg")

stem_to_n = {stem: n for n, stem in figures.items()}
tex = Path("main_diff_V2_to_V3.tex")
pattern = re.compile(
    r"(\\includegraphics(?:\[[^\]]*\])?)\{figs/rendered/([A-Za-z0-9_]+)\.pdf\}"
)

def repl(match):
    stem = match.group(2)
    if stem not in stem_to_n:
        raise SystemExit(f"no submission JPEG for {stem}")
    return f"{match.group(1)}{{figs/highlight_raster/Figure{stem_to_n[stem]}.jpg}}"

text, n = pattern.subn(repl, tex.read_text())
if n != len(figures):
    raise SystemExit(f"rewrote {n} figure includes, expected {len(figures)}")
tex.write_text(text)
print(f"highlight figures: {n} includes -> submission JPEGs")
PY3

latexmk -pdf -g -interaction=nonstopmode main_diff_V2_to_V3.tex > /dev/null 2>&1 || true

errors=$(grep -c '^! ' main_diff_V2_to_V3.log || true)
pages=$(pdfinfo main_diff_V2_to_V3.pdf | awk '/^Pages/{print $2}')
bytes=$(stat -c%s main_diff_V2_to_V3.pdf)
echo "highlight against ${OLD_REF}: ${pages} pages, ${errors} TeX errors, ${bytes} bytes"
[ "$errors" -eq 0 ]
# 20 MB decimal, the stricter of the usual portal readings of "20 MB".
python -c "import sys; sys.exit(0 if int('$bytes') < 20_000_000 else 1)"

