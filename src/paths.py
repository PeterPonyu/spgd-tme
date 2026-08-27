from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DECONV = Path("/home/zeyufu/Desktop/labs/active/deconv-lab")
CBC_MS = Path("/home/zeyufu/Desktop/labs/capsules/spgd-deconv/manuscript")
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
