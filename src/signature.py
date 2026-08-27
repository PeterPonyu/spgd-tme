from __future__ import annotations

from pathlib import Path

import numpy as np


def extract_signature(ref_h5ad: Path, types: list[str]) -> tuple[list[str], np.ndarray]:
    """Library-normalized mean signature P (genes × types), columns sum to 1."""
    import anndata as ad

    ref = ad.read_h5ad(ref_h5ad)
    anno_col = None
    for cand in ("annotation", "cell_type", "celltype", "obs_annotation"):
        if cand in ref.obs.columns:
            anno_col = cand
            break
    if anno_col is None:
        raise KeyError(f"no annotation column in reference obs: {list(ref.obs.columns)}")
    X = ref.layers["raw"] if "raw" in ref.layers else ref.X
    X = np.asarray(X.todense()) if hasattr(X, "todense") else np.asarray(X)
    libr = X.sum(1, keepdims=True)
    libr[libr == 0] = 1.0
    scale = float(np.median(libr))
    Xn = X / libr * scale
    anno = ref.obs[anno_col].astype(str).to_numpy()
    P = np.zeros((X.shape[1], len(types)), dtype=float)
    missing = [ty for ty in types if (anno == ty).sum() == 0]
    if missing:
        raise ValueError(f"{ref_h5ad}: no cells for types {missing} in {anno_col}")
    for k, ty in enumerate(types):
        sel = anno == ty
        P[:, k] = Xn[sel].mean(0)
    col = P.sum(0, keepdims=True)
    col[col == 0] = 1.0
    P = P / col
    return list(map(str, ref.var_names)), P
