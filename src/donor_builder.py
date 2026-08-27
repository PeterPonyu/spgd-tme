"""Parameterize the CosMx BCC cross-donor builder. Does not write realgt4."""
from __future__ import annotations

import collections
import json
from pathlib import Path

import anndata as ad
import numpy as np
import pandas as pd
import scipy.io
import scipy.sparse as sp

from src.donor_split import assert_disjoint_patient_ids, forbid_slide_key_as_donor
from src.paths import BCC_EXPORT, DONOR_PAIRS

DONOR_KEY = "Patient_ID"
SLIDE_KEY = "Run_Tissue_name"
CT_KEY = "celltype"
DROP_TYPES = {"Low.quality", "Unknown", "", "nan"}
MIN_CELLS_PER_SPOT = 5
MIN_TYPE_CELLS = 50
MAX_GENES = 4096
COSMX_UM_PER_PX = 0.12028
MIN_SHARED_TYPES = 8


def is_ctrl(g: str) -> bool:
    gl = str(g).lower()
    return (
        gl.startswith("negprb")
        or gl.startswith("neg_")
        or gl.startswith("negative")
        or gl.startswith("blank")
        or gl.startswith("systemcontrol")
        or gl.startswith("falsecode")
        or "negprobe" in gl
        or gl.startswith("control")
    )


def _short(name: str) -> str:
    return name.replace("Patient", "")


def pair_dirname(spot_donor: str, ref_donor: str) -> str:
    return f"{_short(spot_donor)}_from_{_short(ref_donor)}"


def load_bcc_export():
    feats = np.array([l.strip() for l in (BCC_EXPORT / "features.txt").read_text().splitlines()])
    cells = np.array([l.strip() for l in (BCC_EXPORT / "cells.txt").read_text().splitlines()])
    meta = pd.read_csv(BCC_EXPORT / "metadata.csv")
    if list(meta["cell_id"].astype(str)) != list(cells):
        raise AssertionError("metadata/cells order mismatch")
    mtx = BCC_EXPORT / "counts_genes_x_cells.mtx"
    if not mtx.exists():
        mtx = BCC_EXPORT / "counts_genes_x_cells.mtx.gz"
    M = scipy.io.mmread(str(mtx)).tocsr()
    X = M.T.tocsr()
    del M
    return feats, cells, meta, X


