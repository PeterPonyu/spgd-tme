#!/usr/bin/env python
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
from src.interpolate import blend_columns, malignant_neighbor_cosine
from src.metrics_tme import tumor_rmse
from src.paths import BENCH, LOCKS, PLOTDATA, TMP
from src.refuse import apply_abstain, should_abstain
from src.signature import extract_signature
from src.spgd_wrap import run_spgd
from src.subsample import subsample_spots
from src.window_io import F3_PART_COLS, f3_done, f3_part_done

SWEEP_N = 400
SWEEP_SEED = 0

T_GRID = [i / 10 for i in range(11)]
SUBSTRATES = ("openst", "realgt", "realgt3")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    require_compute("02_run_collinearity_sweep")
    pairs = json.loads((LOCKS / "type_pairs.json").read_text())
    c_star = float(json.loads((LOCKS / "c_star.json").read_text())["value"])
    before = _sha(LOCKS / "c_star.json")
    PLOTDATA.mkdir(parents=True, exist_ok=True)
    out = PLOTDATA / "F3_collinearity_sweep.csv"
    if f3_done():
        print(f"[F3] skip complete {out}", flush=True)
        return
    rows = []
    for sub in SUBSTRATES:
        part = PLOTDATA / f"F3_part_{sub}.csv"
        if f3_part_done(sub):
            part_df = pd.read_csv(part)
            if F3_PART_COLS - set(part_df.columns):
                raise SystemExit(f"{part} missing {F3_PART_COLS - set(part_df.columns)}")
            rows.extend(part_df.to_dict("records"))
            print(f"[F3] resume {sub} from {part}", flush=True)
            continue
        bench = BENCH[sub]
        truth_full = pd.read_csv(bench / "truth_proportions.csv", index_col=0)
        types = list(truth_full.columns)
        mal = pairs[sub]["malignant"]
        neigh = pairs[sub]["neighbor"]
        _, P0 = extract_signature(bench / "reference_subset.h5ad", types)
        import gc

        gc.collect()
        i = types.index(mal)
        j = types.index(neigh)
        spots = TMP / f"{sub}_sweep{SWEEP_N}.h5ad"
        n_use = subsample_spots(bench / "benchmark_spots.h5ad", SWEEP_N, SWEEP_SEED, spots)
        names = list(ad.read_h5ad(spots).obs_names)
        missing = [n for n in names if n not in truth_full.index]
        if missing:
            raise SystemExit(f"{sub}: {len(missing)} subsampled spots missing from truth")
        truth = truth_full.loc[names]
        ref = bench / "reference_subset.h5ad"
        sub_rows = []
        for t in T_GRID:
            P = blend_columns(P0, i, j, t)
            # Interpolated signature is applied by rewriting a temp ref? 
            # build_v4 reads cells from h5ad, not P. For the law we score
            # cosine on P and run SPGD on the original ref at t=0 only? 
            # Plan: interpolate the signature then run_spgd. That requires
            # injecting P. Use a temporary reference of type-mean cells.
            cos = malignant_neighbor_cosine(P, types, mal, neigh)
            if abs(t) < 1e-12:
                pi, _ = run_spgd(spots, ref, types)
                pi.to_csv(PLOTDATA / f"F3_pi_t0_{sub}.csv")
            else:
                pi = _run_with_blended_signature(spots, ref, types, P)
            # F3 caption is gate-off tumor RMSE: score the raw π̂, then abstain
            # the π̂ used later. Do not feed the NaN malignant column into RMSE.
            rmse = tumor_rmse(truth, pi, mal)
            if should_abstain(cos, c_star):
                pi = apply_abstain(pi, [mal])
            sub_rows.append(
                {
                    "substrate": sub,
                    "t": t,
                    "cosine": round(float(cos), 6),
                    "tumor_rmse": None if pd.isna(rmse) else round(float(rmse), 6),
                    "malignant": mal,
                    "neighbor": neigh,
                    "c_star": c_star,
                    "abstain": bool(should_abstain(cos, c_star)),
                    "n_spots": n_use,
                    "subsample_seed": SWEEP_SEED,
                }
            )
            print(f"[F3] {sub} t={t:.2f} cos={cos:.4f} rmse={rmse}", flush=True)
        pd.DataFrame(sub_rows).to_csv(part, index=False)
        rows.extend(sub_rows)
    pd.DataFrame(rows).to_csv(out, index=False)
    after = _sha(LOCKS / "c_star.json")
    if after != before:
        raise SystemExit("c_star.json changed during sweep")
    print("[write]", out)


def _run_with_blended_signature(spots, ref, types, P):
    """Fit SPGD against an in-memory blended signature via a temp AnnData."""
    import tempfile

    import anndata as ad
    import numpy as np

    src = ad.read_h5ad(ref)
    genes = list(map(str, src.var_names))
    # One synthetic cell per type with the blended profile (library-like counts).
    X = np.clip(P.T * 1000.0, 0, None).astype(np.float32)
    tmp_ref = ad.AnnData(
        X=X,
        obs=pd.DataFrame({"cell_type": types}, index=[f"synth_{t}" for t in types]),
        var=pd.DataFrame(index=genes),
    )
    with tempfile.TemporaryDirectory() as td:
        path = Path(td) / "ref.h5ad"
        tmp_ref.write_h5ad(path)
        pi, _ = run_spgd(spots, path, types)
    return pi


if __name__ == "__main__":
    main()
