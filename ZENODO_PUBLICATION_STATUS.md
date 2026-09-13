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

**No V3 Zenodo version has been created or published.** The V3 package accompanies the
manuscript as Supplementary Material, and its deposit is scheduled for acceptance so that the
archived version matches the accepted text. Creating it requires a current API token; no
previously exposed token may be reused.

## V3 upload candidate

The sanitized V3 candidate is prepared from public branch commit `4160489` as
`spgd-tme-v3-4160489.tar.gz` (SHA-256
`10537440b9f08a376bcced2ade102dd94227fae295f3dca00e55b457441c7225`). It has not been
uploaded or published; the extracted archive was re-scanned for machine-local paths, credentials,
internal workflow documents, and confidential agreement files before release.

## Source repository visibility

The Git repository backing this release is **public** on the `codex/v3-public-release` branch. An
unauthenticated GitHub API request returns HTTP 200 with `private=false`; the public branch
resolves to the reviewed V3 source commit. The V3 Zenodo deposit remains separate and is not
claimed until it is created and verified.
