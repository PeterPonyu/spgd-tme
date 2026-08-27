# SPGD-TME 正面贡献稿 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 按正面贡献规格重写读者 PDF：四柱贡献句、盘上八项加厚写进图注与结果、参考文献扩到约 18–22 条、局限收成 Discussion 末段三句。

**Architecture:** 先加会失败的稿面契约测试，再改 `.bib` / 图注 / 八段正文。图件编号与包装画法不动。盘上没有八型 PCC 矩阵，F8 的类型加厚用已有 Type PCC 面，不新造数字。FLEX 行已在渲染器里 `rbind`，只核图、缺了才重画。

**Tech Stack:** pytest、`scripts/check_manuscript_shell.py`、natbib + `manuscript/references.bib`、latexmk、可选 `manuscript/scripts/R/render_disk_faces.R`（I/O 重画，不拟合）。

## Global Constraints

- 工作根：`/home/zeyufu/Desktop/labs/active/spgd-tme`。
- 规格：`/home/zeyufu/.cursor/projects/home-zeyufu-Desktop-labs/canvases/spgd-tme-contribution-spec.canvas.tsx`。
- 读者 PDF 主轴是做成了什么。局限只占 Discussion 最后一段，8–12 行，最多三句。
- 不重跑 sitting，不设 `SPGD_TME_COMPUTE`，不重建 nonempty donor 目录，不下载新队列，不发明数字。
- 正式图仍为 11 张（F1 协议 + F2–F11 数据）+ 3 表。`FIGURES.md` 必须保留子串 `10 figures + 3 tables`。
- 读者正文 / 图注 / 表禁止：`survival`、`biomarker`、`0.2034`、`0.1126`、`sha-256`、`sha256`、`crossdonor.csv`、`realgt`、`plotdata`、`run_tissue_name`、`/home/`、`desktop/labs`、`file://`。
- 局限第三句禁止写 `survival` / `biomarker`（会被 `BANNED` 打掉）。写 `Clinical outcome analysis lies outside this Methods object.`
- 盘上没有 per-type PCC 矩阵。禁止用估计值画「八型 × 四边」热图。F8A 已有 Type PCC 分面，那就是柱 B 的类型加厚。
- 第二面 KEEP 癌症队列不是本计划执行项。
- 不自动 `git commit`，除非用户本轮明确要求。
- 每任务结束后跑该任务写明的测试；全文结束跑 Task 9。

## Locked numbers (copy verbatim)

| Claim | Value |
|---|---|
| CosMx native cosine / call | 0.603666 KEEP |
| openST cosine / call | 0.972678 ABSTAIN |
| Xenium cosine / call | 0.980196 ABSTAIN |
| Xenium FLEX cosine / call | 0.987505 ABSTAIN |
| \(c^\star\) | 0.80 |
| CosMx KEEP window | \(t=0,0.1,0.2\) |
| Cells → eight-type cells | 232,802 → 216,949 |
| Typed cells A/B/C/D | 20,730 / 41,728 / 90,487 / 64,004 |
| Spots A_from_B / B_from_A / D_from_C | 1194 / 2020 / 3261 |
| D-from-C tumor / fibroblast / MoMacDC | 0.8425 → 0.4665 / 0.0881 → 0.2107 / 0.0070 → 0.1280 |
| D-from-C spots by condition | Baseline 977, Unwound 812, Wound 1472 |
| Cell-level D cancer / fibroblast / MoMacDC | 0.8863 → 0.5396 / 0.0607 → 0.1829 / 0.0057 → 0.1266 |
| Typed-cell cancer A / B | 0.4922 / 0.8277 |
| Full-n KEEP n / median / q / mean | 5686 / 0.6739 / 0.0510–0.9195 / 0.5428 |
| t=0 400-spot RMSE openST / Xenium / CosMx | 0.0757 / 0.1558 / 0.1542 |
| t=0 400-spot 95% CI | 0.0643–0.0874 / 0.1380–0.1724 / 0.1364–0.1729 |
| Full-n t=0 RMSE (n) | 0.0903 (6971) / 0.1613 (2864) / 0.1516 (5686) |
| Sweep openST / CosMx | 0.0757→0.3357 / 0.1542→0.6862 |
| Donor RMSE range / type PCC / spot PCC | 0.0659–0.1349 / 0.7034–0.7708 / 0.8030–0.9528 |
| B from A | RMSE 0.0659, type PCC 0.7484, spot PCC 0.9528 |
| C-from-D ledger | RMSE 0.1149, type PCC 0.7708, spot PCC 0.8773 |
| MoMacDC pair means | A_from_B 0.0803, B_from_A 0.0129, D_from_C 0.0636 |
| T2 openST seconds | self-gate 47.961, fit 8.374, Poisson 3.058, extract 0.858, refuse 0.001 |
| Builder floor | fifty reference cells per type |

## File map

| File | Role this plan |
|---|---|
| `tests/test_manuscript_shell.py` | 加贡献句 / 参考文献 / 局限槽测试 |
| `scripts/check_manuscript_shell.py` | 只在需要时加与测试相同的读者禁语；不改 11 图 / F11 / 泄漏锁 |
| `manuscript/references.bib` | 8 → 18–22 条 |
| `manuscript/captions/F1_protocol.tex` … `F11_floor.tex` | 第一句改成贡献句 |
| `manuscript/abstract.tex` `intro.tex` `materials.tex` `methods.tex` `results.tex` `discussion.tex` | 按四柱重写 |
| `FIGURES.md` | 主张句可改；必须保留 `10 figures + 3 tables` |
| `manuscript/scripts/R/render_disk_faces.R` | 仅当 F2/F10 看不见 FLEX 第四柱时才重画 |
| 不改 | `data/plotdata/*`、donor 目录、sitting 脚本、方程主体、T1–T3 数字 |

