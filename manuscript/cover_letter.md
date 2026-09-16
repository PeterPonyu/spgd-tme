# Cover letter — Frontiers in Genetics

**Manuscript title:** Two locked operators report mixed-spot TME composition on CosMx
carcinomas

**Article type:** Methods

**Corresponding author:** Zeyu Fu, State Key Laboratory of Trauma and Chemical Poisoning,
College of Preventive Medicine, Army Medical University, Chongqing, China
(fuzeyu99@tmmu.edu.cn, ORCID 0009-0001-8329-0108)

---

Dear Editors,

This letter is the first part of a single PDF. It continues with the revised manuscript in
tracked-changes form, where every insertion and deletion against the reviewed version is
marked and highlighted, so the changes described below can be read directly against the text
that carries them. All analyses added in this revision appear in that manuscript, and the
values behind every figure and table are supplied as Supplementary Material.

We submit the revised version of *Two locked operators report mixed-spot TME composition on
CosMx carcinomas* for consideration as a Methods article, with a point-by-point response to
each reviewer and a short overview of the revision. Each of those responses is likewise
attached as a single PDF that carries the tracked-changes manuscript behind it.

Spatial composition estimators write a malignant fraction into every mixed spot, including
spots where the reference cannot separate the malignant program from the neighbour it is
nearly collinear with. The number is produced, it is wrong, and nothing in the output marks it
as unsupported. The manuscript adds two operators that address this directly: a KEEP/ABSTAIN
reportability gate that withholds the malignant coordinate once the malignant–neighbour cosine
reaches a cutoff frozen at c\* = 0.80 before any sweep, and a Patient_ID donor split that
builds mixed spots and reference from disjoint patients. Both are evaluated on public
libraries spanning three assay platforms; the quantitative results are in the abstract.

The work suits Frontiers in Genetics as a Methods article because its contribution is a
checkable computational contract rather than a biological finding: every constant is frozen
before use, every reported number is emitted by a released script from a documented input, and
provider-controlled libraries are used only under their applicable access terms. The decision
the method adds is an explicit refusal that a reader can audit.

Two changes in this revision are worth the editor's attention. First, we have refined the
platform-level statement: rather than asserting platform independence, the revision reports it
as an explicitly power-limited observation across eight libraries, grounded in a variance
decomposition that does not depend on the underpowered test. Second, the review's question
about how the malignant–neighbour pair is chosen led us to audit that step, and the audit found
that three different procedures had been in use across the eight libraries, one of them
outcome-dependent. The Methods now state all three as the historical operating estimand rather
than describing a rule those eight calls did not follow, and a single algorithmic rule is
locked for any further library. We judged it better to report what we found than to present the
record more tidily than it supports.

No new data were generated, and every library is named by repository accession in the Data
availability statement. The manuscript is not under consideration elsewhere and has not been
published elsewhere; the fixed composition core is cited for provenance through its software
archive (doi:10.5281/zenodo.21869991). All authors have read and approved the submitted
version and declare no competing interests. Our use of generative AI assistants is disclosed
in the Generative AI statement.

Thank you for your consideration.

Sincerely,

Zeyu Fu, on behalf of all authors
