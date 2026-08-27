from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

from src.paths import DECONV


def run_spgd(
    spots_h5ad: Path, ref_h5ad: Path, types: list[str]
) -> tuple[pd.DataFrame, float]:
    src = str(DECONV / "src")
    if src not in sys.path:
        sys.path.insert(0, src)
    from deconv_metrics import build_v4

    spots_counts = Path(str(spots_h5ad).replace("benchmark_spots.h5ad", "benchmark_spots_counts.h5ad"))
    spots_path = spots_counts if spots_counts.is_file() else Path(spots_h5ad)
    pi, gate = build_v4(str(spots_path), str(ref_h5ad), list(types))
    return pi, float(gate)
