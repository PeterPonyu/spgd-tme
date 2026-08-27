"""Optional fit. Not in the default pytest path."""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.paths import BENCH
from src.spgd_wrap import run_spgd
from src.subsample import subsample_spots


@pytest.mark.skipif(os.environ.get("SPGD_TME_COMPUTE") != "1", reason="compute gated")
def test_run_spgd_columns_match_openst_subset():
    import anndata as ad

    bench = BENCH["openst"]
    dest = ROOT / "data/tmp/openst_wrap300.h5ad"
    subsample_spots(bench / "benchmark_spots.h5ad", 300, 0, dest)
    truth = pd.read_csv(bench / "truth_proportions.csv", index_col=0)
    truth = truth.loc[list(ad.read_h5ad(dest).obs_names)]
    pi, gate = run_spgd(dest, bench / "reference_subset.h5ad", list(truth.columns))
    assert list(pi.columns) == list(truth.columns)
    assert 0.0 <= gate <= 1.0
