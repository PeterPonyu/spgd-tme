from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.metrics_tme import tumor_rmse
from src.paths import BENCH


def test_tumor_rmse_zero_on_truth():
    truth = pd.read_csv(BENCH["openst"] / "truth_proportions.csv", index_col=0)
    assert tumor_rmse(truth, truth, "Tumor") == 0.0
