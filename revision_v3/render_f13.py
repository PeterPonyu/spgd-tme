"""Draw Figure 13 from the revision audit tables.

Works from the lab tree (revision_v3/) and from the Supplementary bundle
(render/), without machine-local paths.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.font_manager import fontManager
from matplotlib.lines import Line2D

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
            "font.size": 8.5,
            "axes.titlesize": 9.5,
            "axes.labelsize": 8.5,
            "xtick.labelsize": 7.5,
            "ytick.labelsize": 7.5,
            "legend.fontsize": 8.5,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )


def panel_title(ax, label: str, title: str) -> None:
    ax.text(-0.12, 1.16, label, transform=ax.transAxes, ha="left", va="top", fontweight="bold", fontsize=14)
    ax.text(-0.01, 1.13, title, transform=ax.transAxes, ha="left", va="top", fontsize=11)


def clean(ax) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(width=0.55, length=3)
    ax.grid(False)


def main() -> None:
    analyses, out = layout()
    out.mkdir(parents=True, exist_ok=True)
    set_font()
    summ = pd.read_csv(find_table(analyses, "neighbor_max_rule_library_summary.csv"))
    denom = pd.read_csv(find_table(analyses, "neighbor_denominator_reconciliation.csv"))
    pert = pd.read_csv(find_table(analyses, "perturbation_summary.csv"))
    fig, ax = plt.subplots(2, 2, figsize=(8.6, 6.2), dpi=300)
    a, b, c, d = ax.flat
    order = ["CosMx CRC", "CosMx HCC", "CosMx NSCLC", "CosMx PDAC"]
    x = range(len(order))
    h = summ.set_index("library").loc[order]
    a.scatter(x, h["historical_cosine"], s=27, c="#4F9F7A", label="historical designated", zorder=3)
    a.scatter(x, h["selected_cosine_max_rule"], s=27, c="#D6A12A", label="all eligible maximum", zorder=3)
    a.axhline(0.8, color="#D17A00", ls="--", lw=0.8)
    a.set_ylim(0.47, 0.93)
    a.set_ylabel("malignant-neighbor cosine")
    a.set_xticks(list(x), order, rotation=18, ha="right")
    panel_title(a, "A", "Designated versus all-eligible rule")
    clean(a)
    a.legend(loc="lower center", bbox_to_anchor=(0.5, 1.24), ncol=2, frameon=False, handletextpad=0.4, columnspacing=0.8)
    bd = denom.set_index("library").loc[order]
    xx = list(range(len(order)))
    b.bar(xx, bd["eligible_rows"], color="#4F9F7A", label="eligible")
    b.bar(xx, bd["excluded_rows"], bottom=bd["eligible_rows"], color="#C06A24", label="excluded")
    b.set_ylabel("neighbor rows")
    b.set_xticks(xx, order, rotation=18, ha="right")
    b.set_ylim(0, 18)
    panel_title(b, "B", "Denominator reconciliation")
    clean(b)
    b.legend(
        handles=[
            Line2D([0], [0], marker="s", color="#B8C4CF", lw=0, markersize=6, label="stored rows"),
            Line2D([0], [0], marker="s", color="#C06A24", lw=0, markersize=6, label="excluded"),
            Line2D([0], [0], marker="s", color="#4F9F7A", lw=0, markersize=6, label="eligible"),
        ],
        loc="lower center",
        bbox_to_anchor=(0.5, 1.24),
        ncol=3,
        frameon=False,
        handletextpad=0.3,
        columnspacing=0.6,
    )
    colors = {"openst": "#0072B2", "realgt": "#E69F00", "realgt3": "#009E73",
              "xenium": "#E69F00", "cosmx": "#009E73"}
    pretty = {"openst": "openST", "realgt": "Xenium", "realgt3": "CosMx",
              "xenium": "Xenium", "cosmx": "CosMx"}
    seen = []
    for sub in ("openst", "realgt", "realgt3", "xenium", "cosmx"):
        q = pert[pert.substrate == sub].sort_values("fraction")
        if q.empty:
            continue
        c.errorbar(
            q.fraction * 100,
            q.historical_cosine_mean,
            yerr=q.historical_cosine_sd.fillna(0),
            marker="o",
            lw=1.4,
            ms=4,
            color=colors[sub],
            label=pretty[sub],
        )
        d.errorbar(
            q.fraction * 100,
            q.malignant_rmse_mean,
            yerr=q.malignant_rmse_sd.fillna(0),
            marker="o",
            lw=1.4,
            ms=4,
            color=colors[sub],
        )
        seen.append(sub)
    c.axhline(0.8, color="#D17A00", ls="--", lw=0.8)
    c.set_ylim(0.45, 1.0)
    c.set_xlabel("reference genes retained (%)")
    c.set_ylabel("cosine")
    c.set_xticks([50, 75, 100])
    panel_title(c, "C", "Reference perturbation preserves calls")
    clean(c)
    d.set_ylim(0.07, 0.19)
    d.set_xlabel("reference genes retained (%)")
    d.set_ylabel("malignant RMSE")
    d.set_xticks([50, 75, 100])
    panel_title(d, "D", "Accuracy cost under gene loss")
    clean(d)
    legend_keys = []
    for sub in seen:
        label = pretty[sub]
        if label not in {k[1] for k in legend_keys}:
            legend_keys.append((sub, label))
    fig.legend(
        handles=[Line2D([0], [0], marker="o", color=colors[s], lw=1.4, markersize=4, label=lab) for s, lab in legend_keys],
        loc="lower center",
        bbox_to_anchor=(0.5, 0.035),
        ncol=3,
        frameon=False,
        handletextpad=0.35,
        columnspacing=0.8,
    )
    fig.subplots_adjust(left=0.105, right=0.985, top=0.78, bottom=0.155, wspace=0.33, hspace=0.62)
    fig.savefig(out / "F13_revision_audit.pdf", pad_inches=0.03)
    fig.savefig(out / "F13_v3_rule_and_perturbation.pdf", bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)


if __name__ == "__main__":
    main()
