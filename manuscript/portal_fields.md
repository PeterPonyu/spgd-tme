# Frontiers submission portal — field-by-field text

Frontiers collects the data availability, ethics, funding, contribution, conflict and AI
statements as separate plain-text form fields, and renders those fields rather than the
ones in the PDF. Numeric citations do not resolve there, so each statement below spells out
what `declarations.tex` reaches by reference number. Keep the two in step: the PDF and the
form must say the same thing.

---

## Article type

Methods

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
> bundle will be deposited as a citable reproducibility archive at Zenodo on acceptance.
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
> analysis. LR: validation, writing – review and editing. RY and TR contributed equally to
> this work and share first authorship. ZF is the corresponding author and directed the
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

> The authors used two generative artificial-intelligence coding assistants, Claude Code
> v2.1.239 (Anthropic) and Codex CLI v0.149.0 (OpenAI), for language editing, for writing
> and refactoring the analysis and figure-rendering scripts, and for typesetting. No
> scientific claim, no reported number, and no figure was produced by an assistant: every
> number in the text, tables, and figures is computed by the released scripts from the
> public inputs named above, and every figure is a direct render of those computed values.
> The authors reviewed and verified all such content and take full responsibility for the
> integrity and accuracy of the work.

## Files to upload

| Portal slot | File |
|-------------|------|
| Manuscript | `submission/manuscript.pdf` (and `manuscript.tex` if source is requested) |
| Figures 1–12 | `submission/Figure1.jpg` … `Figure12.jpg`, 300 dpi at 180 mm |
| Supplementary Material | `supplementary.zip` |
| Cover letter | `manuscript/cover_letter.md`, pasted as plain text |

## Gates that are not mine to clear

1. Zeyu Fu's ORCID has no employment record. The portal resolves an author to an
   institution through that record, so until `Army Medical University` is added there the
   corresponding author is not indexable against the affiliation printed on the paper.
2. Zeyu Fu's ORCID lists three personal email addresses and no institutional one. Add
   `fuzeyu99@tmmu.edu.cn` and make it public.
3. `PeterPonyu/SPGT-site` is a public page carrying this manuscript's byline, and its
   README states that SPGT is "the TME companion to published SPGD" and that "both
   manuscripts are under review". That page is indexable and contradicts a submission that
   presents this work as standalone. Reconcile the two before the manuscript is uploaded.
