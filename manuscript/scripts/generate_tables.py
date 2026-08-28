#!/usr/bin/env python3
"""Generate deterministic TeX table bodies from locked plotdata CSVs."""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLOTDATA = ROOT / "data" / "plotdata"
OUT = ROOT / "manuscript" / "tables"
ESCAPES = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}"}

# The public name of every locked input. The supplementary assembler renames by
# the same map, so a reader who reads "CosMx BCC reference" in Table 1 finds the
# same words in the bundle instead of the substrate codename this repo runs on.
ITEM_LABEL = {
    "cells.txt": "CosMx cells",
    "features.txt": "CosMx features",
    "metadata.csv": "CosMx metadata",
    "counts_genes_x_cells.mtx.gz": "CosMx counts matrix",
    "openst_ref": "HNSCC openST reference",
    "realgt_ref": "Breast Xenium reference",
    "realgt2_ref": "Xenium FLEX orthogonal reference",
    "realgt3_ref": "CosMx BCC reference",
    "realgt4_ref": "CosMx donor-lock (recorded)",
    "crossdonor.csv": "Donor-transfer row",
    "type_pairs.json": "Malignant--neighbor pairs",
    "c_star.json": "Cosine threshold",
}
ROLE_LABEL = {
    "bcc_export": "CosMx export",
    "benchmark_ref": "evaluated",
    "orthogonal_ref": "orthogonal",
    "cbc_lock": "recorded",
    "type_pairs": "type pairs",
    "c_star": "threshold",
}
# realgt4 carries the donor lock rather than an evaluated substrate, so its
# CSV role would otherwise read as a benchmark this paper scores against.
ROLE_OVERRIDE = {"realgt4_ref": "recorded"}
# Substrate codenames as they appear inside file names and table cells. Longest
# first: a bare "realgt" prefixes the numbered ones.
SUBSTRATE_LABEL = {"realgt3": "CosMx", "realgt2": "Xenium FLEX", "realgt": "Xenium", "openst": "openST"}

def esc(value: object) -> str:
    return "".join(ESCAPES.get(c, c) for c in str(value))

def rows(name: str) -> list[dict[str, str]]:
    with (PLOTDATA / name).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def num(value: str, digits: int = 4) -> str:
    return "--" if value == "" else f"{float(value):.{digits}f}"

def floor_num(value: float, digits: int) -> str:
    """A step that costs less than the printed resolution must not read as free."""
    return f"\\(<\\){10 ** -digits:.{digits}f}" if 0 < value < 10 ** -digits / 2 else f"{value:.{digits}f}"

def table(headers: list[str], data: list[list[str]], alignment: str, rules_before: tuple[int, ...] = ()) -> str:
    out = [f"\\begin{{tabular}}{{{alignment}}}", r"\toprule", " & ".join(headers) + r" \\", r"\midrule"]
    for index, row in enumerate(data):
        if index in rules_before:
            out.append(r"\midrule")
        out.append(" & ".join(row) + r" \\")
    out.extend([r"\bottomrule", r"\end{tabular}", ""])
    return "\n".join(out)

def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    materials_raw = rows("T1_materials.csv")
    materials = [
        [
            esc(ITEM_LABEL.get(r["item"], r["item"])),
            esc(ROLE_OVERRIDE.get(r["item"], ROLE_LABEL.get(r["role"], r["role"]))),
        ]
        for r in materials_raw
    ]
    (OUT / "T1_materials.tex").write_text(
        table(["Item", "Role"], materials, "ll"),
        encoding="utf-8",
    )
    timing_label = {
        "extract_signature": "Signature extraction",
        "specificity_weight": "Specificity weights",
        "fit_gamma": "Weighted fit",
        "self_gate": "Platform self-gate",
        "refuse": "Reportability gate",
        "poisson_fit": "Poisson close",
    }
    steps = rows("T2_timing.csv")
    pass_seconds = sum(float(r["seconds"]) for r in steps)
    # The claim the table supports is that refusability is cheap relative to the
    # fit it guards, which is a share of the pass and not an absolute duration.
    timing = [
        [
            esc(timing_label.get(r["step"], r["step"])),
            floor_num(float(r["seconds"]), 3),
            floor_num(100 * float(r["seconds"]) / pass_seconds, 2) + r"\%",
        ]
        for r in steps
    ]
    timing.append(["One openST pass", f"{pass_seconds:.3f}", r"100\%"])
    substrate_label = SUBSTRATE_LABEL
    probes = {r["job"]: r for r in rows("timing_probe_three_substrates.csv")}
    throughput = []
    for key in ("openst", "realgt3", "realgt"):
        probe = probes[f"{key}_t0_fulln"]
        spots, seconds = int(probe["n_spots"]), float(probe["seconds"])
        throughput.append(
            [substrate_label[key], str(spots), f"{seconds:.3f}", f"{1000 * seconds / spots:.1f}"]
        )
    (OUT / "T2_timing.tex").write_text(
        table(["Operator step", "Seconds", "Share of pass"], timing, "lrr", rules_before=(len(steps),))
        + "\n\\vspace{4pt}\n\n"
        + table(
            [r"Full-\(n\) \(t=0\) pass", "Spots", "Seconds", "ms per spot"],
            throughput,
            "lrrr",
        ),
        encoding="utf-8",
    )
    source_label = {
        "locked": "recorded",
        "computed": "this analysis",
    }
    donors = [
        [
            esc(r["pair"]),
            num(r["RMSE"]),
            num(r["PCC_type"]),
            num(r["PCC_spot"]),
            num(r["tumor_rmse"]),
            num(r["pseudobulk_jsd"]),
            esc(source_label.get(r["source"], r["source"])),
        ]
        for r in rows("T3_donor_matrix.csv")
    ]
    (OUT / "T3_donor_matrix.tex").write_text(table(["Pair", "RMSE", "Type PCC", "Spot PCC", "Tumor RMSE", "PB JSD", "Source"], donors, "lrrrrrl"), encoding="utf-8")
    print("wrote T1_materials.tex, T2_timing.tex, and T3_donor_matrix.tex")

if __name__ == "__main__":
    main()
