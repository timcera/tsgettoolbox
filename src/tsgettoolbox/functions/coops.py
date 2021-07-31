# -*- coding: utf-8 -*-
import logging
import os
from collections import defaultdict
from io import BytesIO
from typing import List, Optional

try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal

import mando
import pandas as pd
import requests
import typic

try:
    from mando.rst_text_formatter import RSTHelpFormatter as HelpFormatter
except ImportError:
    from argparse import RawTextHelpFormatter as HelpFormatter

from tstoolbox import tsutils

from tsgettoolbox import utils

_settings_map = defaultdict(lambda: [{"metric": "", "english": ""}])

# Preliminary or verified water levels, depending on availability.
_settings_map["water_level"] = [
    {"metric": "m", "english": "ft"},
    "h",
]

# Air temperature as measured at the station.
_settings_map["air_temperature"] = [
    {"metric": "degC", "english": "degF"},
    "h",
]

# Water temperature as measured at the station.
_settings_map["water_temperature"] = [
    {"metric": "degC", "english": "degF"},
    "h",
]

# Wind speed, direction, and gusts as measured at the station.
_settings_map["wind"] = [{"metric": "m/s", "english": "ft/s"}, "h"]

# Barometric pressure as measured at the station.
_settings_map["air_pressure"] = [
    {"metric": "mb", "english": "mb"},
    "h",
]

# Air Gap (distance between a bridge and the water's surface) at the
# station.
_settings_map["air_gap"] = [
    {"metric": "m", "english": "ft"},
    "h",
]

# The water's conductivity as measured at the station.
_settings_map["conductivity"] = [
    {"metric": "mS/cm", "english": "mS/cm"},
    "h",
]

# Visibility from the station's visibility sensor. A measure of atmospheric
# clarity.
_settings_map["visibility"] = [
    {"metric": "km", "english": "nm"},
    "h",
]

# Relative humidity as measured at the station.
_settings_map["humidity"] = [
    {"metric": "percent", "english": "percent"},
    "h",
]

# Salinity and specific gravity data for the station.
_settings_map["salinity"] = [
    {"metric": "PSU", "english": "PSU"},
    "h",
]

# Verified hourly height water level data for the station.
_settings_map["hourly_height"] = [
    {"metric": "m", "english": "ft"},
    "h",
]

# Verified high/low water level data for the station.
_settings_map["high_low"] = [
    {"metric": "m", "english": "ft"},
    None,
]

# Verified daily mean water level data for the station.
_settings_map["daily_mean"] = [
    {"metric": "m", "english": "ft"},
    None,
]

# Verified monthly mean water level data for the station.
_settings_map["monthly_mean"] = [
    {"metric": "m", "english": "ft"},
    None,
]

# One minute water level data for the station.
_settings_map["one_minute_water_level"] = [
    {"metric": "m", "english": "ft"},
    None,
]

# 6 minute predictions water level data for the station.
_settings_map["predictions"] = [
    {"metric": "m", "english": "ft"},
    "h",
]

# datums data for the currents stations.
_settings_map["datums"] = [
    {"metric": "m", "english": "ft"},
    None,
]

# Currents data for currents stations.
_settings_map["currents"] = [
    {"metric": "m/s", "english": "ft/s"},
    "h",
]


