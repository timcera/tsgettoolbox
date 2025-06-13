import numpy as np

from tsgettoolbox.tsgettoolbox import ldas_nldas_fora


def test_nldas():
    lat, lon = 29.9375, -95.0625
    variables = ["NLDAS_FORA0125_H_v2.0:Rainf", "NLDAS_FORA0125_H_v2.0:PotEvap"]
    start_date, end_date = "2003-01-01", "2003-12-31"
    df = ldas_nldas_fora(
        lat=lat, lon=lon, variables=variables, startDate=start_date, endDate=end_date
    )
    assert np.isclose(df["Rainf:mm"].mean(), 0.155496623554996, rtol=1e-3) and df.shape[
        1
    ] == len(variables)
