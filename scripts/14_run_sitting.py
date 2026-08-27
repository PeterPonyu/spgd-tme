#!/usr/bin/env python
"""One sitting: pytest → preflight → Q2 → Q3 → INTERVAL → Q4 → Q5 → Q6 → P4c. Fail-fast."""
from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.paths import TMP
from src.window_io import (
    bootstrap_done,
    emit_done,
    f3_done,
    f4_done,
    f5_done,
    fulln_done,
    t2_done,
)

PY = sys.executable
LOG = TMP / "sitting.log"
STEPS = (
    (
        "pytest",
        [
            PY,
            "-m",
            "pytest",
            "tests/test_sitting_ready.py",
            "tests/test_trainer_wiring.py",
            "tests/test_refuse.py",
            "tests/test_compute_gate.py",
            "tests/test_locks.py",
            "tests/test_scaffold.py",
            "-q",
        ],
        False,
        lambda: False,
    ),
    ("preflight", [PY, "scripts/00_preflight_windows.py"], False, lambda: False),
    ("Q2", [PY, "scripts/02_run_collinearity_sweep.py"], True, f3_done),
    ("Q3", [PY, "scripts/03_run_refusal.py"], False, f4_done),
    ("INTERVAL", [PY, "scripts/13_bootstrap_t0.py"], False, bootstrap_done),
    ("Q4", [PY, "scripts/04_run_donor_transfer.py"], True, f5_done),
    ("Q5", [PY, "scripts/05_timing.py"], True, t2_done),
    ("Q6", [PY, "scripts/06_emit_plotdata.py"], False, emit_done),
    ("P4c", [PY, "scripts/10_confirm_t0_fulln.py"], True, fulln_done),
)


def main() -> None:
    if os.environ.get("SPGD_TME_COMPUTE") != "1":
        raise SystemExit("REFUSING sitting: set SPGD_TME_COMPUTE=1 only when you sit.")
    TMP.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    log = LOG.open("a", encoding="utf-8")
    try:
        log.write(f"\n=== SITTING START {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n")
        log.flush()
        env = os.environ.copy()
        env["PYTHONUNBUFFERED"] = "1"
        for name, args, needs_gate, done in STEPS:
            if done():
                msg = f"=== {name} SKIP already complete ==="
                print(msg, flush=True)
                log.write(msg + "\n")
                log.flush()
                continue
            print(f"\n=== {name} ===", flush=True)
            log.write(f"=== {name} ===\n")
            log.flush()
            run_env = env.copy()
            if needs_gate:
                run_env["SPGD_TME_COMPUTE"] = "1"
            proc = subprocess.run(args, cwd=ROOT, env=run_env)
            if proc.returncode != 0:
                raise SystemExit(f"SITTING STOPPED at {name} exit={proc.returncode}")
            msg = f"=== {name} OK elapsed_min={(time.time()-t0)/60:.1f} ==="
            print(msg, flush=True)
            log.write(msg + "\n")
            log.flush()
        print(f"SITTING_OK hours={(time.time()-t0)/3600:.2f}")
        log.write(f"SITTING_OK hours={(time.time()-t0)/3600:.2f}\n")
    finally:
        log.close()


if __name__ == "__main__":
    main()
