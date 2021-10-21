# -*- coding: utf-8 -*-
"""Download data from Florida Automated Weather Network (FAWN)."""

import asyncio

import mando
import pandas as pd

try:
    from mando.rst_text_formatter import RSTHelpFormatter as HelpFormatter
except ImportError:
    from argparse import RawTextHelpFormatter as HelpFormatter

import xarray as xr
from tstoolbox import tsutils

_vars = {
    "pr": "precipitation_amount",
    "rmin": "daily_minimum_relative_humidity",
    "rmax": "daily_maximum_relative_humidity",
    "sph": "daily_mean_specific_humidity",
    "srad": "daily_mean_shortwave_radiation_at_surface",
    "tmmn": "daily_minimum_temperature",
    "tmmx": "daily_maximum_temperature",
    "vs": "daily_mean_wind_speed",
    "th": "daily_mean_wind_direction",
    "bi": "daily_mean_burning_index_g",
    "fm100": "dead_fuel_moisture_100hr",
    "fm1000": "dead_fuel_moisture_1000hr",
    "erc": "daily_mean_energy_release_component-g",
    "pdsi": "daily_mean_palmer_drought_severity_index",
    "etr": "daily_mean_reference_evapotranspiration_alfalfa",
    "pet": "daily_mean_reference_evapotranspiration_grass",
    "vpd": "daily_mean_vapor_pressure_deficit",
    "spi14d": "standardized_precipitation_index_14_day",
    "spi30d": "standardized_precipitation_index_30_day",
    "spi90d": "standardized_precipitation_index_90_day",
    "spi180d": "standardized_precipitation_index_180_day",
    "spi270d": "standardized_precipitation_index_270_day",
    "spi1y": "standardized_precipitation_index_1_year",
    "spi2y": "standardized_precipitation_index_2_year",
    "spi5y": "standardized_precipitation_index_5_year",
    "spei14d": "standardized_et_precipitation_index_14_day",
    "spei30d": "standardized_et_precipitation_index_30_day",
    "spei90d": "standardized_et_precipitation_index_90_day",
    "spei180d": "standardized_et_precipitation_index_180_day",
    "spei270d": "standardized_et_precipitation_index_270_day",
    "spei1y": "standardized_et_precipitation_index_1_year",
    "spei2y": "standardized_et_precipitation_index_2_year",
    "spei5y": "standardized_et_precipitation_index_5_year",
    "eddi14d": "evaporative_drought_demand_index_14_day",
    "eddi30d": "evaporative_drought_demand_index_30_day",
    "eddi90d": "evaporative_drought_demand_index_90_day",
    "eddi180d": "evaporative_drought_demand_index_180_day",
    "eddi270d": "evaporative_drought_demand_index_270_day",
    "eddi1y": "evaporative_drought_demand_index_1_year",
    "eddi2y": "evaporative_drought_demand_index_2_year",
    "eddi5y": "evaporative_drought_demand_index_5_year",
    "z": "daily_mean_palmer_z_index",
}

_inv_vars = {v: k for k, v in _vars.items()}

