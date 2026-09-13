# Licensing boundary

This release separates three kinds of material.

1. Manuscript text, response letters, rendering code, and table-generation code are provided
   for scholarly inspection and reproducible use. Their applicable copyright and reuse terms
   should be read together with the repository metadata and any journal policy.
2. Derived plot tables and frozen constants are included to reproduce the reported figures and
   tables. They do not grant rights to redistribute the source libraries from which reference
   matrices or spatial measurements were obtained.
3. Source datasets remain subject to the licences and access conditions of their original
   providers.

## The NanoString / Bruker boundary

The CosMx NSCLC and human liver libraries reach this work through the Zenodo redistribution at
`10.5281/zenodo.15487520`, which deposits the governing agreement alongside the data. That
agreement is the Bruker Spatial Biology Data License Agreement for Non-Commercial Use. It was
read clause by clause for this release, and the determination is recorded here in semantic
form; the agreement text itself is **not** redistributed, because the document is marked
confidential by its provider.

What the clauses establish, for the actions this release actually performs:

- **Analysis use** of the data is permitted for non-commercial purposes.
- **Redistribution of derived reference matrices** ("Modified Data") is permitted
  non-commercially, but only if a copy of the licence travels with them, modifications are
  marked, NanoString is attributed with a link to its website, and the same non-commercial
  terms are carried forward with no additional or different conditions.
- **Publication of non-invertible content digests and semantic source identifiers** is not a
  distribution of the data.

Because the same-terms condition cannot be satisfied by a CC-BY supplement, this release does
not ship NanoString-derived reference matrices under the article terms. It identifies them by
content digest instead, and those matrices remain available under the deposited non-commercial
licence from the archival record. Everything else in this repository — analysis code, frozen
constants, figure-level numerical outputs, and rendering scripts — is unaffected by that
agreement.

This is the authors' reading of the clauses against what this release distributes. It is not a
legal opinion. Confirmation that the arrangement satisfies a journal's data-sharing policy
rests with that journal's editorial office, and institutional sign-off rests with the authors'
institution.

## Not included

The release deliberately omits private workbench records, machine-specific paths, agent
transcripts, unpublished raw donor files, and the provider agreement text itself.
