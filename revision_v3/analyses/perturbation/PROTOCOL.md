# Retrospective reference-gene perturbation protocol (V3)

## Question
Does the fixed cosine reportability decision and downstream malignant-coordinate accuracy remain stable when the same reference representation is reduced to 75% or 50% of the original shared genes?

## Locked design (written before execution)
- Substrates: `openst`, `realgt`, and `realgt3` benchmark folders in the existing deconv-lab data tree.
- Spots: first 400 rows after lexicographic ordering of the benchmark spot identifiers; no outcome-based selection.
- Reference: the existing full reference subset, with the original annotation labels preserved.
- Gene retention: 100% once (seed 0), 75% with seeds 101, 102, 103, and 50% with seeds 101, 102, 103, independently within each substrate. The retained genes are sampled without replacement from the shared gene intersection and applied identically to spot and reference matrices.
- Fits: 7 per substrate, 21 fresh `build_v4` fits total. The 100% fit is the unperturbed representation; partial levels are independent random gene-retention replicates.
- Threshold: `c*=0.80`, unchanged and never selected from these results.
- Gate input: pre-gate mean profile `P`, matching the locked reportability definition. Historical pair is taken from the locked type-pair table. The complete eligible-neighbor maximum is reported descriptively over all non-malignant reference types with nonzero variance and finite cosine.
- Metrics: historical-pair cosine, all-eligible maximum cosine, KEEP/ABSTAIN states for each, malignant-coordinate RMSE against the saved 400-spot truth, overall RMSE, spot PCC, platform gate, fit runtime, and exact retained-gene count.
- No fit is used to choose a threshold, neighbor pair, or seed.
- Output scope: only this analysis directory and temporary files below it. Historical V0/V1/V2 trees and locks remain untouched.

## Interpretation rule
Stability means all three random partial-gene replicates preserve the historical-pair decision and malignant RMSE remains within the full-gene RMSE plus 0.02. Any disagreement is reported as evidence of representation sensitivity rather than hidden or averaged away.
