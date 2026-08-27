"""Tie numbers printed in the manuscript back to the tracked plot data.

The raw CosMx export is KEEP-LOCAL, so the cohort totals cannot be recounted
from inside the repo. Everything downstream of the eight-type restriction can
be, and this module pins those so a reworded paragraph cannot silently drift
away from data/plotdata/.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLOTDATA = ROOT / "data/plotdata"
MANUSCRIPT = ROOT / "manuscript"

BODY = (
    "abstract.tex",
    "intro.tex",
    "materials.tex",
    "methods.tex",
    "results.tex",
    "discussion.tex",
)


def _body_text() -> str:
    text = "\n".join((MANUSCRIPT / name).read_text() for name in BODY)
    for cap in sorted((MANUSCRIPT / "captions").glob("*.tex")):
        text += "\n" + cap.read_text()
    return text.replace("{,}", "")


def _rows(name: str) -> list[dict[str, str]]:
    with (PLOTDATA / name).open() as handle:
        return list(csv.DictReader(handle))


def test_typed_cell_counts_sum_from_condition_summary():
    rows = _rows("F2_condition_cell_summary.csv")
    per_patient = defaultdict(int)
    for row in rows:
        per_patient[row["patient"]] += int(row["n_cells"])

    assert sum(per_patient.values()) == 216949
    assert per_patient == {
        "PatientA": 20730,
        "PatientB": 41728,
        "PatientC": 90487,
        "PatientD": 64004,
    }

    body = _body_text()
    for count in (216949, 20730, 41728, 90487, 64004):
        assert str(count) in body, count


def test_typed_cell_fractions_match_condition_summary():
    rows = {(r["patient"], r["condition"]): r for r in _rows("F2_condition_cell_summary.csv")}
    body = _body_text()
    checks = [
        (("PatientA", "Ulcerated_nodular"), "cancer_fraction"),
        (("PatientB", "Ulcerated_nodular"), "cancer_fraction"),
        (("PatientD", "Baseline"), "cancer_fraction"),
        (("PatientD", "Wound"), "cancer_fraction"),
        (("PatientD", "Baseline"), "fibroblast_fraction"),
        (("PatientD", "Wound"), "fibroblast_fraction"),
        (("PatientD", "Baseline"), "momacdc_fraction"),
        (("PatientD", "Wound"), "momacdc_fraction"),
    ]
    for key, column in checks:
        printed = f"{float(rows[key][column]):.4f}"
        assert printed in body, (key, column, printed)


def test_donor_table_carries_every_computed_edge_metric():
    """Per-edge values live in Table 3; the prose only quotes ranges."""
    table = (MANUSCRIPT / "tables/T3_donor_matrix.tex").read_text()
    rows = {r["pair"]: r for r in _rows("F5_donor_transfer.csv")}
    for pair in ("A_from_B", "B_from_A", "D_from_C"):
        row = rows[pair]
        for column in ("RMSE", "PCC_type", "PCC_spot", "tumor_rmse", "pseudobulk_jsd"):
            assert f"{float(row[column]):.4f}" in table, (pair, column)


def test_donor_prose_quotes_the_real_ranges():
    rows = _rows("F5_donor_transfer.csv")
    body = _body_text()
    spans = {
        "RMSE": [r["RMSE"] for r in rows],
        "PCC_type": [r["PCC_type"] for r in rows],
        "PCC_spot": [r["PCC_spot"] for r in rows],
        "tumor_rmse": [r["tumor_rmse"] for r in rows if r["tumor_rmse"]],
        "pseudobulk_jsd": [r["pseudobulk_jsd"] for r in rows if r["pseudobulk_jsd"]],
    }
    for column, values in spans.items():
        nums = [float(v) for v in values]
        for edge in (min(nums), max(nums)):
            assert f"{edge:.4f}" in body, (column, edge)


def test_gate_cosines_match_keep_table():
    rows = _rows("F12_keep_cosine.csv")
    body = _body_text()
    assert len(rows) == 8
    keeps = [r for r in rows if r["decision"] == "KEEP"]
    abstains = [r for r in rows if r["decision"] == "ABSTAIN"]
    assert len(keeps) == 4 and len(abstains) == 4
    # The point of the cutoff is that it is not a platform split: CosMx has to
    # sit on both sides of it.
    assert {r["substrate"].startswith("CosMx") for r in keeps} == {True}
    assert any(r["substrate"].startswith("CosMx") for r in abstains)
    for row in rows:
        assert f"{float(row['cosine']):.6f}" in body, row["substrate"]
        assert float(row["c_star"]) == 0.80


def test_reported_pass_time_is_the_sum_of_the_timed_steps():
    total = sum(float(r["seconds"]) for r in _rows("T2_timing.csv"))
    assert f"{total:.3f}" == "60.252"
    assert "60.252" in _body_text()


def test_full_n_pass_times_match_the_timing_probe():
    rows = {r["job"]: r for r in _rows("timing_probe_three_substrates.csv")}
    body = _body_text()
    for job in ("openst_t0_fulln", "realgt_t0_fulln", "realgt3_t0_fulln"):
        row = rows[job]
        assert f"{float(row['seconds']):.3f}" in body, job
        assert str(int(row["n_spots"])) in body, job
    # Hour projections in that file are planning arithmetic, not measurements.
    assert "2.15" not in body and "1.608" not in body


def test_occupancy_sparsity_claims_match_the_type_floor():
    rows = {(r["pair"], r["type"]): r for r in _rows("F9_type_floor.csv")}
    body = _body_text()
    for pair in ("B_from_A", "D_from_C"):
        nonzero = (1.0 - float(rows[(pair, "Cancer.cells")]["zero_rate"])) * 100
        absent = float(rows[(pair, "Pericyte")]["zero_rate"]) * 100
        assert f"{nonzero:.1f}" in body, (pair, "cancer nonzero")
        assert f"{absent:.1f}" in body, (pair, "pericyte absent")
    assert {int(r["floor_min_type_cells"]) for r in rows.values()} == {50}
