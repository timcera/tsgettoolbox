"""
daymet              NAmerica 1km 1980- D,M:Daymet, daily meteorology by
                    the Oak Ridge National Laboratory
"""

import datetime
import logging
import os
import warnings
from typing import List, Literal, Optional, Union

import pandas as pd
import pydaymet
from toolbox_utils import tsutils

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
    "penman_monteith": ":mm",
    "hargreaves_samani": ":mm",
    "priestley_taylor": ":mm",
}

_time_scale_map = {
    "daily": (pd.offsets.Day(0), pd.offsets.Day(0)),
    "monthly": (pd.offsets.MonthBegin(0), pd.offsets.MonthEnd(0)),
    "annual": (pd.offsets.YearBegin(0), pd.offsets.YearEnd(0)),
}


@tsutils.transform_args(measuredParams=tsutils.make_list, years=tsutils.make_list)
@tsutils.doc(tsutils.docstrings)
def daymet(
    lat: float,
    lon: float,
    start_date: pd.Timestamp = "1980-01-01",
    end_date: Optional[pd.Timestamp] = None,
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
                    "penman_monteith",
                    "hargreaves_samani",
                    "priestley_taylor",
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
                "penman_monteith",
                "hargreaves_samani",
                "priestley_taylor",
                "all",
            ],
        ]
    ] = None,
    time_scale: Literal["daily", "monthly", "annual"] = "daily",
    snow: bool = False,
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
        though this is dependent on time required to process that data.

    years : CommaSeparatedYears (optional):
        Current Daymet product is available from 1980 to the latest
        full calendar year.::

            Example: --years=2012,2014

        This overrides the start_date and end_date options.

    measuredParams:
        [optional, defaults to "all"]

        Use the abbreviations from the following table:

        +-------------------+-------------------------+---------+-------------+
        | measuredParams    | Description             | Unit    | time_scale  |
        +===================+=========================+=========+=============+
        | prcp              | precipitation           | mm      | daily       |
        |                   |                         |         | monthly     |
        |                   |                         |         | annual      |
        +-------------------+-------------------------+---------+-------------+
        | swe               | snow-water equivalent   | kg/m2   | daily       |
        |                   |                         |         | monthly     |
        |                   |                         |         | annual      |
        +-------------------+-------------------------+---------+-------------+
        | tmax              | maximum temperature     | degC    | daily       |
        |                   |                         |         | monthly     |
        |                   |                         |         | annual      |
        +-------------------+-------------------------+---------+-------------+
        | tmin              | minimum temperature     | degC    | daily       |
        |                   |                         |         | monthly     |
        |                   |                         |         | annual      |
        +-------------------+-------------------------+---------+-------------+
        | vp                | vapor pressure          | Pa      | daily       |
        |                   |                         |         | monthly     |
        |                   |                         |         | annual      |
        +-------------------+-------------------------+---------+-------------+
        | dayl              | daylength               | seconds | daily       |
        +-------------------+-------------------------+---------+-------------+
        | srad              | shortwave radiation     | W/m2    | daily       |
        +-------------------+-------------------------+---------+-------------+
        | penman_monteith   | PET by Penman-Montieth  | mm      | daily       |
        +-------------------+-------------------------+---------+-------------+
        | hargreaves_samani | PET by Hargreaves-      | mm      | daily       |
        |                   | Samani                  |         |             |
        +-------------------+-------------------------+---------+-------------+
        | priestley_taylor  | PET by Priestley-Taylor | mm      | daily       |
        +-------------------+-------------------------+---------+-------------+

        Example: --measuredParams=tmax,tmin

        All variables are returned by default.

    time_scale:
        [optional, default is "daily"]

        One of "daily", "monthly", or "annual".

    snow : bool
        [optional, defaults to False]

        Separate snowfall from precipitation using Martinez and Gupta (2010)
        method.
    """
    years = tsutils.make_list(years)
    avail_params = [
        "tmax",
        "tmin",
        "srad",
        "vp",
        "swe",
        "prcp",
        "dayl",
        "penman_monteith",
        "hargreaves_samani",
        "priestley_taylor",
    ]

    pet_types = [
        "penman_monteith",
        "hargreaves_samani",
        "priestley_taylor",
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

    if time_scale in ("monthly", "annual"):
        for rem in ["srad", "dayl"] + pet_types:
            if rem in measuredParams:
                measuredParams.remove(rem)
                logging.warning(
                    tsutils.error_wrapper(
                        f"""
                        The parameter {rem} is not available for {time_scale}
                        data.
                        """
                    )
                )

    time_code = _time_scale_map[time_scale]

    dates = None
    if years is not None:
        dates = years
    else:
        if end_date is None:
            end_date = pd.Timestamp(
                f"{datetime.datetime.now().year - 1}-12-31"
            ).strftime("%Y-%m-%d")
        dates = (
            (pd.Timestamp(start_date) + time_code[0]).strftime("%Y-%m-%d"),
            (pd.Timestamp(end_date) + time_code[1]).strftime("%Y-%m-%d"),
        )

    obs_data = [i for i in measuredParams if i not in pet_types]

    ndf = pd.DataFrame()
    if obs_data:
        print(lon, lat)
        print(dates)
        print(obs_data)
        print(time_scale)
        print(snow)
        ndf = pydaymet.get_bycoords(
            (lon, lat),
            dates,
            variables=obs_data,
            crs="epsg:4326",
            time_scale=time_scale,
            snow=snow,
        )
        ndf = ndf.rename(lambda x: x.split()[0], axis="columns")
        ndf = ndf[obs_data]

    for pet in pet_types:
        if pet in measuredParams:
            df = pydaymet.get_bycoords(
                (lon, lat),
                dates,
                variables=["tmax"],
                crs="epsg:4326",
                time_scale=time_scale,
                pet=pet,
                snow=snow,
            )
            df = df.rename(lambda x: x.split()[0], axis="columns")
            df = df.drop("tmax", axis="columns")
            ndf[pet] = df["pet"]

    if time_scale == "monthly":
        ndf.index = ndf.index.to_period("M")
    if time_scale == "annual":
        ndf.index = ndf.index.to_period("A")

    if os.path.exists("debug_tsgettoolbox"):
        logging.warning(f"{start_date}, {end_date}, {years}")

    ndf.columns = [i.split()[0] for i in ndf.columns]
    ndf = ndf[measuredParams]
    ndf.columns = [f"Daymet-{i}{_units_map[i]}" for i in ndf.columns]
    ndf.index.name = "Datetime"
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
        time_scale="annual",
    )

    print("Daymet 4")
    print("start_date='1991', end_date='1995', time_scale='annual'")
    print(r)

    r = daymet(
        lat=43.1,
        lon=-85.2,
        start_date="1980",
        end_date="1981",
        time_scale="monthly",
    )

    print("Daymet 5")
    print("start_date='1980', end_date='1981', time_scale='monthly'")
    print(r)

    r = daymet(
        lat=43.1,
        lon=-85.2,
        start_date="2010-04",
        time_scale="annual",
    )

    print("Daymet 6")
    print("start_date='2010-04', time_scale='annual'")
    print(r)

    r = daymet(
        lat=43.1,
        lon=-85.2,
        start_date="2000-04",
        time_scale="monthly",
    )

    print("Daymet 7")
    print("start_date='2000-04', time_scale='monthly'")
    print(r)

    r = daymet(
        lat=43.1,
        lon=-85.2,
        measuredParams="penman_monteith",
    )

    print("Daymet 8")
    print("measuredParams='penman_monteith'")
    print(r)
