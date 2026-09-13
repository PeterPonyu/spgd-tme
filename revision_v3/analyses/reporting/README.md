# V3 reporting analyses

This directory contains panel-ready, zero-fit analyses for the revision.

* `neighbor_max_rule_all_rows.csv` applies a deterministic retrospective maximum over every represented, eligible non-malignant column. Historical designated-pair results are retained alongside it.
* `neighbor_denominator_reconciliation.csv` records all eligible/excluded rows, including the PDAC six-versus-five denominator reconciliation.
* `abstain_truth_corrected_summary.csv` excludes undefined conditional truth rows (zero retained non-malignant truth mass), reports the exclusion count, and contrasts raw, conditional, and merged malignant-plus-neighbor mass errors.
* `abstain_truth_malignant_strata.csv` gives malignant-truth-stratified bias; `abstain_truth_merged_mass.csv` is the spot-level panel source.
* `bcc_directed_donor_inventory.csv` records every reachable BCC directed donor edge and its saved metrics/truth-map denominator.

The max-neighbour rule is a retrospective sensitivity analysis, not a pre-registered operating rule. No manuscript files are modified by this runner.
