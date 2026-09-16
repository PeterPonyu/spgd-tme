# Malignant-neighbor selection rule — author-lock specification (V3)

Status: locked for prospective use. This document does not change, and does not
describe, any of the eight historical calls. Those were designated by three
different procedures, one of them outcome-dependent, which the Methods section
now states in the manuscript rather than only here. What is locked below is the
rule any further library must follow, fixed before a further call is made, so the
designated pair stops being a per-library judgement. It records the rule options,
the complete evidence generated in `revision_v3/`, and the selected rule.

The frozen cutoff `c* = 0.80` is used exactly as locked and is not re-tuned
anywhere in this analysis.

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

Three KEEP libraries flip under the maximum-eligible rule. The three flips are
not equally plausible:

- **NSCLC → epithelial (0.847):** epithelial cells are the tissue of origin of
  a lung carcinoma, so a high malignant–epithelial cosine is a genuine
  collinearity, not an artifact. A flip here is defensible.
- **CosMx BCC → Melanocyte (0.825, 879 reference cells, robust to every support
  floor):** BCC and melanocytes share epidermal lineage and pigment-pathway
  genes on a small panel; the near-collinearity is biologically interpretable.
- **HCC → CD3+ αβ T cells (0.854):** an immune neighbor collinear with the
  malignant hepatocyte program is biologically implausible and most likely a
  small-panel / doublet artifact. A flip driven by this neighbor is a false
  positive of the maximum rule.

The HCC case is the decisive observation: an unconstrained maximum-over-eligible
rule can select a cross-compartment neighbor that no analyst would designate,
and would then withhold a reportable malignant coordinate for the wrong reason.

## 2. Cutoff separability (why 0.80 needs no re-tuning)

From `out/cutoff_separability.json`: the maximum designated-KEEP cosine is
0.6486 (HCC) and the minimum designated-ABSTAIN cosine is 0.8616 (PDAC). The
frozen cutoff 0.80 lies inside the empty interval (0.6486, 0.8616). Because no
designated cosine falls in this band, all eight designated calls are invariant
for every cutoff in 0.75–0.85. The library-clustered bootstrap on the fraction
of eligible pairs at or above 0.80 is 0.24 with a 95% interval of about
[0.12, 0.41] over eight library clusters (`out/clustered_bootstrap.json`).

## 3. Rule options

**Option A — designated-pair operating rule (recommended).** The operating
malignant coordinate is gated on the pre-registered designated pair: the
same-compartment stromal or epithelial program that is the biological neighbor
of the malignant program in that library. The complete maximum-eligible scan is
reported as a transparency audit, not as the operating call. Justification: the
designated calls sit outside the 0.75–0.85 band, and the maximum rule is shown
to select an implausible neighbor in HCC.

**Option B — constrained maximum-eligible rule.** Eligible set = every
annotated non-malignant program with at least `n_min` reference cells that is
represented in the locked reference AND lies in the same tissue compartment as
the malignant program (epithelial/stromal; immune-only programs excluded as
malignant neighbors). Score = maximum eligible cosine; ties broken by
lexicographic reference label. Under this constraint the HCC immune flip is
removed, while NSCLC (epithelial) and BCC (melanocyte) flips remain and require
a downstream recompute.

**Option C — unconstrained maximum-eligible rule (not recommended).** Eligible
set excludes only the malignant program; score = maximum eligible cosine. This
is the descriptive audit already reported; it flips NSCLC, HCC, and BCC,
including the implausible HCC immune neighbor, so it should not be the operating
rule.

## 4. Recommendation

Lock **Option A**. Keep the historical designated calls as the primary
operating estimand; publish the complete eligible scan (this analysis) as the
sensitivity audit that answers R2-3; and state the HCC immune-neighbor result
explicitly as the reason a naive maximum rule is not adopted. If the editor
requires an algorithmic rule, adopt **Option B** and recompute the downstream
composition for NSCLC, BCC (and any other constrained flip) under that lock;
`downstream_and_gate_fulln.py` already provides the BCC KEEP-versus-ABSTAIN
downstream at full n.

## 5. If a flip is locked: downstream contract

For any library whose operating call becomes ABSTAIN, the malignant coordinate
is withheld (missing, never scored as zero) and the remaining simplex is
renormalized. The reported non-malignant composition is then conditional on
malignant withholding. The BCC downstream under this contract is quantified in
`out/bcc_abstain_downstream.json`.
