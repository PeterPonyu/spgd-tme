#!/usr/bin/env python
"""Re-score the full-n conditional composition, excluding undefined rows.

`downstream_and_gate_fulln.abstain_renormalize` divides the non-malignant block
by its row sum and sets a zero sum to 1.0. A spot whose truth is entirely
malignant then keeps an all-zero vector and is scored as though that were its
conditional composition. On CosMx BCC full n that is 1,553 of 5,686 spots, 27.3
per cent, and it inflates the reported conditional RMSE from 0.1876 to 0.2140.

"Given the non-malignant mass, how is it distributed" has no answer when there is
no non-malignant mass. The 400-spot audit already excludes those rows and counts
them (66/400 openST, 3/400 Xenium, 109/400 CosMx); the full-n path did not, so
the two analyses in the same paper used different rules.

This recomputes both so the difference is on the record, and reports the
exclusion count the way the 400-spot audit does.

Integrity: reads the locked benchmark truth and the stored full-n prediction
read-only; writes only revision_v3/out/conditional_rmse_fulln.{csv,json}.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.paths import BENCH, PLOTDATA  # noqa: E402

OUT = Path(__file__).resolve().parent / "out"
MALIGNANT = "Cancer.cells"


def rmse(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.sqrt(np.mean((a - b) ** 2)))


def main() -> None:
    truth = pd.read_csv(Path(BENCH["realgt3"]) / "truth_proportions.csv", index_col=0)
    pi = pd.read_csv(PLOTDATA / "F3_pi_fulln_realgt3.csv", index_col=0)
    common = truth.index.intersection(pi.index)
    types = [c for c in truth.columns if c in pi.columns]
    tr, ph = truth.loc[common, types], pi.loc[common, types]

    full = rmse(tr.to_numpy(float), ph.to_numpy(float))

    keep = [c for c in types if c != MALIGNANT]
    tb, pb = tr[keep].to_numpy(float), ph[keep].to_numpy(float)
    t_sum, p_sum = tb.sum(1, keepdims=True), pb.sum(1, keepdims=True)

    # The shipped behaviour, kept so the superseded number stays reproducible.
    t_one, p_one = t_sum.copy(), p_sum.copy()
    t_one[t_one == 0] = 1.0
    p_one[p_one == 0] = 1.0
    scripted = rmse(pb / p_one, tb / t_one)

    defined = (t_sum.ravel() > 0)
    corrected = rmse(pb[defined] / p_one[defined], tb[defined] / t_sum[defined])

    rows = [
        {"quantity": "full composition RMSE", "n_spots": len(common),
         "dimension": len(types), "value": round(full, 6),
         "note": "all types including the malignant coordinate"},
        {"quantity": "conditional RMSE, zero-mass rows scored", "n_spots": len(common),
         "dimension": len(keep), "value": round(scripted, 6),
         "note": "superseded: an all-zero row is not a conditional composition"},
        {"quantity": "conditional RMSE, zero-mass rows excluded",
         "n_spots": int(defined.sum()), "dimension": len(keep),
         "value": round(corrected, 6),
         "note": "matches the exclusion rule the 400-spot audit already uses"},
    ]
    summary = {
        "library": "CosMx BCC",
        "n_spots_full": len(common),
        "n_zero_nonmalignant_truth_excluded": int((~defined).sum()),
        "zero_mass_fraction": round(float((~defined).mean()), 4),
        "full_composition_rmse": round(full, 6),
        "conditional_rmse_scored_with_zero_rows": round(scripted, 6),
        "conditional_rmse_excluding_zero_rows": round(corrected, 6),
        "comparability": (
            "The full-composition RMSE is an 11-type score including the malignant "
            "coordinate; the conditional RMSE is a 10-type score of a different "
            "estimand after that coordinate is withheld. They are not two "
            "measurements of one quantity and their ordering does not establish "
            "that one neighbour rule is more accurate than another."
        ),
        "rows": rows,
    }

    OUT.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT / "conditional_rmse_fulln.csv", index=False)
    (OUT / "conditional_rmse_fulln.json").write_text(json.dumps(summary, indent=2) + "\n")

    print(pd.DataFrame(rows).to_string(index=False))
    print(f"[cond] {(~defined).sum()} of {len(common)} spots "
          f"({100 * (~defined).mean():.1f}%) have no non-malignant truth mass")
    print(f"[cond] conditional RMSE {scripted:.4f} -> {corrected:.4f} once they are excluded")


if __name__ == "__main__":
    main()
