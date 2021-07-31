# -*- coding: utf-8 -*-
"""Download data from Florida Automated Weather Network (FAWN)."""


import mando
import pandas as pd

try:
    from mando.rst_text_formatter import RSTHelpFormatter as HelpFormatter
except ImportError:
    from argparse import RawTextHelpFormatter as HelpFormatter

import xarray as xr
from tstoolbox import tsutils

_vars = {
    "precip": "precipitation_amount",
    "rhmin": "min_relative_humidity",
    "rhmax": "max_relative_humidity",
    "sph": "specific_humidity",
    "srad": "surface_downwelling_shortwave_flux_in_air",
    "tmin": "min_air_temperature",
    "tmax": "max_air_temperature",
    "winds": "wind_speed",
}


@mando.command("metdata", formatter_class=HelpFormatter, doctype="numpy")
@tsutils.doc(tsutils.docstrings)
def metdata_cli(
    lat,
    lon,
    variables=None,
    start_date=None,
    end_date=None,
):
    r"""Download daily data from METDATA.

    This archive contains daily surface meteorological (METDATA) data for the
    Continental United States at 4-km (1/24-deg) resolution. The meteorological
    variables are maximum/minimum temperature, precipitation amount and duration,
    maximum/minimum relative humidity,downward shortwave solar radiation, wind speed and
    direction, and specific humidity. The method utilized here combines desirable
    spatial attributes of gridded climate data from PRISM and desirable temporal
    attributes of regional-scale reanalysis and daily gauge-based precipitation from
    NLDAS-2 to derive a spatially and temporally complete high resolution gridded
    dataset of surface meteorological variables for the continental US for 1979-present.
    Validation of this data suggests that it can serve as a suitable surrogate for
    landscape-scale ecological modeling across vast unmonitored areas of the US.

    Whenever you publish research based on data from this archive, please reference this
    data by using the phrase "daily gridded meteorological data (METDATA) for the
    continental US" and by citing the article (Abatzoglou,2012). Further, appropriately
    acknowledge the National Science Foundation (NSF), Idaho EPSCoR and the individual
    investigators responsible for the data set.

    Citation:
        Abatzoglou, J.T., 2013, Development of gridded surface meteorological data for
        ecological applications and modeling, International Journal of Climatology, DOI:
        10.1002/joc.3413
    geospatial_bounds_crs:
        EPSG:4326
    Conventions:
        CF-1.0
    geospatial_bounds:
        POLYGON((-124.7666666333333 49.400000000000000, -124.7666666333333
        25.066666666666666, -67.058333300000015 25.066666666666666, -67.058333300000015
        49.400000000000000, -124.7666666333333 49.400000000000000))
    geospatial_lat_min:
        25.0631
    geospatial_lat_max:
        49.3960
    geospatial_lon_min:
        -124.7722
    geospatial_lon_max:
        -67.0648
    geospatial_lon_resolution:
        0.041666666666666
    geospatial_lat_resolution:
        0.041666666666666
    geospatial_lat_units:
        decimal_degrees north
    geospatial_lon_units:
        decimal_degrees east
    coordinate_system:
        EPSG:4326
    author:
        John Abatzoglou - University of Idaho, jabatzoglou @ uidaho.edu
    date:
        02 July 2019
    note1:
        The projection information for this file is: GCS WGS 1984.
    note3:
        Data in slices after last_permanent_slice (1-based) are considered provisional and subject to change with subsequent updates
    note4:
        Data in slices after last_provisional_slice (1-based) are considered early and subject to change with subsequent updates
    note5:
        Days correspond approximately to calendar days ending at midnight, Mountain Standard Time (7 UTC the next calendar day)
    Metadata_Conventions:
        Unidata Dataset Discovery v1.0
    title:
        Daily Meteorological data for continental US
    keywords:
        daily precipitation, daily precipitation duration, daily maximum temperature, daily minimum temperature, daily downward shortwave solar radiation, daily specific humidity, daily maximum relative humidity, daily minimum relative humidity, daily wind speed, daily wind direction, ClimatologyMeteorologyAtmosphere, Gridded Meteorological Data, EPSCoR Data
    id:
        UofIMETDATA
    naming_authority:
        cida.usgs.gov
    cdm_data_type:
        Grid
    date_created:
        2012-08-16
    creator_name:
        Dr. John Abatzoglou
    creator_url:
        http://nimbus.cos.uidaho.eud/METDATA/
    creator_email:
        jabatzoglou @ uidaho.edu
    publisher_name:
        Center for Integrated Data Analytics
    publisher_url:
        https://www.cida.usgs.gov/
    publisher_email:
        dblodgett @ usgs.gov
    institution:
        University of Idaho
    date_issued:
        2012-08-16
    project:
        METDATA
    processing_level:
        Gridded Meteorogolical Data
    contributors:
        Dr. John Abatzoglou
    time_coverage_start:
        1979-01-01T00:00
    time_coverage_resolution:
        P1D
    license:
        Freely available

    Parameters
    ----------
    {lat}

    {lon}

    variables : str
        At the command line can supply a comma separated list of variable
        names.  Using the Python API needs to be a Python list of strings.

        The current list of available METDATA variables are in the following table and
        you can use either the "Short" or "Long" names.

        +--------+-------------------------------------------+-------+
        | Short  | Long                                      | Units |
        +========+===========================================+=======+
        | precip | precipitation_amount                      | mm    |
        +--------+-------------------------------------------+-------+
        | rhmax  | max_relative_humidity                     |       |
        +--------+-------------------------------------------+-------+
        | rhmin  | min_relative_humidity                     |       |
        +--------+-------------------------------------------+-------+
        | sph    | specific_humidity                         | kg/kg |
        +--------+-------------------------------------------+-------+
        | srad   | surface_downwelling_shortwave_flux_in_air | W/m2  |
        +--------+-------------------------------------------+-------+
        | tmin   | min_air_temperature                       | degK  |
        +--------+-------------------------------------------+-------+
        | tmax   | max_air_temperature                       | degK  |
        +--------+-------------------------------------------+-------+
        | winds  | wind_speed                                | m/s   |
        +--------+-------------------------------------------+-------+

    {start_date}

    {end_date}
    """
    tsutils._printiso(
        metdata(
            lat,
            lon,
            variables=variables,
            start_date=start_date,
            end_date=end_date,
        )
    )


