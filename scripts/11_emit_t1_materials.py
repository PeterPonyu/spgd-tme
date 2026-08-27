#!/usr/bin/env python
"""Hash on-disk materials into T1. No build_v4. Does not require F3."""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.paths import BCC_EXPORT, BENCH, CBC_CROSSDONOR, LOCKS, PLOTDATA


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    PLOTDATA.mkdir(parents=True, exist_ok=True)
    rows = []
    for name in ("cells.txt", "features.txt", "metadata.csv", "counts_genes_x_cells.mtx.gz"):
        p = BCC_EXPORT / name
        if not p.is_file():
            raise SystemExit(f"FAIL-CLOSED: missing {p}")
        rows.append({"item": name, "path": p.name, "sha256": _sha(p), "role": "bcc_export"})
    for key in ("openst", "realgt", "realgt2", "realgt3", "realgt4"):
        p = BENCH[key] / "reference_subset.h5ad"
        if not p.is_file():
            raise SystemExit(f"FAIL-CLOSED: missing {p}")
        role = "orthogonal_ref" if key == "realgt2" else "benchmark_ref"
        rows.append({"item": f"{key}_ref", "path": p.name, "sha256": _sha(p), "role": role})
    if not CBC_CROSSDONOR.is_file():
        raise SystemExit(f"FAIL-CLOSED: missing {CBC_CROSSDONOR}")
    rows.append(
        {
            "item": "crossdonor.csv",
            "path": CBC_CROSSDONOR.name,
            "sha256": _sha(CBC_CROSSDONOR),
            "role": "cbc_lock",
        }
    )
    for name, role in (("type_pairs.json", "type_pairs"), ("c_star.json", "c_star")):
        p = LOCKS / name
        if not p.is_file():
            raise SystemExit(f"FAIL-CLOSED: missing {p}")
        rows.append({"item": name, "path": p.name, "sha256": _sha(p), "role": role})
    out = PLOTDATA / "T1_materials.csv"
    pd.DataFrame(rows).to_csv(out, index=False)
    print("[write]", out, "n=", len(rows))


if __name__ == "__main__":
    main()
