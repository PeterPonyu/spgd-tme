#!/usr/bin/env python
"""Ask whether the deciding cosine predicts malignant-column error.

R2 Point 2 asked what justifies c* = 0.80. The answer given was that it is an
inherited round value and that all eight designated calls are invariant over
0.75-0.85. That shows the calls are not borderline. It does not show that a KEEP
coordinate is more accurate than an ABSTAIN one, which is the question behind the
question, and the paper never used the data it already has to answer it.

The collinearity dose-response interpolates each malignant signature toward its
neighbour, so it sweeps the deciding quantity while holding everything else
fixed. That makes it a calibration experiment rather than an observational
correlation, and it is already in the package.

Reads data/plotdata/F3_collinearity_sweep.csv; writes only
revision_v3/out/cutoff_calibration.{csv,json}.
"""
from __future__ import annotations

import collections
import csv
import json
import statistics
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent / "out"
C_STAR = 0.80
LABEL = {"realgt3": "CosMx BCC", "openst": "openST", "realgt": "Xenium"}


def spearman(x, y):
    def rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        out = [0] * len(v)
        for pos, i in enumerate(order):
            out[i] = pos + 1
        return out
    rx, ry = rank(x), rank(y)
    mx, my = statistics.mean(rx), statistics.mean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** 0.5
    return num / den if den else float("nan")


def main() -> None:
    by = collections.defaultdict(list)
    with (ROOT / "data/plotdata/F3_collinearity_sweep.csv").open() as fh:
        for r in csv.DictReader(fh):
            by[r["substrate"]].append((float(r["cosine"]), float(r["tumor_rmse"])))

    rows, crossing = [], {}
    for sub, v in by.items():
        v.sort()
        c = [a for a, _ in v]
        e = [b for _, b in v]
        spans = min(c) < C_STAR <= max(c)
        rows.append({
            "substrate": LABEL.get(sub, sub),
            "n_steps": len(v),
            "cosine_min": round(min(c), 4), "cosine_max": round(max(c), 4),
            "tumor_rmse_min": round(min(e), 4), "tumor_rmse_max": round(max(e), 4),
            "spearman_cosine_vs_error": round(spearman(c, e), 3),
            "monotone_rising": all(e[i] <= e[i + 1] for i in range(len(e) - 1)),
            "sweep_crosses_cutoff": spans,
        })
        if spans:
            below = [(a, b) for a, b in v if a < C_STAR]
            above = [(a, b) for a, b in v if a >= C_STAR]
            crossing = {
                "substrate": LABEL.get(sub, sub),
                "native_cosine": round(below[0][0], 4),
                "native_tumor_rmse": round(below[0][1], 4),
                "first_abstaining_cosine": round(above[0][0], 4),
                "first_abstaining_tumor_rmse": round(above[0][1], 4),
                "error_ratio": round(above[0][1] / below[0][1], 2),
            }

    summary = {
        "c_star": C_STAR,
        "question": "does the deciding cosine predict malignant-column error?",
        "per_substrate": rows,
        "crossing": crossing,
        "reading": (
            "Where the sweep spans the cutoff the deciding quantity orders the "
            "error perfectly and crossing the cutoff more than doubles it, so the "
            "gate's premise holds where it is testable. Only one of the three "
            "substrates spans the cutoff; the other two sit above 0.97 throughout, "
            "and on Xenium the relationship there is absent. The cutoff's position "
            "is therefore calibrated by a single crossing, and the cosine is "
            "informative across the decision-relevant range rather than everywhere."
        ),
    }
    OUT.mkdir(parents=True, exist_ok=True)
    with (OUT / "cutoff_calibration.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    (OUT / "cutoff_calibration.json").write_text(json.dumps(summary, indent=2) + "\n")
    for r in rows:
        print(f"  {r['substrate']:<11} cos {r['cosine_min']:.4f}-{r['cosine_max']:.4f}  "
              f"rho={r['spearman_cosine_vs_error']:+.3f}  crosses={r['sweep_crosses_cutoff']}")
    print(f"  crossing: {crossing['native_tumor_rmse']} -> "
          f"{crossing['first_abstaining_tumor_rmse']} ({crossing['error_ratio']}x)")


if __name__ == "__main__":
    main()
