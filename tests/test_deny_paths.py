from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.paths import BCC_EXPORT, CBC_PORTAL_PDF, REALGT4_TRUTH


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_bcc_export_present():
    assert (BCC_EXPORT / "metadata.csv").is_file()


def test_cbc_and_realgt4_sha_stable_across_import():
    before_pdf = _sha(CBC_PORTAL_PDF)
    before_truth = _sha(REALGT4_TRUTH)
    import src.paths  # noqa: F401

    assert _sha(CBC_PORTAL_PDF) == before_pdf
    assert _sha(REALGT4_TRUTH) == before_truth
