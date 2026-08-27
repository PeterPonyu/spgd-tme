# SPGD-TME design

Physical object: mixed-spot TME composition, and when a tumor fraction
must be refused. Not a prognostic signature and not a clinical biomarker.

## Method increment (two steps on top of SPGD)

1. Malignant collinearity refusal at \(c^\star=0.80\). If the uninterpolated
   (or interpolated) cosine between the locked malignant column and its
   locked neighbor is \(\ge 0.80\), that type is ABSTAIN (NaN). Do not
   write RMSE 0 for a refused type.
2. Donor split by `Patient_ID` only. Never `Run_Tissue_name`. Primary
   pairs are condition-matched: A↔B (Ulcerated_nodular) and C↔D (wound
   time course). C→D is locked from the CBC `crossdonor.csv` OUR-v4 row.

## Forbidden

- Writing CBC `portal_CBC`, `leaderboard.csv`, `crossdonor.csv`, or
  `realgt4_benchmark`
- New downloads
- survival / biomarker / KM / TCGA columns
- Pasting DestVI `0.2034` or crossdonor DestVI `0.1126` into new tables
- Retuning \(c^\star\) from sweep RMSE