---

### Task 1: 先写会失败的稿面契约

**Files:**
- Modify: `tests/test_manuscript_shell.py`
- Test: `tests/test_manuscript_shell.py`

**Interfaces:**
- Consumes: 现有 `test_manuscript_shell_contract`、`test_reader_text_has_no_internal_ledger`、`test_f11_caption_only_claims_plotted_mean_and_floor_metadata`、`test_references_bib_exists`
- Produces: `CAPTION_LEADS`、`REQUIRED_BIB_KEYS`、`DEFENSIVE_PHRASES`、`test_caption_leads_are_contribution_first`、`test_bib_has_contribution_neighborhood`、`test_intro_cites_method_neighborhood`、`test_abstract_opens_with_operators`、`test_discussion_ends_with_short_scope`、`test_reader_body_has_no_defensive_voice`

- [ ] **Step 1: 把下列测试追加到 `tests/test_manuscript_shell.py` 末尾**

```python
CAPTION_LEADS = {
    "F1_protocol.tex": "Two locked operators compute mixed-spot TME composition and decide when the tumor column is reportable.",
    "F2_spatial_maps.tex": "Four-patient CosMx basal-cell carcinoma is the mixed-spot TME object.",
    "F3_cohort.tex": "Four-patient cell-level fields give a clinically separable tissue.",
    "F4_ulcerated.tex": "Patient A is more stromal and Patient B is tumor-rich on the ulcerated-nodular pair.",
    "F5_wound.tex": "Tumor fraction falls and stromal and myeloid occupancy rise along the wound axis.",
    "F6_keep.tex": "The protocol reports CosMx tumor coordinates and places them beside locked tumor truth.",
    "F7_dose.tex": "One frozen cosine produces a platform-dependent KEEP window.",
    "F8_donor.tex": "Directed donor transfer recovers composition across patients.",
    "F9_myeloid.tex": "MoMacDC is an occupancy axis on the computed pairs.",
    "F10_eval.tex": "The evaluation board collects the interval, the full-n confirmation, donor RMSE, and the timed pass.",
    "F11_floor.tex": "Mean truth fraction for each of eight shared types sits on a builder floor of fifty reference cells per type.",
}

REQUIRED_BIB_KEYS = (
    "Lopez2022",
    "Ma2022",
    "Biancalani2021",
    "Danaher2022",
    "Li2022integrate",
    "Sangaram2024",
    "Dvorak1986",
    "Gavish2023",
)

DEFENSIVE_PHRASES = (
    "we did not",
    "we do not evaluate",
    "was not evaluated",
    "not evaluated",
    "not reported",
    "we lack",
    "highest error",
    "incomplete",
    "unavailable",
    "only one keep",
    "we have not",
)


def test_caption_leads_are_contribution_first():
    for name, lead in CAPTION_LEADS.items():
        blob = (ROOT / "manuscript/captions" / name).read_text().strip()
        assert blob.startswith(lead), name


def test_bib_has_contribution_neighborhood():
    bib = (ROOT / "manuscript/references.bib").read_text()
    for key in REQUIRED_BIB_KEYS:
        assert f"@{key}" in bib or f"{{{key}," in bib, key


def test_intro_cites_method_neighborhood():
    intro = (ROOT / "manuscript/intro.tex").read_text()
    assert "Lopez2022" in intro or "Ma2022" in intro
    assert "Danaher2022" in intro or "Li2022integrate" in intro
    assert "Dvorak1986" in intro or "Gavish2023" in intro


def test_abstract_opens_with_operators():
    first = (ROOT / "manuscript/abstract.tex").read_text().strip().split(".")[0]
    assert "two locked operators" in first.lower()


def test_discussion_ends_with_short_scope():
    raw = (ROOT / "manuscript/discussion.tex").read_text()
    paras = [p.strip() for p in raw.split("\n\n") if p.strip()]
    last = paras[-1]
    n_lines = last.count("\n") + 1
    assert n_lines <= 12
    assert last.count(".") <= 4
    low = last.lower()
    assert "cosmx" in low
    assert "c-from-d" in low or "materials ledger" in low
    assert "methods object" in low
    body_before = "\n\n".join(paras[:-1]).lower()
    for tok in DEFENSIVE_PHRASES:
        assert tok not in body_before, tok


def test_reader_body_has_no_defensive_voice():
    names = [
        "abstract.tex",
        "intro.tex",
        "materials.tex",
        "methods.tex",
        "results.tex",
    ]
    blob = "\n".join((ROOT / "manuscript" / n).read_text().lower() for n in names)
    for name in CAPTION_LEADS:
        blob += "\n" + (ROOT / "manuscript/captions" / name).read_text().lower()
    for tok in DEFENSIVE_PHRASES:
        assert tok not in blob, tok
```

- [ ] **Step 2: 跑这些新测试，确认现在失败**

Run:

