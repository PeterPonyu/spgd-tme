"""Library-clustered summary of the historical stored neighbor scan.

The manuscript reports the stored four-library CosMx scan separately from the complete
eight-library scan so that the denominator difference stays visible. This script emits the
stored-scan statistics from their own table rather than leaving them as prose.

Reads  revision_v3/analyses/reporting/neighbor_max_rule_all_rows.csv
Writes revision_v3/out/stored_scan_summary.json
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROWS = HERE / "analyses" / "reporting" / "neighbor_max_rule_all_rows.csv"
OUT = HERE / "out" / "stored_scan_summary.json"
C_STAR = 0.80
SEED = 0
B = 10000


def _clustered_bootstrap(groups: list[np.ndarray], stat, rng) -> tuple[float, float]:
    draws = []
    for _ in range(B):
        pick = rng.integers(0, len(groups), len(groups))
        pooled = np.concatenate([groups[i] for i in pick])
        draws.append(stat(pooled))
    return float(np.percentile(draws, 2.5)), float(np.percentile(draws, 97.5))


def main() -> None:
    rows = pd.read_csv(ROWS)
    eligible = rows[rows["eligible"]].copy()

    per_library = eligible.groupby("library").agg(
        n_stored_rows=("cosine", "size"),
        mean_cosine=("cosine", "mean"),
        max_cosine=("cosine", "max"),
        n_ge_cstar=("cosine", lambda s: int((s >= C_STAR).sum())),
    )

    rng = np.random.default_rng(SEED)
    groups = [g["cosine"].to_numpy() for _, g in eligible.groupby("library")]
    mean_lo, mean_hi = _clustered_bootstrap(groups, lambda a: float(a.mean()), rng)
    rng = np.random.default_rng(SEED)
    frac_lo, frac_hi = _clustered_bootstrap(
        groups, lambda a: float((a >= C_STAR).mean()), rng
    )

    result = {
        "scan": "historical stored CosMx reference export, four libraries",
        "c_star": C_STAR,
        "n_all_rows": int(len(rows)),
        "n_eligible_rows": int(len(eligible)),
        "n_excluded_rows": int(len(rows) - len(eligible)),
        "excluded_labels": sorted(
            set(rows.loc[~rows["eligible"], "neighbor"].astype(str))
        ),
        "n_libraries": int(eligible["library"].nunique()),
        "per_library": [
            {
                "library": name,
                "n_eligible_rows": int(row["n_stored_rows"]),
                "n_ge_cstar": int(row["n_ge_cstar"]),
                "mean_cosine": round(float(row["mean_cosine"]), 6),
                "max_cosine": round(float(row["max_cosine"]), 6),
            }
            for name, row in per_library.iterrows()
        ],
        "mean_cosine": round(float(eligible["cosine"].mean()), 6),
        "mean_cosine_ci95_library_clustered": [round(mean_lo, 6), round(mean_hi, 6)],
        "frac_ge_cstar": round(float((eligible["cosine"] >= C_STAR).mean()), 6),
        "frac_ge_cstar_ci95_library_clustered": [round(frac_lo, 6), round(frac_hi, 6)],
        "n_bootstrap": B,
        "note": "Denominators differ from the complete eight-library scan on purpose: this "
        "table is the stored export the historical calls were read from.",
    }

    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
