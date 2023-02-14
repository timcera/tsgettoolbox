"""
terraclimate19611990
                    global 1/24deg M:Monthly normals using TerraClimate
"""

# http://thredds.northwestknowledge.net:8080/thredds/terraclimate_aggregated.html

import cltoolbox
import pandas as pd
from cltoolbox.rst_text_formatter import RSTHelpFormatter as HelpFormatter
from toolbox_utils import tsutils

from tsgettoolbox import utils

__all__ = ["terraclimate19611990"]

_avail_vars = {
    "aet": {
        "sname": "aet",
        "lname": "actual_et",
        "standard_name": "aet",
        "units": "mm",
        "vname": "TerraClimate19611990_aet.nc",
    },
    "def": {
        "sname": "def",
        "lname": "climate_water_deficit",
        "standard_name": "def",
        "units": "mm",
        "vname": "TerraClimate19611990_def.nc",
    },
    "pet": {
        "sname": "pet",
        "lname": "potential_et",
        "standard_name": "pet",
        "units": "mm",
        "vname": "TerraClimate19611990_pet.nc",
    },
    "ppt": {
        "sname": "ppt",
        "lname": "precipitation",
        "standard_name": "ppt",
        "units": "mm",
        "vname": "TerraClimate19611990_ppt.nc",
    },
    "q": {
        "sname": "q",
        "lname": "runoff",
        "standard_name": "q",
        "units": "mm",
        "vname": "TerraClimate19611990_q.nc",
    },
    "soil": {
        "sname": "soil",
        "lname": "soil_moisture",
        "standard_name": "soil",
        "units": "mm",
        "vname": "TerraClimate19611990_soil.nc",
    },
    "swe": {
        "sname": "swe",
        "lname": "snow_water_equivalent",
        "standard_name": "swe",
        "units": "mm",
        "vname": "TerraClimate19611990_swe.nc",
    },
    "tmin": {
        "sname": "tmin",
        "lname": "minimum_daily_temperature",
        "standard_name": "tmin",
        "units": "degC",
        "vname": "TerraClimate19611990_tmin.nc",
    },
    "tmax": {
        "sname": "tmax",
        "lname": "maximum_daily_temperature",
        "standard_name": "tmax",
        "units": "degC",
        "vname": "TerraClimate19611990_tmax.nc",
    },
}