```bash
cd /home/zeyufu/Desktop/labs/active/spgd-tme
conda run -n dl pytest tests/test_manuscript_shell.py::test_caption_leads_are_contribution_first tests/test_manuscript_shell.py::test_bib_has_contribution_neighborhood tests/test_manuscript_shell.py::test_intro_cites_method_neighborhood tests/test_manuscript_shell.py::test_abstract_opens_with_operators tests/test_manuscript_shell.py::test_discussion_ends_with_short_scope -q
```

Expected: FAIL（现稿图注第一句、bib 键、摘要首句、Discussion 末段都不符合）。

- [ ] **Step 3: 确认旧契约仍然通过**

Run:

```bash
cd /home/zeyufu/Desktop/labs/active/spgd-tme
conda run -n dl pytest tests/test_manuscript_shell.py::test_manuscript_shell_contract tests/test_manuscript_shell.py::test_f11_caption_only_claims_plotted_mean_and_floor_metadata tests/test_manuscript_shell.py::test_reader_text_has_no_internal_ledger -q
```

Expected: PASS

---

### Task 2: 扩 `references.bib`

**Files:**
- Modify: `manuscript/references.bib`
- Test: `tests/test_manuscript_shell.py::test_bib_has_contribution_neighborhood`

**Interfaces:**
- Consumes: 现有 `Yerly2022`、`Yerly2025preprint`、`Andreatta2024zenodo`、`Schott2024`、`Janesick2023`、`He2022`、`Cable2022`、`Kleshchevnikov2022`
- Produces: 下列键，正文用 `\cite{Key}`

- [ ] **Step 1: 把下列条目追加到 `manuscript/references.bib` 末尾。DOI 与检索不一致则删该条，不编 DOI。**

```bibtex
@article{Lopez2022,
  author  = {Lopez, Romain and Li, Baohong and Keren-Shaul, Hadas and Boyeau, Pierre and Kedmi, Merav and Pilzer, David and Jelinski, Adam and Yofe, Ido and David, Eyal and Wagner, Allon and Ergen, Can and Addadi, Yoseph and Golani, Ofra and Ronchese, Franca and Jordan, Martin I. and Amit, Ido and Yosef, Nir},
  title   = {{DestVI} identifies continuums of cell types in spatial transcriptomics data},
  journal = {Nature Biotechnology},
  year    = {2022},
  volume  = {40},
  pages   = {1360--1369},
  doi     = {10.1038/s41587-022-01272-8}
}

@article{Ma2022,
  author  = {Ma, Ying and Zhou, Xiang},
  title   = {Spatially informed cell-type deconvolution for spatial transcriptomics},
  journal = {Nature Biotechnology},
  year    = {2022},
  volume  = {40},
  pages   = {1349--1359},
  doi     = {10.1038/s41587-022-01273-7}
}

@article{Biancalani2021,
  author  = {Biancalani, Tommaso and Scalia, Gabriele and Buffoni, Lorenzo and Avasthi, Raghav and Lu, Ziqing and Sanger, Aman and Tokcan, Neriman and Vanderburg, Charles R. and Segerstolpe, {\AA}sa and Zhang, Meng and Avraham-Davidi, Inbal and Vickovic, Sanja and Nitzan, Mor and Ma, Sai and Price, Andrew and Kumar, Sarah and Montgomery, Charles and Rozenblatt-Rosen, Orit and Xavier, Ramnik J. and Regev, Aviv},
  title   = {Deep learning and alignment of spatially resolved single-cell transcriptomes with {Tangram}},
  journal = {Nature Methods},
  year    = {2021},
  volume  = {18},
  pages   = {1352--1362},
  doi     = {10.1038/s41592-021-01264-7}
}

@article{Danaher2022,
  author  = {Danaher, Patrick and Kim, Youngmi and Nelson, Ben and Griswold, Maddy and Yang, Zhi and Piazza, Erin and Beechem, Joseph M.},
  title   = {Advances in mixed cell deconvolution enable quantification of cell types in spatial transcriptomic data},
  journal = {Nature Communications},
  year    = {2022},
  volume  = {13},
  pages   = {385},
  doi     = {10.1038/s41467-022-28020-5}
}

@article{Li2022integrate,
  author  = {Li, Bin and Zhang, Wenjing and Guo, Chuang and Wu, Hao and Li, Lei and Chen, Jiaqi and Wei, Chen and He, Qingshu and Zhang, Suoqin and Chen, Yixin and others},
  title   = {Benchmarking spatial and single-cell transcriptomics integration methods for transcript distribution prediction and cell type deconvolution},
  journal = {Nature Methods},
  year    = {2022},
  doi     = {10.1038/s41592-022-01480-9}
}

@article{Sangaram2024,
  author  = {Sang-aram, Chananchida and Browaeys, Robin and Seurinck, Ruth and Saeys, Yvan},
  title   = {Spotless, a reproducible pipeline for benchmarking cell type deconvolution in spatial transcriptomics},
  journal = {eLife},
  year    = {2024},
  doi     = {10.7554/eLife.88431}
}

@article{Dvorak1986,
  author  = {Dvorak, Harold F.},
  title   = {Tumors: wounds that do not heal. Similarities between tumor stroma generation and wound healing},
  journal = {The New England Journal of Medicine},
  year    = {1986},
  volume  = {315},
  pages   = {1650--1659},
  doi     = {10.1056/NEJM198612253152606}
}

@article{Gavish2023,
  author  = {Gavish, Avishai and Tyler, Menachem and Greenwald, Adi C. and Hoefflin, Rouven and Simkin, Dor and Tschernichovsky, Roi and Galili Darnell, Noam and Somech, Einav and Baron, Chaya and Barbolin, Tamar and Tsabar, Michael and Kovarsky, David and Barrett, Thomas and Gonzalez Castro, L. Nicolas and Halder, Daniel and Berezovskaya, Anna and Greenwald, Orr and De Vries, Galina and Sharif-Chulpon, Hila and Raviv, Adva and Nasrollahi, Hadas and Ardalan, Adi and Tirosh, Itay},
  title   = {Hallmarks of transcriptional programmes in cancer},
  journal = {Nature},
  year    = {2023},
  doi     = {10.1038/s41586-023-06130-4}
}

@article{Andersson2020,
  author  = {Andersson, Alma and Bergenstr{\aa}hle, Joseph and Asp, Maja and Bergenstr{\aa}hle, Ludvig and Jurek, Alexander and Fern{\'a}ndez Navarro, Joakim and Lundeberg, Joakim},
  title   = {Single-cell and spatial transcriptomics enables probabilistic inference of cell type topography},
  journal = {Communications Biology},
  year    = {2020},
  volume  = {3},
  pages   = {565},
  doi     = {10.1038/s42003-020-01247-y}
}

@article{ElosuaBayes2021,
  author  = {Elosua-Bayes, Marc and Nieto, Paula and Mereu, Elisabetta and Gut, Ivo and Heyn, Holger},
  title   = {{SPOTlight}: seeded {NMF} regression to deconvolute spatial transcriptomics spots with single-cell transcriptomes},
  journal = {Nucleic Acids Research},
  year    = {2021},
  volume  = {49},
  pages   = {e50},
  doi     = {10.1093/nar/gkab147}
}

@article{Dong2021,
  author  = {Dong, Rui and Yuan, Guo-Cheng},
  title   = {{SpatialDWLS}: accurate deconvolution of spatial transcriptomic data},
  journal = {Genome Biology},
  year    = {2021},
  volume  = {22},
  pages   = {145},
  doi     = {10.1186/s13059-021-02362-7}
}
```

