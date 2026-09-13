# Cover letter — Frontiers in Genetics

**Manuscript title:** Two locked operators report mixed-spot TME composition on CosMx
carcinomas

**Article type:** Methods

**Corresponding author:** Zeyu Fu, State Key Laboratory of Trauma and Chemical Poisoning,
College of Preventive Medicine, Army Medical University, Chongqing, China
(fuzeyu99@tmmu.edu.cn, ORCID 0009-0001-8329-0108)

---

Dear Editors,

We submit *Two locked operators report mixed-spot TME composition on CosMx carcinomas* for
consideration as a Methods article.

Spatial composition estimators write a malignant fraction into every mixed spot, including
spots where the reference cannot separate the malignant program from the stromal or
epithelial neighbour it is nearly collinear with. The number is produced, it is wrong, and
nothing in the output marks it as unsupported. This manuscript adds two operators that
address that failure directly: a KEEP/ABSTAIN reportability gate that withholds the
malignant coordinate once the malignant–neighbour cosine reaches a cutoff frozen at
c\* = 0.80 before any sweep, and a Patient_ID donor split that builds mixed spots and
reference from disjoint patients so a transfer result cannot be read off the donor it came
from.

Both operators are evaluated on public spatial transcriptomics libraries. On four-patient
CosMx basal-cell carcinoma they recover named tissue objects — the ulcerated-nodular and
wound axes — and directed donor transfer reaches RMSE 0.0659 and spot-level PCC 0.9528 on
the tightest edge. The frozen cutoff returns KEEP on four independent CosMx carcinomas and
ABSTAIN on CosMx pancreatic adenocarcinoma, HNSCC openST, breast Xenium, and an orthogonal
Xenium FLEX reference. The pancreatic abstention is the within-platform control: it sits on
the same assay platform as the four KEEP calls, so the observed pattern is consistent with
malignant--neighbour collinearity. The library-level design and the formal permutation analysis
are deliberately reported as underpowered for establishing platform independence. A repeated
400-spot openST build takes 22.565 +/- 2.861 s, while 1,000 in-memory refusal applications
take 0.455 s.

We believe the work suits Frontiers in Genetics as a Methods article because its
contribution is a checkable computational contract rather than a biological finding: every
constant is frozen before use, every reported number is emitted by a released script from a
documented input, and provider-controlled source libraries are used only under their
applicable access terms. The decision the method adds is an explicit refusal that a reader
can audit.

This manuscript is not under consideration at any other journal and has not been published
elsewhere. The fixed composition core is cited for provenance through its software archive
(doi:10.5281/zenodo.21869991); the present manuscript contributes and evaluates the two
locked operators, their audit analyses, and the reproducibility contract as a standalone
SPGD-TME Methods implementation.

**Data and reproducibility.** No new data were generated. Every library is public and named
by repository accession in the Data availability statement. The values behind every panel,
the frozen constants, the content digest of every locked input, and the scripts that render
every figure and table accompany the submission as Supplementary Material.

All authors have read and approved the submitted version and declare no competing
interests. Our use of generative AI assistants is disclosed in the Generative AI statement.

Thank you for your consideration.

Sincerely,

Zeyu Fu, on behalf of all authors
