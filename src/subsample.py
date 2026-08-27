from __future__ import annotations

from pathlib import Path

import anndata as ad
import numpy as np


def subsample_spots(spots_h5ad: Path, n: int, seed: int, dest: Path) -> int:
    """Write a seeded subset of spots. Returns n used."""
    spots = ad.read_h5ad(spots_h5ad)
    n_use = min(int(n), int(spots.n_obs))
    rng = np.random.default_rng(seed)
    idx = np.sort(rng.choice(spots.n_obs, size=n_use, replace=False))
    sub = spots[idx].copy()
    dest.parent.mkdir(parents=True, exist_ok=True)
    sub.write_h5ad(dest)
    return n_use
