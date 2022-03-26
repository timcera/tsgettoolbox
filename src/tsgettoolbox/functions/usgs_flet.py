# -*- coding: utf-8 -*-
"""Download data from Florida Automated Weather Network (FAWN)."""

from typing import Callable

import mando
import pandas as pd

try:
    from mando.rst_text_formatter import RSTHelpFormatter as HelpFormatter
except ImportError:
    from argparse import RawTextHelpFormatter as HelpFormatter

from tstoolbox import tsutils

from tsgettoolbox import utils

_vars = {
    # For the time-being comment out non-timeseries data.
    # "wmd": {
    #     "sname": "wmd",
    #     "lname": "WMD",
    #     "vname": "Water management district integer code",
    #     "standard_name": "WMD",
    # },
    # "fips": {
    #     "sname": "fips",
    #     "lname": "FIPS",
    #     "vname": "Federal Information Processing Standards state/county code",
    #     "standard_name": "FIPS",
    # },
    # 'ETo', 'PET', 'Solar', 'Albedo', 'Tmin', 'Tmax', 'RHmin', 'RHmax', 'ws2m', 'SolarCode'
    "ETo": {
        "sname": "ret",
        "lname": "ETo",
        "vname": "Daily reference and potential evapotranspiration, and supporting meteorological data from the North American Regional Reanalysis, solar insolation data from the GOES satellite, and blue-sky albedo data from the MODIS satellite, Florida",
        "standard_name": "ETo",
    },
    "PET": {
        "sname": "pet",
        "lname": "PET",
        "vname": "Daily reference and potential evapotranspiration, and supporting meteorological data from the North American Regional Reanalysis, solar insolation data from the GOES satellite, and blue-sky albedo data from the MODIS satellite, Florida",
        "standard_name": "PET",
    },
    "Solar": {
        "sname": "srad",
        "lname": "Solar",
        "vname": "Daily reference and potential evapotranspiration, and supporting meteorological data from the North American Regional Reanalysis, solar insolation data from the GOES satellite, and blue-sky albedo data from the MODIS satellite, Florida",
        "standard_name": "Solar",
    },
    "Albedo": {
        "sname": "albedo",
        "lname": "Albedo",
        "vname": "Daily reference and potential evapotranspiration, and supporting meteorological data from the North American Regional Reanalysis, solar insolation data from the GOES satellite, and blue-sky albedo data from the MODIS satellite, Florida",
        "standard_name": "Albedo",
    },
    "Tmin": {
        "sname": "tmin",
        "lname": "Tmin",
        "vname": "Daily reference and potential evapotranspiration, and supporting meteorological data from the North American Regional Reanalysis, solar insolation data from the GOES satellite, and blue-sky albedo data from the MODIS satellite, Florida",
        "standard_name": "Tmin",
    },
    "Tmax": {
        "sname": "tmax",
        "lname": "Tmax",
        "vname": "Daily reference and potential evapotranspiration, and supporting meteorological data from the North American Regional Reanalysis, solar insolation data from the GOES satellite, and blue-sky albedo data from the MODIS satellite, Florida",
        "standard_name": "Tmax",
    },
    "RHmin": {
        "sname": "rhmin",
        "lname": "RHmin",
        "vname": "Daily reference and potential evapotranspiration, and supporting meteorological data from the North American Regional Reanalysis, solar insolation data from the GOES satellite, and blue-sky albedo data from the MODIS satellite, Florida",
        "standard_name": "RHmin",
    },
    "RHmax": {
        "sname": "rhmax",
        "lname": "RHmax",
        "vname": "Daily reference and potential evapotranspiration, and supporting meteorological data from the North American Regional Reanalysis, solar insolation data from the GOES satellite, and blue-sky albedo data from the MODIS satellite, Florida",
        "standard_name": "RHmax",
    },
    "ws2m": {
        "sname": "ws2m",
        "lname": "ws2m",
        "vname": "Daily reference and potential evapotranspiration, and supporting meteorological data from the North American Regional Reanalysis, solar insolation data from the GOES satellite, and blue-sky albedo data from the MODIS satellite, Florida",
        "standard_name": "ws2m",
    },
    "SolarCode": {
        "sname": "qcode",
        "lname": "SolarCode",
        "vname": "Daily reference and potential evapotranspiration, and supporting meteorological data from the North American Regional Reanalysis, solar insolation data from the GOES satellite, and blue-sky albedo data from the MODIS satellite, Florida",
        "standard_name": "Solar",
    },
}


