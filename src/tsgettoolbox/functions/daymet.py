# -*- coding: utf-8 -*-
r"""
tsgettoolbox command line/library tools to retrieve time series.

This program is a collection of utilities to download data from various
web services.
"""

from __future__ import absolute_import, division, print_function

import datetime
import logging
import os
from typing import List, Optional, Union

try:
    import urllib.parse as urlp
except ImportError:
    import urllib as urlp

import warnings

import mando
import pandas as pd
import typic

try:
    from mando.rst_text_formatter import RSTHelpFormatter as HelpFormatter
except ImportError:
    from argparse import RawTextHelpFormatter as HelpFormatter

from tstoolbox import tsutils

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


def _daymet_date_parser(year, doy):
    return pd.to_datetime(
        "{}-{}".format(int(float(year)), int(float(doy))), format="%Y-%j"
    )


@mando.command("daymet", formatter_class=HelpFormatter, doctype="numpy")
def daymet_cli(lat, lon, measuredParams=None, year=None):
    r"""Download data from Daymet by the Oak Ridge National Laboratory.

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

    measuredParams:  CommaSeparatedVariables (optional)
        Use the abbreviations from the following table:

        +----------------+-----------------------+---------+
        | measuredParams | Description           | Unit    |
        +================+=======================+=========+
        | tmax           | maximum temperature   | degC    |
        +----------------+-----------------------+---------+
        | tmin           | minimum temperature   | degC    |
        +----------------+-----------------------+---------+
        | srad           | shortwave radiation   | W/m2    |
        +----------------+-----------------------+---------+
        | vp             | vapor pressure        | Pa      |
        +----------------+-----------------------+---------+
        | swe            | snow-water equivalent | kg/m2   |
        +----------------+-----------------------+---------+
        | prcp           | precipitation         | mm      |
        +----------------+-----------------------+---------+
        | dayl           | daylength             | seconds |
        +----------------+-----------------------+---------+

        Example: --measuredParams=tmax,tmin

        All variables are returned by default.

    year : CommaSeparatedYears (optional):
        Current Daymet product (version 2) is available from 1980 to the latest
        full calendar year.::

            Example: --years=2012,2013

        All years are returned by default.
    """
    tsutils._printiso(daymet(lat, lon, measuredParams=measuredParams, year=year))


@tsutils.transform_args(measuredParams=tsutils.make_list, year=tsutils.make_list)
@typic.al
def daymet(
    lat: float,
    lon: float,
    measuredParams: Optional[Union[List[str], str]] = None,
    year: Optional[Union[List[int], int]] = None,
):
    r"""Download data from Daymet by the Oak Ridge National Laboratory."""
    url = r"http://daymet.ornl.gov/data/send/saveData"
    avail_params = ["tmax", "tmin", "srad", "vp", "swe", "prcp", "dayl"]
    params = {}
    params["lat"] = lat
    params["lon"] = lon
    if measuredParams is None:
        measuredParams = avail_params
    else:
        for testparams in measuredParams:
            if testparams not in avail_params:
                raise ValueError(
                    tsutils.error_wrapper(
                        """
The measuredParams should be a single string or a list of strings from
{1}
You supplied {0}.
""".format(
                            testparams, avail_params
                        )
                    )
                )

    last_year = datetime.datetime.now().year - 1
    if year is None:
        params["year"] = ",".join([str(i) for i in range(1980, last_year + 1)])
    else:
        accumyear = []
        for testyear in year:
            try:
                iyear = int(tsutils.parsedate(testyear, strftime="%Y"))
                accumyear.append(iyear)
            except ValueError:
                raise ValueError(
                    tsutils.error_wrapper(
                        """
The year= option must contain a comma separated list of integers.  You
supplied {}.
""".format(
                            testyear
                        )
                    )
                )
            if iyear < 1980 or iyear > last_year:
                raise ValueError(
                    tsutils.error_wrapper(
                        """
The year= option must contain values from 1980 up to and including the last
calendar year.  You supplied {}.
""".format(
                            iyear
                        )
                    )
                )

        params["year"] = ",".join([str(i) for i in accumyear])

    params["measuredParams"] = ",".join(measuredParams)

    req = urlp.unquote("{}?{}".format(url, urlp.urlencode(params)))
    if os.path.exists("debug_tsgettoolbox"):
        logging.warning(req)
    df = pd.read_csv(
        req,
        skiprows=7,
        sep=",",
        date_parser=_daymet_date_parser,
        header=0,
        index_col=0,
        skipinitialspace=True,
        parse_dates=[[0, 1]],
    )
    df.columns = [i.split()[0] for i in df.columns]
    df = df[measuredParams]
    df.columns = ["Daymet-{}{}".format(i, _units_map[i]) for i in df.columns]
    df.index.name = "Datetime"
    return df


daymet.__doc__ = daymet_cli.__doc__


if __name__ == "__main__":
    r = daymet(
        measuredParams="tmax,tmin",
        lat=43.1,
        lon=-85.2,
        year="2000,2001",
    )

    print("Daymet")
    print(r)

    r = daymet(
        measuredParams=None,
        lat=43.1,
        lon=-85.2,
        year="3 years ago,2 years ago",
    )

    print("Daymet")
    print(r)
