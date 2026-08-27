from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def test_emit_t1_from_disk_hashes():
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts/11_emit_t1_materials.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout
    t1 = pd.read_csv(ROOT / "data/plotdata/T1_materials.csv")
    assert {"item", "path", "sha256", "role"} <= set(t1.columns)
    assert len(t1) >= 10
    assert t1["sha256"].map(
        lambda s: len(str(s)) == 64
        and all(c in "0123456789abcdef" for c in str(s))
    ).all()
    paths = t1["path"].map(Path)
    assert paths.map(lambda path: not path.is_absolute()).all()
    assert paths.map(lambda path: ".." not in path.parts).all()
    assert paths.map(lambda path: path == Path(path.name)).all()
    assert "c_star.json" in set(t1["item"])
    blob = t1.to_csv(index=False).lower()
    assert "survival" not in blob and "0.2034" not in blob
