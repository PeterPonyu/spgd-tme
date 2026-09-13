#!/usr/bin/env python
"""revision_v3 / scan_all_libraries.py

Unified complete eligible-neighbor scan across all eight SPGD-TME libraries,
with per-type reference counts, support-floor sensitivity, designated-versus-
maximum-eligible rule comparison, a cutoff-separability audit, and a
library-clustered bootstrap.

Integrity
---------
* Additive V3 sensitivity analysis. Reads references read-only; writes only
  inside revision_v3/out/. Does NOT overwrite any lock, historical call,
  probe JSON, or manuscript number. The frozen cutoff c* = 0.80 is never
  re-tuned.
* Carcinoma signatures are rebuilt from raw data through the same probe code
  paths (module 20 helpers) that produced the historical probe cosines.
* Platform signatures are rebuilt through the deconv-lab `_nnls_setup` path
  used by the C03 gate-input audit, reproducing the locked designated cosines
  to six decimals as a validation anchor.
"""
from __future__ import annotations

import importlib.util
import io
import json
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
DECONV = Path(os.environ.get("SPGD_DECONV_ROOT", Path(__file__).resolve().parents[1] / "data" / "external" / "deconv-lab"))
OUT = Path(__file__).resolve().parent / "out"
OUT.mkdir(parents=True, exist_ok=True)

C_STAR = 0.80
FLOORS = [0, 25, 50, 75, 100]

# --- shared probe helpers (module 20) ---------------------------------------
sys.path.insert(0, str(REPO))
_spec = importlib.util.spec_from_file_location("probe_he", REPO / "scripts/20_probe_he_nsclc_keep.py")
he = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(he)

sys.path.insert(0, str(DECONV / "src"))
from deconv_metrics import _nnls_setup  # noqa: E402


def _cos(P: np.ndarray, i: int, j: int) -> float:
    a, b = P[:, i], P[:, j]
    na, nb = float(np.linalg.norm(a)), float(np.linalg.norm(b))
    return 0.0 if na == 0 or nb == 0 else float(np.dot(a, b) / (na * nb))


def _counts_from_anno(anno_coarse: np.ndarray) -> dict[str, int]:
    vals, cts = np.unique(anno_coarse, return_counts=True)
    return {str(v): int(c) for v, c in zip(vals, cts)}


# --- carcinoma loaders (rebuild P + counts, never write probe JSON) ----------
def load_crc():
    import anndata as ad

    adata = ad.read_h5ad(REPO / "data/external/crc_cosmx/232.h5ad")
    raw = adata.obs["lv2"].astype(str).to_numpy() if "lv2" in adata.obs.columns else None
    if raw is None:
        col = next(c for c in ("cell_type", "celltype", "annotation", "lv1") if c in adata.obs.columns)
        raw = adata.obs[col].astype(str).to_numpy()
    anno = []
    for v in raw:
        vs = str(v).lower()
        if vs.startswith("epi.") or vs == "epi" or "tumor" in vs or vs.startswith("cancer"):
            anno.append("tumor")
        elif vs.startswith("caf") or "fib" in vs:
            anno.append("fibroblast")
        else:
            anno.append(str(v))
    anno = np.array(anno, dtype=object)
    types, P = he._type_means(adata.X, anno)
    coarse = np.array([he._coarse_label(a) for a in anno], dtype=object)
    return "CosMx CRC", types, P, _counts_from_anno(coarse), "tumor", "fibroblast"


def load_nsclc():
    X, anno, genes, meta = he._load_from_zip()
    types, P = he._type_means(X, anno)
    coarse = np.array([he._coarse_label(a) for a in anno], dtype=object)
    return "CosMx NSCLC", types, P, _counts_from_anno(coarse), "tumor", "fibroblast"


def load_hcc():
    from scipy.io import mmread

    zip_path = REPO / "data/external/he_liver/cosmx_liver.zip"
    with zipfile.ZipFile(zip_path) as zf:
        names = zf.namelist()
        prefixes = sorted({n.split("/")[0] for n in names if n.endswith("/qc/counts.mtx")})
        chosen = prefixes[0]
        for prefix in prefixes:
            lab = pd.read_csv(zf.open(f"{prefix}/labels.tsv"), sep="\t")
            c = "cell_type" if "cell_type" in lab.columns else lab.columns[-1]
            if lab[c].astype(str).str.lower().str.contains(r"tumor|cancer|malignant|\bhcc\b|hepatocellular").any():
                chosen = prefix
                break
        X = mmread(io.BytesIO(zf.read(f"{chosen}/qc/counts.mtx"))).tocsr()
        obs = pd.read_csv(zf.open(f"{chosen}/qc/observations.tsv"), sep="\t", index_col=0)
        lab = pd.read_csv(zf.open(f"{chosen}/labels.tsv"), sep="\t", index_col=0)
    lab = lab.reindex(obs.index)
    type_col = "cellType" if "cellType" in lab.columns else "cell_type"
    mask = lab[type_col].notna().to_numpy()
    X = X[mask]
    anno = lab.loc[mask, type_col].astype(str).to_numpy()

    orig = he._is_tumor_name

    def _liver_tumor(name: str) -> bool:
        n = str(name).lower().strip()
        return orig(n) or "hepatocellular" in n or n == "hcc" or "cholangiocarcinoma" in n

    he._is_tumor_name = _liver_tumor
    try:
        types, P = he._type_means(X, anno)
        coarse = np.array([he._coarse_label(a) for a in anno], dtype=object)
    finally:
        he._is_tumor_name = orig
    return "CosMx HCC", types, P, _counts_from_anno(coarse), "tumor", "Stellate.cells"


