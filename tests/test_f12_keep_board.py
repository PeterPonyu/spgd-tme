from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def test_f12_keep_board_locked_calls():
    cosine = pd.read_csv(ROOT / "data/plotdata/F12_keep_cosine.csv")
    donor = pd.read_csv(ROOT / "data/plotdata/F12_donor_rmse.csv")
    keep = set(cosine.loc[cosine.decision == "KEEP", "substrate"])
    abstain = set(cosine.loc[cosine.decision == "ABSTAIN", "substrate"])
    assert keep == {"CosMx BCC", "CosMx NSCLC", "CosMx CRC", "CosMx HCC"}
    assert "CosMx PDAC" in abstain
    hcc = cosine.loc[cosine.substrate == "CosMx HCC"].iloc[0]
    assert hcc.neighbor == "Stellate.cells"
    assert abs(float(hcc.cosine) - 0.648597) < 1e-9
    pdac = cosine.loc[cosine.substrate == "CosMx PDAC"].iloc[0]
    assert abs(float(pdac.cosine) - 0.861599) < 1e-9
    assert "NSCLC P1 from P0" in set(donor.edge)
    assert len(donor) == 4
