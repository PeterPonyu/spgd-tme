#!/usr/bin/env python
"""Cosine probe for Nanostring CosMx liver (SACCELERATOR zip, two patients)."""
from __future__ import annotations

import io
import json
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
spec_path = ROOT / "scripts/20_probe_he_nsclc_keep.py"
import importlib.util

spec = importlib.util.spec_from_file_location("probe_he", spec_path)
he = importlib.util.module_from_spec(spec)
spec.loader.exec_module(he)

INV = ROOT / "data" / "external" / "he_liver"
ZIP_PATH = INV / "cosmx_liver.zip"
OUT = ROOT / "data" / "plotdata" / "F12_he_liver_cosine_probe.json"
C_STAR = 0.80
MAX_BYTES = 560_000_000
ZENODO_URL = "https://zenodo.org/api/records/15487520/files/cosmx_liver.zip/content"


def _download() -> None:
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


def _pick_cancer_sample(zf: zipfile.ZipFile) -> tuple[str, dict]:
    samples = pd.read_csv(zf.open("samples.tsv"), sep="\t")
    print(samples.to_string(), flush=True)
    names = zf.namelist()
    prefixes = sorted({n.split("/")[0] for n in names if n.endswith("/qc/counts.mtx")})
    chosen = prefixes[0]
    for prefix in prefixes:
        lab = pd.read_csv(zf.open(f"{prefix}/labels.tsv"), sep="\t")
        col = "cell_type" if "cell_type" in lab.columns else lab.columns[-1]
        types = lab[col].astype(str).str.lower()
        if types.str.contains(r"tumor|cancer|malignant|\bhcc\b|hepatocellular").any():
            chosen = prefix
            break
    pid_col = next((c for c in samples.columns if c.lower() in {"patient", "patient_id", "pid"}), None)
    meta = {
        "n_patients": int(samples[pid_col].nunique()) if pid_col else None,
        "patient_column": pid_col,
        "samples": samples.to_dict(orient="records"),
        "prefixes": prefixes,
        "chosen": chosen,
    }
    return chosen, meta


def main() -> None:
    _download()
    size = ZIP_PATH.stat().st_size
    if size > MAX_BYTES:
        raise SystemExit(f"PROBE_ABORT zip too large {size}")
    from scipy.io import mmread

    with zipfile.ZipFile(ZIP_PATH) as zf:
        prefix, meta = _pick_cancer_sample(zf)
        print("reading", prefix, flush=True)
        X = mmread(io.BytesIO(zf.read(f"{prefix}/qc/counts.mtx"))).tocsr()
        obs = pd.read_csv(zf.open(f"{prefix}/qc/observations.tsv"), sep="\t", index_col=0)
        lab = pd.read_csv(zf.open(f"{prefix}/labels.tsv"), sep="\t", index_col=0)
        feat = pd.read_csv(zf.open(f"{prefix}/qc/features.tsv"), sep="\t")
    lab = lab.reindex(obs.index)
    type_col = "cellType" if "cellType" in lab.columns else "cell_type"
    mask = lab[type_col].notna().to_numpy()
    X = X[mask]
    anno = lab.loc[mask, type_col].astype(str).to_numpy()
    genes = [str(g) for g in feat.iloc[:, 0].tolist()]
    orig_is_tumor = he._is_tumor_name

    def _liver_tumor(name: str) -> bool:
        n = str(name).lower().strip()
        if orig_is_tumor(n):
            return True
        return "hepatocellular" in n or n == "hcc" or "cholangiocarcinoma" in n

    he._is_tumor_name = _liver_tumor
    # Hepatic stellate cells are the CAF analogue; do not take the first
    # immune KEEP if macrophage/endothelium already sit at or above c*.
    he.NEIGHBOR_PREF = (
        "fibroblast",
        "caf",
        "stellate",
    ) + tuple(k for k in he.NEIGHBOR_PREF if k not in {"fibroblast", "caf", "stellate"})
    types, P = he._type_means(X, anno)
    decision, malignant, neighbor, cos, scans = he._decide(types, P)
    rec = {
        "source": "CosMx_liver_zenodo15487520",
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
        "patient_column": meta.get("patient_column"),
        "tumor_on_normal": False,
        "donor_tumor_column": False,
        "sample": prefix,
        "prefixes": meta.get("prefixes"),
        "neighbor_scan": scans,
        "zip_bytes": size,
        "gene_head": genes[:8],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rec, indent=2) + "\n")
    print(json.dumps({k: rec[k] for k in rec if k != "neighbor_scan"}, indent=2))
    if decision != "KEEP":
        sys.exit(2)


if __name__ == "__main__":
    main()
