from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def test_f3_schema_when_present():
    p = ROOT / "data/plotdata/F3_collinearity_sweep.csv"
    if not p.exists():
        pytest.skip("F3 not emitted yet")
    df = pd.read_csv(p)
    assert len(df) == 33
    assert "survival" not in df.columns
    locks = json.loads((ROOT / "locks/type_pairs.json").read_text())
    for sub, g in df.groupby("substrate"):
        t0 = g.loc[g["t"] == 0.0].iloc[0]
        assert abs(float(t0["cosine"]) - float(locks[sub]["cosine"])) < 1e-3


def test_f4_na_when_refused():
    p = ROOT / "data/plotdata/F4_refusal.csv"
    if not p.exists():
        pytest.skip("F4 not emitted yet")
    df = pd.read_csv(p)
    hit = df[df["refused"] == True]  # noqa: E712
    if len(hit) == 0:
        return
    assert hit["rmse_gate_on"].isna().all() or (hit["rmse_gate_on"].astype(str) == "").all()


def test_f5_locked_cd_row():
    p = ROOT / "data/plotdata/F5_donor_transfer.csv"
    if not p.exists():
        pytest.skip("F5 not emitted yet")
    df = pd.read_csv(p)
    row = df.loc[df["pair"] == "C_from_D"].iloc[0]
    lock = json.loads((ROOT / "locks/cd_lock.json").read_text())
    assert row["source"] == "locked"
    assert abs(float(row["RMSE"]) - float(lock["RMSE"])) < 1e-9
    blob = p.read_text()
    assert "0.2034" not in blob
    assert "0.1126" not in blob
