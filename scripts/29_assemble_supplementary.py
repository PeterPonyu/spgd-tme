#!/usr/bin/env python
"""Assemble the Supplementary Material bundle the Data availability statement promises.

The statement tells a reader that the locked reference matrices, the plotted values
behind every panel, and the scripts that render every figure and table travel with
the submission. Nothing in the repository produced that bundle, so the statement
named files a reviewer could not open. This writes them, indexes them so a panel's
numbers can be reached from the figure number alone, and refuses to finish if the
bundle carries a local path or a substrate codename that only means something here.

Run from anywhere:

    python scripts/29_assemble_supplementary.py
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "manuscript" / "scripts"))
sys.path.insert(0, str(ROOT / "scripts"))

from check_manuscript_shell import LOCAL_PATH_MARKERS, REQUIRED_EVIDENCE  # noqa: E402
from generate_tables import ITEM_LABEL, ROLE_LABEL, ROLE_OVERRIDE  # noqa: E402

PLOTDATA = ROOT / "data" / "plotdata"
LOCKS = ROOT / "locks"
RENDER = ROOT / "manuscript" / "scripts"
OUT = ROOT / "supplementary"
# Not inside submission/: the capsule assembler empties that directory, and not
# inside the bundle either, because the archive would then have to hash itself.
ZIP = ROOT / "supplementary.zip"

# Substrate codenames leak two ways: into file names and into cells inside the
# files. Both are rewritten with the public substrate the manuscript prints.
# Longest first, because a bare "realgt" prefixes the numbered ones.
CODENAME = (
    ("realgt4", "donor_lock"),
    ("realgt3", "cosmx"),
    ("realgt2", "xenium_flex"),
    ("realgt", "xenium"),
    ("crossdonor", "donor_transfer_row"),
)
# input_sha256.txt is the one lock written as absolute paths on the machine that
# ran the sitting. Its hashes reach the reader through the public materials table
# instead, so the file itself does not travel.
LOCKS_WITHHELD = ("input_sha256.txt",)
# A marker recording that a map was reused from the parent estimator's capsule
# rather than drawn here. It is bookkeeping between two repositories and carries
# no plotted value, so it is not part of what a reader is promised.
PLOTDATA_WITHHELD = ("CBC_spatial_maps.REUSE",)
# Two locks record where a file sat on the machine that ran the sitting. That is
# provenance for this repository and not for a reader, and it is the only content
# in the locks that names a path, so the key goes rather than its value being
# rewritten into a directory nobody has.
PROVENANCE_KEYS = ("from", "out_dir", "pair_dir")
BINARY_SUFFIXES = (".gz",)
# A bundle is only as good as the worst string in it. Anything here fails the
# build rather than shipping.
FORBIDDEN = tuple(LOCAL_PATH_MARKERS) + ("deconv-lab", "spgd-deconv", "capsules", "realgt")


def public_name(name: str) -> str:
    for codename, public in CODENAME:
        name = name.replace(codename, public)
    return name


def rewrite(text: str) -> str:
    for codename, public in CODENAME:
        text = re.sub(codename, public, text, flags=re.IGNORECASE)
    return text


def copy_text(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(rewrite(src.read_text(encoding="utf-8")), encoding="utf-8")


def strip_provenance(node: object) -> object:
    if isinstance(node, dict):
        return {k: strip_provenance(v) for k, v in node.items() if k not in PROVENANCE_KEYS}
    if isinstance(node, list):
        return [strip_provenance(v) for v in node]
    return node


def copy_gzip(src: Path, dst: Path) -> None:
    """A gzipped table still carries its header row into the bundle."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(src, "rt", encoding="utf-8") as f_in:
        body = rewrite(f_in.read())
    with gzip.open(dst, "wt", encoding="utf-8", compresslevel=9) as f_out:
        f_out.write(body)


def copy_json(src: Path, dst: Path) -> None:
    body = strip_provenance(json.loads(src.read_text(encoding="utf-8")))
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(rewrite(json.dumps(body, indent=2, ensure_ascii=False)) + "\n", encoding="utf-8")


def copy_file(src: Path, dst: Path) -> None:
    if src.suffix in BINARY_SUFFIXES:
        copy_gzip(src, dst)
    elif src.suffix == ".json":
        copy_json(src, dst)
    else:
        copy_text(src, dst)


def write_materials_lock() -> None:
    """The withheld lock's content, keyed by the names Table 1 prints."""
    with (PLOTDATA / "T1_materials.csv").open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    lines = ["item\trole\tsha256"]
    for row in rows:
        item = ITEM_LABEL.get(row["item"], public_name(row["item"]))
        role = ROLE_OVERRIDE.get(row["item"], ROLE_LABEL.get(row["role"], row["role"]))
        lines.append(f"{item.replace('--', chr(8211))}\t{role}\t{row['sha256']}")
    (OUT / "locks" / "materials_sha256.tsv").write_text("\n".join(lines) + "\n", encoding="utf-8")