tsutils.docstrings.update(_vars)


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
    variables are maximum/minimum temperature, precipitation amount and
    duration, maximum/minimum relative humidity,downward shortwave solar
    radiation, wind speed and direction, and specific humidity. The method
    utilized here combines desirable spatial attributes of gridded climate data
    from PRISM and desirable temporal attributes of regional-scale reanalysis
    and daily gauge-based precipitation from NLDAS-2 to derive a spatially and
    temporally complete high resolution gridded dataset of surface
    meteorological variables for the continental US for 1979-present.
    Validation of this data suggests that it can serve as a suitable surrogate
    for landscape-scale ecological modeling across vast unmonitored areas of
    the US.

    Whenever you publish research based on data from this archive, please
    reference this data by using the phrase "daily gridded meteorological data
    (METDATA) for the continental US" and by citing the article
    (Abatzoglou,2012). Further, appropriately acknowledge the National Science
    Foundation (NSF), Idaho EPSCoR and the individual investigators responsible
    for the data set.

    Citation:
        Abatzoglou, J.T., 2013, Development of gridded surface meteorological
        data for ecological applications and modeling, International Journal of
        Climatology, DOI: 10.1002/joc.3413
    geospatial_bounds_crs:
        EPSG:4326
    Conventions:
        CF-1.0
    geospatial_bounds:
        POLYGON((-124.7666666333333 49.400000000000000, -124.7666666333333
        25.066666666666666, -67.058333300000015 25.066666666666666,
        -67.058333300000015 49.400000000000000, -124.7666666333333
        49.400000000000000))
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
        Data in slices after last_permanent_slice (1-based) are considered
        provisional and subject to change with subsequent updates
    note4:
        Data in slices after last_provisional_slice (1-based) are considered
        early and subject to change with subsequent updates
    note5:
        Days correspond approximately to calendar days ending at midnight,
        Mountain Standard Time (7 UTC the next calendar day)
    Metadata_Conventions:
        Unidata Dataset Discovery v1.0
    title:
        Daily Meteorological data for continental US
    keywords:
        daily precipitation, daily precipitation duration, daily maximum
        temperature, daily minimum temperature, daily downward shortwave solar
        radiation, daily specific humidity, daily maximum relative humidity,
        daily minimum relative humidity, daily wind speed, daily wind
        direction, ClimatologyMeteorologyAtmosphere, Gridded Meteorological
        Data, EPSCoR Data
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

        +----------+----------------------------------------------------+-------+
        | Short    | Long                                               | Units |
        +==========+====================================================+=======+
        | pr       | {pr:50} | mm    |
        +----------+----------------------------------------------------+-------+
        | rmax     | {rmax:50} |       |
        +----------+----------------------------------------------------+-------+
        | rmin     | {rmin:50} |       |
        +----------+----------------------------------------------------+-------+
        | sph      | {sph:50} | kg/kg |
        +----------+----------------------------------------------------+-------+
        | srad     | {srad:50} | W/m2  |
        +----------+----------------------------------------------------+-------+
        | tmmn     | {tmmn:50} | degK  |
        +----------+----------------------------------------------------+-------+
        | tmmx     | {tmmx:50} | degK  |
        +----------+----------------------------------------------------+-------+
        | vs       | {vs:50} | m/s   |
        +----------+----------------------------------------------------+-------+
        | bi       | {bi:50} |       |
        +----------+----------------------------------------------------+-------+
        | fm100    | {fm100:50} |       |
        +----------+----------------------------------------------------+-------+
        | fm1000   | {fm1000:50} |       |
        +----------+----------------------------------------------------+-------+
        | erc      | {erc:50} |       |
        +----------+----------------------------------------------------+-------+
        | pdsi     | {pdsi:50} |       |
        +----------+----------------------------------------------------+-------+
        | etr      | {etr:50} |       |
        +----------+----------------------------------------------------+-------+
        | pet      | {pet:50} |       |
        +----------+----------------------------------------------------+-------+
        | vpd      | {vpd:50} |       |
        +----------+----------------------------------------------------+-------+
        | spi14d   | {spi14d:50} |       |
        +----------+----------------------------------------------------+-------+
        | spi30d   | {spi30d:50} |       |
        +----------+----------------------------------------------------+-------+
        | spi90d   | {spi90d:50} |       |
        +----------+----------------------------------------------------+-------+
        | spi180d  | {spi180d:50} |       |
        +----------+----------------------------------------------------+-------+
        | spi270d  | {spi270d:50} |       |
        +----------+----------------------------------------------------+-------+
        | spi1y    | {spi1y:50} |       |
        +----------+----------------------------------------------------+-------+
        | spi2y    | {spi2y:50} |       |
        +----------+----------------------------------------------------+-------+
        | spi5y    | {spi5y:50} |       |
        +----------+----------------------------------------------------+-------+
        | spei14d  | {spei14d:50} |       |
        +----------+----------------------------------------------------+-------+
        | spei30d  | {spei30d:50} |       |
        +----------+----------------------------------------------------+-------+
        | spei90d  | {spei90d:50} |       |
        +----------+----------------------------------------------------+-------+
        | spei180d | {spei180d:50} |       |
        +----------+----------------------------------------------------+-------+
        | spei270d | {spei270d:50} |       |
        +----------+----------------------------------------------------+-------+
        | spei1y   | {spei1y:50} |       |
        +----------+----------------------------------------------------+-------+
        | spei2y   | {spei2y:50} |       |
        +----------+----------------------------------------------------+-------+
        | spei5y   | {spei5y:50} |       |
        +----------+----------------------------------------------------+-------+
        | eddi14d  | {eddi14d:50} |       |
        +----------+----------------------------------------------------+-------+
        | eddi30d  | {eddi30d:50} |       |
        +----------+----------------------------------------------------+-------+
        | eddi90d  | {eddi90d:50} |       |
        +----------+----------------------------------------------------+-------+
        | eddi180d | {eddi180d:50} |       |
        +----------+----------------------------------------------------+-------+
        | eddi270d | {eddi270d:50} |       |
        +----------+----------------------------------------------------+-------+
        | eddi1y   | {eddi1y:50} |       |
        +----------+----------------------------------------------------+-------+
        | eddi2y   | {eddi2y:50} |       |
        +----------+----------------------------------------------------+-------+
        | eddi5y   | {eddi5y:50} |       |
        +----------+----------------------------------------------------+-------+
        | z        | {z:50} |       |
        +----------+----------------------------------------------------+-------+

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


