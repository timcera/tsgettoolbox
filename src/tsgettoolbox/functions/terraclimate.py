# -*- coding: utf-8 -*-
"""Download data from terraclimate."""

# http://thredds.northwestknowledge.net:8080/thredds/terraclimate_aggregated.html

from datetime import date, datetime

import mando
import numpy as np
import pandas as pd

try:
    from mando.rst_text_formatter import RSTHelpFormatter as HelpFormatter
except ImportError:
    from argparse import RawTextHelpFormatter as HelpFormatter

from tstoolbox import tsutils

_vars = {
    "aet": {"long_name": "actual_et", "units": "mm"},
    "def": {"long_name": "climate_water_defecit", "units": "mm"},
    "pet": {"long_name": "potential_et", "units": "mm"},
    "ppt": {"long_name": "precipitation", "units": "mm"},
    "PDSI": {"long_name": "palmer_drought_index", "units": ""},
    "q": {"long_name": "runoff", "units": "mm"},
    "soil": {"long_name": "soil_moisture", "units": "mm"},
    "srad": {"long_name": "downward_shortwave_radiation", "units": "W/m**2"},
    "swe": {"long_name": "snow_water_equivalent", "units": "mm"},
    "tmin": {"long_name": "tmin", "units": "degC"},
    "tmax": {"long_name": "tmax", "units": "degC"},
    "vap": {"long_name": "vapor_pressure", "units": "kPa"},
    "vpd": {"long_name": "vapor_pressure_deficit", "units": "kPa"},
    "ws": {"long_name": "wind_speed_2m", "units": "m/s"},
}


@mando.command("terraclimate", formatter_class=HelpFormatter, doctype="numpy")
@tsutils.doc(tsutils.docstrings)
def terraclimate_cli(
    lat: float,
    lon: float,
    variables=None,
    start_date=None,
    end_date=None,
):
    r"""Download monthly data from Terraclimate.

    method: These layers from TerraClimate were derived from the essential
    climate variables of TerraClimate. Water balance variables, actual
    evapotranspiration, climatic water deficit, runoff, soil moisture, and snow
    water equivalent were calculated using a water balance model and plant
    extractable soil water capacity derived from Wang-Erlandsson et al (2016).

    title: TerraClimate: monthly climate and climatic water balance for global
    land surfaces

    summary: This archive contains a dataset of high-spatial resolution
    (1/24Â°, ~4-km) monthly climate and climatic water balance for global
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

    keywords: WORLDCLIM,global,monthly,
    temperature,precipitation,wind,radiation,vapor
    pressure,evapotranspiration,water balance,soil water capacity,snow water
    equivalent,runoff

    naming_authority: edu.uidaho.nkn

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
    {lat}

    {lon}

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
        | PDSI   | Palmer Drought Severity Index    |           |
        +--------+----------------------------------+-----------+
        | pet    | Reference ET                     | mm        |
        +--------+----------------------------------+-----------+
        | q      | Runoff                           | mm        |
        +--------+----------------------------------+-----------+
        | soil   | Soil moisture                    | mm        |
        +--------+----------------------------------+-----------+
        | srad   | Downwelling solar shortwave      | W/m^2     |
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

    {start_date}

    {end_date}
    """
    tsutils._printiso(
        terraclimate(
            lat,
            lon,
            variables=variables,
            start_date=start_date,
            end_date=end_date,
        )
    )


def opendap(variables, lat, lon, start_date=None, end_date=None):
    from netCDF4 import Dataset, num2date

    turl = "http://thredds.northwestknowledge.net:8080/thredds/dodsC/agg_terraclimate_{0}_1958_CurrentYear_GLOBE.nc"

    if not variables:
        variables = _vars.keys()

    variables = tsutils.make_list(variables)

    ndf = pd.DataFrame()
    time = None
    for var in variables:
        # Get and subset the data.
        url = turl.format(var)

        filehandle = Dataset(url, "r", format="NETCDF4")
        datahandle = filehandle.variables[var]
        scale_factor = datahandle.scale_factor
        add_offset = datahandle.add_offset

        if time is None:
            timehandle = filehandle.variables["time"]
            time = timehandle[:]
            if start_date is None:
                time_index_min = 0
            else:
                time_min = (
                    date(start_date.year, start_date.month, 1) - date(1900, 1, 1)
                ).days
                time_index_min = (np.abs(time - time_min)).argmin()
            if end_date is None:
                time_index_max = -1
            else:
                time_max = (
                    date(end_date.year, end_date.month, 1) - date(1900, 1, 1)
                ).days
                time_index_max = (np.abs(time - time_max)).argmin() + 1
            time = num2date(timehandle[time_index_min:time_index_max], timehandle.units)
            time = [
                datetime(i.year, i.month, i.day, i.hour, i.minute, i.second)
                for i in time
            ]
            time = pd.to_datetime(time)

        # subset in space (lat/lon)
        lathandle = filehandle.variables["lat"]
        lonhandle = filehandle.variables["lon"]
        latgrid = lathandle[:]
        longrid = lonhandle[:]

        # find indices of target lat/lon/day
        lat_index = (np.abs(latgrid - lat)).argmin()
        lon_index = (np.abs(longrid - lon)).argmin()

        # For some reason the scale_factor and offset was already applied, so
        # reset.
        scale_factor = 1.0
        add_offset = 0.0

        # subset data, applying the scale_factor and add_offset
        ts = (
            add_offset
            + scale_factor
            * datahandle[time_index_min:time_index_max, lat_index, lon_index]
        )

        df = pd.DataFrame(
            ts,
            index=time,
            columns=[_vars[var]["long_name"] + ":" + _vars[var]["units"]],
        )
        ndf = ndf.join(df, how="outer")

    ndf.index.name = "Datetime"

    return ndf


@tsutils.transform_args(start_date=pd.to_datetime, end_date=pd.to_datetime)
def terraclimate(
    lat: float,
    lon: float,
    variables=None,
    start_date=None,
    end_date=None,
):
    r"""Download terraclimate data."""
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
Terraclimate returned no data for lat/lon "{lat}/{lon}", variables "{variables}"
between {start_date} and {end_date}.
""".format(
                    **locals()
                )
            )
        )

    return df


terraclimate.__doc__ = terraclimate_cli.__doc__


if __name__ == "__main__":
    r = terraclimate(29.6, -82.3)
    print(r)
