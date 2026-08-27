#!/usr/bin/env python
"""Emit F2/F9/F10 tables from Q1 truth + locks. No build_v4. No compute gate."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.paths import DONOR_PAIRS, LOCKS, PLOTDATA
from src.refuse import should_abstain

PAIRS = ("A_from_B", "B_from_A", "D_from_C")
BANNED = ("survival", "biomarker", "0.2034", "0.1126")


def _refuse_blob(path: Path) -> None:
    blob = path.read_text().lower()
    for tok in BANNED:
        if tok in blob:
            raise SystemExit(f"banned token {tok} in {path}")


def main() -> None:
    PLOTDATA.mkdir(parents=True, exist_ok=True)
    c_star = float(json.loads((LOCKS / "c_star.json").read_text())["value"])
    pairs = json.loads((LOCKS / "type_pairs.json").read_text())
    cd = json.loads((LOCKS / "cd_lock.json").read_text())

    cards = []
    mass_rows = []
    floor_rows = []
    myeloid = []
    for name in PAIRS:
        man = json.loads((DONOR_PAIRS / name / "manifest.json").read_text())
        truth = pd.read_csv(DONOR_PAIRS / name / "truth_proportions.csv", index_col=0)
        cards.append(
            {
                "pair": name,
                "spot_donor": man["spot_donor"],
                "ref_donor": man["ref_donor"],
                "n_spots": int(man["n_spots"]),
                "median_cells": float(man["median_cells_per_spot"]),
                "approx_um": round(float(man["approx_spot_um_if_cosmx_px"]), 2),
                "n_types": int(man["n_types"]),
            }
        )
        for col in truth.columns:
            s = truth[col].astype(float)
            mass_rows.append(
                {
                    "pair": name,
                    "type": col,
                    "mean": round(float(s.mean()), 6),
                    "zero_rate": round(float((s == 0).mean()), 6),
                    "below_0_05": round(float((s < 0.05).mean()), 6),
                }
            )
            floor_rows.append(
                {
                    "pair": name,
                    "type": col,
                    "mean": round(float(s.mean()), 6),
                    "zero_rate": round(float((s == 0).mean()), 6),
                    "below_0_05": round(float((s < 0.05).mean()), 6),
                    "floor_min_type_cells": 50,
                }
            )
        if "MoMacDC" in truth.columns:
            s = truth["MoMacDC"].astype(float)
            myeloid.append(
                {
                    "pair": name,
                    "type": "MoMacDC",
                    "mean": round(float(s.mean()), 6),
                    "zero_rate": round(float((s == 0).mean()), 6),
                    "source": "q1_truth",
                }
            )

    refuse_rows = []
    for sub, rec in pairs.items():
        cos = float(rec["cosine"])
        refuse_rows.append(
            {
                "substrate": sub,
                "malignant": rec["malignant"],
                "neighbor": rec["neighbor"],
                "cosine": cos,
                "c_star": c_star,
                "decision": "ABSTAIN" if should_abstain(cos, c_star) else "KEEP",
            }
        )

    edges = [
        {"pair": "A_from_B", "n_spots": 1194, "source": "q1_truth"},
        {"pair": "B_from_A", "n_spots": 2020, "source": "q1_truth"},
        {"pair": "D_from_C", "n_spots": 3261, "source": "q1_truth"},
        {
            "pair": cd["pair"],
            "n_spots": "",
            "source": "locked",
            "RMSE": cd["RMSE"],
            "PCC_type": cd["PCC_type"],
            "PCC_spot": cd["PCC_spot"],
        },
    ]

    outs = {
        "F2_pair_cards.csv": pd.DataFrame(cards),
        "F2_truth_mass.csv": pd.DataFrame(mass_rows),
        "F2_native_refuse.csv": pd.DataFrame(refuse_rows),
        "F2_donor_edges.csv": pd.DataFrame(edges),
        "F9_type_floor.csv": pd.DataFrame(floor_rows),
        "F10_myeloid_occupancy.csv": pd.DataFrame(myeloid),
    }
    for name, df in outs.items():
        path = PLOTDATA / name
        df.to_csv(path, index=False)
        _refuse_blob(path)
        print("[write]", path)

    # Spatial extracts; I/O only. A-from-B path and CSV layout stay as locked.
    import anndata as ad

    keep = ["Cancer.cells", "Fibroblast", "MoMacDC"]
    h5 = DONOR_PAIRS / "A_from_B" / "benchmark_spots.h5ad"
    truth = pd.read_csv(DONOR_PAIRS / "A_from_B" / "truth_proportions.csv", index_col=0)
    if h5.is_file():
        adata = ad.read_h5ad(h5, backed="r")
        if "spatial" in adata.obsm:
            xy = pd.DataFrame(adata.obsm["spatial"], index=list(adata.obs_names), columns=["x", "y"])
            out = xy.join(truth[keep], how="inner")
            path = PLOTDATA / "F2D_A_from_B_truth_maps.csv"
            out.to_csv(path)
            _refuse_blob(path)
            print("[write]", path, "n=", len(out))
        adata.file.close()

    h5_d = DONOR_PAIRS / "D_from_C" / "benchmark_spots.h5ad"
    truth_d = pd.read_csv(DONOR_PAIRS / "D_from_C" / "truth_proportions.csv", index_col=0)
    if h5_d.is_file():
        adata = ad.read_h5ad(h5_d, backed="r")
        if "spatial" in adata.obsm:
            xy = pd.DataFrame(adata.obsm["spatial"], index=list(adata.obs_names), columns=["x", "y"])
            out = xy.join(truth_d[keep], how="inner")
            path = PLOTDATA / "F9_D_from_C_truth_maps.csv"
            out.to_csv(path)
            _refuse_blob(path)
            print("[write]", path, "n=", len(out))
        adata.file.close()


if __name__ == "__main__":
    main()
