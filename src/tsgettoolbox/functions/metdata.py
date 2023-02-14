"""
metdata             NAmerica 4km 1980- D: Download daily data from METDATA
                    based on PRISM.
"""

import cltoolbox
from cltoolbox.rst_text_formatter import RSTHelpFormatter as HelpFormatter
from toolbox_utils import tsutils

from tsgettoolbox import utils

__all__ = ["metdata"]

_vars = {
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
    # Commented out because it has an unusual URL.
    #    "spi270d": {
    #        "sname": "spi",
    #        "lname": "standard_precipitation_index_270_day",
    #        "standard_name": "spi",
    #        "vname": "METDATA (GRIDMET) 270 Day Standardized Precipitation Index(SPI) - Pentad",
    #    },
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

tsutils.docstrings.update({k: f"{v['standard_name']:50}" for k, v in _vars.items()})


@cltoolbox.command("metdata", formatter_class=HelpFormatter)
@tsutils.doc(tsutils.docstrings)
def metdata_cli(
    lat,
    lon,
    variables=None,
    start_date=None,
    end_date=None,
):
    r"""NAmerica 4km 1980- D: Download daily data from METDATA based on PRISM.

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
    ${lat}

    ${lon}

    variables : str
        At the command line can supply a comma separated list of variable
        names.  Using the Python API needs to be a Python list of strings.

        The current list of available METDATA variables are in the following table and
        you can use either the "Short" or "Long" names.

        +----------+----------------------------------------------------+-------+
        | Short    | Long                                               | Units |
        +==========+====================================================+=======+
        | pr       | ${pr} | mm    |
        +----------+----------------------------------------------------+-------+
        | rmax     | ${rmax} |       |
        +----------+----------------------------------------------------+-------+
        | rmin     | ${rmin} |       |
        +----------+----------------------------------------------------+-------+
        | sph      | ${sph} | kg/kg |
        +----------+----------------------------------------------------+-------+
        | srad     | ${srad} | W/m2  |
        +----------+----------------------------------------------------+-------+
        | tmmn     | ${tmmn} | degK  |
        +----------+----------------------------------------------------+-------+
        | tmmx     | ${tmmx} | degK  |
        +----------+----------------------------------------------------+-------+
        | vs       | ${vs} | m/s   |
        +----------+----------------------------------------------------+-------+
        | bi       | ${bi} |       |
        +----------+----------------------------------------------------+-------+
        | fm100    | ${fm100} |       |
        +----------+----------------------------------------------------+-------+
        | fm1000   | ${fm1000} |       |
        +----------+----------------------------------------------------+-------+
        | erc      | ${erc} |       |
        +----------+----------------------------------------------------+-------+
        | pdsi     | ${pdsi} |       |
        +----------+----------------------------------------------------+-------+
        | etr      | ${etr} |       |
        +----------+----------------------------------------------------+-------+
        | pet      | ${pet} |       |
        +----------+----------------------------------------------------+-------+
        | vpd      | ${vpd} |       |
        +----------+----------------------------------------------------+-------+
        | spi14d   | ${spi14d} |       |
        +----------+----------------------------------------------------+-------+
        | spi30d   | ${spi30d} |       |
        +----------+----------------------------------------------------+-------+
        | spi90d   | ${spi90d} |       |
        +----------+----------------------------------------------------+-------+
        | spi180d  | ${spi180d} |       |
        +----------+----------------------------------------------------+-------+
        | spi1y    | ${spi1y} |       |
        +----------+----------------------------------------------------+-------+
        | spi2y    | ${spi2y} |       |
        +----------+----------------------------------------------------+-------+
        | spi5y    | ${spi5y} |       |
        +----------+----------------------------------------------------+-------+
        | spei14d  | ${spei14d} |       |
        +----------+----------------------------------------------------+-------+
        | spei30d  | ${spei30d} |       |
        +----------+----------------------------------------------------+-------+
        | spei90d  | ${spei90d} |       |
        +----------+----------------------------------------------------+-------+
        | spei180d | ${spei180d} |       |
        +----------+----------------------------------------------------+-------+
        | spei270d | ${spei270d} |       |
        +----------+----------------------------------------------------+-------+
        | spei1y   | ${spei1y} |       |
        +----------+----------------------------------------------------+-------+
        | spei2y   | ${spei2y} |       |
        +----------+----------------------------------------------------+-------+
        | spei5y   | ${spei5y} |       |
        +----------+----------------------------------------------------+-------+
        | eddi14d  | ${eddi14d} |       |
        +----------+----------------------------------------------------+-------+
        | eddi30d  | ${eddi30d} |       |
        +----------+----------------------------------------------------+-------+
        | eddi90d  | ${eddi90d} |       |
        +----------+----------------------------------------------------+-------+
        | eddi180d | ${eddi180d} |       |
        +----------+----------------------------------------------------+-------+
        | eddi270d | ${eddi270d} |       |
        +----------+----------------------------------------------------+-------+
        | eddi1y   | ${eddi1y} |       |
        +----------+----------------------------------------------------+-------+
        | eddi2y   | ${eddi2y} |       |
        +----------+----------------------------------------------------+-------+
        | eddi5y   | ${eddi5y} |       |
        +----------+----------------------------------------------------+-------+
        | z        | ${z} |       |
        +----------+----------------------------------------------------+-------+

    ${start_date}

    ${end_date}
    """
    tsutils.printiso(
        metdata(
            lat,
            lon,
            variables=variables,
            start_date=start_date,
            end_date=end_date,
        )
    )


@tsutils.copy_doc(metdata_cli)
def metdata(
    lat,
    lon,
    variables=None,
    start_date=None,
    end_date=None,
):
    r"""Download METDATA data."""
    if variables is None:
        cvars = sorted(_vars.keys())
    else:
        cvars = tsutils.make_list(variables)

    turl = "http://thredds.northwestknowledge.net:8080/thredds/dodsC/agg_met_{}_1979_CurrentYear_CONUS.nc"
    # turl = "http://thredds.northwestknowledge.net:8080/thredds/ncss/grid/agg_met_{}_1979_CurrentYear_CONUS.nc"
    return utils.opendap(
        turl,
        lat,
        lon,
        _vars,
        variables=cvars,
        start_date=start_date,
        end_date=end_date,
        tzname=None,
        missing_value=-9999,
        time_name="day",
        single_var_url=True,
    )


if __name__ == "__main__":
    r = metdata(29.6, -82.3, variables="pr")
    print(r)
