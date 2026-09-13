#!/usr/bin/env bash
# Build the V2-to-V3 highlight PDF.
#
# latexdiff --flatten leaves three defects that stop pdflatex on this manuscript, so they are
# repaired here rather than by hand on each rebuild:
#   - \protect glued to inlined caption text        -> \protectMaterials
#   - \hskip0pt followed by the word "plus"         -> parsed as glue syntax
#   - \DIFadd markup inserted inside \csname        -> unterminated csname
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MS="$ROOT/manuscript"
OLD_REF="${1:-v2-public-release}"
OLD_DIR="$(mktemp -d)"
trap 'rm -rf "$OLD_DIR"' EXIT

git -C "$ROOT" archive "$OLD_REF" manuscript | tar -x -C "$OLD_DIR"

cd "$MS"
latexdiff --flatten "$OLD_DIR/manuscript/main.tex" main.tex > main_diff_V2_to_V3.tex

sed -i 's/\\protect\([A-Za-z]\)/\\protect \1/g' main_diff_V2_to_V3.tex
sed -i 's/\\hskip0pt%DIFAUXCMD/\\hskip0pt\\relax%DIFAUXCMD/g' main_diff_V2_to_V3.tex
sed -i 's/\\csname \\DIFadd{\([A-Za-z]*\)}\\endcsname/\\csname \1\\endcsname/g' main_diff_V2_to_V3.tex

latexmk -pdf -g -interaction=nonstopmode main_diff_V2_to_V3.tex > /dev/null 2>&1 || true

errors=$(grep -c '^! ' main_diff_V2_to_V3.log || true)
pages=$(pdfinfo main_diff_V2_to_V3.pdf | awk '/^Pages/{print $2}')
echo "highlight against ${OLD_REF}: ${pages} pages, ${errors} TeX errors"
[ "$errors" -eq 0 ]
