"""Draw Figure 15 from the full-n comparator tables.

Works from the lab tree (revision_v3/) and from the Supplementary bundle
(render/), without machine-local paths. Panel D does not rank neighbor rules
from incommensurable RMSEs.
"""
from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.font_manager import fontManager

HERE = Path(__file__).resolve().parent


def layout() -> tuple[list[Path], Path]:
    if HERE.name == "render":
        return [HERE.parent / "analyses"], HERE.parent / "figures"
    return [HERE / "analyses", HERE / "out"], HERE.parents[1] / "manuscript" / "figs" / "rendered"


def find_table(search: list[Path], name: str) -> Path:
    for base in search:
        hits = sorted(base.rglob(name))
        if hits:
            return hits[0]
    raise FileNotFoundError(name)


def set_font() -> None:
    names = {font.name for font in fontManager.ttflist}
    plt.rcParams.update(
        {
            "font.family": "Tinos" if "Tinos" in names else "DejaVu Serif",
            "font.size": 10,
            "axes.titlesize": 11,
            "axes.labelsize": 10,
            "xtick.labelsize": 8.5,
            "ytick.labelsize": 9,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "savefig.dpi": 300,
        }
    )


def main() -> None:
    search, out = layout()
    out.mkdir(parents=True, exist_ok=True)
    set_font()
    rule = pd.read_csv(find_table(search, "library_rule_comparison.csv")).drop_duplicates("library")
    gate = pd.read_csv(find_table(search, "gate_input_fulln.csv"))
    tang = json.loads(find_table(search, "comparator_tangram.json").read_text())
    cond = json.loads(find_table(search, "conditional_rmse_fulln.json").read_text())
    blue, orange, teal, red = "#0072B2", "#E69F00", "#009E73", "#D55E00"
    fig, ax = plt.subplots(2, 2, figsize=(8.6, 6.2), constrained_layout=True)
    a = ax[0, 0]
    x = np.arange(len(rule))
    a.scatter(x, rule.designated_cosine, color=teal, s=34, label="designated pair")
    a.scatter(x, rule.max_cosine, color=orange, s=34, label="all eligible maximum")
    a.axhline(0.8, color=red, ls="--", lw=1)
    a.set_xticks(x, rule.library, rotation=45, ha="right")
    a.set_ylabel("malignant-neighbor cosine")
    a.set_title("Eight-library rule sensitivity")
    a.text(-0.12, 1.06, "A", transform=a.transAxes, fontsize=13, fontweight="bold", va="top")
    a.legend(frameon=False, fontsize=7.5)
    a = ax[0, 1]
    metrics = ["overall_RMSE", "tumor_RMSE", "PCC_type", "PCC_spot", "JSD"]
    labels = ["overall RMSE", "tumor RMSE", "type PCC", "spot PCC", "JSD"]
    sp = [tang["SPGD_build_v4"][m] for m in metrics]
    ta = [tang["Tangram_clusters"][m] for m in metrics]
    xx = np.arange(len(metrics))
    w = 0.36
    a.bar(xx - w / 2, sp, w, color=blue, label="SPGD")
    a.bar(xx + w / 2, ta, w, color=orange, label="Tangram")
    a.set_xticks(xx, labels, rotation=35, ha="right")
    a.set_ylabel("matched 800-spot metric")
    a.set_title("Independent comparator")
    a.text(-0.12, 1.06, "B", transform=a.transAxes, fontsize=13, fontweight="bold", va="top")
    a.legend(frameon=False, fontsize=8)
    a = ax[1, 0]
    libs = gate.library.tolist()
    xx = np.arange(len(libs))
    a.scatter(xx, gate.cosine_P, color=blue, s=34, label="pre-gate P")
    a.scatter(xx, gate.cosine_S, color=orange, s=34, label="fit signature S")
    a.axhline(0.8, color=red, ls="--", lw=1)
    a.set_xticks(xx, libs, rotation=35, ha="right")
    a.set_ylabel("malignant-neighbor cosine")
    a.set_title("Full-n gate input check")
    a.text(-0.12, 1.06, "C", transform=a.transAxes, fontsize=13, fontweight="bold", va="top")
    a.legend(frameon=False, fontsize=8)
    a = ax[1, 1]
    full = cond["full_composition_rmse"]
    excluded = cond["conditional_rmse_excluding_zero_rows"]
    scored = cond["conditional_rmse_scored_with_zero_rows"]
    n_ex = cond["n_spots_full"] - cond["n_zero_nonmalignant_truth_excluded"]
    a.bar(
        ["11-type full\nsimplex", f"10-type conditional\n(n={n_ex})"],
        [full, excluded],
        color=[teal, orange],
    )
    a.set_ylabel("RMSE")
    a.set_title("BCC downstream (distinct estimands)")
    a.text(-0.12, 1.06, "D", transform=a.transAxes, fontsize=13, fontweight="bold", va="top")
    a.set_ylim(0, max(full, excluded, scored) * 1.45)
    a.text(0, full + 0.008, f"{full:.3f}", ha="center")
    a.text(1, excluded + 0.008, f"{excluded:.3f}", ha="center")
    a.text(
        0.5,
        max(full, excluded, scored) * 1.22,
        f"superseded zero-mass score {scored:.3f} (n={cond['n_spots_full']})",
        ha="center",
        fontsize=7.5,
    )
    fig.savefig(out / "F15_v3_fulln_comparator.pdf", facecolor="white")
    fig.savefig(out / "F15_v3_fulln_comparator.png", facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    main()
