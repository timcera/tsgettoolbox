# -*- coding: utf-8 -*-
from typing import Optional

import mando
import pandas as pd

try:
    from mando.rst_text_formatter import RSTHelpFormatter as HelpFormatter
except ImportError:
    from argparse import RawTextHelpFormatter as HelpFormatter

import typic
from tstoolbox import tsutils

from tsgettoolbox.ulmo.cpc.drought.core import get_data

unit_conv = {
    "precipitation": "precipitation:in",
    "temperature": "temperature:degF",
    "potential_evap": "potential_evap:in",
    "runoff": "runoff:in",
    "soil_moisture_upper": "soil_moisture_upper:in",
    "soil_moisture_lower": "soil_moisture_lower:in",
}


def ulmo_df(state=None, climate_division=None, start_date=None, end_date=None):
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
    return df


@mando.command("cpc", formatter_class=HelpFormatter, doctype="numpy")
@tsutils.doc(tsutils.docstrings)
def cpc_cli(state=None, climate_division=None, start_date=None, end_date=None):
    r"""station: Climate Prediction Center, Weekly Drought Index

    Climate Prediction Center: http://www.cpc.ncep.noaa.gov/
    Weekly Drought Index:

    http://www.cpc.ncep.noaa.gov/products/analysis_monitoring/cdus/palmer_drought/

    The `climate_division` integer value identifies a portion of the
    desired `state` divided along county boundaries. Maps of the climate
    divisions within each state are at:

    https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/regional_monitoring/CLIM_DIVS/states_counties_climate-divisions.shtml

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
    tsutils._printiso(
        cpc(
            state=state,
            climate_division=climate_division,
            start_date=start_date,
            end_date=end_date,
        )
    )


@typic.al
def cpc(
    state: Optional[str] = None,
    climate_division: Optional[int] = None,
    start_date=None,
    end_date=None,
):
    r"""Access Climate Prediction Center, Weekly Drought Index dataset."""
    df = ulmo_df(
        state=state,
        climate_division=climate_division,
        start_date=tsutils.parsedate(start_date),
        end_date=tsutils.parsedate(end_date),
    )
    return df


cpc.__doc__ = cpc_cli.__doc__


if __name__ == "__main__":
    r = ulmo_df(
        state="FL", climate_division=1, start_date="2017-01-01", end_date="2017-10-02"
    )

    print("FL EVERYTHING")
    print(r)
