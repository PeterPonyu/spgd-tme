#!/usr/bin/env python
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.compute_gate import require_compute
from src.donor_builder import build_pair, load_bcc_export, pair_dirname
from src.paths import DONOR_PAIRS, LOCKS, REALGT4

PAIRS = (
    ("PatientA", "PatientB"),
    ("PatientB", "PatientA"),
    ("PatientD", "PatientC"),
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    require_compute("01_build_donor_pairs")
    truth = REALGT4 / "truth_proportions.csv"
    before = _sha(truth)
    DONOR_PAIRS.mkdir(parents=True, exist_ok=True)
    print("[load] CosMx BCC export (once)")
    feats, cells, meta, X = load_bcc_export()
    reports = []
    for spot, ref in PAIRS:
        out = DONOR_PAIRS / pair_dirname(spot, ref)
        print(f"[build] spots={spot} ref={ref} -> {out.name}")
        status = build_pair(spot, ref, out, feats=feats, cells=cells, meta=meta, X_cells_genes=X)
        reports.append(status)
        print(status)
    status_path = LOCKS / "donor_pair_STATUS.txt"
    lines = []
    for st in reports:
        name = pair_dirname(st["spot_donor"], st["ref_donor"])
        if "blocked" in st:
            lines.append(f"BLOCKED {name}: {st['blocked']} shared_types={st['n_shared_types']}")
        else:
            lines.append(f"OK {name}: types={st['n_shared_types']} spots={st.get('n_spots')}")
    status_path.write_text("\n".join(lines) + "\n")
    (LOCKS / "donor_pair_STATUS.json").write_text(json.dumps(reports, indent=2) + "\n")
    after = _sha(truth)
    if after != before:
        raise SystemExit("realgt4 truth sha changed; abort")
    print("[status]", status_path.read_text())


if __name__ == "__main__":
    main()
