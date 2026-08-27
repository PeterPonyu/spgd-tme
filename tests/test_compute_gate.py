from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_heavy_script_refuses_without_env():
    env = os.environ.copy()
    env.pop("SPGD_TME_COMPUTE", None)
    for name in (
        "02_run_collinearity_sweep.py",
        "16_time_and_save_fulln_pi.py",
        "17_time_fulln_three_substrates.py",
    ):
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / name)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            env=env,
        )
        assert proc.returncode == 3, name
        assert "REFUSING" in proc.stderr, name
