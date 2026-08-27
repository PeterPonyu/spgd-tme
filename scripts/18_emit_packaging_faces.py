#!/usr/bin/env python
"""I/O packaging faces: cell-level CosMx maps and extra pair truth maps.

No sitting. No donor rebuild. No new fit.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.paths import BCC_EXPORT, DONOR_PAIRS, PLOTDATA

SHARED = [
    "Cancer.cells",
    "Endothelial",
    "Fibroblast",
    "Melanocyte",
    "MoMacDC",
    "Normal.Kerat",
    "Pericyte",
    "PlasmaCell",
]
BANNED = ("survival", "biomarker", "0.2034", "0.1126")


def _refuse(path: Path) -> None:
    blob = path.read_text().lower()
    for tok in BANNED:
        if tok in blob:
            raise SystemExit(f"banned token {tok} in {path}")


def _write_maps(pair: str, out_name: str) -> None:
    import anndata as ad

    keep = ["Cancer.cells", "Fibroblast", "MoMacDC"]
    h5 = DONOR_PAIRS / pair / "benchmark_spots.h5ad"
    truth = pd.read_csv(DONOR_PAIRS / pair / "truth_proportions.csv", index_col=0)
    adata = ad.read_h5ad(h5, backed="r")
    xy = pd.DataFrame(adata.obsm["spatial"], index=list(adata.obs_names), columns=["x", "y"])
    adata.file.close()
    out = xy.join(truth[keep], how="inner")
    path = PLOTDATA / out_name
    out.to_csv(path)
    _refuse(path)
    print("[write]", path, "n=", len(out))


def main() -> None:
    PLOTDATA.mkdir(parents=True, exist_ok=True)
    meta = pd.read_csv(
        BCC_EXPORT / "metadata.csv",
        usecols=["celltype", "Patient_ID", "Condition", "x", "y", "fov"],
    )
    keep = meta["celltype"].isin(SHARED)
    cells = meta.loc[keep, ["Patient_ID", "Condition", "fov", "celltype", "x", "y"]].copy()
    cells = cells.rename(columns={"Patient_ID": "patient"})
    cells["condition"] = cells["Condition"].astype(str).str.replace("_", " ", regex=False)
    cells = cells.drop(columns=["Condition"])
    path = PLOTDATA / "cells_spatial.csv.gz"
    cells.to_csv(path, index=False, compression="gzip")
    print("[write]", path, "n=", len(cells))

    _write_maps("B_from_A", "F2D_B_from_A_truth_maps.csv")
    if not (PLOTDATA / "F9_D_from_C_truth_maps.csv").is_file():
        _write_maps("D_from_C", "F9_D_from_C_truth_maps.csv")


if __name__ == "__main__":
    main()
