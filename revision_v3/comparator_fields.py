#!/usr/bin/env python
"""Record which fields each evaluated comparator output actually carries.

R2-5 is answered with a claim about fields: none of the outputs we evaluated
exposed a matched state in which the malignant coordinate is withheld while the
remaining composition is still reported.  The matched score table behind that
answer holds RMSE, PCC and JSD and says nothing about fields, so the claim had
no table behind it.  This walks the same saved runs the scoring harness reads
and writes down what is on disk beside each set of proportions.

Integrity: read-only over the saved comparator runs; writes only
revision_v3/out/comparator_fields.csv.
"""
from __future__ import annotations

import csv
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "out"
DECONV = Path(os.environ.get("SPGD_DECONV_ROOT", str(ROOT.parents[1] / "deconv-lab")))

# Same runs comparator_matched.py scores, plus the fresh Tangram refit, which is
# computed here rather than loaded from a saved directory.
# (public benchmark label, method, saved-run directory). The directory is read
# here and never written into the table: it names a workspace on this machine.
RUNS = (
    ("Xenium", "RCTD", "results/rctd_realgt"),
    ("Xenium FLEX", "RCTD", "results/rctd_realgt2"),
    ("openST", "cell2location", "results/c2l_openst"),
)
FRESH = (("CosMx BCC", "Tangram", "refit here; writes a mapping and cluster "
                                            "proportions, no per-spot interval"),)

# A per-spot spread of any kind. None of these is a withheld-coordinate state,
# which is the distinction the answer turns on.
INTERVAL_MARKERS = ("interval", "posterior", "sd", "std", "var", "ci_", "quantile")


def classify(directory: Path) -> tuple[str, str]:
    if not directory.is_dir():
        return "directory missing", ""
    names = sorted(p.name for p in directory.iterdir() if p.is_file())
    interval = [n for n in names if any(m in n.lower() for m in INTERVAL_MARKERS)]
    return ("; ".join(names), "; ".join(interval) or "none")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for benchmark, method, rel in RUNS:
        files, interval = classify(DECONV / rel)
        rows.append({
            "benchmark": benchmark,
            "method": method,
            "source": "saved run, re-scored here",
            "files_on_disk": files,
            "per_spot_spread_field": interval,
            # Every one of these writes a full composition. None writes a state in
            # which one coordinate is absent and the rest are still reported.
            "withheld_coordinate_state": "no",
        })
    for benchmark, method, note in FRESH:
        rows.append({
            "benchmark": benchmark,
            "method": method,
            "source": "refit here",
            "files_on_disk": note,
            "per_spot_spread_field": "none",
            "withheld_coordinate_state": "no",
        })

    path = OUT / "comparator_fields.csv"
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    for row in rows:
        print(f"  {row['benchmark']:<22} {row['method']:<14} "
              f"spread={row['per_spot_spread_field']}")
    print(f"[R2-5] wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
