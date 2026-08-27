#!/usr/bin/env python
"""Time CosMx 400-spot vs full-n t=0 and save full-n π̂ for the KEEP map.

Does not overwrite sitting F3/F4/F5 tables, donor pairs, or F3_pi_t0_realgt3.csv.
"""
from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.compute_gate import require_compute
from src.paths import BENCH, PLOTDATA, TMP
from src.spgd_wrap import run_spgd

OUT_PI = PLOTDATA / "F3_pi_fulln_realgt3.csv"
OUT_KEEP = PLOTDATA / "F4_keep_spatial_fulln.csv"
OUT_SUM = PLOTDATA / "F4_keep_spatial_fulln_summary.csv"
OUT_TIME = PLOTDATA / "timing_probe.csv"
LOCKED = (
    PLOTDATA / "F3_collinearity_sweep.csv",
    PLOTDATA / "F3_t0_fulln.csv",
    PLOTDATA / "F3_pi_t0_realgt3.csv",
    PLOTDATA / "F4_keep_spatial.csv",
    PLOTDATA / "F5_donor_transfer.csv",
)


def _refuse_overwrite(path: Path) -> None:
    if path.is_file() and path.stat().st_size > 0:
        raise SystemExit(f"REFUSING overwrite: {path}")


def _sha_lock(path: Path) -> str:
    import hashlib

    return hashlib.sha256(path.read_bytes()).hexdigest()


def _join_keep(pi: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    import anndata as ad

    if "Cancer.cells" not in pi.columns:
        raise SystemExit("full-n π̂ missing Cancer.cells")
    h5 = BENCH["realgt3"] / "benchmark_spots.h5ad"
    adata = ad.read_h5ad(h5, backed="r")
    if "spatial" not in adata.obsm:
        adata.file.close()
        raise SystemExit("realgt3 spots lack spatial")
    xy = pd.DataFrame(adata.obsm["spatial"], index=list(adata.obs_names), columns=["x", "y"])
    adata.file.close()
    tumor = pi["Cancer.cells"].astype(float).rename("tumor_hat")
    out = xy.join(tumor, how="inner")
    if len(out) != len(pi):
        raise SystemExit(f"full-n KEEP join {len(out)} != pi {len(pi)}")
    out = out.reset_index().rename(columns={"index": "spot"})
    summary = pd.DataFrame(
        [
            {
                "substrate": "realgt3",
                "t": 0.0,
                "decision": "KEEP",
                "n_spots": int(len(out)),
                "tumor_hat_mean": round(float(out["tumor_hat"].mean()), 6),
                "tumor_hat_median": round(float(out["tumor_hat"].median()), 6),
                "tumor_hat_q25": round(float(out["tumor_hat"].quantile(0.25)), 6),
                "tumor_hat_q75": round(float(out["tumor_hat"].quantile(0.75)), 6),
                "source": "fulln_pi_probe",
            }
        ]
    )
    return out, summary


def _fit(spots: Path, ref: Path, types: list[str], label: str) -> tuple[pd.DataFrame, float]:
    t0 = time.perf_counter()
    pi, gate = run_spgd(spots, ref, types)
    elapsed = time.perf_counter() - t0
    print(
        f"[probe] {label} n={len(pi)} gate={gate:.4f} seconds={elapsed:.3f}",
        flush=True,
    )
    return pi, elapsed


def main() -> None:
    require_compute("16_time_and_save_fulln_pi")
    for path in (OUT_PI, OUT_KEEP, OUT_SUM, OUT_TIME):
        _refuse_overwrite(path)
    sitting_sha = {p.name: _sha_lock(p) for p in LOCKED if p.is_file()}
    bench = BENCH["realgt3"]
    truth = pd.read_csv(bench / "truth_proportions.csv", index_col=0)
    types = list(truth.columns)
    ref = bench / "reference_subset.h5ad"
    spots400 = TMP / "realgt3_sweep400.h5ad"
    if not spots400.is_file():
        raise SystemExit(f"missing subsample {spots400}")
    rows = []
    started = datetime.now(timezone.utc).isoformat()

    _, sec400 = _fit(spots400, ref, types, "realgt3_t0_n400")
    rows.append(
        {
            "job": "realgt3_t0_n400",
            "n_spots": 400,
            "seconds": round(sec400, 3),
            "source": "timing_probe",
            "started_utc": started,
        }
    )

    pi, sec_full = _fit(bench / "benchmark_spots.h5ad", ref, types, "realgt3_t0_fulln")
    if len(pi) != 5686:
        raise SystemExit(f"expected 5686 CosMx spots, got {len(pi)}")
    rows.append(
        {
            "job": "realgt3_t0_fulln",
            "n_spots": int(len(pi)),
            "seconds": round(sec_full, 3),
            "source": "timing_probe",
            "started_utc": started,
        }
    )
    PLOTDATA.mkdir(parents=True, exist_ok=True)
    pi.to_csv(OUT_PI)
    keep, summary = _join_keep(pi)
    keep.to_csv(OUT_KEEP, index=False)
    summary.to_csv(OUT_SUM, index=False)
    scale = 33 * sec_full / 3600.0
    rows.append(
        {
            "job": "projected_fulln_x11_x3_hours",
            "n_spots": 33,
            "seconds": round(scale, 3),
            "source": "33 * realgt3_fulln / 3600",
            "started_utc": started,
        }
    )
    pd.DataFrame(rows).to_csv(OUT_TIME, index=False)
    after_sha = {p.name: _sha_lock(p) for p in LOCKED if p.is_file()}
    if after_sha != sitting_sha:
        raise SystemExit("sitting plotdata changed during probe")
    print("[write]", OUT_PI, OUT_KEEP, OUT_SUM, OUT_TIME)
    print(
        json.dumps(
            {
                "n400_seconds": round(sec400, 3),
                "fulln_seconds": round(sec_full, 3),
                "projected_33_fulln_hours": round(scale, 3),
            }
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
