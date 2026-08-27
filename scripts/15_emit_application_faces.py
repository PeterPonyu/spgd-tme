#!/usr/bin/env python
"""Tumor-application faces from on-disk BCC metadata, Q1 truth, and saved t=0 π̂.

No build_v4. No donor rebuild. No new download.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.donor_builder import DROP_TYPES, MIN_CELLS_PER_SPOT
from src.paths import BCC_EXPORT, BENCH, DONOR_PAIRS, PLOTDATA

SHARED_TYPES = [
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


def _refuse_blob(path: Path) -> None:
    blob = path.read_text().lower()
    for tok in BANNED:
        if tok in blob:
            raise SystemExit(f"banned token {tok} in {path}")


def _write(df: pd.DataFrame, name: str) -> Path:
    path = PLOTDATA / name
    df.to_csv(path, index=False)
    _refuse_blob(path)
    print("[write]", path, "n=", len(df))
    return path


def _load_meta() -> pd.DataFrame:
    meta = pd.read_csv(BCC_EXPORT / "metadata.csv", usecols=["cell_id", "celltype", "Patient_ID", "Condition", "x", "y"])
    ct = meta["celltype"].astype(str)
    keep = ct.isin(SHARED_TYPES) & ~ct.isin(DROP_TYPES)
    return meta.loc[keep].copy()


def _condition_occupancy(meta: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (patient, cond), sub in meta.groupby(["Patient_ID", "Condition"], sort=True):
        n = len(sub)
        vc = sub["celltype"].value_counts()
        for typ in SHARED_TYPES:
            k = int(vc.get(typ, 0))
            rows.append(
                {
                    "patient": patient,
                    "condition": cond,
                    "type": typ,
                    "n_cells": k,
                    "n_condition": n,
                    "fraction": round(k / n, 6) if n else 0.0,
                }
            )
    return pd.DataFrame(rows)


def _replay_d_from_c_condition(meta: pd.DataFrame) -> pd.DataFrame | None:
    name = "D_from_C"
    man_path = DONOR_PAIRS / name / "manifest.json"
    truth_path = DONOR_PAIRS / name / "truth_proportions.csv"
    if not man_path.is_file() or not truth_path.is_file():
        return None
    man = json.loads(man_path.read_text())
    kept = list(man["cell_type"])
    bin_edge = float(man["bin_edge_native_units"])
    spot_donor = str(man["spot_donor"])
    sub = meta.loc[(meta["Patient_ID"].astype(str) == spot_donor) & meta["celltype"].isin(kept)].copy()
    if sub.empty:
        return None
    xy = sub[["x", "y"]].to_numpy(dtype=float)
    ij = np.floor((xy - xy.min(0)) / bin_edge).astype(np.int64)
    bin_id = ij[:, 0] * (int(ij[:, 1].max()) + 1) + ij[:, 1]
    sub = sub.assign(bin_id=bin_id)
    truth = pd.read_csv(truth_path, index_col=0)
    recs = []
    for b, g in sub.groupby("bin_id"):
        if len(g) < MIN_CELLS_PER_SPOT:
            continue
        spot = f"cosmx_bcc_xdonor_spot_{int(b):010d}"
        if spot not in truth.index:
            continue
        cond = str(g["Condition"].mode().iat[0])
        recs.append({"spot": spot, "condition": cond, "n_cells": int(len(g))})
    if not recs:
        return None
    cond_map = pd.DataFrame(recs).set_index("spot")
    joined = truth.join(cond_map[["condition"]], how="inner")
    if joined.empty:
        return None
    rows = []
    for cond, g in joined.groupby("condition"):
        for typ in truth.columns:
            rows.append(
                {
                    "pair": name,
                    "condition": cond,
                    "type": typ,
                    "n_spots": int(len(g)),
                    "mean": round(float(g[typ].mean()), 6),
                }
            )
    out = pd.DataFrame(rows)
    out.attrs["n_matched"] = int(len(joined))
    out.attrs["n_truth"] = int(len(truth))
    return out


def _keep_spatial() -> tuple[pd.DataFrame, pd.DataFrame]:
    pi = pd.read_csv(PLOTDATA / "F3_pi_t0_realgt3.csv", index_col=0)
    if "Cancer.cells" not in pi.columns:
        raise SystemExit("F3_pi_t0_realgt3.csv missing Cancer.cells")
    h5 = BENCH["realgt3"] / "benchmark_spots.h5ad"
    if not h5.is_file():
        raise SystemExit(f"missing {h5}")
    import anndata as ad

    adata = ad.read_h5ad(h5, backed="r")
    if "spatial" not in adata.obsm:
        adata.file.close()
        raise SystemExit("realgt3 spots lack spatial")
    xy = pd.DataFrame(adata.obsm["spatial"], index=list(adata.obs_names), columns=["x", "y"])
    adata.file.close()
    tumor = pi["Cancer.cells"].astype(float).rename("tumor_hat")
    out = xy.join(tumor, how="inner")
    if len(out) != len(pi):
        raise SystemExit(f"KEEP spatial join {len(out)} != pi {len(pi)}")
    out = out.reset_index().rename(columns={"index": "spot"})
    summary = pd.DataFrame(
        [
            {
                "substrate": "realgt3",
                "t": 0.0,
                "decision": "KEEP",
                "n_spots": int(len(out)),
                "tumor_hat_mean": round(float(out["tumor_hat"].mean()), 6),
                "tumor_hat_median": round(float(out["tumor_hat"].median()), 6),
                "tumor_hat_q25": round(float(out["tumor_hat"].quantile(0.25)), 6),
                "tumor_hat_q75": round(float(out["tumor_hat"].quantile(0.75)), 6),
            }
        ]
    )
    return out, summary


def main() -> None:
    PLOTDATA.mkdir(parents=True, exist_ok=True)
    meta = _load_meta()
    cond = _condition_occupancy(meta)
    _write(cond, "F9_condition_occupancy.csv")

    cell_summary_rows = []
    for (patient, cname), g in meta.groupby(["Patient_ID", "Condition"]):
        n = len(g)
        cancer = float((g["celltype"] == "Cancer.cells").mean())
        fibro = float((g["celltype"] == "Fibroblast").mean())
        myelo = float((g["celltype"] == "MoMacDC").mean())
        cell_summary_rows.append(
            {
                "patient": patient,
                "condition": cname,
                "n_cells": int(n),
                "cancer_fraction": round(cancer, 6),
                "fibroblast_fraction": round(fibro, 6),
                "momacdc_fraction": round(myelo, 6),
            }
        )
    _write(pd.DataFrame(cell_summary_rows), "F2_condition_cell_summary.csv")

    replay = _replay_d_from_c_condition(meta)
    if replay is None:
        raise SystemExit("D_from_C condition replay failed to match Q1 truth spots")
    n_matched = int(replay.attrs.get("n_matched", 0))
    n_truth = int(replay.attrs.get("n_truth", 0))
    if n_matched != n_truth:
        raise SystemExit(f"D_from_C condition replay matched {n_matched}/{n_truth} spots")
    _write(replay, "F9_condition_spot_truth.csv")

    spatial, summary = _keep_spatial()
    path = PLOTDATA / "F4_keep_spatial.csv"
    spatial.to_csv(path, index=False)
    _refuse_blob(path)
    print("[write]", path, "n=", len(spatial))
    _write(summary, "F4_keep_spatial_summary.csv")

    fulln_path = PLOTDATA / "F4_keep_spatial_fulln.csv"
    truth_path = BENCH["realgt3"] / "truth_proportions.csv"
    if fulln_path.is_file() and truth_path.is_file():
        keep_full = pd.read_csv(fulln_path)
        tumor_truth = pd.read_csv(truth_path, index_col=0)["Cancer.cells"].rename("tumor_truth")
        compare = keep_full.set_index("spot").join(tumor_truth, how="inner").reset_index()
        if len(compare) != 5686:
            raise SystemExit(f"KEEP compare join {len(compare)} != 5686")
        if compare["tumor_truth"].isna().any():
            raise SystemExit("KEEP compare missing tumor truth")
        _write(compare, "F4_keep_spatial_fulln_compare.csv")


if __name__ == "__main__":
    main()
