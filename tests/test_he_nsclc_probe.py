from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def _load_probe():
    spec = importlib.util.spec_from_file_location(
        "probe_he_nsclc", ROOT / "scripts/20_probe_he_nsclc_keep.py"
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_probe_pools_tumor_against_fibroblast():
    probe = _load_probe()
    types = ["tumor", "tumor 12", "fibroblast", "macrophage", "epithelial"]
    coarse = sorted({probe._coarse_label(t) for t in types})
    assert "tumor" in coarse
    assert "tumor 12" not in coarse
    mal, nbr = probe._pick_pair(coarse)
    assert mal == "tumor"
    assert nbr == "fibroblast"


def test_probe_refuses_second_tumor_as_neighbor():
    probe = _load_probe()
    types = ["tumor", "tumor 5", "prolif invasive"]
    ranked = probe._ranked_neighbors(["tumor", "tumor 5"])
    assert ranked == []
    src = (ROOT / "scripts/20_probe_he_nsclc_keep.py").read_text()
    assert "qc/counts.mtx" in src
    assert "mtx+labels" in src


def test_probe_keep_when_tumor_separable():
    probe = _load_probe()
    types = ["endothelial", "fibroblast", "tumor"]
    rng = np.random.default_rng(0)
    P = np.zeros((12, 3))
    P[:, 0] = rng.random(12)
    P[:, 1] = rng.random(12)
    P[:, 2] = np.arange(12, dtype=float) + 3.0
    P = P / P.sum(0, keepdims=True)
    decision, mal, nbr, cos, scans = probe._decide(types, P)
    assert mal == "tumor"
    assert nbr == "fibroblast"
    assert decision == "KEEP"
    assert cos < probe.C_STAR
    assert scans[0]["neighbor"] == "fibroblast"
