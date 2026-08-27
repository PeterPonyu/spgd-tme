"""Idempotent sitting checks. No fits."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.paths import PLOTDATA

F3_N = 33
F3_PART_N = 11
F5_N = 4
T2_STEPS = {
    "extract_signature",
    "specificity_weight",
    "fit_gamma",
    "self_gate",
    "refuse",
    "poisson_fit",
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
    return df is not None and set(df["step"]) == T2_STEPS


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
