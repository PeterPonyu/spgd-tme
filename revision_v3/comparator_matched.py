#!/usr/bin/env python
"""revision_v3 / comparator_matched.py

Matched multi-method comparison for R2-5. For each benchmark that has a real
saved comparator output (RCTD via spacexr, or cell2location), SPGD (build_v4) is
fit fresh and both are scored against the same locked truth on the common spot
set. The CosMx BCC (realgt3) row folds in the fresh Tangram refit already
computed in comparator_tangram.json.

Integrity: reads references/saved outputs read-only; writes only to
revision_v3/out/. The saved RCTD/cell2location proportions are the deconv-lab
pipeline's real runs (see each provenance.json); this harness only re-scores
them against truth alongside a fresh SPGD fit. No lock or manuscript number is
modified. realgt4 is intentionally excluded (design guardrail).
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

# deconv-lab is a sibling of spgd-tme under labs/active/; override with SPGD_DECONV_ROOT.
DECONV = Path(os.environ.get("SPGD_DECONV_ROOT", str(Path(__file__).resolve().parents[2] / "deconv-lab")))
OUT = Path(__file__).resolve().parent / "out"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(DECONV / "src"))
from deconv_metrics import build_v4, point_metrics, simplex  # noqa: E402

# benchmark -> (saved comparator dir, comparator label, malignant type)
JOBS = {
    "Xenium (realgt)": ("realgt_benchmark", "results/rctd_realgt", "RCTD", "Invasive_Tumor"),
    "Xenium FLEX (realgt2)": ("realgt2_benchmark", "results/rctd_realgt2", "RCTD", "Invasive_Tumor"),
    "openST (openst)": ("openst_benchmark", "results/c2l_openst", "cell2location", "Tumor"),
}


def tumor_rmse(truth: pd.DataFrame, pred: pd.DataFrame, mal: str) -> float:
    if mal not in truth.columns or mal not in pred.columns:
        return float("nan")
    return float(np.sqrt(np.mean((pred[mal].to_numpy(float) - truth[mal].to_numpy(float)) ** 2)))


def score(truth, pred, mal, common):
    t, p = truth.loc[common], pred.reindex(index=common, columns=truth.columns).fillna(0.0)
    m = point_metrics(t, p)
    return {
        "overall_RMSE": round(m["RMSE"], 6), "tumor_RMSE": round(tumor_rmse(t, simplex(p), mal), 6),
        "PCC_type": round(m["PCC_type"], 6), "PCC_spot": round(m["PCC_spot"], 6), "JSD": round(m["JSD"], 6),
    }


def main() -> None:
    rows = []
    for bench, (data_dir, comp_dir, comp_label, mal) in JOBS.items():
        base = DECONV / "data" / data_dir
        truth = pd.read_csv(base / "truth_proportions.csv", index_col=0)
        types = list(truth.columns)
        comp = pd.read_csv(DECONV / comp_dir / "estimated_proportions.csv", index_col=0)
        comp = comp.reindex(columns=types).fillna(0.0)

        sp = base / "benchmark_spots_counts.h5ad"
        if not sp.is_file():
            sp = base / "benchmark_spots.h5ad"
        pi_spgd, gate = build_v4(str(sp), str(base / "reference_subset.h5ad"), types)

        common = truth.index.intersection(comp.index).intersection(pi_spgd.index)
        n = len(common)
        s_spgd = score(truth, pi_spgd, mal, common)
        s_comp = score(truth, comp, mal, common)
        rows.append({"benchmark": bench, "method": "SPGD (build_v4)", "n_spots": n, "malignant": mal, **s_spgd})
        rows.append({"benchmark": bench, "method": comp_label, "n_spots": n, "malignant": mal, **s_comp})
        print(f"[{bench}] n={n}  SPGD RMSE={s_spgd['overall_RMSE']} tumorRMSE={s_spgd['tumor_RMSE']} | "
              f"{comp_label} RMSE={s_comp['overall_RMSE']} tumorRMSE={s_comp['tumor_RMSE']}")

    # fold in the fresh Tangram BCC refit
    tg = OUT / "comparator_tangram.json"
    if tg.is_file():
        d = json.loads(tg.read_text())
        for label, key in (("SPGD (build_v4)", "SPGD_build_v4"), ("Tangram", "Tangram_clusters")):
            m = d[key]
            rows.append({"benchmark": "CosMx BCC (realgt3)", "method": label, "n_spots": d["n_spots_matched"],
                         "malignant": "Cancer.cells", "overall_RMSE": m["overall_RMSE"], "tumor_RMSE": m["tumor_RMSE"],
                         "PCC_type": m["PCC_type"], "PCC_spot": m["PCC_spot"], "JSD": m["JSD"]})

    df = pd.DataFrame(rows)
    df.to_csv(OUT / "comparator_matched.csv", index=False)
    (OUT / "comparator_matched.json").write_text(json.dumps(rows, indent=2) + "\n")
    print("\n=== matched multi-method comparison (vs locked truth) ===")
    print(df.to_string(index=False))
    print("\nwrote ->", OUT / "comparator_matched.csv")


if __name__ == "__main__":
    main()
