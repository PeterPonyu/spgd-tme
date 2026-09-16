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
# The donor pairs live in the response workspace beside this repository, not in
# it. Point SPGD_DONOR_PAIRS at them; the default is the sibling layout and
# carries no machine-specific prefix.
MIRROR = Path(os.environ.get("SPGD_DONOR_PAIRS", str(
    ROOT.parents[2] / "singlecell-genomics-research/research/results/SPGD_TME_REVISION"
    / "MIRROR_v3_enhanced_20260912/data/donor_pairs")))
PAIR = "D_from_C"
MALIGNANT = "Cancer.cells"
# The Abstract claims three things move together, so all three are scored.
TRACKED_TYPES = ("Cancer.cells", "Fibroblast", "MoMacDC")
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

    # The refit has to be the same fit the paper reports, or the table below
    # describes a different run. Scored against the pair's own locked truth.
    import numpy as np
    shared_idx = [s for s in pi.index if s in truth.index]
    a = truth.loc[shared_idx, list(pi.columns)].to_numpy(float)
    b = pi.loc[shared_idx].to_numpy(float)
    refit = {
        "RMSE": round(float(np.sqrt(np.mean((a - b) ** 2))), 6),
        "tumor_RMSE": round(float(np.sqrt(np.mean(
            (truth.loc[shared_idx, MALIGNANT].to_numpy(float)
             - pi.loc[shared_idx, MALIGNANT].to_numpy(float)) ** 2))), 6),
        "PCC_spot": round(float(np.mean([
            np.corrcoef(a[i], b[i])[0, 1] for i in range(len(a))
            if a[i].std() > 0 and b[i].std() > 0])), 6),
    }
    published = {r["pair"]: r for r in pd.read_csv(
        PLOTDATA / "F5_donor_transfer.csv").to_dict("records")}.get(PAIR, {})
    print(f"[wound] refit RMSE {refit['RMSE']} against published "
          f"{published.get('RMSE', 'n/a')}", flush=True)

    # The per-spot matrix, so the next reader does not have to refit to check.
    pi.loc[shared].to_csv(OUT / "wound_axis_per_spot_estimate.csv")

    rows = []
    for condition in ORDER:
        spots = [s for s in shared if conditions.loc[s, "condition"] == condition]
        if not spots:
            continue
        row = {"condition": condition, "n_spots": len(spots)}
        for kind in TRACKED_TYPES:
            if kind not in pi.columns or kind not in conditions.columns:
                continue
            est = [float(pi.loc[s, kind]) for s in spots]
            tru = [float(conditions.loc[s, kind]) for s in spots]
            row[f"{kind}_truth"] = round(statistics.mean(tru), 4)
            row[f"{kind}_estimate"] = round(statistics.mean(est), 4)
            row[f"{kind}_difference"] = round(statistics.mean(est) - statistics.mean(tru), 4)
        rows.append(row)

    OUT.mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame(rows)
    frame.to_csv(OUT / "wound_axis_prediction.csv", index=False)

    gradients = {}
    for kind in TRACKED_TYPES:
        tk, ek = f"{kind}_truth", f"{kind}_estimate"
        if tk not in rows[0]:
            continue
        rising = rows[0][tk] < rows[-1][tk]
        gradients[kind] = {
            "truth_change_baseline_to_wound": round(rows[-1][tk] - rows[0][tk], 4),
            "estimate_change_baseline_to_wound": round(rows[-1][ek] - rows[0][ek], 4),
            "direction_agrees": (rows[-1][ek] > rows[0][ek]) == rising,
            "estimate_monotone": all(
                (rows[i + 1][ek] > rows[i][ek]) == rising for i in range(len(rows) - 1)),
        }
    summary = {
        "pair": PAIR,
        "types_scored": list(gradients),
        "n_spots_scored": len(shared),
        "refit_metrics": refit,
        "published_metrics": {k: published.get(k) for k in ("RMSE", "PCC_spot", "tumor_rmse")},
        "environment": {
            "python": sys.version.split()[0],
            "numpy": __import__("numpy").__version__,
            "pandas": pd.__version__,
        },
        "gradients": gradients,
        "rows": rows,
    }
    (OUT / "wound_axis_prediction.json").write_text(json.dumps(summary, indent=2) + "\n")

    print(frame.to_string(index=False))
    for kind, g in gradients.items():
        print(f"[wound] {kind:<14} truth {g['truth_change_baseline_to_wound']:+.4f}  "
              f"estimate {g['estimate_change_baseline_to_wound']:+.4f}  "
              f"direction agrees: {g['direction_agrees']}  monotone: {g['estimate_monotone']}")


if __name__ == "__main__":
    main()
