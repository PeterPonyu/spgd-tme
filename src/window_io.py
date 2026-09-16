"""Idempotent sitting checks. No fits."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.paths import PLOTDATA

F3_N = 33
F3_PART_N = 11
F5_N = 4
# Stages of one composition build, timed so they do not overlap and so they sum
# to the build they decompose. The earlier set timed the whole build under the
# name "self_gate" beside three of that build's own internal stages.
T2_STEPS = {
    "signature_setup",
    "specificity_weight",
    "platform_self_gate",
    "platform_factor_fit",
    "poisson_close",
    "reportability_gate",
    "build_total",
}
# Run-to-run spread of the same repeats, written beside the decomposition.
T2_REPEAT_METRICS = {
    "n_warm_runs",
    "mean_s",
    "sd_s",
    "cv_pct",
    "min_s",
    "max_s",
    "hardware",
}
F3_PART_COLS = {
    "substrate",
    "t",
    "cosine",
    "tumor_rmse",
    "malignant",
    "neighbor",
    "c_star",
    "abstain",
    "n_spots",
    "subsample_seed",
}


def _csv(path: Path) -> pd.DataFrame | None:
    if not path.is_file() or path.stat().st_size == 0:
        return None
    return pd.read_csv(path)


def f3_done() -> bool:
    df = _csv(PLOTDATA / "F3_collinearity_sweep.csv")
    if df is None or len(df) != F3_N:
        return False
    for sub in ("openst", "realgt", "realgt3"):
        pi = _csv(PLOTDATA / f"F3_pi_t0_{sub}.csv")
        if pi is None or len(pi) == 0:
            return False
    return True


def f3_part_done(sub: str) -> bool:
    df = _csv(PLOTDATA / f"F3_part_{sub}.csv")
    return df is not None and len(df) == F3_PART_N and F3_PART_COLS <= set(df.columns)


def f4_done() -> bool:
    df = _csv(PLOTDATA / "F4_refusal.csv")
    return df is not None and len(df) == F3_N


def f5_done() -> bool:
    df = _csv(PLOTDATA / "F5_donor_transfer.csv")
    if df is None or len(df) != F5_N:
        return False
    return set(df["source"]) <= {"locked", "computed"} and "C_from_D" in set(df["pair"])


def t2_done() -> bool:
    df = _csv(PLOTDATA / "T2_timing.csv")
    if df is None or set(df["step"]) != T2_STEPS:
        return False
    # The run-to-run summary the review asked for comes off the same repeats, so
    # the step is only done once both files exist and agree on the build they
    # describe.  A summary left over from an earlier run reads as incomplete
    # rather than as done, which is how the two drifted apart before.
    rep = _csv(PLOTDATA / "T2_repeated_timing.csv")
    if rep is None or not T2_REPEAT_METRICS <= set(rep["metric"]):
        return False
    mean = float(rep.loc[rep["metric"] == "mean_s", "value"].iloc[0])
    total = float(df.loc[df["step"] == "build_total", "seconds"].iloc[0])
    if abs(mean - total) > 0.001:
        return False
    # A decomposition that does not account for the build it decomposes is not a
    # finished measurement.  An earlier probe left the locked-pair read between
    # two stages, so 1.5 ms of every build sat outside all of them and the
    # printed stages summed to less than the printed total.
    steps = float(df.loc[df["step"] != "build_total", "seconds"].astype(float).sum())
    return abs(steps - total) <= 0.001


def t3_done() -> bool:
    df = _csv(PLOTDATA / "T3_donor_matrix.csv")
    return df is not None and len(df) == F5_N


def bootstrap_done() -> bool:
    df = _csv(PLOTDATA / "F3_t0_bootstrap.csv")
    return df is not None and len(df) == 3


def fulln_done() -> bool:
    df = _csv(PLOTDATA / "F3_t0_fulln.csv")
    return df is not None and len(df) == 3


def emit_done() -> bool:
    return (
        f3_done()
        and f4_done()
        and f5_done()
        and t2_done()
        and t3_done()
        and (PLOTDATA / "CBC_spatial_maps.REUSE").exists()
    )
