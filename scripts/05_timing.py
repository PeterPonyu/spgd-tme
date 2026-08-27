#!/usr/bin/env python
from __future__ import annotations

import sys
import time
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.compute_gate import require_compute
from src.paths import BENCH, DECONV, LOCKS, PLOTDATA, TMP
from src.refuse import apply_abstain, should_abstain
from src.signature import extract_signature
from src.subsample import subsample_spots
from src.window_io import t2_done


def main() -> None:
    require_compute("05_timing")
    if t2_done():
        print("[T2] skip complete", flush=True)
        return
    sys.path.insert(0, str(DECONV / "src"))
    from deconv_metrics import _fit_gamma_pois, _poisson_fit, _specificity_weight, build_v4

    bench = BENCH["openst"]
    truth = pd.read_csv(bench / "truth_proportions.csv", index_col=0)
    types = list(truth.columns)
    spots = TMP / "openst_timing400.h5ad"
    subsample_spots(bench / "benchmark_spots.h5ad", 400, 0, spots)
    ref = bench / "reference_subset.h5ad"
    times = {}

    t0 = time.perf_counter()
    _, P = extract_signature(ref, types)
    times["extract_signature"] = time.perf_counter() - t0

    t0 = time.perf_counter()
    w = _specificity_weight(P)
    times["specificity_weight"] = time.perf_counter() - t0

    from deconv_metrics import _nnls_setup

    sig, Y, _, _ = _nnls_setup(str(spots), str(ref), types)
    import numpy as np

    Pw = (sig / np.clip(sig.sum(0, keepdims=True), 1e-12, None)) * w[:, None]
    Yw = Y * w[None, :]
    lo, hi = np.log(0.1), np.log(10.0)
    t0 = time.perf_counter()
    lg = _fit_gamma_pois(Pw, Yw, 8, 150, lo, hi)
    times["fit_gamma"] = time.perf_counter() - t0

    t0 = time.perf_counter()
    pi_full, _ = build_v4(str(spots), str(ref), types)
    times["self_gate"] = time.perf_counter() - t0

    import json

    pairs = json.loads((LOCKS / "type_pairs.json").read_text())
    c_star = float(json.loads((LOCKS / "c_star.json").read_text())["value"])
    t0 = time.perf_counter()
    if should_abstain(float(pairs["openst"]["cosine"]), c_star):
        pi_full = apply_abstain(pi_full, [pairs["openst"]["malignant"]])
    times["refuse"] = time.perf_counter() - t0

    S = np.exp(lg)[:, None] * Pw
    t0 = time.perf_counter()
    _poisson_fit(S, Yw, 300)
    times["poisson_fit"] = time.perf_counter() - t0

    rows = [{"step": k, "seconds": round(v, 6)} for k, v in times.items()]
    PLOTDATA.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(PLOTDATA / "T2_timing.csv", index=False)
    print(rows)


if __name__ == "__main__":
    main()
