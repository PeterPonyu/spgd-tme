#!/usr/bin/env python
"""Report the estimated wound-axis gradient beside the truth gradient.

The Abstract says the operators recover the wound axis and then prints
0.8425 -> 0.7518 -> 0.4665. Those three numbers are locked truth:
F9_D_from_C_spot_condition.csv is byte-identical to F9_D_from_C_truth_maps.csv
on the Cancer.cells column over all 3,261 shared spots. The donor-transfer run
persists only aggregate metrics -- RMSE, PCC_type, PCC_spot -- so no stored
output holds the predicted composition per spot, and nothing in the package
shows the estimate reproducing that gradient by condition.

This refits the D-from-C edge, keeps the per-spot simplex, and groups the
estimated malignant column by wound condition against the truth it is supposed
to recover. It writes a new file and overwrites nothing.

Integrity: reads the locked donor pair read-only; writes only
revision_v3/out/wound_axis_prediction.csv and .json.
"""
from __future__ import annotations

import json
import os
import statistics
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.compute_gate import require_compute  # noqa: E402
from src.paths import PLOTDATA  # noqa: E402

OUT = Path(__file__).resolve().parent / "out"
MIRROR = Path(os.environ.get(
    "SPGD_DONOR_PAIRS",
    "/home/zeyufu/Desktop/singlecell-genomics-research/research/results/"
    "SPGD_TME_REVISION/MIRROR_v3_enhanced_20260912/data/donor_pairs",
))
PAIR = "D_from_C"
MALIGNANT = "Cancer.cells"
ORDER = ("Baseline", "Unwound", "Wound")


def main() -> None:
    require_compute("wound_axis_prediction")
    # 04_run_donor_transfer starts with a digit, so it is loaded by path.
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "donor_transfer", ROOT / "scripts" / "04_run_donor_transfer.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    pair_dir = MIRROR / PAIR
    truth = pd.read_csv(pair_dir / "truth_proportions.csv", index_col=0)
    types = list(truth.columns)
    print(f"[wound] refitting {PAIR}: {len(truth)} spots, {len(types)} types", flush=True)
    pi, _ = module.run_spgd(pair_dir / "benchmark_spots_counts.h5ad",
                            pair_dir / "reference_subset.h5ad", types)

    conditions = pd.read_csv(PLOTDATA / "F9_D_from_C_spot_condition.csv")
    conditions = conditions.set_index("spot")
    shared = [s for s in pi.index if s in conditions.index]
    print(f"[wound] {len(shared)} spots carry a wound condition", flush=True)

    rows = []
    for condition in ORDER:
        spots = [s for s in shared if conditions.loc[s, "condition"] == condition]
        if not spots:
            continue
        est = [float(pi.loc[s, MALIGNANT]) for s in spots]
        tru = [float(conditions.loc[s, MALIGNANT]) for s in spots]
        rows.append({
            "condition": condition,
            "n_spots": len(spots),
            "truth_mean": round(statistics.mean(tru), 4),
            "estimate_mean": round(statistics.mean(est), 4),
            "difference": round(statistics.mean(est) - statistics.mean(tru), 4),
        })

    OUT.mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame(rows)
    frame.to_csv(OUT / "wound_axis_prediction.csv", index=False)

    drop_truth = rows[0]["truth_mean"] - rows[-1]["truth_mean"]
    drop_est = rows[0]["estimate_mean"] - rows[-1]["estimate_mean"]
    summary = {
        "pair": PAIR,
        "malignant": MALIGNANT,
        "n_spots_scored": len(shared),
        "truth_drop_baseline_to_wound": round(drop_truth, 4),
        "estimate_drop_baseline_to_wound": round(drop_est, 4),
        "monotone_in_estimate": all(
            rows[i]["estimate_mean"] > rows[i + 1]["estimate_mean"]
            for i in range(len(rows) - 1)),
        "rows": rows,
    }
    (OUT / "wound_axis_prediction.json").write_text(json.dumps(summary, indent=2) + "\n")

    print(frame.to_string(index=False))
    print(f"[wound] truth falls {drop_truth:.4f}, estimate falls {drop_est:.4f}; "
          f"estimate monotone: {summary['monotone_in_estimate']}")


if __name__ == "__main__":
    main()
