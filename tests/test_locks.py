from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_c_star_is_point_eight_float():
    p = ROOT / "locks/c_star.json"
    if not p.exists():
        subprocess.check_call([sys.executable, str(ROOT / "scripts/00_lock_constants.py")])
    spec = json.loads(p.read_text())
    assert spec["value"] == 0.8
    assert isinstance(spec["value"], float)


def test_second_lock_run_fails():
    script = ROOT / "scripts/00_lock_constants.py"
    if not (ROOT / "locks/c_star.json").exists():
        subprocess.check_call([sys.executable, str(script)])
    proc = subprocess.run([sys.executable, str(script)], capture_output=True, text=True)
    assert proc.returncode == 2
    assert "REFUSING overwrite" in proc.stderr


def test_realgt_neighbor_is_concrete():
    p = ROOT / "locks/type_pairs.json"
    spec = json.loads(p.read_text())
    assert spec["realgt"]["neighbor"] != "TO_FILL_MAX_COSINE"
    assert spec["realgt"]["neighbor"]
    assert "cosine" in spec["realgt"]
