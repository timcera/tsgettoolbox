"""
topowx              US 30arcsecond 1948- M:Topoclimatic Monthly Air
                    Temperature Dataset.
topowx_daily        US 30arcsecond 1948- D:Topoclimatic Daily Air
                    Temperature Dataset.
"""

import cltoolbox
from cltoolbox.rst_text_formatter import RSTHelpFormatter as HelpFormatter
from toolbox_utils import tsutils

from tsgettoolbox import utils

__all__ = [
    "topowx",
    "topowx_daily",
]

_base_avail_vars = {
    "tmin": {
        "sname": "tmin",
        "lname": "daily_minimum_temperature",
        "standard_name": "daily_minimum_temperature",
        "vname": "Daily Minimum Temperature",
    },
    "tmax": {
        "sname": "tmax",
        "lname": "daily_maximum_temperature",
        "standard_name": "daily_maximum_temperature",
        "vname": "Daily Maximum Temperature",
    },
}


tsutils.docstrings.update({k: v["standard_name"] for k, v in _base_avail_vars.items()})


@cltoolbox.command("topowx", formatter_class=HelpFormatter)
@tsutils.doc(tsutils.docstrings)
def topowx_cli(
    lat,
    lon,
    variables=None,
    start_date=None,
    end_date=None,
):
    r"""US 30arcsecond 1948- M:Topoclimatic Monthly Air Temperature Dataset.

    institution: USGS

    history: Created on: 2017-07-06, dataset version 2016.1

    references: http://dx.doi.org/10.1002/joc.4127
    , http://dx.doi.org/10.1002/2014GL062803
    , http://dx.doi.org/10.1175/JAMC-D-15-0276.1

    comment: The TopoWx ('Topography Weather') gridded dataset contains daily
    30-arcsec resolution (~800-m resolution; WGS84) interpolations of minimum
    and maximum topoclimatic air temperature for the conterminous U.S. Using
    both DEM-based variables and MODIS land skin temperature as predictors of
    air temperature, interpolation procedures include moving window regression
    kriging and geographically weighted regression. To avoid artificial climate
    trends, all input station data are homogenized using the GHCN/USHCN
    Pairwise Homogenization Algorithm
    (http://www.ncdc.noaa.gov/oa/climate/research/ushcn/#phas).

    Conventions: CF-1.6

    source: TopoWx software version 1.3.0 (https://github.com/jaredwo/topowx)

    license: This work is licensed under a Creative Commons
    Attribution-ShareAlike 4.0 International License
    (https://creativecommons.org/licenses/by-sa/4.0/).

    Metadata_Conventions: Unidata Dataset Discovery v1.0

    summary: The TopoWx ('Topography Weather') dataset contains historical
    30-arcsec resolution (~800-m) interpolations of daily minimum and maximum
    topoclimatic air temperature for the conterminous U.S. Using both DEM-based
    variables and MODIS land skin temperature as predictors of air temperature,
    interpolation procedures include moving window regression kriging and
    geographically weighted regression. To avoid artificial climate trends, all
    input station data are homogenized using the GHCN/USHCN Pairwise
    Homogenization Algorithm
    (http://www.ncdc.noaa.gov/oa/climate/research/ushcn/#phas). The following
    data are available in this archive: 1948-2016 daily and monthly minimum and
    maximum temperature, and 1981-2010 monthly normals for minimum and maximum
    temperature with corresponding uncertainty (kriging prediction error).
    Ongoing annual updates will regenerate the entire dataset incorporating
    both new observations and model enhancements. This will result in
    a continuously improved dataset. However, different versions of TopoWx will
    be incompatible. For instance, data from the original 1948-2012 version
    should not be mixed with data from the new 1948-2016 version.

    keywords: maximum temperature, minimum temperature, land skin temperature,
    MODIS, kriging, homogenization, gridded meteorological data

    id: topowx

    naming_authority: cida.usgs.gov

    cdm_data_type: Grid

    date_created: 2017-07-06

    creator_name: Jared Oyler

    creator_url: http://www.scrimhub.org

    creator_email: jared.oyler@psu.edu

    publisher_name: Office of Water Information

    publisher_url: https://owi.usgs.gov/

    publisher_email: wwatkins@usgs.gov

    date_issued: 2017-08-18

    project: TopoWx: Topoclimatic Daily Air Temperature Dataset for the
    Conterminous United States

    processing_level: Historical Gridded Meteorological Data

    acknowledgement: Please cite this data as: Oyler JW, Ballantyne A, Jencso
    K, Sweet M, Running S. Creating a Topoclimatic Daily Air Temperature
    Dataset for the Conterminous United States using Homogenized Station Data
    and Remotely Sensed Land Skin Temperature. International Journal of
    Climatology. http://dx.doi.org/10.1002/joc.4127

    geospatial_lat_min: 24.1

    geospatial_lat_max: 51.2

    geospatial_lon_min: -125

    geospatial_lon_max: -99.7

    time_coverage_start: 1948-01-01T00:00:00

    time_coverage_end: 2016-12-31T00:00:00

    time_coverage_resolution: P1D

    Parameters
    ----------
    ${lat}

    ${lon}

    variables : str
        At the command line can supply a comma separated list of variable
        names.  Using the Python API needs to be a Python list of strings.

        The current list of available topowx variables are daily minimum
        temperature (tmin) and daily maximum temperature (tmax).

    ${start_date}

    ${end_date}
    """
    tsutils.printiso(
        topowx(
            lat,
            lon,
            variables=variables,
            start_date=start_date,
            end_date=end_date,
        )
    )