def opendap(variables, lat, lon, start_date=None, end_date=None):
    url = "https://cida.usgs.gov/thredds/dodsC/UofIMETDATA"

    if not variables:
        variables = _vars.keys()

    variables = tsutils.make_list(variables)

    nvars = [_vars.get(i, i) for i in variables]

    # Get and subset the data.
    dataset = (
        xr.open_dataset(url, engine="pydap", cache=True, mask_and_scale=True)
        .sel(lat=lat, lon=lon, method="nearest")[nvars]
        .drop_vars(["lat", "lon"])
        .sel(day=slice(start_date, end_date))
    )

    # Rename the columns to include units of the form "name:unit".
    rename = {}
    for i in nvars:
        if i in ["min_air_temperature", "max_air_temperature"]:
            unit_label = "degK"
        else:
            unit_label = dataset[i].attrs["units"]
        rename[i] = "{}:{}".format(i, unit_label)
    ndf = dataset.to_dataframe().rename(rename, axis="columns")

    ndf.index.name = "Datetime"

    return ndf


def metdata(
    lat,
    lon,
    variables=None,
    start_date=None,
    end_date=None,
):
    r"""Download METDATA data from CIDA."""
    if variables is None:
        variables = _vars.keys()

    df = opendap(variables, lat, lon, start_date=start_date, end_date=end_date)

    if len(df.dropna(how="all")) == 0:
        if start_date is None:
            start_date = "beginning of record"
        if end_date is None:
            end_date = "end of record"
        raise ValueError(
            tsutils.error_wrapper(
                """
USGS-CIDA returned no METDATA data for lat/lon "{lat}/{lon}", variables "{variables}"
between {start_date} and {end_date}.
""".format(
                    **locals()
                )
            )
        )

    return df


metdata.__doc__ = metdata_cli.__doc__


if __name__ == "__main__":
    r = metdata(29.6, -82.3, "precipitation_amount")
    print(r)
