#!/usr/bin/env python
"""P4c: required confirmation — full-n t=0 only. Does not overwrite F3 sweep."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.compute_gate import require_compute
from src.interpolate import malignant_neighbor_cosine
from src.metrics_tme import tumor_rmse
from src.paths import BENCH, LOCKS, PLOTDATA
from src.refuse import apply_abstain, should_abstain
from src.signature import extract_signature
from src.spgd_wrap import run_spgd
from src.window_io import fulln_done

OUT = PLOTDATA / "F3_t0_fulln.csv"
SUBSTRATES = ("openst", "realgt", "realgt3")
PART_COLS = {
    "substrate",
    "t",
    "n_spots",
    "n_pred",
    "n_truth",
    "cosine",
    "tumor_rmse",
    "malignant",
    "neighbor",
    "c_star",
    "abstain",
    "source",
}


def _part_path(sub: str) -> Path:
    return PLOTDATA / f"F3_fulln_part_{sub}.csv"


def _part_valid(path: Path, sub: str) -> bool:
    if not path.is_file() or path.stat().st_size == 0:
        return False
    df = pd.read_csv(path)
    if len(df) != 1 or not PART_COLS <= set(df.columns):
        return False
    return str(df.iloc[0]["substrate"]) == sub


def main() -> None:
    require_compute("10_confirm_t0_fulln")
    if fulln_done():
        print(f"[P4c] skip complete {OUT}", flush=True)
        return
    pairs = json.loads((LOCKS / "type_pairs.json").read_text())
    c_star = float(json.loads((LOCKS / "c_star.json").read_text())["value"])
    PLOTDATA.mkdir(parents=True, exist_ok=True)
    rows = []
    for sub in SUBSTRATES:
        part = _part_path(sub)
        if _part_valid(part, sub):
            rows.append(pd.read_csv(part).iloc[0].to_dict())
            print(f"[P4c] resume {sub} from {part}", flush=True)
            continue
        bench = BENCH[sub]
        truth = pd.read_csv(bench / "truth_proportions.csv", index_col=0)
        types = list(truth.columns)
        mal = pairs[sub]["malignant"]
        neigh = pairs[sub]["neighbor"]
        _, P = extract_signature(bench / "reference_subset.h5ad", types)
        cos = malignant_neighbor_cosine(P, types, mal, neigh)
        spots = bench / "benchmark_spots.h5ad"
        ref = bench / "reference_subset.h5ad"
        pi, _ = run_spgd(spots, ref, types)
        n_pred = int(len(pi))
        n_truth = int(len(truth))
        # Ungated RMSE on the full truth. Do not truth.loc[pi.index].
        # tumor_rmse errors if pred misses truth spots.
        rmse = tumor_rmse(truth, pi, mal)
        abstain = bool(should_abstain(cos, c_star))
        if abstain:
            apply_abstain(pi.copy(), [mal])
        row = {
            "substrate": sub,
            "t": 0.0,
            "n_spots": n_pred,
            "n_pred": n_pred,
            "n_truth": n_truth,
            "cosine": round(float(cos), 6),
            "tumor_rmse": None if pd.isna(rmse) else round(float(rmse), 6),
            "malignant": mal,
            "neighbor": neigh,
            "c_star": c_star,
            "abstain": abstain,
            "source": "confirm_t0_fulln",
        }
        pd.DataFrame([row]).to_csv(part, index=False)
        rows.append(row)
        print(
            f"[P4c] {sub} n_pred={n_pred} n_truth={n_truth} rmse={rmse} abstain={abstain}",
            flush=True,
        )
    pd.DataFrame(rows).to_csv(OUT, index=False)
    print("[write]", OUT)


if __name__ == "__main__":
    main()
