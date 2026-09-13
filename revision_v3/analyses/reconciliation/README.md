# V3 claim reconciliation ledger

This ledger is the numerical source-of-truth for the V3 review build. Each row records the estimand, library universe, denominator, spot count, value, source artifact, and current manuscript location. It is deliberately additive and does not overwrite historical V0/V1/V2 records.

## How to read the two neighbor scans

- The **51-row scan** is the stored-reference CosMx audit for four libraries. It preserves the historical export and its denominator reconciliation (NSCLC 17, CRC 8, HCC 15 stored/14 eligible, PDAC 6 stored/5 eligible). Its descriptive exceedance fraction is 29.4% with a library-clustered interval of 6.3–68.4%.
- The **112-row scan** is a separate full-input audit across eight libraries. It uses the complete eligible non-malignant columns available in each library and has an exceedance fraction of 24.1% (library-clustered 95% interval 11.8–41.0%). The two fractions must not be pooled or substituted for each other.

## Status vocabulary

`RECONCILED` means the value and manuscript location agree. `OPEN_CONFLICT` marks a real numerical discrepancy requiring harmonization before the response package is final. `OPEN_EDITORIAL` marks a wording/layout or bibliographic item. `OPEN_EXTERNAL` marks an issue that cannot be closed from the current local evidence.

## Current blocking finding

The Xenium FLEX designated cosine appears as 0.987505 in the older raw cell-mean confirmation and as 0.977005 in the canonical library-size-normalized profile used by the full-input scan and P/S audit. Both calls are ABSTAIN, but the number is not interchangeable. The current V3 manuscript and figure inputs have now been harmonized to the canonical value; the two profile constructions remain documented here for provenance.

## Xenium FLEX harmonization rule

The older raw cell-mean confirmation (0.987505) is retained only as a historical audit value. The V3 operating value is 0.977005, computed from the library-size-normalized reference profile used by the canonical full-input loader. Because both values are above 0.80, the KEEP/ABSTAIN state is unchanged; all current manuscript and figure inputs use 0.977005.
