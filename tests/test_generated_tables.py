from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "manuscript/scripts/generate_tables.py"
TABLES = ROOT / "manuscript/tables"
NAMES = ("T1_materials.tex", "T2_timing.tex", "T3_donor_matrix.tex")


def test_regenerating_the_tables_reproduces_the_typeset_ones():
    """A hand-edit to a table body is silently reverted the next time anyone
    runs the generator, so the committed bodies have to be its own output."""
    before = {name: (TABLES / name).read_text(encoding="utf-8") for name in NAMES}
    proc = subprocess.run(
        [sys.executable, str(GENERATOR)], cwd=ROOT, capture_output=True, text=True
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout
    for name in NAMES:
        after = (TABLES / name).read_text(encoding="utf-8")
        if after != before[name]:
            (TABLES / name).write_text(before[name], encoding="utf-8")
            raise AssertionError(f"{name} has drifted from generate_tables.py")


def test_the_timing_table_shares_sum_to_the_pass_it_reports():
    body = (TABLES / "T2_timing.tex").read_text(encoding="utf-8")
    shares = [
        float(cell.rstrip("\\%"))
        for line in body.splitlines()
        if line.endswith(r"\%" + " \\\\") and "One openST pass" not in line
        for cell in [line.split("&")[-1].strip().removesuffix("\\\\").strip()]
        if not cell.startswith(r"\(<\)")
    ]
    assert shares, "no per-step shares parsed out of T2"
    assert abs(sum(shares) - 100) < 0.05, f"steps sum to {sum(shares):.2f}%, not 100%"