@cltoolbox.command("terraclimate19611990", formatter_class=HelpFormatter)
@tsutils.doc(tsutils.docstrings)
def terraclimate19611990_cli(
    lat: float,
    lon: float,
    variables=None,
    start_date=None,
    end_date=None,
):
    r"""global 1/24deg M:Monthly normals using TerraClimate monthly data from 1961 to 1990.

    method: These layers from TerraClimate were derived from the essential
    climate variables of TerraClimate. Water balance variables, actual
    evapotranspiration, climatic water deficit, runoff, soil moisture, and snow
    water equivalent were calculated using a water balance model and plant
    extractable soil water capacity derived from Wang-Erlandsson et al (2016).

    title: TerraClimate: monthly climate and climatic water balance for global
    land surfaces

    summary: This archive contains a dataset of high-spatial resolution
    (1/24deg, ~4-km) monthly climate and climatic water balance for global
    terrestrial surfaces from 1958-2015. These data were created by using
    climatically aided interpolation, combining high-spatial resolution
    climatological normals from the WorldClim version 1.4 and version
    2 datasets, with coarser resolution time varying (i.e. monthly) data from
    CRU Ts4.0 and JRA-55 to produce a monthly dataset of precipitation, maximum
    and minimum temperature, wind speed, vapor pressure, and solar radiation.
    TerraClimate additionally produces monthly surface water balance datasets
    using a water balance model that incorporates reference evapotranspiration,
    precipitation, temperature, and interpolated plant extractable soil water
    capacity.

    method: These layers from TerraClimate were creating using climatically
    aided interpolation of monthly anomalies from the CRU Ts4.0 and Japanese
    55-year Reanalysis (JRA-55) datasets with WorldClim v2.0 climatologies.

    keywords: WORLDCLIM,global,monthly,
    temperature,precipitation,wind,radiation,vapor
    pressure,evapotranspiration,water balance,soil water capacity,snow water
    equivalent,runoff

    history: Created by John Abatzoglou, University of California Merced

    creator_url: climate.nkn.uidaho.edu/TerraClimate

    creator_email: jabatzoglou at ucmerced.edu

    institution: University of California Merced

    project: Global Dataset of Monthly Climate and Climatic Water Balance
    (1958-2015)

    acknowledgment: Please cite the references included herein. We also
    acknowledge the WorldClim datasets (Fick and Hijmans, 2017; Hijmans et al.,
    2005) and the CRU Ts4.0 (Harris et al., 2014) and JRA-55 (Kobayashi et al.,
    2015) datasets.

    geospatial_lat_min: -89.979164

    geospatial_lat_max: 89.979164

    geospatial_lon_min: -179.97917

    geospatial_lon_max: 179.97917

    time_coverage_start: 1958-01-01T00:0

    time_coverage_end: present

    time_coverage_resolution: P1M

    standard_nam_vocabulary: CF-1.0

    license: No restrictions

    geospatial_lat_units: decimal degrees north

    geospatial_lat_resolution: -0.041666668

    geospatial_lon_units: decimal degrees east

    geospatial_lon_resolution: 0.041666668

    references: Abatzoglou, J.T., S.Z. Dobrowski, S.A. Parks, and K.C.
    Hegewisch, 2017, High-resolution global dataset of monthly climate and
    climatic water balance from 1958-2015, submitted to Scientific Data.

    source: WorldClim v2.0 (2.5m), CRU Ts4.0, JRA-55

    version: v1.0

    Conventions: CF-1.6

    Parameters
    ----------
    ${lat}

    ${lon}

    variables : str
        At the command line can supply a comma separated list of variable
        names.  Using the Python API needs to be a Python list of strings.

        The current list of available variables are in the following table.

        +--------+----------------------------------+-----------+
        | Short  | Long                             | Units     |
        +========+==================================+===========+
        | aet    | Actual ET                        | mm        |
        +--------+----------------------------------+-----------+
        | def    | Climate water deficit            | mm        |
        +--------+----------------------------------+-----------+
        | pet    | Reference ET                     | mm        |
        +--------+----------------------------------+-----------+
        | q      | Runoff                           | mm        |
        +--------+----------------------------------+-----------+
        | soil   | Soil moisture                    | mm        |
        +--------+----------------------------------+-----------+
        | swe    | Snow water equivalence           | mm        |
        +--------+----------------------------------+-----------+
        | tmax   | maximum temperature              | degC      |
        +--------+----------------------------------+-----------+
        | tmin   | minimum temperature              | degC      |
        +--------+----------------------------------+-----------+
        | vap    | Vapor pressure                   | kPa       |
        +--------+----------------------------------+-----------+
        | vpd    | Vapor pressure deficit           | kPa       |
        +--------+----------------------------------+-----------+
        | ws     | wind_speed                       | m/s       |
        +--------+----------------------------------+-----------+

    ${start_date}

    ${end_date}
    """
    tsutils.printiso(
        terraclimate19611990(
            lat,
            lon,
            variables=variables,
            start_date=start_date,
            end_date=end_date,
        )
    )


@tsutils.transform_args(start_date=pd.to_datetime, end_date=pd.to_datetime)
@tsutils.copy_doc(terraclimate19611990_cli)
def terraclimate19611990(
    lat: float,
    lon: float,
    variables=None,
    start_date=None,
    end_date=None,
):
    r"""Download terraclimate data."""
    turl = "http://thredds.northwestknowledge.net:8080/thredds/dodsC/TERRACLIMATE_ALL/summaries/TerraClimate19611990_{}.nc"

    df = utils.opendap(
        turl,
        lat,
        lon,
        _avail_vars,
        variables=variables,
        start_date=start_date,
        end_date=end_date,
        time_name="time",
        single_var_url=True,
    )

    df = df.rename(columns=lambda x: f"{x}:19611990")

    return df


if __name__ == "__main__":
    r = terraclimate19611990(29.6, -82.3)
    print(r)
