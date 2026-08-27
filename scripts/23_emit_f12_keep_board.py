#!/usr/bin/env python
"""Emit F12 KEEP-carcinoma board tables from locked warehouse numbers."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "plotdata"

COSINE_ROWS = [
    {"substrate": "CosMx BCC", "malignant": "Cancer.cells", "neighbor": "Normal.Kerat", "cosine": 0.603666, "c_star": 0.80, "decision": "KEEP"},
    {"substrate": "CosMx NSCLC", "malignant": "tumor", "neighbor": "fibroblast", "cosine": 0.648151, "c_star": 0.80, "decision": "KEEP"},
    {"substrate": "CosMx CRC", "malignant": "tumor", "neighbor": "fibroblast", "cosine": 0.505826, "c_star": 0.80, "decision": "KEEP"},
    {"substrate": "CosMx HCC", "malignant": "tumor", "neighbor": "Stellate.cells", "cosine": 0.648597, "c_star": 0.80, "decision": "KEEP"},
    {"substrate": "CosMx PDAC", "malignant": "tumor", "neighbor": "CAF", "cosine": 0.861599, "c_star": 0.80, "decision": "ABSTAIN"},
    {"substrate": "openST", "malignant": "Tumor", "neighbor": "Tumor_Keratin_Pearl", "cosine": 0.972678, "c_star": 0.80, "decision": "ABSTAIN"},
    {"substrate": "Xenium", "malignant": "Invasive_Tumor", "neighbor": "Prolif_Invasive_Tumor", "cosine": 0.980196, "c_star": 0.80, "decision": "ABSTAIN"},
    {"substrate": "Xenium FLEX", "malignant": "Invasive_Tumor", "neighbor": "Prolif_Invasive_Tumor", "cosine": 0.987505, "c_star": 0.80, "decision": "ABSTAIN"},
]

DONOR_ROWS = [
    {"edge": "BCC B from A", "overall_rmse": 0.0659, "spot_pcc": 0.9528, "n_spots": 2020},
    {"edge": "BCC D from C", "overall_rmse": 0.0906, "spot_pcc": 0.9037, "n_spots": 3261},
    {"edge": "BCC A from B", "overall_rmse": 0.1349, "spot_pcc": 0.8030, "n_spots": 1194},
    {"edge": "NSCLC P1 from P0", "overall_rmse": 0.1066, "spot_pcc": 0.8415, "n_spots": 4237},
]


def main() -> None:
    cosine = pd.DataFrame(COSINE_ROWS)
    donor = pd.DataFrame(DONOR_ROWS)
    OUT.mkdir(parents=True, exist_ok=True)
    cosine.to_csv(OUT / "F12_keep_cosine.csv", index=False)
    donor.to_csv(OUT / "F12_donor_rmse.csv", index=False)
    print("wrote F12_keep_cosine.csv", len(cosine))
    print("wrote F12_donor_rmse.csv", len(donor))


if __name__ == "__main__":
    main()