@mando.command("coops", formatter_class=HelpFormatter, doctype="numpy")
@tsutils.doc(tsutils.docstrings)
def coops_cli(
    station,
    date=None,
    begin_date=None,
    end_date=None,
    range=None,
    product="water_level",
    datum="NAVD",
    time_zone="GMT",
    interval="h",
    bin=None,
):
    r"""Download Center for Operational Oceanographic Products and Services.

    CO-OPS web services is at https://tidesandcurrents.noaa.gov/api/.
    The time zone of the returned data depends on the setting of the
    "time_zone" option.  The default is "GMT" also known as "UTC".

    Parameters
    ----------
    station
        A 7 character station ID, or a currents station ID.  Specify the
        station ID with the "station=" parameter.::

            Example: '--station=9414290'

        Station listings for various products can be viewed at
        https://tidesandcurrents.noaa.gov or viewed on a map at Tides
        & Currents Station Map

    date : str
        [optional, default is None]

        The API understands several parameters related to date ranges.
        Date formats are pretty flexible, however the closer to ISO
        8601, the better.

        The date related options are 'begin_date', 'end_date', 'date',
        and 'range'.  They can be combined in the following 5 ways, but
        if conflicting then follows the table in order.  For example,
        the 'date' option will be used if present regardless of any
        other option, then 'range', ...etc.:

        +-------------------+---------------------------------------+
        | Parameter Name(s) | Description                           |
        +===================+=======================================+
        | date              | 'latest', 'today', or 'recent'        |
        +-------------------+---------------------------------------+
        | range             | Specify a number of hours to go back  |
        |                   | from now and retrieve data for that   |
        |                   | date range                            |
        +-------------------+---------------------------------------+
        | begin_date and    | Specify a begin date and a number of  |
        | range             | hours to retrieve data starting from  |
        |                   | that date                             |
        +-------------------+---------------------------------------+
        | begin_date and    | Specify the date/time range of        |
        | end_date          | retrieval                             |
        +-------------------+---------------------------------------+
        | end_date and a    | Specify an end date and a number of   |
        | range             | hours to retrieve data ending at that |
        |                   | date                                  |
        +-------------------+---------------------------------------+

        +--------------------------------------+-----------------+
        | Description of "--date" option       | Option          |
        +======================================+=================+
        | Today's data                         | --date='today'  |
        +--------------------------------------+-----------------+
        | The last 3 days of data              | --date='recent' |
        +--------------------------------------+-----------------+
        | The last data point available within | --date='latest' |
        | the last 18 minutes.                 |                 |
        +--------------------------------------+-----------------+

    begin_date
        [optional, default is None]

        The beginning date for the data.  See explanation with the 'date'
        option on how to use all of the date related parameters.

    end_date
        [optional, default is None]

        The end date for the data.  January 1st, 2012 through January 2nd,
        2012::

            --begin_date='20120101' --end_date='20120102'

        See explanation with the 'date' option on how to use all of the date
        related parameters.

    range
        [optional, default is None]

        Specify the number of hours to go back from now, an 'end_date', or
        forward from a 'begin_date'.

        48 hours beginning on April 15, 2012::

            --begin_date='20120415' --range=48

        48 hours ending on March 17, 2012::

            --end_date='20120307' --range=48

        The last 24 hours from now::

            --range=24

        The last 3 hours from now::

            --range=3

        See explanation with the 'date' option on how to use all of the date
        related parameters.

    product : str
        [optional, default is 'water_level']

        Specify the observation requested.

        +------------------------+------------------------------------+
        | Option                 | Description                        |
        +========================+====================================+
        | water_level            | Six minute preliminary or verified |
        |                        | water levels, depending on         |
        |                        | availability.                      |
        +------------------------+------------------------------------+
        | air_temperature        | Air temperature                    |
        +------------------------+------------------------------------+
        | water_temperature      | Water temperature                  |
        +------------------------+------------------------------------+
        | wind                   | Wind speed, direction, and gusts   |
        +------------------------+------------------------------------+
        | air_gap                | (distance between a bridge and the |
        |                        | water's surface)                   |
        +------------------------+------------------------------------+
        | conductivity           | The water's conductivity           |
        +------------------------+------------------------------------+
        | visibility             | Visibility from the station's      |
        |                        | visibility sensor. A measure of    |
        |                        | atmospheric clarity.               |
        +------------------------+------------------------------------+
        | humidity               | Relative humidity                  |
        +------------------------+------------------------------------+
        | salinity               | Salinity and specific gravity      |
        +------------------------+------------------------------------+
        | hourly_height          | Verified hourly height water level |
        |                        | data                               |
        +------------------------+------------------------------------+
        | high_low               | Verified high/low water level data |
        +------------------------+------------------------------------+
        | daily_mean             | Verified daily mean water level    |
        |                        | data                               |
        +------------------------+------------------------------------+
        | monthly_mean           | Verified monthly mean water level  |
        |                        | data                               |
        +------------------------+------------------------------------+
        | one_minute_water_level | One minute water level data        |
        +------------------------+------------------------------------+
        | predictions            | Six minute predictions water       |
        |                        | level data                         |
        +------------------------+------------------------------------+
        | datums                 | datums data                        |
        +------------------------+------------------------------------+
        | currents               | Currents data                      |
        +------------------------+------------------------------------+

        Flags:

        +------+------------------------------------------------------+
        | Flag | Description                                          |
        +======+======================================================+
        | O    | Count of number of 1 second that falls outside a     |
        |      | 3-sigma band about the mean                          |
        +------+------------------------------------------------------+
        | F    | A flag that when set to 1 indicates that the flat    |
        |      | tolerance limit was exceeded                         |
        +------+------------------------------------------------------+
        | R    | A flag that when set to 1 indicates that the rate    |
        |      | of change tolerance limit was exceeded               |
        +------+------------------------------------------------------+
        | L    | A flag that when set to 1 indicates that either the  |
        |      | maximum or minimum expected value was exceeded       |
        +------+------------------------------------------------------+
        | I    | A flag that when set to 1 indicates that the water   |
        |      | level value has been inferred                        |
        +------+------------------------------------------------------+
        | X    | A flag that when set to 1 indicates that the maximum |
        |      | expected value was exceeded                          |
        +------+------------------------------------------------------+
        | N    | A flag that when set to 1 indicates that the minimum |
        |      | expected value was exceeded                          |
        +------+------------------------------------------------------+
        | R    | A flag that when set to 1 indicates that the rate of |
        |      | change tolerance limit was exceeded                  |
        +------+------------------------------------------------------+

        Preliminary and verified water level data

        product = "water_level"

        +-------+----------------------------------------+
        | Field | Description                            |
        +=======+========================================+
        | t     | Date and time of the observation       |
        +-------+----------------------------------------+
        | v     | Measurement                            |
        +-------+----------------------------------------+
        | s     | Standard deviation of 1 second samples |
        |       | used to compute the water level height |
        +-------+----------------------------------------+
        | f     | Flags described above                  |
        |       | Four comma separated numbers           |
        |       | Preliminary water level "O,F,R,L"      |
        |       | Verified water level "I,F,R,T"         |
        +-------+----------------------------------------+
        | q     | Quality Assurance/Quality Control      |
        |       | "p" = preliminary                      |
        |       | "v" = verified                         |
        +-------+----------------------------------------+

        product = "air_pressure", "air_temperature", "humidity",
        "water_temperature", or "conductivity"

        +-------+----------------------------------+
        | Field | Description                      |
        +=======+==================================+
        | t     | Date and time of the observation |
        +-------+----------------------------------+
        | v     | Measurement                      |
        +-------+----------------------------------+
        | f     | Flags described above            |
        |       | Three comma separated numbers    |
        |       | "X,N,R"                          |
        +-------+----------------------------------+

        Hourly Height: product = "hourly_height"

        +-------+------------------------------------------------+
        | Field | Description                                    |
        +=======+================================================+
        | t     | Time - Date and time of the observation        |
        +-------+------------------------------------------------+
        | v     | Value - Measured water level height            |
        +-------+------------------------------------------------+
        | s     | Sigma - Standard deviation of 1 second         |
        |       | samples used to compute the water level height |
        +-------+------------------------------------------------+
        | f     | Data Flags - in order of listing:              |
        |       | Flags described above "I,L"                    |
        +-------+------------------------------------------------+

        High Low: product = "high_low"

        +-------+-------------------------------------------+
        | Field | Description                               |
        +=======+===========================================+
        | t     | Time - Date and time of the observation   |
        +-------+-------------------------------------------+
        | v     | Value - Measured water level height       |
        +-------+-------------------------------------------+
        | ty    | Type - Designation of Water level height. |
        |       | HH = Higher High water                    |
        |       | H = High water                            |
        |       | L = Low water                             |
        |       | LL = Lower Low water                      |
        +-------+-------------------------------------------+
        | f     | Data Flags - in order of listing "I,L"    |
        |       | Flags described above                     |
        +-------+-------------------------------------------+

        Daily Mean: product = "daily_mean"

        +-------+------------------------------------------------+
        | Field | Description                                    |
        +=======+================================================+
        | t     | Time - Date and time of the observation        |
        +-------+------------------------------------------------+
        | v     | Value – Mean hourly data over a 24 hour period |
        +-------+------------------------------------------------+
        | f     | Data Flags - in order of listing "I,L"         |
        |       | Flags described above                          |
        +-------+------------------------------------------------+

        Monthly Mean: product = "monthly_mean"

        +----------+------------------------------------------+
        | Field    | Description                              |
        +==========+==========================================+
        | year     | Year                                     |
        +----------+------------------------------------------+
        | month    | Month                                    |
        +----------+------------------------------------------+
        | highest  | Highest Tide                             |
        +----------+------------------------------------------+
        | MHHW     | Mean Higher-High Water                   |
        +----------+------------------------------------------+
        | MHW      | Mean High Water                          |
        +----------+------------------------------------------+
        | MSL      | Mean Sea Level                           |
        +----------+------------------------------------------+
        | MTL      | Mean Tide Level                          |
        +----------+------------------------------------------+
        | MLW      | Mean Low Water                           |
        +----------+------------------------------------------+
        | MLLW     | Mean Lower-Low Water                     |
        +----------+------------------------------------------+
        | DTL      | Mean Diurnal Tide Level                  |
        +----------+------------------------------------------+
        | GT       | Great Diurnal Range                      |
        +----------+------------------------------------------+
        | MN       | Mean Range of Tide                       |
        +----------+------------------------------------------+
        | DHQ      | Mean Diurnal High Water Inequality       |
        +----------+------------------------------------------+
        | DLQ      | Mean Diurnal Low Water Inequality        |
        +----------+------------------------------------------+
        | HWI      | Greenwich High Water Interval (in Hours) |
        +----------+------------------------------------------+
        | LWI      | Greenwich Low Water Interval (in Hours)  |
        +----------+------------------------------------------+
        | lowest   | Lowest Tide                              |
        +----------+------------------------------------------+
        | inferred | A flag that when set to 1 indicates that |
        |          | the water level value has been inferred  |
        +----------+------------------------------------------+

        One Minute Water Level: product = "one_minute_water_level"

        +-------+-----------------------------------------+
        | Field | Description                             |
        +=======+=========================================+
        | t     | Time - Date and time of the observation |
        +-------+-----------------------------------------+
        | v     | Value - Measured water level height     |
        +-------+-----------------------------------------+

        Tide Predictions: product = "predictions"

        +-------+-----------------------------------------+
        | Field | Description                             |
        +=======+=========================================+
        | t     | Time - Date and time of the observation |
        +-------+-----------------------------------------+
        | v     | Value - Predicted water level height    |
        +-------+-----------------------------------------+

        Air Gap: product = "air_gap"

        +-------+--------------------------------------------+
        | Field | Description                                |
        +=======+============================================+
        | t     | Time - Date and time of the observation    |
        +-------+--------------------------------------------+
        | v     | Value - Measured air gap                   |
        +-------+--------------------------------------------+
        | s     | Sigma - Standard deviation of 1 second     |
        |       | samples used to compute the air gap        |
        +-------+--------------------------------------------+
        | f     | Data Flags - in order of listing "O,F,R,A" |
        |       | Flags described above                      |
        +-------+--------------------------------------------+

        Wind: product = "wind"

        +-------+-----------------------------------------+
        | Field | Description                             |
        +=======+=========================================+
        | t     | Time - Date and time of the observation |
        +-------+-----------------------------------------+
        | s     | Speed - Measured wind speed             |
        +-------+-----------------------------------------+
        | d     | Direction - wind direction in degrees   |
        +-------+-----------------------------------------+
        | dr    | Direction - wind direction in text      |
        +-------+-----------------------------------------+
        | g     | Gust - Measured wind gust speed         |
        +-------+-----------------------------------------+
        | f     | Data Flags - in order of listing "X,R"  |
        |       | Flags described above                   |
        +-------+-----------------------------------------+

        Visibility: product = "visibility"

        +-------+-----------------------------------------+
        | Field | Description                             |
        +=======+=========================================+
        | t     | Time - Date and time of the observation |
        +-------+-----------------------------------------+
        | v     | Value - Measured visibility             |
        +-------+-----------------------------------------+

        Salinity: product = "salinity"

        +-------+-----------------------------------------+
        | Field | Description                             |
        +=======+=========================================+
        | t     | Time - Date and time of the observation |
        +-------+-----------------------------------------+
        | s     | Salinity                                |
        +-------+-----------------------------------------+
        | g     | Specific Gravity                        |
        +-------+-----------------------------------------+

        Currents: product = "currents"

        +-------+------------------------------------------+
        | Field | Description                              |
        +=======+==========================================+
        | t     | Time - Date and time of the observation  |
        +-------+------------------------------------------+
        | s     | Speed - Measured current speed           |
        +-------+------------------------------------------+
        | d     | Direction - current direction in degrees |
        +-------+------------------------------------------+
        | b     | Bin number                               |
        +-------+------------------------------------------+

    datum
        [optional, default is 'NAVD']

        Specify the datum that all water levels will be
        reported against.  Note! Datum is mandatory for all water level
        products and defaults to "NAVD".

        +--------+-------------------------------+
        | Option | Description                   |
        +========+===============================+
        | MHHW   | Mean Higher High Water        |
        +--------+-------------------------------+
        | MHW    | Mean High Water               |
        +--------+-------------------------------+
        | MTL    | Mean Tide Level               |
        +--------+-------------------------------+
        | MSL    | Mean Sea Level                |
        +--------+-------------------------------+
        | MLW    | Mean Low Water                |
        +--------+-------------------------------+
        | MLLW   | Mean Lower Low Water          |
        +--------+-------------------------------+
        | NAVD   | North American Vertical Datum |
        +--------+-------------------------------+
        | STND   | Station Datum                 |
        +--------+-------------------------------+

    time_zone
        [optional, default is 'GMT']

        The time zone is specified as 'gmt', 'lst'
        or 'lst_ldt'.

        +---------+----------------------------------------------------+
        | Option  | Description                                        |
        +=========+====================================================+
        | gmt     | Greenwich Mean Time                                |
        +---------+----------------------------------------------------+
        | lst     | Local Standard Time. The time local to the         |
        |         | requested station.                                 |
        +---------+----------------------------------------------------+
        | lst_ldt | Local Standard/Local Daylight Time. The time local |
        |         | to the requested station.                          |
        +---------+----------------------------------------------------+

    interval
        [optional, defaults to 'h']

        Deliver the meteorological and prediction data at hourly
        intervals.  Does not override 6 minute intervals for
        --product='water_level' or 1 minute intervals for
        --product='one_minute_water_level'.

        +--------+-----------------------------------------------+
        | Option | Description                                   |
        +========+===============================================+
        | h      | Hourly meteorological data                    |
        +--------+-----------------------------------------------+
        | hilo   | High/low predictions for subordinate stations |
        +--------+-----------------------------------------------+

    bin
        [optional, defaults to None]

        The bin number for the specified currents station Example:'--bin=4'
        Will retrieve data for bin number 4. Note! If a bin is not specified
        for a PORTS station, the data is returned using a predefined real-time
        bin.

    """
    tsutils._printiso(
        coops(
            station,
            date=date,
            begin_date=begin_date,
            end_date=end_date,
            range=range,
            product=product,
            datum=datum,
            time_zone=time_zone,
            interval=interval,
            bin=bin,
        )
    )


