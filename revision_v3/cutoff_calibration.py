#!/usr/bin/env python
"""Ask where along the deciding cosine the malignant error becomes large.

R2 Point 2 asked what justifies c* = 0.80. The answer given was that it is an
inherited round value and that all eight designated calls are invariant over
0.75-0.85. Invariance shows the calls are not borderline. It does not say where
on the cosine axis the coordinate stops being usable, and the paper never used
the data it already has to look.

The collinearity dose-response interpolates each malignant signature toward its
neighbour at eleven steps t = 0.0 ... 1.0, so it moves the deciding quantity
while holding the spots, the truth and the fit procedure fixed.

Two limits are recorded with the result rather than left for a reader to find.

Both the cosine and the error are functions of the same interpolation parameter,
so a high rank correlation between them is close to guaranteed wherever the error
rises with t at all. The sweep therefore locates where along the cosine axis the
error becomes large; it does not establish the cosine as an independent predictor
of error in unmanipulated data.

And the ratio across the cutoff depends on which pair of steps is compared. The
native step and the first abstaining step are three interpolation steps apart, so
that ratio is not the marginal cost of crossing. Both are reported.

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
            by[r["substrate"]].append((float(r["t"]), float(r["cosine"]), float(r["tumor_rmse"])))

    rows, crossing = [], {}
    for sub, v in by.items():
        v.sort()  # by interpolation step
        c = [b for _, b, _ in v]
        e = [x for _, _, x in v]
        spans = min(c) < C_STAR <= max(c)
        rows.append({
            "substrate": LABEL.get(sub, sub),
            "n_steps": len(v),
            "cosine_min": round(min(c), 4), "cosine_max": round(max(c), 4),
            "tumor_rmse_at_native": round(e[0], 4),
            "tumor_rmse_min": round(min(e), 4), "tumor_rmse_max": round(max(e), 4),
            "spearman_cosine_vs_error": round(spearman(c, e), 3),
            # Both quantities rise with t by construction, so this flag says
            # whether the error responded at all, not whether the cosine predicts it.
            "error_monotone_in_t": all(e[i] <= e[i + 1] for i in range(len(e) - 1)),
            "sweep_crosses_cutoff": spans,
        })
        if spans:
            below = [(a, b, x) for a, b, x in v if b < C_STAR]
            above = [(a, b, x) for a, b, x in v if b >= C_STAR]
            last_keep, first_abstain = below[-1], above[0]
            crossing = {
                "substrate": LABEL.get(sub, sub),
                "native_t": below[0][0],
                "native_cosine": round(below[0][1], 4),
                "native_tumor_rmse": round(below[0][2], 4),
                # The marginal cost of crossing: the two adjacent steps that straddle c*.
                "last_keep_t": last_keep[0],
                "last_keep_cosine": round(last_keep[1], 4),
                "last_keep_tumor_rmse": round(last_keep[2], 4),
                "first_abstain_t": first_abstain[0],
                "first_abstain_cosine": round(first_abstain[1], 4),
                "first_abstain_tumor_rmse": round(first_abstain[2], 4),
                "adjacent_step_ratio": round(first_abstain[2] / last_keep[2], 2),
                "native_to_first_abstain_ratio": round(first_abstain[2] / below[0][2], 2),
                "steps_between_native_and_first_abstain":
                    round((first_abstain[0] - below[0][0]) / 0.1),
            }

    summary = {
        "c_star": C_STAR,
        "question": "where along the deciding cosine does the malignant error become large?",
        "design": (
            "Eleven-step interpolation of the malignant signature toward its neighbour. "
            "The cosine and the error are both functions of the interpolation parameter, "
            "so their rank correlation is not evidence that the cosine predicts error "
            "independently; what the sweep gives is the position on the cosine axis at "
            "which the error becomes large."
        ),
        "per_substrate": rows,
        "crossing": crossing,
        "reading": (
            "Only CosMx BCC spans the cutoff, because openST and Xenium sit above 0.97 at "
            "every step. On CosMx BCC the malignant error rises monotonically across the "
            "sweep, from 0.1542 at the native cosine 0.6037 to 0.6862 at 1.0. The two steps "
            "that straddle the cutoff are 0.2805 at cosine 0.7871 and 0.3604 at 0.8548, a "
            "factor of 1.29; measured instead from the native step, three interpolation "
            "steps below, the factor is 2.34. On openST the error rises over the sweep as "
            "a whole, while on Xenium it rises to 0.1759 and falls back to 0.1272 before "
            "the final step, so the error there is not monotone in the sweep at all. "
            "The cutoff's position is calibrated by a single library's crossing, and the "
            "sweep says where the error becomes large rather than that the cosine predicts "
            "it in unmanipulated data."
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
              f"rho={r['spearman_cosine_vs_error']:+.3f}  "
              f"err_monotone={r['error_monotone_in_t']}  crosses={r['sweep_crosses_cutoff']}")
    print(f"  crossing (adjacent): {crossing['last_keep_tumor_rmse']} -> "
          f"{crossing['first_abstain_tumor_rmse']} ({crossing['adjacent_step_ratio']}x)")
    print(f"  crossing (from native, {crossing['steps_between_native_and_first_abstain']} steps): "
          f"{crossing['native_tumor_rmse']} -> {crossing['first_abstain_tumor_rmse']} "
          f"({crossing['native_to_first_abstain_ratio']}x)")


if __name__ == "__main__":
    main()
