#!/usr/bin/env python
"""revision_v3 / downstream_and_gate_fulln.py

Task B (downstream of the neighbor-rule flip) + Task C (full-n gate-input
consistency) for the platform benchmarks.

For each platform library the working signature is fit once at FULL n (no
400-spot bound) through the released baseline primitives. From that single fit
we report:

* full-n gate-input consistency: the reportability cosine on the pre-gate mean
  signature P versus the platform-corrected working signature S (Task C, the
  full-n version of the bounded C03 audit);
* for CosMx BCC (realgt3), the exact downstream consequence of the max-eligible
  rule flipping the historical KEEP to ABSTAIN: the malignant (Cancer.cells)
  coordinate is withheld and the remaining simplex renormalized, and the
  non-malignant composition metrics are recomputed (Task B).

Integrity: reads references read-only; writes only to revision_v3/out/. c*=0.80
frozen. No lock or historical output is modified. The malignant coordinate that
is withheld under ABSTAIN is reported as withheld, never scored as zero.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd

DECONV = Path(os.environ.get("SPGD_DECONV_ROOT", Path(__file__).resolve().parents[1] / "data" / "external" / "deconv-lab"))
OUT = Path(__file__).resolve().parent / "out"
OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(DECONV / "src"))
from deconv_metrics import (  # noqa: E402
    _fit_gamma_pois,
    _nnls_setup,
    _poisson_fit,
    _specificity_weight,
    point_metrics,
    simplex,
)

C_STAR = 0.80
PLATFORM = {
    "openST": ("openst_benchmark", "Tumor", "Tumor_Keratin_Pearl"),
    "Xenium": ("realgt_benchmark", "Invasive_Tumor", "Prolif_Invasive_Tumor"),
    "Xenium FLEX": ("realgt2_benchmark", "Invasive_Tumor", "Prolif_Invasive_Tumor"),
    "CosMx BCC": ("realgt3_benchmark", "Cancer.cells", "Normal.Kerat"),
}


def _cos_cols(M: np.ndarray, types: list[str], a: str, b: str) -> float:
    x, y = M[:, types.index(a)], M[:, types.index(b)]
    return float(np.dot(x, y) / (np.linalg.norm(x) * np.linalg.norm(y) + 1e-12))


def fit_full(base: Path, n_gamma: int = 8, n_fit: int = 150, seed: int = 0):
    """Full-n build_v4 fit that also returns P, S, and pi_hat for auditing."""
    sp = base / "benchmark_spots_counts.h5ad"
    if not sp.is_file():
        sp = base / "benchmark_spots.h5ad"
    seed_types = list(pd.read_csv(base / "truth_proportions.csv", index_col=0, nrows=0).columns)
    sig, Y, idx, types = _nnls_setup(str(sp), str(base / "reference_subset.h5ad"), seed_types)
    P = sig / np.clip(sig.sum(0, keepdims=True), 1e-12, None)
    w = _specificity_weight(P)
    Pw, Yw = P * w[:, None], Y * w[None, :]
    lo, hi = np.log(0.1), np.log(10.0)
    rng = np.random.default_rng(seed)
    perm = rng.permutation(Yw.shape[0])
    h = Yw.shape[0] // 2
    A, B = Yw[perm[:h]], Yw[perm[h:]]
    z = np.zeros(Pw.shape[0])

    def dev(lg, Yt):
        S = np.exp(lg)[:, None] * Pw
        W = _poisson_fit(S, Yt, n_fit)
        r = W @ S.T + 1e-9
        return float(np.mean(np.sum(r - Yt * np.log(r), axis=1)))

    lgA = _fit_gamma_pois(Pw, A, n_gamma, n_fit, lo, hi)
    lgB = _fit_gamma_pois(Pw, B, n_gamma, n_fit, lo, hi)
    gate = float(np.clip(0.5 * ((dev(z, B) - dev(lgA, B)) / abs(dev(z, B) + 1e-9)
                                + (dev(z, A) - dev(lgB, A)) / abs(dev(z, A) + 1e-9)), 0.0, 1.0))
    lg_full = _fit_gamma_pois(Pw, Yw, n_gamma, n_fit, lo, hi)
    S = np.exp(gate * lg_full)[:, None] * Pw
    pi = simplex(pd.DataFrame(_poisson_fit(S, Yw, n_fit * 2), index=idx, columns=types))
    return {"types": types, "idx": idx, "P": P, "S": S, "gate": gate, "pi": pi, "n_spots": len(idx), "n_genes": P.shape[0]}


def abstain_renormalize(pi: pd.DataFrame, malignant: str) -> pd.DataFrame:
    keep_cols = [c for c in pi.columns if c != malignant]
    block = pi[keep_cols].to_numpy(float)
    s = block.sum(1, keepdims=True)
    s[s == 0] = 1.0
    return pd.DataFrame(block / s, index=pi.index, columns=keep_cols)


def main() -> None:
    gate_rows = []
    downstream = {}
    for lib, (d, mal, nbr) in PLATFORM.items():
        base = DECONV / "data" / d
        f = fit_full(base)
        types = f["types"]
        cp = _cos_cols(f["P"], types, mal, nbr)
        cs = _cos_cols(f["S"], types, mal, nbr)
        gate_rows.append({
            "library": lib, "malignant": mal, "neighbor": nbr,
            "n_spots_full": f["n_spots"], "n_genes": f["n_genes"], "gate_g": round(f["gate"], 6),
            "cosine_P": round(cp, 6), "cosine_S": round(cs, 6), "delta_S_minus_P": round(cs - cp, 6),
            "decision_P": "ABSTAIN" if cp >= C_STAR else "KEEP",
            "decision_S": "ABSTAIN" if cs >= C_STAR else "KEEP",
            "status": "identical" if (cp >= C_STAR) == (cs >= C_STAR) else "DISCREPANT",
        })
        print(f"[{lib}] full-n={f['n_spots']} gate={f['gate']:.4f} cos_P={cp:.6f} cos_S={cs:.6f}")

        if lib == "CosMx BCC":
            truth = pd.read_csv(base / "truth_proportions.csv", index_col=0)
            truth = truth.reindex(index=f["pi"].index).dropna(how="all")
            common = f["pi"].index.intersection(truth.index)
            pi = f["pi"].loc[common]
            tr = truth.loc[common]
            keep_metrics = point_metrics(tr, pi)
            tumor_rmse = float(np.sqrt(np.mean((pi[mal].to_numpy(float) - tr[mal].to_numpy(float)) ** 2)))
            tr_nm = abstain_renormalize(tr, mal)
            pi_nm = abstain_renormalize(pi, mal)
            abstain_metrics = point_metrics(tr_nm, pi_nm)
            downstream = {
                "library": lib, "malignant_withheld": mal, "n_spots_full": int(len(common)),
                "historical_call": "KEEP (designated Normal.Kerat cos 0.603666)",
                "max_eligible_call": "ABSTAIN (Melanocyte cos 0.824700)",
                "KEEP_reported": {
                    "overall_RMSE": round(keep_metrics["RMSE"], 6),
                    "tumor_RMSE_reported": round(tumor_rmse, 6),
                    "PCC_type": round(keep_metrics["PCC_type"], 6),
                    "PCC_spot": round(keep_metrics["PCC_spot"], 6),
                },
                "ABSTAIN_nonmalignant": {
                    "tumor_RMSE_reported": "withheld (malignant coordinate missing, not zero)",
                    "nonmalignant_RMSE": round(abstain_metrics["RMSE"], 6),
                    "nonmalignant_PCC_type": round(abstain_metrics["PCC_type"], 6),
                    "nonmalignant_PCC_spot": round(abstain_metrics["PCC_spot"], 6),
                },
                "interpretation": (
                    "Under the max-eligible rule BCC flips to ABSTAIN, so the Cancer.cells "
                    "coordinate would be withheld rather than reported. The historical KEEP "
                    "tumor RMSE above is what would no longer be reported; the non-malignant "
                    "composition is re-scored after malignant withholding and renormalization."
                ),
            }
            print(f"  [BCC downstream] KEEP tumor_RMSE={tumor_rmse:.4f} "
                  f"-> ABSTAIN nonmal RMSE={abstain_metrics['RMSE']:.4f}")

    gate = pd.DataFrame(gate_rows)
    gate.to_csv(OUT / "gate_input_fulln.csv", index=False)
    (OUT / "gate_input_fulln.json").write_text(json.dumps(gate_rows, indent=2) + "\n")
    (OUT / "bcc_abstain_downstream.json").write_text(json.dumps(downstream, indent=2) + "\n")

    print("\n=== full-n gate-input consistency (Task C) ===")
    print(gate.to_string(index=False))
    print("\nwrote ->", OUT)


if __name__ == "__main__":
    main()
