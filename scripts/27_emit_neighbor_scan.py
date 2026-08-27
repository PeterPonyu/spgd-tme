#!/usr/bin/env python
"""Flatten the recorded malignant-versus-every-neighbor cosine scans into one table.

Each independent-carcinoma probe already scored the malignant program against
every annotated type in its library and kept the whole scan, but only the
designated stromal pair reached the figures. This projects the scans into one
tidy table so the gate board can show the neighborhood a single reported cosine
summarises.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PLOTDATA = ROOT / "data" / "plotdata"

# Probe file -> reader-facing library name, in KEEP-then-ABSTAIN order.
PROBES = {
    "F12_crc_cosine_probe.json": "CosMx CRC",
    "F12_he_nsclc_cosine_probe.json": "CosMx NSCLC",
    "F12_he_liver_cosine_probe.json": "CosMx HCC",
    "F12_pdac_cosine_probe.json": "CosMx PDAC",
}


def scan_rows(path: Path, library: str) -> list[dict[str, object]]:
    probe = json.loads(path.read_text())
    designated = probe["neighbor"]
    rows = []
    for entry in probe["neighbor_scan"]:
        rows.append(
            {
                "library": library,
                "malignant": probe["malignant"],
                "neighbor": entry["neighbor"],
                "cosine": entry["cosine"],
                "c_star": probe["c_star"],
                "decision": entry["decision"],
                "designated": entry["neighbor"] == designated,
                "library_decision": probe["decision"],
            }
        )
    if not any(r["designated"] for r in rows):
        raise SystemExit(f"{path.name}: designated neighbor {designated} missing from scan")
    return rows


def main() -> None:
    rows: list[dict[str, object]] = []
    for name, library in PROBES.items():
        rows.extend(scan_rows(PLOTDATA / name, library))
    scan = pd.DataFrame(rows)

    reported = scan[scan["designated"]]
    mismatch = reported[reported["decision"] != reported["library_decision"]]
    if len(mismatch):
        raise SystemExit(f"designated pair disagrees with the library call: {mismatch}")

    dest = PLOTDATA / "F12_neighbor_scan.csv"
    scan.to_csv(dest, index=False)
    above = scan.groupby("library")["decision"].apply(lambda s: (s == "ABSTAIN").sum())
    print("wrote", dest.name, len(scan))
    for library, n in above.items():
        total = int((scan["library"] == library).sum())
        print(f"  {library}: {int(n)}/{total} neighbors at or above the cutoff")


if __name__ == "__main__":
    main()
