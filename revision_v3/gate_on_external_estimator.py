#!/usr/bin/env python
"""Apply the reportability gate to another estimator's output.

The Discussion claims the missing-coordinate state "can be applied around a
composition estimate, including estimates from another underlying estimator".
Nothing in the paper demonstrates it. The gate reads the reference profile, not
the estimator's output, so the claim should hold by construction -- but "should
hold by construction" is the kind of assertion this revision has already had to
withdraw twice.

Saved RCTD runs exist on three of the locked libraries, one of which the gate
calls KEEP and two of which it calls ABSTAIN. Running the same frozen cutoff over
those outputs shows the gate deciding without touching the estimator, and lets the
withheld coordinate be scored against the truth it would have been reported
against.

Zero non-malignant truth mass is excluded and counted, the way the 400-spot audit
does and the way the full-n path failed to.

Integrity: reads the saved comparator runs and the locked truth read-only; writes
only revision_v3/out/gate_on_external_estimator.{csv,json}.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.paths import BENCH  # noqa: E402

OUT = Path(__file__).resolve().parent / "out"
DECONV = Path(os.environ.get("SPGD_DECONV_ROOT", str(ROOT.parent / "deconv-lab")))
C_STAR = 0.80

# library key -> (public label, saved RCTD run, malignant type, locked cosine)
RUNS = (
    ("realgt3", "CosMx BCC", "results/rctd_realgt3", "Cancer.cells", 0.603666),
    ("realgt", "Xenium", "results/rctd_realgt", "Invasive_Tumor", 0.980196),
    ("realgt2", "Xenium FLEX", "results/rctd_realgt2", "Invasive_Tumor", 0.977005),
)


def rmse(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.sqrt(np.mean((a - b) ** 2)))


def main() -> None:
    rows = []
    for key, label, rel, mal, cosine in RUNS:
        pred_path = DECONV / rel / "estimated_proportions.csv"
        truth_path = Path(BENCH[key]) / "truth_proportions.csv"
        if not pred_path.is_file() or not truth_path.is_file():
            print(f"  {label}: inputs missing, skipped", file=sys.stderr)
            continue
        pred = pd.read_csv(pred_path, index_col=0)
        truth = pd.read_csv(truth_path, index_col=0)
        common = truth.index.intersection(pred.index)
        types = [c for c in truth.columns if c in pred.columns]
        tr, ph = truth.loc[common, types], pred.loc[common, types]

        # The decision comes from the locked reference cosine. It does not read
        # the estimator's output, which is the whole point being demonstrated.
        abstain = cosine >= C_STAR

        mal_err = rmse(tr[mal].to_numpy(float), ph[mal].to_numpy(float))

        keep_cols = [c for c in types if c != mal]
        tb, pb = tr[keep_cols].to_numpy(float), ph[keep_cols].to_numpy(float)
        t_sum, p_sum = tb.sum(1, keepdims=True), pb.sum(1, keepdims=True)
        p_one = p_sum.copy()
        p_one[p_one == 0] = 1.0
        defined = t_sum.ravel() > 0
        cond_err = rmse(pb[defined] / p_one[defined], tb[defined] / t_sum[defined])

        rows.append({
            "library": label,
            "estimator": "RCTD (saved spacexr 2.2.1)",
            "n_spots": len(common),
            "locked_cosine": cosine,
            "gate_decision": "ABSTAIN" if abstain else "KEEP",
            "malignant_coordinate": "withheld" if abstain else "reported",
            "malignant_rmse_of_that_coordinate": round(mal_err, 6),
            "conditional_rmse_after_withholding": round(cond_err, 6),
            "n_zero_nonmalignant_truth_excluded": int((~defined).sum()),
        })
        print(f"  {label:<12} cos={cosine:.4f} -> {'ABSTAIN' if abstain else 'KEEP':<7} "
              f"malignant RMSE {mal_err:.4f} "
              f"({'withheld' if abstain else 'reported'}), conditional {cond_err:.4f}, "
              f"{int((~defined).sum())} rows excluded")

    summary = {
        "c_star": C_STAR,
        "claim_under_test": (
            "the reportability state can be applied around an estimate produced by "
            "another estimator"
        ),
        "how": (
            "The gate reads the locked reference profile, so the same frozen cutoff "
            "decides over a saved RCTD output without the estimator being rerun or "
            "modified. On these three libraries it returns KEEP once and ABSTAIN "
            "twice, which is the same split it returns for the estimator used here."
        ),
        "caveat": (
            "The gate asserts that the reference separates the two programs, not that "
            "the reported coordinate is accurate. The malignant RMSE it withholds and "
            "the one it reports are listed so that distinction can be checked rather "
            "than assumed."
        ),
        "rows": rows,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT / "gate_on_external_estimator.csv", index=False)
    (OUT / "gate_on_external_estimator.json").write_text(json.dumps(summary, indent=2) + "\n")


if __name__ == "__main__":
    main()
