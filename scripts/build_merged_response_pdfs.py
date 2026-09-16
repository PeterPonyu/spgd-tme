#!/usr/bin/env python
"""Join each standalone response PDF with the tracked-changes manuscript.

The portal attachment cap is 20 MB. Standalone letters stay where they are;
each merged file is the letter, then the highlight manuscript. Page counts must
add: front + tracked == merged.

Run from anywhere:

    python scripts/build_merged_response_pdfs.py
    python scripts/build_merged_response_pdfs.py --pack /path/to/FRONTIERS_V3_FLAT_*
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAX_BYTES = 20_000_000

LETTERS = (
    "reviewer1_response.pdf",
    "reviewer2_response.pdf",
    "rebuttal_overview.pdf",
    "cover_letter.pdf",
)
MERGED_NAMES = {
    "reviewer1_response.pdf": "reviewer1_response_with_tracked_changes.pdf",
    "reviewer2_response.pdf": "reviewer2_response_with_tracked_changes.pdf",
    "rebuttal_overview.pdf": "rebuttal_overview_with_tracked_changes.pdf",
    "cover_letter.pdf": "cover_letter_with_tracked_changes.pdf",
}


def run(cmd: list[str]) -> None:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        sys.exit(f"FAIL: {' '.join(cmd)}\n{proc.stdout[-2000:]}\n{proc.stderr[-2000:]}")


def pdf_pages(path: Path) -> int:
    proc = subprocess.run(["pdfinfo", str(path)], capture_output=True, text=True)
    if proc.returncode != 0:
        sys.exit(f"FAIL: pdfinfo {path}\n{proc.stderr[-2000:]}")
    for line in proc.stdout.splitlines():
        if line.startswith("Pages:"):
            return int(line.split(":")[1])
    sys.exit(f"FAIL: no page count in pdfinfo {path}")


def check_size(path: Path) -> None:
    size = path.stat().st_size
    if size >= MAX_BYTES:
        mb = size / 1_000_000
        sys.exit(f"FAIL: {path.name} is {mb:.2f} MB; portal attachments must stay under 20 MB")


def merge_one(front: Path, tracked: Path, dest: Path) -> None:
    run(["mutool", "merge", "-o", str(dest), str(front), str(tracked)])
    front_pages = pdf_pages(front)
    tracked_pages = pdf_pages(tracked)
    merged_pages = pdf_pages(dest)
    if merged_pages != front_pages + tracked_pages:
        sys.exit(
            f"FAIL: {dest.name} is {merged_pages} pages, "
            f"not {front_pages} + {tracked_pages}"
        )
    check_size(dest)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--pack",
        type=Path,
        help="flat Frontiers pack; default is the local highlight PDF plus responses/",
    )
    parser.add_argument(
        "--tracked",
        type=Path,
        help="tracked-changes PDF to join behind each letter (default: pack or local highlight)",
    )
    args = parser.parse_args()
    pack = args.pack.resolve() if args.pack else None
    if pack is not None and not pack.is_dir():
        sys.exit(f"FAIL: pack is not a directory: {pack}")

    if args.tracked is not None:
        tracked = args.tracked.resolve()
    elif pack is not None:
        tracked = pack / "manuscript_tracked_changes.pdf"
    else:
        tracked = ROOT / "manuscript" / "main_diff_V2_to_V3.pdf"
    if not tracked.exists():
        sys.exit(f"FAIL: missing tracked-changes PDF {tracked}")
    check_size(tracked)

    if pack is None:
        out_dir = ROOT / "responses" / "merged"
        letter_root = ROOT / "responses"
    else:
        out_dir = pack / "merged"
        letter_root = pack
    out_dir.mkdir(parents=True, exist_ok=True)

    for name in LETTERS:
        front = letter_root / name
        if not front.exists():
            sys.exit(f"FAIL: missing {front}")
        dest = out_dir / MERGED_NAMES[name]
        merge_one(front, tracked, dest)
        print(
            f"wrote {dest} "
            f"({pdf_pages(front)} + {pdf_pages(tracked)} = {pdf_pages(dest)} pages, "
            f"{dest.stat().st_size / 1_000_000:.2f} MB)"
        )

    if pack is not None:
        dest_tracked = pack / "manuscript_tracked_changes.pdf"
        if tracked.resolve() != dest_tracked.resolve():
            shutil.copy2(tracked, dest_tracked)
        check_size(dest_tracked)
        check_size(pack / "manuscript.pdf")


if __name__ == "__main__":
    main()
