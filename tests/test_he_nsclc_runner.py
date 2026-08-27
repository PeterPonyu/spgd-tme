from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_nsclc_runner_does_not_touch_yerly_pairs():
    src = (ROOT / "src/he_nsclc_builder.py").read_text()
    driver = (ROOT / "scripts/21_he_nsclc_t0_donor.py").read_text()
    assert '"he_nsclc" / "run"' in src
    assert "must not write Yerly donor_pairs" in src
    assert "SPGD_TME_NSCLC" in driver
    assert "14_run_sitting" not in driver
    assert "DONOR_PAIRS" not in driver


def test_nsclc_runner_requires_keep_probe():
    driver = (ROOT / "scripts/21_he_nsclc_t0_donor.py").read_text()
    assert 'probe.get("decision") != "KEEP"' in driver
    assert "does not retune c*" in driver


def test_nsclc_runner_gated_without_env():
    env = {k: v for k, v in os.environ.items() if k != "SPGD_TME_NSCLC"}
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts/21_he_nsclc_t0_donor.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        env=env,
    )
    assert proc.returncode == 3
    assert "REFUSING" in (proc.stderr + proc.stdout)