- [ ] **Step 2: 核 DOI 与作者行。以出版社页为准覆盖 `Li2022integrate`、`Gavish2023`、`Lopez2022`、`Sangaram2024` 的作者名单；对不上的字段改成出版社页，不要改 DOI 凑数。任一条 DOI 失效则删除该条。`REQUIRED_BIB_KEYS` 八条必须留下。**

- [ ] **Step 3: 跑 bib 测试**

Run:

```bash
cd /home/zeyufu/Desktop/labs/active/spgd-tme
conda run -n dl pytest tests/test_manuscript_shell.py::test_bib_has_contribution_neighborhood tests/test_manuscript_shell.py::test_references_bib_exists -q
```

Expected: PASS

---

### Task 3: 图注第一句改成贡献句

**Files:**
- Modify: `manuscript/captions/F1_protocol.tex`
- Modify: `manuscript/captions/F2_spatial_maps.tex`
- Modify: `manuscript/captions/F3_cohort.tex`
- Modify: `manuscript/captions/F4_ulcerated.tex`
- Modify: `manuscript/captions/F5_wound.tex`
- Modify: `manuscript/captions/F6_keep.tex`
- Modify: `manuscript/captions/F7_dose.tex`
- Modify: `manuscript/captions/F8_donor.tex`
- Modify: `manuscript/captions/F9_myeloid.tex`
- Modify: `manuscript/captions/F10_eval.tex`
- Modify: `manuscript/captions/F11_floor.tex`
- Modify: `manuscript/captions/T1_materials.tex`
- Modify: `manuscript/captions/T3_donor_matrix.tex`
- Modify: `FIGURES.md`（只改 Role 列措辞；保留 `10 figures + 3 tables`）

**Interfaces:**
- Consumes: Task 1 `CAPTION_LEADS`
- Produces: 每张正式图注以贡献句开头，后面仍写 A–F 面

- [ ] **Step 1: 用下列全文覆盖十一张正式图注（第一句必须与测试逐字相同）**

`F1_protocol.tex`:

```tex
Two locked operators compute mixed-spot TME composition and decide when the tumor column is reportable. (A)~Reference, specificity weights, platform self-gate, and collinearity refusal. (B)~Weighted signatures and the simplex composition. (C)~Refusal at \(c^\star=0.80\). (D)~Patient-identity donor split. (E)~Evaluation metrics. (F)~The six operator steps.
```

`F2_spatial_maps.tex`:

```tex
Four-patient CosMx basal-cell carcinoma is the mixed-spot TME object. (A)~Spot counts on the three computed pairs. (B)~Mean type mass. (C)~Locked malignant--neighbor cosine versus \(c^\star=0.80\), including the orthogonal Xenium FLEX reference. (D)~Directed donor edges. (E)~Native KEEP and ABSTAIN calls on openST, Xenium, Xenium FLEX, and CosMx. (F)~Approximate mixed-spot diameter.
```

`F3_cohort.tex`:

```tex
Four-patient cell-level fields give a clinically separable tissue. (A--D)~Cancer cells inside complete fields of view for Patients A--D. (E)~Typed-cell cancer, fibroblast, and MoMacDC fractions by patient and condition. (F)~Median cells per mixed spot.
```

`F4_ulcerated.tex`:

