"""He 2022 CosMx NSCLC unique pair builder. Does not touch Yerly donor_pairs."""
from __future__ import annotations

import collections
import io
import json
import zipfile
from pathlib import Path

import anndata as ad
import numpy as np
import pandas as pd
import scipy.sparse as sp
from scipy.io import mmread

from src.donor_builder import MIN_CELLS_PER_SPOT, MIN_SHARED_TYPES, MIN_TYPE_CELLS, is_ctrl
from src.donor_split import assert_disjoint_patient_ids, forbid_slide_key_as_donor

ZIP_PATH = Path(__file__).resolve().parents[1] / "data" / "external" / "he_nsclc" / "cosmx_lung.zip"
OUT_ROOT = Path(__file__).resolve().parents[1] / "data" / "external" / "he_nsclc" / "run"
DONOR_KEY = "Patient_ID"


def coarse_cell_type(name: str) -> str:
    n = str(name).lower().strip()
    if n.startswith("tumor") or n.startswith("cancer") or "malignant" in n:
        return "tumor"
    return str(name)


def load_sample(zf: zipfile.ZipFile, prefix: str) -> dict:
    X = mmread(io.BytesIO(zf.read(f"{prefix}/qc/counts.mtx"))).tocsr()
    obs = pd.read_csv(zf.open(f"{prefix}/qc/observations.tsv"), sep="\t", index_col=0)
    lab = pd.read_csv(zf.open(f"{prefix}/labels.tsv"), sep="\t", index_col=0)
    feat = pd.read_csv(zf.open(f"{prefix}/qc/features.tsv"), sep="\t")
    xy = pd.read_csv(zf.open(f"{prefix}/qc/coordinates.tsv"), sep="\t", index_col=0)
    if X.shape[0] != len(obs):
        raise ValueError(f"{prefix}: mtx rows {X.shape[0]} != obs {len(obs)}")
    lab = lab.reindex(obs.index)
    xy = xy.reindex(obs.index)
    mask = lab["cell_type"].notna() & xy["x"].notna() & xy["y"].notna()
    genes = np.array([str(g) for g in feat.iloc[:, 0].tolist()])
    return {
        "prefix": prefix,
        "X": X[mask.to_numpy()],
        "genes": genes,
        "cell_id": obs.index[mask].astype(str).to_numpy(),
        "cell_type": np.array([coarse_cell_type(v) for v in lab.loc[mask, "cell_type"]]),
        "xy": xy.loc[mask, ["x", "y"]].to_numpy(dtype=float),
    }


def patient_map(zf: zipfile.ZipFile) -> dict[str, int]:
    samples = pd.read_csv(zf.open("samples.tsv"), sep="\t")
    return {str(r["directory"]): int(r["patient"]) for _, r in samples.iterrows()}


def _bin_spots(xy: np.ndarray, X, labels: np.ndarray, kept: list[str], genes: np.ndarray):
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
        return None
    _, bin_edge, med, _nsp = best
    ij = np.floor((xy - xy.min(0)) / bin_edge).astype(np.int64)
    bin_id = ij[:, 0] * (ij[:, 1].max() + 1) + ij[:, 1]
    rows, truth_rows, coords, ncells, names = [], [], [], [], []
    for b in np.unique(bin_id):
        sel = np.flatnonzero(bin_id == b)
        if len(sel) < MIN_CELLS_PER_SPOT:
            continue
        rows.append(sp.csr_matrix(X[sel].sum(axis=0)))
        prop = pd.Series(labels[sel]).value_counts().reindex(kept).fillna(0.0).to_numpy()
        truth_rows.append(prop / prop.sum())
        coords.append(xy[sel].mean(axis=0))
        ncells.append(len(sel))
        names.append(f"cosmx_nsclc_xdonor_spot_{int(b):010d}")
    if len(rows) < 100:
        return None
    spots = ad.AnnData(
        X=sp.vstack(rows, format="csr").astype(np.float32),
        obs=pd.DataFrame({"n_cells_pooled": ncells}, index=pd.Index(names)),
        var=pd.DataFrame(index=pd.Index(genes)),
    )
    spots.obsm["spatial"] = np.asarray(coords, float)
    truth = pd.DataFrame(np.asarray(truth_rows), index=pd.Index(names), columns=kept)
    return spots, truth, float(bin_edge), float(np.median(ncells))


