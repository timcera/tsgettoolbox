import os

import numpy as np
import pytest

from tsgettoolbox.tsgettoolbox import ldas_nldas_fora


@pytest.mark.skipif(
    os.environ.get("GITHUB_ACTIONS") == "true",
    reason="Skip NLDAS test on GitHub Actions",
)
def test_nldas():
    lat, lon = 29.9375, -95.0625
    variables = ["NLDAS_FORA0125_H_2_0_Rainf", "NLDAS_FORA0125_H_2_0_PotEvap"]
    start_date, end_date = "2003-01-01", "2003-12-31"
    df = ldas_nldas_fora(
        lat=lat, lon=lon, variables=variables, startDate=start_date, endDate=end_date
    )
    assert np.isclose(
        df["NLDAS_FORA0125_H_2_0_Rainf:mm"].mean(), 0.155496623554996, rtol=1e-3
    ) and df.shape[1] == len(variables)
