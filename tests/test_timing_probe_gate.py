from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_timing_probe_refuses_without_env():
    env = os.environ.copy()
    env.pop("SPGD_TME_COMPUTE", None)
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts/16_time_and_save_fulln_pi.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        env=env,
    )
    assert proc.returncode == 3
    assert "REFUSING" in proc.stderr