```tex
Patient A is more stromal and Patient B is tumor-rich on the ulcerated-nodular pair. (A)~Patient A field of view colored by type. (B)~Cancer cells in the same field. (C)~Fibroblasts in the same field. (D)~Patient B cancer field. (E)~A-from-B mixed-spot tumor truth. (F)~B-from-A mixed-spot tumor truth. Bars are 500 µm.
```

`F5_wound.tex`:

```tex
Tumor fraction falls and stromal and myeloid occupancy rise along the wound axis. (A)~Baseline cancer field. (B)~Unwound cancer field. (C)~Wound cancer field. (D)~D-from-C mixed-spot tumor truth. (E)~D-from-C fibroblast truth. (F)~Mean truth fraction by wound condition. Each spot carries the majority condition of its pooled Patient D cells.
```

`F6_keep.tex`:

```tex
The protocol reports CosMx tumor coordinates and places them beside locked tumor truth. (A)~Cancer cells in Patient C fields of view. (B)~Locked tumor truth on a dense CosMx window. (C)~Estimated tumor fraction on the same window. (D)~A tighter window of the estimate. (E)~Native cosine versus \(c^\star=0.80\). (F)~KEEP and ABSTAIN calls. The CosMx cosine is 0.603666.
```

`F7_dose.tex`:

```tex
One frozen cosine produces a platform-dependent KEEP window. (A--C)~Ungated tumor RMSE as the malignant signature is interpolated toward its neighbor on openST, Xenium, and CosMx. (D--F)~The same sweep with the refusal overlay: CosMx remains KEEP at \(t=0,0.1,0.2\).
```

`F8_donor.tex`:

```tex
Directed donor transfer recovers composition across patients. (A)~Overall RMSE, tumor RMSE, type PCC, and spot PCC. (B)~Overall RMSE on the computed edges. (C)~Spot-level PCC. (D--F)~Tumor-truth geography on B from A, D from C, and A from B. Type PCC on the computed edges is 0.7034--0.7708. The materials ledger records the C-from-D composition.
```

`F9_myeloid.tex`:

```tex
MoMacDC is an occupancy axis on the computed pairs. (A)~MoMacDC mean truth on the three computed pairs. (B)~A-from-B MoMacDC field. (C)~D-from-C MoMacDC field. (D)~Patient A myeloid cells in one field of view. (E)~Patient D wound-field myeloid cells. (F)~A-from-B fibroblast field.
```

`F10_eval.tex`:

```tex
The evaluation board collects the interval, the full-n confirmation, donor RMSE, and the timed pass. (A)~Tumor RMSE at \(t=0\) with a \(B=1000\) interval. (B)~Full-\(n\) tumor RMSE. (C)~Donor-transfer RMSE. (D)~Operator wall-clock on one openST pass. (E)~Native cosine and KEEP/ABSTAIN, including Xenium FLEX. (F)~Spot counts on the computed pairs.
```

`F11_floor.tex`:

```tex
Mean truth fraction for each of eight shared types sits on a builder floor of fifty reference cells per type. (A)~Mean truth fraction for each of eight shared types and each pair, with a builder floor of fifty reference cells per type. (B)~Wound-axis occupancy. (C)~MoMacDC means. (D--F)~Tumor-truth fields on A from B, B from A, and D from C.
```

- [ ] **Step 2: 表注改成贡献句，不改表内数字**

`T1_materials.tex`:

```tex
Materials for the CosMx four-patient export, the evaluated references, the orthogonal Xenium FLEX reference, the donor-transfer composition row, and the frozen type-pair and \(c^\star\) locks.
```

`T3_donor_matrix.tex`:

```tex
Directed Patient\_ID transfer recovers composition on three computed edges; the C-from-D row is the materials-ledger composition that closes the four-edge matrix.
```

- [ ] **Step 3: 扫全部 `manuscript/captions/*.tex`，确认没有 `DEFENSIVE_PHRASES` 和 `READER_LEAKS`。旧残留图注（`F4_keep.tex`、`F9_wound.tex` 等）不进 PDF，但泄漏测试会读到它们；只清泄漏，不把它们写成正式图。**

- [ ] **Step 4: 跑图注测试**

Run:

```bash
cd /home/zeyufu/Desktop/labs/active/spgd-tme
conda run -n dl pytest tests/test_manuscript_shell.py::test_caption_leads_are_contribution_first tests/test_manuscript_shell.py::test_f11_caption_only_claims_plotted_mean_and_floor_metadata tests/test_manuscript_shell.py::test_reader_text_has_no_internal_ledger -q
```

Expected: PASS

---

### Task 4: 摘要与引言按贡献命题重写

**Files:**
- Modify: `manuscript/abstract.tex`
- Modify: `manuscript/intro.tex`

**Interfaces:**
- Consumes: Task 2 的 cite 键；Locked numbers
- Produces: 摘要首句含 `two locked operators`；引言引用方法邻域与 BCC 生物学

- [ ] **Step 1: 用下列摘要覆盖 `abstract.tex`（可微调连接词，不可改数字，不可删首句里的 `two locked operators`）**

