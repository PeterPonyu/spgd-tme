from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.metrics_tme import point_rmse, tumor_rmse
from src.signature import extract_signature
from src.window_io import bootstrap_done, f3_done, f5_done, fulln_done, t2_done


def test_sitting_refuses_without_gate():
    env = os.environ.copy()
    env.pop("SPGD_TME_COMPUTE", None)
    proc = subprocess.run(
        [sys.executable, "scripts/14_run_sitting.py"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
    )
    assert proc.returncode != 0
    assert "REFUSING sitting" in proc.stdout + proc.stderr


def test_window_io_predicates_are_bool():
    assert isinstance(f3_done(), bool)
    assert isinstance(bootstrap_done(), bool)
    assert isinstance(fulln_done(), bool)
    assert isinstance(t2_done(), bool)
    assert isinstance(f5_done(), bool)


def test_metrics_align_by_index_not_position():
    truth = pd.DataFrame({"Tumor": [0.1, 0.9]}, index=["a", "b"])
    pred = pd.DataFrame({"Tumor": [0.9, 0.1]}, index=["b", "a"])
    assert tumor_rmse(truth, pred, "Tumor") == pytest.approx(0.0)
    assert point_rmse(truth, pred) == pytest.approx(0.0)


def test_metrics_missing_spot_raises():
    truth = pd.DataFrame({"Tumor": [0.1, 0.9]}, index=["a", "b"])
    pred = pd.DataFrame({"Tumor": [0.1]}, index=["a"])
    with pytest.raises(ValueError, match="missed"):
        tumor_rmse(truth, pred, "Tumor")


def test_extract_signature_missing_type_raises(tmp_path):
    import anndata as ad

    X = np.ones((2, 3), dtype=float)
    ref = ad.AnnData(
        X=X,
        obs=pd.DataFrame({"cell_type": ["A", "A"]}, index=["c1", "c2"]),
        var=pd.DataFrame(index=["g1", "g2", "g3"]),
    )
    path = tmp_path / "ref.h5ad"
    ref.write_h5ad(path)
    with pytest.raises(ValueError, match="no cells"):
        extract_signature(path, ["A", "B"])


def test_new_window_scripts_exist():
    for name in (
        "00_preflight_windows.py",
        "13_bootstrap_t0.py",
        "14_run_sitting.py",
    ):
        assert (ROOT / "scripts" / name).is_file()
    blob = (ROOT / "scripts/13_bootstrap_t0.py").read_text()
    assert "apply_abstain" in blob
    assert "B = 1000" in blob


def test_sitting_interval_before_q4():
    blob = (ROOT / "scripts/14_run_sitting.py").read_text()
    assert blob.index("13_bootstrap") < blob.index("04_run_donor")


def test_sitting_pytest_is_not_whole_tree():
    blob = (ROOT / "scripts/14_run_sitting.py").read_text()
    assert '"tests"' not in blob
    assert "'tests'" not in blob
    assert "test_t1_emit" not in blob


def test_trainer_scripts_still_apply_abstain():
    for name in (
        "02_run_collinearity_sweep.py",
        "04_run_donor_transfer.py",
        "05_timing.py",
        "10_confirm_t0_fulln.py",
    ):
        assert "apply_abstain" in (ROOT / "scripts" / name).read_text()
