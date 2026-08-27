# SPGD-TME infrastructure (audit 2026-08-26)

| Layer | Status |
|---|---|
| Window 1/2 entry scripts + `build_v4` wrap | **present; abstain now wired** |
| Trainer class (separate) | **none — scripts call `build_v4`** |
| Smoke (300-spot leftover) | **OK** (`run_spgd` + blend path) |
| INTERVAL bootstrap output | **complete** (B=1000 at t=0 plus full-n confirmation) |
| Post-sitting manuscript build | **local R + TeX only; no estimator fits** |
| GPU / AutoDL 4090 | **Do not book.** Scientific return $0 |
| This workbench as git repo | **stays local** (no public push of `spgd-tme`) |
| Public capture | `labs/active/SPGT-site/` → public `PeterPonyu/SPGT-site` |
| Related remotes | `deconv-lab` + `submission-capsules` private; CBC site is a sibling, not a merge |
| SSH nicknames for this paper | **0 / 3** — CPU stays on the laptop |

Do not push capsules. Do not `git init` this workbench. Public git lives only in `SPGT-site`.
