#!/usr/bin/env python
"""Unique He NSCLC t=0 donor edge. Does not sit Yerly and does not retune c*."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.he_nsclc_builder import OUT_ROOT, ZIP_PATH, build_pair
from src.interpolate import malignant_neighbor_cosine
from src.metrics_tme import pcc_spot, pcc_type, point_rmse, tumor_rmse
from src.refuse import should_abstain
from src.signature import extract_signature
from src.spgd_wrap import run_spgd

PROBE = ROOT / "data" / "plotdata" / "F12_he_nsclc_cosine_probe.json"
OUT_JSON = ROOT / "data" / "plotdata" / "F12_he_nsclc_t0_donor.json"
SPOT_PREFIX = "Lung6"
REF_PREFIX = "Lung5_Rep2"
C_STAR = 0.80


def require_nsclc(job: str) -> None:
    if os.environ.get("SPGD_TME_NSCLC") == "1":
        return
    print(
        f"REFUSING {job}: NSCLC unique runner is gated.\n"
        "Set SPGD_TME_NSCLC=1 after the cosine probe returns KEEP.",
        file=sys.stderr,
    )
    raise SystemExit(3)


def main() -> None:
    require_nsclc("21_he_nsclc_t0_donor")
    if not ZIP_PATH.is_file():
        raise SystemExit("PROBE_ABORT missing NSCLC zip")
    probe = json.loads(PROBE.read_text())
    if probe.get("decision") != "KEEP":
        raise SystemExit("PROBE_STOP ABSTAIN: do not build NSCLC donor or sit")
    if should_abstain(float(probe["cosine"]), C_STAR):
        raise SystemExit("PROBE_STOP cosine does not keep")
    pair_dir = OUT_ROOT / f"{SPOT_PREFIX}_from_{REF_PREFIX}"
    print(f"[build] spots={SPOT_PREFIX} ref={REF_PREFIX} -> {pair_dir}", flush=True)
    status = build_pair(SPOT_PREFIX, REF_PREFIX, pair_dir)
    print(status, flush=True)
    if "blocked" in status:
        rec = {"decision": "BLOCKED", "status": status, "probe": probe}
        OUT_JSON.write_text(json.dumps(rec, indent=2) + "\n")
        raise SystemExit(f"NSCLC pair blocked: {status['blocked']}")
    types = status["kept"]
    genes, P = extract_signature(pair_dir / "reference_subset.h5ad", types)
    cos = malignant_neighbor_cosine(P, types, "tumor", "fibroblast")
    print(f"[cosine] tumor vs fibroblast {cos:.6f}", flush=True)
    if should_abstain(cos, C_STAR):
        rec = {
            "decision": "ABSTAIN",
            "pair_cosine": round(float(cos), 6),
            "status": status,
        }
        OUT_JSON.write_text(json.dumps(rec, indent=2) + "\n")
        print("PROBE_STOP pair cosine ABSTAIN: do not fit", flush=True)
        sys.exit(2)
    print("[fit] t=0 SPGD", flush=True)
    pi, gate = run_spgd(pair_dir / "benchmark_spots.h5ad", pair_dir / "reference_subset.h5ad", types)
    truth = pd.read_csv(pair_dir / "truth_proportions.csv", index_col=0)
    pred = pi.reindex(index=truth.index, columns=truth.columns)
    rec = {
        "source": "He2022_CosMx_NSCLC_zenodo15487520",
        "decision": "KEEP",
        "spot_prefix": SPOT_PREFIX,
        "ref_prefix": REF_PREFIX,
        "n_spots": int(status["n_spots"]),
        "n_types": len(types),
        "types": types,
        "probe_cosine": probe["cosine"],
        "pair_cosine": round(float(cos), 6),
        "c_star": C_STAR,
        "gate": float(gate),
        "overall_rmse": round(point_rmse(truth, pred), 6),
        "tumor_rmse": round(tumor_rmse(truth, pred, "tumor"), 6),
        "type_pcc": round(pcc_type(truth, pred), 6),
        "spot_pcc": round(pcc_spot(truth, pred), 6),
        "n_genes_signature": len(genes),
        "pair_dir": str(pair_dir),
    }
    OUT_JSON.write_text(json.dumps(rec, indent=2) + "\n")
    print(json.dumps(rec, indent=2))
    print("NSCLC numbers stay warehouse-only until folded into F7/F8/T3", flush=True)


if __name__ == "__main__":
    main()