def core(params):
    if params["end_date"] is not None:
        params["end_date"] = params["end_date"].strftime("%Y%m%d")
    if params["begin_date"] is not None:
        params["begin_date"] = params["begin_date"].strftime("%Y%m%d")

    url = r"https://tidesandcurrents.noaa.gov/api/datagetter"
    session = utils.requests_retry_session()
    req = session.get(url, params=params)

    if os.path.exists("debug_tsgettoolbox"):
        logging.warning(req.url)
    req.raise_for_status()

    if (
        b"Error" in req.content
        or b"Wrong" in req.content
        or b"Range limit" in req.content
    ):
        df = pd.DataFrame()
        error = req.content
    else:
        df = pd.read_csv(BytesIO(req.content), index_col=0, parse_dates=True)
        error = ""
    return df, error


def precore(query_params, i):
    if query_params["date"] is not None:
        ndf, error = core(query_params)
    elif (
        query_params["range"] is not None
        and query_params["begin_date"] is None
        and query_params["end_date"] is None
    ):
        ndf, error = core(query_params)
    elif query_params["begin_date"] is not None and query_params["range"] is not None:
        ndf, error = core(query_params)
    elif (
        query_params["begin_date"] is not None and query_params["end_date"] is not None
    ):
        ndf = pd.DataFrame()
        sdate = query_params["begin_date"]
        edate = query_params["end_date"]
        testdate = sdate
        while testdate < edate:
            query_params["begin_date"] = testdate
            testdate = testdate + pd.Timedelta(days=deltas[i])
            if testdate > edate:
                testdate = edate
            query_params["end_date"] = testdate
            df, error = core(query_params)
            ndf = ndf.combine_first(df)
    elif query_params["end_date"] is not None and query_params["range"] is not None:
        ndf, error = core(query_params)

    if len(ndf) == 0:
        raise ValueError(
            tsutils.error_wrapper(
                """
COOPS service returned the error "{}".
""".format(
                    error
                )
            )
        )

    new_column_names = []
    for icolumn_name in ndf.columns:
        ncolumn_name = icolumn_name.lower().strip().replace(" ", "_")
        units = _settings_map[ncolumn_name][0][query_params["units"]]
        unitstr = ncolumn_name
        if units != "":
            unitstr = ":".join([ncolumn_name, units])
        new_column_names.append(("NOS", query_params["station"], unitstr))
    ndf.columns = ["-".join(i).rstrip("-") for i in new_column_names]
    time_zone_name = query_params["time_zone"].upper()
    if time_zone_name == "GMT":
        time_zone_name = "UTC"
    ndf = ndf.tz_localize(time_zone_name)
    ndf.index.name = "Datetime:{}".format(time_zone_name)
    return ndf


