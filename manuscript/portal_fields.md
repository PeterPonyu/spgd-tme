# Frontiers submission portal — field-by-field text

Frontiers collects the data availability, ethics, funding, contribution, conflict and AI
statements as separate plain-text form fields, and renders those fields rather than the
ones in the PDF. Numeric citations do not resolve there, so each statement below spells out
what `declarations.tex` reaches by reference number. Keep the two in step: the PDF and the
form must say the same thing.

---

## Article type

Methods

## Research Topic

Decoding Tumor Complexity: Broad Perspectives from Integrative Multi-Omics and Single-Cell
Technologies in Cancer Genetics (topic 73845, deadline 21 December 2026). The topic runs
under both Cancer Genetics and Oncogenomics and Computational Genomics, so it can be
selected without moving the submission off the section it was created under. None of its
three topic editors share an institution with any author.

## Scope statement

> This manuscript describes two computational operators added to a training-free cell-type
> composition estimator for spatial transcriptomics, which places it within Computational
> Genomics: methods and applications of analytical platforms for complex biological data.
>
> The first operator is a KEEP/ABSTAIN reportability gate that withholds the malignant
> coordinate once the malignant-neighbour cosine of the reference reaches a cutoff frozen
> before any sweep. The second is a Patient_ID donor split that builds mixed spots and
> reference from disjoint patients, so transfer is measured across donors rather than
> within one. Both are evaluated on eight spatial libraries spanning CosMx, openST
> and Xenium, covering basal-cell carcinoma, non-small-cell lung, colorectal,
> hepatocellular, pancreatic, head-and-neck and breast tissue.
>
> The contribution states where a per-spot tumour fraction can be trusted and where it
> must be refused. Across these libraries most variance in the deciding quantity sits
> between reference programs rather than platform families, reported as an association
> rather than as platform independence. Plotted values, frozen constants, input digests
> and rendering scripts are supplied as Supplementary Material; provider-controlled
> inputs are identified by digest and used under their access terms.
>
> For the Research Topic "Decoding Tumor Complexity", this is a cross-cancer
> spatial-transcriptomics framework applied unchanged to seven tumour types.

198 words against the 200-word cap.

## Abstract

Paste this into the manuscript-information Abstract field. It is the current
abstract, not the Version 1 text still on the project page.

> This study presents two locked operators around a training-free composition baseline in a standalone SPGD-TME Methods implementation, so that, for the locked or explicitly eligible malignant-neighbor comparison, a per-spot malignant fraction is written only where the reference can separate the malignant program from its neighbor: a KEEP/ABSTAIN reportability gate that withholds the malignant coordinate once the malignant-neighbor cosine reaches a frozen cutoff c* = 0.80, and a Patient_ID donor split that builds mixed spots and reference from disjoint patients. On four-patient CosMx basal-cell carcinoma the operators recover named tissue objects: ulcerated-nodular Patient B is tumor-rich relative to Patient A, the wound axis on D-from-C drops tumor fraction from 0.8425 to 0.4665 while MoMacDC rises in both locked truth and the estimate; fibroblast occupancy rises in the locked truth, though the estimate recovers only part of that shift and is not monotone, and directed transfer recovers composition most tightly on B from A (RMSE 0.0659, spot-level PCC 0.9528). The frozen cosine reports KEEP, and therefore a tumor fraction, on CosMx BCC (cosine 0.6037), independent CosMx NSCLC (tumor versus fibroblast 0.6482; directed-transfer RMSE 0.1066, spot-level PCC 0.8415), CosMx colorectal carcinoma (0.5058), and CosMx HCC (0.6486). It returns ABSTAIN, holding the malignant coordinate missing and continuing the remaining types on the simplex, on CosMx PDAC (0.8616), HNSCC openST (0.9727), breast Xenium (0.9802), and an orthogonal Xenium FLEX reference (0.9770). CosMx PDAC abstains on the same platform that carries all four KEEP calls, so the observed pattern is consistent with collinear type pairs; the present library-level design does not establish platform independence. A repeated 400-spot openST build takes 16.103 +/- 2.891 s (five warm runs; CV 17.95%), of which the in-memory reportability decision is 0.001 s, so reportability remains a small operation relative to the fixed baseline fit.

## Running title

Locked mixed-spot TME operators

## Counts to type into the form

Word count 11739. Figures 15. Tables 4.

The Version 1 project page still shows FLEX 0.987505, "the cutoff separates collinear type pairs rather than assay platforms", and "0.001 s of a 60.252 s pass". Those are the submitted abstract. Replace them with the abstract above when the form is edited. Do not type a calendar date into any correspondence box.

## Title

## Keywords

tumor microenvironment; spatial transcriptomics; mixed-spot composition; cell-type
deconvolution; reportability gate; abstention; donor transfer; CosMx

## Authors, in submission order

| # | Name | ORCID | Affiliation (Department / Institution / City / Country) | Role |
|---|------|-------|--------------------------------------------------------|------|
| 1 | Rui Yang | 0009-0009-5669-245X | Department of Medical Engineering / Army Medical University / Chongqing / China | co-first |
| 2 | Tianfei Ran | 0009-0003-0124-7638 | Xinqiao Hospital, Second Affiliated Hospital of Army Medical University / Army Medical University / Chongqing / China | co-first |
| 3 | Lei Ran | 0009-0002-0565-0240 | Department of Dermatology and Rheumatology / Army Medical University / Chongqing / China | author |
| 4 | Zeyu Fu | 0009-0001-8329-0108 | State Key Laboratory of Trauma and Chemical Poisoning, College of Preventive Medicine / Army Medical University / Chongqing / China | corresponding |