```tex
This Methods article adds two locked operators to a training-free composition estimator: a collinearity KEEP/ABSTAIN gate and a Patient\_ID donor split. A frozen cosine \(c^\star=0.80\) reports a tumor fraction when the locked malignant column stays separable from its neighbor, and continues the remaining types on the simplex when the columns meet the gate. The same rule returns KEEP on CosMx basal-cell carcinoma (cosine \(0.603666\)) and ABSTAIN on HNSCC openST (\(0.972678\)), breast Xenium (\(0.980196\)), and an orthogonal Xenium FLEX reference (\(0.987505\)). On four-patient CosMx, mixed-spot occupancy tracks the cohort labels: ulcerated-nodular Patient B is tumor-rich relative to Patient A, and the wound axis on D-from-C drops tumor fraction from \(0.8425\) to \(0.4665\) while fibroblast and MoMacDC rise. Directed transfer recovers composition across patients, most tightly on B from A (RMSE \(0.0659\), spot-level PCC \(0.9528\)).
```

- [ ] **Step 2: 重写 `intro.tex` 为五段，顺序固定**

1. 对象：混合斑 TME 组成是可读量。引用 `Cable2022,Kleshchevnikov2022,Danaher2022`。点名 openST / Xenium / CosMx 平台 `Schott2024,Janesick2023,He2022`。
2. 邻域：RCTD、cell2location、DestVI、CARD、Tangram 恢复组成 `Cable2022,Kleshchevnikov2022,Lopez2022,Ma2022,Biancalani2021`。独立地图把 RCTD / cell2location 放在组成前排 `Li2022integrate,Sangaram2024`。本协议在同一对象上加可报告性规则与供体分裂。
3. 算子：\(c^\star=0.80\) KEEP/ABSTAIN；四平台原生调用（含 FLEX）。不要写「我们只做了一面 KEEP」。
4. 生物学：伤口–肿瘤经典与 BCC 队列 `Dvorak1986,Yerly2022,Yerly2025preprint,Gavish2023,Andreatta2024zenodo`。A/B 溃疡结节，C/D 伤口轴。供体键 `Patient_ID`。
5. 贡献收束（可沿用规格一句话）：232,802 → 216,949 细胞；1194 / 2020 / 3261 斑；两道算子在四患者 CosMx 与两套锁定平台上的示范。

禁止引言出现 `DEFENSIVE_PHRASES`。不要用「when tumor mass can migrate」开篇占满第一段。

- [ ] **Step 3: 跑摘要 / 引言测试**

Run:

```bash
cd /home/zeyufu/Desktop/labs/active/spgd-tme
conda run -n dl pytest tests/test_manuscript_shell.py::test_abstract_opens_with_operators tests/test_manuscript_shell.py::test_intro_cites_method_neighborhood tests/test_manuscript_shell.py::test_reader_body_has_no_defensive_voice -q
```

Expected: `test_reader_body_has_no_defensive_voice` 可能仍因结果 / 图注以外的正文失败；摘要与引言两条必须 PASS。

---

### Task 5: Materials / Methods 只加邻域引用，不改方程

**Files:**
- Modify: `manuscript/materials.tex`
- Modify: `manuscript/methods.tex`（只改开篇段与 cite，不动方程块）

**Interfaces:**
- Consumes: Task 2 键；现有方程与锁定数字
- Produces: 材料段把 FLEX 写成正交加厚；Methods 开篇把 RCTD / cell2location / DestVI / CARD 写成邻域

- [ ] **Step 1: `materials.tex` 第三段三底物句改为（数字不动）**

现有三底物句后加一句，不得引入内部文件名：

```tex
An orthogonal Xenium FLEX reference on the same 2864 spots returns cosine \(0.987505\) and ABSTAIN, so the frozen rule is read on a second library for that malignant--neighbor pair~\cite{Janesick2023}.
```

C-from-D 句保持「materials ledger」表述，不要写 SHA / `crossdonor.csv`。

- [ ] **Step 2: `methods.tex` 第一段换成**

```tex
The estimator is the locked SPGD stack plus two operators: a collinearity refusal and a patient-identity donor split (Figure~\ref{fig:protocol}). Related mixed-spot readers recover composition, including RCTD, cell2location, DestVI, and CARD~\cite{Cable2022,Kleshchevnikov2022,Lopez2022,Ma2022}. This protocol adds an explicit rule for when the malignant coordinate is reportable.
```

后面 `\paragraph{Signatures...}` 到 Metrics 一段不改公式、不改数字。DestVI 只出现在 cite，正文不出现 `0.2034` 或 `0.1126`。

- [ ] **Step 3: 跑壳 + 禁语**

Run:

```bash
cd /home/zeyufu/Desktop/labs/active/spgd-tme
conda run -n dl pytest tests/test_manuscript_shell.py::test_manuscript_shell_contract tests/test_manuscript_shell.py::test_reader_text_has_no_internal_ledger -q
```

Expected: PASS

---

### Task 6: Results 按四柱写贡献句，图序不变

**Files:**
- Modify: `manuscript/results.tex`

**Interfaces:**
- Consumes: 现有 `\includegraphics` 行与 `\label`；Locked numbers；Task 3 图注
- Produces: 每个 figure 前的段落以贡献句开头；八项加厚都有着落

- [ ] **Step 1: 重写 `results.tex` 的文字段。保留全部 `figure` / `table` 环境和 `\includegraphics` 行，包括**

```tex
\includegraphics[width=\textwidth]{figs/rendered/F2_hero.pdf}
\includegraphics[width=\textwidth]{figs/rendered/F3_cohort.pdf}
\includegraphics[width=0.92\textwidth]{figs/rendered/F11_floor.pdf}
```

