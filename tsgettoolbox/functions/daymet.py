#!/usr/bin/env python
r"""
tsgettoolbox command line/library tools to retrieve time series.

This program is a collection of utilities to download data from various
web services.
"""

from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import warnings

from tsgettoolbox.odo import odo, resource
import pandas as pd
import mando

try:
    from mando.rst_text_formatter import RSTHelpFormatter as HelpFormatter
except ImportError:
    from argparse import RawTextHelpFormatter as HelpFormatter

from tstoolbox import tsutils

warnings.filterwarnings("ignore")


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
    year :  CommaSeparatedYears (optional):
        Current Daymet product (version 2) is available from 1980 to the latest
        full calendar year.::

            Example: --years=2012,2013

        All years are returned by default.
    """
    tsutils._printiso(daymet(lat, lon, measuredParams=measuredParams, year=year))


def daymet(lat, lon, measuredParams=None, year=None):
    r"""Download data from Daymet by the Oak Ridge National Laboratory."""
    from tsgettoolbox.services import daymet as placeholder

    r = resource(
        r"http://daymet.ornl.gov/data/send/saveData",
        measuredParams=measuredParams,
        lat=lat,
        lon=lon,
        year=year,
    )
    return odo(r, pd.DataFrame)


daymet.__doc__ = daymet_cli.__doc__
