# Zenodo publication status

The SPGD-TME V2 public reproducibility package is published at [10.5281/zenodo.22726775](https://doi.org/10.5281/zenodo.22726775).

- Zenodo record: `22726775`
- Publication state: `done`
- Published file: `PUBLIC_RELEASE_V2_20260912.tar.gz`
- Published file size: 38,561,772 bytes
- Zenodo file checksum: `md5:f17eb25649b2989593b96dd9e881c6fb`
- Local archive SHA-256: `1db3801ca35755596e0470d18144afd3202ed8c9b0e3b3891e6ac20f743d9a8f`

The pre-existing baseline record `10.5281/zenodo.21869991` remains unchanged. The published V2 archive contains the sanitized release directory.

## V3 status

The V3 source archive is published under the concept DOI
[10.5281/zenodo.22759792](https://doi.org/10.5281/zenodo.22759792), which always resolves to the
newest version. The manuscript cites that concept DOI rather than a version DOI, so the data
statement keeps resolving as later versions are deposited.

- Concept DOI: `10.5281/zenodo.22759792`
- Latest version: `3.0.2`, record `22764388`, DOI `10.5281/zenodo.22764388`
- Published file: `spgd-tme-v3-184beab-source.tar.gz`
- Published file size: 2,796,376 bytes
- Zenodo file checksum: `md5:4aaa022565cd0a59810ac79975c50ddc`
- Local archive SHA-256: `69098d433d0bfcc7350efd96713226abb13f592f3d805798b9fed0e1e9fd5c81`
- Source commit inside the archive: `184beabd5faabb298a32eea2159872ad8b2f7323`

Earlier versions under the same concept remain citable: `3.0.0` (`22759793`) and `3.0.1`
(`22760810`).

The archive carries the source, the frozen constants, the plotted values, the analysis and
render scripts, and the test suite. It deliberately omits the rendered figure PDFs, which the
render scripts regenerate from the included plot data; the journal receives those figures as
JPEG attachments instead.

The V2 DOI remains the citable archival release of the earlier public package. The V3 record is
a new software deposit linked to V2 by `isVersionOf`; it does not reuse the V2 concept DOI.