deltas = {
    "water_level": 31,
    "air_temperature": 31,
    "water_temperature": 31,
    "wind": 31,
    "air_gap": 31,
    "conductivity": 31,
    "visibility": 31,
    "humidity": 31,
    "salinity": 31,
    "hourly_height": 365,
    "high_low": 365,
    "daily_mean": 3650,
    "monthly_mean": 3650,
    "one_minute_water_level": 31,
    "predictions": 31,
    "datums": 31,
    "currents": 31,
}


@tsutils.transform_args(
    product=tsutils.make_list,
    time_zone=str.upper,
    datum=str.upper,
    begin_date=tsutils.parsedate,
    end_date=tsutils.parsedate,
)
@typic.al
def coops(
    station: str,
    date: Literal["latest", "today", "recent"] = None,
    begin_date: Optional[pd.Timestamp] = None,
    end_date: Optional[pd.Timestamp] = None,
    range: Optional[int] = None,
    product: List[
        Literal[
            "water_level",
            "air_temperature",
            "water_temperature",
            "wind",
            "air_gap",
            "conductivity",
            "visibility",
            "humidity",
            "salinity",
            "hourly_height",
            "high_low",
            "daily_mean",
            "monthly_mean",
            "one_minute_water_level",
            "predictions",
            "datums",
            "currents",
        ]
    ] = "water_level",
    datum: Literal["MHHW", "MHW", "MTL", "MSL", "MLW", "MLLW", "NAVD", "STND"] = "NAVD",
    time_zone: Literal["GMT", "UTC", "LST", "LST_LDT"] = "GMT",
    interval="h",
    bin=None,
):
    r"""Download Center for Operational Oceanographic Products and Services."""
    params = {}
    params["station"] = station
    params["date"] = date
    params["range"] = range
    params["product"] = product
    params["bin"] = bin
    params["interval"] = interval
    params["units"] = "metric"
    params["time_zone"] = time_zone
    params["datum"] = datum
    try:
        params["begin_date"] = begin_date
    except ValueError:
        params["begin_date"] = None
    try:
        params["end_date"] = end_date
    except ValueError:
        params["end_date"] = None
    params["format"] = "csv"
    params["application"] = "tsgettoolbox"

    ndf = pd.DataFrame()
    for cnt, i in enumerate(product):
        r = precore(params, i)
        ndf = ndf.join(r, how="outer", rsuffix="_{}".format(cnt))
    return ndf


