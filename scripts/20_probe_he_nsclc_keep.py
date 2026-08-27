#!/usr/bin/env python
"""Cosine probe for He 2022 CosMx NSCLC as a second KEEP-cancer candidate.

Fail-closed: download at most the processed lung zip (~285 MB). Pool tumor
clusters against a stromal/immune neighbor. Do not sit, do not rebuild Yerly
donors, and do not write reader-PDF numbers unless KEEP.
"""
from __future__ import annotations

import io
import json
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
INV = ROOT / "data" / "external" / "he_nsclc"
ZIP_PATH = INV / "cosmx_lung.zip"
OUT = ROOT / "data" / "plotdata" / "F12_he_nsclc_cosine_probe.json"
C_STAR = 0.80
MAX_BYTES = 400_000_000
ZENODO_URL = "https://zenodo.org/api/records/15487520/files/cosmx_lung.zip/content"
PREFERRED_SAMPLE = "Lung5_Rep2"

NEIGHBOR_PREF = (
    "fibroblast",
    "caf",
    "macrophage",
    "endothelial",
    "neutrophil",
    "t cd4",
    "b-cell",
    "nk",
    "monocyte",
    "mast",
)


def _is_tumor_name(name: str) -> bool:
    n = str(name).lower().strip()
    return n.startswith("tumor") or n.startswith("cancer") or "malignant" in n


def _coarse_label(name: str) -> str:
    return "tumor" if _is_tumor_name(name) else str(name)


def _is_forbidden_neighbor(name: str) -> bool:
    n = str(name).lower()
    return _is_tumor_name(n) or "prolif" in n


def _ranked_neighbors(types: list[str]) -> list[str]:
    rest = [t for t in types if t != "tumor" and not _is_forbidden_neighbor(t)]
    ranked = []
    for t in rest:
        tl = t.lower()
        score = next((i for i, k in enumerate(NEIGHBOR_PREF) if k in tl), 99)
        ranked.append((score, t))
    ranked.sort()
    return [t for _, t in ranked]


def _pick_pair(types: list[str]) -> tuple[str, str]:
    if "tumor" not in types:
        raise SystemExit(f"PROBE_ABORT no pooled tumor column in {types[:30]}")
    neighbors = _ranked_neighbors(types)
    if not neighbors:
        raise SystemExit(f"PROBE_ABORT no stromal/immune neighbor in {types[:30]}")
    return "tumor", neighbors[0]


def _column_cosine(a: np.ndarray, b: np.ndarray) -> float:
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def _decide(types: list[str], P: np.ndarray) -> tuple[str, str, str, float, list[dict]]:
    malignant, _preferred = _pick_pair(types)
    i = types.index(malignant)
    scans = []
    keep = None
    for neighbor in _ranked_neighbors(types):
        j = types.index(neighbor)
        cos = _column_cosine(P[:, i], P[:, j])
        decision = "ABSTAIN" if cos >= C_STAR else "KEEP"
        rec = {"neighbor": neighbor, "cosine": round(float(cos), 6), "decision": decision}
        scans.append(rec)
        if keep is None and decision == "KEEP":
            keep = rec
    chosen = keep if keep is not None else scans[0]
    return chosen["decision"], malignant, chosen["neighbor"], float(chosen["cosine"]), scans


def _download_zip() -> None:
    INV.mkdir(parents=True, exist_ok=True)
    if ZIP_PATH.is_file() and ZIP_PATH.stat().st_size > 10_000_000:
        return
    import urllib.request

    print(f"downloading {ZENODO_URL}", flush=True)
    tmp = ZIP_PATH.with_suffix(".part")
    with urllib.request.urlopen(ZENODO_URL, timeout=120) as resp, tmp.open("wb") as fh:
        n = 0
        while True:
            chunk = resp.read(1024 * 1024)
            if not chunk:
                break
            n += len(chunk)
            if n > MAX_BYTES:
                tmp.unlink(missing_ok=True)
                raise SystemExit(f"PROBE_ABORT download exceeded {MAX_BYTES} bytes")
            fh.write(chunk)
            if n % (20 * 1024 * 1024) < 1024 * 1024:
                print(f"  {n / 1e6:.0f} MB", flush=True)
    tmp.replace(ZIP_PATH)
    print(f"wrote {ZIP_PATH} ({ZIP_PATH.stat().st_size} bytes)", flush=True)


def _sample_prefix(names: list[str]) -> str:
    if any(n.startswith(PREFERRED_SAMPLE + "/") for n in names):
        return PREFERRED_SAMPLE
    for n in names:
        if n.endswith("/qc/counts.mtx"):
            return n.split("/")[0]
    raise SystemExit("PROBE_ABORT no qc/counts.mtx member")


