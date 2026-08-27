from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_window_scripts_apply_abstain_before_tumor_rmse():
    for name in (
        "02_run_collinearity_sweep.py",
        "04_run_donor_transfer.py",
        "09_confirm_seed1_sweep.py",
        "10_confirm_t0_fulln.py",
    ):
        blob = (ROOT / "scripts" / name).read_text()
        assert "apply_abstain" in blob, name
        assert "require_compute" in blob, name


def test_timing_refuse_is_not_a_max_stub():
    blob = (ROOT / "scripts/05_timing.py").read_text()
    assert "apply_abstain" in blob
    assert "np.max(w)" not in blob
    assert "type_pairs.json" in blob


def test_sitting_driver_is_serial_fail_fast():
    blob = (ROOT / "scripts/14_run_sitting.py").read_text()
    assert "02_run_collinearity_sweep.py" in blob
    assert "10_confirm_t0_fulln.py" in blob
    assert "13_bootstrap_t0.py" in blob
    assert "SITTING STOPPED" in blob
