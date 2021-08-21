# -*- coding: utf-8 -*-
"""Download data from Florida Automated Weather Network (FAWN)."""

from typing import Callable

import mando
import pandas as pd

try:
    from mando.rst_text_formatter import RSTHelpFormatter as HelpFormatter
except ImportError:
    from argparse import RawTextHelpFormatter as HelpFormatter

import xarray as xr
from tstoolbox import tsutils

_vars = {
    "ret": "ETo",
    "pet": "PET",
    "srad": "Solar",
    "albedo": "Albedo",
    "tmin": "Tmin",
    "tmax": "Tmax",
    "rhmin": "RHmin",
    "rhmax": "RHmax",
    "ws": "ws2m",
    "qcode": "SolarCode",
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


def opendap(url, variables, lat, lon, start_date=None, end_date=None):
    if variables is None:
        variables = _vars.keys()

    if not variables:
        variables = _vars.keys()

    variables = tsutils.make_list(variables)

    nvars = [_vars.get(i, i) for i in variables]

    # Get and subset the data.
    dataset = (
        xr.open_dataset(url, engine="pydap", cache=True, mask_and_scale=True)
        .sel(lat=lat, lon=lon, method="nearest")[nvars]
        .drop_vars(["lat", "lon"])
        .sel(time=slice(start_date, end_date))
    )

    # Rename the columns to include units of the form "name:unit".
    rename = {}
    for i in nvars:
        if i in ["Tmin", "Tmax"]:
            unit_label = "degC"
        else:
            unit_label = dataset[i].attrs["units"]
        unit_label = unit_label.replace(" per ", "/")
        unit_label = unit_label.replace("millimeters", "mm")
        unit_label = unit_label.replace("square meter", "m^2")
        unit_label = unit_label.replace("meters", "m")
        unit_label = unit_label.replace("second", "s")
        rename[i] = "{}:{}".format(i, unit_label)
    ndf = dataset.to_dataframe().rename(rename, axis="columns")

    ndf.index.name = "Datetime"

    if len(ndf.dropna(how="all")) == 0:
        if start_date is None:
            start_date = "beginning of record"
        if end_date is None:
            end_date = "end of record"
        raise ValueError(
            tsutils.error_wrapper(
                """
USGS-CIDA returned no USGS WATERS data for lat/lon "{lat}/{lon}", variables
"{variables}" between {start_date} and {end_date}.
""".format(
                    **locals()
                )
            )
        )

    return ndf


@mando.command("usgs_flet_narr", formatter_class=HelpFormatter, doctype="numpy")
@assign_docstring(docs)
def usgs_flet_narr_cli(
    lat,
    lon,
    variables=None,
    start_date=None,
    end_date=None,
):
    """USGS FL ET data from NARR meteorologic data."""
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
    r"""Download USGS WATERS data from CIDA."""
    url = "https://cida.usgs.gov/thredds/dodsC/flet_narr"
    df = opendap(url, variables, lat, lon, start_date=start_date, end_date=end_date)

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
    """USGS FL ET data from station interpolated meteorologic data."""
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
    r"""Download USGS WATERS data from CIDA."""
    url = "https://cida.usgs.gov/thredds/dodsC/flet_stns"
    df = opendap(url, variables, lat, lon, start_date=start_date, end_date=end_date)

    return df


usgs_flet_stns.__doc__ = usgs_flet_stns_cli.__doc__


if __name__ == "__main__":
    print("flet_narr")
    r = usgs_flet_narr(29.6, -82.3)
    print(r)
    print("flet_stns")
    r = usgs_flet_stns(29.6, -82.3)
    print(r)
