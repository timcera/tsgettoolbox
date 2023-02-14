"""
cpc                 US/region W: Climate Prediction Center, Weekly Drought
                    Index
"""

from typing import Optional

import cltoolbox
import pandas as pd
from cltoolbox.rst_text_formatter import RSTHelpFormatter as HelpFormatter
from toolbox_utils import tsutils

from tsgettoolbox.ulmo.cpc.drought.core import get_data

__all__ = ["cpc"]

unit_conv = {
    "precipitation": "precipitation:in",
    "temperature": "temperature:degF",
    "potential_evap": "potential_evap:in",
    "runoff": "runoff:in",
    "soil_moisture_upper": "soil_moisture_upper:in",
    "soil_moisture_lower": "soil_moisture_lower:in",
}


def ulmo_df(state=None, climate_division=None, start_date=None, end_date=None):
    """Get data from ulmo.cpc.drought.core.get_data() and return a dataframe."""
    df = get_data(
        state=state,
        climate_division=climate_division,
        start=start_date,
        end=end_date,
        as_dataframe=True,
    )
    df = df.set_index("period")
    df.index = pd.PeriodIndex(df.index)
    df.index.name = "Datetime"
    df.columns = [unit_conv.get(i, i) for i in df.columns]
    df = df.rename(
        {"pdsi": "palmer_drought_severity_index", "cmi": "crop_moisture_index"},
        axis="columns",
    )
    return df


@cltoolbox.command("cpc", formatter_class=HelpFormatter)
@tsutils.doc(tsutils.docstrings)
def cpc_cli(state=None, climate_division=None, start_date=None, end_date=None):
    r"""US/region W: Climate Prediction Center, Weekly Drought Index

    Climate Prediction Center:

        www.cpc.ncep.noaa.gov

    Weekly Drought Index:

        www.cpc.ncep.noaa.gov/products/analysis_monitoring/cdus/palmer_drought

    The `climate_division` integer value identifies a portion of the
    desired `state` divided along county boundaries. Maps of the climate
    divisions within each state are at:

    www.cpc.ncep.noaa.gov/products/analysis_monitoring/regional_monitoring/CLIM_DIVS/states_counties_climate-divisions.shtml

    The only way to get a time-series is to specify both `state` and
    `climate_division` keywords.

    Command Line ::

        tsgettoolbox cpc --state=FL --climate_division=1 --start_date 2017-01-01

    Python API ::

        df = tsgettoolbox.cpc(state="FL",
                              climate_division=1,
                              start_date="2017-01-01",
                              end_date="2017-02-01")

    Parameters
    ----------
    state : ``None`` or str
        [optional]

        If specified, results will be limited to the state corresponding to the
        given 2-character state code.

    climate_division : ``None`` or int
        [optional]

        If specified, results will be limited to the climate division.

    ${start_date}

    ${end_date}
    """
    tsutils.printiso(
        cpc(
            state=state,
            climate_division=climate_division,
            start_date=start_date,
            end_date=end_date,
        )
    )


@tsutils.copy_doc(cpc_cli)
def cpc(
    state: Optional[str] = None,
    climate_division: Optional[int] = None,
    start_date=None,
    end_date=None,
):
    r"""Access Climate Prediction Center, Weekly Drought Index dataset."""
    return ulmo_df(
        state=state,
        climate_division=climate_division,
        start_date=tsutils.parsedate(start_date),
        end_date=tsutils.parsedate(end_date),
    )


if __name__ == "__main__":
    r = ulmo_df(
        state="FL", climate_division=1, start_date="2017-01-01", end_date="2017-10-02"
    )

    print("FL EVERYTHING")
    print(r)
