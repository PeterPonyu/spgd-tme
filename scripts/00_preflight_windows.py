#!/usr/bin/env python
"""Fail before a sitting window. No build_v4."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.paths import BCC_EXPORT, BENCH, CBC_CROSSDONOR, CBC_MS, DECONV, DONOR_PAIRS, LOCKS, TMP

SUBSTRATES = ("openst", "realgt", "realgt3")
PAIRS = ("A_from_B", "B_from_A", "D_from_C")


def _need(path: Path, label: str) -> None:
    if not path.is_file():
        raise SystemExit(f"PREFLIGHT FAIL: missing {label}: {path}")


def main() -> None:
    pairs = json.loads((LOCKS / "type_pairs.json").read_text())
    c_star = json.loads((LOCKS / "c_star.json").read_text())
    if float(c_star["value"]) != 0.8:
        raise SystemExit(f"PREFLIGHT FAIL: c_star {c_star}")
    cd = json.loads((LOCKS / "cd_lock.json").read_text())
    for k in ("RMSE", "PCC_type", "PCC_spot"):
        if k not in cd:
            raise SystemExit(f"PREFLIGHT FAIL: cd_lock missing {k}")

    import anndata as ad

    for sub in SUBSTRATES:
        b = BENCH[sub]
        _need(b / "benchmark_spots.h5ad", f"{sub} spots")
        _need(b / "reference_subset.h5ad", f"{sub} ref")
        _need(b / "truth_proportions.csv", f"{sub} truth")
        truth = pd.read_csv(b / "truth_proportions.csv", index_col=0)
        mal, neigh = pairs[sub]["malignant"], pairs[sub]["neighbor"]
        if mal not in truth.columns or neigh not in truth.columns:
            raise SystemExit(f"PREFLIGHT FAIL: {sub} types {mal}/{neigh}")
        spots = ad.read_h5ad(b / "benchmark_spots.h5ad", backed="r")
        ref = ad.read_h5ad(b / "reference_subset.h5ad", backed="r")
        if len(set(spots.obs_names) & set(truth.index)) != spots.n_obs:
            raise SystemExit(f"PREFLIGHT FAIL: {sub} spot/truth mismatch")
        genes = set(map(str, spots.var_names)) & set(map(str, ref.var_names))
        if len(genes) < 64:
            raise SystemExit(f"PREFLIGHT FAIL: {sub} gene overlap {len(genes)}")
        anno_col = None
        for cand in ("annotation", "cell_type", "celltype", "obs_annotation"):
            if cand in ref.obs.columns:
                anno_col = cand
                break
        if anno_col is None:
            raise SystemExit(f"PREFLIGHT FAIL: {sub} ref has no annotation")
        present = set(map(str, ref.obs[anno_col].astype(str)))
        missing_ty = [c for c in truth.columns if c not in present]
        if missing_ty:
            raise SystemExit(f"PREFLIGHT FAIL: {sub} ref missing types {missing_ty}")
        spots.file.close()
        ref.file.close()

    for name in PAIRS:
        d = DONOR_PAIRS / name
        for fn in ("truth_proportions.csv", "benchmark_spots_counts.h5ad", "reference_subset.h5ad", "manifest.json"):
            _need(d / fn, f"{name}/{fn}")
        truth = pd.read_csv(d / "truth_proportions.csv", index_col=0)
        spots = ad.read_h5ad(d / "benchmark_spots_counts.h5ad", backed="r")
        ref = ad.read_h5ad(d / "reference_subset.h5ad", backed="r")
        if "Cancer.cells" not in truth.columns:
            raise SystemExit(f"PREFLIGHT FAIL: {name} missing Cancer.cells")
        if len(set(spots.obs_names) & set(truth.index)) != spots.n_obs:
            raise SystemExit(f"PREFLIGHT FAIL: {name} spot/truth mismatch")
        if "cell_type" not in ref.obs.columns:
            raise SystemExit(f"PREFLIGHT FAIL: {name} ref has no cell_type")
        present = set(map(str, ref.obs["cell_type"].astype(str)))
        missing_ty = [c for c in truth.columns if c not in present]
        if missing_ty:
            raise SystemExit(f"PREFLIGHT FAIL: {name} ref missing types {missing_ty}")
        spots.file.close()
        ref.file.close()

    _need(CBC_MS / "data/spatial_maps.csv", "CBC spatial reuse")
    _need(CBC_CROSSDONOR, "CBC crossdonor")
    for fn in ("cells.txt", "features.txt", "metadata.csv", "counts_genes_x_cells.mtx.gz"):
        _need(BCC_EXPORT / fn, f"bcc_export/{fn}")
    for key in ("openst", "realgt", "realgt2", "realgt3", "realgt4"):
        _need(BENCH[key] / "reference_subset.h5ad", f"{key} ref")
    sys.path.insert(0, str(DECONV / "src"))
    from deconv_metrics import (  # noqa: F401
        _fit_gamma_pois,
        _nnls_setup,
        _poisson_fit,
        _specificity_weight,
        build_v4,
    )
    avail = None
    for line in Path("/proc/meminfo").read_text().splitlines():
        if line.startswith("MemAvailable:"):
            avail = int(line.split()[1]) * 1024
            break
    if avail is None:
        avail = os.sysconf("SC_AVPHYS_PAGES") * os.sysconf("SC_PAGE_SIZE")
    if avail < 8 * (1 << 30):
        raise SystemExit(f"PREFLIGHT FAIL: available RAM {avail/1e9:.1f} GB < 8 GB")
    TMP.mkdir(parents=True, exist_ok=True)
    print("PREFLIGHT_OK substrates", SUBSTRATES, "pairs", PAIRS, f"ram_avail_gb={avail/1e9:.1f}")


if __name__ == "__main__":
    main()
