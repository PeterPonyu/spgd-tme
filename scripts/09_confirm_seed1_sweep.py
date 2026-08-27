#!/usr/bin/env python
"""P4b mutex fallback: seed=1 t=0 ×3 only. Not an 11-point second grid."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import anndata as ad
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.compute_gate import require_compute
from src.interpolate import malignant_neighbor_cosine
from src.metrics_tme import tumor_rmse
from src.paths import BENCH, LOCKS, PLOTDATA, TMP
from src.refuse import apply_abstain, should_abstain
from src.signature import extract_signature
from src.spgd_wrap import run_spgd
from src.subsample import subsample_spots

SWEEP_N = 400
SWEEP_SEED = 1
SUBSTRATES = ("openst", "realgt", "realgt3")
OUT = PLOTDATA / "F3_seed1_t0.csv"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    require_compute("09_confirm_seed1_sweep")
    if OUT.exists() and OUT.stat().st_size > 0:
        raise SystemExit(f"REFUSING overwrite: {OUT}")
    if not (PLOTDATA / "F3_collinearity_sweep.csv").is_file():
        raise SystemExit("FAIL-CLOSED: run Q2 before P4b")
    pairs = json.loads((LOCKS / "type_pairs.json").read_text())
    c_star = float(json.loads((LOCKS / "c_star.json").read_text())["value"])
    before = _sha(LOCKS / "c_star.json")
    rows = []
    for sub in SUBSTRATES:
        bench = BENCH[sub]
        truth_full = pd.read_csv(bench / "truth_proportions.csv", index_col=0)
        types = list(truth_full.columns)
        mal = pairs[sub]["malignant"]
        neigh = pairs[sub]["neighbor"]
        _, P0 = extract_signature(bench / "reference_subset.h5ad", types)
        spots = TMP / f"{sub}_sweep{SWEEP_N}_seed{SWEEP_SEED}.h5ad"
        n_use = subsample_spots(bench / "benchmark_spots.h5ad", SWEEP_N, SWEEP_SEED, spots)
        names = list(ad.read_h5ad(spots).obs_names)
        truth = truth_full.loc[names]
        pi, _ = run_spgd(spots, bench / "reference_subset.h5ad", types)
        cos = malignant_neighbor_cosine(P0, types, mal, neigh)
        if should_abstain(cos, c_star):
            pi = apply_abstain(pi, [mal])
        rmse = tumor_rmse(truth, pi, mal)
        rows.append(
            {
                "substrate": sub,
                "t": 0.0,
                "cosine": round(float(cos), 6),
                "tumor_rmse": None if pd.isna(rmse) else round(float(rmse), 6),
                "malignant": mal,
                "neighbor": neigh,
                "c_star": c_star,
                "abstain": bool(should_abstain(cos, c_star)),
                "n_spots": n_use,
                "subsample_seed": SWEEP_SEED,
                "source": "confirm_seed1_t0",
            }
        )
        print(f"[P4b] {sub} t=0 cos={cos:.4f} rmse={rmse}")
    PLOTDATA.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT, index=False)
    if _sha(LOCKS / "c_star.json") != before:
        raise SystemExit("c_star.json changed during seed1 t=0")
    print("[write]", OUT)


if __name__ == "__main__":
    main()
