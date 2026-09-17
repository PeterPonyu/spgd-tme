"""Tie numbers printed in the manuscript back to the tracked plot data.

The raw CosMx export is KEEP-LOCAL, so the cohort totals cannot be recounted
from inside the repo. Everything downstream of the eight-type restriction can
be, and this module pins those so a reworded paragraph cannot silently drift
away from data/plotdata/.
"""

from __future__ import annotations

import csv
import json
import math
import statistics
from collections import Counter, defaultdict
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
        assert f"{float(row['cosine']):.4f}" in body, row["substrate"]
        assert float(row["c_star"]) == 0.80


def test_the_timed_steps_decompose_the_build_rather_than_overlapping_it():
    """The stages must sum to the build they decompose, not to each other.

    The superseded profile timed a whole build under the name of one of its own
    stages, so its rows overlapped and summed to a duration no pass had.  Summing
    the step rows against the separately measured ``build_total`` is what catches
    that, and the earlier version of this test summed ``build_total`` in with the
    steps, which would have passed on the broken table.
    """
    rows = {r["step"]: float(r["seconds"]) for r in _rows("T2_timing.csv")}
    total = rows.pop("build_total")
    assert math.isclose(sum(rows.values()), total, abs_tol=0.01)
    assert f"{total:.3f}" in _body_text()


def test_v3_repeated_timing_is_reported():
    """Every timing figure in the prose comes off the tracked measurement."""
    body = _body_text()
    summary = {r["metric"]: r["value"] for r in _rows("T2_repeated_timing.csv")}
    steps = {r["step"]: r for r in _rows("T2_timing.csv")}

    mean, sd = float(summary["mean_s"]), float(summary["sd_s"])
    assert f"{mean:.3f}" in body
    assert f"{sd:.3f}" in body
    assert f"{float(summary['cv_pct']):.2f}" in body
    assert "five warm" in body

    gate = steps["reportability_gate"]
    self_gate = steps["platform_self_gate"]
    assert f"{float(self_gate['seconds']):.3f}" in body
    assert f"{float(self_gate['seconds_sd']):.3f}" in body
    # The gate rounds to a millisecond; the share is what the prose claims for it.
    assert f"{float(gate['seconds']):.3f}" in body
    assert 100 * float(gate["seconds"]) / mean < 0.01
    caption = (MANUSCRIPT / "captions/F10_eval.tex").read_text()
    assert "47.96" not in caption
    assert f"{float(self_gate['seconds']):.2f}" in caption


def test_occupancy_sparsity_claims_match_the_type_floor():
    rows = {(r["pair"], r["type"]): r for r in _rows("F9_type_floor.csv")}
    body = _body_text()
    for pair in ("B_from_A", "D_from_C"):
        nonzero = (1.0 - float(rows[(pair, "Cancer.cells")]["zero_rate"])) * 100
        absent = float(rows[(pair, "Pericyte")]["zero_rate"]) * 100
        assert f"{nonzero:.1f}" in body, (pair, "cancer nonzero")
        assert f"{absent:.1f}" in body, (pair, "pericyte absent")
    assert {int(r["floor_min_type_cells"]) for r in rows.values()} == {50}


def test_keep_map_agreement_matches_the_paired_column():
    """The reported column is 5686 paired values; the figure scores them."""
    rows = _rows("F4_keep_spatial_fulln_compare.csv")
    truth = [float(r["tumor_truth"]) for r in rows]
    hat = [float(r["tumor_hat"]) for r in rows]
    n = len(rows)
    assert n == 5686

    rmse = math.sqrt(sum((a - b) ** 2 for a, b in zip(hat, truth)) / n)
    mh, mt = sum(hat) / n, sum(truth) / n
    cov = sum((a - mh) * (b - mt) for a, b in zip(hat, truth))
    pcc = cov / math.sqrt(
        sum((a - mh) ** 2 for a in hat) * sum((b - mt) ** 2 for b in truth)
    )

    body = _body_text()
    assert f"{rmse:.4f}" in body
    assert f"{pcc:.4f}" in body
    saturated = 100 * sum(1 for v in truth if v >= 0.999) / n
    topped = 100 * sum(1 for v in hat if v >= 0.99) / n
    assert f"{saturated:.1f}" in body
    assert f"{topped:.1f}" in body


