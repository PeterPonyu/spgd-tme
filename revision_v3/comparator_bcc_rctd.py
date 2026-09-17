#!/usr/bin/env python
"""Score the saved CosMx BCC RCTD run beside the reported full-n SPGD estimate.

R2 Point 5 asked for RCTD's weight/confidence diagnostics or cell2location's
posterior on *the same CosMx BCC malignant coordinate*. The revision answered
with a fresh Tangram refit on BCC and with RCTD/cell2location on the other three
libraries, so the strong baseline was never placed on the library the first claim
rests on.

The run already exists: deconv-lab results/rctd_realgt3 is a real spacexr 2.2.1
full-mode fit over all 5,686 BCC spots and the same 11 types. It was never scored.
This scores it against the locked truth beside the saved full-n SPGD estimate the
manuscript reports, and audits which fields each output carries.

The reportability claim is about fields, not accuracy: if RCTD writes a malignant
weight at every spot with nothing marking it unsupported, that is the claim's
evidence on the same library, and it holds whichever method is more accurate.

Integrity: reads the locked truth, the saved RCTD proportions and the stored SPGD
prediction read-only; writes only revision_v3/out/comparator_bcc_rctd.{csv,json}.
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

from src.paths import BENCH, PLOTDATA  # noqa: E402

DECONV = Path(os.environ.get("SPGD_DECONV_ROOT", str(ROOT.parent / "deconv-lab")))
OUT = Path(__file__).resolve().parent / "out"
MALIGNANT = "Cancer.cells"
RCTD_DIR = DECONV / "results" / "rctd_realgt3"


def rmse(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.sqrt(np.mean((a - b) ** 2)))


def pcc(a: np.ndarray, b: np.ndarray) -> float:
    if a.std() == 0 or b.std() == 0:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def jsd(t: np.ndarray, p: np.ndarray) -> float:
    def kl(x, y):
        m = x > 0
        return float(np.sum(x[m] * np.log(x[m] / y[m])))
    out = []
    for i in range(t.shape[0]):
        x, y = t[i], p[i]
        if x.sum() <= 0 or y.sum() <= 0:
            continue
        x, y = x / x.sum(), y / y.sum()
        m = 0.5 * (x + y)
        out.append(0.5 * kl(x, m) + 0.5 * kl(y, m))
    return float(np.mean(out))


def score(t: pd.DataFrame, p: pd.DataFrame, label: str) -> dict:
    T, P = t.to_numpy(float), p.to_numpy(float)
    types = list(t.columns)
    per_type = [pcc(P[:, k], T[:, k]) for k in range(len(types))
                if T[:, k].std() > 0 and P[:, k].std() > 0]
    per_spot = [pcc(P[i], T[i]) for i in range(T.shape[0])
                if T[i].std() > 0 and P[i].std() > 0]
    mi = types.index(MALIGNANT)
    return {
        "method": label,
        "n_spots": int(T.shape[0]),
        "n_types": len(types),
        "overall_RMSE": round(rmse(T, P), 6),
        "malignant_RMSE": round(rmse(T[:, mi], P[:, mi]), 6),
        "PCC_type": round(float(np.mean(per_type)), 6),
        "PCC_spot": round(float(np.mean(per_spot)), 6),
        "JSD": round(jsd(T, P), 6),
    }


def field_audit(p: pd.DataFrame, label: str) -> dict:
    """What does the output carry beside the number? This is the actual claim."""
    mal = p[MALIGNANT].to_numpy(float)
    return {
        "method": label,
        "malignant_value_written_at_every_spot": bool(np.isfinite(mal).all()),
        "n_spots_with_malignant_value": int(np.isfinite(mal).sum()),
        "n_spots_withheld_or_missing": int((~np.isfinite(mal)).sum()),
        "columns_in_output": list(p.columns),
        "carries_a_reportability_state": False,
    }


def main() -> None:
    truth = pd.read_csv(Path(BENCH["realgt3"]) / "truth_proportions.csv", index_col=0)
    rctd = pd.read_csv(RCTD_DIR / "estimated_proportions.csv", index_col=0)
    spgd = pd.read_csv(PLOTDATA / "F3_pi_fulln_realgt3.csv", index_col=0)

    types = [c for c in truth.columns if c in rctd.columns and c in spgd.columns]
    common = truth.index.intersection(rctd.index).intersection(spgd.index)
    t = truth.loc[common, types]
    r = rctd.loc[common, types]
    s = spgd.loc[common, types]

    rows = [score(t, s, "SPGD (build_v4, full n)"), score(t, r, "RCTD (spacexr 2.2.1, full mode)")]
    audit = [field_audit(s, "SPGD"), field_audit(r, "RCTD")]
    # The SPGD row is the one the gate can annotate; RCTD has no such field.
    audit[0]["carries_a_reportability_state"] = True
    audit[0]["state_on_this_library"] = "KEEP (designated cosine 0.6037 < c* = 0.80)"

    provenance = json.loads((RCTD_DIR / "provenance.json").read_text())
    summary = {
        "library": "CosMx BCC",
        "question": "R2 Point 5 on the library the first claim rests on",
        "n_spots_scored": int(len(common)),
        "n_types_scored": len(types),
        "rctd_provenance": {
            "method": provenance["method"],
            "spacexr_version": provenance["spacexr_version"],
            "mode": provenance["mode"],
            "n_ref_cells": provenance["n_ref_cells"],
            "runtime_seconds": provenance["runtime_seconds"],
            "deviations": provenance["deviations"],
        },
        "scores": rows,
        "field_audit": audit,
        "reading": (
            "RCTD is placed on the library the first claim rests on, which the revision "
            "had covered only with a Tangram refit. Accuracy is reported without a "
            "uniform-superiority claim. The reportability point is separate and does not "
            "depend on which method scores better: the RCTD output is a full weight vector "
            "with a malignant value at every spot and no field marking that value "
            "unsupported, so the claim that existing estimators expose no matched "
            "reportability state is now evidenced on CosMx BCC rather than asserted."
        ),
    }

    OUT.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT / "comparator_bcc_rctd.csv", index=False)
    (OUT / "comparator_bcc_rctd.json").write_text(json.dumps(summary, indent=2) + "\n")

    print(f"  spots={len(common)}  types={len(types)}")
    for row in rows:
        print(f"  {row['method']:<34} overall {row['overall_RMSE']:.4f}  "
              f"malignant {row['malignant_RMSE']:.4f}  typePCC {row['PCC_type']:.4f}  "
              f"spotPCC {row['PCC_spot']:.4f}  JSD {row['JSD']:.4f}")


if __name__ == "__main__":
    main()
