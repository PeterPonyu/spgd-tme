#!/usr/bin/env python
"""Cosine probe for GEO GSE277782 CosMx PDAC (3 patients, ~13 MB tables)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import importlib.util

spec = importlib.util.spec_from_file_location("probe_he", ROOT / "scripts/20_probe_he_nsclc_keep.py")
he = importlib.util.module_from_spec(spec)
spec.loader.exec_module(he)

INV = ROOT / "data" / "external" / "gse277782"
SCT = INV / "GSE277782_CosMx_SCT_data.csv.gz"
META = INV / "GSE277782_Meta.data_CoxMx.csv.gz"
OUT = ROOT / "data" / "plotdata" / "F12_pdac_cosine_probe.json"
C_STAR = 0.80
MAX_BYTES = 40_000_000
FTP_SCT = "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE277nnn/GSE277782/suppl/GSE277782_CosMx_SCT_data.csv.gz"
FTP_META = "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE277nnn/GSE277782/suppl/GSE277782_Meta.data_CoxMx.csv.gz"


def _fetch(url: str, dest: Path) -> None:
    INV.mkdir(parents=True, exist_ok=True)
    if dest.is_file() and dest.stat().st_size > 1000:
        return
    import urllib.request

    print(f"downloading {url}", flush=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=120) as resp, tmp.open("wb") as fh:
        n = 0
        while True:
            chunk = resp.read(1024 * 1024)
            if not chunk:
                break
            n += len(chunk)
            if n > MAX_BYTES:
                tmp.unlink(missing_ok=True)
                raise SystemExit(f"PROBE_ABORT download exceeded {MAX_BYTES}")
            fh.write(chunk)
    tmp.replace(dest)


def main() -> None:
    _fetch(FTP_SCT, SCT)
    _fetch(FTP_META, META)
    sct = pd.read_csv(SCT, index_col=0)
    meta = pd.read_csv(META, index_col=0)
    shared = sct.index.intersection(meta.index)
    if len(shared) == 0:
        raise SystemExit("PROBE_ABORT SCT/meta index mismatch")
    sct = sct.loc[shared]
    meta = meta.loc[shared]
    anno = meta["Annotation_main"].astype(str).to_numpy()
    X = np.asarray(sct.to_numpy(), dtype=float)
    types, P = he._type_means(X, anno)
    decision, malignant, neighbor, cos, scans = he._decide(types, P)
    rec = {
        "source": "GSE277782_CosMx_PDAC",
        "n_cells": int(X.shape[0]),
        "n_genes": int(X.shape[1]),
        "n_types": len(types),
        "types": types,
        "malignant": malignant,
        "neighbor": neighbor,
        "cosine": round(float(cos), 6),
        "c_star": C_STAR,
        "decision": decision,
        "n_patients": int(meta["Pt"].nunique()),
        "patients": sorted(meta["Pt"].astype(str).unique().tolist()),
        "n_samples": int(meta["Sample_name"].nunique()),
        "neighbor_scan": scans,
        "sct_bytes": int(SCT.stat().st_size),
        "meta_bytes": int(META.stat().st_size),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rec, indent=2) + "\n")
    print(json.dumps({k: rec[k] for k in rec if k != "neighbor_scan"}, indent=2))
    if decision != "KEEP":
        sys.exit(2)


if __name__ == "__main__":
    main()
