#!/usr/bin/env python
"""Time full-n t=0 on openST and Xenium to test the 33-job hour projection.

CosMx full-n t=0 was already timed by script 16 (234.554 s). This probe does not
overwrite sitting F3/F4/F5 tables, donor pairs, or timing_probe.csv.
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.compute_gate import require_compute
from src.paths import BENCH, PLOTDATA
from src.spgd_wrap import run_spgd

OUT = PLOTDATA / "timing_probe_three_substrates.csv"
PRIOR = PLOTDATA / "timing_probe.csv"
LOCKED = (
    PLOTDATA / "F3_collinearity_sweep.csv",
    PLOTDATA / "F3_t0_fulln.csv",
    PLOTDATA / "F3_pi_t0_realgt3.csv",
    PLOTDATA / "F4_keep_spatial.csv",
    PLOTDATA / "F5_donor_transfer.csv",
    PLOTDATA / "timing_probe.csv",
)
EXPECTED_N = {"openst": 6971, "realgt": 2864, "realgt3": 5686}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fit(sub: str) -> tuple[int, float]:
    bench = BENCH[sub]
    types = list(pd.read_csv(bench / "truth_proportions.csv", index_col=0, nrows=0).columns)
    t0 = time.perf_counter()
    pi, gate = run_spgd(bench / "benchmark_spots.h5ad", bench / "reference_subset.h5ad", types)
    elapsed = time.perf_counter() - t0
    n = int(len(pi))
    print(f"[probe] {sub}_t0_fulln n={n} gate={gate:.4f} seconds={elapsed:.3f}", flush=True)
    if n != EXPECTED_N[sub]:
        raise SystemExit(f"{sub}: expected {EXPECTED_N[sub]} spots, got {n}")
    return n, elapsed


def main() -> None:
    require_compute("17_time_fulln_three_substrates")
    if OUT.is_file() and OUT.stat().st_size > 0:
        raise SystemExit(f"REFUSING overwrite: {OUT}")
    if not PRIOR.is_file() or PRIOR.stat().st_size == 0:
        raise SystemExit(f"missing CosMx timing {PRIOR}")
    prior = pd.read_csv(PRIOR)
    cosmx = prior.loc[prior["job"] == "realgt3_t0_fulln"]
    if len(cosmx) != 1:
        raise SystemExit("timing_probe.csv missing realgt3_t0_fulln")
    sitting_sha = {p.name: _sha(p) for p in LOCKED if p.is_file()}
    started = datetime.now(timezone.utc).isoformat()
    rows = [
        {
            "job": "realgt3_t0_fulln",
            "n_spots": int(cosmx.iloc[0]["n_spots"]),
            "seconds": float(cosmx.iloc[0]["seconds"]),
            "source": "timing_probe.csv",
            "started_utc": started,
        }
    ]
    for sub in ("openst", "realgt"):
        n, sec = _fit(sub)
        rows.append(
            {
                "job": f"{sub}_t0_fulln",
                "n_spots": n,
                "seconds": round(sec, 3),
                "source": "timing_probe_three_substrates",
                "started_utc": started,
            }
        )
    by_job = {r["job"]: r["seconds"] for r in rows}
    cycle = by_job["openst_t0_fulln"] + by_job["realgt_t0_fulln"] + by_job["realgt3_t0_fulln"]
    hours = 11.0 * cycle / 3600.0
    naive = 33.0 * by_job["realgt3_t0_fulln"] / 3600.0
    rows.append(
        {
            "job": "projected_11_x_sum3_hours",
            "n_spots": 33,
            "seconds": round(hours, 3),
            "source": "11 * (openst+realgt+realgt3)_fulln_t0 / 3600",
            "started_utc": started,
        }
    )
    rows.append(
        {
            "job": "naive_33_x_cosmx_hours",
            "n_spots": 33,
            "seconds": round(naive, 3),
            "source": "33 * realgt3_fulln / 3600",
            "started_utc": started,
        }
    )
    PLOTDATA.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT, index=False)
    after = {p.name: _sha(p) for p in LOCKED if p.is_file()}
    if after != sitting_sha:
        raise SystemExit("sitting plotdata changed during probe")
    print("[write]", OUT)
    print(
        json.dumps(
            {
                "openst_fulln_seconds": by_job["openst_t0_fulln"],
                "realgt_fulln_seconds": by_job["realgt_t0_fulln"],
                "realgt3_fulln_seconds": by_job["realgt3_t0_fulln"],
                "one_t_cycle_seconds": round(cycle, 3),
                "projected_33_fulln_hours": round(hours, 3),
                "naive_cosmx_only_hours": round(naive, 3),
            }
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
