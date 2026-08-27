#!/usr/bin/env python
"""Write TME locks once. Refuses to overwrite existing lock files."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import pandas as pd

from src.interpolate import malignant_neighbor_cosine
from src.paths import BCC_EXPORT, BENCH, CBC_CROSSDONOR, LOCKS
from src.signature import extract_signature

REALGT_NEIGHBOR_CANDIDATES = (
    "DCIS_1",
    "DCIS_2",
    "Prolif_Invasive_Tumor",
    "Myoepi_KRT15+",
    "Myoepi_ACTA2+",
)

FIXED_PAIRS = {
    "openst": {"malignant": "Tumor", "neighbor": "Tumor_Keratin_Pearl"},
    "realgt3": {"malignant": "Cancer.cells", "neighbor": "Normal.Kerat"},
}


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _types(bench: Path) -> list[str]:
    return list(pd.read_csv(bench / "truth_proportions.csv", index_col=0, nrows=0).columns)


def _refuse_if_exists(path: Path) -> None:
    if path.exists():
        print(f"REFUSING overwrite: {path}", file=sys.stderr)
        raise SystemExit(2)


def main() -> None:
    LOCKS.mkdir(parents=True, exist_ok=True)
    type_pairs_path = LOCKS / "type_pairs.json"
    c_star_path = LOCKS / "c_star.json"
    cd_lock_path = LOCKS / "cd_lock.json"
    sha_path = LOCKS / "input_sha256.txt"
    for p in (type_pairs_path, c_star_path, cd_lock_path, sha_path):
        _refuse_if_exists(p)

    pairs: dict = {}
    for key, spec in FIXED_PAIRS.items():
        bench = BENCH[key]
        types = _types(bench)
        _, P = extract_signature(bench / "reference_subset.h5ad", types)
        cos = malignant_neighbor_cosine(P, types, spec["malignant"], spec["neighbor"])
        pairs[key] = {**spec, "cosine": round(float(cos), 6)}
        print(f"[pair] {key} {spec['malignant']} vs {spec['neighbor']} cosine={cos:.6f}")

    types = _types(BENCH["realgt"])
    _, P = extract_signature(BENCH["realgt"] / "reference_subset.h5ad", types)
    mal = "Invasive_Tumor"
    best_name = None
    best_cos = -1.0
    for cand in REALGT_NEIGHBOR_CANDIDATES:
        if cand not in types:
            continue
        cos = malignant_neighbor_cosine(P, types, mal, cand)
        print(f"[realgt candidate] {mal} vs {cand} cosine={cos:.6f}")
        if cos > best_cos:
            best_cos = cos
            best_name = cand
    if best_name is None:
        raise SystemExit("no realgt neighbor candidate present")
    pairs["realgt"] = {
        "malignant": mal,
        "neighbor": best_name,
        "cosine": round(float(best_cos), 6),
    }
    print(f"[pair] realgt {mal} vs {best_name} cosine={best_cos:.6f}")

    type_pairs_path.write_text(json.dumps(pairs, indent=2) + "\n")
    c_star_path.write_text(
        json.dumps(
            {
                "value": 0.8,
                "locked_before": "sweep",
                "rule": "refuse malignant type when cosine with locked neighbor >= 0.8",
            },
            indent=2,
        )
        + "\n"
    )

    cd = pd.read_csv(CBC_CROSSDONOR)
    row = cd.loc[cd["method"] == "OUR-v4"].iloc[0]
    cd_lock_path.write_text(
        json.dumps(
            {
                "pair": "C_from_D",
                "method": "OUR-v4",
                "RMSE": float(row["RMSE"]),
                "PCC_type": float(row["PCC_type"]),
                "PCC_spot": float(row["PCC_spot"]),
                "source": "locked",
                "from": "capsules/spgd-deconv/manuscript/data/crossdonor.csv",
            },
            indent=2,
        )
        + "\n"
    )

    sha_rows = []
    for name in ("cells.txt", "features.txt", "metadata.csv", "counts_genes_x_cells.mtx.gz"):
        p = BCC_EXPORT / name
        sha_rows.append(f"{p}\t{_sha(p)}")
    for key in ("openst", "realgt", "realgt3", "realgt4"):
        p = BENCH[key] / "reference_subset.h5ad"
        sha_rows.append(f"{p}\t{_sha(p)}")
    sha_rows.append(f"{CBC_CROSSDONOR}\t{_sha(CBC_CROSSDONOR)}")
    sha_path.write_text("\n".join(sha_rows) + "\n")
    print("[write]", type_pairs_path)
    print("[write]", c_star_path)
    print("[write]", cd_lock_path)
    print("[write]", sha_path)


if __name__ == "__main__":
    main()