以及 `fig:hero` … `fig:floor`、`tab:donor`。` \begin{figure}` 仍为 11（F1 在 `main.tex`）。

各段开句（数字必须用 Locked numbers 表）：

1. F2 前：四患者 CosMx 是混合斑 TME 对象。写出 232,802 / 216,949、三对斑数、四次原生调用（含 FLEX 0.987505 ABSTAIN）、账本 C-from-D。
2. F3 前：细胞场给出临床可分组织。A/B 肿瘤分数 0.4922 / 0.8277；Patient D 细胞级伤口轴。
3. F4 前：溃疡结节 A 间质、B 富肿瘤在组织上可读。
4. F5 前：伤口轴肿瘤 0.8425→0.4665，成纤维与 MoMacDC 上升；3261 斑条件计数。
5. F6 前：协议在 CosMx 上报告肿瘤坐标。全 n 5686，中位 0.6739，与真值 5686/5686 对齐。
6. F7 前：同一 \(c^\star\) 给出平台响应与 KEEP 窗。400 斑 CI、全 n 复验、CosMx \(t=0,0.1,0.2\) KEEP。
7. F8 + T3 前：跨患者组成可恢复。RMSE 0.0659–0.1349；最强边 B from A；Type PCC 0.7034–0.7708 就是类型加厚（不要声称画了八型热图）。
8. F9 前：MoMacDC 是占用轴。0.0803 / 0.0129 / 0.0636。
9. F10 前：评价板一次收齐区间、全 n、供体 RMSE、计时。
10. F11 前：八型占用落在五十参考细胞地板上。必须出现 `mean truth fraction` 的语义（图注已锁）。

- [ ] **Step 2: 对照规格八项加厚，在 `results.tex` 里必须能搜到**

| 加厚 | 正文必须出现的字面 |
|---|---|
| FLEX 正交调用 | `0.987505` 与 `FLEX` 与 `ABSTAIN` |
| 剂量 KEEP 窗 | `t=0,0.1,0.2` 或 `$t=0,0.1,0.2$` |
| 全 n t=0 复验 | `0.0903`、`0.1613`、`0.1516` 与三个 n |
| 供体类型 PCC | `0.7034` 与 `0.7708` |
| 最强边 | `0.0659` 与 `0.9528` |
| 三尺度伤口轴 | 细胞级 `0.8863` 与斑点级 `0.8425` |
| MoMacDC 轴 | `0.0803` |
| KEEP 真值对照 | `5686` 与 `0.6739` |

- [ ] **Step 3: 跑结果相关测试**

Run:

```bash
cd /home/zeyufu/Desktop/labs/active/spgd-tme
conda run -n dl pytest tests/test_manuscript_shell.py::test_required_figures_are_directly_included tests/test_manuscript_shell.py::test_reader_body_has_no_defensive_voice tests/test_manuscript_shell.py::test_manuscript_shell_contract -q
```

Expected: PASS

---

### Task 7: Discussion 贡献 + 邻域 + 三句局限

**Files:**
- Modify: `manuscript/discussion.tex`

**Interfaces:**
- Consumes: 四柱数字；Task 2 cite 键
- Produces: 五段贡献 / 邻域 + 最后一段三句局限

- [ ] **Step 1: 用下列六段覆盖 `discussion.tex`。前五段与末段之间必须空一行，这样 `split("\n\n")` 的最后一段才是局限。**

```tex
The protocol reports a tumor fraction when CosMx signatures remain separable, and writes ABSTAIN when openST, Xenium, or the orthogonal Xenium FLEX library meet the frozen cosine \(c^\star=0.80\) (Figure~\ref{fig:protocol}; Figure~\ref{fig:dose}). Those native calls are CosMx KEEP at cosine \(0.603666\) and three ABSTAIN calls at \(0.972678\), \(0.980196\), and \(0.987505\). CosMx remains KEEP at interpolation fractions \(t=0,0.1,0.2\). A tumor coordinate is therefore a KEEP/ABSTAIN decision, and the remaining types continue on the simplex in either case.

On four-patient CosMx basal-cell carcinoma, cell-level fields and mixed-spot occupancy track the cohort labels (Figures~\ref{fig:hero}--\ref{fig:floor}). Ulcerated-nodular Patient B is tumor-rich relative to the more stromal Patient A. The wound time course on Patients C and D is a drop in tumor fraction with a rise in fibroblast and MoMacDC, recovered on D-from-C mixed spots (Baseline tumor \(0.8425\) to Wound \(0.4665\); MoMacDC \(0.0070\) to \(0.1280\)) and in the same direction on typed Patient D cells.

Donor transfer recovers mixed-spot truth across patients (Figure~\ref{fig:donor}; Table~\ref{tab:donor}). Overall RMSE on the computed edges is \(0.0659\)--\(0.1349\), type-level Pearson correlation is \(0.7034\)--\(0.7708\), and spot-level Pearson correlation reaches \(0.9528\) on B from A. D from C carries the wound axis. The C-from-D row in the materials ledger completes the four-edge matrix.

The full-\(n\) CosMx KEEP map writes that reportable tumor column on 5686 spots (median \(0.6739\)) beside locked tumor truth (Figure~\ref{fig:keep}). The evaluation board collects the \(t=0\) interval, the full-\(n\) confirmation, donor RMSE, and the timed openST pass (Figure~\ref{fig:eval}; Table~\ref{tab:timing}).

Related mixed-spot readers recover composition~\cite{Cable2022,Kleshchevnikov2022,Lopez2022,Ma2022,Biancalani2021,Danaher2022}. Independent maps place RCTD and cell2location among the leading composition estimators~\cite{Li2022integrate,Sangaram2024}. This companion keeps those parent constants locked and adds a reportability gate plus a Patient\_ID split, demonstrated on the CosMx wound and ulcerated-nodular axes~\cite{Yerly2022,Yerly2025preprint,Dvorak1986}.

This sitting reports the KEEP cancer demonstration on CosMx BCC; openST and Xenium display the ABSTAIN face of the same rule. The C-from-D edge is the materials-ledger composition that closes the four-edge matrix. Clinical outcome analysis lies outside this Methods object.
```