The Institution field is `Army Medical University` for all four, so the portal indexes one
institution rather than four variants. Everything above it goes in the Department field.

## Data availability statement

> This study is a reanalysis of public spatial transcriptomics data; no new data were
> generated, and every library below is named with the repository that serves it. The
> four-patient CosMx basal-cell carcinoma export that carries the wound axis
> and the donor split is deposited at Zenodo under doi:10.5281/zenodo.14330691 (Andreatta
> et al., 2024) and is described in Yerly et al., Nature Communications 2022 and Yerly et
> al., bioRxiv 2025. The CosMx non-small-cell lung and human liver libraries are the
> NanoString NSCLC and human liver FFPE releases (He et al., Nature Biotechnology 2022),
> taken from the redistribution at Zenodo doi:10.5281/zenodo.15487520 and governed by the
> NanoString data licence deposited in that record (Sun et al., 2025). That agreement is
> the Bruker Spatial Biology Data License Agreement for Non-Commercial Use. Those terms are
> not compatible with a CC-BY supplement, so the matrices derived from that release stay
> under the deposited licence rather than the article terms. The CosMx colorectal
> sections are at Zenodo doi:10.5281/zenodo.15574384 (Crowell et al., bioRxiv 2025). The
> CosMx pancreatic library is at NCBI GEO under accession GSE277782 (Pei et al., Nature
> 2025). The HNSCC openST library and the breast Xenium and Xenium FLEX libraries are the
> public releases of their source publications (Schott et al., Cell 2024; Janesick et al.,
> Nature Communications 2023). The values plotted behind every panel, the cutoff frozen
> before any sweep, the locked constants as they stand, the content digest of every locked
> input, and the scripts that render
> every figure and table are provided as Supplementary Material with this submission; the
> reference matrices are derived from the public libraries named above and are identified
> in that bundle by digest rather than redistributed under their source licences. The
> same review-build source is archived at Zenodo, doi:10.5281/zenodo.22759792, in
> the form already used for the parent estimator (Fu et al., 2026, doi:10.5281/zenodo.21869991).
> Requests for any input not covered above should go to the corresponding author.

## Ethics statement

> Ethical review and informed consent were obtained in the primary studies that generated
> the tissue and are reported there (Yerly et al., Nature Communications 2022; Yerly et
> al., bioRxiv 2025; He et al., Nature Biotechnology 2022; Janesick et al., Nature
> Communications 2023; Schott et al., Cell 2024; Crowell et al., bioRxiv 2025; Pei et al.,
> Nature 2025). Two of those source records are preprints at the time of writing. This work
> used only de-identified, publicly released data and did not recruit participants, collect
> new specimens, or access identifiable information; we therefore did not seek additional
> ethical approval for this secondary analysis.

## Author contributions

> ZF: conceptualization, methodology, funding acquisition, resources, supervision, project
> administration, validation, writing – review and editing. RY: software, formal analysis,
> visualization, writing – original draft. TR: data curation, investigation, formal
> analysis, writing – original draft. LR: investigation, validation, writing – review and
> editing. RY and TR
> contributed equally to this work and share first authorship. ZF is the corresponding author and directed the
> study. All authors read and approved the submitted version.

## Funding

> This work was supported by the Ministry of Science and Technology of the People's
> Republic of China (Grant No. 2024YFA1107101) and by the State Key Laboratory of Trauma
> and Chemical Poisoning (Grant No. 2024K004). The funders had no role in the design of the
> study, the analysis or interpretation of the data, the writing of the manuscript, or the
> decision to submit it.

## Conflict of interest

> The authors declare that the research was conducted in the absence of any commercial or
> financial relationships that could be construed as a potential conflict of interest.

## Generative AI statement

> The authors used Claude (Anthropic; models Claude Opus 5 and Claude Sonnet 5, accessed
> through Claude Code, https://claude.com/claude-code) for language editing of the
> manuscript text and for writing and refactoring the analysis, figure-rendering, and
> typesetting code. No claim, number, or figure was generated by these tools: every reported
> value is computed by the released scripts from the inputs named above, and the tools took
> no part in selecting, interpreting, or deciding any result. The authors verified all
> content and take full responsibility for the work.

## Files to upload

Use the current pack, not `labs/active/spgd-tme/submission/`. Do not type a calendar
date into any correspondence box.

| Portal slot | File |
|-------------|------|
| Manuscript PDF | `manuscript.pdf` |
| Manuscript source | `manuscript.tex` (one flattened file; JPEG figures; `\bibliography{references}`) |
| Bibliography | `references.bib` (31 cited entries, each with a DOI) |
| Figures 1–15 | `Figure1.jpg` … `Figure15.jpg`, 300 dpi; do not downsample |
| Supplementary Material | `supplementary.zip` |
| Reviewer 1 attachment | `merged/reviewer1_response_with_tracked_changes.pdf` |
| Reviewer 2 attachment | `merged/reviewer2_response_with_tracked_changes.pdf` |
| Editor / cover attachment | `merged/cover_letter_with_tracked_changes.pdf` |

Paste, not upload: `cover_letter.txt`, `reviewer1_portal.txt`, `reviewer2_portal.txt`,
`rebuttal_overview_portal.txt`, and the statement blocks above.
