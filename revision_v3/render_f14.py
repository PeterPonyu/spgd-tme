"""Draw Figure 14 from the truth-stratified error tables.

Works from the lab tree (revision_v3/) and from the Supplementary bundle
(render/), without machine-local paths. Only the full-n CosMx BCC row uses
tissue coordinates; the 400-spot rows block by index.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.font_manager import fontManager

HERE = Path(__file__).resolve().parent


def layout() -> tuple[Path, Path]:
    if HERE.name == "render":
        return HERE.parent / "analyses", HERE.parent / "figures"
    return HERE / "analyses", HERE.parents[1] / "manuscript" / "figs" / "rendered"


def find_table(analyses: Path, name: str) -> Path:
    hits = sorted(analyses.rglob(name))
    if not hits:
        raise FileNotFoundError(f"{name} not under {analyses}")
    return hits[0]


def set_font() -> None:
    names = {font.name for font in fontManager.ttflist}
    plt.rcParams.update(
        {
            "font.family": "Tinos" if "Tinos" in names else "DejaVu Serif",
            "font.size": 10,
            "axes.titlesize": 11,
            "axes.labelsize": 10,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "savefig.dpi": 300,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def main() -> None:
    analyses, out = layout()
    out.mkdir(parents=True, exist_ok=True)
    set_font()
    summary = pd.read_csv(find_table(analyses, "summary_metrics.csv"))
    strata = pd.read_csv(find_table(analyses, "stratified_metrics.csv"))
    order = ["cosmx_bcc", "openst", "realgt", "realgt3"]
    present = set(summary.substrate)
    if "xenium" in present:
        order = ["cosmx_bcc", "openst", "xenium", "cosmx" if "cosmx" in present else "realgt3"]
        if "cosmx" not in present and "xenium_flex" in present:
            order[3] = "xenium_flex"
    labels = {
        "cosmx_bcc": "CosMx BCC\n(full n)",
        "openst": "openST",
        "realgt": "Xenium",
        "realgt3": "CosMx BCC\n(400 spots)",
        "xenium": "Xenium",
        "cosmx": "CosMx BCC\n(400 spots)",
        "xenium_flex": "CosMx BCC\n(400 spots)",
    }
    blue, orange, teal, red = "#0072B2", "#E69F00", "#009E73", "#D55E00"
    fig, ax = plt.subplots(2, 2, figsize=(8.6, 6.2), constrained_layout=True)
    a = ax[0, 0]
    x = np.arange(len(order))
    s = summary.set_index("substrate").loc[order]
    lo = s.bootstrap_rmse_lo.to_numpy()
    hi = s.bootstrap_rmse_hi.to_numpy()
    y = s.rmse.to_numpy()
    a.errorbar(x, y, yerr=[y - lo, hi - y], fmt="o", color=blue, capsize=4, lw=1.2)
    a.set_xticks(x, [labels[k] for k in order])
    a.set_ylabel("malignant RMSE")
    a.set_title("Block-bootstrap error")
    a.text(-0.12, 1.02, "A", transform=a.transAxes, fontsize=13, fontweight="bold", va="bottom")
    a.set_ylim(0, max(hi) * 1.18)
    b = ax[0, 1]
    q = strata.pivot(index="substrate", columns="stratum", values="bias").loc[order]
    vmax = max(abs(q.to_numpy().ravel()))
    im = b.imshow(q.to_numpy(), cmap="RdBu_r", vmin=-vmax, vmax=vmax)
    b.set_xticks(range(4), ["Q1", "Q2", "Q3", "Q4"])
    b.set_yticks(range(4), [labels[k] for k in order])
    b.set_title("Bias by truth stratum")
    b.set_xlabel("truth quartile")
    b.text(-0.12, 1.02, "B", transform=b.transAxes, fontsize=13, fontweight="bold", va="bottom")
    for i in range(4):
        for j in range(4):
            b.text(j, i, f"{q.iloc[i, j]:+.3f}", ha="center", va="center", fontsize=8)
    fig.colorbar(im, ax=b, fraction=0.046, pad=0.04, label="estimate minus truth")
    c = ax[1, 0]
    palette = [blue, orange, teal, red]
    for i, k in enumerate(order):
        d = strata[strata.substrate.eq(k)].sort_values("stratum")
        c.plot(d.truth_mean, d.estimate_mean, marker="o", lw=1.3, color=palette[i],
               label=labels[k].replace("\n", " "))
    c.plot([0, 1], [0, 1], ls="--", color="#777777", lw=0.9)
    c.set_xlim(0, 1)
    c.set_ylim(0, 1)
    c.set_xlabel("truth mean")
    c.set_ylabel("estimate mean")
    c.set_title("Stratum means (binned by truth)")
    c.legend(frameon=False, fontsize=7.5)
    c.text(-0.12, 1.02, "C", transform=c.transAxes, fontsize=13, fontweight="bold", va="bottom")
    dax = ax[1, 1]
    for i, k in enumerate(order):
        z = strata[strata.substrate.eq(k)].sort_values("stratum")
        dax.plot(range(4), z.mae, marker="o", lw=1.3, color=palette[i],
                 label=labels[k].replace("\n", " "))
    dax.set_xticks(range(4), ["Q1", "Q2", "Q3", "Q4"])
    dax.set_xlabel("truth quartile")
    dax.set_ylabel("MAE")
    dax.set_title("Error concentration")
    dax.text(-0.12, 1.02, "D", transform=dax.transAxes, fontsize=13, fontweight="bold", va="bottom")
    fig.savefig(out / "F14_revision_support.pdf", facecolor="white")
    fig.savefig(out / "F14_v3_calibration.pdf", facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    main()
