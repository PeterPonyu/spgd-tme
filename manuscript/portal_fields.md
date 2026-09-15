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
> within one. Both are evaluated on eight public spatial libraries spanning CosMx, openST
> and Xenium, covering basal-cell carcinoma, non-small-cell lung, colorectal,
> hepatocellular, pancreatic, head-and-neck and breast tissue.
>
> The contribution is a statement of where a per-spot tumour fraction can be trusted and
> where it must be refused, with evidence that the refusal boundary tracks collinearity
> between reference programs rather than assay platform. Plotted values, frozen constants,
> input digests and the rendering scripts are supplied as Supplementary Material, so every
> reported number is recomputable from public inputs.
>
> For the Research Topic "Decoding Tumor Complexity", this is spatial transcriptomics used
> to decipher tumour ecosystems, and a cross-cancer framework applied unchanged to seven
> tumour types.

195 words against the 200-word cap.

## Title

Two locked operators report mixed-spot TME composition on CosMx carcinomas

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
> generated. The four-patient CosMx basal-cell carcinoma export that carries the wound axis
> and the donor split is deposited at Zenodo under doi:10.5281/zenodo.14330691 (Andreatta
> et al., 2024) and is described in Yerly et al., Nature Communications 2022 and Yerly et
> al., bioRxiv 2025. The CosMx non-small-cell lung and human liver libraries are the
> NanoString NSCLC and human liver FFPE releases (He et al., Nature Biotechnology 2022),
> taken from the redistribution at Zenodo doi:10.5281/zenodo.15487520 and governed by the
> NanoString data licence deposited in that record (Sun et al., 2025). The CosMx colorectal
> sections are at Zenodo doi:10.5281/zenodo.15574384 (Crowell et al., bioRxiv 2025). The
> CosMx pancreatic library is at NCBI GEO under accession GSE277782 (Pei et al., Nature
> 2025). The HNSCC openST library and the breast Xenium and Xenium FLEX libraries are the
> public releases of their source publications (Schott et al., Cell 2024; Janesick et al.,
> Nature Communications 2023). The values plotted behind every panel, the constants frozen
> before any sweep, the content digest of every locked input, and the scripts that render
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
> Nature 2025). This work used only de-identified, already public data and did not recruit
> participants, collect new specimens, or access identifiable information, so it required
> no additional ethical approval.

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

> The authors used large-language-model assistants for language editing and for the
> analysis, figure-rendering, and typesetting code. No claim,
> number, or figure was generated by these tools: every reported value is computed by the
> released scripts from the public inputs named above. The authors verified all content and
> take full responsibility for the work.

## Files to upload

| Portal slot | File |
|-------------|------|
| Manuscript | `submission/manuscript.pdf` (and `manuscript.tex` if source is requested) |
| Figures 1–15 | `submission/Figure1.jpg` … `Figure15.jpg`, 300 dpi at 180 mm |
| Supplementary Material | `supplementary.zip` |
| Cover letter | `manuscript/cover_letter.md`, pasted as plain text |