def build_pair(spot_prefix: str, ref_prefix: str, out_dir: Path) -> dict:
    forbid_slide_key_as_donor(DONOR_KEY)
    if out_dir.exists() and any(out_dir.iterdir()):
        raise FileExistsError(f"refusing to overwrite nonempty {out_dir}")
    yerly = Path(__file__).resolve().parents[1] / "data" / "donor_pairs"
    if out_dir.resolve() == yerly.resolve() or yerly.resolve() in out_dir.resolve().parents:
        raise ValueError("NSCLC runner must not write Yerly donor_pairs")
    with zipfile.ZipFile(ZIP_PATH) as zf:
        patients = patient_map(zf)
        spot = load_sample(zf, spot_prefix)
        ref = load_sample(zf, ref_prefix)
    spot_pid = np.array([patients[spot_prefix]] * len(spot["cell_id"]))
    ref_pid = np.array([patients[ref_prefix]] * len(ref["cell_id"]))
    assert_disjoint_patient_ids(
        np.concatenate([spot_pid, ref_pid]),
        np.array([True] * len(spot_pid) + [False] * len(ref_pid)),
        np.array([False] * len(spot_pid) + [True] * len(ref_pid)),
    )
    genes, si, ri = np.intersect1d(spot["genes"], ref["genes"], return_indices=True)
    ctrl = np.array([is_ctrl(g) for g in genes])
    gene_idx = np.flatnonzero(~ctrl)
    genes = genes[gene_idx]
    Xs = spot["X"][:, si[gene_idx]]
    Xr = ref["X"][:, ri[gene_idx]]
    cs = pd.Series(spot["cell_type"]).value_counts()
    cr = pd.Series(ref["cell_type"]).value_counts()
    kept = sorted(
        t
        for t in set(cs.index) & set(cr.index)
        if cs.get(t, 0) >= MIN_TYPE_CELLS and cr.get(t, 0) >= MIN_TYPE_CELLS
    )
    status = {
        "spot_prefix": spot_prefix,
        "ref_prefix": ref_prefix,
        "spot_patient": int(patients[spot_prefix]),
        "ref_patient": int(patients[ref_prefix]),
        "n_shared_types": len(kept),
        "kept": kept,
        "spot_n": int(len(spot["cell_id"])),
        "ref_n": int(len(ref["cell_id"])),
    }
    if "tumor" not in kept:
        status["blocked"] = "pooled tumor missing after type floor"
        return status
    if len(kept) < MIN_SHARED_TYPES:
        status["blocked"] = f"shared types {len(kept)} < {MIN_SHARED_TYPES}"
        return status
    spot_keep = np.isin(spot["cell_type"], kept)
    ref_keep = np.isin(ref["cell_type"], kept)
    packed = _bin_spots(
        spot["xy"][spot_keep],
        Xs[spot_keep],
        spot["cell_type"][spot_keep],
        kept,
        genes,
    )
    if packed is None:
        status["blocked"] = "bin auto-tune failed"
        return status
    spots, truth, bin_edge, med = packed
    ref_ad = ad.AnnData(
        X=Xr[ref_keep].astype(np.float32),
        obs=pd.DataFrame(
            {"cell_type": pd.Categorical(ref["cell_type"][ref_keep])},
            index=pd.Index(ref["cell_id"][ref_keep]),
        ),
        var=pd.DataFrame(index=pd.Index(genes)),
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    spots.write_h5ad(out_dir / "benchmark_spots.h5ad")
    spots.write_h5ad(out_dir / "benchmark_spots_counts.h5ad")
    ref_ad.write_h5ad(out_dir / "reference_subset.h5ad")
    truth.to_csv(out_dir / "truth_proportions.csv")
    manifest = {
        "spot_donor": f"Patient{status['spot_patient']}",
        "ref_donor": f"Patient{status['ref_patient']}",
        "donor_key_in_source": DONOR_KEY,
        "spot_prefix": spot_prefix,
        "ref_prefix": ref_prefix,
        "n_types": len(kept),
        "cell_type": kept,
        "n_spots": int(spots.n_obs),
        "ref_cells": int(ref_ad.n_obs),
        "bin_edge_native_units": float(bin_edge),
        "median_cells_per_spot": float(med),
        "ref_per_type": dict(collections.Counter(ref["cell_type"][ref_keep].tolist())),
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    status.update({"n_spots": int(spots.n_obs), "out_dir": str(out_dir)})
    return status
