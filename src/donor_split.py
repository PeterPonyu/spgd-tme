from __future__ import annotations

import numpy as np


def assert_disjoint_patient_ids(
    patient: np.ndarray, spot_mask: np.ndarray, ref_mask: np.ndarray
) -> None:
    spot_ids = set(map(str, np.unique(patient[spot_mask])))
    ref_ids = set(map(str, np.unique(patient[ref_mask])))
    overlap = spot_ids & ref_ids
    if overlap:
        raise AssertionError(f"Patient_ID overlap between spot and ref: {sorted(overlap)}")


def forbid_slide_key_as_donor(donor_key: str) -> None:
    if donor_key == "Run_Tissue_name":
        raise ValueError("donor key must be Patient_ID, not Run_Tissue_name")