def test_wound_axis_per_spot_split_matches_the_recovered_labels():
    rows = _rows("F9_D_from_C_spot_condition.csv")
    body = _body_text()
    counts = Counter(r["condition"] for r in rows)
    assert counts == {"Baseline": 977, "Unwound": 812, "Wound": 1472}

    order = ("Baseline", "Unwound", "Wound")
    tumor = [
        statistics.median(
            float(r["Cancer.cells"]) for r in rows if r["condition"] == cond
        )
        for cond in order
    ]
    assert tumor == sorted(tumor, reverse=True)
    for value in tumor:
        assert f"{value:.4f}" in body

    for column, ends in (("Cancer.cells", "absent"), ("MoMacDC", "present")):
        shares = []
        for cond in ("Baseline", "Wound"):
            vals = [float(r[column]) for r in rows if r["condition"] == cond]
            hit = sum(1 for v in vals if (v == 0 if ends == "absent" else v > 0))
            shares.append(100 * hit / len(vals))
        for share in shares:
            assert f"{share:.1f}" in body, (column, share)


def test_occupancy_span_and_reference_floor_match_the_tables():
    occupied = [
        (100 * (1 - float(r["zero_rate"])), r["pair"], r["type"])
        for r in _rows("F2_truth_mass.csv")
    ]
    body = _body_text()
    for value, _, _ in (min(occupied), max(occupied)):
        assert f"{value:.1f}" in body

    per_donor = defaultdict(int)
    for row in _rows("F9_condition_occupancy.csv"):
        per_donor[(row["patient"], row["type"])] += int(row["n_cells"])
    assert len(per_donor) == 32
    assert min(per_donor.values()) == 137
    assert all(v >= 50 for v in per_donor.values())
    assert "32 donor" in body and "137 Pericyte" in body


def test_neighbor_scan_counts_match_the_recorded_probes():
    rows = _rows("F12_neighbor_scan.csv")
    body = _body_text()
    per_library = defaultdict(lambda: [0, 0])
    for row in rows:
        seen = per_library[row["library"]]
        seen[1] += 1
        seen[0] += row["decision"] == "ABSTAIN"
    assert dict(per_library) == {
        "CosMx CRC": [0, 8],
        "CosMx NSCLC": [2, 17],
        "CosMx HCC": [8, 15],
        "CosMx PDAC": [6, 6],
    }
    # PDAC is the ABSTAIN face of the cutoff, and it is the only library whose
    # malignant program is collinear with every neighbor it was scored against.
    saturated = [lib for lib, (bad, total) in per_library.items() if bad == total]
    assert saturated == ["CosMx PDAC"]
    for library, (bad, total) in per_library.items():
        assert f"\\({bad}\\) of \\({total}\\)" in body, library


def test_cutoff_margins_match_the_native_board():
    rows = _rows("F2_native_refuse.csv") + _rows("F2_realgt2_cosine.csv")
    body = _body_text()
    margins = {r["substrate"]: float(r["c_star"]) - float(r["cosine"]) for r in rows}
    keep = [m for m in margins.values() if m > 0]
    refused = sorted(-m for m in margins.values() if m < 0)
    assert len(keep) == 1
    assert f"{keep[0]:.4f}" in body
    assert f"{refused[0]:.4f}" in body and f"{refused[-1]:.4f}" in body


def test_the_rendered_evaluation_board_agrees_with_the_timing_table():
    """The figure's own labels must match the measurement, not just the caption.

    A caption guard already forbids the superseded 47.96 s in F10's caption, but
    the seconds a reader actually sees are drawn inside the figure. A pack once
    shipped with the caption corrected and Figure 10 still rendering the
    withdrawn overlapping profile, because every check looked at text and none
    looked at the plot. This reads the rendered vector's own labels.
    """
    import shutil
    import subprocess

    figure = MANUSCRIPT / "figs/rendered/F10_eval.pdf"
    if shutil.which("pdftotext") is None or not figure.is_file():
        return
    drawn = subprocess.run(["pdftotext", str(figure), "-"],
                           capture_output=True, text=True, check=True).stdout
    seconds = {r["step"]: float(r["seconds"]) for r in _rows("T2_timing.csv")}
    for step in ("signature_setup", "platform_self_gate", "platform_factor_fit", "poisson_close"):
        assert f"{seconds[step]:.2f} s" in drawn, (step, f"{seconds[step]:.2f} s")
    # The profile the revision withdrew, in the artefact a reader looks at.
    for stale in ("47.96", "60.25", "22.56", "Signature extraction", "Weighted fit"):
        assert stale not in drawn, stale


