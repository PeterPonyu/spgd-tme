from __future__ import annotations

import numpy as np
import pandas as pd

from src.interpolate import column_cosine, malignant_neighbor_cosine


def should_abstain(cos_theta: float, c_star: float) -> bool:
    return float(cos_theta) >= float(c_star)


def refusal_mask(P, malignant, neighbor, c_star, types=None) -> bool:
    """True when the locked malignant/neighbor pair must ABSTAIN.

    ``malignant`` / ``neighbor`` are column indices, or type names when
    ``types`` is supplied. Plan alias for ``should_abstain`` on that cosine.
    """
    if isinstance(malignant, str) or isinstance(neighbor, str):
        if types is None:
            raise TypeError("types required when malignant/neighbor are names")
        cos = malignant_neighbor_cosine(P, list(types), str(malignant), str(neighbor))
    else:
        cos = column_cosine(P, int(malignant), int(neighbor))
    return should_abstain(cos, c_star)


def apply_abstain(pi: pd.DataFrame, types_to_drop: list[str]) -> pd.DataFrame:
    out = pi.copy()
    keep = [c for c in out.columns if c not in types_to_drop]
    for col in types_to_drop:
        if col in out.columns:
            out[col] = np.nan
    if keep:
        block = out[keep].to_numpy(dtype=float)
        s = block.sum(axis=1, keepdims=True)
        s[s == 0] = 1.0
        out.loc[:, keep] = block / s
    return out
