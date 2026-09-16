#!/usr/bin/env python
"""Time one openST 400-spot build, decomposed into steps that do not overlap.

The earlier version timed ``build_v4`` under the name ``self_gate`` and then timed
``extract_signature``, ``fit_gamma`` and ``poisson_fit`` separately.  ``build_v4``
performs all of those internally, so the six numbers overlapped and their sum,
60.252 s, was not the duration of any pass.  The label was wrong as well: the
47.961 s attributed to the platform self-gate was a complete composition build.

This version walks the same sequence ``build_v4`` walks, timing each stage once,
so the stages sum to the build they decompose.  It repeats the build after a
warm-up pass and reports mean and spread, which is what a reader budgeting a run
needs and what the review asked for.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.compute_gate import require_compute
from src.paths import BENCH, DECONV, LOCKS, PLOTDATA, TMP
from src.refuse import apply_abstain, should_abstain
from src.subsample import subsample_spots
from src.window_io import t2_done

REPEATS = 5
N_GAMMA, N_FIT = 8, 150
GAMMA_CLIP = (0.1, 10.0)
SEED = 0


def hardware() -> str:
    """Describe the machine in the record rather than typing it into the table."""
    model = ""
    try:
        for line in Path("/proc/cpuinfo").read_text().splitlines():
            if line.startswith("model name"):
                model = line.split(":", 1)[1].strip()
                break
    except OSError:
        pass
    cpus = os.cpu_count() or 0
    try:
        gib = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES") / 1024**3
        ram = f"{gib:.0f} GiB RAM"
    except (ValueError, OSError):
        ram = "RAM unknown"
    py = f"Python {sys.version_info.major}.{sys.version_info.minor}"
    return f"{model or 'CPU unknown'}; {cpus} logical CPUs; {ram}; {py}; CPU only"


def timed_build(spots: str, ref: str, types: list[str], deconv) -> dict[str, float]:
    """Run build_v4's sequence, timing each stage exactly once."""
    _nnls_setup = deconv._nnls_setup
    _specificity_weight = deconv._specificity_weight
    _fit_gamma_pois = deconv._fit_gamma_pois
    _poisson_fit = deconv._poisson_fit
    simplex = deconv.simplex

    times: dict[str, float] = {}

    t0 = time.perf_counter()
    sig, Y, idx, resolved = _nnls_setup(spots, ref, types)
    P = sig / np.clip(sig.sum(0, keepdims=True), 1e-12, None)
    times["signature_setup"] = time.perf_counter() - t0

    t0 = time.perf_counter()
    w = _specificity_weight(P)
    Pw, Yw = P * w[:, None], Y * w[None, :]
    times["specificity_weight"] = time.perf_counter() - t0

    lo, hi = np.log(GAMMA_CLIP[0]), np.log(GAMMA_CLIP[1])
    rng = np.random.default_rng(SEED)
    perm = rng.permutation(Yw.shape[0])
    half = Yw.shape[0] // 2
    A, B = Yw[perm[:half]], Yw[perm[half:]]
    z = np.zeros(Pw.shape[0])

    def dev(lg, Yt):
        S = np.exp(lg)[:, None] * Pw
        W = _poisson_fit(S, Yt, N_FIT)
        r = W @ S.T + 1e-9
        return float(np.mean(np.sum(r - Yt * np.log(r), axis=1)))

    # The self-gate proper: two held-out halves, their deviance comparison, and
    # the clip that turns the comparison into the transferable fraction g.
    t0 = time.perf_counter()
    lgA = _fit_gamma_pois(Pw, A, N_GAMMA, N_FIT, lo, hi)
    lgB = _fit_gamma_pois(Pw, B, N_GAMMA, N_FIT, lo, hi)
    gate = float(np.clip(0.5 * ((dev(z, B) - dev(lgA, B)) / abs(dev(z, B) + 1e-9)
                                + (dev(z, A) - dev(lgB, A)) / abs(dev(z, A) + 1e-9)), 0.0, 1.0))
    times["platform_self_gate"] = time.perf_counter() - t0

    t0 = time.perf_counter()
    lg_full = _fit_gamma_pois(Pw, Yw, N_GAMMA, N_FIT, lo, hi)
    times["platform_factor_fit"] = time.perf_counter() - t0

    t0 = time.perf_counter()
    S = np.exp(gate * lg_full)[:, None] * Pw
    pi_full = simplex(pd.DataFrame(_poisson_fit(S, Yw, N_FIT * 2), index=idx, columns=resolved))
    times["poisson_close"] = time.perf_counter() - t0

    pairs = json.loads((LOCKS / "type_pairs.json").read_text())
    c_star = float(json.loads((LOCKS / "c_star.json").read_text())["value"])
    t0 = time.perf_counter()
    if should_abstain(float(pairs["openst"]["cosine"]), c_star):
        apply_abstain(pi_full, [pairs["openst"]["malignant"]])
    times["reportability_gate"] = time.perf_counter() - t0

    return times


