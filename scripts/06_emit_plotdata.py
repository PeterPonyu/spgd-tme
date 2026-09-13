#!/usr/bin/env python
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.paths import BCC_EXPORT, BENCH, CBC_CROSSDONOR, CBC_MS, LOCKS, PLOTDATA

F3_COLS = {
    "substrate",
    "t",
    "cosine",
    "tumor_rmse",
    "malignant",
    "neighbor",
    "c_star",
    "abstain",
}
F4_COLS = {
    "substrate",
    "t",
    "cosine",
    "rmse_gate_off",
    "rmse_gate_on",
    "refused",
    "refusal_rate",
    "c_star",
}
F5_COLS = {
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
T2_STEPS = {
    "extract_signature",
    "specificity_weight",
    "fit_gamma",
    "self_gate",
    "refuse",
    "poisson_fit",
}
BANNED_TEXT = ("survival", "biomarker")
BANNED_NUM = {0.2034, 0.1126}


def _sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _check_cols(path: Path, required: set[str]) -> None:
    if not path.exists():
        raise SystemExit(f"missing {path}")
    df = pd.read_csv(path)
    missing = required - set(df.columns)
    if missing:
        raise SystemExit(f"{path.name} missing columns {missing}")
    blob = path.read_text().lower()
    for tok in BANNED_TEXT:
        if tok in blob:
            raise SystemExit(f"banned token {tok} in {path}")
    for col in df.columns:
        for val in df[col]:
            try:
                if float(val) in BANNED_NUM:
                    raise SystemExit(f"banned lock value {val} in {path.name}.{col}")
            except (TypeError, ValueError):
                continue


def main() -> None:
    _check_cols(PLOTDATA / "F3_collinearity_sweep.csv", F3_COLS)
    _check_cols(PLOTDATA / "F4_refusal.csv", F4_COLS)
    _check_cols(PLOTDATA / "F5_donor_transfer.csv", F5_COLS)
    t2 = pd.read_csv(PLOTDATA / "T2_timing.csv")
    if set(t2["step"]) != T2_STEPS:
        raise SystemExit(f"T2 steps {set(t2['step'])} != {T2_STEPS}")
    _check_cols(PLOTDATA / "T3_donor_matrix.csv", F5_COLS)

    spatial = CBC_MS / "data/spatial_maps.csv"
    (PLOTDATA / "CBC_spatial_maps.REUSE").write_text(
        f"provider://spgd-deconv/manuscript/data/spatial_maps.csv\t{_sha(spatial)}\trole=cbc_reuse_not_f2_hero\n"
    )

    rows = []
    for name in ("cells.txt", "features.txt", "metadata.csv", "counts_genes_x_cells.mtx.gz"):
        p = BCC_EXPORT / name
        rows.append({"item": name, "path": p.name, "sha256": _sha(p), "role": "bcc_export"})
    for key in ("openst", "realgt", "realgt2", "realgt3", "realgt4"):
        p = BENCH[key] / "reference_subset.h5ad"
        role = "orthogonal_ref" if key == "realgt2" else "benchmark_ref"
        rows.append({"item": f"{key}_ref", "path": p.name, "sha256": _sha(p), "role": role})
    rows.append(
        {
            "item": "crossdonor.csv",
            "path": CBC_CROSSDONOR.name,
            "sha256": _sha(CBC_CROSSDONOR),
            "role": "cbc_lock",
        }
    )
    for name, role in (("type_pairs.json", "type_pairs"), ("c_star.json", "c_star")):
        p = LOCKS / name
        rows.append({"item": name, "path": p.name, "sha256": _sha(p), "role": role})
    pd.DataFrame(rows).to_csv(PLOTDATA / "T1_materials.csv", index=False)
    print("[write] T1 + CBC reuse hash; schemas OK")


if __name__ == "__main__":
    main()