@cltoolbox.command("topowx_daily", formatter_class=HelpFormatter)
@tsutils.doc(tsutils.docstrings)
def topowx_daily_cli(
    lat,
    lon,
    variables=None,
    start_date=None,
    end_date=None,
):
    r"""US 30arcsecond 1948- D:Topoclimatic Daily Air Temperature Dataset.

    institution: USGS

    history: Created on: 2017-07-06, dataset version 2016.1

    references: http://dx.doi.org/10.1002/joc.4127
    , http://dx.doi.org/10.1002/2014GL062803
    , http://dx.doi.org/10.1175/JAMC-D-15-0276.1

    comment: The TopoWx ('Topography Weather') gridded dataset contains daily
    30-arcsec resolution (~800-m resolution; WGS84) interpolations of minimum
    and maximum topoclimatic air temperature for the conterminous U.S. Using
    both DEM-based variables and MODIS land skin temperature as predictors of
    air temperature, interpolation procedures include moving window regression
    kriging and geographically weighted regression. To avoid artificial climate
    trends, all input station data are homogenized using the GHCN/USHCN
    Pairwise Homogenization Algorithm
    (http://www.ncdc.noaa.gov/oa/climate/research/ushcn/#phas).

    Conventions: CF-1.6

    source: TopoWx software version 1.3.0 (https://github.com/jaredwo/topowx)

    license: This work is licensed under a Creative Commons
    Attribution-ShareAlike 4.0 International License
    (https://creativecommons.org/licenses/by-sa/4.0/).

    Metadata_Conventions: Unidata Dataset Discovery v1.0

    summary: The TopoWx ('Topography Weather') dataset contains historical
    30-arcsec resolution (~800-m) interpolations of daily minimum and maximum
    topoclimatic air temperature for the conterminous U.S. Using both DEM-based
    variables and MODIS land skin temperature as predictors of air temperature,
    interpolation procedures include moving window regression kriging and
    geographically weighted regression. To avoid artificial climate trends, all
    input station data are homogenized using the GHCN/USHCN Pairwise
    Homogenization Algorithm
    (http://www.ncdc.noaa.gov/oa/climate/research/ushcn/#phas). The following
    data are available in this archive: 1948-2016 daily and monthly minimum and
    maximum temperature, and 1981-2010 monthly normals for minimum and maximum
    temperature with corresponding uncertainty (kriging prediction error).
    Ongoing annual updates will regenerate the entire dataset incorporating
    both new observations and model enhancements. This will result in
    a continuously improved dataset. However, different versions of TopoWx will
    be incompatible. For instance, data from the original 1948-2012 version
    should not be mixed with data from the new 1948-2016 version.

    keywords: maximum temperature, minimum temperature, land skin temperature,
    MODIS, kriging, homogenization, gridded meteorological data

    id: topowx

    naming_authority: cida.usgs.gov

    cdm_data_type: Grid

    date_created: 2017-07-06

    creator_name: Jared Oyler

    creator_url: http://www.scrimhub.org

    creator_email: jared.oyler@psu.edu

    publisher_name: Office of Water Information

    publisher_url: https://owi.usgs.gov/

    publisher_email: wwatkins@usgs.gov

    date_issued: 2017-08-18

    project: TopoWx: Topoclimatic Daily Air Temperature Dataset for the
    Conterminous United States

    processing_level: Historical Gridded Meteorological Data

    acknowledgement: Please cite this data as: Oyler JW, Ballantyne A, Jencso
    K, Sweet M, Running S. Creating a Topoclimatic Daily Air Temperature
    Dataset for the Conterminous United States using Homogenized Station Data
    and Remotely Sensed Land Skin Temperature. International Journal of
    Climatology. http://dx.doi.org/10.1002/joc.4127

    geospatial_lat_min: 24.1

    geospatial_lat_max: 51.2

    geospatial_lon_min: -125

    geospatial_lon_max: -99.7

    time_coverage_start: 1948-01-01T00:00:00

    time_coverage_end: 2016-12-31T00:00:00

    time_coverage_resolution: P1D

    Parameters
    ----------
    ${lat}

    ${lon}

    variables : str
        At the command line can supply a comma separated list of variable
        names.  Using the Python API needs to be a Python list of strings.

        The current list of available topowx variables are daily minimum
        temperature (tmin) and daily maximum temperature (tmax).

    ${start_date}

    ${end_date}
    """
    tsutils.printiso(
        topowx_daily(
            lat,
            lon,
            variables=variables,
            start_date=start_date,
            end_date=end_date,
        )
    )


@tsutils.copy_doc(topowx_cli)
def topowx(
    lat,
    lon,
    variables=None,
    start_date=None,
    end_date=None,
):
    r"""Download topowx data from CIDA."""
    url = "https://cida.usgs.gov/thredds/dodsC/topowx_monthly"

    return utils.opendap(
        url,
        lat,
        lon,
        _base_avail_vars,
        variables=variables,
        start_date=start_date,
        end_date=end_date,
        time_name="time",
    )


@tsutils.copy_doc(topowx_daily_cli)
def topowx_daily(
    lat,
    lon,
    variables=None,
    start_date=None,
    end_date=None,
):
    r"""Download topowx data from CIDA."""
    url = "https://cida.usgs.gov/thredds/dodsC/topowx"

    return utils.opendap(
        url,
        lat,
        lon,
        _base_avail_vars,
        variables=variables,
        start_date=start_date,
        end_date=end_date,
        time_name="time",
    )


if __name__ == "__main__":
    print("topoWX")
    r = topowx(29.6, -82.3, "tmin")
    print(r)
    print("topoWX_DAILY")
    r = topowx_daily(
        29.6, -82.3, "tmin", start_date="2000-01-01", end_date="2000-01-31"
    )
    print(r)