def load_pdac():
    base = REPO / "data/external/gse277782"
    sct = pd.read_csv(base / "GSE277782_CosMx_SCT_data.csv.gz", index_col=0)
    meta = pd.read_csv(base / "GSE277782_Meta.data_CoxMx.csv.gz", index_col=0)
    shared = sct.index.intersection(meta.index)
    sct, meta = sct.loc[shared], meta.loc[shared]
    anno = meta["Annotation_main"].astype(str).to_numpy()
    X = np.asarray(sct.to_numpy(), dtype=float)
    types, P = he._type_means(X, anno)
    coarse = np.array([he._coarse_label(a) for a in anno], dtype=object)
    return "CosMx PDAC", types, P, _counts_from_anno(coarse), "tumor", "CAF"


PLATFORM = {
    "openST": ("openst_benchmark", "Tumor", "Tumor_Keratin_Pearl", 0.972678),
    "Xenium": ("realgt_benchmark", "Invasive_Tumor", "Prolif_Invasive_Tumor", 0.980196),
    "Xenium FLEX": ("realgt2_benchmark", "Invasive_Tumor", "Prolif_Invasive_Tumor", None),
    "CosMx BCC": ("realgt3_benchmark", "Cancer.cells", "Normal.Kerat", 0.603666),
}


def load_platform(lib):
    d, mal, nbr, lock = PLATFORM[lib]
    base = DECONV / "data" / d
    sp = base / "benchmark_spots_counts.h5ad"
    if not sp.is_file():
        sp = base / "benchmark_spots.h5ad"
    seed = list(pd.read_csv(base / "truth_proportions.csv", index_col=0, nrows=0).columns)
    sig, _Y, _idx, types = _nnls_setup(str(sp), str(base / "reference_subset.h5ad"), seed)
    P = sig / np.clip(sig.sum(0, keepdims=True), 1e-12, None)
    import anndata as ad

    r = ad.read_h5ad(base / "reference_subset.h5ad")
    acol = next((c for c in ("cell_type", "annotation", "celltype") if c in r.obs.columns), None)
    counts = {str(k): int(v) for k, v in r.obs[acol].astype(str).value_counts().items()} if acol else {}
    return lib, types, P, counts, mal, nbr, lock


def scan_library(lib, types, P, counts, mal, nbr, family):
    idx = types.index(mal)
    rows = []
    for t in types:
        if t == mal:
            continue
        c = _cos(P, idx, types.index(t))
        rows.append({
            "library": lib, "platform_family": family, "malignant": mal, "neighbor": t,
            "cosine": round(c, 6), "n_ref_cells": counts.get(t, np.nan),
            "designated": bool(t == nbr), "decision": "ABSTAIN" if c >= C_STAR else "KEEP",
        })
    return rows