docs = r"""

    Daily reference and potential evapotranspiration, and supporting
    meteorological, solar insolation, and blue-sky albedo data, Florida, 2019
    (ver. 1.1)

    version: 1.1

    acknowledgement: U.S. Geological Survey, Caribbean-Florida Water Science
    Center, www.usgs.gov/centers/car-fl-water

    Metadata_Conventions: Unidata Dataset Discovery v1.0

    keywords: Evapotranspiration, Atmospheric Temperature, Humidity, Surface
    Winds, Albedo, Incoming Solar Radiation

    keywords_vocabulary: GCMD Science Keywords

    id: flet/thredds/cida.usgs.gov

    naming_authority: cida.usgs.gov

    cdm_data_type: Grid

    creator_name: Jason Bellino

    creator_email: jbellino at usgs.gov

    publisher_name: U.S. Geological Survey

    publisher_url: www.usgs.gov

    time_coverage_resolution: Daily

    license: These data are freely available and public domain.

    authors: Bellino, Jason C.; Shoemaker, W.B.; and Mecikalski, J.R.

    institution: U.S. Geological Survey

    Parameters
    ----------
    {lat}
    {lon}
    variables : str
        At the command line can supply a comma separated list of variable
        names.  Using the Python API needs to be a Python list of strings.

        The current list of available variables are in the following table.

        +--------+----------------------------------+-----------+
        | Short  | Long                             | Units     |
        +========+==================================+===========+
        | ret    | reference ET                     | mm        |
        +--------+----------------------------------+-----------+
        | pet    | potential ET                     | mm        |
        +--------+----------------------------------+-----------+
        | srad   | solar radiation                  | MJ/m2/day |
        +--------+----------------------------------+-----------+
        | albedo | albedo                           |           |
        +--------+----------------------------------+-----------+
        | tmin   | minimum temperature              | degC      |
        +--------+----------------------------------+-----------+
        | tmax   | maximum temperature              | degC      |
        +--------+----------------------------------+-----------+
        | rhmin  | minimum relative humidity        | percent   |
        +--------+----------------------------------+-----------+
        | rhmax  | maximum relative humidity        | percent   |
        +--------+----------------------------------+-----------+
        | ws     | wind_speed                       | m/s       |
        +--------+----------------------------------+-----------+
        | qcode  | solar radiation quality code     |           |
        +--------+----------------------------------+-----------+

    {start_date}
    {end_date}
    """.format(
    **tsutils.docstrings
)


def assign_docstring(indocstring: str) -> Callable:
    """Assign docstring."""

    def f(fn):
        fn.__doc__ = fn.__doc__ + "\n" + indocstring
        return fn

    return f


def _rename_columns(x):
    words = x.split(":")
    words[0] = words[0].split(",")[0]
    return ":".join(words)


@mando.command("usgs_flet_narr", formatter_class=HelpFormatter, doctype="numpy")
@assign_docstring(docs)
def usgs_flet_narr_cli(
    lat,
    lon,
    variables=None,
    start_date=None,
    end_date=None,
):
    """gridded: USGS FL ET data from NARR meteorologic data."""
    tsutils._printiso(
        usgs_flet_narr(
            lat,
            lon,
            variables=variables,
            start_date=start_date,
            end_date=end_date,
        )
    )


def usgs_flet_narr(
    lat,
    lon,
    variables=None,
    start_date=None,
    end_date=None,
):
    r"""gridded: Download USGS WATERS data from CIDA."""
    url = "https://cida.usgs.gov/thredds/dodsC/flet_narr"
    if variables is None:
        variables = list(_vars.keys())
    df = utils.opendap(
        url,
        lat,
        lon,
        _vars,
        time_name="time",
        variables=variables,
        start_date=start_date,
        end_date=end_date,
        tzname=None,
        missing_value=-9999,
    )

    df = df.rename(columns=_rename_columns)

    return df


usgs_flet_narr.__doc__ = usgs_flet_narr_cli.__doc__


@mando.command("usgs_flet_stns", formatter_class=HelpFormatter, doctype="numpy")
@assign_docstring(docs)
def usgs_flet_stns_cli(
    lat,
    lon,
    variables=None,
    start_date=None,
    end_date=None,
):
    """gridded: USGS FL ET data from station interpolated meteorologic data."""
    tsutils._printiso(
        usgs_flet_stns(
            lat,
            lon,
            variables=variables,
            start_date=start_date,
            end_date=end_date,
        )
    )


def usgs_flet_stns(
    lat,
    lon,
    variables=None,
    start_date=None,
    end_date=None,
):
    r"""gridded: Download USGS WATERS data from CIDA."""
    url = "https://cida.usgs.gov/thredds/dodsC/flet_stns"
    if variables is None:
        variables = list(_vars.keys())
    df = utils.opendap(
        url,
        lat,
        lon,
        _vars,
        time_name="time",
        variables=variables,
        start_date=start_date,
        end_date=end_date,
        tzname=None,
        missing_value=-9999,
    )

    df = df.rename(columns=_rename_columns)

    return df


usgs_flet_stns.__doc__ = usgs_flet_stns_cli.__doc__


if __name__ == "__main__":
    print("flet_narr")
    r = usgs_flet_narr(29.6, -82.3)
    print(r)
    print("flet_stns")
    r = usgs_flet_stns(29.6, -82.3)
    print(r)