coops.__doc__ = coops_cli.__doc__


if __name__ == "__main__":
    """
    https://tidesandcurrents.noaa.gov/api/datagetter?begin_date=20020101
    &end_date=20020102&range=1&station=8720218&product=water_level
    """

    r = coops(
        station="8720218",
        product="water_level",
        interval="h",
        time_zone="gmt",
        datum="mllw",
        range=20,
        begin_date=None,
        end_date=None,
        date=None,
    )

    print("tidesandcurrents")
    print(r)

    r = coops(
        station="8720218",
        product="water_temperature",
        interval="h",
        time_zone="gmt",
        datum="mllw",
        begin_date="01/10/2002",
        range=2,
        end_date=None,
        date=None,
    )

    print("tidesandcurrents")
    print(r)

    r = coops(
        station="8720218",
        product="water_level",
        interval="h",
        time_zone="gmt",
        datum="mllw",
        begin_date="01/10/2002",
        range=5,
        end_date=None,
        date=None,
    )

    print("tidesandcurrents")
    print(r)

    r = coops(
        station="8720218",
        product="air_temperature",
        interval="h",
        time_zone="gmt",
        datum="mllw",
        end_date="01/10/2002",
        range=3,
        begin_date=None,
        date=None,
    )

    print("tidesandcurrents")
    print(r)

    r = coops(
        station="8720218",
        product="water_level",
        interval="h",
        time_zone="gmt",
        datum="mllw",
        begin_date="01/10/2002",
        end_date="2003-01-01",
        range=None,
        date=None,
    )

    print("tidesandcurrents")
    print(r)

    try:
        r = coops(
            station="8720218",
            product="water_level",
            time_zone="gmt",
            datum="mllw",
            begin_date=None,
            end_date=None,
            range=745,
            date=None,
        )
        print(r)
    except ValueError:
        print("Correct ValueError")
