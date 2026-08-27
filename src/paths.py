import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# deconv-lab and the CBC capsule are siblings under labs/. Derive them from
# ROOT so no user's home directory is baked into the tree; SPGD_TME_LABS_ROOT
# relocates the whole set when the checkout is not under its usual parent.
LABS = Path(os.environ.get("SPGD_TME_LABS_ROOT", ROOT.parents[1]))
DECONV = LABS / "active/deconv-lab"
CBC_MS = LABS / "capsules/spgd-deconv/manuscript"
BCC_EXPORT = DECONV / "data/realgt3_benchmark/downloads/bcc_export"
REALGT4 = DECONV / "data/realgt4_benchmark"
LOCKS = ROOT / "locks"
PLOTDATA = ROOT / "data/plotdata"
DONOR_PAIRS = ROOT / "data/donor_pairs"
TMP = ROOT / "data/tmp"
BENCH = {
    "openst": DECONV / "data/openst_benchmark",
    "realgt": DECONV / "data/realgt_benchmark",
    "realgt2": DECONV / "data/realgt2_benchmark",
    "realgt3": DECONV / "data/realgt3_benchmark",
    "realgt4": REALGT4,
}
CBC_PORTAL_PDF = CBC_MS / "submission/portal_CBC/main.pdf"
CBC_CROSSDONOR = CBC_MS / "data/crossdonor.csv"
REALGT4_TRUTH = REALGT4 / "truth_proportions.csv"