def build_pair(
    spot_donor: str,
    ref_donor: str,
    out_dir: Path,
    *,
    feats,
    cells,
    meta: pd.DataFrame,
    X_cells_genes,
) -> dict:
    forbid_slide_key_as_donor(DONOR_KEY)
    if out_dir.exists() and any(out_dir.iterdir()):
        raise FileExistsError(f"refusing to overwrite nonempty {out_dir}")
    donor = meta[DONOR_KEY].astype(str).to_numpy()
    slide = meta[SLIDE_KEY].astype(str).to_numpy()
    ct = meta[CT_KEY].astype(str).to_numpy()
    good_ct = ~np.isin(ct, list(DROP_TYPES))
    spot_mask = (donor == spot_donor) & good_ct
    ref_mask = (donor == ref_donor) & good_ct
    assert_disjoint_patient_ids(donor, donor == spot_donor, donor == ref_donor)
    spot_slides = set(np.unique(slide[donor == spot_donor]).tolist())
    ref_slides = set(np.unique(slide[donor == ref_donor]).tolist())
    if not spot_slides.isdisjoint(ref_slides):
        raise AssertionError(f"slides overlap {spot_slides} vs {ref_slides}")

    cs = pd.Series(ct[spot_mask]).value_counts()
    cr = pd.Series(ct[ref_mask]).value_counts()
    kept = sorted(
        t
        for t in set(cs.index) & set(cr.index)
        if cs.get(t, 0) >= MIN_TYPE_CELLS and cr.get(t, 0) >= MIN_TYPE_CELLS
    )
    status = {
        "spot_donor": spot_donor,
        "ref_donor": ref_donor,
        "n_shared_types": len(kept),
        "kept": kept,
        "spot_n": int(spot_mask.sum()),
        "ref_n": int(ref_mask.sum()),
    }
    if len(kept) < MIN_SHARED_TYPES:
        status["blocked"] = f"shared types {len(kept)} < {MIN_SHARED_TYPES}"
        return status

    ctrl = np.array([is_ctrl(g) for g in feats])
    ref_idx_all = np.flatnonzero(ref_mask & np.isin(ct, kept))
    ref_means = np.asarray(X_cells_genes[ref_idx_all].mean(axis=0)).ravel()
    cand = np.flatnonzero(~ctrl)
    order = cand[np.argsort(ref_means[cand])[::-1]]
    gene_idx = np.sort(order[:MAX_GENES])
    genes = feats[gene_idx]

    spot_idx = np.flatnonzero(spot_mask & np.isin(ct, kept))
    xy = meta.loc[spot_idx, ["x", "y"]].to_numpy(dtype=float)
    span = xy.max(0) - xy.min(0)
    lo, hi = span.min() / 4000.0, span.min() / 4.0
    best = None
    for be in np.geomspace(lo, hi, 50):
        ij = np.floor((xy - xy.min(0)) / be).astype(np.int64)
        bid = ij[:, 0] * (ij[:, 1].max() + 1) + ij[:, 1]
        vc = pd.Series(bid).value_counts()
        vc = vc[vc >= MIN_CELLS_PER_SPOT]
        if len(vc) < 200:
            continue
        med = float(vc.median())
        score = abs(med - 19.0)
        if best is None or score < best[0]:
            best = (score, be, med, len(vc))
    if best is None:
        status["blocked"] = "bin auto-tune failed"
        return status
    _, bin_edge, med, nsp = best
    ij = np.floor((xy - xy.min(0)) / bin_edge).astype(np.int64)
    bin_id = ij[:, 0] * (ij[:, 1].max() + 1) + ij[:, 1]
    Xspot = X_cells_genes[spot_idx][:, gene_idx].tocsr()
    labels = ct[spot_idx]
    rows, truth_rows, coords, ncells, names = [], [], [], [], []
    for b in np.unique(bin_id):
        sel = np.flatnonzero(bin_id == b)
        if len(sel) < MIN_CELLS_PER_SPOT:
            continue
        rows.append(sp.csr_matrix(Xspot[sel].sum(axis=0)))
        prop = pd.Series(labels[sel]).value_counts().reindex(kept).fillna(0.0).to_numpy()
        truth_rows.append(prop / prop.sum())
        coords.append(xy[sel].mean(axis=0))
        ncells.append(len(sel))
        names.append(f"cosmx_bcc_xdonor_spot_{int(b):010d}")
    if len(rows) < 100:
        status["blocked"] = f"only {len(rows)} spots"
        return status

    Xs = sp.vstack(rows, format="csr").astype(np.float32)
    obs = pd.DataFrame(index=pd.Index(names))
    obs["n_cells_pooled"] = ncells
    var = pd.DataFrame(index=pd.Index(genes))
    spots = ad.AnnData(X=Xs, obs=obs, var=var.copy())
    spots.obsm["spatial"] = np.asarray(coords, float)
    truth = pd.DataFrame(np.asarray(truth_rows), index=pd.Index(names), columns=kept)
    ref_idx = np.flatnonzero(ref_mask & np.isin(ct, kept))
    ref = ad.AnnData(
        X=X_cells_genes[ref_idx][:, gene_idx].astype(np.float32),
        obs=pd.DataFrame(
            {"cell_type": pd.Categorical(ct[ref_idx])},
            index=pd.Index(cells[ref_idx]),
        ),
        var=var.copy(),
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    spots.write_h5ad(out_dir / "benchmark_spots.h5ad")
    spots.write_h5ad(out_dir / "benchmark_spots_counts.h5ad")
    ref.write_h5ad(out_dir / "reference_subset.h5ad")
    truth.to_csv(out_dir / "truth_proportions.csv")
    nc = np.asarray(ncells)
    manifest = {
        "spot_donor": spot_donor,
        "ref_donor": ref_donor,
        "donor_key_in_source": DONOR_KEY,
        "n_types": len(kept),
        "cell_type": kept,
        "n_spots": int(spots.n_obs),
        "ref_cells": int(ref.n_obs),
        "bin_edge_native_units": float(bin_edge),
        "median_cells_per_spot": float(np.median(nc)),
        "approx_spot_um_if_cosmx_px": float(bin_edge * COSMX_UM_PER_PX),
        "ref_per_type": dict(collections.Counter(ct[ref_idx].tolist())),
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    status["out_dir"] = str(out_dir)
    status["n_spots"] = int(spots.n_obs)
    return status
