# Malignant-neighbor selection rule — author-lock specification (V3)

Status: the eight published calls remain the designated-pair operating
estimand, because that is the pair each call was read from. This document
records the complete eligible scan and three prospective rules. It does not
change any historical call, and it does not retune the frozen cutoff
`c* = 0.80`.

What is locked for any further library is still a scientific choice. Three
executable options are written below. This file does not adopt one of them on
the basis of a type name, a headline result, or a comparison of incommensurable
RMSE values.

## 1. What the audit established

The complete eligible-neighbor scan (`out/complete_eligible_scan.csv`) was
rebuilt from raw data for all eight libraries. Every platform designated cosine
with a historical lock reproduces to six decimals
(`out/validation_anchor.csv`): openST 0.972678, Xenium 0.980196, CosMx BCC
0.603666.

Designated pair versus maximum-eligible neighbor at `c* = 0.80`
(`out/library_rule_comparison.csv`, floor = 0):

| Library | Designated pair → call | Max-eligible neighbor → call | Rule flips call? |
|---|---|---|---|
| CosMx CRC | fibroblast 0.5058 → KEEP | BEC 0.7913 → KEEP | No |
| CosMx NSCLC | fibroblast 0.6482 → KEEP | epithelial 0.8473 → ABSTAIN | **Yes** |
| CosMx HCC | Stellate.cells 0.6486 → KEEP | CD3+ αβ T cells 0.8541 → ABSTAIN | **Yes** |
| CosMx PDAC | CAF 0.8616 → ABSTAIN | Macrophage 0.9051 → ABSTAIN | No |
| openST | Tumor_Keratin_Pearl 0.9727 → ABSTAIN | (same) 0.9727 → ABSTAIN | No |
| Xenium | Prolif_Invasive_Tumor 0.9802 → ABSTAIN | (same) 0.9802 → ABSTAIN | No |
| Xenium FLEX | Prolif_Invasive_Tumor 0.9770 → ABSTAIN | (same) 0.9770 → ABSTAIN | No |
| CosMx BCC | Normal.Kerat 0.6037 → KEEP | Melanocyte 0.8247 → ABSTAIN | **Yes** |

Three KEEP libraries flip under the unconstrained maximum. Those flips are
collinearity facts on the measured panel:

- **NSCLC → epithelial (0.847).** A high malignant–epithelial cosine is a
  genuine collinearity with the tissue of origin. It is not, by itself, a
  reason to keep or discard either rule.
- **CosMx BCC → Melanocyte (0.825, 879 reference cells, robust to every
  support floor).** BCC and melanocytes share epidermal *residence*. They do
  not share lineage: basal-cell carcinoma is epithelial in origin; melanocytes
  are neural-crest derived. Shared pigment-pathway genes on a small panel can
  still produce a high cosine. That is a geometry fact, not a QC diagnosis.
- **HCC → CD3+ αβ T cells (0.854).** An immune neighbor can sit near the
  malignant hepatocyte program on this panel. Calling that a false positive or
  a doublet/contamination artifact requires independent QC evidence (doublet
  rate, contamination, annotation audit). The type name is not that evidence.

The unconstrained maximum therefore answers a different question (any eligible
neighbor) from the historical designated pair (a stated pair). A flip of the
BCC application cohort, or of any other KEEP library, is a consequence to
state. It is not a justification for retaining the designated pair.

The previously quoted BCC downstream RMSEs cannot rank the rules either. The
historical full-simplex score (0.106) is an eleven-type estimand including the
malignant coordinate. The conditional score after withholding is a ten-type
estimand. Scoring spots with no non-malignant truth mass as an all-zero
composition yields 0.214; excluding those 1,553 of 5,686 spots (27.3%) yields
0.188 on 4,133 spots. The two numbers stay on the record in
`out/conditional_rmse_fulln.json`. Their ordering does not show that one
neighbor rule is more accurate than the other.

## 2. Cutoff separability (why 0.80 needs no re-tuning)

From `out/cutoff_separability.json`: the maximum designated-KEEP cosine is
0.6486 (HCC) and the minimum designated-ABSTAIN cosine is 0.8616 (PDAC). The
frozen cutoff 0.80 lies inside the empty interval (0.6486, 0.8616). Because no
designated cosine falls in this band, all eight designated calls are invariant
for every cutoff in 0.75–0.85. The library-clustered bootstrap on the fraction
of eligible pairs at or above 0.80 is 0.24 with a 95% interval of about
[0.12, 0.41] over eight library clusters (`out/clustered_bootstrap.json`).

## 3. Rule options

These are prospective contracts. None is selected here by outcome.

**Option A — designated-pair operating rule.** The operating malignant
coordinate is gated on a pair named before scoring. For the eight libraries in
this article, that pair is the historical designated pair already reported.
The complete maximum-eligible scan is a transparency audit, not the operating
call. This option is executable only if the pair is named independently of the
cosine it will receive. "The biologically meaningful same-compartment neighbor"
is not such a name: two analysts can disagree about the compartment, so it is
not a unique rule.

**Option B — constrained maximum-eligible rule.** Eligible set = every
annotated non-malignant program with at least `n_min` reference cells that is
represented in the locked reference AND whose annotation label is in a
pre-specified candidate set written down before any cosine is read. Score =
maximum eligible cosine; ties broken by lexicographic reference label. A
compartment filter is allowed only if the membership list is attached to the
lock and is not edited after a cosine is seen. Under a stromal/epithelial
candidate set the HCC immune flip is removed, while NSCLC (epithelial) and BCC
(melanocyte) flips remain and require a downstream recompute.

**Option C — unconstrained maximum-eligible rule.** Eligible set excludes only
the malignant program; score = maximum eligible cosine. This is the
descriptive audit already reported. It flips NSCLC, HCC, and BCC. It is a
complete identifiability scan. It is not the same scientific object as the
eight designated calls.

## 4. What the current manuscript uses

The current manuscript uses the historical designated pairs as the operating
estimand of the eight published calls, and publishes the complete eligible
scan as the sensitivity audit that answers R2-3. That is a description of
what was already read, not a new prospective lock chosen to preserve a
headline.

If a later library needs a prospective algorithmic rule, one of Options A–C
must be named, with its eligible set written down, before that library is
scored. Recomputing the eight historical libraries after seeing their results
is retrospective robustness, not prospective validation.

If a flip is later locked as the operating call, the downstream contract in
section 5 applies. `downstream_and_gate_fulln.py` already provides the BCC
KEEP-versus-ABSTAIN downstream at full n; `conditional_rmse_fulln.py` reports
the exclusion-corrected conditional RMSE beside the superseded figure.

## 5. If a flip is locked: downstream contract

For any library whose operating call becomes ABSTAIN, the malignant coordinate
is withheld (missing, never scored as zero) and the remaining simplex is
renormalized. The reported non-malignant composition is then conditional on
malignant withholding. Spots with no non-malignant truth mass are undefined
for that conditional question and are excluded and counted, matching the
400-spot audit. The BCC downstream under this contract is quantified in
`out/bcc_abstain_downstream.json` and `out/conditional_rmse_fulln.json`.
