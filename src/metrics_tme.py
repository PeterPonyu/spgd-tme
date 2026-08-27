from __future__ import annotations

import numpy as np
import pandas as pd


def _align(truth: pd.DataFrame, pred: pd.DataFrame) -> pd.DataFrame:
    missing = truth.index.difference(pred.index)
    if len(missing):
        raise ValueError(f"pred missed {len(missing)} truth spots")
    return pred.loc[truth.index]


def tumor_rmse(truth: pd.DataFrame, pred: pd.DataFrame, malignant: str) -> float:
    pred = _align(truth, pred)
    a = truth[malignant].to_numpy(dtype=float)
    b = pred[malignant].to_numpy(dtype=float)
    if np.isnan(b).any():
        return float("nan")
    return float(np.sqrt(np.mean((b - a) ** 2)))


def refusal_rate(mask: pd.Series) -> float:
    x = mask.astype(bool)
    if len(x) == 0:
        return float("nan")
    return float(x.mean())


def point_rmse(truth: pd.DataFrame, pred: pd.DataFrame) -> float:
    pred = _align(truth, pred).reindex(columns=truth.columns)
    t = truth.to_numpy(dtype=float)
    p = pred.to_numpy(dtype=float)
    return float(np.sqrt(np.mean((p - t) ** 2)))


def pcc_type(truth: pd.DataFrame, pred: pd.DataFrame) -> float:
    pred = _align(truth, pred).reindex(columns=truth.columns)
    vals = []
    for col in truth.columns:
        a = truth[col].to_numpy(dtype=float)
        b = pred[col].to_numpy(dtype=float)
        if np.std(a) == 0 or np.std(b) == 0:
            continue
        vals.append(float(np.corrcoef(a, b)[0, 1]))
    return float(np.mean(vals)) if vals else float("nan")


def pcc_spot(truth: pd.DataFrame, pred: pd.DataFrame) -> float:
    pred = _align(truth, pred).reindex(columns=truth.columns)
    vals = []
    t = truth.to_numpy(dtype=float)
    p = pred.to_numpy(dtype=float)
    for i in range(t.shape[0]):
        if np.std(t[i]) == 0 or np.std(p[i]) == 0:
            continue
        vals.append(float(np.corrcoef(t[i], p[i])[0, 1]))
    return float(np.mean(vals)) if vals else float("nan")
