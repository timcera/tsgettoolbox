"""
daymet              NAmerica 1km 1980- D,M:Daymet, daily meteorology by
                    the Oak Ridge National Laboratory
"""

import datetime
import logging
import os
import warnings
from io import BytesIO
from typing import List, Literal, Optional, Union

import async_retriever as ar
import pandas as pd

from tsgettoolbox.toolbox_utils.src.toolbox_utils import tsutils

__all__ = ["daymet"]

warnings.filterwarnings("ignore")

_units_map = {
    "tmax": ":degC",
    "tmin": ":degC",
    "srad": ":W/m2",
    "vp": ":Pa",
    "swe": ":kg/m2",
    "prcp": ":mm",
    "dayl": ":s",
}


@tsutils.transform_args(measuredParams=tsutils.make_list, years=tsutils.make_list)
@tsutils.doc(tsutils.docstrings)
def daymet(
    lat: float,
    lon: float,
    start_date: Optional[Union[pd.Timestamp, str]] = "1980-01-01",
    end_date: Optional[Union[pd.Timestamp, str]] = None,
    years: Optional[Union[str, List[int]]] = None,
    measuredParams: Optional[
        Union[
            List[
                Literal[
                    "tmax",
                    "tmin",
                    "srad",
                    "vp",
                    "swe",
                    "prcp",
                    "dayl",
                ]
            ],
            Literal[
                "tmax",
                "tmin",
                "srad",
                "vp",
                "swe",
                "prcp",
                "dayl",
                "all",
            ],
        ]
    ] = None,
):
    r"""NAmerica:1km:1980-:D,M:Daymet, daily meteorology by the Oak Ridge National Laboratory

    Detailed documentation is at http://daymet.ornl.gov/.  Since this is
    daily data, it covers midnight to midnight based on local time.

    Parameters
    ----------
    lat : float
        Latitude (required): Enter single geographic point by latitude, value
        between 52.0N and 14.5N.::

            Example: --lat=43.1

    lon : float
        Longitude (required): Enter single geographic point by longitude, value
        between -131.0W and -53.0W.::

            Example: --lon=-85.3

    ${start_date}
        For North America and Hawaii, the earliest date is 1980-01-01. For
        Puerto Rico, the earliest date it 1950-01-01.

    ${end_date}
        The latest end date is usually 12-31 of the previous calendar year,
        though this is dependent on time required to process the previous
        year's data.

    years : CommaSeparatedYears (optional):
        Current Daymet product is available from 1980 to the latest
        full calendar year.::

            Example: --years=2012,2014

        This overrides the start_date and end_date options.

    measuredParams:
        [optional, defaults to "all"]

        Use the abbreviations from the following table:

        +-------------------+--------------------------+---------+
        | measuredParams    | Description              | Unit    |
        +===================+==========================+=========+
        | prcp              | precipitation            | mm      |
        +-------------------+--------------------------+---------+
        | swe               | snow-water equivalent    | kg/m2   |
        +-------------------+--------------------------+---------+
        | tmax              | maximum temperature      | degC    |
        +-------------------+--------------------------+---------+
        | tmin              | minimum temperature      | degC    |
        +-------------------+--------------------------+---------+
        | vp                | vapor pressure           | Pa      |
        +-------------------+--------------------------+---------+
        | dayl              | daylength                | seconds |
        +-------------------+--------------------------+---------+
        | srad              | shortwave radiation      | W/m2    |
        +-------------------+--------------------------+---------+

        Example: --measuredParams=tmax,tmin

        All variables are returned by default.
    """
    avail_params = [
        "tmax",
        "tmin",
        "srad",
        "vp",
        "swe",
        "prcp",
        "dayl",
    ]

    if measuredParams is None or "all" in measuredParams:
        measuredParams = avail_params
    else:
        for testparams in measuredParams:
            if testparams not in avail_params:
                raise ValueError(
                    tsutils.error_wrapper(
                        f"""
                        The measuredParams should be a single string or a list
                        of strings from {avail_params} You supplied
                        {testparams}.
                        """
                    )
                )

    if years:
        years = ",".join([str(y) for y in years])
        update_params = {"years": years}
    else:
        if start_date is None:
            start_date = "1980-01-01"
        if end_date is None:
            end_date = f"{datetime.datetime.now().year - 1}-12-31"

        start = pd.Timestamp(start_date).strftime("%Y-%m-%d")
        end = pd.Timestamp(end_date).strftime("%Y-%m-%d")
        update_params = {"start": start, "end": end}

    time_series_url = "https://daymet.ornl.gov/single-pixel/api/data"

    def year_doy(year, doy):
        collect = []
        for yr, dy in zip(year, doy):
            collect.append(pd.to_datetime(f"{yr}-{dy}", format="%Y-%j"))
        return collect

    ndf = pd.DataFrame()

    params = {"lat": lat, "lon": lon, "vars": ",".join(measuredParams), "format": "csv"}
    params.update(update_params)
    urls, kwds = [[time_series_url], [{"params": params}]]
    resp = ar.retrieve_binary(urls, kwds)

    ndf = pd.DataFrame()
    for response, keyword in zip(resp, kwds):
        df = pd.read_csv(
            BytesIO(response),
            sep=",",
            skiprows=6,
            header=0,
            date_parser=year_doy,
            parse_dates={"Datetime": ["year", "yday"]},
            index_col="Datetime",
        )
        df.index = pd.to_datetime(df.index)

        ndf = ndf.combine_first(df)

    if os.path.exists("debug_tsgettoolbox"):
        logging.warning(f"{start_date}, {end_date}, {years}")

    ndf.index.name = "Datetime"
    ndf.columns = [
        i.replace("(", "").replace(")", "").replace("deg c", "degC").replace(" ", "::")
        for i in ndf.columns
    ]
    return ndf


if __name__ == "__main__":
    r = daymet(
        measuredParams="tmax,tmin",
        lat=43.1,
        lon=-85.2,
        years=[2000, 2001],
    )

    print("Daymet 1")
    print("years=[2000, 2001]")
    print(r)

    r = daymet(
        measuredParams=None,
        lat=43.1,
        lon=-85.2,
        start_date="1995-04-01",
        end_date="2000-01-02",
    )

    print("Daymet 2")
    print("start_date='1995-04-01', end_date='2000-01-02'")
    print(r)

    r = daymet(
        lat=43.1,
        lon=-85.2,
        end_date="2002-12-31",
    )

    print("Daymet 3")
    print("end_date='2002-12-31'")
    print(r)

    r = daymet(
        lat=43.1,
        lon=-85.2,
        start_date="1991",
        end_date="1995",
    )

    print("Daymet 4")
    print("start_date='1991', end_date='1995'")
    print(r)

    r = daymet(
        lat=43.1,
        lon=-85.2,
        start_date="1980",
        end_date="1981",
    )

    print("Daymet 5")
    print("start_date='1980', end_date='1981'")
    print(r)

    r = daymet(
        lat=43.1,
        lon=-85.2,
        start_date="2010-04",
    )

    print("Daymet 6")
    print("start_date='2010-04'")
    print(r)

    r = daymet(
        lat=43.1,
        lon=-85.2,
        start_date="2000-04",
    )

    print("Daymet 7")
    print("start_date='2000-04'")
    print(r)
