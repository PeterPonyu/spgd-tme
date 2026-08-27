#!/usr/bin/env python
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.paths import LOCKS, PLOTDATA
from src.refuse import should_abstain


def main() -> None:
    f3_path = PLOTDATA / "F3_collinearity_sweep.csv"
    if not f3_path.is_file():
        raise SystemExit(f"FAIL-CLOSED: missing {f3_path}")
    f3 = pd.read_csv(f3_path)
    c_star = float(json.loads((LOCKS / "c_star.json").read_text())["value"])
    rows = []
    for sub, g in f3.groupby("substrate", sort=False):
        refused = g["cosine"].map(lambda c: should_abstain(float(c), c_star))
        rate = float(refused.mean())
        for _, r in g.iterrows():
            refuse = bool(should_abstain(float(r["cosine"]), c_star))
            # F3 tumor_rmse is already ungated (gate-off). Copy it; do not refit.
            rmse_off = r["tumor_rmse"]
            rows.append(
                {
                    "substrate": r["substrate"],
                    "t": r["t"],
                    "cosine": r["cosine"],
                    "rmse_gate_off": rmse_off,
                    "rmse_gate_on": "" if refuse else rmse_off,
                    "refused": refuse,
                    "refusal_rate": rate,
                    "c_star": c_star,
                }
            )
    out = PLOTDATA / "F4_refusal.csv"
    pd.DataFrame(rows).to_csv(out, index=False)
    print("[write]", out)


if __name__ == "__main__":
    main()
