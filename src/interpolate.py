from __future__ import annotations

import numpy as np


def column_cosine(P: np.ndarray, i: int, j: int) -> float:
    a = P[:, i]
    b = P[:, j]
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def blend_columns(P: np.ndarray, i: int, j: int, t: float) -> np.ndarray:
    """Replace column i with (1-t)*P_i + t*P_j, then renormalize columns."""
    out = np.array(P, dtype=float, copy=True)
    out[:, i] = (1.0 - t) * P[:, i] + t * P[:, j]
    col = out.sum(0, keepdims=True)
    col[col == 0] = 1.0
    return out / col


def malignant_neighbor_cosine(
    P: np.ndarray, types: list[str], malignant: str, neighbor: str
) -> float:
    i = types.index(malignant)
    j = types.index(neighbor)
    return column_cosine(P, i, j)