def index_lines(copied: list[Path]) -> list[str]:
    """Group the bundle by the figure or table whose numbers each file carries.

    Every plotted value is named ``F<n>_`` or ``T<n>_`` by the emit scripts, so the
    prefix is the index. A file without one is listed under its own heading rather
    than dropped, which is what makes the absence of an orphan checkable.
    """
    grouped: dict[str, list[str]] = {}
    for path in sorted(copied):
        stem = path.name
        match = re.match(r"([FT])(\d+)[_D]", stem)
        key = f"{'Figure' if match.group(1) == 'F' else 'Table'} {int(match.group(2))}" if match else "Shared inputs"
        grouped.setdefault(key, []).append(stem)

    def order(key: str) -> tuple[int, int]:
        if key == "Shared inputs":
            return (2, 0)
        kind, number = key.split()
        return (0 if kind == "Figure" else 1, int(number))

    lines = []
    for key in sorted(grouped, key=order):
        lines.append(f"  {key}")
        for name in grouped[key]:
            lines.append(f"    plotdata/{name}")
    return lines


README = """SPGD-TME Supplementary Material
===============================

Two locked operators report mixed-spot TME composition on CosMx carcinomas

This bundle is the material the Data availability statement names. It holds every
number the figures and tables plot, the frozen constants those numbers were
produced under, and the scripts that turn one into the other. It holds no
sequencing data: the libraries are public and are cited by repository accession in
the manuscript, and the reference matrices they yield are named here by content
hash rather than redistributed under their source licences.

Contents
--------

  plotdata/    one table per panel; the values the figures and tables plot
  locks/       the constants frozen before any sweep, and the input hashes
  render/      the scripts that draw every figure and write every table body
  SHA256SUMS.txt

Reproducing a figure or a table
-------------------------------

  Figures 2-12   Rscript render/render_disk_faces.R
                 reads plotdata/, writes one PDF and one PNG per figure
  Figure 1       drawn in the manuscript source as a TikZ picture, not from data
  Tables 1-3     python render/generate_tables.py
                 reads plotdata/T1_materials.csv, T2_timing.csv, T3_donor_matrix.csv

Locks
-----

  locks/c_star.json             the frozen malignant-neighbour cosine cutoff
  locks/type_pairs.json         the malignant-neighbour type pair per substrate
  locks/cd_lock.json            the donor split
  locks/f6_protocol.json        the reportability protocol constants
  locks/donor_pair_STATUS.json  which donor pairs were built, and from what
  locks/materials_sha256.tsv    SHA-256 of every locked input, keyed by the name
                                Table 1 prints for it

Where each file belongs
-----------------------

"""


def main() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "plotdata").mkdir(parents=True)
    (OUT / "locks").mkdir(parents=True)
    (OUT / "render").mkdir(parents=True)

    copied: list[Path] = []
    for src in sorted(PLOTDATA.iterdir()):
        if not src.is_file() or src.name in PLOTDATA_WITHHELD:
            continue
        dst = OUT / "plotdata" / public_name(src.name)
        copy_file(src, dst)
        copied.append(dst)

    for src in sorted(LOCKS.iterdir()):
        if src.is_file() and src.name not in LOCKS_WITHHELD:
            copy_file(src, OUT / "locks" / public_name(src.name))
    write_materials_lock()

    copy_text(RENDER / "generate_tables.py", OUT / "render" / "generate_tables.py")
    for src in sorted((RENDER / "R").glob("*.R")):
        copy_text(src, OUT / "render" / public_name(src.name))

    missing = [name for name in REQUIRED_EVIDENCE if not (OUT / "plotdata" / public_name(name)).is_file()]
    if missing:
        sys.exit(f"FAIL: bundle is missing evidence the manuscript requires: {missing}")

    (OUT / "README.txt").write_text(README + "\n".join(index_lines(copied)) + "\n", encoding="utf-8")

    digests = []
    for path in sorted(OUT.rglob("*")):
        if path.is_file() and path.name != "SHA256SUMS.txt":
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            digests.append(f"{digest}  {path.relative_to(OUT).as_posix()}")
    (OUT / "SHA256SUMS.txt").write_text("\n".join(digests) + "\n", encoding="utf-8")

    for path in sorted(OUT.rglob("*")):
        if not path.is_file():
            continue
        haystack = [path.relative_to(OUT).as_posix().lower()]
        if path.suffix in BINARY_SUFFIXES:
            with gzip.open(path, "rt", encoding="utf-8", errors="replace") as f:
                haystack.append(f.read().lower())
        else:
            haystack.append(path.read_text(encoding="utf-8", errors="replace").lower())
        for token in FORBIDDEN:
            if any(token in blob for blob in haystack):
                sys.exit(f"FAIL: {path.relative_to(OUT)} carries {token!r}")

    ZIP.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(OUT.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(OUT).as_posix())

    files = sum(1 for p in OUT.rglob("*") if p.is_file())
    print(f"wrote {OUT.relative_to(ROOT)}/ with {files} files")
    print(f"wrote {ZIP.relative_to(ROOT)} ({ZIP.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
