from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.donor_split import assert_disjoint_patient_ids, forbid_slide_key_as_donor


def test_overlap_raises():
    patient = np.array(["PatientA", "PatientA", "PatientB"])
    spot = np.array([True, False, False])
    ref = np.array([True, False, True])
    with pytest.raises(AssertionError, match="Patient_ID"):
        assert_disjoint_patient_ids(patient, spot, ref)


def test_disjoint_ok():
    patient = np.array(["PatientA", "PatientA", "PatientB"])
    spot = np.array([True, True, False])
    ref = np.array([False, False, True])
    assert_disjoint_patient_ids(patient, spot, ref)


def test_slide_key_forbidden():
    with pytest.raises(ValueError, match="Patient_ID"):
        forbid_slide_key_as_donor("Run_Tissue_name")