def _load_from_zip() -> tuple[np.ndarray, np.ndarray, list[str], dict]:
    with zipfile.ZipFile(ZIP_PATH) as zf:
        names = zf.namelist()
        print("zip members", len(names), names[:8], flush=True)
        h5ads = [n for n in names if n.endswith(".h5ad")]
        if h5ads:
            import anndata as ad
            import tempfile

            member = h5ads[0]
            with tempfile.TemporaryDirectory() as td:
                zf.extract(member, td)
                adata = ad.read_h5ad(Path(td) / member)
            X = adata.X
            X = np.asarray(X.todense()) if hasattr(X, "todense") else np.asarray(X)
            anno = None
            for cand in ("cell_type", "celltype", "annotation", "cluster", "label"):
                if cand in adata.obs.columns:
                    anno = adata.obs[cand].astype(str).to_numpy()
                    break
            if anno is None:
                raise SystemExit(f"PROBE_ABORT no type column in {list(adata.obs.columns)}")
            meta = {"layout": "h5ad", "member": member, "n_patients": None}
            return X, anno, list(map(str, adata.var_names)), meta

        prefix = _sample_prefix(names)
        mtx_name = f"{prefix}/qc/counts.mtx"
        obs_name = f"{prefix}/qc/observations.tsv"
        feat_name = f"{prefix}/qc/features.tsv"
        lab_name = f"{prefix}/labels.tsv"
        for member in (mtx_name, obs_name, feat_name, lab_name):
            if member not in names:
                raise SystemExit(f"PROBE_ABORT missing {member}")
        print(f"reading {mtx_name}", flush=True)
        from scipy.io import mmread

        X = mmread(io.BytesIO(zf.read(mtx_name))).tocsr()
        obs = pd.read_csv(zf.open(obs_name), sep="\t", index_col=0)
        lab = pd.read_csv(zf.open(lab_name), sep="\t", index_col=0)
        feat = pd.read_csv(zf.open(feat_name), sep="\t")
        if X.shape[0] != len(obs):
            raise SystemExit(f"PROBE_ABORT mtx rows {X.shape[0]} != obs {len(obs)}")
        lab_aligned = lab.reindex(obs.index)
        mask = lab_aligned["cell_type"].notna().to_numpy()
        X = X[mask]
        anno = lab_aligned.loc[mask, "cell_type"].astype(str).to_numpy()
        genes = [str(g) for g in feat.iloc[:, 0].tolist()]
        n_patients = None
        if "samples.tsv" in names:
            samples = pd.read_csv(zf.open("samples.tsv"), sep="\t")
            if "patient" in samples.columns:
                n_patients = int(samples["patient"].nunique())
        meta = {
            "layout": "mtx+labels",
            "sample": prefix,
            "n_patients": n_patients,
        }
        return X, anno, genes, meta


def _type_means(X, anno: np.ndarray) -> tuple[list[str], np.ndarray]:
    if hasattr(X, "tocsr"):
        X = X.tocsr()
    coarse = np.array([_coarse_label(a) for a in anno], dtype=object)
    types = sorted(set(coarse.tolist()))
    libr = np.asarray(X.sum(axis=1)).reshape(-1)
    libr[libr == 0] = 1.0
    scale = float(np.median(libr))
    P = np.zeros((X.shape[1], len(types)), dtype=float)
    for k, ty in enumerate(types):
        sel = coarse == ty
        n = int(sel.sum())
        if n == 0:
            continue
        rows = X[sel]
        if hasattr(rows, "multiply"):
            weights = (scale / libr[sel]).reshape(-1, 1)
            scaled = rows.multiply(weights)
            P[:, k] = np.asarray(scaled.mean(axis=0)).ravel()
        else:
            P[:, k] = (np.asarray(rows) / libr[sel, None] * scale).mean(0)
    col = P.sum(0, keepdims=True)
    col[col == 0] = 1.0
    return types, P / col


def main() -> None:
    _download_zip()
    size = ZIP_PATH.stat().st_size
    if size > MAX_BYTES:
        raise SystemExit(f"PROBE_ABORT zip too large {size}")
    X, anno, genes, meta = _load_from_zip()
    print(f"loaded cells={X.shape[0]} genes={X.shape[1]} layout={meta.get('layout')}", flush=True)
    types, P = _type_means(X, anno)
    decision, malignant, neighbor, cos, scans = _decide(types, P)
    rec = {
        "source": "He2022_CosMx_NSCLC_zenodo15487520",
        "n_cells": int(X.shape[0]),
        "n_genes": int(X.shape[1]),
        "n_types": len(types),
        "types": types,
        "malignant": malignant,
        "neighbor": neighbor,
        "cosine": round(float(cos), 6),
        "c_star": C_STAR,
        "decision": decision,
        "n_patients": meta.get("n_patients"),
        "sample": meta.get("sample"),
        "layout": meta.get("layout"),
        "neighbor_scan": scans,
        "zip_bytes": size,
        "gene_head": genes[:8],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rec, indent=2) + "\n")
    print(json.dumps(rec, indent=2))
    if decision != "KEEP":
        print("PROBE_STOP ABSTAIN: do not pull full S3 tarballs or sit", flush=True)
        sys.exit(2)


if __name__ == "__main__":
    main()
