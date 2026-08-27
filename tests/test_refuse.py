from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.interpolate import blend_columns, column_cosine
from src.refuse import apply_abstain, refusal_mask, should_abstain


def test_blend_t1_makes_identical_columns():
    rng = np.random.default_rng(0)
    P = rng.random((8, 3))
    P = P / P.sum(0, keepdims=True)
    out = blend_columns(P, 0, 1, 1.0)
    assert column_cosine(out, 0, 1) == np.clip(column_cosine(out, 0, 1), 0, 1)
    assert abs(column_cosine(out, 0, 1) - 1.0) < 1e-9


def test_should_abstain_threshold():
    assert should_abstain(0.80, 0.80) is True
    assert should_abstain(0.79, 0.80) is False


def test_refusal_mask_alias_on_identical_columns():
    P = np.eye(3)
    P[:, 1] = P[:, 0]
    assert refusal_mask(P, 0, 1, 0.80) is True
    types = ["Tumor", "Tumor_Keratin_Pearl", "Stroma"]
    named = np.array([[1.0, 1.0, 0.0], [0.0, 0.0, 1.0]], dtype=float)
    named = named / named.sum(0, keepdims=True)
    assert refusal_mask(named, "Tumor", "Tumor_Keratin_Pearl", 0.80, types=types) is True


def test_apply_abstain_does_not_zero_refused_rmse_column():
    pi = pd.DataFrame({"Tumor": [0.4, 0.6], "Stroma": [0.6, 0.4]})
    out = apply_abstain(pi, ["Tumor"])
    assert out["Tumor"].isna().all()
    assert abs(out["Stroma"].sum() - 2.0) < 1e-9
