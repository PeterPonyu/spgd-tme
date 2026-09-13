#!/usr/bin/env python
"""revision_v3 / comparator_tangram.py

Fresh external-comparator refit (Task D) to strengthen R2-5. Tangram is run as
an independent, third-party spatial deconvolution method on the CosMx BCC
(realgt3) benchmark and compared head-to-head with the released SPGD baseline
(build_v4) against the same locked cell-count truth, on a matched bounded spot
subset.

Integrity: reads references read-only; writes only to revision_v3/out/. This is
an additive comparison and does not alter any historical number. cell2location
and RCTD are not installed in this environment (see availability note in the
summary); Tangram and scvi-tools are. This provides a genuinely fresh external
refit rather than a re-use of saved comparator output.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

DECONV = Path(os.environ.get("SPGD_DECONV_ROOT", Path(__file__).resolve().parents[1] / "data" / "external" / "deconv-lab"))
OUT = Path(__file__).resolve().parent / "out"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(DECONV / "src"))

BASE = DECONV / "data" / "realgt3_benchmark"
N_SPOTS = 800
SEED = 0
MALIGNANT = "Cancer.cells"


def main() -> None:
    import anndata as ad
    from deconv_metrics import build_v4, point_metrics, simplex

    try:
        import tangram as tg
    except Exception as e:  # noqa: BLE001
        (OUT / "comparator_tangram.json").write_text(
            json.dumps({"status": "SKIPPED", "reason": f"tangram import failed: {e}"}, indent=2) + "\n"
        )
        print("tangram unavailable:", e)
        return

    truth = pd.read_csv(BASE / "truth_proportions.csv", index_col=0)
    types = list(truth.columns)
    spots_path = BASE / "benchmark_spots_counts.h5ad"
    if not spots_path.is_file():
        spots_path = BASE / "benchmark_spots.h5ad"

    # matched bounded spot subset
    rng = np.random.default_rng(SEED)
    sp = ad.read_h5ad(spots_path)
    common = [s for s in truth.index if s in set(sp.obs_names)]
    if len(common) > N_SPOTS:
        common = list(rng.choice(common, N_SPOTS, replace=False))
    sp = sp[common].copy()
    truth = truth.loc[common]

    # SPGD baseline on the matched subset (write subset spots to a temp file)
    tmp = OUT / "_tmp_realgt3_subset.h5ad"
    sp.write_h5ad(tmp)
    pi_spgd, gate = build_v4(str(tmp), str(BASE / "reference_subset.h5ad"), types)
    pi_spgd = pi_spgd.reindex(index=truth.index, columns=types)
    m_spgd = point_metrics(truth, pi_spgd)
    tumor_rmse_spgd = float(np.sqrt(np.mean((pi_spgd[MALIGNANT].to_numpy(float) - truth[MALIGNANT].to_numpy(float)) ** 2)))

    # Tangram cluster-mode mapping
    ref = ad.read_h5ad(BASE / "reference_subset.h5ad")
    acol = next((c for c in ("cell_type", "annotation", "celltype") if c in ref.obs.columns), None)
    ref.obs["cell_type"] = ref.obs[acol].astype(str)
    tg.pp_adatas(ref, sp, genes=None)
    ad_map = tg.map_cells_to_space(
        ref, sp, mode="clusters", cluster_label="cell_type",
        density_prior="rna_count_based", num_epochs=500, device="cpu",
    )
    tg.project_cell_annotations(ad_map, sp, annotation="cell_type")
    pred = sp.obsm["tangram_ct_pred"]
    pred = pred.reindex(columns=types).fillna(0.0)
    pi_tg = simplex(pred).reindex(index=truth.index, columns=types)
    m_tg = point_metrics(truth, pi_tg)
    tumor_rmse_tg = float(np.sqrt(np.mean((pi_tg[MALIGNANT].to_numpy(float) - truth[MALIGNANT].to_numpy(float)) ** 2)))

    result = {
        "benchmark": "CosMx BCC (realgt3)", "n_spots_matched": int(len(truth)), "n_types": len(types),
        "truth": "locked cell-count proportions",
        "SPGD_build_v4": {
            "overall_RMSE": round(m_spgd["RMSE"], 6), "tumor_RMSE": round(tumor_rmse_spgd, 6),
            "PCC_type": round(m_spgd["PCC_type"], 6), "PCC_spot": round(m_spgd["PCC_spot"], 6),
            "JSD": round(m_spgd["JSD"], 6), "gate_g": round(float(gate), 6),
        },
        "Tangram_clusters": {
            "overall_RMSE": round(m_tg["RMSE"], 6), "tumor_RMSE": round(tumor_rmse_tg, 6),
            "PCC_type": round(m_tg["PCC_type"], 6), "PCC_spot": round(m_tg["PCC_spot"], 6),
            "JSD": round(m_tg["JSD"], 6), "num_epochs": 500, "mode": "clusters",
        },
        "note": (
            "Matched bounded subset, same locked truth. Tangram is a fresh independent "
            "refit (not a saved comparator output). cell2location and RCTD/spacexr are "
            "not installed in this environment."
        ),
    }
    (OUT / "comparator_tangram.json").write_text(json.dumps(result, indent=2) + "\n")
    tmp.unlink(missing_ok=True)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
