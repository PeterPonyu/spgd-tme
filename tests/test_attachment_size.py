"""Portal attachments must stay under 20 MB."""

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MAX_BYTES = 20_000_000


def test_merge_and_highlight_scripts_enforce_the_cap():
    merge = (ROOT / "scripts/build_merged_response_pdfs.py").read_text()
    highlight = (ROOT / "scripts/build_v2_to_v3_highlight.sh").read_text()
    assert "MAX_BYTES = 20_000_000" in merge
    assert "20_000_000" in highlight
    assert "highlight_raster" in highlight


def test_local_highlight_pdf_fits_if_built():
    pdf = ROOT / "manuscript" / "main_diff_V2_to_V3.pdf"
    if not pdf.exists():
        pytest.skip("highlight PDF not built")
    assert pdf.stat().st_size < MAX_BYTES
