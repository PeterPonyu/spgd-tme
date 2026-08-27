#!/usr/bin/env python3
"""Generate deterministic TeX table bodies from locked plotdata CSVs."""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLOTDATA = ROOT / "data" / "plotdata"
OUT = ROOT / "manuscript" / "tables"
ESCAPES = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}"}

def esc(value: object) -> str:
    return "".join(ESCAPES.get(c, c) for c in str(value))

def rows(name: str) -> list[dict[str, str]]:
    with (PLOTDATA / name).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def num(value: str, digits: int = 4) -> str:
    return "--" if value == "" else f"{float(value):.{digits}f}"

def table(headers: list[str], data: list[list[str]], alignment: str) -> str:
    out = [f"\\begin{{tabular}}{{{alignment}}}", r"\toprule", " & ".join(headers) + r" \\", r"\midrule"]
    out.extend(" & ".join(row) + r" \\" for row in data)
    out.extend([r"\bottomrule", r"\end{tabular}", ""])
    return "\n".join(out)

def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    materials_raw = rows("T1_materials.csv")
    item_label = {
        "cells.txt": "CosMx cells",
        "features.txt": "CosMx features",
        "metadata.csv": "CosMx metadata",
        "counts_genes_x_cells.mtx.gz": "CosMx counts matrix",
        "openst_ref": "HNSCC openST reference",
        "realgt_ref": "Breast Xenium reference",
        "realgt2_ref": "Xenium FLEX orthogonal reference",
        "realgt3_ref": "CosMx BCC reference",
        "realgt4_ref": "CosMx donor-lock (provenance)",
        "crossdonor.csv": "Donor-transfer ledger",
        "type_pairs.json": "Malignant--neighbor pairs",
        "c_star.json": "Cosine threshold",
    }
    role_label = {
        "bcc_export": "CosMx export",
        "benchmark_ref": "evaluated",
        "orthogonal_ref": "orthogonal",
        "cbc_lock": "ledger",
        "type_pairs": "type pairs",
        "c_star": "threshold",
    }
    materials = [
        [
            esc(item_label.get(r["item"], r["item"])),
            esc("provenance" if r["item"] == "realgt4_ref" else role_label.get(r["role"], r["role"])),
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
        "refuse": "Collinearity refusal",
        "poisson_fit": "Poisson close",
    }
    timing = [
        [esc(timing_label.get(r["step"], r["step"])), num(r["seconds"], 3)]
        for r in rows("T2_timing.csv")
    ]
    (OUT / "T2_timing.tex").write_text(table(["Operator step", "Seconds"], timing, "lr"), encoding="utf-8")
    source_label = {
        "locked": "ledger",
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