def test_recovery_claims_do_not_rest_on_a_truth_table():
    """A sentence about the estimate must not be evidenced by the truth.

    F9_D_from_C_spot_condition.csv is byte-identical to the truth maps on the
    malignant column, yet the Abstract printed its numbers under "the operators
    recover". Every check in this file compared a printed number to some table
    and none asked what the table was, so the claim stayed green for three
    rounds. This pins the distinction: the condition table is truth, and the
    prose that claims recovery must be able to reach an estimate.
    """
    truth_rows = {r["spot"]: r for r in _rows("F9_D_from_C_spot_condition.csv")}
    maps = {r[""]: r for r in _rows("F9_D_from_C_truth_maps.csv")}
    shared = set(truth_rows) & set(maps)
    assert shared, "the two D-from-C tables no longer share spots"
    same = all(
        math.isclose(float(truth_rows[s]["Cancer.cells"]),
                     float(maps[s]["Cancer.cells"]), abs_tol=1e-12)
        for s in shared
    )
    assert same, "F9_D_from_C_spot_condition is no longer the truth column"

    body = _body_text()
    if "per-spot estimate" not in body:
        return
    # The claim is made, so the estimate must exist as its own table.
    estimate = PLOTDATA.parent.parent / "revision_v3/out/wound_axis_prediction.csv"
    assert estimate.is_file(), (
        "the text claims the gradient is visible in the per-spot estimate, but no "
        "estimate table exists; run revision_v3/wound_axis_prediction.py"
    )


def test_conditional_rmse_in_results_is_the_excluded_estimand():
    """0.214 scored undefined rows; 0.188 is the paper's own exclusion rule."""
    record = json.loads(
        (ROOT / "revision_v3/out/conditional_rmse_fulln.json").read_text()
    )
    assert record["n_zero_nonmalignant_truth_excluded"] == 1553
    assert record["n_spots_full"] == 5686
    assert abs(record["conditional_rmse_excluding_zero_rows"] - 0.187631) < 1e-6
    body = _body_text()
    assert "4{,}133" in body or "4133" in body
    assert "1{,}553" in body or "1553" in body
    assert "0.188" in body
    assert "27.3" in body
    # The superseded number may still be named as superseded; it must not
    # justify keeping the designated pair.
    results = (MANUSCRIPT / "results.tex").read_text()
    assert "cannot rank the designated pair against the maximum" in results
    assert "demonstrates why the designated pair is retained" not in results


def test_abstract_does_not_claim_fibroblast_rises_in_the_estimate():
    """Locked truth rises; the estimate is not monotone and recovers ~56%."""
    abstract = (MANUSCRIPT / "abstract.tex").read_text()
    assert "fibroblast and MoMacDC rise" not in abstract
    assert "estimate recovers only part of that shift and is not monotone" in abstract
    gradients = json.loads(
        (ROOT / "revision_v3/out/wound_axis_prediction.json").read_text()
    )["gradients"]
    assert gradients["Fibroblast"]["estimate_monotone"] is False
    assert gradients["MoMacDC"]["estimate_monotone"] is True
    assert gradients["Cancer.cells"]["estimate_monotone"] is True


def test_lock_spec_does_not_use_withdrawn_neighbor_defences():
    spec = (ROOT / "revision_v3/NEIGHBOR_RULE_LOCK_SPEC.md").read_text()
    assert "share epidermal lineage" not in spec
    assert "biologically implausible" not in spec
    assert "false positive of the maximum" not in spec
    assert "neural-crest" in spec
    assert "type name is not that evidence" in spec
    assert "not a justification for retaining the designated pair" in spec
