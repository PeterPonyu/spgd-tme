# Zenodo publication status

The SPGD-TME V2 public reproducibility package is published at [10.5281/zenodo.22726775](https://doi.org/10.5281/zenodo.22726775).

- Zenodo record: `22726775`
- State verified through the public API: `done`
- Published file: `PUBLIC_RELEASE_V2_20260912.tar.gz`
- Published file size: 38,561,772 bytes
- Zenodo file checksum: `md5:f17eb25649b2989593b96dd9e881c6fb`
- Local archive SHA-256: `1db3801ca35755596e0470d18144afd3202ed8c9b0e3b3891e6ac20f743d9a8f`

The pre-existing baseline record `10.5281/zenodo.21869991` was inspected and left unchanged. The published V2 archive contains the exact sanitized release directory; the mutable publication-status note is kept outside that directory so the archive's own integrity inventory remains stable.

## V3 status

The V3 review-build archive is published at [10.5281/zenodo.22759793](https://doi.org/10.5281/zenodo.22759793)
(concept DOI [10.5281/zenodo.22759792](https://doi.org/10.5281/zenodo.22759792)).

- Zenodo record: `22759793`
- State verified through the public API: `done`
- Published file: `spgd-tme-v3-03b1517.tar.gz`
- Published file size: 78,414,118 bytes
- Zenodo file checksum: `md5:5ac5d2e15d87870650a55d21b3ee6138`
- Local archive SHA-256: `93f426371c03f5122fa85c80464042b6c67a8bc95fc13e44af548eea352c851e`
- Source commit inside the archive: `03b15179a809f37f7c29f871429921569dfbe439`

The V2 DOI remains the citable archival release of the earlier public package. The V3 record
is a new software deposit linked to V2 by `isVersionOf`; it does not reuse the V2 concept DOI.

## Source repository visibility

The Git repository backing this release is **public** on the `codex/v3-public-release` branch. An
unauthenticated GitHub API request returns HTTP 200 with `private=false`; the public branch
resolves to the reviewed V3 source commit. Later citation commits that name the V3 DOI are
additive and are not inside the deposited tarball.
