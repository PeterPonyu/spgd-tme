#!/usr/bin/env python
"""Label each D-from-C mixed spot with the wound condition of the field it sits in.

The donor builder pooled Patient D cells into spots and recorded the majority
Condition per spot, but only the per-condition counts survived into the plot
tables. Patient D fields of view are single-condition, so the label is
recoverable from the tracked cell table using the same 80 px field pad the
spatial renderer uses. The recovered counts must reproduce the recorded
Baseline/Unwound/Wound split exactly or this script refuses to write.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PLOTDATA = ROOT / "data" / "plotdata"

# Same pad as assign_fov() in manuscript/scripts/R/spatial_geom.R.
FOV_PAD_PX = 80
RECORDED = {"Baseline": 977, "Unwound": 812, "Wound": 1472}


def field_boxes(cells: pd.DataFrame) -> pd.DataFrame:
    per_fov = cells.groupby("fov").agg(
        xmin=("x", "min"),
        xmax=("x", "max"),
        ymin=("y", "min"),
        ymax=("y", "max"),
        condition=("condition", "unique"),
    )
    mixed = per_fov[per_fov["condition"].apply(len) > 1]
    if len(mixed):
        raise SystemExit(f"fields carry more than one condition: {list(mixed.index)}")
    per_fov["condition"] = per_fov["condition"].apply(lambda v: v[0])
    return per_fov.reset_index()


def label_spots(spots: pd.DataFrame, boxes: pd.DataFrame) -> pd.Series:
    out = pd.Series(pd.NA, index=spots.index, dtype="object")
    for row in boxes.itertuples():
        hit = (
            out.isna()
            & spots["x"].between(row.xmin - FOV_PAD_PX, row.xmax + FOV_PAD_PX)
            & spots["y"].between(row.ymin - FOV_PAD_PX, row.ymax + FOV_PAD_PX)
        )
        out[hit] = row.condition
    return out


def main() -> None:
    cells = pd.read_csv(PLOTDATA / "cells_spatial.csv.gz")
    spots = pd.read_csv(PLOTDATA / "F9_D_from_C_truth_maps.csv").rename(
        columns={"Unnamed: 0": "spot"}
    )
    boxes = field_boxes(cells[cells["patient"] == "PatientD"])
    spots["condition"] = label_spots(spots, boxes)

    unassigned = int(spots["condition"].isna().sum())
    if unassigned:
        raise SystemExit(f"{unassigned} spots fell outside every Patient D field")
    counts = spots["condition"].value_counts().to_dict()
    if counts != RECORDED:
        raise SystemExit(f"recovered {counts}, recorded {RECORDED}")

    out = spots[["spot", "condition", "Cancer.cells", "Fibroblast", "MoMacDC"]]
    dest = PLOTDATA / "F9_D_from_C_spot_condition.csv"
    out.to_csv(dest, index=False)
    print("wrote", dest.name, len(out), counts)


if __name__ == "__main__":
    main()