- [ ] **Step 2: 确认末段没有 `survival` / `biomarker` / `we did not` / `highest error`。**

- [ ] **Step 3: 跑 Discussion 测试**

Run:

```bash
cd /home/zeyufu/Desktop/labs/active/spgd-tme
conda run -n dl pytest tests/test_manuscript_shell.py::test_discussion_ends_with_short_scope tests/test_manuscript_shell.py::test_manuscript_shell_contract -q
```

Expected: PASS

---

### Task 8: 核 FLEX 是否已在 F2 / F10，缺了才重画

**Files:**
- Read: `manuscript/scripts/R/render_disk_faces.R`（约 30–34、384–390 行）
- Modify only if needed: `manuscript/scripts/R/render_disk_faces.R`
- Produce only if needed: `manuscript/figs/rendered/F2_hero.pdf`、`F10_eval.pdf`

**Interfaces:**
- Consumes: `F2_native_refuse.csv` + `F2_realgt2_cosine.csv`；`pretty_substrate()` 已把 `realgt2` 映成 `Xenium FLEX`
- Produces: F2 C/E 与 F10 E 可见四条调用（openST / Xenium / Xenium FLEX / CosMx）

- [ ] **Step 1: 确认渲染器已经**

```r
orth <- read.csv(file.path(plotdir, "F2_realgt2_cosine.csv"), ...)
refuse <- rbind(refuse, orth)
refuse$substrate <- factor(pretty_substrate(refuse$substrate), levels = refuse_levels)
```

且 `refuse_levels <- c("openST", "Xenium", "Xenium FLEX", "CosMx")`。

- [ ] **Step 2: 目视 `manuscript/figs/rendered/F2_hero.pdf` 的 C/E 与 `F10_eval.pdf` 的 E。若已有四柱，跳过 Step 3。**

- [ ] **Step 3: 仅当缺 FLEX 柱时，从工作根重画（不设 `SPGD_TME_COMPUTE`）**

```bash
cd /home/zeyufu/Desktop/labs/active/spgd-tme
Rscript manuscript/scripts/R/render_disk_faces.R
```

Expected: 重写 rendered PDF；不写 `data/plotdata`；不跑 `14_run_sitting.py`。

- [ ] **Step 4: 不要为「八型热图」改 F8。F8A 的 Type PCC 分面已是柱 B 加厚。**

---

### Task 9: 全量核验

**Files:**
- Test: `tests/`（忽略 `tests/compute`）
- Produce: `manuscript/main.pdf`

- [ ] **Step 1: pytest**

```bash
cd /home/zeyufu/Desktop/labs/active/spgd-tme
conda run -n dl pytest tests -q --ignore=tests/compute
```

Expected: 全部 PASS，包含 `MANUSCRIPT_SHELL_OK`。

- [ ] **Step 2: 编译**

```bash
cd /home/zeyufu/Desktop/labs/active/spgd-tme/manuscript
latexmk -pdf -interaction=nonstopmode main.tex
```

Expected: `main.pdf` 生成；bibliography 出现 Lopez / Ma / Danaher / Dvorak 等。

- [ ] **Step 3: PDF 抽字泄漏扫描**

```bash
pdftotext -layout /home/zeyufu/Desktop/labs/active/spgd-tme/manuscript/main.pdf - \
  | rg -i 'sha-256|sha256|crossdonor|realgt|plotdata|/home/|0\.2034|0\.1126|survival|biomarker|we did not|highest error'
```

Expected: 无匹配。

- [ ] **Step 4: 人工读四句**

打开 `manuscript/main.pdf`，确认摘要首句是两道算子；Introduction 把 RCTD / DestVI / CARD 写成邻域而不是「我们没比」；Results 伤口轴与 B from A 是成就句；Discussion 最后一段只有三句。

---

## Self-review against the spec

| 规格块 | 对应任务 |
|---|---|
| 0. 一句话贡献 | Task 4 摘要 / 引言第 5 段 |
| 1. 四根贡献柱 | Task 6 结果开句 + Task 7 前四段 |
| 2. 八个盘上加厚 | Task 3 图注 + Task 6 检索表；FLEX 核图在 Task 8；八型热图改为 Type PCC，不造矩阵 |
| 3. 参考文献 8→18–22 | Task 2 + Task 4/5/7 的 `\cite` |
| 4. 语气与篇幅 / 局限 ≤12 行 | Task 1 测试 + Task 7 末段；`survival`/`biomarker` 不进局限 |
| 5. 图件主张句 | Task 3 `CAPTION_LEADS` |
| 6. 不改稿以外的门 | Global Constraints；本计划是执行稿面，不是新 sitting |

无 TBD。无「类似 Task N」。无自动 commit。
