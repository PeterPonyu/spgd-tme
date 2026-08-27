"""Heavy fits do not run unless the user later sets SPGD_TME_COMPUTE=1."""
from __future__ import annotations

import os
import sys


def require_compute(job: str) -> None:
    if os.environ.get("SPGD_TME_COMPUTE") == "1":
        return
    print(
        f"REFUSING {job}: compute is gated. Scaffold only.\n"
        "Set SPGD_TME_COMPUTE=1 when the user schedules the fit queue.",
        file=sys.stderr,
    )
    raise SystemExit(3)
