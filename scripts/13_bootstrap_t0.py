#!/usr/bin/env python
"""INTERVAL: B=1000 spot bootstrap on saved t=0 π̂. Zero extra fits."""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.paths import BENCH, PLOTDATA
from src.refuse import apply_abstain, should_abstain
from src.window_io import bootstrap_done

B = 1000
SEED = 0
SUBSTRATES = ("openst", "realgt", "realgt3")
OUT = PLOTDATA / "F3_t0_bootstrap.csv"


def main() -> None:
    if bootstrap_done():
        print(f"[INTERVAL] skip complete {OUT}", flush=True)
        return
    rng = np.random.default_rng(SEED)
    rows = []
    for sub in SUBSTRATES:
        pi_p = PLOTDATA / f"F3_pi_t0_{sub}.csv"
        if not pi_p.is_file():
            raise SystemExit(f"FAIL-CLOSED: missing {pi_p} (run 02 first)")
        pi = pd.read_csv(pi_p, index_col=0)
        truth = pd.read_csv(BENCH[sub] / "truth_proportions.csv", index_col=0)
        truth = truth.loc[pi.index]
        mal = [c for c in pi.columns if c in ("Tumor", "Invasive_Tumor", "Cancer.cells")]
        if not mal:
            raise SystemExit(f"no malignant column in {pi_p}")
        mal = mal[0]
        f3 = pd.read_csv(PLOTDATA / "F3_collinearity_sweep.csv")
        rec = f3[(f3["substrate"] == sub) & (f3["t"].astype(float).abs() < 1e-12)].iloc[0]
        abstain = bool(should_abstain(float(rec["cosine"]), float(rec["c_star"])))
        if abstain:
            apply_abstain(pi.copy(), [mal])
        err = (pi[mal] - truth[mal]).to_numpy(dtype=float)
        if np.isnan(err).any():
            raise SystemExit(f"ungated t=0 π̂ has NaN malignant for {sub}")
        boots = []
        n = len(err)
        for _ in range(B):
            take = rng.integers(0, n, size=n)
            boots.append(float(np.sqrt(np.mean(err[take] ** 2))))
        lo, hi = np.percentile(boots, [2.5, 97.5])
        rows.append(
            {
                "substrate": sub,
                "n_spots": int(n),
                "B": B,
                "tumor_rmse": round(float(np.sqrt(np.mean(err**2))), 6),
                "ci95_lo": round(float(lo), 6),
                "ci95_hi": round(float(hi), 6),
                "abstain": abstain,
            }
        )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT, index=False)
    print("[write]", OUT)


if __name__ == "__main__":
    main()
