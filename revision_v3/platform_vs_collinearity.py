"""Library-clustered permutation test of platform family against pair collinearity.

Reviewer 2 point 4 asks whether the frozen cutoff separates collinear malignant-neighbor
pairs or assay platforms. The library-level design has eight points, so the test is run on
the complete eligible pair scan and the platform label is permuted at the library level:
neighbor pairs inside one library share a malignant column and are not exchangeable.

Reads  revision_v3/out/complete_eligible_scan.csv
Writes revision_v3/out/platform_vs_collinearity.json
"""

from __future__ import annotations

import itertools
import json
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
SCAN = HERE / "out" / "complete_eligible_scan.csv"
OUT = HERE / "out" / "platform_vs_collinearity.json"
C_STAR = 0.80
SEED = 0
N_PERM = 20000


def _family(library: str) -> str:
    if library.startswith("CosMx"):
        return "CosMx"
    if library.startswith("Xenium"):
        return "Xenium"
    return "openST"


def _between_family_spread(lib_stat: pd.Series, lib_family: pd.Series) -> float:
    """Range of family means over library-level statistics."""
    means = lib_stat.groupby(lib_family).mean()
    return float(means.max() - means.min())


def main() -> None:
    scan = pd.read_csv(SCAN)
    scan["family"] = scan["library"].map(_family)

    # Library-level statistics: these are the exchangeable units under the null.
    lib = scan.groupby("library").agg(
        n_pairs=("cosine", "size"),
        mean_cosine=("cosine", "mean"),
        max_cosine=("cosine", "max"),
        frac_ge=("cosine", lambda s: float((s >= C_STAR).mean())),
    )
    lib["family"] = [_family(name) for name in lib.index]

    observed_cos = _between_family_spread(lib["mean_cosine"], lib["family"])
    observed_frac = _between_family_spread(lib["frac_ge"], lib["family"])

    # Exact enumeration is feasible: 8 libraries into fixed family sizes (5 CosMx,
    # 2 Xenium, 1 openST). Enumerate every assignment rather than sampling.
    families = list(lib["family"])
    counts = pd.Series(families).value_counts().to_dict()
    names = list(lib.index)
    ge_cos = 0
    ge_frac = 0
    total = 0
    for cosmx in itertools.combinations(range(len(names)), counts["CosMx"]):
        rest = [i for i in range(len(names)) if i not in cosmx]
        for xen in itertools.combinations(rest, counts["Xenium"]):
            perm = []
            for i in range(len(names)):
                if i in cosmx:
                    perm.append("CosMx")
                elif i in xen:
                    perm.append("Xenium")
                else:
                    perm.append("openST")
            perm = pd.Series(perm, index=lib.index)
            total += 1
            if _between_family_spread(lib["mean_cosine"], perm) >= observed_cos - 1e-12:
                ge_cos += 1
            if _between_family_spread(lib["frac_ge"], perm) >= observed_frac - 1e-12:
                ge_frac += 1

    # Within-CosMx spread, for the same statistic, as the competing explanation.
    cosmx_libs = lib[lib["family"] == "CosMx"]
    within_cosmx_range = float(cosmx_libs["mean_cosine"].max() - cosmx_libs["mean_cosine"].min())

    rng = np.random.default_rng(SEED)
    boot = []
    lib_groups = [g["cosine"].to_numpy() for _, g in scan.groupby("library")]
    for _ in range(N_PERM // 5):
        pick = rng.integers(0, len(lib_groups), len(lib_groups))
        pooled = np.concatenate([lib_groups[i] for i in pick])
        boot.append(float((pooled >= C_STAR).mean()))
    boot = np.asarray(boot)

    result = {
        "question": "Does assay platform, rather than pair collinearity, explain which "
        "malignant-neighbor pairs reach the frozen cutoff?",
        "c_star": C_STAR,
        "n_pairs": int(len(scan)),
        "n_libraries": int(len(lib)),
        "n_platform_families": int(lib["family"].nunique()),
        "exchangeable_unit": "library",
        "permutation": "exact enumeration of library-to-family assignments",
        "n_assignments": total,
        "library_table": [
            {
                "library": name,
                "family": row["family"],
                "n_pairs": int(row["n_pairs"]),
                "mean_cosine": round(float(row["mean_cosine"]), 6),
                "max_cosine": round(float(row["max_cosine"]), 6),
                "frac_ge_cstar": round(float(row["frac_ge"]), 6),
            }
            for name, row in lib.iterrows()
        ],
        "observed_between_family_range_mean_cosine": round(observed_cos, 6),
        "p_between_family_mean_cosine": round(ge_cos / total, 6),
        "observed_between_family_range_frac_ge": round(observed_frac, 6),
        "p_between_family_frac_ge": round(ge_frac / total, 6),
        "within_cosmx_range_mean_cosine": round(within_cosmx_range, 6),
        "pooled_frac_ge_cstar": round(float((scan["cosine"] >= C_STAR).mean()), 6),
        "pooled_frac_ge_cstar_ci95_library_clustered": [
            round(float(np.percentile(boot, 2.5)), 6),
            round(float(np.percentile(boot, 97.5)), 6),
        ],
        "interpretation": "With eight libraries in three families the permutation null is "
        "coarse and the test is underpowered by construction. The reported p-values are "
        "therefore a bound on what this design can establish, not a demonstration of "
        "platform independence.",
    }

    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