def main():
    all_rows, anchor = [], []
    carc_loaders = [load_crc, load_nsclc, load_hcc, load_pdac]
    for fn in carc_loaders:
        try:
            lib, types, P, counts, mal, nbr = fn()
            all_rows += scan_library(lib, types, P, counts, mal, nbr, "cosmx_carcinoma")
            print(f"[ok] {lib}: {len(types)} types")
        except Exception as e:  # noqa: BLE001
            print(f"[FAIL] {fn.__name__}: {e}", file=sys.stderr)
    for lib in PLATFORM:
        try:
            lib, types, P, counts, mal, nbr, lock = load_platform(lib)
            all_rows += scan_library(lib, types, P, counts, mal, nbr, "platform")
            rep = _cos(P, types.index(mal), types.index(nbr))
            anchor.append({"library": lib, "designated_neighbor": nbr, "reproduced_cosine": round(rep, 6),
                           "locked_cosine": lock, "matches_lock": (lock is not None and abs(rep - lock) < 1e-6)})
            print(f"[ok] {lib}: {len(types)} types, designated cos {rep:.6f} lock {lock}")
        except Exception as e:  # noqa: BLE001
            print(f"[FAIL] platform {lib}: {e}", file=sys.stderr)

    scan = pd.DataFrame(all_rows)
    scan.to_csv(OUT / "complete_eligible_scan.csv", index=False)
    pd.DataFrame(anchor).to_csv(OUT / "validation_anchor.csv", index=False)

    # rule comparison across floors
    comp = []
    for lib, g in scan.groupby("library", sort=False):
        des = g[g["designated"]]
        dcos = float(des["cosine"].iloc[0]) if len(des) else np.nan
        dnbr = str(des["neighbor"].iloc[0]) if len(des) else ""
        for floor in FLOORS:
            known = g["n_ref_cells"].notna()
            e = g[(~known) | (g["n_ref_cells"] >= floor)]
            if not len(e):
                continue
            im = e["cosine"].idxmax()
            comp.append({
                "library": lib, "floor": floor, "n_eligible": int(len(e)),
                "designated_neighbor": dnbr, "designated_cosine": round(dcos, 6),
                "designated_decision": "ABSTAIN" if dcos >= C_STAR else "KEEP",
                "max_neighbor": str(e.loc[im, "neighbor"]), "max_cosine": round(float(e.loc[im, "cosine"]), 6),
                "max_decision": "ABSTAIN" if e.loc[im, "cosine"] >= C_STAR else "KEEP",
                "rule_changes_call": (dcos >= C_STAR) != (float(e.loc[im, "cosine"]) >= C_STAR),
            })
    comp = pd.DataFrame(comp)
    comp.to_csv(OUT / "library_rule_comparison.csv", index=False)

    # threshold grid 0.75-0.85
    grid = []
    for lib, g in scan.groupby("library", sort=False):
        des = g[g["designated"]]
        dcos = float(des["cosine"].iloc[0]) if len(des) else np.nan
        mcos = float(g["cosine"].max())
        for c in [round(0.75 + 0.01 * i, 2) for i in range(11)]:
            grid.append({"library": lib, "cutoff": c,
                         "designated_cosine": round(dcos, 6), "designated_decision": "ABSTAIN" if dcos >= c else "KEEP",
                         "max_eligible_cosine": round(mcos, 6), "max_eligible_decision": "ABSTAIN" if mcos >= c else "KEEP"})
    pd.DataFrame(grid).to_csv(OUT / "threshold_grid.csv", index=False)

    # separability (R2-2)
    designated = scan[scan["designated"]][["library", "cosine", "decision"]].drop_duplicates("library").sort_values("cosine")
    keep = designated[designated["decision"] == "KEEP"]["cosine"]
    abst = designated[designated["decision"] == "ABSTAIN"]["cosine"]
    max_keep = float(keep.max()) if len(keep) else float("nan")
    min_abst = float(abst.min()) if len(abst) else float("nan")
    allc = scan["cosine"].to_numpy(float)
    sep = {
        "c_star": C_STAR, "n_libraries": int(designated.shape[0]),
        "designated_sorted": designated.round(6).to_dict("records"),
        "max_designated_KEEP": round(max_keep, 6), "min_designated_ABSTAIN": round(min_abst, 6),
        "separation_gap": [round(max_keep, 6), round(min_abst, 6)],
        "gap_width": round(min_abst - max_keep, 6),
        "c_star_inside_gap": bool(max_keep < C_STAR < min_abst),
        "designated_calls_stable_0p75_0p85": bool(max_keep < 0.75 and min_abst > 0.85),
        "eligible_pair_cosines": {"n": int(allc.size), "min": round(float(allc.min()), 6),
                                   "median": round(float(np.median(allc)), 6), "max": round(float(allc.max()), 6),
                                   "frac_ge_cstar": round(float(np.mean(allc >= C_STAR)), 6)},
    }
    (OUT / "cutoff_separability.json").write_text(json.dumps(sep, indent=2) + "\n")

    # clustered bootstrap (R2-4)
    rng = np.random.default_rng(0)
    libs = scan["library"].unique().tolist()
    per = {l: scan[scan["library"] == l]["cosine"].to_numpy(float) for l in libs}
    stats = []
    for _ in range(4000):
        pick = rng.choice(len(libs), len(libs), replace=True)
        pooled = np.concatenate([per[libs[i]] for i in pick])
        stats.append(float(np.mean(pooled >= C_STAR)))
    lo, hi = np.percentile(stats, [2.5, 97.5])
    boot = {"statistic": "fraction eligible pairs cosine>=c*", "c_star": C_STAR,
            "point_estimate": round(float(np.mean(allc >= C_STAR)), 6),
            "ci95": [round(float(lo), 6), round(float(hi), 6)], "n_bootstrap": 4000,
            "cluster_unit": "library", "n_clusters": len(libs)}
    (OUT / "clustered_bootstrap.json").write_text(json.dumps(boot, indent=2) + "\n")

    print("\n=== validation anchor ===")
    print(pd.DataFrame(anchor).to_string(index=False))
    print("\n=== rule comparison (floor=0) ===")
    print(comp[comp["floor"] == 0][["library", "designated_cosine", "designated_decision",
                                     "max_neighbor", "max_cosine", "max_decision", "rule_changes_call"]].to_string(index=False))
    print(f"\nseparability: max KEEP={sep['max_designated_KEEP']} min ABSTAIN={sep['min_designated_ABSTAIN']} "
          f"0.80 in gap={sep['c_star_inside_gap']} stable 0.75-0.85={sep['designated_calls_stable_0p75_0p85']}")
    print(f"clustered bootstrap frac>=0.80: {boot['point_estimate']} CI {boot['ci95']}")
    print("wrote ->", OUT)


if __name__ == "__main__":
    main()
