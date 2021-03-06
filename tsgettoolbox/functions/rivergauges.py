"""
Provide access to data from the USACE `Rivergages`_ web site.

`United States Army Corps of Engineers`_ `Rivergages`_ web site.

.. _United States Army Corps of Engineers: http://www.usace.army.mil/
.. _Rivergages: http://rivergages.mvr.usace.army.mil/WaterControl/new/layout.cfm
"""
import warnings

warnings.filterwarnings("ignore")

import pandas as pd

from tstoolbox import tsutils

from tsgettoolbox.ulmo.usace.rivergages.core import get_station_data
from tsgettoolbox.ulmo.usace.rivergages.core import get_station_parameters
from tsgettoolbox.ulmo.usace.rivergages.core import get_stations

# def get_station_data(station_code, parameter, start=None, end=None,
#         min_value=None, max_value=None):


def ulmo_df(station_code, parameter, start_date=None, end_date=None):
    tstations = get_stations()
    if station_code not in tstations:
        raise ValueError(
            tsutils.error_wrapper(
                """
Station code {0} not in available stations:
{1}
""".format(
                    station_code, tstations.keys
                )
            )
        )

    tparameters = get_station_parameters(station_code)
    if parameter not in tparameters:
        raise ValueError(
            tsutils.error_wrapper(
                """
Parameter code {0} not in available parameters at station {1}:
{2}
""".format(
                    parameter, station_code, tparameters
                )
            )
        )
    df = get_station_data(
        station_code,
        parameter,
        start=pd.to_datetime(start_date),
        end=pd.to_datetime(end_date),
    )
    df = pd.DataFrame.from_dict(df, orient="index")
    df.sort_index(inplace=True)
    df.index.name = "Datetime"
    df.columns = ["{0}_{1}".format(station_code, parameter)]
    return df


if __name__ == "__main__":
    #    import time
    #
    #    r = ulmo_df('blah',
    #                'upperbasin')
    #
    #    print('BIVOI_HL')
    #    print(r)
    #
    r = ulmo_df("BIVO1", "HL", start_date="2015-11-04", end_date="2015-12-05")

    print("BIVOI HL")
    print(r)
