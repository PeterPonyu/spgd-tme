from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def test_emit_truth_faces_from_q1():
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts/08_emit_truth_faces.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout
    refuse = pd.read_csv(ROOT / "data/plotdata/F2_native_refuse.csv")
    assert set(refuse["decision"]) == {"ABSTAIN", "KEEP"}
    assert (refuse["decision"] == "ABSTAIN").sum() == 2
    assert (refuse["decision"] == "KEEP").sum() == 1
    floor = pd.read_csv(ROOT / "data/plotdata/F9_type_floor.csv")
    assert len(floor) == 24
    myelo = pd.read_csv(ROOT / "data/plotdata/F10_myeloid_occupancy.csv")
    assert set(myelo["pair"]) == {"A_from_B", "B_from_A", "D_from_C"}
    blob = (ROOT / "data/plotdata/F2_donor_edges.csv").read_text()
    assert "0.2034" not in blob and "0.1126" not in blob
