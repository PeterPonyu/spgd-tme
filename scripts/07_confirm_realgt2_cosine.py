#!/usr/bin/env python
"""P4a: realgt2 FLEX-reference cosine only. No build_v4. Does not rewrite type_pairs."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import anndata as ad
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.paths import BENCH, LOCKS, PLOTDATA
from src.refuse import should_abstain

OUT = PLOTDATA / "F2_realgt2_cosine.csv"


def _anno_col(ref) -> str:
    for cand in ("annotation", "cell_type", "celltype", "obs_annotation"):
        if cand in ref.obs.columns:
            return cand
    raise KeyError(f"no annotation column: {list(ref.obs.columns)}")


def _type_mean(ref, types_wanted: list[str]) -> dict[str, np.ndarray]:
    X = ref.layers["raw"] if "raw" in ref.layers else ref.X
    anno = ref.obs[_anno_col(ref)].astype(str).to_numpy()
    out = {}
    for ty in types_wanted:
        sel = anno == ty
        if not sel.any():
            raise SystemExit(f"type {ty} missing in realgt2 reference")
        block = X[sel]
        if hasattr(block, "mean"):
            m = np.asarray(block.mean(axis=0)).ravel()
        else:
            m = np.asarray(block).mean(0)
        n = float(np.linalg.norm(m))
        out[ty] = m / n if n else m
    return out


def main() -> None:
    if OUT.exists() and OUT.stat().st_size > 0:
        raise SystemExit(f"REFUSING overwrite: {OUT}")
    pairs = json.loads((LOCKS / "type_pairs.json").read_text())
    c_star = float(json.loads((LOCKS / "c_star.json").read_text())["value"])
    mal = pairs["realgt"]["malignant"]
    neigh = pairs["realgt"]["neighbor"]
    bench = BENCH["realgt2"]
    types = list(pd.read_csv(bench / "truth_proportions.csv", index_col=0, nrows=0).columns)
    if mal not in types or neigh not in types:
        raise SystemExit(f"locked pair {mal}/{neigh} missing from realgt2 types")
    ref = ad.read_h5ad(bench / "reference_subset.h5ad")
    vecs = _type_mean(ref, [mal, neigh])
    cos = float(np.clip(np.dot(vecs[mal], vecs[neigh]), -1.0, 1.0))
    xenium_cos = float(pairs["realgt"]["cosine"])
    row = {
        "substrate": "realgt2",
        "reference": "FLEX_orthogonal",
        "malignant": mal,
        "neighbor": neigh,
        "cosine": round(cos, 6),
        "xenium_ref_cosine": xenium_cos,
        "c_star": c_star,
        "decision": "ABSTAIN" if should_abstain(cos, c_star) else "KEEP",
        "n_spots": 2864,
        "source": "confirm_cosine_only",
    }
    PLOTDATA.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([row]).to_csv(OUT, index=False)
    print("[write]", OUT, "cosine=", row["cosine"], "decision=", row["decision"])


if __name__ == "__main__":
    main()