def main() -> None:
    require_compute("05_timing")
    if t2_done():
        print("[T2] skip complete", flush=True)
        return
    sys.path.insert(0, str(DECONV / "src"))
    import deconv_metrics as deconv

    bench = BENCH["openst"]
    truth = pd.read_csv(bench / "truth_proportions.csv", index_col=0)
    types = list(truth.columns)
    spots = TMP / "openst_timing400.h5ad"
    subsample_spots(bench / "benchmark_spots.h5ad", 400, 0, spots)
    ref = bench / "reference_subset.h5ad"

    print("[T2] warm-up pass", flush=True)
    timed_build(str(spots), str(ref), types, deconv)

    runs = []
    for i in range(REPEATS):
        t0 = time.perf_counter()
        times = timed_build(str(spots), str(ref), types, deconv)
        total = time.perf_counter() - t0
        times["_total"] = total
        runs.append(times)
        print(f"[T2] run {i + 1}/{REPEATS}: {total:.3f} s", flush=True)

    # "seconds" stays the mean so the readers that already pull that column keep
    # working; the spread rides alongside it.
    steps = [k for k in runs[0] if not k.startswith("_")]
    rows = []
    for step in steps:
        values = np.array([r[step] for r in runs])
        rows.append({
            "step": step,
            "seconds": round(float(values.mean()), 6),
            "seconds_sd": round(float(values.std(ddof=1)), 6),
        })
    totals = np.array([r["_total"] for r in runs])
    rows.append({
        "step": "build_total",
        "seconds": round(float(totals.mean()), 6),
        "seconds_sd": round(float(totals.std(ddof=1)), 6),
    })

    # The run-to-run summary the review asked for, taken off these same repeats
    # so the decomposition and the spread can never describe different runs.
    summary = [
        {"metric": "n_warm_runs", "value": REPEATS, "note": "same 400-spot openST build"},
        {"metric": "mean_s", "value": round(float(totals.mean()), 3), "note": "wall time"},
        {"metric": "sd_s", "value": round(float(totals.std(ddof=1)), 3), "note": "wall time"},
        {"metric": "cv_pct", "value": round(float(100 * totals.std(ddof=1) / totals.mean()), 2),
         "note": "SD as share of mean"},
        {"metric": "min_s", "value": round(float(totals.min()), 3), "note": "range over runs"},
        {"metric": "max_s", "value": round(float(totals.max()), 3), "note": "range over runs"},
        {"metric": "hardware", "value": hardware(), "note": ""},
    ]

    PLOTDATA.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(PLOTDATA / "T2_timing.csv", index=False)
    pd.DataFrame(summary).to_csv(PLOTDATA / "T2_repeated_timing.csv", index=False)
    print(json.dumps(rows, indent=2))
    covered = sum(r["seconds"] for r in rows if r["step"] != "build_total")
    print(f"[T2] steps sum to {covered:.3f} s against a measured build of {totals.mean():.3f} s")


if __name__ == "__main__":
    main()
