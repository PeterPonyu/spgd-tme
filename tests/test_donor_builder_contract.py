from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.donor_builder import pair_dirname
from src.paths import DONOR_PAIRS


def test_pair_dirname():
    assert pair_dirname("PatientA", "PatientB") == "A_from_B"
    assert pair_dirname("PatientD", "PatientC") == "D_from_C"


def test_existing_pair_dir_not_overwritten_if_present(tmp_path):
    from src.donor_builder import build_pair

    d = tmp_path / "_empty_probe"
    d.mkdir(parents=True)
    (d / "marker").write_text("x")
    with pytest.raises(FileExistsError, match="overwrite"):
        build_pair(
            "PatientA",
            "PatientB",
            d,
            feats=["g"],
            cells=["c"],
            meta=None,
            X_cells_genes=None,
        )


def test_manifest_contract_if_pair_built():
    p = DONOR_PAIRS / "D_from_C" / "manifest.json"
    if not p.exists():
        pytest.skip("donor pair not built yet")
    man = json.loads(p.read_text())
    assert man["spot_donor"] != man["ref_donor"]
    assert man["donor_key_in_source"] == "Patient_ID"
