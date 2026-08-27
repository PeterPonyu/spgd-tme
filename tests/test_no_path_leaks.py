from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ABSOLUTE_LOCAL = re.compile(r"/home/[a-z0-9_.-]+/|/root/|miniconda3?/")

# Provenance records pin the inputs a sitting consumed, so their locator
# strings are absolute by design and stay local. Everything else must be
# relocatable, and these four are the scrub list for any public deposit.
PROVENANCE_RECORDS = {
    "locks/input_sha256.txt",
    "locks/donor_pair_STATUS.json",
    "data/plotdata/CBC_spatial_maps.REUSE",
    "data/plotdata/F12_he_nsclc_t0_donor.json",
}

# Agent planning notes are working material, not part of the paper package.
# This file is exempt because it has to spell the forbidden prefixes to detect them.
EXEMPT_PREFIXES = ("docs/superpowers/", "tests/test_no_path_leaks.py")


def _tracked_text_files() -> list[str]:
    out = subprocess.run(
        ["git", "ls-files"], cwd=ROOT, capture_output=True, text=True, check=True
    )
    return [p for p in out.stdout.splitlines() if p]


def _leaks(rel: str) -> bool:
    try:
        text = (ROOT / rel).read_text(errors="ignore")
    except (OSError, UnicodeDecodeError):
        return False
    return bool(ABSOLUTE_LOCAL.search(text))


def test_no_new_absolute_paths_in_tracked_files():
    offenders = sorted(
        rel
        for rel in _tracked_text_files()
        if rel not in PROVENANCE_RECORDS
        and not rel.startswith(EXEMPT_PREFIXES)
        and _leaks(rel)
    )
    assert not offenders, f"absolute local paths outside the scrub list: {offenders}"


def test_manuscript_sources_are_relocatable():
    sources = [
        rel
        for rel in _tracked_text_files()
        if rel.startswith("manuscript/") and rel.endswith((".tex", ".bib"))
    ]
    assert sources
    assert not [rel for rel in sources if _leaks(rel)]


def test_scrub_list_still_describes_real_files():
    for rel in PROVENANCE_RECORDS:
        assert (ROOT / rel).is_file(), rel
