#!/usr/bin/env python
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.compute_gate import require_compute
from src.metrics_tme import pcc_spot, pcc_type, point_rmse, tumor_rmse
from src.paths import DONOR_PAIRS, LOCKS, PLOTDATA
from src.refuse import apply_abstain, should_abstain
from src.signature import extract_signature
from src.spgd_wrap import run_spgd
from src.window_io import f5_done

NEW_PAIRS = ("A_from_B", "B_from_A", "D_from_C")
FORBIDDEN = {0.2034, 0.1126}
F5_PART_COLS = {
    "pair",
    "spot_donor",
    "ref_donor",
    "RMSE",
    "PCC_type",
    "PCC_spot",
    "tumor_rmse",
    "pseudobulk_jsd",
    "source",
}


def _pseudobulk_jsd(spots_h5ad: Path, ref_h5ad: Path, types: list[str]) -> float:
    import anndata as ad

    spots = ad.read_h5ad(spots_h5ad)
    ref = ad.read_h5ad(ref_h5ad)
    shared = [g for g in map(str, spots.var_names) if g in set(map(str, ref.var_names))]
    if len(shared) < 32:
        raise SystemExit(f"JSD gene overlap {len(shared)} < 32")
    spots = spots[:, shared]
    Xs = spots.X
    Xs = np.asarray(Xs.todense()) if hasattr(Xs, "todense") else np.asarray(Xs)
    spot_bulk = np.asarray(Xs.sum(0)).ravel()
    spot_bulk = spot_bulk / spot_bulk.sum()
    genes, P = extract_signature(ref_h5ad, types)
    gene_ix = {g: i for i, g in enumerate(genes)}
    ref_bulk = np.array([P.mean(1)[gene_ix[g]] if g in gene_ix else 0.0 for g in shared])
    ref_bulk = ref_bulk / ref_bulk.sum()
    m = 0.5 * (spot_bulk + ref_bulk)

    def kl(p, q):
        p = np.clip(p, 1e-12, None)
        q = np.clip(q, 1e-12, None)
        return float(np.sum(p * np.log(p / q)))

    return 0.5 * kl(spot_bulk, m) + 0.5 * kl(ref_bulk, m)


def _num(x):
    x = float(x)
    return "" if pd.isna(x) else round(x, 6)


def _load_part(name: str) -> dict | None:
    path = PLOTDATA / f"F5_part_{name}.csv"
    if not path.is_file() or path.stat().st_size == 0:
        return None
    df = pd.read_csv(path)
    if F5_PART_COLS - set(df.columns) or len(df) < 1:
        return None
    rec = df.iloc[0].to_dict()
    if rec.get("source") != "computed":
        return None
    return rec


def _forbid_locks(row: dict, name: str) -> None:
    for key in ("RMSE", "PCC_type", "PCC_spot"):
        val = row[key]
        if val != "" and not pd.isna(val) and float(val) in FORBIDDEN:
            raise SystemExit(f"forbidden lock value {val} in {name}.{key}")


def main() -> None:
    require_compute("04_run_donor_transfer")
    if f5_done():
        t3 = PLOTDATA / "T3_donor_matrix.csv"
        if not t3.is_file():
            import shutil

            shutil.copyfile(PLOTDATA / "F5_donor_transfer.csv", t3)
        print("[F5] skip complete", flush=True)
        return
    cd = json.loads((LOCKS / "cd_lock.json").read_text())
    rows = [
        {
            "pair": "C_from_D",
            "spot_donor": "PatientC",
            "ref_donor": "PatientD",
            "RMSE": cd["RMSE"],
            "PCC_type": cd["PCC_type"],
            "PCC_spot": cd["PCC_spot"],
            "tumor_rmse": "",
            "pseudobulk_jsd": "",
            "source": "locked",
        }
    ]
    PLOTDATA.mkdir(parents=True, exist_ok=True)
    status_lines = []
    for name in NEW_PAIRS:
        part = PLOTDATA / f"F5_part_{name}.csv"
        cached = _load_part(name)
        if cached is not None:
            _forbid_locks(cached, name)
            rows.append(cached)
            status_lines.append(f"RESUME {name}")
            print(f"[F5] resume {name} from {part}", flush=True)
            continue
        d = DONOR_PAIRS / name
        truth_p = d / "truth_proportions.csv"
        spots = d / "benchmark_spots_counts.h5ad"
        ref = d / "reference_subset.h5ad"
        if not truth_p.exists():
            raise SystemExit(f"BLOCKED {name}: missing truth")
        if not spots.exists() or not ref.exists():
            raise SystemExit(f"BLOCKED {name}: missing h5ad")
        truth = pd.read_csv(truth_p, index_col=0)
        types = list(truth.columns)
        pi, _ = run_spgd(spots, ref, types)
        man = json.loads((d / "manifest.json").read_text())
        mal = "Cancer.cells" if "Cancer.cells" in types else types[0]
        pairs = json.loads((LOCKS / "type_pairs.json").read_text())
        c_star = float(json.loads((LOCKS / "c_star.json").read_text())["value"])
        cos_lock = float(pairs["realgt3"]["cosine"])
        if should_abstain(cos_lock, c_star):
            pi = apply_abstain(pi, [mal])
        row = {
            "pair": name,
            "spot_donor": man["spot_donor"],
            "ref_donor": man["ref_donor"],
            "RMSE": _num(point_rmse(truth, pi)),
            "PCC_type": _num(pcc_type(truth, pi)),
            "PCC_spot": _num(pcc_spot(truth, pi)),
            "tumor_rmse": _num(tumor_rmse(truth, pi, mal)),
            "pseudobulk_jsd": _num(_pseudobulk_jsd(spots, ref, types)),
            "source": "computed",
        }
        json.dumps(row, allow_nan=False)
        _forbid_locks(row, name)
        pd.DataFrame([row]).to_csv(part, index=False)
        rows.append(row)
        status_lines.append(f"OK {name}")
        print(row)
    f5 = pd.DataFrame(rows)
    f5.to_csv(PLOTDATA / "F5_donor_transfer.csv", index=False)
    f5.to_csv(PLOTDATA / "T3_donor_matrix.csv", index=False)
    print("[write] F5/T3")


if __name__ == "__main__":
    main()