async def dapdownloader(url, lat, lon, vname, vr, start_date, end_date):
    try:
        dataset = (
            xr.open_dataset(url, engine="pydap", cache=True, mask_and_scale=True)
            .sel(lat=lat, lon=lon, method="nearest")[vname]
            .drop_vars(["lat", "lon"])
            .sel(day=slice(start_date, end_date))
        )
    except AttributeError:
        return pd.DataFrame()
    dataset = dataset.rename(_vars[vr])
    ndf = dataset.to_dataframe()
    ndf.columns = [f"{ndf.columns[0]}:{dataset.attrs['units']}"]
    return ndf


async def opendap(variables, lat, lon, start_date=None, end_date=None):

    tasks = []

    if not variables:
        variables = _vars.keys()

    variables = tsutils.make_list(variables)

    nvars = []
    for i in variables:
        aval = ""
        if i in _vars:
            aval = i
        elif i in _inv_vars:
            aval = _inv_vars[i]
        if aval:
            nvars.append(aval)
        else:
            raise ValueError(
                tsutils.error_wrapper(
                    f"""
The variable {i} must be in {_vars.keys()} or in {_inv_vars.keys()}."""
                )
            )

    ndf = pd.DataFrame()
    for vr in nvars:
        # Get and subset the data.
        vname = _vars[vr]
        testname = vr.rstrip("0123456789dy")
        if testname in ["spi", "spei", "eddi"]:
            vname = testname
        url = f"http://thredds.northwestknowledge.net:8080/thredds/dodsC/agg_met_{vr}_1979_CurrentYear_CONUS.nc"
        tasks.append(
            asyncio.create_task(
                dapdownloader(url, lat, lon, vname, vr, start_date, end_date)
            )
        )

    results = await asyncio.gather(*tasks)

    ndf = pd.concat(results, axis="columns", join="outer")

    # Rename the columns to include units of the form "name:unit".
    rename = []
    for name_unit in ndf.columns:
        name, unit = name_unit.split(":")
        if name in ["min_air_temperature", "max_air_temperature"]:
            unit_label = "degK"
        else:
            unit_label = unit
        if unit_label == "Unitless":
            unit_label = ""
        if unit_label == "K":
            unit_label = "degK"
        rename.append("{}:{}".format(name, unit_label))
    ndf.columns = rename

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

    df = asyncio.run(
        opendap(variables, lat, lon, start_date=start_date, end_date=end_date)
    )
    print(df)
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
