#!/usr/bin/env python
"""Cosine probe for one CosMx CRC section (Zenodo 15574384, 232.h5ad ~227 MB).

Fail-closed: download at most this h5ad. Pool tumor against stroma/immune.
Do not sit Yerly and do not write reader-PDF numbers unless KEEP.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
INV = ROOT / "data" / "external" / "crc_cosmx"
H5AD = INV / "232.h5ad"
OUT = ROOT / "data" / "plotdata" / "F12_crc_cosine_probe.json"
C_STAR = 0.80
MAX_BYTES = 400_000_000
ZENODO_URL = "https://zenodo.org/api/records/15574384/files/232.h5ad/content"

# Reuse NSCLC pairing logic.
sys.path.insert(0, str(ROOT / "scripts"))
import importlib.util

_spec = importlib.util.spec_from_file_location("probe_he", ROOT / "scripts/20_probe_he_nsclc_keep.py")
_he = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_he)


def _download() -> None:
    INV.mkdir(parents=True, exist_ok=True)
    if H5AD.is_file() and H5AD.stat().st_size > 10_000_000:
        return
    import urllib.request

    print(f"downloading {ZENODO_URL}", flush=True)
    tmp = H5AD.with_suffix(".part")
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
    tmp.replace(H5AD)
    print(f"wrote {H5AD} ({H5AD.stat().st_size} bytes)", flush=True)


def main() -> None:
    _download()
    size = H5AD.stat().st_size
    if size > MAX_BYTES:
        raise SystemExit(f"PROBE_ABORT file too large {size}")
    import anndata as ad

    adata = ad.read_h5ad(H5AD)
    print("obs cols", list(adata.obs.columns)[:30], flush=True)
    anno = None
    col_used = None
    for cand in (
        "lv2",
        "cell_type",
        "celltype",
        "annotation",
        "cluster",
        "label",
        "cellType",
        "lv1",
        "typ",
        "Level1",
        "level1",
    ):
        if cand in adata.obs.columns:
            raw = adata.obs[cand].astype(str).to_numpy()
            col_used = cand
            print(f"using obs.{cand}", flush=True)
            break
    if col_used is None:
        raise SystemExit(f"PROBE_ABORT no type column in {list(adata.obs.columns)}")
    anno = []
    for v in raw:
        vs = str(v).lower()
        if vs.startswith("epi.") or vs == "epi" or "tumor" in vs or vs.startswith("cancer"):
            anno.append("tumor")
        elif vs.startswith("caf") or "fib" in vs:
            anno.append("fibroblast")
        else:
            anno.append(str(v))
    anno = np.array(anno, dtype=object)
    X = adata.X
    types, P = _he._type_means(X, anno)
    decision, malignant, neighbor, cos, scans = _he._decide(types, P)
    rec = {
        "source": "CosMx_CRC_zenodo15574384_232",
        "n_cells": int(adata.n_obs),
        "n_genes": int(adata.n_vars),
        "n_types": len(types),
        "types": types,
        "malignant": malignant,
        "neighbor": neighbor,
        "cosine": round(float(cos), 6),
        "c_star": C_STAR,
        "decision": decision,
        "obs_columns": list(map(str, adata.obs.columns)),
        "file_bytes": size,
        "neighbor_scan": scans[:8],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rec, indent=2) + "\n")
    print(json.dumps({k: rec[k] for k in rec if k != "neighbor_scan"}, indent=2))
    print("scan", json.dumps(scans[:6], indent=2))
    if decision != "KEEP":
        print("PROBE_STOP ABSTAIN: do not pull remaining CRC sections", flush=True)
        sys.exit(2)


if __name__ == "__main__":
    main()
