from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def test_emit_application_faces_from_disk():
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts/15_emit_application_faces.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout
    cells = pd.read_csv(ROOT / "data/plotdata/F2_condition_cell_summary.csv")
    assert len(cells) == 8
    assert set(cells["patient"]) == {"PatientA", "PatientB", "PatientC", "PatientD"}
    spots = pd.read_csv(ROOT / "data/plotdata/F9_condition_spot_truth.csv")
    cancer = spots[spots["type"] == "Cancer.cells"]
    assert int(cancer["n_spots"].sum()) == 3261
    keep = pd.read_csv(ROOT / "data/plotdata/F4_keep_spatial.csv")
    assert len(keep) == 400
    assert "tumor_hat" in keep.columns
    summary = pd.read_csv(ROOT / "data/plotdata/F4_keep_spatial_summary.csv")
    assert str(summary.loc[0, "decision"]) == "KEEP"
    fulln = pd.read_csv(ROOT / "data/plotdata/F4_keep_spatial_fulln.csv")
    assert len(fulln) == 5686
    fulln_sum = pd.read_csv(ROOT / "data/plotdata/F4_keep_spatial_fulln_summary.csv")
    assert int(fulln_sum.loc[0, "n_spots"]) == 5686
    assert str(fulln_sum.loc[0, "decision"]) == "KEEP"
    blob = "\n".join(
        (ROOT / "data/plotdata" / name).read_text().lower()
        for name in (
            "F2_condition_cell_summary.csv",
            "F9_condition_occupancy.csv",
            "F9_condition_spot_truth.csv",
            "F4_keep_spatial_summary.csv",
        )
    )
    assert "0.2034" not in blob and "0.1126" not in blob
