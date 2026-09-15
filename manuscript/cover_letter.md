# Cover letter — Frontiers in Genetics

**Manuscript title:** Two locked operators report mixed-spot TME composition on CosMx
carcinomas

**Article type:** Methods

**Corresponding author:** Zeyu Fu, State Key Laboratory of Trauma and Chemical Poisoning,
College of Preventive Medicine, Army Medical University, Chongqing, China
(fuzeyu99@tmmu.edu.cn, ORCID 0009-0001-8329-0108)

---

Dear Editors,

We submit the revised version of *Two locked operators report mixed-spot TME composition on
CosMx carcinomas* for consideration as a Methods article, with a point-by-point response to
each reviewer and a short overview of the revision.

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
decomposition that does not depend on the underpowered test. Second, in response to the review
we now specify in full the rule by which the malignant–neighbour pair is designated, making the
selection criterion explicit and auditable. The revision presents 15 figures and 4 tables, above the nominal 15-object combined cap for this article type; all are retained as review evidence and the counts are stated on the first page.

No new data were generated, and every library is named by repository accession in the Data
availability statement. The manuscript is not under consideration elsewhere and has not been
published elsewhere; the fixed composition core is cited for provenance through its software
archive (doi:10.5281/zenodo.21869991). All authors have read and approved the submitted
version and declare no competing interests. Our use of generative AI assistants is disclosed
in the Generative AI statement.

Thank you for your consideration.

Sincerely,

Zeyu Fu, on behalf of all authors
