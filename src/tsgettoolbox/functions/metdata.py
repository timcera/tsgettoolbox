# -*- coding: utf-8 -*-
"""Download data from Florida Automated Weather Network (FAWN)."""

import mando

try:
    from mando.rst_text_formatter import RSTHelpFormatter as HelpFormatter
except ImportError:
    from argparse import RawTextHelpFormatter as HelpFormatter

from tstoolbox import tsutils

from tsgettoolbox import utils

_avail_vars = {
    "pr": {
        "sname": "pr",
        "lname": "precipitation_amount",
        "standard_name": "precipitation_amount",
        "vname": "METDATA (GRIDMET) Precipitation - Daily",
    },
    "rmin": {
        "sname": "rmin",
        "lname": "daily_minimum_relative_humidity",
        "standard_name": "daily_minimum_relative_humidity",
        "vname": "METDATA (GRIDMET) Minimum Relative Humidity - Daily",
    },
    "rmax": {
        "sname": "rmax",
        "lname": "daily_maximum_relative_humidity",
        "standard_name": "daily_maximum_relative_humidity",
        "vname": "METDATA (GRIDMET) Maximum Relative Humidity - Daily",
    },
    "sph": {
        "sname": "sph",
        "lname": "daily_mean_specific_humidity",
        "standard_name": "daily_mean_specific_humidity",
        "vname": "METDATA (GRIDMET) Specific Humidity - Daily",
    },
    "srad": {
        "sname": "srad",
        "lname": "daily_mean_shortwave_radiation_at_surface",
        "standard_name": "daily_mean_shortwave_radiation_at_surface",
        "vname": "METDATA (GRIDMET) Surface Radiation - Daily",
    },
    "tmmn": {
        "sname": "tmmn",
        "lname": "daily_minimum_temperature",
        "standard_name": "daily_minimum_temperature",
        "vname": "METDATA (GRIDMET) Minimum Air Temperature - Daily",
    },
    "tmmx": {
        "sname": "tmmx",
        "lname": "daily_maximum_temperature",
        "standard_name": "daily_maximum_temperature",
        "vname": "METDATA (GRIDMET) Maximum Air Temperature - Daily",
    },
    "vs": {
        "sname": "vs",
        "lname": "daily_mean_wind_speed",
        "standard_name": "daily_mean_wind_speed",
        "vname": "METDATA (GRIDMET) Wind Speed - Daily",
    },
    "th": {
        "sname": "th",
        "lname": "daily_mean_wind_direction",
        "standard_name": "daily_mean_wind_direction",
        "vname": "METDATA (GRIDMET) Wind Direction - Daily",
    },
    "bi": {
        "sname": "bi",
        "lname": "daily_mean_burning_index_g",
        "standard_name": "daily_mean_burning_index_g",
        "vname": "METDATA (GRIDMET) Burning Index - Daily",
    },
    "fm100": {
        "sname": "fm100",
        "lname": "dead_fuel_moisture_100hr",
        "standard_name": "dead_fuel_moisture_100hr",
        "vname": "METDATA (GRIDMET) Fuel Moisture (100-hr) - Daily",
    },
    "fm1000": {
        "sname": "fm1000",
        "lname": "dead_fuel_moisture_1000hr",
        "standard_name": "dead_fuel_moisture_1000hr",
        "vname": "METDATA (GRIDMET) Fuel Moisture (1000-hr) - Daily",
    },
    "erc": {
        "sname": "erc",
        "lname": "daily_mean_energy_release_component-g",
        "standard_name": "daily_mean_energy_release_component-g",
        "vname": "METDATA (GRIDMET) Energy Release Component - Daily",
    },
    "pdsi": {
        "sname": "pdsi",
        "lname": "daily_mean_palmer_drought_severity_index",
        "standard_name": "daily_mean_palmer_drought_severity_index",
        "vname": "METDATA (GRIDMET) Palmer Drought Severity Index(PDSI) - Pentad",
    },
    "etr": {
        "sname": "etr",
        "lname": "daily_mean_reference_evapotranspiration_alfalfa",
        "standard_name": "daily_mean_reference_evapotranspiration_alfalfa",
        "vname": "METDATA (GRIDMET) Reference Evapotranspiration (Alfalfa) - Daily",
    },
    "pet": {
        "sname": "pet",
        "lname": "daily_mean_reference_evapotranspiration_grass",
        "standard_name": "daily_mean_reference_evapotranspiration_grass",
        "vname": "METDATA (GRIDMET) Reference Evapotranspiration (Grass) - Daily",
    },
    "vpd": {
        "sname": "vpd",
        "lname": "daily_mean_vapor_pressure_deficit",
        "standard_name": "daily_mean_vapor_pressure_deficit",
        "vname": "METDATA (GRIDMET) Vapor Pressure Deficit - Daily",
    },
    "spi14d": {
        "sname": "spi",
        "lname": "standard_precipitation_index_14_day",
        "standard_name": "spi",
        "vname": "METDATA (GRIDMET) 14 Day Standardized Precipitation Index(SPI) - Pentad",
    },
    "spi30d": {
        "sname": "spi",
        "lname": "standard_precipitation_index_30_day",
        "standard_name": "spi",
        "vname": "METDATA (GRIDMET) 30 Day Standardized Precipitation Index(SPI) - Pentad",
    },
    "spi90d": {
        "sname": "spi",
        "lname": "standard_precipitation_index_90_day",
        "standard_name": "spi",
        "vname": "METDATA (GRIDMET) 90 Day Standardized Precipitation Index(SPI) - Pentad",
    },
    "spi180d": {
        "sname": "spi",
        "lname": "standard_precipitation_index_180_day",
        "standard_name": "spi",
        "vname": "METDATA (GRIDMET) 180 Day Standardized Precipitation Index(SPI) - Pentad",
    },
    "spi270d": {
        "sname": "spi",
        "lname": "standard_precipitation_index_270_day",
        "standard_name": "spi",
        "vname": "METDATA (GRIDMET) 270 Day Standardized Precipitation Index(SPI) - Pentad",
    },
    "spi1y": {
        "sname": "spi",
        "lname": "standard_precipitation_index_1_year",
        "standard_name": "spi",
        "vname": "METDATA (GRIDMET) 1 Year Standardized Precipitation Index(SPI) - Pentad",
    },
    "spi2y": {
        "sname": "spi",
        "lname": "standard_precipitation_index_2_year",
        "standard_name": "spi",
        "vname": "METDATA (GRIDMET) 2 Year Standardized Precipitation Index(SPI) - Pentad",
    },
    "spi5y": {
        "sname": "spi",
        "lname": "standard_precipitation_index_5_year",
        "standard_name": "spi",
        "vname": "METDATA (GRIDMET) 5 Year Standardized Precipitation Index(SPI) - Pentad",
    },
    "spei14d": {
        "sname": "spei",
        "lname": "standard_precipitation_evapotranspiration_index_14_day",
        "standard_name": "spei",
        "vname": "METDATA (GRIDMET) 14 Day Standardized Precipitation Evapotranspiration Index(SPEI) - Pentad",
    },
    "spei30d": {
        "sname": "spei",
        "lname": "standard_precipitation_evapotranspiration_index_30_day",
        "standard_name": "spei",
        "vname": "METDATA (GRIDMET) 30 Day Standardized Precipitation Evapotranspiration Index(SPEI) - Pentad",
    },
    "spei90d": {
        "sname": "spei",
        "lname": "standard_precipitation_evapotranspiration_index_90_day",
        "standard_name": "spei",
        "vname": "METDATA (GRIDMET) 90 Day Standardized Precipitation Evapotranspiration Index(SPEI) - Pentad",
    },
    "spei180d": {
        "sname": "spei",
        "lname": "standard_precipitation_evapotranspiration_index_180_day",
        "standard_name": "spei",
        "vname": "METDATA (GRIDMET) 180 Day Standardized Precipitation Evapotranspiration Index(SPEI) - Pentad",
    },
    "spei270d": {
        "sname": "spei",
        "lname": "standard_precipitation_evapotranspiration_index_270_day",
        "standard_name": "spei",
        "vname": "METDATA (GRIDMET) 270 Day Standardized Precipitation Evapotranspiration Index(SPEI) - Pentad",
    },
    "spei1y": {
        "sname": "spei",
        "lname": "standard_precipitation_evapotranspiration_index_1_year",
        "standard_name": "spei",
        "vname": "METDATA (GRIDMET) 1 Year Standardized Precipitation Evapotranspiration Index(SPEI) - Pentad",
    },
    "spei2y": {
        "sname": "spei",
        "lname": "standard_precipitation_evapotranspiration_index_2_year",
        "standard_name": "spei",
        "vname": "METDATA (GRIDMET) 2 Year Standardized Precipitation Evapotranspiration Index(SPEI) - Pentad",
    },
    "spei5y": {
        "sname": "spei",
        "lname": "standard_precipitation_evapotranspiration_index_5_year",
        "standard_name": "spei",
        "vname": "METDATA (GRIDMET) 5 Year Standardized Precipitation Evapotranspiration Index(SPEI) - Pentad",
    },
    "eddi14d": {
        "sname": "eddi",
        "lname": "evaporative_drought_demand_index_14_day",
        "standard_name": "eddi",
        "vname": "METDATA (GRIDMET) 14 Day Evaporative Drought Demand Index(EDDI) - Pentad",
    },
    "eddi30d": {
        "sname": "eddi",
        "lname": "evaporative_drought_demand_index_30_day",
        "standard_name": "eddi",
        "vname": "METDATA (GRIDMET) 30 Day Evaporative Drought Demand Index(EDDI) - Pentad",
    },
    "eddi90d": {
        "sname": "eddi",
        "lname": "evaporative_drought_demand_index_90_day",
        "standard_name": "eddi",
        "vname": "METDATA (GRIDMET) 90 Day Evaporative Drought Demand Index(EDDI) - Pentad",
    },
    "eddi180d": {
        "sname": "eddi",
        "lname": "evaporative_drought_demand_index_180_day",
        "standard_name": "eddi",
        "vname": "METDATA (GRIDMET) 180 Day Evaporative Drought Demand Index(EDDI) - Pentad",
    },
    "eddi270d": {
        "sname": "eddi",
        "lname": "evaporative_drought_demand_index_270_day",
        "standard_name": "eddi",
        "vname": "METDATA (GRIDMET) 270 Day Evaporative Drought Demand Index(EDDI) - Pentad",
    },
    "eddi1y": {
        "sname": "eddi",
        "lname": "evaporative_drought_demand_index_1_year",
        "standard_name": "eddi",
        "vname": "METDATA (GRIDMET) 1 Year Evaporative Drought Demand Index(EDDI) - Pentad",
    },
    "eddi2y": {
        "sname": "eddi",
        "lname": "evaporative_drought_demand_index_2_year",
        "standard_name": "eddi",
        "vname": "METDATA (GRIDMET) 2 Year Evaporative Drought Demand Index(EDDI) - Pentad",
    },
    "eddi5y": {
        "sname": "eddi",
        "lname": "evaporative_drought_demand_index_5_year",
        "standard_name": "eddi",
        "vname": "METDATA (GRIDMET) 5 Year Evaporative Drought Demand Index(EDDI) - Pentad",
    },
    "z": {
        "sname": "z",
        "lname": "daily_mean_palmer_z_index",
        "standard_name": "daily_mean_palmer_z_index",
        "vname": "METDATA (GRIDMET) Palmer Z Index(Z) - Pentad",
    },
}


tsutils.docstrings.update({k: v["standard_name"] for k, v in _avail_vars.items()})


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


def metdata(
    lat,
    lon,
    variables=None,
    start_date=None,
    end_date=None,
):
    r"""Download METDATA data from CIDA."""

    turl = [
        "http://thredds.northwestknowledge.net:8080/thredds/ncss/grid/agg_met_{var}_1979_CurrentYear_CONUS.nc/",
        "http://thredds.northwestknowledge.net:8080/thredds/ncss/grid/agg_met_{var}_CONUS.nc/",
    ]

    df = utils.opendap(
        turl,
        variables,
        lat,
        lon,
        _avail_vars,
        start_date=start_date,
        end_date=end_date,
        all_vars_at_url=False,
    )

    if len(df.dropna(how="all")) == 0:
        if start_date is None:
            start_date = "beginning of record"
        if end_date is None:
            end_date = "end of record"
        raise ValueError(
            tsutils.error_wrapper(
                """
GRIDMET returned no data for lat/lon "{lat}/{lon}", variables "{variables}"
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
