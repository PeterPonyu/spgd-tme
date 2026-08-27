#!/usr/bin/env python
"""Verify the tree is importable and locks exist. No SPGD fits."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.interpolate import blend_columns, column_cosine
from src.paths import BCC_EXPORT, CBC_PORTAL_PDF, LOCKS, REALGT4
from src.refuse import refusal_mask, should_abstain


def main() -> None:
    assert BCC_EXPORT.joinpath("metadata.csv").is_file()
    assert CBC_PORTAL_PDF.is_file()
    assert REALGT4.joinpath("truth_proportions.csv").is_file()
    for name in ("c_star.json", "type_pairs.json", "cd_lock.json", "input_sha256.txt"):
        assert (LOCKS / name).is_file(), name
    c_star = json.loads((LOCKS / "c_star.json").read_text())
    assert c_star["value"] == 0.8
    pairs = json.loads((LOCKS / "type_pairs.json").read_text())
    assert pairs["realgt"]["neighbor"] == "Prolif_Invasive_Tumor"
    assert should_abstain(0.80, 0.80)
    assert not should_abstain(0.79, 0.80)
    import numpy as np

    P = np.eye(3)
    assert abs(column_cosine(blend_columns(P, 0, 1, 1.0), 0, 1) - 1.0) < 1e-9
    ident = np.array(P, copy=True)
    ident[:, 1] = ident[:, 0]
    assert refusal_mask(ident, 0, 1, 0.80)
    print("SCAFFOLD_OK")


if __name__ == "__main__":
    main()
