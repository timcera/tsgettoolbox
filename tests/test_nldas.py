import numpy as np

from tsgettoolbox.tsgettoolbox import ldas_nldas_fora


def test_nldas():
    lat, lon = 29.9375, -95.0625
    variables = ["NLDAS_FORA0125_H.002:APCPsfc", "NLDAS_FORA0125_H.002:PEVAPsfc"]
    start_date, end_date = "2003-01-01", "2003-12-31"
    df = ldas_nldas_fora(
        lat=lat, lon=lon, variables=variables, startDate=start_date, endDate=end_date
    )
    assert np.isclose(df["APCPsfc:mm"].mean(), 0.1555, rtol=1e-3) and df.shape[
        1
    ] == len(variables)
