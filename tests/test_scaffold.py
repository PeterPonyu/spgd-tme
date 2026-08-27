from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_check_scaffold():
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts/check_scaffold.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    assert "SCAFFOLD_OK" in proc.stdout
