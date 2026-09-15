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

sed -i 's/\\protect\([A-Za-z]\)/\\protect \1/g' main_diff_V2_to_V3.tex
sed -i 's/\\hskip0pt%DIFAUXCMD/\\hskip0pt\\relax%DIFAUXCMD/g' main_diff_V2_to_V3.tex
sed -i 's/\\csname \\DIFadd{\([A-Za-z]*\)}\\endcsname/\\csname \1\\endcsname/g' main_diff_V2_to_V3.tex
# Bibliographies are generated output, not a manuscript change.  Replace the
# flattened added bibliography with the current bbl so unchanged references stay black.
# latexdiff lengthens the Discussion, so the journal \clearpage would leave two
# leftover lines alone on the next page. Keep the float drain; drop the page
# break so Declarations continue on that page instead of after a white gap.
python - <<'PY2'
from pathlib import Path
d=Path("main_diff_V2_to_V3.tex"); b=Path("main.bbl")
s=d.read_text(); bb=b.read_text()
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

latexmk -pdf -g -interaction=nonstopmode main_diff_V2_to_V3.tex > /dev/null 2>&1 || true

errors=$(grep -c '^! ' main_diff_V2_to_V3.log || true)
pages=$(pdfinfo main_diff_V2_to_V3.pdf | awk '/^Pages/{print $2}')
echo "highlight against ${OLD_REF}: ${pages} pages, ${errors} TeX errors"
[ "$errors" -eq 0 ]
